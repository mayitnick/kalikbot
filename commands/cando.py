from telebot import TeleBot
from telebot.types import Message
import modules.permissions as permissions
from modules.constants import CONSTANTS
import database

ALIASES = ["можешь", "умеешь", "команды", "помощь"]

def handle(
    message: Message,
    bot: TeleBot,
    db: database.Database,
    perm: permissions.Permissions,
    CONSTANTS: CONSTANTS,
    FOUNDER_ID: int,) -> bool:
    
    bot.reply_to(message, "Я пока мало что умею. " \
                 "Но я буду старатся учится, честно-честно! " \
                 "Обо мне можно прочитать на вики, " \
                 "где всё подробно расфыркано: " \
                 "https://mayitnick.github.io/kalikbot-docs/")
    return True  # сигнал, что команда сработала
    # я хезе, это не везде есть, но мне в падлу это проверять :3
