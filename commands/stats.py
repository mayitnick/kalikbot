import psutil
from telebot import TeleBot
from telebot.types import Message
import modules.permissions as permissions
from modules.constants import CONSTANTS
import database

ALIASES = ["система", "статус", "загрузка"]

def handle(
    message: Message,
    bot: TeleBot,
    db: database.Database,
    perm: permissions.Permissions,
    CONSTANTS: CONSTANTS,
    FOUNDER_ID: int,
) -> bool:
    # Получаем загрузку CPU за 1 секунду в процентах
    cpu_usage = psutil.cpu_percent(interval=1)
    # Получаем информацию об оперативной памяти
    ram = psutil.virtual_memory()
    ram_usage = ram.percent
    ram_used_gb = round(ram.used / 1e9, 2)
    ram_total_gb = round(ram.total / 1e9, 2)

    # Формируем текст ответа с основными показателями
    response = (
        f"Статус системы:\n"
        f"CPU загрузка: {cpu_usage}%\n"
        f"ОЗУ использовано: {ram_used_gb} ГБ / {ram_total_gb} ГБ ({ram_usage}%)\n"
    )

    bot.reply_to(message, response)
    return True
