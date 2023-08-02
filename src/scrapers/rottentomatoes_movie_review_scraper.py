import urllib.parse
from playwright.async_api import async_playwright
from selectolax.parser import HTMLParser, Node

from . import HTMLScraper
from src.models import Movie
from src.models.movie_review import MovieReviewStats

SEARCH_URL = "https://www.rottentomatoes.com/search?search={search}"


class RottenTomatoesMovieReviewScraper:
    def __init__(self, scraper: HTMLScraper):
        self.scraper = scraper
        self.logger = scraper.logger

    def __parse_movie_scores(self, html: HTMLParser, url: str) -> MovieReviewStats:
        """Parses the rottentomatoes scores from the movie details page"""
        stats = MovieReviewStats("rottentomatoes")
        score_board_elem = html.css_first("score-board")
        if not score_board_elem:
            self.logger.debug(f"No score-board element at '{url}'")
            return stats

        audience_score_attr = score_board_elem.attrs.get("audiencescore")
        audience_rating_count_elem = score_board_elem.css_first(
            'a[data-qa="audience-rating-count"]'
        )
        audience_rating_count = (
            audience_rating_count_elem.text(strip=True).split()
            if audience_rating_count_elem
            else None
        )

        tomatometer_score_attr = score_board_elem.attrs.get("tomatometerscore")
        tomatometer_review_count_elem = score_board_elem.css_first(
            'a[data-qa="tomatometer-review-count"]'
        )
        tomatometer_review_count = (
            tomatometer_review_count_elem.text(strip=True)
            if tomatometer_review_count_elem
            else None
        )

        stats.audience.score = int(audience_score_attr) if audience_score_attr else None
        if audience_rating_count:
            stats.audience.review_count = audience_rating_count[0]

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
            self.logger.debug(f"No search results for movie '{movie_title}'")
            return None

        movie_search_results_node = html.css_first('search-page-result[type="movie"]')
        if not movie_search_results_node:
            self.logger.debug(f"No movie search result node found for '{movie_title}'")
            return None

        # Return link for the movie with the matching title
        movie_search_results = movie_search_results_node.css("search-page-media-row")
        for movie_node in movie_search_results:
            title, movie_url = self.__get_title_and_link(movie_node)
            if title.upper() == movie_title.upper():
                return movie_url
        else:
            # Fall back to the first movie if no movie title matches exactly
            self.logger.debug(
                f"Match not found for {movie_title}, falling back to first movie"
            )
            if movie_search_results:
                __, movie_url = self.__get_title_and_link(movie_search_results[0])
                return movie_url

        self.logger.debug("Fallback failed, movie list is empty")
        return None

    async def run(self, movies: list[Movie]) -> list[MovieReviewStats]:
        stat_results: list[MovieReviewStats] = []
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()

            for movie in movies:
                search_url = SEARCH_URL.format(search=urllib.parse.quote(movie.title))
                search_page_html = await self.scraper.get_html(page, search_url)
                if search_page_html is None:
                    continue

                movie_url = self.__get_movie_url(search_page_html, movie.title)
                if movie_url is None:
                    continue

                movie_page_html = await self.scraper.get_html(page, movie_url)
                if movie_page_html is None:
                    continue

                stats = self.__parse_movie_scores(movie_page_html, movie_url)
                stats.movie_id = movie.id
                stat_results.append(stats)

            await browser.close()
        return stat_results
