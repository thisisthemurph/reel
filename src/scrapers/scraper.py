from playwright.async_api import Page
from selectolax.parser import HTMLParser


class Scraper:
    @staticmethod
    async def _get_html(page: Page, url: str):
        try:
            await page.goto(url)
            return HTMLParser(await page.content())
        except Exception as ex:
            print(type(ex))
            print(ex)
            return None
