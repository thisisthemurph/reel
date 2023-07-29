from supabase import Client
from src.models import Movie
from src.repositories.table import Table


class MoviesRepo:
    def __init__(self, supabase: Client):
        self.supabase = supabase

    def add(self, movie: Movie):
        self.supabase.table(Table.Movies).insert(movie.supabase_dict).execute()

    def update(self, movie_id: int, movie: Movie):
        self.supabase.table(Table.Movies).update(movie.supabase_dict).eq(
            "id", movie_id
        ).execute()

    def get_by_title(self, title: str) -> Movie | None:
        movie = (
            self.supabase.table(Table.Movies)
            .select("*")
            .eq("title", title)
            .limit(1)
            .execute()
        )

        return Movie.from_dict(movie.data[0]) if movie.data else None
