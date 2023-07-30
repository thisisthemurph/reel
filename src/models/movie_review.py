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
    def __init__(self):
        self.critic = MovieReview()
        self.audience = MovieReview()

    def __str__(self):
        return (
            f"{self.__class__.__name__}(critic={self.critic}, audience={self.audience})"
        )
