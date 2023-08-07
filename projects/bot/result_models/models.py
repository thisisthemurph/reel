from datetime import date
from dataclasses import dataclass


@dataclass
class SourceResult:
    name: str
    url: str


@dataclass
class MovieResult:
    title: str
    release_date: date | None
    source: SourceResult


@dataclass
class ReviewResult:
    source_id: int
    audience_score: int | None
    audience_count: str | None
    critic_score: int | None
    critic_count: str | None

    def should_save(self) -> bool:
        """Details if the item has enough data to warrant saving."""
        return self.source_id is not None and any(
            [
                self.audience_score is not None,
                self.audience_count is not None,
                self.critic_score is not None,
                self.critic_count is not None,
            ]
        )
