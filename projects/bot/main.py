import asyncio
import logging
import os
from datetime import datetime

from dotenv import load_dotenv

from database import database as db
from database.models import Movie
from projects.bot import HttpxHtmlParser
from projects.bot.scrapers import RottenTomatoesMovieListScraper, RottenTomatoesMovieReviewScraper


async def scrape_recent_movies():
    """Scrapes recent movies and adds/updates the database with the results."""
    scraper = RottenTomatoesMovieListScraper(HttpxHtmlParser())
    for movie in await scraper.run():
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
    scraper = RottenTomatoesMovieReviewScraper(HttpxHtmlParser())
    for review in await scraper.run(movies):
        await review.save()


async def main():
    load_dotenv()
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    logger.debug(f"Started executing at {datetime.now().isoformat()}")

    await db.init_database(os.getenv("DATABASE_URL"))

    await scrape_recent_movies()
    await scrape_movie_reviews()

    logger.debug(f"Finished executing at {datetime.now().isoformat()}")


if __name__ == "__main__":
    asyncio.run(main())
