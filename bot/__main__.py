import asyncio
import configparser
import logging
import os

import default_commands
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from ui_commands import set_bot_commands

# Read the secrets
current_directory = os.getcwd()
secret_path = os.path.join(current_directory, "secrets.ini")
config = configparser.ConfigParser()
config.read(secret_path)
BOT_TOKEN = config.get("secrets", "BOT_TOKEN")


async def main():
    logging.basicConfig(
        level=logging.DEBUG,
        filename="wrb_log.log",
        filemode="w",
        format="%(asctime)s %(levelname)s %(message)s",
    )

    wrb = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
    dp = Dispatcher()
    dp.message.filter(F.chat.type == "private")
    dp.include_router(default_commands.router)

    await set_bot_commands(wrb)

    try:
        await dp.start_polling(wrb, allowed_updates=dp.resolve_used_update_types())
    finally:
        await wrb.session.close()


if __name__ == "__main__":
    asyncio.run(main())
