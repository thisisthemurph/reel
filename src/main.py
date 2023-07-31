import os
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client

from src.repositories import MoviesRepo, ReviewsRepo
from src.scrapers.boxofficemojo_movie_list_scraper import BoxOfficeMojoMovieListScraper
from src.scrapers.rottentomatoes_movie_review_scraper import (
    RottenTomatoesMovieReviewScraper,
)


async def scrape_recent_movies(movies_repo: MoviesRepo):
    """Scrapes recent movies and adds/updates the database with the results."""
    scraper = BoxOfficeMojoMovieListScraper()
    for movie in await scraper.run(year=datetime.now().year):
        existing_movie = movies_repo.get_by_title(movie.title)
        if existing_movie is None:
            movies_repo.add(movie)
        elif movie != existing_movie:
            movies_repo.update(existing_movie.id, movie)


async def scrape_movie_reviews(movies_repo: MoviesRepo, reviews_repo: ReviewsRepo):
    """Scrapes reviews from rotten tomatoes for all movies in the database."""
    movies = movies_repo.all()
    scraper = RottenTomatoesMovieReviewScraper()
    for review in await scraper.run(movies):
        reviews_repo.add(review)


async def main():
    load_dotenv()
    supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
    movies_repo = MoviesRepo(supabase)
    reviews_repo = ReviewsRepo(supabase)

    await scrape_recent_movies(movies_repo)
    await scrape_movie_reviews(movies_repo, reviews_repo)


if __name__ == "__main__":
    asyncio.run(main())
