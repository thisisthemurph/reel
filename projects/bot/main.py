import os
import asyncio
import logging
from datetime import datetime

from dotenv import load_dotenv

from database import database as db
from database.models import MovieModel, SourceModel, ReviewModel
from projects.bot import HttpxHtmlParser, sites
from projects.bot.scrapers import (
    RottenTomatoesMovieListScraper,
    RottenTomatoesMovieReviewScraper,
    IMDBMovieReviewScraper,
)
from projects.bot.scrapers.imdb_movie_list_scraper import IMDBMovieListScraper


async def scrape_recent_movies() -> list[MovieModel]:
    """Scrapes recent movies and adds/updates the database with the results."""
    rt_scraper = RottenTomatoesMovieListScraper(HttpxHtmlParser())
    imdb_scraper = IMDBMovieListScraper(HttpxHtmlParser())

    movie_results: list[MovieModel] = []
    scraped_movies = await asyncio.gather(rt_scraper.run(), imdb_scraper.run())
    scraped_movies = [m for movie_list in scraped_movies for m in movie_list]
    for movie in scraped_movies:
        existing_movie = (
            await MovieModel.filter(title=movie.title).prefetch_related("sources").first()
        )

        if existing_movie:
            # Update the movie if the details are different
            if existing_movie != movie:
                existing_movie.release_date = movie.release_date
                await existing_movie.save()

            # Add the source for the movie if it isn't there already
            # TODO: There could be an issue with the URL having changed for the movie source
            if movie.source.url not in [source.url for source in existing_movie.sources]:
                await SourceModel.get_or_create(
                    name=movie.source.name, url=movie.source.url, movie_id=existing_movie.id
                )

            movie_results.append(existing_movie)
        else:
            new_movie = await MovieModel.create(title=movie.title, release_date=movie.release_date)
            await SourceModel.create(
                name=movie.source.name, url=movie.source.url, movie_id=new_movie.id
            )

            await new_movie.fetch_related("sources")
            movie_results.append(new_movie)

    return movie_results


async def fill_missing_movie_sources(movies: list[MovieModel]):
    """Finds movie sources for movies that do not have a source from a given site."""
    rt_scraper = RottenTomatoesMovieReviewScraper(HttpxHtmlParser())
    # imdb_scraper = IMDBMovieReviewScraper(HttpxHtmlParser())

    rotten_tomato_movies = [
        m for m in movies if sites.ROTTENTOMATOES not in [s.name for s in m.sources]
    ]

    sources = await rt_scraper.get_sources(rotten_tomato_movies)
    for source in sources:
        await source.save()


async def scrape_movie_reviews():
    """Scrapes reviews from Rottentomatoes for all movies in the database."""
    movies = await MovieModel.all().prefetch_related("sources")
    rt_scraper = RottenTomatoesMovieReviewScraper(HttpxHtmlParser())
    imdb_scraper = IMDBMovieReviewScraper(HttpxHtmlParser())
    scraped_reviews = await asyncio.gather(rt_scraper.run(movies), imdb_scraper.run(movies))

    for review in [r for reviews in scraped_reviews for r in reviews]:
        if review.should_save():
            await ReviewModel.get_or_create(
                source_id=review.source_id,
                audience_score=review.audience_score,
                audience_count=review.audience_count,
                critic_score=review.critic_score,
                critic_count=review.critic_count,
            )


async def main():
    load_dotenv()
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    logger.debug(f"Started executing at {datetime.now().isoformat()}")

    await db.init_database(os.getenv("DATABASE_URL"))

    recent_movies = await scrape_recent_movies()
    await fill_missing_movie_sources(recent_movies)

    await scrape_movie_reviews()

    logger.debug(f"Finished executing at {datetime.now().isoformat()}")


if __name__ == "__main__":
    asyncio.run(main())
