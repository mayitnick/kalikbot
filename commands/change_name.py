from telebot import TeleBot
from telebot.types import Message
import modules.permissions as permissions
from modules.constants import CONSTANTS
import database

ALIASES = ["автор", "создатель", "создал", "основатель"]

def handle(
    message: Message,
    bot: TeleBot,
    db: database.Database,
    perm: permissions.Permissions,
    CONSTANTS: CONSTANTS,
    FOUNDER_ID: int,) -> bool:
    parts =  message.text.split()
    
    try:
        # пытаемся изменить имя у айди parts[3]
        user_id = int(parts[3])
        # parts[4] до последнего слова
        new_full_name = " ".join(parts[4:])
        user = db.get_user_by_id(user_id)
        db.update_user_field(user_id, "full_name", new_full_name)
        bot.reply_to(message, f"Имя студента {user['telegram_id']} изменено на {new_full_name}!")
    except:
        bot.reply_to(message, '❌ Ошибка! Нужно написать в таком формате: "Калик, изменить имя 12345678 Фамилия Имя". Вместо 12345678 надо указать айди студента в ТГ ("Калик, айди")') 
    return True  # сигнал, что команда сработала
    # я хезе, это не везде есть, но мне в падлу это проверять :3
