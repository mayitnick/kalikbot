from telebot import TeleBot
from telebot.types import Message
import modules.permissions as permissions
from modules.constants import CONSTANTS
import modules.ai as ai
import database

ALIASES = ["ии"]

def handle(
    message: Message,
    bot: TeleBot,
    db: database.Database,
    perm: permissions.Permissions,
    CONSTANTS: CONSTANTS,
    FOUNDER_ID: int,
) -> bool:
    try:
        # Берём текст без команды/алиаса
        text = message.text
        for alias in ALIASES:
            if text.lower().startswith(f"кали {alias}"):
                text = text[len(f"кали {alias}"):].strip()
                break

        if not text:
            text = "привет"  # чтобы не отправлять пустоту в нейросеть

        answer = ai.ask_io_net(text)

        if not answer or answer.strip() == "":
            answer = "(завис... попробуй ещё раз?) (・・ )?"

        bot.reply_to(message, answer)
        return True
    except Exception as e:
        bot.reply_to(message, f"Ошибка модуля ии: {e}")
        return False