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
    
    bot.reply_to(message, "Меня создал величайший VayLorm! Он же @MayITNick. Он меня наделил всеми теми репликами, которыми я обнимаю вас каждый день!\nВ общем, топ челик!")
    return True  # сигнал, что команда сработала
    # я хезе, это не везде есть, но мне в падлу это проверять :3
