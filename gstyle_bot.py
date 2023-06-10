import logging
import asyncio
from aiogram import Bot, Dispatcher
from config import Config, load_config
from handlers import handlers


# Функция конфигурирования и запуска бота
async def main() -> None:
    # Загружаем конфиг в переменную config
    config: Config = load_config()

    # Инициализируем бот и диспетчер
    bot: Bot = Bot(token=config.tg_bot.token)
    dp: Dispatcher = Dispatcher()

    # Регистрируем роутеры в диспетчере
    dp.include_router(handlers.router)

    # Пропускаем накопившиеся апдейты и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    # Настройка логирования
    logging.basicConfig(
        level=logging.ERROR,  # Уровень логирования (в данном случае, только ошибки)
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Формат записи логов
        filename='bot.log',  # Имя файла логов
    )
    # Запуск бота
    asyncio.run(main())
