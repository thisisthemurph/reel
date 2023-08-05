from logging import Logger
from typing import Protocol

import httpx
from httpx import AsyncClient
from playwright.async_api import Page
from selectolax.parser import HTMLParser

from libs.supalogger import make_logger


class HtmlParserProtocol(Protocol):
    @property
    def logger(self) -> Logger:
        ...

    @classmethod
    def httpx_scraper(cls):
        logger = make_logger("HttpxHtmlScraper")
        return HttpxHtmlParser(logger)

    @classmethod
    def playwright_scraper(cls):
        logger = make_logger("PlaywrightHTMLScraper")
        return PlaywrightHtmlParser(logger)

    async def get_html_parser(self, client, url: str):
        ...


class PlaywrightHtmlParser:
    def __init__(self, logger: Logger):
        self.logger = logger

    async def get_html_parser(self, page: Page, url: str):
        try:
            await page.goto(url)
            return HTMLParser(await page.content())
        except Exception as ex:
            self.logger.exception(ex)
            return None


class HttpxHtmlParser:
    def __init__(self, logger: Logger):
        self.logger = logger

    async def get_html_parser(self, client: AsyncClient, url: str):
        try:
            resp = await client.get(url)
            return HTMLParser(resp.content)
        except httpx.ReadTimeout as ex:
            self.logger.exception(f"httpx.ReadTimeout for '{url}'")
            return None
