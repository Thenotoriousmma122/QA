import asyncio
import logging
from aiogram import Bot,Dispatcher

from app.handlers.registration import register_router
from app.handlers.api import api_router
from app.handlers.client import client
from app.database.models import init_models
from aiogram.fsm.storage.redis import RedisStorage
import redis.asyncio as aioredis
import os

from dotenv import load_dotenv

from app.handlers.usersbox import usersbox_router

load_dotenv()

async def startup():
    await init_models()
'''''
async def test():
    print(await get_weathers(51.1605, 71.4704))  # пример: Астана
asyncio.run(test())
'''''

async def main():
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=os.getenv('TG_TOKEN'))

    redis_host = os.getenv("REDIS_HOST")
    redis_port = os.getenv("REDIS_PORT")
    redis_db = os.getenv("Redis_DB")
    redis = await aioredis.from_url(f'redis://{redis_host}:{redis_port}/{redis_db}')

    dp = Dispatcher(storage=RedisStorage(redis))
    dp.include_routers(register_router, api_router, client, usersbox_router)


    dp.startup.register(startup)
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info('Bot was stopped')

