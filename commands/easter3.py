from telebot import TeleBot
from telebot.types import Message
import modules.permissions as permissions
from modules.constants import CONSTANTS
import database

ALIASES = ["парить", "курить", "куришь", "паришь", "ашка", "ашку"]

def handle(
    message: Message,
    bot: TeleBot,
    db: database.Database,
    perm: permissions.Permissions,
    CONSTANTS: CONSTANTS,
    FOUNDER_ID: int,) -> bool:
    
    bot.reply_to(message, "Эй! >:( Я ж не курю, фу-фу! (≧へ≦ )")
    return True  # сигнал, что команда сработала
    # я хезе, это не везде есть, но мне в падлу это проверять :3
