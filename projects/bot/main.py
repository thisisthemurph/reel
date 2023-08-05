import asyncio
from datetime import datetime

from dotenv import load_dotenv

from database import database as db
from database.models import Movie
from libs.supalogger import make_logger
from projects.bot import HtmlParserProtocol
from projects.bot.boxofficemojo_movie_list_scraper import BoxOfficeMojoMovieListScraper
from projects.bot.rottentomatoes_movie_review_scraper import RottenTomatoesMovieReviewScraper


async def scrape_recent_movies():
    """Scrapes recent movies and adds/updates the database with the results."""
    scraper = BoxOfficeMojoMovieListScraper(HtmlParserProtocol.httpx_scraper())
    for movie in await scraper.run(year=datetime.now().year):
        existing_movie = await Movie.filter(title=movie.title).first()

        # The movie already exists
        if existing_movie and existing_movie == movie:
            continue

        # The movie exists but needs updating
        if existing_movie:
            existing_movie.title = movie.title
            existing_movie.rank = movie.rank
            existing_movie.release_date = movie.release_date
            existing_movie.distributor = movie.distributor
            await existing_movie.save()
            continue

        await movie.save()


async def scrape_movie_reviews():
    """Scrapes reviews from rotten tomatoes for all movies in the database."""
    movies = await Movie.all()
    scraper = RottenTomatoesMovieReviewScraper(HtmlParserProtocol.httpx_scraper())
    for review in await scraper.run(movies):
        await review.save()


async def main():
    load_dotenv()
    logger = make_logger(__name__)
    logger.debug(f"Started executing at {datetime.now().isoformat()}")

    await db.init_database()

    await scrape_recent_movies()
    await scrape_movie_reviews()

    logger.debug(f"Finished executing at {datetime.now().isoformat()}")


if __name__ == "__main__":
    asyncio.run(main())
