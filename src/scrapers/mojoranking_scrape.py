import asyncio
from datetime import datetime
from playwright.async_api import async_playwright, Page
from selectolax.parser import HTMLParser

from src.models import Film

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

        try:
            d = f"{data[8].text()} {year}"
            release_date = datetime.strptime(d, "%b %d %Y").date()
        except ValueError as ex:
            release_date = None

        distributor = data[9].text(strip=True)
        yield Film(
            data[1].text(),
            int(data[0].text()),
            release_date,
            None if not distributor or distributor == "-" else distributor,
        )


async def run(year: int) -> enumerate[Film]:
    mojo_box_office_url = BOX_OFFICE_MOJO_URL.format(year=year)
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        html = await __get_html(page, mojo_box_office_url)
        await browser.close()

        return __parse_html(html, year)


async def main():
    for film in await run(year=datetime.now().year):
        print(film)


if __name__ == "__main__":
    asyncio.run(main())
