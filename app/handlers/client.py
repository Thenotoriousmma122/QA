from aiogram.filters import CommandStart, StateFilter, Command
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from pyexpat.errors import messages
from sqlalchemy import select
import ssl
import certifi
from geopy.geocoders import Nominatim
from sqlalchemy.testing.suite.test_reflection import metadata

from app.database.models import async_session, User, Photo
from app.database.request import get_card, check_user, get_user, check_admin, get_photos, get_all_users
import app.keyboards as kb
from aiogram.fsm.context import FSMContext

from app.state import RegStates


client = Router()

ctx = ssl.create_default_context(cafile=certifi.where())
geolocator = Nominatim(user_agent='TelegramBotForShop', ssl_context=ctx)

@client.message(CommandStart())
async def start(message: Message):
    is_registered = await check_user(message.from_user.id)
    #print(is_registered)
    if not is_registered:
        await message.answer('You need to registration! use command /reg or click on -> /reg \nYou can use /help command')
    else:
        await message.answer("Hello again, welcome to our shop!", reply_markup=kb.menu)



@client.callback_query(F.data.startswith('categories'))
@client.message(F.text == 'Catalog')
async def catalog(event: Message | CallbackQuery):
    if isinstance(event, Message):
        await event.answer('Chose the category', reply_markup=await kb.categories())
    else:
        await event.answer('U back ')
        await event.message.edit_text('Chose the category', reply_markup=await kb.categories())

@client.message(F.text=='Contacts')
async def contacts(message: Message):
    await message.answer('This is our contacts if you have some issues', reply_markup=kb.contacts)


@client.callback_query(F.data.startswith('category_'))
async def cards(callback: CallbackQuery):
    await callback.answer()
    category_id = callback.data.split('_')[1]
    try:
        await callback.message.edit_text('Chose the thing', reply_markup=await kb.cards(category_id))
    except:
        await callback.message.delete()
        await callback.message.answer('Chose the thing', reply_markup=await kb.cards(category_id))

'''''
@client.callback_query(F.data.startswith('categories'))
async def back_to_categories(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer('Chose the category', reply_markup=await kb.categories())
'''''




@client.callback_query(F.data.startswith('card_'))
async def card_info(callback: CallbackQuery):
    await callback.answer()
    card_id = int(callback.data.split('_')[1])
    card = await get_card(card_id)
    await callback.message.delete()
    await callback.message.answer_photo(photo=card.image,
                               caption=f'{card.name} \n\n {card.price}Rub \n\n {card.description}',
                               reply_markup=await kb.back_to_categories(card.category_id, card_id))


@client.callback_query(F.data.startswith('buy_'))
async def client_buy(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    card_id = int(callback.data.split('_')[1])
    await state.set_state('waiting for address')
    await state.update_data(card_id=card_id)
    await callback.message.answer('You need to share your location', reply_markup=await kb.client_location())

@client.message(F.location, StateFilter('waiting for address'))
async def getting_location(message: Message, state: FSMContext):
    data = await state.get_data()
    address = geolocator.reverse(f'{message.location.latitude}, {message.location.longitude}',
                                 exactly_one=True, language='ru')
    user = await get_user(message.from_user.id)
    card_id = data.get('card_id')

    full_info = (
        f'New order\n\n'
        f'User: {user.name}, @{message.from_user.username}, ID-{user.tg_id}\n'
        f'number: {user.phone_number}\n'
        f'address: {address}\n'
        f'Thing ID {card_id}'

    )

    await message.bot.send_message(-4809427347, full_info)
    await message.answer('Perfect, waiting for admins', reply_markup=kb.menu)
    await state.clear()


@client.message(StateFilter('waiting for address'))
async def getting_location(message: Message, state: FSMContext):
    data = await state.get_data()
    address = message.text
    user = await get_user(message.from_user.id)
    card_id = data.get('card_id')

    full_info = (
        f'New order\n\n'
        f'User: {user.name}, @{message.from_user.username}, ID-{user.tg_id}\n'
        f'number: {user.phone_number}\n'
        f'address: {address}\n'
        f'Thing ID {card_id}'

    )

    await message.bot.send_message(-4809427347, full_info)
    await message.answer('Perfect, waiting for admins', reply_markup=kb.menu)
    await state.clear()


@client.message(Command('help'))
async def cmd_help(message: Message):
    await message.answer('/start - Start the bot\n'
                         '/reg - Register your account\n'
                         '/share - Share any photo\n'
                         '/weather - Show the weather\n'
                         '/currency - Show currency rates\n'
                         '/fact - Get a random useless fact')


@client.message(Command('share'))
async def share(message:Message, state:FSMContext):
    is_register = await check_user(message.from_user.id)
    if is_register:
        await message.answer('Share your picture')
        await state.set_state('waiting_photo')
    else:
        await message.answer('You need to register first! Click on -> /reg')


@client.message(F.photo, StateFilter('waiting_photo'))
async def getting_photo(message:Message, state: FSMContext):
    file_id = message.photo[-1].file_id
    name = message.from_user.first_name
    tg_id = message.from_user.id
    print(file_id)

    async with async_session() as session:
        photo = Photo(image=file_id, name=name, tg_id=tg_id)
        session.add(photo)
        await session.commit()

    await message.answer('Photo saved ✅')
    await state.clear()

@client.message(F.text=='Photo')
async def get_all_photo(message: Message):
    is_admin = await check_admin(message.from_user.id)
    if is_admin:
        photos = await get_photos()
        print(photos)
        for photo in photos:
            await message.answer_photo(photo=photo.image, caption=f'name_of_user: {photo.name} \ntelegramID_of_user {photo.tg_id}')
    else :
        await message.answer('You are not admin')

@client.message(Command('broadcast'))
async def start_broadcast(message: Message, state: FSMContext):
    is_admin = await check_admin(message.from_user.id)
    if not is_admin:
        await message.answer('You are not admin')
        return
    await message.answer('Write your text for all users')
    await state.set_state('waiting_text')

@client.message(StateFilter('waiting_text'))
async def do_broadcast(message: Message, state: FSMContext):
    text = message.text
    users = await get_all_users()
    success = 0

    for user_id in users:
        try:
            await message.bot.send_message(chat_id=user_id, text=text)
            success += 1
        except Exception as e:
            print(f'Error : {e}')

    await message.answer(f'success = {success}')
    await state.clear()







@client.message(F.text)
async def text(message: Message):
    await message.reply('Unknown command to see all commands click on -> /help')

@client.message(F.photo)
async def get_photo(message:Message):
    file_id = message.photo[-1].file_id
    await message.answer(file_id)

@client.message(F.text == 'Лес')
async def send_photo(message: Message):
    await message.answer_photo(photo='AgACAgIAAxkBAAIDY2iHXn9FaiO-WZKD8zmlUXbWRBIAA87yMRuvLzlIOV-_jdlzqrABAAMCAAN5AAM2BA')


'''''
@client.message(F.text == 'Анель')
async def send_photo(message: Message):
    await message.answer_photo(photo='AgACAgIAAxkBAAIDXWiHXi4M2RklAAGJ5dpQK0MPGdeQQQACyvIxG68vOUhv2t1-yr7hiwEAAwIAA3kAAzYE')


@client.message(F.text == 'Очки')
async def send_photo(message: Message):
    await message.answer_photo(photo='AgACAgIAAxkBAAIDjWiHYCVSzfys2-_tipz5GdUghUdSAALe8jEbry85SJH-319uFEneAQADAgADeQADNgQ')

@client.message(F.text == 'Жоламан')
async def send_photo(message: Message):
    await message.answer_photo(photo='AgACAgIAAxkBAAIDk2iHYIbyraODVuV-G-M6UG6FFkiaAALg8jEbry85SOO70OWJ4d_ZAQADAgADeQADNgQ')

@client.message(F.text == 'Дилека')
async def send_photo(message: Message):
    await message.answer_photo(photo='AgACAgIAAxkBAAIDoWiHYUqFZmENfYa6cWLMRAh6ZZAxAALl8jEbry85SIIeaxzw6OXaAQADAgADeQADNgQ')

'''''