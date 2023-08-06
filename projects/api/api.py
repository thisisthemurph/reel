import os
import asyncio

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from tortoise.contrib.fastapi import register_tortoise

from database import database as db
from database.models import Movie, Review

api = FastAPI()
api.mount("/static", StaticFiles(directory="projects/api/static"), name="static")
templates = Jinja2Templates(directory="projects/api/templates")

load_dotenv()
database_url = os.getenv("DATABASE_URL")


async def init():
    await db.init_database(database_url)


@api.get("/", response_class=HTMLResponse)
async def index(request: Request):
    # TODO: Figure out how to force tortoise-orm to use an INNER JOIN and remove raw SQL
    top_movies: list[Movie] = await Movie.raw(
        """SELECT m.*, r.audience_score, r.audience_count
        FROM movies m
        INNER JOIN reviews r
            ON m.id = r.movie_id
        WHERE m.release_date >= CURRENT_DATE - INTERVAL '30 days' 
        ORDER BY m.release_date DESC NULLS LAST
        LIMIT(5)"""
    )

    for movie in top_movies:
        await movie.fetch_related("reviews")

    ctx = dict(request=request, movies=top_movies)
    return templates.TemplateResponse("pages/home.html", ctx)


@api.get("/m/{movie_id}", response_class=HTMLResponse)
async def movie_page(request: Request, movie_id: int):
    movie = await Movie.filter(id=movie_id).first()
    if movie:
        await movie.fetch_related("reviews")

    ctx = dict(request=request, movie=movie)
    return templates.TemplateResponse("pages/movie.html", ctx)


if __name__ == "__main__":
    asyncio.run(init())

register_tortoise(
    api,
    db_url=database_url,
    modules={"models": db.MODELS_PATHS},
    generate_schemas=True,
    add_exception_handlers=True,
)
