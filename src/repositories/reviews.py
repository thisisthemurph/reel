from supabase import Client

from ..models import MovieReviewStats
from ..repositories.table import Table
from ..supabase_extensions import eq_with_null


class ReviewsRepo:
    def __init__(self, supabase: Client):
        self.supabase = supabase

    def add(self, review: MovieReviewStats):
        """Adds a review to the database if a duplicate does not already exist."""
        if not self.has_matching(review):
            self.supabase.table(Table.Reviews).insert(review.supabase_dict()).execute()

    def has_matching(self, review: MovieReviewStats) -> bool:
        """Determines if there is a matching review based on associated movie_id, site, and review stats.
        This does not take into consideration the reviews table's primary key."""
        if review.movie_id is None:
            raise Exception("Movie id is none!")

        # The `maybe_single` method does not seem to work
        # A ticket has been raised on the supabase-py repository
        # https://github.com/supabase-community/supabase-py/issues/511
        query = (
            self.supabase.table(Table.Reviews)
            .select("*")
            .eq("movie_id", review.movie_id)
            .eq("site", review.site)
        )

        eq_with_null(query, "audience_score", review.audience.score)
        eq_with_null(query, "audience_count", review.audience.review_count)
        eq_with_null(query, "critic_score", review.critic.score)
        eq_with_null(query, "critic_count", review.critic.review_count)

        response = query.execute()
        return len(response.data) >= 1
