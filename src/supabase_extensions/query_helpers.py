from typing import Any
from postgrest import SyncSelectRequestBuilder


def eq_with_null(query: SyncSelectRequestBuilder, column: str, value: Any) -> None:
    """Supabase extension fn to .eq on the value or filter with `is null` if value is None."""
    if value is None:
        query.filter(column, "is", "null")
    else:
        query.eq(column, value)
