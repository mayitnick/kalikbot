"""Старый, рабочий, но грязный код"""
"""if message.reply_to_message:
    reply_to_message_id = message.reply_to_message.from_user.id
    user = db.get_user_by_id(reply_to_message_id)
    if perm.check_for_permissions(author["type"], f"give.{parts[3]}"):
        if user:
            db.update_user_field(reply_to_message_id, "type", parts[3])
            bot.reply_to(message, f"Тип студента {user['telegram_id']} изменён на {parts[3]}!")
        else:
            bot.reply_to("Пользователь не найден. (я увидел, что ты ответил на сообщение, но не нашёл пользователя в БД)")
    else:
        if message.from_user.id == FOUNDER_ID:
            db.update_user_field(user_id, "type", parts[3])
            bot.reply_to(message, f"У тебя нет прав, но так как ты - основатель, я всё равно сделаю это!\nТип студента {user['telegram_id']} изменён на {parts[3]}!")
        else:
            bot.reply_to(message, random.choice(CONSTANTS["kalik_noperm"]))
# "Калик, измени тип 12345678 student"
else:
    user = db.get_user_by_id(user_id)
    if perm.check_for_permissions(author["type"], f"give.{parts[4]}"):
        if user:
            db.update_user_field(user_id, "type", parts[4])
            bot.reply_to(message, f"Тип студента {user['telegram_id']} изменён на {parts[4]}!")
        else:
            bot.reply_to("Пользователь не найден. (я увидел, что ты указал айди, но не нашёл пользователя в БД)")
    else:
        if message.from_user.id == FOUNDER_ID:
            db.update_user_field(user_id, "type", parts[4])
            bot.reply_to(message, f"У тебя нет прав, но так как ты - основатель, я всё равно сделаю это!\nТип студента {user['telegram_id']} изменён на {parts[4]}!")
        else:
            bot.reply_to(message, random.choice(CONSTANTS["kalik_noperm"]))
"""