from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats


async def set_bot_commands(bot: Bot):
    commands = [
            BotCommand(command="start", description="Перезапустить"),
            # BotCommand(command="show", description="Показать клавиатуру"),
            # BotCommand(command="hide", description="Убрать клавиатуру"),
            # BotCommand(command="help", description="Справочная информация")
        ]
    await bot.set_my_commands(commands=commands,
                              scope=BotCommandScopeAllPrivateChats())
