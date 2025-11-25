# News Scraper

A Python-based web scraper designed to extract news articles from websites and convert them into clean, structured Markdown format using vision-capable AI models.

## Features

- Web scraping using Selenium with Firefox WebDriver
- **Full-page screenshot capture** to preserve all content and metadata
- **Vision AI-powered content extraction** from screenshots
- Captures critical metadata: publication dates, last updated timestamps, publisher, and author
- Reader mode support for cleaner article extraction
- Headless browser operation for background processing
- OpenAI-compatible API (works with LM Studio and other local servers)

## Requirements

See [requirements.txt](requirements.txt) for Python dependencies:
- selenium>=4.0.0
- openai>=1.0.0

**Additional Requirements:**
- Firefox browser and geckodriver installed
- Nexa AI Server (or other OpenAI-compatible server) running locally with a vision-capable model
  - Currently configured for: `http://127.0.0.1:18181`
  - Model: Qwen3-VL-8B-Thinking-GGUF

## How It Works

1. Uses Selenium WebDriver to navigate to news URLs
2. **Captures full-page screenshot** (adjusts window size to page dimensions)
3. Sends screenshot to vision-capable LLM via OpenAI-compatible API
4. AI extracts structured information from the screenshot:
   - Article title
   - Publication date (with time if available)
   - Last updated timestamp (if different from publication)
   - Publisher name
   - Author name(s)
   - Main content (preserving original text and formatting)

## Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Start your AI server:
   - Currently configured for Nexa AI Server at `http://127.0.0.1:18181`
   - Model: `NexaAI/Qwen3-VL-8B-Thinking-GGUF:Q8_0`
   - Any OpenAI-compatible vision API can be used by updating `extractor.py`

3. Run the scraper:
```bash
python main.py
```

## Usage

The scraper can be used programmatically:

```python
from main import WebScraper
from extractor import use_ai

url = "https://example-news-site.com/article"

with WebScraper() as scraper:
    screenshot_b64 = scraper.get_full_page_screenshot(url)
    if screenshot_b64:
        use_ai(screenshot_b64)
```

### Options

- `reader_mode`: Enable Firefox's reader mode for cleaner article extraction
- Custom Firefox options can be passed to the scraper

## Why Screenshots?

The screenshot-based approach has critical advantages for historical data preservation:

1. **Metadata Preservation**: Publication dates, update timestamps, and source attribution are often only visible in the rendered page
2. **Layout Context**: Vision models can understand visual hierarchy to distinguish article content from ads/navigation
3. **Dynamic Content**: Captures JavaScript-rendered content that may not be in the initial HTML
4. **Authenticity**: Preserves the article as it actually appeared, important for historical records

## Current Configuration

- **API Endpoint**: Nexa AI Server at `http://127.0.0.1:18181/v1`
- **Model**: `NexaAI/Qwen3-VL-8B-Thinking-GGUF:Q8_0`
- **Special Features**: Thinking mode enabled (`enable_think: true`)
- **Context Window**: 8192 tokens
- **Output**: Extracted content printed to console

## Current Limitations

- Requires Nexa AI Server (or compatible server) to be running locally
- Hardcoded endpoint and model in `extractor.py`
- No RSS feed support yet
- No batch processing or historical data acquisition
- Output only to console (no file writing)
- Large screenshots may be slow to process

## Planned Improvements

- Configuration file for API endpoints and models
- Output to file system with structured storage
- Batch processing support
- RSS feed integration
- Historical data acquisition capabilities
- Support for multiple AI providers (OpenAI, Anthropic, etc.)

## Disclaimer

This tool is for educational purposes. Please respect website terms of service and robots.txt when scraping content. Consider rate limiting and caching to avoid overloading servers.