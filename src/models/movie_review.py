from datetime import datetime
from typing import TypedDict, NotRequired


class MovieReviewStatsDict(TypedDict):
    id: NotRequired[int | None]
    movie_id: int | None
    site: str
    created_at: str
    critic_score: int | None
    critic_count: str
    audience_score: int | None
    audience_count: str


class MovieReview:
    def __init__(self):
        self.score: int | None = None
        self.review_count: str = "0"

    def get_score(self, default: str = "-") -> str:
        """Returns the score as a percentage string, e.g: 12%. If no score, returns default param."""
        return f"{self.score}%" if self.score else default

    def __str__(self):
        return f"{self.__class__.__name__}(score: {self.get_score()}, review_count: {self.review_count})"


class MovieReviewStats:
    def __init__(self, site: str):
        self.id: int | None = None
        self.movie_id: int | None = None
        self.site = site
        self.critic = MovieReview()
        self.audience = MovieReview()
        self.created_at = datetime.now()

    def supabase_dict(self) -> MovieReviewStatsDict:
        review: MovieReviewStatsDict = dict(
            movie_id=self.movie_id,
            site=self.site,
            created_at=str(self.created_at),
            audience_score=self.audience.score,
            audience_count=self.audience.review_count,
            critic_score=self.critic.score,
            critic_count=self.critic.review_count,
        )

        if self.id is not None:
            review["id"] = self.id

        return review

    def __str__(self):
        return (
            f"{self.__class__.__name__}(critic={self.critic}, audience={self.audience})"
        )
