import os
import signal
import threading
import time
from telebot import TeleBot
from telebot.types import Message

ALIASES = ["перезапуск", "рестарт", "перезагрузить", "поспи", "ложись"]

def handle(
    message: Message,
    bot: TeleBot,
    db=None,
    perm=None,
    CONSTANTS=None,
    FOUNDER_ID=None,
) -> bool:
    # Только основатель может перезапускать
    if message.from_user.id != FOUNDER_ID:
        bot.reply_to(message, "❌ Мяу~ 🐾 Я засыпаю так сладко только под рукой моего хозяина~  Я тут просто пушистик, нyaa~")
        return True

    # Сообщаем пользователю и даём время на доставку сообщения
    bot.reply_to(message, "🔄 Хи-хи~ 🐾 Сейчас я засну чуть-чуть, очищу хвостатые мысли, а Pterodactyl скоро разбудит меня~")


    def _delayed_shutdown():
        # Небольшая пауза, чтобы ответ успел уйти
        time.sleep(1)

        # Попытка аккуратно остановить polling (если используется polling)
        try:
            bot.stop_polling()
        except Exception:
            pass

        # Попытка "чистого" завершения через SIGTERM
        try:
            os.kill(os.getpid(), signal.SIGTERM)
        except Exception:
            # На крайний случай — форсированный выход
            os._exit(0)

    # Запускаем фоновую нить, которая завершит процесс
    threading.Thread(target=_delayed_shutdown, daemon=True).start()

    return True
