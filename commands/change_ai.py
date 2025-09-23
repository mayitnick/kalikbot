from telebot import TeleBot
from telebot.types import Message
import modules.permissions as permissions
from modules.constants import CONSTANTS
import modules.ai as ai
import database

ALIASES = ["изменить ии"]

def handle(
    message: Message,
    bot: TeleBot,
    db: database.Database,
    perm: permissions.Permissions,
    CONSTANTS: CONSTANTS,
    FOUNDER_ID: int,
) -> bool:
    try:
        text = message.text.lower()
        for alias in ALIASES:
            if text.startswith(f"кали, {alias}"):
                text = message.text[len(f"Калик, {alias}"):].strip()
                break

        if not text:
            # Если пользователь не указал модель → выводим список
            models = ai.list_models()
            if not models:
                bot.reply_to(message, "Не удалось получить список моделей (・へ・)")
            else:
                reply_text = "Доступные модели:\n\n" + "\n".join(models)
                bot.reply_to(message, reply_text[:4000])  # ограничение телеги
        else:
            # Пользователь указал модель → меняем её
            chosen = ai.set_model(text)
            bot.reply_to(message, f"Модель изменена на: `{chosen}` ✨", parse_mode="Markdown")

        return True
    except Exception as e:
        bot.reply_to(message, f"Ошибка модуля изменить ии: {e}")
        return False
