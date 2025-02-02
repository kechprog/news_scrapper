from typing import Optional
from selenium import webdriver
from selenium.webdriver import Firefox, FirefoxOptions

from html_cleaner import HTMLTreeBuilder
from extractor import use_ai

class WebScraper:
    def __init__(self, reader_mode=False, options: Optional[FirefoxOptions]=None):
        if not options:
            self.options = webdriver.FirefoxOptions()
            self.options.add_argument("--headless")
            self.options.add_argument("--new-window")
        else:
            self.options = options

        self.reader_mode = reader_mode
        self.driver = None
        self.service = webdriver.FirefoxService()

    def __enter__(self):
        if self.driver is None:
            self.driver = Firefox(service=self.service, options=self.options)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.driver is not None:
            self.driver.quit()
            self.driver = None

    def get_html(self, url: str):
        assert self.driver is not None, "Use inside \"with\" statement"
        if self.reader_mode:
            url = f"about:reader?url={url}"
        try:
            self.driver.get(url)
            self.driver.implicitly_wait(10)
            return self.driver.page_source
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None

if __name__ == "__main__":
    url = "https://www.nytimes.com/live/2025/02/01/us/trump-tariffs-news"
    with WebScraper() as scraper:
        if html := scraper.get_html(url):
            cleaner = HTMLTreeBuilder()
            use_ai(cleaner.build_tree(html))
        else:
            print("Something went wrong")
