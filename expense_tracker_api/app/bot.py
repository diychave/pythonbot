import logging
import sys
import asyncio
import aiohttp
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters.state import StateFilter
from currency_parser import get_exchange_rate  

API_URL = "http://127.0.0.1:8000"  
BOT_TOKEN = "7914104932:AAHM-IHfzuVgZ2nEFauIgncra8ys2RXFF3c" 

logging.basicConfig(level=logging.INFO, stream=sys.stdout)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())  


main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="➕ Додати витрату")],
        [KeyboardButton(text="📊 Отримати звіт")],
        [KeyboardButton(text="❌ Видалити витрату")],
        [KeyboardButton(text="✏️ Редагувати витрату")],
    ],
    resize_keyboard=True
)


class ExpenseForm(StatesGroup):
    title = State()
    date = State()
    amount = State()

class ReportPeriod(StatesGroup):
    start_date = State()
    end_date = State()

class EditExpense(StatesGroup):
    id = State()
    choose_field = State()
    new_title = State()
    new_date = State()
    new_amount = State()

class DeleteExpense(StatesGroup):
    expense_id = State()

def parse_date(date_str: str) -> str | None:
    formats = ["%d.%m.%Y", "%d.%m.%y", "%d/%m/%Y", "%d/%m/%y"]
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привіт! Обери дію з меню:", reply_markup=main_menu)

@dp.message(F.text == "➕ Додати витрату")
async def add_expense_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Введи назву витрати:")
    await state.set_state(ExpenseForm.title)

@dp.message(ExpenseForm.title)
async def get_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("Введи дату у форматі DD.MM.YYYY:")
    await state.set_state(ExpenseForm.date)

@dp.message(ExpenseForm.date)
async def get_date(message: types.Message, state: FSMContext):
    parsed = parse_date(message.text)
    if not parsed:
        await message.answer("❗ Невірний формат дати. Спробуй ще раз.")
        return
    await state.update_data(date=parsed)
    await message.answer("Введи суму (в грн):")
    await state.set_state(ExpenseForm.amount)

@dp.message(ExpenseForm.amount)
async def get_amount(message: types.Message, state: FSMContext):
    try:
        amount = float(message.text.replace(",", "."))
    except ValueError:
        await message.answer("❗ Неправильна сума. Введи еще раз.")
        return


    exchange_rate = await get_exchange_rate()

    amount_usd = amount / exchange_rate if exchange_rate != 1 else 0
    
    await state.update_data(amount=amount, amount_usd=amount_usd)
    data = await state.get_data()

    expense_data = {
        "name": data["title"],
        "amount_uah": amount,
        "amount_usd": amount_usd,
        "date": data["date"]
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(f"{API_URL}/expenses/", json=expense_data) as resp:
            if resp.status == 200:
                await message.answer("✅ Витрату додано!", reply_markup=main_menu)
            else:
                error = await resp.json()
                error_message = error.get("detail", "Невідома помилка.")
                await message.answer(f"❌ Помилка при додаванні! {error_message}", reply_markup=main_menu)

    await state.clear()

@dp.message(F.text == "📊 Отримати звіт")
async def report_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Введи дату **початку** періоду у форматі DD.MM.YYYY:")
    await state.set_state(ReportPeriod.start_date)

@dp.message(StateFilter(ReportPeriod.start_date))
async def get_report_start_date(message: types.Message, state: FSMContext):
    parsed_date = parse_date(message.text)
    if not parsed_date:
        await message.answer("❗ Невірний формат дати. Спробуй ще раз.")
        return
    await state.update_data(start_date=parsed_date)
    await message.answer("Введи дату **кінця** періоду у форматі DD.MM.YYYY:")
    await state.set_state(ReportPeriod.end_date)

@dp.message(StateFilter(ReportPeriod.end_date))
async def get_report_end_date(message: types.Message, state: FSMContext):
    parsed_date = parse_date(message.text)
    if not parsed_date:
        await message.answer("❗ Невірний формат дати. Спробуй ще раз.")
        return

    await state.update_data(end_date=parsed_date)
    data = await state.get_data()

    start_date = data["start_date"]
    end_date = data["end_date"]

    await message.answer("⏳ Формую звіт...")

    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}/report/", params={"start_date": start_date, "end_date": end_date}) as resp:
            if resp.status == 200:
                file_bytes = await resp.read()
                await message.answer_document(
                    types.BufferedInputFile(file_bytes, filename="report.xlsx"),
                    caption=f"📊 Звіт з {start_date} по {end_date}",
                    reply_markup=main_menu
                )
            else:
                await message.answer("❌ Помилка при отриманні звіту.", reply_markup=main_menu)

    await state.clear()

@dp.message(F.text == "❌ Видалити витрату")
async def delete_expense_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Введи ID витрати, яку хочеш видалити:")
    await state.set_state(DeleteExpense.expense_id)

@dp.message(DeleteExpense.expense_id)
async def delete_expense(message: types.Message, state: FSMContext):
    expense_id = message.text.strip()
    if not expense_id.isdigit():
        await message.answer("❗ ID має бути числом.")
        return

    async with aiohttp.ClientSession() as session:
        async with session.delete(f"{API_URL}/expenses/{expense_id}") as resp:
            if resp.status == 200:
                await message.answer(f"✅ Витрату з ID {expense_id} видалено!", reply_markup=main_menu)
            else:
                await message.answer(f"❌ Помилка при видаленні витрати з ID {expense_id}.", reply_markup=main_menu)

    await state.clear()

@dp.message(F.text == "✏️ Редагувати витрату")
async def edit_expense_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Введи ID витрати, яку хочеш редагувати:")
    await state.set_state(EditExpense.id)

@dp.message(EditExpense.id)
async def get_expense_id(message: types.Message, state: FSMContext):
    expense_id = message.text.strip()
    if not expense_id.isdigit():
        await message.answer("❗ ID має бути числом.")
        return

    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}/expenses/{expense_id}") as resp:
            if resp.status == 200:
                data = await resp.json()
                await state.update_data(id=expense_id, current=data)
                await message.answer(
                    f"🔍 Поточна інформація:\n"
                    f"Назва: {data['name']}\n"
                    f"Дата: {data['date']}\n"
                    f"Сума: {data['amount_uah']} грн\n\n"
                    f"Що хочеш змінити? (назва / дата / сума):"
                )
                await state.set_state(EditExpense.choose_field)
            else:
                await message.answer("❌ Витрату не знайдено.")

@dp.message(EditExpense.choose_field)
async def choose_field_to_edit(message: types.Message, state: FSMContext):
    field = message.text.strip().lower()
    if field == "назва":
        await message.answer("Введи нову назву витрати:")
        await state.set_state(EditExpense.new_title)
    elif field == "дата":
        await message.answer("Введи нову дату витрати (DD.MM.YYYY):")
        await state.set_state(EditExpense.new_date)
    elif field == "сума":
        await message.answer("Введи нову суму витрати (грн):")
        await state.set_state(EditExpense.new_amount)
    else:
        await message.answer("❗ Невірний вибір. Вибери між 'назва', 'дата' або 'сума'.")

@dp.message(EditExpense.new_title)
async def edit_expense_title(message: types.Message, state: FSMContext):
    new_title = message.text.strip()
    await state.update_data(new_title=new_title)
    await message.answer("🔄 Назву змінено. Тепер введи нову дату витрати (DD.MM.YYYY):")
    await state.set_state(EditExpense.new_date)

@dp.message(EditExpense.new_date)
async def edit_expense_date(message: types.Message, state: FSMContext):
    new_date = parse_date(message.text)
    if not new_date:
        await message.answer("❗ Невірний формат дати. Спробуй ще раз.")
        return
    await state.update_data(new_date=new_date)
    await message.answer("🔄 Дату змінено. Тепер введи нову суму витрати (грн):")
    await state.set_state(EditExpense.new_amount)

@dp.message(EditExpense.new_amount)
async def edit_expense_amount(message: types.Message, state: FSMContext):
    try:
        new_amount = float(message.text.replace(",", "."))
    except ValueError:
        await message.answer("❗ Невірний формат суми. Спробуй ще раз.")
        return

    exchange_rate = await get_exchange_rate()
    new_amount_usd = new_amount / exchange_rate if exchange_rate != 1 else 0

    data = await state.get_data()
    expense_id = data['id']
    updated_data = {
        "name": data.get("new_title", data["current"]["name"]),
        "amount_uah": new_amount,
        "amount_usd": new_amount_usd,
        "date": data.get("new_date", data["current"]["date"]),
    }

    async with aiohttp.ClientSession() as session:
        async with session.put(f"{API_URL}/expenses/{expense_id}", json=updated_data) as resp:
            if resp.status == 200:
                await message.answer("✅ Витрату змінено,вітаю!", reply_markup=main_menu)
            else:
                await message.answer("❌ Помилка при зміні витрати,вітаю.", reply_markup=main_menu)

    await state.clear()


if __name__ == '__main__':
    asyncio.run(dp.start_polling(bot))
