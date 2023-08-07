import logging
from logging import Logger
from typing import Protocol

import httpx
from httpx import AsyncClient
from playwright.async_api import Page
from selectolax.parser import HTMLParser


class HtmlParserProtocol(Protocol):
    @property
    def logger(self) -> Logger:
        ...

    async def get_html_parser(self, client, url: str):
        ...


class PlaywrightHtmlParser:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    async def get_html_parser(self, page: Page, url: str):
        try:
            await page.goto(url)
            return HTMLParser(await page.content())
        except Exception as ex:
            self.logger.exception(ex)
            return None


class HttpxHtmlParser:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    async def get_html_parser(self, client: AsyncClient, url: str):
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
            }
            resp = await client.get(url, headers=headers)
            if resp.status_code != 200:
                self.logger.warning(f"URL '{url} returned status code of {resp.status_code}'")
                return None
            return HTMLParser(resp.content)
        except httpx.ReadTimeout as ex:
            self.logger.exception(f"httpx.ReadTimeout for '{url}'")
            return None
