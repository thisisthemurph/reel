import asyncio
import urllib.parse
from playwright.async_api import async_playwright, Page
from selectolax.parser import HTMLParser

SEARCH_URL = "https://www.rottentomatoes.com/search?search={search}"


class Review:
    def __init__(self):
        self.score: int | None = None
        self.review_count: int = 0

    def __str__(self):
        return f"{self.__class__.__name__}(score: {self.score}%, review_count: {self.review_count})"


class ReviewStats:
    def __init__(self):
        self.critic = Review()
        self.audience = Review()

    def __str__(self):
        return f"{self.__class__.__name__}(critic={self.critic}, audience={self.audience})"


async def __get_html(page: Page, url: str) -> HTMLParser:
    await page.goto(url)
    html = HTMLParser(await page.content())
    return html


def __get_film_scores(html: HTMLParser, url: str) -> ReviewStats:
    """Parses the rottentomatoes scores from the film details page"""
    stats = ReviewStats()
    score_board_elem = html.css_first("score-board")
    if not score_board_elem:
        print(f"No score-board element at '{url}'")
        return stats

    audience_score_attr = score_board_elem.attrs.get("audiencescore")
    tomatometer_score_attr = score_board_elem.attrs.get("tomatometerscore")

    stats.critic.score = int(tomatometer_score_attr) if tomatometer_score_attr else None
    stats.audience.score = int(audience_score_attr) if audience_score_attr else None
    return stats


def __get_film_url(html: HTMLParser, film_title: str) -> str | None:
    """Given a film title, searches rottentomatoes for it and returns a URL
    for the movie details page.
    """
    movie_search_results_elems = html.css("search-page-result[type=\"movie\"]")
    if not movie_search_results_elems:
        print(f"No movie search result element found for '{film_title}'")
        return None

    # TODO: Search the list as the first film is not always a perfect match
    movie_search_results = movie_search_results_elems[0]
    movie_links = movie_search_results.css("a[data-qa=\"info-name\"]")
    if not movie_links:
        print(f"No films found for search '{film_title}'")
        return None

    first_movie_link = movie_links[0]
    attrs = first_movie_link.attrs
    return attrs.get("href")


async def run(film_title: str):
    search_url = SEARCH_URL.format(search=urllib.parse.quote(film_title))
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        search_page_html = await __get_html(page, search_url)

        film_url = __get_film_url(search_page_html, film_title)
        if film_url is None:
            await browser.close()
            return

        film_page_html = await __get_html(page, film_url)
        scores = __get_film_scores(film_page_html, film_url)
        print(scores)

        await browser.close()

        # return rankings


async def main():
    await run("Die Hard")


if __name__ == "__main__":
    asyncio.run(main())
