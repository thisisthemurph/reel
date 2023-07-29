import os
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from dataclasses import dataclass
from supabase import Client, create_client

from src.repositories import MoviesRepo
from src.scrapers import mojoranking_scrape


@dataclass
class SupabaseConfig:
    url: str
    key: str


async def scrape_recent_movies(movies_repo: MoviesRepo):
    """Scrapes recent movies and adds/updates the database with the results."""
    for movie in await mojoranking_scrape.run(year=datetime.now().year):
        existing_movie = movies_repo.get_by_title(movie.title)
        if existing_movie is None:
            movies_repo.add(movie)
        elif movie != existing_movie:
            movies_repo.update(existing_movie.id, movie)


def make_supabase_config() -> SupabaseConfig:
    return SupabaseConfig(url=os.getenv("SUPABASE_URL"), key=os.getenv("SUPABASE_KEY"))


async def run(movies_repo: MoviesRepo):
    await scrape_recent_movies(movies_repo)


async def main():
    load_dotenv()
    supabase_config = make_supabase_config()
    supabase: Client = create_client(supabase_config.url, supabase_config.key)
    movies_repo = MoviesRepo(supabase)

    await run(movies_repo)


if __name__ == "__main__":
    asyncio.run(main())
