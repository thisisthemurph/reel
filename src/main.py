import os
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from dataclasses import dataclass
from supabase import Client, create_client

from src.repositories import MoviesRepo
from src.scrapers.boxofficemojo_movie_list_scraper import BoxOfficeMojoMovieListScraper


@dataclass
class SupabaseConfig:
    url: str
    key: str


async def scrape_recent_movies(
    movies_repo: MoviesRepo, scraper: BoxOfficeMojoMovieListScraper
):
    """Scrapes recent movies and adds/updates the database with the results."""
    for movie in await scraper.run(year=datetime.now().year):
        existing_movie = movies_repo.get_by_title(movie.title)
        if existing_movie is None:
            movies_repo.add(movie)
        elif movie != existing_movie:
            movies_repo.update(existing_movie.id, movie)


def make_supabase_config() -> SupabaseConfig:
    return SupabaseConfig(url=os.getenv("SUPABASE_URL"), key=os.getenv("SUPABASE_KEY"))


async def main():
    load_dotenv()
    supabase_config = make_supabase_config()
    supabase: Client = create_client(supabase_config.url, supabase_config.key)
    movies_repo = MoviesRepo(supabase)
    scraper = BoxOfficeMojoMovieListScraper()

    await scrape_recent_movies(movies_repo, scraper)


if __name__ == "__main__":
    asyncio.run(main())
