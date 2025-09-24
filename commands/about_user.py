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

# Ещё одно временное решение)
def if_reply_to_message(message, user_id, db):
    if message.reply_to_message:
        reply_to_message_id = message.reply_to_message.from_user.id
        return db.get_user_by_id(reply_to_message_id), 1
    else:
        return db.get_user_by_id(int(user_id)), 0

ALIASES = ["узнать о"]

def handle(
    message: Message,
    bot: TeleBot,
    db: database.Database,
    perm: permissions.Permissions,
    CONSTANTS: CONSTANTS,
    FOUNDER_ID: int,) -> bool:
    parts = message.text.split()
    
    try:
        if message.reply_to_message:
            user_id = message.reply_to_message.from_user.id
        else:
            user_id = parts[3]
        author = db.get_user_by_id(message.from_user.id)
        if author:
            if perm.check_for_permissions(author["type"], f"see.other"):
                # Дополнительная проверка на реплай
                user, is_reply = if_reply_to_message(message, user_id, db)
                if user:
                    full_name = user["full_name"]
                    bot.reply_to(message,
                                f"Информация о {get_url_from_id(full_name, user_id)}\nАйди: {user['telegram_id']}\nТип: {user['type']}\nГруппа: {user['group']}")
                    return
            else:
                if message.from_user.id == FOUNDER_ID:
                    user, is_reply = if_reply_to_message(message, user_id, db)
                    if user:
                        full_name = user["full_name"]
                        bot.reply_to(message,
                                    f"Инфа о {get_url_from_id(full_name, user_id)}\nАйди: {user['telegram_id']}\nТип: {user['type']}\nГруппа: {user['group']}")
                        return
                bot.reply_to(message, random.choice(CONSTANTS["kalik_noperm"]))
                return
    except:
        bot.reply_to(message, '❌ Ошибка! Нужно написать в таком формате: "Калик, о нём 12345678". Вместо 12345678 надо указать айди студента в ТГ ("Калик, айди")') 
    return True  # сигнал, что команда сработала
    # я хезе, это не везде есть, но мне в падлу это проверять :3
