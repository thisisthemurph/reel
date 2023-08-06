from tortoise import Tortoise

from database import MODELS_PATHS


async def init_database(database_url: str):
    Tortoise.init_models(MODELS_PATHS, "models")
    await Tortoise.init(
        db_url=database_url,
        modules=dict(models=MODELS_PATHS),
    )

    await Tortoise.generate_schemas()
