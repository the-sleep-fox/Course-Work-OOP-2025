from aiogram.fsm.state import State, StatesGroup

class AuthState(StatesGroup):
    choosing_country = State()
    entering_email = State()
    entering_password = State()
    entering_country = State()
    after_login = State()
    entering_cancel_country = State()
    canceling_country = State()
    menu = State()

class RegisterStates(StatesGroup):
    waiting_for_email = State()
    waiting_for_passport = State()
    waiting_for_password = State()
    waiting_for_password_confirm = State()
    waiting_for_retry = State()


