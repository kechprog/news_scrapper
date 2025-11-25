# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Python web scraper that extracts news articles from websites and converts them to clean Markdown format using **vision-capable AI models**. The scraper uses Selenium with Chrome WebDriver to capture full-page screenshots, which are then processed by a vision LLM via OpenAI-compatible API (LM Studio).

**Critical Design Goal**: Preserve historical metadata (publication dates, update timestamps, publisher, author) that may not be available through other means.

## Dependencies & Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Requirements:
# - selenium>=4.0.0
# - openai>=1.0.0
# - Chrome browser and chromedriver must be installed on the system
# - Nexa AI Server (or OpenAI-compatible server) with a vision-capable model
#   Currently: http://127.0.0.1:18181 with Qwen3-VL-8B-Thinking-GGUF
```

## Running the Scraper

```bash
# 1. Start Nexa AI Server with the vision model
# Basic (uses default context window, typically 8K-32K):
nexa server NexaAI/Qwen3-VL-8B-Thinking-GGUF:Q8_0

# With increased context window (256K tokens):
nexa server NexaAI/Qwen3-VL-8B-Thinking-GGUF:Q8_0 --nctx 262144

# 2. Run the scraper (in a separate terminal)
python main.py
```

**Server endpoint**: http://127.0.0.1:18181
**Expected VRAM usage**: ~8-10GB for Q8_0 quantization
**Max output**: 32K tokens (configurable in extractor.py)

## Architecture

The codebase uses a **screenshot-based extraction pipeline**:

### 1. WebScraper (main.py:8-92)
- Context manager for Selenium Chrome WebDriver
- Headless mode enabled by default with Chrome-specific flags (--disable-gpu, --no-sandbox)
- **Key method**: `get_full_page_screenshot(url)` → returns base64 encoded PNG
  - Dynamically resizes browser window to capture entire page
  - Critical for capturing metadata that may appear anywhere on the page
  - Restores original window size after capture
- Reader mode parameter exists but is not supported in Chrome (Firefox-specific feature)

### 2. AI Extractor (extractor.py:51-97)
- Uses OpenAI Python client pointed at Nexa AI Server: `http://127.0.0.1:18181/v1`
- **Vision API**: Sends base64 screenshot via OpenAI's image_url format
- Model: `NexaAI/Qwen3-VL-8B-Thinking-GGUF:Q8_0` (Qwen3 8B vision model with thinking capabilities)
  - **Native context length**: 256K tokens (extendable to 1M with YaRN)
  - **VRAM usage**: ~8-10GB for Q8_0 quantization
- Temperature: 0.1 (low for consistent extraction)
- **Max output tokens**: 32768 (32K) - suitable for very long articles
  - Model supports up to 40960 tokens for thinking tasks
  - Can be increased further if needed
- **Timeout**: 600 seconds (10 minutes) set on client to prevent connection drops
- **Logging**: Detailed progress logs show API call status, screenshot size, and max tokens
- **Note**: Uses Nexa SDK-compatible parameters only (removed `extra_body` params)
- System prompt emphasizes:
  - Extracting exact text (no summarization)
  - **Critical focus on metadata**: publication date, last updated, publisher, author
  - Scanning entire screenshot for date/time info

### 3. HTMLTreeBuilder (html_cleaner.py) - DEPRECATED
- **Note**: This module is no longer used in the main workflow
- Previously used for HTML parsing approach (now replaced by screenshot-based approach)
- May be useful for future HTML-based preprocessing

## Data Flow

```
URL → WebScraper.get_full_page_screenshot()
    → Base64 PNG screenshot
    → use_ai(screenshot_b64)
    → OpenAI client → Nexa AI Server (Qwen3-VL-8B-Thinking)
    → Markdown output (printed to console)
```

## Typical Usage Pattern

```python
from main import WebScraper
from extractor import use_ai

url = "https://example-news-site.com/article"
with WebScraper() as scraper:
    screenshot_b64 = scraper.get_full_page_screenshot(url)
    if screenshot_b64:
        use_ai(screenshot_b64)  # Prints extracted Markdown to console
```

## Important Implementation Details

- **WebDriver**: Chrome WebDriver with headless mode (requires Chrome and chromedriver installed)
- **API Endpoint**: Nexa AI Server endpoint is hardcoded in extractor.py:45-48: `http://127.0.0.1:18181/v1`
- **Model**: `NexaAI/Qwen3-VL-8B-Thinking-GGUF:Q8_0` - Qwen3 8B vision model with thinking mode
  - Native 256K token context window (extendable to 1M with YaRN)
  - VRAM usage: ~8-10GB for Q8_0 quantization
- **Output Limits**: 32K max_tokens (32768) for very long article extraction
  - Can be increased up to 40960+ if needed (extractor.py:87)
  - Model natively supports thinking tasks with extended output
- **API Timeout**: 600 seconds (10 minutes) set on OpenAI client initialization to prevent connection drops
  - **Critical**: Timeout must be on the CLIENT, not individual API calls, to avoid "connection forcibly closed" errors
  - Vision model processing can take 1-5+ minutes for large screenshots
- **Full Page Capture**: The screenshot captures the ENTIRE page height, not just viewport (main.py:51-57)
- **Progress Logging**: Detailed step-by-step logging shows execution progress (6 steps in screenshot capture, API call status)
- **Output**: `use_ai()` prints directly to console; no file writing is implemented
- **Error Handling**: Basic try/except blocks, errors printed to console with clear indicators
- **Nexa SDK Compatibility**: Uses only documented Nexa SDK parameters (max_tokens, temperature, stream)

## Why Screenshot-Based Approach?

1. **Metadata Preservation**: Publication dates/times often only appear in rendered page, not easily in HTML
2. **Visual Context**: Vision models understand layout to distinguish content from ads/navigation
3. **JavaScript Content**: Captures dynamically rendered elements
4. **Historical Authenticity**: Preserves how the article actually appeared

## Known Limitations

- Requires Nexa AI Server (or compatible server) running locally at http://127.0.0.1:18181
- API endpoint and model are hardcoded (no configuration file)
- No output file writing; results only printed
- No RSS feed support
- No historical data acquisition/batch processing
- Screenshot size may be very large for long articles (impacts API performance)
- No retry logic or fallback models

## Configuration Notes

### Output Token Limits

To adjust max output tokens:
- Edit `extractor.py:87` to change `max_tokens` parameter
- Current: 32768 (32K tokens)
- Model supports up to 40960+ tokens for thinking tasks
- Higher values will take longer to generate and use more VRAM

### Context Window Configuration

The Qwen3-VL-8B model natively supports a **256K token context window**. The context window is controlled server-side when starting Nexa AI server.

**To increase context window beyond default:**
```bash
# Start Nexa server with custom context length (nctx parameter)
nexa server NexaAI/Qwen3-VL-8B-Thinking-GGUF:Q8_0 --nctx 262144  # 256K context
```

**For extremely long documents (1M tokens with YaRN):**
- This requires server-side configuration
- See Qwen3-VL documentation for YaRN rope scaling configuration
- VRAM requirements will increase significantly

**Current setup:**
- Input context: Uses Nexa server default (typically 8192-32768)
- Output tokens: 32768 (configurable in extractor.py:87)
- VRAM usage: ~8-10GB for Q8_0 quantization

### API Endpoint and Model

To change API endpoint or model:
- Edit `extractor.py:45-48` to modify the OpenAI client base_url and timeout
- Edit `extractor.py:68` to change the model name
- Edit `extractor.py:48` to adjust the timeout value (default: 600 seconds / 10 minutes)
  - **Important**: Timeout must be set on CLIENT initialization, not individual API calls
- For cloud providers (OpenAI, Anthropic), update base_url and api_key accordingly

### Browser Configuration

To switch back to Firefox:
- Change imports in `main.py:4` from Chrome/ChromeOptions to Firefox/FirefoxOptions
- Update `main.py:11` to use FirefoxOptions()
- Update `main.py:21` to use FirefoxService()
- Update `main.py:26` to instantiate Firefox() instead of Chrome()
- Firefox reader mode will work with `about:reader?url=` prefix
