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
    return f"{s // 3600} ч {(s % 3600) // 60} м"

def handle(
    message: Message,
    bot: TeleBot,
    db: database.Database,
    perm: permissions.Permissions,
    CONSTANTS: CONSTANTS,
    FOUNDER_ID: int,) -> bool:

    bot.reply_to(message, 
        f"```Осталось: {get_time_until_target_simple()}\n1. 8:20 - 9:05\n2. 9:05 - 9:50\n3. 10:00 - 10:45\n4. 10:45 - 11:30\n5. 11:35 - 12:20\n6. 12:25 - 13:10\n7. 13:15 - 14:00\n8. 14:00 - 14:45\n9. 14:50 - 15:35\n10. 15:40 - 16:25\n```", parse_mode="MARKDOWNV2")
    
    
    return True  # сигнал, что команда сработала
    # я хезе, это не везде есть, но мне в падлу это проверять :3
