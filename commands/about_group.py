from telebot import TeleBot
from telebot.types import Message
import modules.permissions as permissions
from modules.constants import CONSTANTS
import database
import random

# Временное решение, нужно будет это потом в отдельный модуль вынести ;)
def get_url_from_id(full_name, id):
    # [Имя](tg://user?id=123456789)
    return f"[{full_name}](tg://user?id={id})"

ALIASES = ["о группе"]

def handle(
    message: Message,
    bot: TeleBot,
    db: database.Database,
    perm: permissions.Permissions,
    CONSTANTS: CONSTANTS,
    FOUNDER_ID: int,) -> bool:
    parts = message.text.split()
    
    # Пытаемся узнать всех участников группы
    # Пока тестово, без проверки на права
    group_name = parts[3]
    group = db.get_group_by_name(group_name)
    if group:
        if message.from_user.id == FOUNDER_ID:
            # В группе в студентах хранятся только айди
            students = []
            for user in group["students"]:
                user = db.get_user_by_id(user)
                students.append(user)
            bot.reply_to(message, f"Группа {group['group']} состоит из {len(group['students'])} человек:\n{', '.join([get_url_from_id(user['full_name'], user['telegram_id']) for user in students])}")
        else:
            bot.reply_to(message, random.choice(CONSTANTS["kalik_noperm"]))
    return True  # сигнал, что команда сработала
    # я хезе, это не везде есть, но мне в падлу это проверять :3
