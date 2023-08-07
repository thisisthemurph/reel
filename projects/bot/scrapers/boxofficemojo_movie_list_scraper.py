from datetime import datetime

import httpx
from selectolax.parser import HTMLParser

from database.models import MovieModel
from projects.bot import HtmlParserProtocol

BOX_OFFICE_MOJO_URL = "https://www.boxofficemojo.com/year/{year}/"


class BoxOfficeMojoMovieListScraper:
    def __init__(self, scraper: HtmlParserProtocol):
        self.scraper = scraper
        self.logger = scraper.logger

    def __parse_html(self, parser: HTMLParser, year: int) -> enumerate[MovieModel]:
        ranking_table = parser.css_first("tbody")
        for row in ranking_table.css("tr"):
            data = row.css("td")
            if not data:
                continue

            try:
                # The website stores the date with the format Jan 17
                date_with_year = f"{data[8].text()} {year}"
                release_date = datetime.strptime(date_with_year, "%b %d %Y").date()
            except ValueError as ex:
                self.logger.exception(ex)
                release_date = None

            distributor = data[9].text(strip=True)
            yield MovieModel(
                title=data[1].text(strip=True),
                rank=int(data[0].text(strip=True)),
                release_date=release_date,
                distributor=None if not distributor or distributor == "-" else distributor,
            )

    async def run(self, year: int) -> enumerate[MovieModel]:
        mojo_box_office_url = BOX_OFFICE_MOJO_URL.format(year=year)
        async with httpx.AsyncClient() as client:
            parser = await self.scraper.get_html_parser(client, mojo_box_office_url)
            return self.__parse_html(parser, year)
