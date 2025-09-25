import os
import requests
from aiogram import Router, types
from aiogram.filters import Command

usersbox_router = Router()

USERSBOX_API_KEY = os.getenv("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjcmVhdGVkX2F0IjoxNzU0NzQ3MzA2LCJhcHBfaWQiOjE3NTQ3NDczMDZ9.asMt7cShkNDXBdI7XP5K_pDB1G8-z_xwHPUa-mfxrR8")
BASE_URL = "https://api.usersbox.ru/v1"

def search_global(query):
    url = f"{BASE_URL}/search"
    headers = {"Authorization": f"Bearer {USERSBOX_API_KEY}"}
    params = {"q": query}
    response = requests.get(url, headers=headers, params=params)
    return response.json()

@usersbox_router.message(Command("search"))
async def cmd_search(message: types.Message):
    await message.answer("Введите ФИО для поиска:")

@usersbox_router.message()
async def handle_search(message: types.Message):
    fio = message.text.strip()
    data = search_global(fio)

    if data.get("status") != "success" or not data.get("data"):
        await message.answer("Ничего не найдено.")
        return

    result_text = f"🔍 Результаты поиска по: {fio}\n"
    for source, info in data["data"].items():
        count = info.get("count", 0)
        result_text += f"\n📂 {source} — {count} совпадений"

    await message.answer(result_text)