from telebot import TeleBot
from telebot.types import Message
import modules.permissions as permissions
from modules.constants import CONSTANTS
import database

ALIASES = ["привет", "хай"]

def handle(
    message: Message,
    bot: TeleBot,
    db: database.Database,
    perm: permissions.Permissions,
    CONSTANTS: CONSTANTS,
    FOUNDER_ID: int,) -> bool:
    
    bot.send_sticker(message.chat.id, "CAACAgIAAxkBAAE7gGho0jhXFIdOkmj0bLHxCrcDe37l9QAC9RUAAsR5-Urb_UUJV9x07jYE")
    return True  # сигнал, что команда сработала
    # я хезе, это не везде есть, но мне в падлу это проверять :3
