from playwright.async_api import Page
from selectolax.parser import HTMLParser


class Scraper:
    @staticmethod
    async def _get_html(page: Page, url: str):
        await page.goto(url)
        html = HTMLParser(await page.content())
        return html
