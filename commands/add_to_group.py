from telebot import TeleBot
from telebot.types import Message
import modules.permissions as permissions
from modules.constants import CONSTANTS
import database
import random
import traceback

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

ALIASES = ["в группу"]

def handle(
    message: Message,
    bot: TeleBot,
    db: database.Database,
    perm: permissions.Permissions,
    CONSTANTS: CONSTANTS,
    FOUNDER_ID: int,) -> bool:
    parts = message.text.split()
    
    try:
        # Калик, в группу 12345678 group_name
        # или
        # Калик, в группу group_name (с ответом на сообщение)
        user_id = parts[3]
        
        author = db.get_user_by_id(message.from_user.id)
        
        # Если есть ответ на сообщение
        user, is_reply = if_reply_to_message(message, user_id)
        
        group_name = parts[3] if is_reply else parts[4]
        user_id = int(user_id) if not is_reply else message.reply_to_message.from_user.id
        group = db.get_group_by_name(group_name)
        
        if perm.check_for_permissions(author["type"], f"group.invite"):
            if user:
                # db.update_user_field(user_id, "group", group_name)
                if group:
                    db.add_student(group_name, user_id)
                    bot.reply_to(message, f"Группа студента {user['telegram_id']} изменена на {group_name}!")
                else:
                    bot.reply_to(message, f"Группа {group_name} не найдена.")
            else:
                bot.reply_to("Пользователь не найден.")
        else:
            if message.from_user.id == FOUNDER_ID:
                if user:
                    if group:
                        db.add_student(group_name, user_id)
                        bot.reply_to(message, f"У тебя нет прав, но так как ты - основатель, я всё равно сделаю это!\nГруппа студента {user['telegram_id']} изменена на {group_name}!")
                    else:
                        bot.reply_to(message, f"Группа {group_name} не найдена.")
                else:
                    bot.reply_to(message, "Ты хоть и всемогущий, но я не нашёл пользователя ;(")
            else:
                bot.reply_to(message, random.choice(CONSTANTS["kalik_noperm"]))
    except Exception as e:
        bot.reply_to(message, '❌ Ошибка! Нужно написать в таком формате: "Калик, в группу 12345678 group_name". Вместо 12345678 надо указать айди студента в ТГ ("Калик, айди")') 
        traceback.print_exc()
