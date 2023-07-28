from datetime import date, datetime


class Film:
    def __init__(self, title: str, rank: int, release_date: date, distributor: str):
        self.title = title
        self.rank = rank
        self.release_date = release_date
        self.distributor = distributor

        self.id: int | None = None
        self.created_at = None

    @classmethod
    def from_dict(cls, d):
        release_date = datetime.strptime(d["release_date"], "%Y-%m-%d").date()
        film = cls(d["title"], int(d["rank"]), release_date, d["distributor"])

        # If the film has been fetched from Supabase, it will have additional properties
        film.id = d["id"] if "id" in d else None
        film.created_at = d["created_at"] if "created_at" in d else None

        return film

    @property
    def supabase_dict(self):
        return dict(
            rank=self.rank,
            title=self.title,
            release_date=str(self.release_date),
            distributor=self.distributor,
        )

    def __eq__(self, other):
        if not isinstance(other, Film):
            return False

        return (self.title == other.title
                and self.rank == other.rank
                and self.release_date == other.release_date
                and self.distributor == other.distributor
                )
