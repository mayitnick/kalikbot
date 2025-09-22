from telebot import TeleBot
from telebot.types import Message
import sys

ALIASES = ["перезапуск", "рестарт", "перезагрузить"]

def handle(
    message: Message,
    bot: TeleBot,
    db=None,
    perm=None,
    CONSTANTS=None,
    FOUNDER_ID=None,
) -> bool:
    # Проверяем, что команду может выполнять только основатель
    if message.from_user.id != FOUNDER_ID:
        bot.reply_to(message, "❌ Только основатель может перезапустить сервер~ 🦊✨")
        return True

    bot.reply_to(message, "🔄 Скрипт завершает работу… Панель Pterodactyl подхватит и запустит его заново~ 💛")
    
    sys.exit(0)  # Завершаем скрипт, автоперезапуск сработает
    
    return True
