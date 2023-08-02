import logging
import os

from supabase import create_client
from .filters import MinLevelAndAboveFilter
from .supabase_handler import SupabaseHandler


def make_logger(name: str) -> logging.Logger:
    supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
    handler = SupabaseHandler(supabase)
    handler.addFilter(MinLevelAndAboveFilter(logging.WARNING))

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    return logger
