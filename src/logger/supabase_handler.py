import logging
from datetime import datetime
from supabase import Client


class SupabaseHandler(logging.Handler):
    """A handler class which writes logging records to Supabase."""

    def __init__(self, supabase: Client):
        super().__init__()
        self.supabase = supabase

    def emit(self, record: logging.LogRecord) -> None:
        log = dict(
            name=record.name,
            level=record.levelno,
            level_name=record.levelname,
            message=self.format(record),
            created_unix=record.created,
            created=datetime.utcfromtimestamp(record.created).isoformat(),
            file_name=record.filename,
            path_name=record.pathname,
        )

        self.supabase.table("logs").insert(log).execute()
