from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from app.config import MongoConfig


async def init_mongodb():
    client = AsyncIOMotorClient(MongoConfig.MONGO_URL)
    database = getattr(client, MongoConfig.MONGO_DATABASE_NAME)

    await init_beanie(database=database, document_models=[])
