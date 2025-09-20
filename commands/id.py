from telebot import TeleBot
from telebot.types import Message
import modules.permissions as permissions
from modules.constants import CONSTANTS
import database

ALIASES = ["айди", "id"]

def handle(
    message: Message,
    bot: TeleBot,
    db: database.Database,
    perm: permissions.Permissions,
    CONSTANTS: CONSTANTS,
    FOUNDER_ID: int,
) -> None:
    parts = message.text.split()

    if "мой" in message.text.lower():
        bot.reply_to(message, f"Айди: {message.from_user.id}")
        return

    if message.reply_to_message:
        bot.reply_to(message, f"Айди: {message.reply_to_message.from_user.id}")
        return

    if len(parts) > 2 and parts[2][0] == "@":
        username = parts[2][1:]
        user = db.get_user_by_username(username)
        if user:
            user_id = user["telegram_id"]
            bot.reply_to(message, f"Айди: {user_id}")
            return

    if message.entities:
        for entity in message.entities:
            if entity.type == "text_mention":
                bot.reply_to(message, f"Айди: {entity.user.id}")
                return

    bot.reply_to(message, "Я не могу найти айди, если ты не ответил на сообщение")
