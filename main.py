import logging
import asyncio
from aiogram import Bot, Dispatcher
from config import config

from bot.handlers import router  # Импортируем роутер из handlers.py

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.bot_token)
dp = Dispatcher()

@dp.errors()
async def handle_errors(exception):
    if isinstance(exception, Exception):
        logging.warning(f"Throttled error: {exception}")
    else:
        logging.error(f"Произошла ошибка: {exception}")
    return True

async def main():
    # Регистрация роутера
    dp.include_router(router)

    # Запуск бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())