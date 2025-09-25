from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.database.request import get_categories, get_card_by_category

menu = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text='Catalog')],
        [KeyboardButton(text='Contacts')]
    ],
    resize_keyboard=True,
    input_field_placeholder='Chose the one'
)

contacts = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Whatsapp', url='https://wa.me/77067208442')],
    [InlineKeyboardButton(text='Telegram', url='https://t.me/Thenotoriousmma122')]
])

async def clients_name(name):
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=name)]],
                               resize_keyboard=True)

async def clients_phone():
    return ReplyKeyboardMarkup(keyboard=[[
        KeyboardButton(text='Share ur contact',
                       request_contact=True)
    ]], resize_keyboard=True)

async def client_location():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text='Share location', request_location=True)]
    ], resize_keyboard=True)

async def categories():
    keyboard = InlineKeyboardBuilder()
    all_categories = await get_categories()
    for category in all_categories:
        keyboard.add(InlineKeyboardButton(text=category.name, callback_data=f'category_{category.id}'))
    return keyboard.adjust(2).as_markup()


async def cards(category_id):
    keyboard = InlineKeyboardBuilder()
    all_cards = await get_card_by_category(category_id)
    for card in all_cards:
        keyboard.row(InlineKeyboardButton(text=f'{card.name} | {card.price}Rub',
                                          callback_data=f'card_{card.id}'))
    keyboard.row(InlineKeyboardButton(text='Back', callback_data='categories'))
    return keyboard.as_markup()

async def back_to_categories(category_id, card_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Buy', callback_data=f'buy_{card_id}')],
        [InlineKeyboardButton(text='Back', callback_data=f'category_{category_id}')]
    ])

