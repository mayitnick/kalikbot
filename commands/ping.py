# commands/ping.py
import time

ALIASES = ["пинг", "понг"]

def handle(message, bot, db, perm, CONSTANTS, FOUNDER_ID):
    start = time.time()
    sent_msg = bot.send_message(message.chat.id, "Пингую...")
    end = time.time()
    ping_ms = int((end - start) * 1000)
    bot.edit_message_text(
        f"Мой пинг: {ping_ms} мс. Хорошо считаю, правда? :3",
        chat_id=message.chat.id,
        message_id=sent_msg.message_id,
    )