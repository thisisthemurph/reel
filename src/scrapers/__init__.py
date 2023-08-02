from logging import Logger

from playwright.async_api import Page
from selectolax.parser import HTMLParser


class HTMLScraper:
    def __init__(self, logger: Logger):
        self.logger = logger

    async def get_html(self, page: Page, url: str):
        try:
            await page.goto(url)
            return HTMLParser(await page.content())
        except Exception as ex:
            self.logger.exception(ex)
            return None
