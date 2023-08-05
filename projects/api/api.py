import asyncio
import datetime

from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from tortoise import Tortoise
from tortoise.contrib.fastapi import register_tortoise

from database.models import Movie, Review

MODELS_PATHS = ["database.models"]
DATABASE_URL = "postgres://postgres:GreenAli3n2001@localhost:5432/reel"

api = FastAPI()
templates = Jinja2Templates(directory="projects/api/templates")


async def init():
    Tortoise.init_models(MODELS_PATHS, "models")
    await Tortoise.init(
        db_url=DATABASE_URL,
        modules=dict(models=MODELS_PATHS),
    )

    await Tortoise.generate_schemas()

    register_tortoise(
        api,
        db_url=DATABASE_URL,
        modules={"models": MODELS_PATHS},
        generate_schemas=True,
        add_exception_handlers=True,
    )

    # await test_insert_movie()
    # await test_create_review()
    await loop_over_movies()


@api.get("/", response_class=HTMLResponse)
async def index(request: Request):
    r = await Movie.all().limit(5)
    ctx = dict(request=request, movies=r)
    return templates.TemplateResponse("pages/home.html", ctx)


async def test_insert_movie():
    movie = Movie(
        title="die hard", rank=1, release_date=datetime.datetime.now().date(), distributor="Mike"
    )
    await movie.save()


async def test_create_review():
    movie = await Movie.get(id=1).prefetch_related("reviews")
    await Review.create(
        site="tomatomater",
        audience_score=88,
        audience_count="9",
        critic_score=14,
        critic_count="4",
        movie=movie,
    )


async def loop_over_movies():
    movies = await Movie.all().prefetch_related("reviews")
    for movie in movies:
        print(movie)
        async for review in movie.reviews:
            print("\t", review)


if __name__ == "__main__":
    asyncio.run(init())
