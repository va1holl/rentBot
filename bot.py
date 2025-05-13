import asyncio
from aiogram import Bot
from aiogram import Dispatcher
from handlers import menu, rent, profile, mainInfo, getter
from config import BOT_TOKEN


bot = Bot(token=BOT_TOKEN)

dp = Dispatcher()


dp.include_router(menu.router)
dp.include_router(rent.router)
dp.include_router(profile.router)
dp.include_router(mainInfo.router)
dp.include_router(getter.router)


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())