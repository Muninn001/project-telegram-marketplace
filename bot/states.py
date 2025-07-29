from aiogram.fsm.state import State, StatesGroup # type: ignore

class OrderStates(StatesGroup):
    choosing_product = State()
    choosing_quantity = State()

class AddProductStates(StatesGroup):
    waiting_type = State()
    waiting_name = State()
    waiting_price = State()
    waiting_quantity = State()
    waiting_specific_field = State()
