import asyncio

import httpx
from selectolax.parser import HTMLParser, Node

from projects.bot import HtmlParserProtocol, HttpxHtmlParser
from projects.bot.result_models import MovieResult, SourceResult
from projects.bot import sites

# URL for the list of fresh movies - page number just loads more movies - max page is 5
BASE_URL = "https://www.imdb.com"
MOVIE_LIST_URL = "https://www.imdb.com/chart/moviemeter/?sort=release_date%2Cdesc"


class IMDBMovieListScraper:
    def __init__(self, scraper: HtmlParserProtocol):
        self.scraper = scraper
        self.logger = scraper.logger

    async def __parse(self, parser: HTMLParser) -> list[MovieResult]:
        movie_results: list[MovieResult] = []
        for movie in parser.css("ul.ipc-metadata-list li.ipc-metadata-list-summary-item"):
            link_node = movie.css_first("a.ipc-title-link-wrapper")
            title_node = movie.css_first("h3.ipc-title__text")
            rating_placeholder_node = movie.css_first("span.ratingGroup--placeholder")

            # Skip movies that cannot have a rating
            if rating_placeholder_node is not None:
                continue

            url_part = link_node.attrs.get("href")
            movie_results.append(
                MovieResult(
                    title=title_node.text(strip=True),
                    release_date=None,
                    source=SourceResult(sites.IMDB, f"{BASE_URL}{url_part}"),
                )
            )

        return movie_results

    async def run(self) -> list[MovieResult]:
        async with httpx.AsyncClient() as client:
            parser = await self.scraper.get_html_parser(client, MOVIE_LIST_URL)
            return await self.__parse(parser)


if __name__ == "__main__":
    s = IMDBMovieListScraper(HttpxHtmlParser())
    asyncio.run(s.run())
