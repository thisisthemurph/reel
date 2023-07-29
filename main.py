import os
import asyncio
from enum import Enum
from datetime import datetime
from dotenv import load_dotenv
from dataclasses import dataclass
from supabase import Client, create_client

from models import Film
from scrapers import mojoranking_scrape


class Table(Enum):
    FILMS = "films"

    def __str__(self):
        return str(self.value)


@dataclass
class SupabaseConfig:
    url: str
    key: str


async def get_film_rankings(supabase: Client):
    for film in await mojoranking_scrape.run(year=datetime.now().year):
        existing_film = get_film_by_title(film.title, supabase)
        if existing_film is None:
            add_film(film, supabase)
        elif film != existing_film:
            update_film(existing_film.id, film, supabase)


def add_film(film: Film, supabase: Client):
    supabase.table(Table.FILMS).insert(film.supabase_dict).execute()


def update_film(film_id: int, film: Film, supabase: Client):
    supabase.table(Table.FILMS).update(film.supabase_dict).eq("id", film_id).execute()


def get_film_by_title(title: str, supabase: Client) -> Film | None:
    film = supabase.table(Table.FILMS).select("*").eq("title", title).limit(1).execute()
    return Film.from_dict(film.data[0]) if film.data else None


async def main():
    load_dotenv()
    supabase_config = SupabaseConfig(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
    supabase: Client = create_client(supabase_config.url, supabase_config.key)
    await get_film_rankings(supabase)


if __name__ == "__main__":
    asyncio.run(main())
