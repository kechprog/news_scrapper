# News Scraper

A Python-based web scraper designed to extract news articles from websites and convert them into clean, structured Markdown format using AI processing.

## Features

- Web scraping using Selenium with Firefox WebDriver
- HTML cleaning to remove unnecessary elements (scripts, styles, ads, etc.)
- AI-powered content extraction and conversion to Markdown format
- Reader mode support for cleaner article extraction
- Headless browser operation for background processing

## Requirements

See [requirements.txt](requirements.txt) for Python dependencies.

## How It Works

1. Uses Selenium WebDriver to fetch web pages
2. Cleans the HTML by removing unwanted tags and attributes
3. Processes the cleaned HTML with an AI model (Qwen) to extract structured information:
   - Article title
   - Publication date
   - Publisher name
   - Author name
   - Main content (preserving original text and formatting)

## Usage

The scraper can be used programmatically:

```python
from main import WebScraper
from html_cleaner import HTMLTreeBuilder
from extractor import use_ai

url = "https://example-news-site.com/article"

with WebScraper() as scraper:
    html = scraper.get_html(url)
    if html:
        cleaner = HTMLTreeBuilder()
        tree = cleaner.build_tree(html)
        use_ai(tree)
```

### Options

- `reader_mode`: Enable Firefox's reader mode for cleaner article extraction
- Custom Firefox options can be passed to the scraper

## Current Limitations

- Hardcoded to use a specific Ollama endpoint
- Currently configured for a specific news site in the example
- Basic HTML cleaning implementation
- No RSS feed support yet
- No historical data acquisition

## Planned Improvements

- Better attribute handling in HTML cleaning
- AI prompt experimentation and fine-tuning
- RSS feed support
- Historical data acquisition capabilities

## Disclaimer

This tool is for educational purposes. Please respect website terms of service and robots.txt when scraping content. Consider rate limiting and caching to avoid overloading servers.