from telebot import TeleBot
from telebot.types import Message
import modules.permissions as permissions
from modules.constants import CONSTANTS
import database
from datetime import datetime, timedelta

ALIASES = ["время"]

def get_time_until_target_simple():
    now = datetime.now()
    h, m = (16, 25) if now.weekday() == 0 else (14, 45)
    target = now.replace(hour=h, minute=m, second=0, microsecond=0)
    if now > target:
        target += timedelta(days=1)
    diff = target - now
    s = int(diff.total_seconds())
    return f"{s // 3600} часов {(s % 3600) // 60} минут {s % 60} секунд"

def handle(
    message: Message,
    bot: TeleBot,
    db: database.Database,
    perm: permissions.Permissions,
    CONSTANTS: CONSTANTS,
    FOUNDER_ID: int,) -> bool:

    bot.reply_to(message, f"До конца пар осталось: {get_time_until_target_simple}")
    
    
    return True  # сигнал, что команда сработала
    # я хезе, это не везде есть, но мне в падлу это проверять :3
