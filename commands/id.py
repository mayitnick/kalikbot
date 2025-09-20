# Алиасы, по которым будет срабатывать команда
ALIASES = ["айди", "id"]

def handle(message, bot, db, perm, CONSTANTS, FOUNDER_ID):
    parts = message.text.split()

    # Если пользователь хочет узнать свой айди
    if "мой" in message.text.lower():
        bot.reply_to(message, f"Айди: {message.from_user.id}")
        return

    # Если айди узнаём через реплай
    if message.reply_to_message:
        bot.reply_to(message, f"Айди: {message.reply_to_message.from_user.id}")
        return

    # Если айди указан через ник
    if len(parts) > 2:
        if parts[2][0] == "@":
            username = parts[2][1:]
            user = db.get_user_by_username(username)
            if user:
                user_id = user["telegram_id"]
                bot.reply_to(message, f"Айди: {user_id}")
                return

    # Если айди указан через entities (text_mention)
    if message.entities:
        for entity in message.entities:
            if entity.type == "text_mention":
                bot.reply_to(message, f"Айди: {entity.user.id}")
                return

    # Если ничего не подошло
    bot.reply_to(message, "Я не могу найти айди, если ты не ответил на сообщение")
