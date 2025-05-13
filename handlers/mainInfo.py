from aiogram import Router, types
from info.info import Info


router = Router()


@router.message(lambda msg: msg.text == "📌 О нас")
async def about_info(message: types.Message):
    await message.answer(Info.info)


@router.message(lambda msg: msg.text == "📜 Правила")
async def rules_info(message: types.Message):
    await message.answer(Info.rules)


@router.message(lambda msg: msg.text == "🔍 FAQ")
async def faq_info(message: types.Message):
    await message.answer(Info.faq,
                         parse_mode='HTML')


@router.message(lambda msg: msg.text == "👩‍💻 Оператор")
async def faq_info(message: types.Message):
    await message.answer(Info.operator,
                         parse_mode='HTML')