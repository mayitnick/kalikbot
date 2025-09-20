from telebot import TeleBot
from telebot.types import Message
import modules.permissions as permissions
from modules.constants import CONSTANTS
import database
from typing import Any, Dict
import random
import re

# Алиасы можно оставить пустыми — мы будем ловить "чистый зов"
ALIASES = []

def handle(
    message: Message,
    bot: TeleBot,
    db: database.Database,
    perm: permissions.Permissions,
    CONSTANTS: CONSTANTS,
    FOUNDER_ID: int,) -> bool:
    
    text = message.text.lower().strip()
    is_only_kalik = bool(re.match(r"^кал[а-яё]*$", text))

    if is_only_kalik:
        bot.reply_to(message, random.choice(CONSTANTS.kalik_answers))
        return True  # сигнал, что команда сработала
    return False
