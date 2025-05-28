from aiogram.fsm.state import State, StatesGroup

class AuthState(StatesGroup):
    choosing_country = State()
    entering_email = State()
    entering_password = State()
    entering_country = State()
