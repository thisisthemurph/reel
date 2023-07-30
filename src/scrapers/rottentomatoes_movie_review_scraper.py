import urllib.parse
from playwright.async_api import async_playwright
from selectolax.parser import HTMLParser, Node

from src.models.movie_review import MovieReviewStats
from src.scrapers.scraper import Scraper

SEARCH_URL = "https://www.rottentomatoes.com/search?search={search}"


class RottenTomatoesMovieReviewScraper(Scraper):
    @staticmethod
    def __parse_movie_scores(html: HTMLParser, url: str) -> MovieReviewStats:
        """Parses the rottentomatoes scores from the movie details page"""
        stats = MovieReviewStats()
        score_board_elem = html.css_first("score-board")
        if not score_board_elem:
            print(f"No score-board element at '{url}'")
            return stats

        audience_score_attr = score_board_elem.attrs.get("audiencescore")
        tomatometer_score_attr = score_board_elem.attrs.get("tomatometerscore")
        audience_review_count = (
            score_board_elem.css_first('a[data-qa="audience-rating-count"]')
            .text(strip=True)
            .split()
        )
        tomatometer_review_count = (
            score_board_elem.css_first('a[data-qa="tomatometer-review-count"]')
            .text(strip=True)
            .split()
        )

        stats.audience.score = int(audience_score_attr) if audience_score_attr else None
        if audience_review_count:
            stats.audience.review_count = audience_review_count[0]

        stats.critic.score = (
            int(tomatometer_score_attr) if tomatometer_score_attr else None
        )
        if tomatometer_review_count:
            stats.critic.review_count = tomatometer_review_count[0]

        return stats

    @staticmethod
    def __search_page_has_results(html: HTMLParser) -> bool:
        page_heading = html.css_first("h1")
        return (
            "search__no-results-header"
            not in page_heading.attrs.get("class", "").split()
        )

    @staticmethod
    def __get_title_and_link(movie: Node) -> tuple[str, str]:
        link_node = movie.css_first('a[data-qa="info-name"]')
        return link_node.text(strip=True), link_node.attrs.get("href")

    def __get_movie_url(self, html: HTMLParser, movie_title: str) -> str | None:
        """Given a movie title, searches rottentomatoes for it and returns a
        URL for the movie details page."""
        if not self.__search_page_has_results(html):
            print(f"No search results for movie '{movie_title}'")
            return None

        movie_search_results_node = html.css_first('search-page-result[type="movie"]')
        if not movie_search_results_node:
            print(f"No movie search result node found for '{movie_title}'")
            return None

        # Return link for the movie with the matching title
        movie_search_results = movie_search_results_node.css("search-page-media-row")
        for movie_node in movie_search_results:
            title, movie_url = self.__get_title_and_link(movie_node)
            if title.upper() == movie_title.upper():
                return movie_url
        else:
            # Fall back to the first movie if no movie title matches exactly
            if movie_search_results:
                __, movie_url = self.__get_title_and_link(movie_search_results[0])
                return movie_url

        return None

    async def run(self, movie_title: str) -> MovieReviewStats | None:
        search_url = SEARCH_URL.format(search=urllib.parse.quote(movie_title))
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            search_page_html = await self._get_html(page, search_url)

            movie_url = self.__get_movie_url(search_page_html, movie_title)
            if movie_url is None:
                await browser.close()
                return

            movie_page_html = await self._get_html(page, movie_url)
            await browser.close()

            return self.__parse_movie_scores(movie_page_html, movie_url)
