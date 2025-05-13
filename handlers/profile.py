from aiogram import Router, types, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from handlers import menu

router = Router()

#тут БД
user_data = {}


class AddRequisites(StatesGroup):
    choosing_bank = State()
    entering_phone = State()


profile_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="➕ Добавить реквизиты"), KeyboardButton(text="🔙 В главное меню")],
], resize_keyboard=True)

bank_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="🏦 Сбербанк"), KeyboardButton(text="🏦 ВТБ")],
    [KeyboardButton(text="🏦 Т-Банк"), KeyboardButton(text="🏦 Альфа-Банк")],
    [KeyboardButton(text="🏦 Другой банк"), KeyboardButton(text="🔙 Назад")],
], resize_keyboard=True)

phone_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="🔙 Назад")],
], resize_keyboard=True)


@router.message(F.text == "👤 Профиль")
async def profile_info(message: types.Message):
    user_id = message.from_user.id
    requisites = user_data.get(user_id, {}).get("requisites", "❌ Не заданы ❗️")

    await message.answer(
        f"<b>Профиль</b> \nID: {user_id}"
        "\nКол-во Аккаунтов: 0"
        "\nСледующая оплата: 0"
        "\nВыплачено всего: 0"
        f"\nРеквизиты: {requisites}",
        reply_markup=profile_kb, parse_mode='HTML'
    )


@router.message(F.text == "➕ Добавить реквизиты")
async def ask_for_bank(message: types.Message, state: FSMContext):
    await state.set_state(AddRequisites.choosing_bank)
    await message.answer("📌 Укажите банк, на который будет отправляться оплата:", reply_markup=bank_kb)


@router.message(StateFilter(AddRequisites.choosing_bank), F.text.in_(["🏦 Сбербанк", "🏦 ВТБ", "🏦 Т-Банк", "🏦 Альфа-Банк", "🏦 Другой банк"]))
async def ask_for_phone(message: types.Message, state: FSMContext):
    await state.update_data(bank=message.text)  # Сохраняем банк
    await state.set_state(AddRequisites.entering_phone)
    await message.answer("Введите номер телефона для перевода:", reply_markup=phone_kb)


@router.message(StateFilter(AddRequisites.entering_phone), F.text)
async def save_requisites(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    data = await state.get_data()

    user_data[user_id] = {"requisites": f"{data['bank']} {message.text}"}  # Сохраняем реквизиты

    await state.clear()
    await profile_info(message)


@router.message(F.text == "🔙 Назад")
async def back_to_profile(message: types.Message, state: FSMContext):
    await state.clear()
    await profile_info(message)


@router.message(F.text == "🔙 В главное меню")
async def back_to_main_menu(message: types.Message, state: FSMContext):
    await menu.start_command(message, state)
