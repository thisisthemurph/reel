import logging
from supabase import Client
from .filters import MinLevelAndAboveFilter
from .supabase_handler import SupabaseHandler


def make_logger(name: str, supabase: Client) -> logging.Logger:
    handler = SupabaseHandler(supabase)
    handler.addFilter(MinLevelAndAboveFilter(logging.WARNING))

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    return logger
