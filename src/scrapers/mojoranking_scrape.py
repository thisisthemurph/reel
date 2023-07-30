import asyncio
from datetime import datetime
from playwright.async_api import async_playwright, Page
from selectolax.parser import HTMLParser

from src.models import Movie
from src.scrapers.scraper import Scraper

BOX_OFFICE_MOJO_URL = "https://www.boxofficemojo.com/year/{year}/"


class BoxOfficeMojoMovieListScraper(Scraper):
    @staticmethod
    def __parse_html(html: HTMLParser, year: int) -> enumerate[Movie]:
        ranking_table = html.css("tbody")[1]
        for row in ranking_table.css("tr"):
            data = row.css("td")
            if not data:
                continue

            try:
                # The website stores the date with the format Jan 17
                date_with_year = f"{data[8].text()} {year}"
                release_date = datetime.strptime(date_with_year, "%b %d %Y").date()
            except ValueError as ex:
                release_date = None

            distributor = data[9].text(strip=True)
            yield Movie(
                title=data[1].text(strip=True),
                rank=int(data[0].text(strip=True)),
                release_date=release_date,
                distributor=None
                if not distributor or distributor == "-"
                else distributor,
            )

    async def run(self, year: int) -> enumerate[Movie]:
        mojo_box_office_url = BOX_OFFICE_MOJO_URL.format(year=year)
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            html = await self._get_html(page, mojo_box_office_url)
            await browser.close()

            return self.__parse_html(html, year)


async def main():
    scraper = BoxOfficeMojoMovieListScraper()
    for movie in await scraper.run(year=datetime.now().year):
        print(movie)


if __name__ == "__main__":
    asyncio.run(main())
