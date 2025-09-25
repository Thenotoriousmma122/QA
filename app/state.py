from aiogram.fsm.state import StatesGroup, State


class RegStates(StatesGroup):
    name = State()
    phone_number = State()
