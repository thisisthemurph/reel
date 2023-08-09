import urllib.parse

import httpx
from selectolax.parser import HTMLParser, Node

from database.models import MovieModel
from projects.bot import HtmlParserProtocol, sites, HttpxHtmlParser
from projects.bot.result_models import ReviewResult

SEARCH_URL = "https://www.rottentomatoes.com/search?search={search}"


class IMDBMovieReviewScraper:
    def __init__(self, scraper: HtmlParserProtocol):
        self.scraper = scraper
        self.logger = scraper.logger

    def __parse_reviews(self, parser: HTMLParser, source_id: int | None, url: str) -> ReviewResult:
        """Parses the rottentomatoes scores from the movie details page"""
        imdb_rating_node = parser.css_first("span.sc-5931bdee-1.jUnWeS")
        imdb_count_node = parser.css_first("div.sc-5931bdee-3.dWymrF")
        user_rating_node = parser.css_first('p[data-testid="calculations-label"]')

        imdb_rating, user_rating = None, None
        if imdb_rating_node:
            imdb_rating = imdb_rating_node.text(strip=True)
        if user_rating_node:
            user_rating = user_rating_node.text(strip=True)

        return ReviewResult(
            source_id=source_id,
            audience_score=int(float(user_rating.split(" ", 1)[0]) * 10),
            audience_count=None,
            critic_score=int(float(imdb_rating) * 10) if imdb_rating else None,
            critic_count=imdb_count_node.text(strip=True) if imdb_count_node else None,
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

    # def __get_movie_url(self, parser: HTMLParser, movie_title: str) -> str | None:
    #     """Given a movie title, searches IMDB for it and returns a URL for the movie details page."""

    async def run(self, movies: list[MovieModel]) -> list[ReviewResult]:
        movie_reviews: list[ReviewResult] = []
        async with httpx.AsyncClient() as client:
            for movie in movies:
                sources = [s for s in movie.sources if s.name == sites.IMDB]
                source = sources[0] if len(sources) else None

                if not source:
                    continue

                ratings_url = urllib.parse.urljoin(source.url, "ratings")
                print(ratings_url)
                parser = await self.scraper.get_html_parser(client, ratings_url)

                if parser is not None:
                    review = self.__parse_reviews(parser, source.id, source.url)
                    review.movie_id = movie.id
                    movie_reviews.append(review)

        return movie_reviews
