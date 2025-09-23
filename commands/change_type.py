from telebot import TeleBot
from telebot.types import Message
import modules.permissions as permissions
from modules.constants import CONSTANTS
import database
import traceback
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

ALIASES = ["изменить тип"]

def handle(
    message: Message,
    bot: TeleBot,
    db: database.Database,
    perm: permissions.Permissions,
    CONSTANTS: CONSTANTS,
    FOUNDER_ID: int,) -> bool:
    
    parts = message.text.split()
    
    try:
        # Калик, измени тип 12345678 student/elder/curator/admin
        # или
        # Калик, измени тип student/elder/curator/admin (с ответом на сообщение)
        user_id = parts[3]
        
        author = db.get_user_by_id(message.from_user.id)
        
        # Если есть ответ на сообщение
        user, is_reply = if_reply_to_message(message, user_id)
        
        # Если ответил на сообщение, то parts[3] - роль, если не ответил, то parts[4], т.к. parts[3] - это айди
        role = parts[3] if is_reply else parts[4]
        user_id = int(user_id) if not is_reply else message.reply_to_message.from_user.id
        
        if perm.check_for_permissions(author["type"], f"give.{role}"):
            if user:
                db.update_user_field(user_id, "type", role)
                bot.reply_to(message, f"Тип студента {user['telegram_id']} изменён на {role}!")
            else:
                bot.reply_to("Пользователь не найден.")
        else:
            if message.from_user.id == FOUNDER_ID:
                if user:
                    db.update_user_field(user_id, "type", role)
                    bot.reply_to(message, f"У тебя нет прав, но так как ты - основатель, я всё равно сделаю это!\nТип студента {user['telegram_id']} изменён на {role}!")
                else:
                    bot.reply_to(message, "Ты хоть и всемогущий, но я не нашёл пользователя ;(")
            else:
                bot.reply_to(message, random.choice(CONSTANTS["kalik_noperm"]))
    except Exception as e:
        bot.reply_to(message, '❌ Ошибка! Нужно написать в таком формате: "Калик, измени тип 12345678 student/elder/curator/admin". Вместо 12345678 надо указать айди студента в ТГ ("Калик, айди")') 
        traceback.print_exc()
