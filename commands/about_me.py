from telebot import TeleBot
from telebot.types import Message
import modules.permissions as permissions
from modules.constants import CONSTANTS
import database

# Временное решение, нужно будет это потом в отдельный модуль вынести ;)
def get_url_from_id(full_name, id):
    # [Имя](tg://user?id=123456789)
    return f"[{full_name}](tg://user?id={id})"

ALIASES = ["я", "обо мне"]

def handle(
    message: Message,
    bot: TeleBot,
    db: database.Database,
    perm: permissions.Permissions,
    CONSTANTS: CONSTANTS,
    FOUNDER_ID: int,) -> bool:
    
    user = db.get_user_by_id(message.from_user.id)
    if user:
        full_name = user["full_name"]
        bot.reply_to(message,
                        f"Информация о {get_url_from_id(full_name, message.from_user.id)}\nАйди: {user['telegram_id']}\nТип: {user['type']}\nГруппа: {user['group']}")
    bot.reply_to(message, "Меня создал величайший VayLorm! Он же @MayITNick. Он меня наделил всеми теми репликами, которыми я обнимаю вас каждый день!\nВ общем, топ челик!")
    return True  # сигнал, что команда сработала
    # я хезе, это не везде есть, но мне в падлу это проверять :3
