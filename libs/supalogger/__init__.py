import logging
import os

from supabase import create_client
from .filters import MinLevelAndAboveFilter
from .supabase_handler import SupabaseHandler


def __get_log_level_from_env() -> int:
    """Returns the appropriate logging level. If in DEVELOPMENT uses DEBUG.
    If LOG_LEVEL int is set in environment variables, uses that. Otherwise, WARNING."""
    if os.getenv("ENVIRONMENT") == "development":
        return logging.DEBUG

    try:
        return int(os.getenv("LOG_LEVEL") or "")
    except ValueError:
        return logging.WARNING


def make_logger(name: str) -> logging.Logger:
    log_level = __get_log_level_from_env()
    supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

    handler = SupabaseHandler(supabase)
    handler.addFilter(MinLevelAndAboveFilter(logging.WARNING))

    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    logger.addHandler(handler)
    return logger
