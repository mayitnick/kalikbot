import re
import random

# Алиасы можно оставить пустыми — мы будем ловить "чистый зов"
ALIASES = []

def handle(message, bot, db, perm, CONSTANTS, FOUNDER_ID):
    text = message.text.lower().strip()
    is_only_kalik = bool(re.match(r"^кал[а-яё]*$", text))

    if is_only_kalik:
        bot.reply_to(message, random.choice(CONSTANTS["kalik_answers"]))
        return True  # сигнал, что команда сработала
    return False
