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

ALIASES = ["кик из группы"]

def handle(
    message: Message,
    bot: TeleBot,
    db: database.Database,
    perm: permissions.Permissions,
    CONSTANTS: CONSTANTS,
    FOUNDER_ID: int,) -> bool:
    parts = message.text.split()
    
    # Калик, кик из группы 12345678 group_name
    author = db.get_user_by_id(message.from_user.id)
    
    if perm.check_for_permissions(author["type"], f"group.kick"):
        user_id = parts[4]
        group_name = parts[5]
        user_id = int(user_id)
        group = db.get_group_by_name(group_name)
        if group:
            if user_id in group["users"]:
                if db.remove_student(group_name, user_id):
                    bot.reply_to(message, f"Студент {user_id} успешно исключён из группы {group_name}!")
                else:
                    bot.reply_to(message, f"Что-то пошло не так. Попробуйте ещё раз.")
    return True  # сигнал, что команда сработала
    # я хезе, это не везде есть, но мне в падлу это проверять :3
