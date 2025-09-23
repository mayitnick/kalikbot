from telebot import TeleBot
from telebot.types import Message
import modules.permissions as permissions
from modules.constants import CONSTANTS
import modules.react as react
import database

ALIASES = ["харофий", "хороший", "харош", "хароший", "добрий", "добрый", "лютый", "имба", "лега", "легенда"]

def handle(
    message: Message,
    bot: TeleBot,
    db: database.Database,
    perm: permissions.Permissions,
    CONSTANTS: CONSTANTS,
    FOUNDER_ID: int,) -> bool:
    
    react.send_react(message.chat.id, message.message_id, "🔥")
    return True  # сигнал, что команда сработала
    # я хезе, это не везде есть, но мне в падлу это проверять :3
