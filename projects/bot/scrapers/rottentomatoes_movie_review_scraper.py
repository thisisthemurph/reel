import urllib.parse

import httpx
from httpx import AsyncClient
from selectolax.parser import HTMLParser, Node

from database.models import MovieModel
from projects.bot import HtmlParserProtocol, sites
from projects.bot.result_models import ReviewResult

SEARCH_URL = "https://www.rottentomatoes.com/search?search={search}"


class RottenTomatoesMovieReviewScraper:
    def __init__(self, scraper: HtmlParserProtocol):
        self.scraper = scraper
        self.logger = scraper.logger

    @staticmethod
    def __parse_audience_scoreboard(score_board_node: Node):
        css_query = 'a[data-qa="audience-rating-count"]'
        audience_score_attr = score_board_node.attrs.get("audiencescore")
        audience_rating_count_elem = score_board_node.css_first(css_query)
        audience_rating_count = (
            audience_rating_count_elem.text(strip=True).split()
            if audience_rating_count_elem
            else None
        )

        return (
            int(audience_score_attr) if audience_score_attr else None,
            audience_rating_count[0] if audience_rating_count else None,
        )

    @staticmethod
    def __parse_critic_scoreboard(score_board_node: Node):
        css_query = 'a[data-qa="tomatometer-review-count"]'
        critic_score_attr = score_board_node.attrs.get("tomatometerscore")
        critic_review_count_elem = score_board_node.css_first(css_query)
        critic_review_count = (
            critic_review_count_elem.text(strip=True) if critic_review_count_elem else None
        )

        return (
            int(critic_score_attr) if critic_score_attr else None,
            critic_review_count,
        )

    def __parse_reviews(self, parser: HTMLParser, source_id: int | None, url: str) -> ReviewResult:
        """Parses the rottentomatoes scores from the movie details page"""
        score_board_node = parser.css_first("score-board")
        if not score_board_node:
            self.logger.debug(f"No score-board element at '{url}'")
            return ReviewResult(source_id, None, None, None, None)

        audience_score, audience_count = self.__parse_audience_scoreboard(score_board_node)
        critic_score, critic_count = self.__parse_critic_scoreboard(score_board_node)

        return ReviewResult(
            source_id=source_id,
            audience_score=audience_score,
            audience_count=audience_count,
            critic_score=critic_score,
            critic_count=critic_count,
        )

    @staticmethod
    def __search_page_has_results(parser: HTMLParser) -> bool:
        """Determines if the search page has any movies present or not."""
        page_heading = parser.css_first("h1")
        return "search__no-results-header" not in page_heading.attrs.get("class", "").split()

    @staticmethod
    def __get_title_and_link(movie_node: Node) -> tuple[str, str]:
        """Returns the title and url link to the movie."""
        link_node = movie_node.css_first('a[data-qa="info-name"]')
        return link_node.text(strip=True), link_node.attrs.get("href")

    def __get_movie_url(self, parser: HTMLParser, movie_title: str) -> str | None:
        """Given a movie title, searches rottentomatoes for it and returns a URL for the movie details page."""
        if not self.__search_page_has_results(parser):
            self.logger.debug(f"No search results for movie '{movie_title}'")
            return None

        movie_search_results_node = parser.css_first('search-page-result[type="movie"]')
        if not movie_search_results_node:
            self.logger.debug(f"No movie search result node found for '{movie_title}'")
            return None

        # Return link for the movie with the matching title or default to first movie
        movie_search_results = movie_search_results_node.css("search-page-media-row")
        for movie_node in movie_search_results:
            title, movie_url = self.__get_title_and_link(movie_node)
            if title.upper() == movie_title.upper():
                return movie_url
        else:
            self.logger.debug(f"Match not found for '{movie_title}', falling back to first movie")
            if movie_search_results:
                __, movie_url = self.__get_title_and_link(movie_search_results[0])
                return movie_url

        self.logger.debug("Fallback failed, movie list is empty")
        return None

    async def get_movie_urls(
        self, c: AsyncClient, movies: list[MovieModel]
    ) -> list[tuple[int, str]]:
        """Searches the website for the movies and returns a list or urls for the movie pages."""
        all_movie_urls: list[tuple[int, str]] = []
        for movie in movies:
            search_url = SEARCH_URL.format(search=urllib.parse.quote(movie.title))
            parser = await self.scraper.get_html_parser(c, search_url)
            if parser is not None:
                movie_url = self.__get_movie_url(parser, movie.title)
                if movie_url is not None:
                    all_movie_urls.append((movie.id, movie_url))

        return all_movie_urls

    async def run(self, movies: list[MovieModel]) -> list[ReviewResult]:
        movie_reviews: list[ReviewResult] = []
        async with httpx.AsyncClient() as client:
            for movie in movies:
                sources = [s for s in movie.sources if s.name == sites.ROTTENTOMATOES]
                source = sources[0] if len(sources) else None
                parser = await self.scraper.get_html_parser(client, source.url)
                if parser is not None:
                    review = self.__parse_reviews(parser, source.id, source.url)
                    review.movie_id = movie.id
                    movie_reviews.append(review)

        return movie_reviews
