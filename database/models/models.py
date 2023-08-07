from tortoise import fields
from tortoise.fields import ForeignKeyRelation
from tortoise.models import Model

from projects.bot.result_models import MovieResult


class MovieModel(Model):
    id = fields.IntField(pk=True)
    title = fields.TextField()
    release_date = fields.DateField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    reviews: fields.ReverseRelation["ReviewModel"]
    sources: fields.ReverseRelation["SourceModel"]

    class Meta:
        table = "movies"

    def __repr__(self):
        return f"Movie(title={self.title})"

    def __str__(self):
        return self.__repr__()

    def __eq__(self, other):
        """Determines if the same movie, does not check based on PK"""
        if isinstance(other, MovieModel):
            return self.title == other.title and self.release_date == other.release_date

        if isinstance(other, MovieResult):
            return self.title == other.title and self.release_date == other.release_date

        return False


class SourceModel(Model):
    movie: ForeignKeyRelation[MovieModel] = fields.ForeignKeyField(
        "models.MovieModel", related_name="sources", description="FK to movie"
    )

    name = fields.TextField()
    url = fields.TextField()

    class Meta:
        table = "movie_sources"

    def __repr__(self):
        return f"Source(title={self.name}, url={self.url})"

    def __str__(self):
        return self.__repr__()


class ReviewModel(Model):
    movie: ForeignKeyRelation[MovieModel] = fields.ForeignKeyField(
        "models.MovieModel", related_name="reviews", description="FK to movie"
    )

    site = fields.TextField()
    url = fields.TextField(null=True)
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
