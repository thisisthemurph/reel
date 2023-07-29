import asyncio
import urllib.parse
from playwright.async_api import async_playwright, Page
from selectolax.parser import HTMLParser, Node

SEARCH_URL = "https://www.rottentomatoes.com/search?search={search}"


class Review:
    def __init__(self):
        self.score: int | None = None
        self.review_count: str = "0"

    def get_score(self, default: str = "-") -> str:
        """Returns the score as a percentage string, e.g: 12%. If no score, returns default param."""
        return f"{self.score}%" if self.score else default

    def __str__(self):
        return f"{self.__class__.__name__}(score: {self.get_score()}, review_count: {self.review_count})"


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
    audience_review_count = score_board_elem.css_first("a[data-qa=\"audience-rating-count\"]").text(strip=True).split()
    tomatometer_review_count = (score_board_elem.css_first("a[data-qa=\"tomatometer-review-count\"]")
                                .text(strip=True)
                                .split())

    stats.audience.score = int(audience_score_attr) if audience_score_attr else None
    if audience_review_count:
        stats.audience.review_count = audience_review_count[0]

    stats.critic.score = int(tomatometer_score_attr) if tomatometer_score_attr else None
    if tomatometer_review_count:
        stats.critic.review_count = tomatometer_review_count[0]

    return stats


def __get_film_url(html: HTMLParser, film_title: str) -> str | None:
    """Given a film title, searches rottentomatoes for it and returns a URL for the movie details page."""
    def search_page_has_results() -> bool:
        page_heading = html.css_first("h1")
        return "search__no-results-header" not in page_heading.attrs.get("class", "").split()

    def get_title_and_link_from_movie_node(movie: Node) -> tuple[str, str]:
        link_node = movie.css_first("a[data-qa=\"info-name\"]")
        return link_node.text(strip=True), link_node.attrs.get("href")

    if not search_page_has_results():
        print(f"No search results for movie '{film_title}'")
        return None

    movie_search_results_node = html.css_first("search-page-result[type=\"movie\"]")
    if not movie_search_results_node:
        print(f"No movie search result node found for '{film_title}'")
        return None

    # Return link for the movie with the matching title
    movie_search_results = movie_search_results_node.css("search-page-media-row")
    for movie_node in movie_search_results:
        title, link = get_title_and_link_from_movie_node(movie_node)
        if title.upper() == film_title.upper():
            return link
    else:
        # Fall back to the first movie if no movie title matches exactly
        if movie_search_results:
            __, link = get_title_and_link_from_movie_node(movie_search_results[0])
            return link

    return None


async def run(film_title: str):
    search_url = SEARCH_URL.format(search=urllib.parse.quote(film_title))
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        search_page_html = await __get_html(page, search_url)

        movie_url = __get_film_url(search_page_html, film_title)
        if movie_url is None:
            await browser.close()
            return

        film_page_html = await __get_html(page, movie_url)
        await browser.close()

        scores = __get_film_scores(film_page_html, movie_url)
        print(scores)


async def main():
    await run("die hard")


if __name__ == "__main__":
    asyncio.run(main())
