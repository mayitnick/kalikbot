#  $$\   $$\          $$\ $$\           $$\             $$\ 
#  $$ | $$  |         $$ |\__|          $$ |            $$ |
#  $$ |$$  / $$$$$$\  $$ |$$\  $$$$$$$\ $$ |  $$\       $$ |
#  $$$$$  /  \____$$\ $$ |$$ |$$  _____|$$ | $$  |      $$ |
#  $$  $$<   $$$$$$$ |$$ |$$ |$$ /      $$$$$$  /       \__|
#  $$ |\$$\ $$  __$$ |$$ |$$ |$$ |      $$  _$$<            
#  $$ | \$$\\$$$$$$$ |$$ |$$ |\$$$$$$$\ $$ | \$$\       $$\ 
#  \__|  \__|\_______|\__|\__| \_______|\__|  \__|      \__|
#
# Created by: MayITNick

# Бот для техникума!

# Импортируем необходимые библиотеки
from telebot import types, TeleBot
import modules.permissions as permissions
import modules.constants as constants
import modules.ai as ai
from dotenv import load_dotenv
from datetime import datetime
import requests
import database
import os
import re
import importlib
import pkgutil
import commands
from commands import double

COMMANDS = []

def send_to_ai(message):
    try:
        text = message.text or "привет"
        sent_msg = bot.reply_to(message, "Секу, дай подумать...")

        # передаём message.chat.id в ai
        answer = ai.ask_io_net(text.replace('--force', ''), user_id=message.from_user.id, chat_id=message.chat.id)

        if not answer.strip():
            answer = "(завис... попробуй ещё раз?) (・・ )?"

        bot.edit_message_text(
            answer,
            chat_id=message.chat.id,
            message_id=sent_msg.message_id,
        )
        return True
    except Exception as e:
        bot.reply_to(message, f"Ошибка модуля ии: {e}")
        return False

for _, module_name, _ in pkgutil.iter_modules(commands.__path__):
    module = importlib.import_module(f"commands.{module_name}")
    COMMANDS.append(module)

load_dotenv()

db = database.Database()
perm = permissions.Permissions()
CONSTANTS = constants.CONSTANTS()
bot = TeleBot(os.getenv('TOKEN'))
profanity_regex = re.compile(r"(\s+|^)[пПnрРp]?[3ЗзВBвПnпрРpPАaAаОoO0о]?[сСcCиИuUОoO0оАaAаыЫуУyтТT]?[Ппn][иИuUeEеЕ][зЗ3][ДдDd]\w*[\?\,\.\;\-]*|(\s+|^)[рРpPпПn]?[рРpPоОoO0аАaAзЗ3]?[оОoO0иИuUаАaAcCсСзЗ3тТTуУy]?[XxХх][уУy][йЙеЕeEeяЯ9юЮ]\w*[\?\,\.\;\-]*|(\s+|^)[бпПnБ6][лЛ][яЯ9]([дтДТDT]\w*)?[\?\,\.\;\-]*|(\s+|^)(([зЗоОoO03]?[аАaAтТT]?[ъЪ]?)|(\w+[оОOo0еЕeE]))?[еЕeEиИuUёЁ][бБ6пП]([аАaAиИuUуУy]\w*)?[\?\,\.\;\-]*")

FOUNDER_ID = int(os.getenv('FOUNDER_ID'))

def check_for_kalik(message):
    text = message.text.lower().strip()
    # Ловим любой "зов", даже с командами
    # "Кал..."
    # К примеру - "Калииик, пинг"
    return bool(re.match(r"^кал[а-яё]*[,.!?]?\s*", text))

def get_url_from_id(full_name, id):
    # [Имя](tg://user?id=123456789)
    return f"[{full_name}](tg://user?id={id})"

def if_reply_to_message(message, user_id):
    if message.reply_to_message:
        reply_to_message_id = message.reply_to_message.from_user.id
        return db.get_user_by_id(reply_to_message_id), 1
    else:
        return db.get_user_by_id(int(user_id)), 0

def get_current_pair(schedule_times):
    """
    schedule_times = ["8:20-9:50", "10:00-11:30", ...]
    Возвращает (номер пары, минуты до конца) или (None, None)
    """
    now = datetime.now().time()

    for i, pair in enumerate(schedule_times, start=1):
        start_str, end_str = pair.split("-")
        start = datetime.strptime(start_str, "%H:%M").time()
        end = datetime.strptime(end_str, "%H:%M").time()

        if start <= now <= end:
            now_dt = datetime.combine(datetime.today(), now)
            end_dt = datetime.combine(datetime.today(), end)
            remaining = int((end_dt - now_dt).total_seconds() // 60)
            return i, remaining

    return None, None

@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.type == 'private':
        markup = types.InlineKeyboardMarkup()
        bot_username = (bot.get_me()).username
        add_to_group_url = f"https://t.me/{bot_username}?startgroup=true"
        button1 = types.InlineKeyboardButton("Добавь меня в группу :3", url=add_to_group_url)
        markup.add(button1)
        bot.reply_to(message, "Привет! Я Калик, и мой функционал раскрывается только в группе!", reply_markup=markup)

@bot.message_handler(commands=['ping'])
def ping_command(message):
    bot.reply_to(message, "🏓 Поньг~")
    
@bot.message_handler(commands=['0'])
def delmes_command(message: types.Message):
    reply_message = message.reply_to_message
    author_id = message.from_user.id
    bot.delete_message(message.chat.id, message.id)
    if reply_message and author_id == int(FOUNDER_ID):
        bot.delete_message(message.chat.id, reply_message.id)
    

def send_long_message(chat_id, text):
    max_len = 4000  # чуть меньше лимита, чтобы с запасом
    for i in range(0, len(text), max_len):
        bot.send_message(chat_id, text[i:i+max_len])

@bot.message_handler(commands=["analyze"])
def analyze_command(message):
    print("DEBUG: /analyze вызвана")  # Старт команды

    # Проверяем, что сообщение — ответ на другое сообщение
    if not message.reply_to_message:
        bot.reply_to(message, "DEBUG: нет reply_to_message. Нужно ответить на фото.")
        print("DEBUG: Сообщение не в ответ на фото")
        return

    print(f"DEBUG: reply_to_message есть, content_type: {message.reply_to_message.content_type}")

    # Ищем фото
    if message.reply_to_message.photo:
        photo = message.reply_to_message.photo[-1]
        file_id = photo.file_id
        print(f"DEBUG: найдено фото, file_id={file_id}, размеры: {photo.width}x{photo.height}")
    elif message.reply_to_message.document and message.reply_to_message.document.mime_type.startswith("image/"):
        file_id = message.reply_to_message.document.file_id
        print(f"DEBUG: найден документ с изображением, file_id={file_id}")
    else:
        bot.reply_to(message, "DEBUG: не найдено фото или изображение в документе")
        return

    sent_msg = bot.reply_to(message, "Ням-ням, анализирую изображение… ⏳")

    try:
        print("DEBUG: вызываем ai.analyze_image_file")
        description = ai.analyze_image_file(
            file_id=file_id,
            user_id=message.from_user.id,
            bot=bot,
            prompt="Что на этом изображении?"
        )
        print(f"DEBUG: analyse_image_file вернула: {description[:100]}...")  # первые 100 символов

        if not description:
            description = "Упс… анализ занял слишком много времени. Попробуй прислать фото снова чуть позже ^_^"

        bot.edit_message_text(
            description,
            chat_id=sent_msg.chat.id,
            message_id=sent_msg.message_id
        )
        print("DEBUG: сообщение с результатом отправлено")
    except Exception as e:
        bot.edit_message_text(
            f"Ошибка при анализе изображения: {e}",
            chat_id=sent_msg.chat.id,
            message_id=sent_msg.message_id
        )
        print(f"DEBUG: исключение в analyze_command: {e}")

@bot.message_handler(commands=['check'])
def check_admin_rights(message):
    # Получаем информацию о боте как о члене чата
    chat_id = message.chat.id
    bot_user_id = bot.get_me().id  # ID самого бота
    chat_member = bot.get_chat_member(chat_id, bot_user_id)
    
    # Проверяем статус и права
    if chat_member.status == 'administrator':
        rights = []
        if chat_member.can_post_messages:
            rights.append('Может публиковать сообщения')
        if chat_member.can_edit_messages:
            rights.append('Может редактировать сообщения')
        if chat_member.can_delete_messages:
            rights.append('Может удалять сообщения')
        if chat_member.can_invite_users:
            rights.append('Может приглашать пользователей')
        if chat_member.can_restrict_members:
            rights.append('Может ограничивать участников')
        if chat_member.can_pin_messages:
            rights.append('Может закреплять сообщения')
        if chat_member.can_promote_members:
            rights.append('Может назначать админов')
        print("Права:" + "\n".join(rights))
    else:
        print("Походу, у бота нет прав администратора в этом чате.")
    bot.send_message(chat_id, "Я проверил все модули, и вывел в консоль :)")

# --- команды для управления памятью ---

# показать личную память
@bot.message_handler(commands=["showmem"])
def showmem(message):
    user_mem = ai.show_memory(message.from_user.id)
    if not user_mem:
        bot.reply_to(message, "Память пользователя пустая~ (｡･ω･｡)")
    else:
        lines = [f"{i}. {fact}" for i, fact in enumerate(user_mem)]
        bot.reply_to(message, "Личная память:\n" + "\n".join(lines))


# показать память чата
@bot.message_handler(commands=["showchatmem"])
def showchatmem(message):
    chat_mem = ai.show_chat_memory(message.chat.id)
    if not chat_mem:
        bot.reply_to(message, "Память чата пустая~")
    else:
        lines = [f"{i}. {fact}" for i, fact in enumerate(chat_mem)]
        bot.reply_to(message, "Память этого чата:\n" + "\n".join(lines))


# забыть факт по индексу или тексту
@bot.message_handler(commands=["forget"])
def forget(message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        bot.reply_to(message, "Укажи, что забыть: индекс или текст~")
        return

    arg = args[1].strip()
    if arg.isdigit():
        idx = int(arg)
        removed = ai.forget_memory(message.from_user.id, idx)
        if removed:
            bot.reply_to(message, f"Удалил из памяти: {removed}")
        else:
            bot.reply_to(message, "Не нашёл факт с таким индексом.")
    else:
        removed_list = ai.forget_memory_by_text(message.from_user.id, arg)
        if removed_list:
            bot.reply_to(message, "Удалил факты:\n" + "\n".join(removed_list))
        else:
            bot.reply_to(message, "Не нашёл фактов, содержащих этот текст.")


# сбросить личную память
@bot.message_handler(commands=["resetmem"])
def resetmem(message):
    ok = ai.reset_memory(message.from_user.id)
    if ok:
        bot.reply_to(message, "Личная память очищена~")
    else:
        bot.reply_to(message, "Память и так пуста.")


# сбросить память чата
@bot.message_handler(commands=["resetchatmem"])
def resetchatmem(message):
    ok = ai.reset_chat_memory(message.chat.id)
    if ok:
        bot.reply_to(message, "Память чата очищена~")
    else:
        bot.reply_to(message, "Память чата и так пуста.")

@bot.message_reaction_handler(func=lambda m: True)
def handle_reaction(reaction):
    # Информация о чате
    chat_info = f"Чат: {reaction.chat.title} (ID: {reaction.chat.id})"
    
    # ID сообщения
    message_info = f"Сообщение: {reaction.message_id}"
    
    # Кто поставил реакцию (если не аноним)
    user_info = f"Пользователь: {reaction.user.first_name} {reaction.user.last_name} (ID: {reaction.user.id})" if reaction.user else "Пользователь: Аноним"
    
    # Если реакция анонимная, но есть actor_chat
    if not reaction.user and reaction.actor_chat:
        user_info = f"Чат (аноним): {reaction.actor_chat.title} (ID: {reaction.actor_chat.id})"
    
    # Дата
    from datetime import datetime
    date_info = f"Дата: {datetime.fromtimestamp(reaction.date)}"
    
    # Старые и новые реакции
    old_reactions = [r.emoji if hasattr(r, 'emoji') else r.type for r in reaction.old_reaction]
    new_reactions = [r.emoji if hasattr(r, 'emoji') else r.type for r in reaction.new_reaction]
    
    reactions_info = f"Старые реакции: {old_reactions}\nНовые реакции: {new_reactions}"
    
    # Вывод всей информации
    info = f"{chat_info}\n{message_info}\n{user_info}\n{date_info}\n{reactions_info}"
    print(info)
    bot.send_message(reaction.chat.id, info)

    # Проверка: если автор — нужный ID и реакция 🙊, удаляем сообщение
    if reaction.user and reaction.user.id == 1408266288:
        for r in reaction.new_reaction:
            if hasattr(r, 'emoji') and r.emoji == '🙊':
                try:
                    bot.delete_message(reaction.chat.id, reaction.message_id)
                    bot.send_message(reaction.chat.id, "Сообщение удалено по правилам.")
                except Exception as e:
                    print(f"Ошибка при удалении сообщения: {e}")
                break

# Сделаем обработчик для всех сообщений
@bot.message_handler(func=lambda message: True)
def message_listener(message):
    # Запоминаем =3
    author = message.from_user
    last_name = author.last_name
    chat = message.chat
    chat_type = chat.type

    print(f"DEBUG: {author.id} {type(author.id)} {message.text}")
    
    if chat_type == "group" or chat_type == "supergroup":
        print(f"Кажется, это в группе пишут. ({chat_type})")
    
    if author.id == 8539187812:
        bot.delete_message(message.chat.id, message.id)
    if not last_name:
        last_name = ""
    if not db.get_user_by_id(author.id):
        db.add_user(telegram_id=author.id,
                    telegram_username=author.username,
                    full_name=author.first_name + last_name)
    if chat_type == "group" or chat_type == "supergroup":
        # Заглушка
        user = db.get_user_by_id(author.id)
        group = get_group_by_id(chat.id)
        if group:
            db.upgrade_to_student(author.id, group["group"])
            db.add_student(group["group"], author.id)
            
    if check_for_kalik(message):
        kalik(message)
    
def kalik(message):
    text = message.text.lower()
    
    """contains_profanity = bool(profanity_regex.search(text))
    if contains_profanity:
        bot.reply_to(message, "Я не люблю маты! 😡")
        return"""
    
    if "--force" in text:
        send_to_ai(message)
        return
    
    # 1. Сначала проверяем чистый зов
    from commands import call
    if call.handle(message, bot, db, perm, CONSTANTS, FOUNDER_ID):
        return

    # 2. Потом остальные команды
    for cmd in COMMANDS:
        if any(alias in text for alias in getattr(cmd, "ALIASES", [])):
            cmd.handle(message, bot, db, perm, CONSTANTS, FOUNDER_ID)
            return

    # 3. Если ничего не подошло
    # bot.reply_to(message, random.choice(CONSTANTS.dont_know))
    # Раньше бот не знал что делать, а теперь, мы отправляем нейросетке сообщение >:3
    send_to_ai(message)

double.handle_callback(bot)

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    data = call.data
    if data.startswith("group."):
        if call.from_user.id == FOUNDER_ID:
            group_name = data.split(".")[1]
            group = db.get_group_by_name(group_name)
            # Доделать надо, я спать :|

me = bot.get_me()
print(f"Я запущен :3 У меня ник @{me.username} с id {me.id}.\nГотов помогать!")
bot.send_message(FOUNDER_ID, "🔥 Калик запущен!")
try:
    bot.infinity_polling()
except requests.exceptions.ConnectionError:
    print("🌐 Ой, интернет потерялся... ищем снова 🦊")
except Exception as e:
    # на всякий случай ловим всё остальное
    print(f"⚠ Неожиданная ошибка: {e}")
