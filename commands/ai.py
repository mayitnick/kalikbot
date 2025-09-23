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
        # Достаём имя и пол пользователя
        user_firstname = message.from_user.first_name or "пользователь"
        user_is_male = message.from_user.is_premium  # тут костыль, в API Telegram пола нет
        # В базе можно хранить выбранный пол/обращение (если реализуешь)
        
        # Формируем текст с контекстом
        user_context = f"Имя пользователя: {user_firstname}. " \
                       f"Пол: {'мужской' if user_is_male else 'неизвестен/женский'}. " \
                       f"Сообщение: {message.text}"
        
        answer = ai.ask_io_net(user_context)
        
        if not answer or answer.strip() == "":
            answer = f"{user_firstname}, я что-то завис... повтори? (・・ )?"
        
        bot.reply_to(message, answer)
        return True
    except Exception as e:
        bot.reply_to(message, f"Ошибка модуля ии: {e}")
        return False
