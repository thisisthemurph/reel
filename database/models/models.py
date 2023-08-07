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

    id = fields.IntField(pk=True)
    name = fields.TextField()
    url = fields.TextField()

    reviews: fields.ReverseRelation["ReviewModel"]

    class Meta:
        table = "movie_sources"

    def __repr__(self):
        return f"Source(title={self.name}, url={self.url})"

    def __str__(self):
        return self.__repr__()


class ReviewModel(Model):
    source: ForeignKeyRelation[MovieModel] = fields.ForeignKeyField(
        "models.SourceModel", related_name="reviews", description="FK to a movie source"
    )

    audience_score = fields.IntField(null=True)
    audience_count = fields.TextField(null=True)
    critic_score = fields.IntField(null=True)
    critic_count = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "reviews"

    def __repr__(self):
        return f"Review(audience={self.audience_score}, critic={self.critic_score})"

    def __str__(self):
        return self.__repr__()
