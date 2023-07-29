from supabase import Client
from src.models import Film
from typing import Literal

MOVIES_TABLE: Literal["films"] = "films"


class MoviesRepo:
    def __init__(self, supabase: Client):
        self.supabase = supabase

    def add(self, film: Film):
        self.supabase.table(MOVIES_TABLE).insert(film.supabase_dict).execute()

    def update(self, film_id: int, film: Film):
        self.supabase.table(MOVIES_TABLE).update(film.supabase_dict).eq(
            "id", film_id
        ).execute()

    def get_by_title(self, title: str) -> Film | None:
        film = (
            self.supabase.table(MOVIES_TABLE)
            .select("*")
            .eq("title", title)
            .limit(1)
            .execute()
        )
        
        return Film.from_dict(film.data[0]) if film.data else None
