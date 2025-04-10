from aiogram.fsm.state import StatesGroup, State

class ExpenseForm(StatesGroup):
    title = State()
    date = State()
    amount = State()
    delete_id = State()  
