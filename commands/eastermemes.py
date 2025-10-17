from telebot import TeleBot
from telebot.types import Message
import modules.permissions as permissions
from modules.constants import CONSTANTS
import database
import requests

ALIASES = ["meme"]

def handle(
    message: Message,
    bot: TeleBot,
    db: database.Database,
    perm: permissions.Permissions,
    CONSTANTS: CONSTANTS,
    FOUNDER_ID: int,) -> bool:
    
    print("Fetching meme...")
    try:
        data = requests.get("https://meme-api.com/gimme/Pikabu", timeout=5)
    except requests.exceptions.Timeout:
        bot.reply_to(message, "Мемы слишком долго грузятся! Попробуй позже.")
        return False
    except requests.exceptions.RequestException as e:
        bot.reply_to(message, f"Ошибка получения мема: {e}")
        return False
    print("Meme data received.")
    
    """
    Пример выводимых данных:
    {
        "postLink": "https://redd.it/1o6qqkp",
        "subreddit": "Pikabu",
        "title": "Да что вы знаете о бюджетных сборках!",
        "url": "https://i.redd.it/23f85qvvz4vf1.png",
        "nsfw": false,
        "spoiler": false,
        "author": "DarkAster_86",
        "ups": 136,
        "preview": [
            "https://preview.redd.it/23f85qvvz4vf1.png?width=108&crop=smart&auto=webp&s=7081ab083a9a103c41f7c6c3d1e7f1ed04f832f2",
            "https://preview.redd.it/23f85qvvz4vf1.png?width=216&crop=smart&auto=webp&s=7fca8315d7e6b11b521df116db97d94c2beb2991",
            "https://preview.redd.it/23f85qvvz4vf1.png?width=320&crop=smart&auto=webp&s=12466979d88cda89998a9c79f29a03d9fc220436",
            "https://preview.redd.it/23f85qvvz4vf1.png?width=640&crop=smart&auto=webp&s=47c59fa45acb032104f2e3fa63d9318412d16b04",
            "https://preview.redd.it/23f85qvvz4vf1.png?width=960&crop=smart&auto=webp&s=996a9ec44548b03310996abb9a3055f7b7656472",
            "https://preview.redd.it/23f85qvvz4vf1.png?width=1080&crop=smart&auto=webp&s=eadc821672921c1b1592163ee2abafa5b952ff79"
        ]
    }
    """
    
    print("Processing meme data...")
    if data.status_code == 200:
        if data.json() is None:
            bot.reply_to(message, "Не удалось получить мем, попробуй ещё раз позже!")
            return False
        meme_json = data.json()
        # нужно как то получить картинку с ссылки и отправить в чат
        meme_url = meme_json.get("url")
        meme_title = meme_json.get("title")
        if meme_url:
            if meme_title:
                bot.send_photo(message.chat.id, meme_url, caption=meme_title)
            else:
                bot.send_photo(message.chat.id, meme_url)
    else:
        bot.reply_to(message, "Не удалось получить мем, попробуй ещё раз позже!")
    print("Meme sent.")
    return True  # сигнал, что команда сработала
    # я хезе, это не везде есть, но мне в падлу это проверять :3
