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

ALIASES = ["создать группу"]

def handle(
    message: Message,
    bot: TeleBot,
    db: database.Database,
    perm: permissions.Permissions,
    CONSTANTS: CONSTANTS,
    FOUNDER_ID: int,) -> bool:
    parts = message.text.split()
    
    author = db.get_user_by_id(message.from_user.id)
    if perm.check_for_permissions(author["type"], "group.create"):
        group_name = parts[3]
        if db.get_group_by_name(group_name):
            bot.reply_to(message, f"Группа {group_name} уже существует!")
        else:
            db.create_group(group_name)
            bot.reply_to(message, f"Группа {group_name} создана!")
    else:
        if message.from_user.id == FOUNDER_ID:
            group_name = parts[3]
            if db.get_group_by_name(group_name):
                bot.reply_to(message, f"Группа {group_name} уже существует!")
            else:
                db.create_group(group_name)
                bot.reply_to(message, f"Группа {group_name} создана!")
        else:
            bot.reply_to(message, random.choice(CONSTANTS["kalik_noperm"]))
    return True  # сигнал, что команда сработала
    # я хезе, это не везде есть, но мне в падлу это проверять :3
