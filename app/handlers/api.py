from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.api.currency.currency import get_currency_rates
from app.api.facts.fact import get_fact
from app.api.weather.weather import get_weathers
from app.database.request import check_user
import app.keyboards as kb

api_router = Router()

@api_router.message(Command('weather'))
async def get_weather(message: Message, state: FSMContext):
    is_register = await check_user(message.from_user.id)
    if is_register:
        await message.answer('Share your location you need to click button', reply_markup=await kb.client_location())
        await state.set_state('waiting_location')
    else:
        await message.answer('You need to register first! Click on -> /reg')

@api_router.message(F.location, StateFilter('waiting_location'))
async def getting_weather(message: Message, state: FSMContext):
    lat = message.location.latitude
    lon = message.location.longitude
    weather_info = await get_weathers(lat, lon)
    await message.answer(weather_info)
    await state.clear()

@api_router.message(Command('currency'))
async def currency(message: Message):
    currencies = await get_currency_rates()
    await message.answer(currencies)

@api_router.message(Command('fact'))
async def fact(message: Message):
    useless_fact = await get_fact()
    await message.answer(useless_fact)