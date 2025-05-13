from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

router = Router()

menu_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="📌 О нас"), KeyboardButton(text="👤 Профиль"), KeyboardButton(text="🔍 FAQ")],
    [KeyboardButton(text="📜 Правила"), KeyboardButton(text="👩‍💻 Оператор")],
    [KeyboardButton(text="❗ Сдать аккаунт в аренду ❗")],
], resize_keyboard=True)


@router.message(Command("start"))
async def start_command(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Привет! Выберите действие:", reply_markup=menu_kb)
