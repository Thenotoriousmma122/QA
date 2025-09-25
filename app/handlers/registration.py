from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy import select

from app.database.models import async_session, User
import app.keyboards as kb
from app.state import RegStates

register_router = Router()

@register_router.message(Command('reg'))
async def reg(message: Message, state: FSMContext):
    async with async_session() as session:
        res = await session.execute(select(User).where(User.tg_id==message.from_user.id))
        if res.scalar():
            await message.answer('You are already in database', reply_markup=kb.menu)
            return

    await message.answer('Write your name or use the button', reply_markup=await kb.clients_name(message.from_user.first_name))
    await state.set_state(RegStates.name)

@register_router.message(RegStates.name)
async def get_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Send your phone number or use the button", reply_markup= await kb.clients_phone())
    await state.set_state(RegStates.phone_number)

@register_router.message(RegStates.phone_number)
async def get_phone(message: Message, state: FSMContext):
    await state.update_data(phone_number=message.text)
    data = await state.get_data()
    name = data.get('name')
    phone = message.contact.phone_number if message.contact else data.get('phone_number')

    async with async_session() as session:
        user = User(tg_id=message.from_user.id, name = name, phone_number=phone)
        session.add(user)
        await session.commit()

    await message.answer('Success, You can buy or show our products', reply_markup=kb.menu)
    await state.clear()



