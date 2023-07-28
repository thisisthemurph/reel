import asyncio
from datetime import datetime
from playwright.async_api import async_playwright, Page
from selectolax.parser import HTMLParser

from models.film import Film

BOX_OFFICE_MOJO_URL = "https://www.boxofficemojo.com/year/{year}/"


async def __get_html(page: Page, url: str) -> HTMLParser:
    await page.goto(url)
    html = HTMLParser(await page.content())
    return html


def __parse_html(html: HTMLParser, year: int) -> enumerate[Film]:
    ranking_table = html.css("tbody")[1]
    for row in ranking_table.css("tr"):
        data = row.css("td")
        if not data:
            continue

        rank = int(data[0].text())
        title = data[1].text()
        release_date_value = data[8].text()  # Release date formats: Jan 2, May 26
        distributor = data[9].text(strip=True)

        try:
            d = f"{release_date_value} {year}"
            release_date = datetime.strptime(d, "%b %d %Y").date()
        except ValueError as ex:
            release_date = None

        film = Film(
            title,
            rank,
            release_date,
            None if not distributor or distributor == "-" else distributor
        )

        yield film


async def run(year: int) -> enumerate[Film]:
    mojo_box_office_url = BOX_OFFICE_MOJO_URL.format(year=year)
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        html = await __get_html(page, mojo_box_office_url)
        rankings = __parse_html(html, year)
        await browser.close()

        return rankings


async def main():
    for film in await run(year=datetime.now().year):
        print(film)


if __name__ == "__main__":
    asyncio.run(main())
