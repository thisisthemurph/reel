import asyncio
from datetime import datetime, date

import httpx
from selectolax.parser import HTMLParser, Node

from projects.bot import HtmlParserProtocol
from projects.bot.result_models import MovieResult, SourceResult
from projects.bot import sites

# URL for the list of fresh movies - page number just loads more movies - max page is 5
BASE_URL = "https://www.rottentomatoes.com"
MOVIE_LIST_URL = "https://www.rottentomatoes.com/browse/movies_in_theaters/sort:a_z?page=5"


class RottenTomatoesMovieListScraper:
    def __init__(self, scraper: HtmlParserProtocol):
        self.scraper = scraper
        self.logger = scraper.logger

    @staticmethod
    def safe_parse_open_date(node: Node) -> date | None:
        open_date_text = node.text(strip=True)
        if open_date_text.startswith("Open"):
            open_date_text = open_date_text.split(" ", 1)[1]

        try:
            return datetime.strptime(open_date_text, "%b %d, %Y").date()
        except ValueError:
            return None

    async def __parse_video_tiles(self, parser: HTMLParser) -> list[MovieResult]:
        movies: list[MovieResult] = []
        tile_nodes = parser.css("div.js-tile-link")
        for tile_node in tile_nodes:
            link_node = tile_node.css_first('a[data-qa="discovery-media-list-item-caption"]')
            title_node = tile_node.css_first('span[data-qa="discovery-media-list-item-title"]')
            opened_node = tile_node.css_first(
                'span[data-qa="discovery-media-list-item-start-date"]'
            )

            title = title_node.text(strip=True)
            movies.append(
                MovieResult(
                    title=title,
                    release_date=self.safe_parse_open_date(opened_node),
                    source=SourceResult(
                        sites.ROTTENTOMATOES, f"{BASE_URL}{link_node.attrs.get('href')}"
                    ),
                )
            )

        return movies

    async def __parse_normal_tiles(self, parser: HTMLParser) -> list[MovieResult]:
        movies: list[MovieResult] = []
        tile_nodes = parser.css("a.js-tile-link")
        for tile_node in tile_nodes:
            title_node = tile_node.css_first('span[data-qa="discovery-media-list-item-title"]')
            opened_node = tile_node.css_first(
                'span[data-qa="discovery-media-list-item-start-date"]'
            )

            movies.append(
                MovieResult(
                    title=title_node.text(strip=True),
                    release_date=self.safe_parse_open_date(opened_node) if opened_node else None,
                    source=SourceResult(
                        sites.ROTTENTOMATOES, f"{BASE_URL}{tile_node.attrs.get('href')}"
                    ),
                )
            )

        return movies

    async def __parse_tiles(self, parser: HTMLParser) -> list[MovieResult]:
        coroutines = [self.__parse_normal_tiles(parser), self.__parse_video_tiles(parser)]
        results: tuple[list[MovieResult]] = await asyncio.gather(*coroutines)
        return [movie for movie_list in results for movie in movie_list]

    async def run(self) -> list[MovieResult]:
        async with httpx.AsyncClient() as client:
            parser = await self.scraper.get_html_parser(client, MOVIE_LIST_URL)
            return await self.__parse_tiles(parser)
