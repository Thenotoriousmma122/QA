from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.database.models import async_session, User, Card, Category, Photo
from sqlalchemy import select, update

async def check_user(tg_id:int):
    async with async_session() as session:
        if await session.scalar(select(User).where(User.tg_id==tg_id)):
            return True
        return False


async def get_categories():
    async with async_session() as session:
        return await session.scalars(select(Category))

async def get_card_by_category(category_id):
    category_id = int(category_id)
    async with async_session() as session:
        return await session.scalars(
            select(Card).where(Card.category_id == category_id)
        )

async def get_card(card_id):
    async with async_session() as session:
        return await session.scalar(select(Card).where(Card.id==card_id))

async def get_user(tg_id):
    async with async_session() as session:
        return await session.scalar(select(User).where(User.tg_id==tg_id))

async def check_admin(tg_id: int) -> bool:
    async with async_session() as session:
        stmt = select(User).where(User.tg_id == tg_id, User.is_admin == True)
        result = await session.scalar(stmt)
        return result is not None


async def get_photos():
    async with async_session() as session:
        return await session.scalars(select(Photo))

async def get_all_users():
    async with async_session() as session:
        result = await session.execute(select(User.tg_id))
        return result.scalars().all()




