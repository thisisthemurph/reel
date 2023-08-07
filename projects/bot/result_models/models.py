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
