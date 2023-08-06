from datetime import datetime, timezone

from tortoise import fields
from tortoise.fields import ForeignKeyRelation
from tortoise.models import Model


class Movie(Model):
    id = fields.IntField(pk=True)
    title = fields.TextField()
    rank = fields.IntField()
    release_date = fields.DateField(null=True)
    distributor = fields.TextField(null=True)
    created_at = fields.DatetimeField(default=datetime.now(timezone.utc))

    reviews: fields.ReverseRelation["Review"]

    class Meta:
        table = "movies"

    def __repr__(self):
        return f"Movie(title={self.title})"

    def __str__(self):
        return self.__repr__()

    def __eq__(self, other):
        """Determines if the same movie, does not check based on PK"""
        if not isinstance(other, Movie):
            return False

        return (
            self.title == other.title
            and self.rank == other.rank
            and self.release_date == other.release_date
            and self.distributor == other.distributor
        )


class Review(Model):
    movie: ForeignKeyRelation[Movie] = fields.ForeignKeyField(
        "models.Movie", related_name="reviews", description="FK to movie"
    )

    site = fields.TextField()
    audience_score = fields.IntField(null=True)
    audience_count = fields.TextField(null=True)
    critic_score = fields.IntField(null=True)
    critic_count = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "reviews"

    def __repr__(self):
        return (
            f"Review(site={self.site}, audience={self.audience_score}, critic={self.critic_score})"
        )

    def __str__(self):
        return self.__repr__()
