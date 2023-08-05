import logging


class MinLevelAndAboveFilter(logging.Filter):
    def __init__(self, min_level_no: int):
        super().__init__()
        self.min_level_no = min_level_no

    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno >= self.min_level_no
