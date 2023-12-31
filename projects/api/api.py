import os
import asyncio
import urllib.parse

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from tortoise.contrib.fastapi import register_tortoise

from database import database as db
from database.models import MovieModel


load_dotenv()
database_url = os.getenv("DATABASE_URL")
static_dir = "static" if os.getcwd().endswith("api") else "projects/api/static"
templates_dir = "templates" if os.getcwd().endswith("api") else "projects/api/templates"

api = FastAPI()
api.mount("/static", StaticFiles(directory=static_dir), name="static")
templates = Jinja2Templates(directory=templates_dir)


@api.get("/", response_class=HTMLResponse)
async def index(request: Request):
    # TODO: Figure out how to force tortoise-orm to use an INNER JOIN and remove raw SQL
    top_movies: list[MovieModel] = await MovieModel.raw(
        """SELECT m.*, r.audience_score, r.audience_count
        FROM movies m
        INNER JOIN movie_sources s
            ON m.id = s.movie_id
        INNER JOIN reviews r
            ON s.id = r.source_id
        WHERE m.release_date >= CURRENT_DATE - INTERVAL '30 days'
        ORDER BY m.release_date DESC NULLS LAST
        LIMIT(5)"""
    )

    for movie in top_movies:
        await movie.fetch_related("sources", "sources__reviews")

    ctx = dict(request=request, movies=top_movies)
    print(top_movies)
    return templates.TemplateResponse("pages/home.html", ctx)


@api.get("/m/{movie_id}", response_class=HTMLResponse)
async def movie_page(request: Request, movie_id: int, return_url: str | None = None):
    movie = await MovieModel.filter(id=movie_id).first()
    if movie:
        await movie.fetch_related("sources__reviews")

    print(return_url)

    ctx = dict(request=request, movie=movie, return_url=return_url)
    return templates.TemplateResponse("pages/movie.html", ctx)


@api.get("/s", response_class=HTMLResponse)
async def search_movie(request: Request, q: str):
    await MovieModel.filter()
    movies = await MovieModel.filter(title__icontains=q)

    for movie in movies:
        await movie.fetch_related("sources__reviews")

    ctx = dict(request=request, movies=movies, query=q)
    return templates.TemplateResponse("pages/search-results.html", ctx)


async def main():
    await db.init_database(database_url)
    config = uvicorn.Config("api:api", port=5000, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())

register_tortoise(
    api,
    db_url=database_url,
    modules={"models": db.MODELS_PATHS},
    generate_schemas=True,
    add_exception_handlers=True,
)
