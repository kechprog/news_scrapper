from typing import Optional
import base64
from selenium import webdriver
from selenium.webdriver import Chrome, ChromeOptions

from extractor import use_ai

class WebScraper:
    def __init__(self, reader_mode=False, options: Optional[ChromeOptions]=None):
        if not options:
            self.options = webdriver.ChromeOptions()
            self.options.add_argument("--headless")
            self.options.add_argument("--disable-gpu")
            self.options.add_argument("--no-sandbox")
            self.options.add_argument("--disable-dev-shm-usage")
        else:
            self.options = options

        self.reader_mode = reader_mode
        self.driver = None
        self.service = webdriver.ChromeService()

    def __enter__(self):
        if self.driver is None:
            print("[1/6] Initializing Chrome WebDriver...")
            self.driver = Chrome(service=self.service, options=self.options)
            print("✓ Chrome WebDriver initialized")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.driver is not None:
            self.driver.quit()
            self.driver = None

    def get_full_page_screenshot(self, url: str) -> Optional[str]:
        """
        Captures a full-page screenshot and returns it as a base64 encoded string.
        Critical: Captures entire page height to ensure publication data, timestamps, and source are visible.
        """
        assert self.driver is not None, "Use inside \"with\" statement"
        if self.reader_mode:
            print("⚠ Warning: Reader mode (about:reader) is Firefox-specific and not supported in Chrome")
            # Reader mode not supported in Chrome, proceeding with normal URL

        try:
            print(f"[2/6] Loading URL: {url}")
            self.driver.get(url)
            self.driver.implicitly_wait(10)
            print("✓ Page loaded")

            # Get the full page dimensions
            print("[3/6] Getting page dimensions...")
            original_size = self.driver.get_window_size()
            required_width = self.driver.execute_script('return document.body.scrollWidth')
            required_height = self.driver.execute_script('return document.body.scrollHeight')
            print(f"✓ Page dimensions: {required_width}x{required_height}px")

            # Set window size to capture full page
            print("[4/6] Resizing window for full page capture...")
            self.driver.set_window_size(required_width, required_height)

            # Wait a moment for any dynamic content to render
            self.driver.implicitly_wait(2)

            # Take screenshot and encode to base64
            print("[5/6] Capturing screenshot...")
            screenshot_png = self.driver.get_screenshot_as_png()
            screenshot_size_mb = len(screenshot_png) / (1024 * 1024)
            print(f"✓ Screenshot captured ({screenshot_size_mb:.2f} MB)")

            print("[6/6] Encoding to base64...")
            screenshot_b64 = base64.b64encode(screenshot_png).decode('utf-8')
            print(f"✓ Encoded to base64 ({len(screenshot_b64)} chars)")

            # Restore original window size
            self.driver.set_window_size(original_size['width'], original_size['height'])

            return screenshot_b64
        except Exception as e:
            print(f"Error capturing screenshot for {url}: {e}")
            return None

if __name__ == "__main__":
    print("=" * 80)
    print("Starting News Scraper")
    print("=" * 80)

    url = "https://www.ctvnews.ca/kitchener/guelph/article/guelph-mother-still-waiting-to-find-out-how-her-son-died-at-millhaven-institution/"
    with WebScraper() as scraper:
        screenshot_b64 = scraper.get_full_page_screenshot(url)
        if screenshot_b64:
            use_ai(screenshot_b64)
        else:
            print("Failed to capture screenshot")
