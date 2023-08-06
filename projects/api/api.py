import os
import asyncio
from datetime import datetime, timedelta

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from tortoise.contrib.fastapi import register_tortoise
from tortoise.expressions import Q

from database import database as db
from database.models import Movie

api = FastAPI()
templates = Jinja2Templates(directory="projects/api/templates")

load_dotenv()
database_url = os.getenv("DATABASE_URL")


async def init():
    await db.init_database(database_url)


@api.get("/", response_class=HTMLResponse)
async def index(request: Request):
    delta = datetime.now().date() - timedelta(days=30)
    movies_by_review_and_release_date = (
        await Movie.filter(release_date__gte=delta)
        .prefetch_related("reviews")
        .order_by("-reviews__audience_score", "-release_date")
    )

    # TODO: Figure out how to force tortoise-orm to use an INNER JOIN
    top_movies: list[Movie] = []
    for movie in movies_by_review_and_release_date[:5]:
        if len(movie.reviews):
            top_movies.append(movie)

    ctx = dict(request=request, movies=top_movies)
    return templates.TemplateResponse("pages/home.html", ctx)


if __name__ == "__main__":
    asyncio.run(init())

register_tortoise(
    api,
    db_url=database_url,
    modules={"models": db.MODELS_PATHS},
    generate_schemas=True,
    add_exception_handlers=True,
)
