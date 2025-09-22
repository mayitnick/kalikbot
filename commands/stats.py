import psutil
from telebot import TeleBot
from telebot.types import Message
import modules.permissions as permissions
from modules.constants import CONSTANTS
import database
import os

ALIASES = ["система", "статус", "загрузка"]

def get_container_memory_limit_gb():
    """Возвращает лимит памяти контейнера в ГБ"""
    try:
        with open("/sys/fs/cgroup/memory/memory.limit_in_bytes", "r") as f:
            limit = int(f.read())
        # Если лимит слишком большой (например, хост не ограничен), используем psutil
        if limit > 1e12:  # больше ~1 ТБ считаем неограниченным
            return None
        return limit / 1e9
    except Exception:
        return None

def get_container_memory_usage_gb():
    """Возвращает текущую используемую память контейнера в ГБ"""
    try:
        with open("/sys/fs/cgroup/memory/memory.usage_in_bytes", "r") as f:
            usage = int(f.read())
        return usage / 1e9
    except Exception:
        return None

def get_cpu_count_container():
    """Количество доступных ядер для контейнера"""
    try:
        return len(os.sched_getaffinity(0))
    except Exception:
        return psutil.cpu_count()

def handle(
    message: Message,
    bot: TeleBot,
    db: database.Database,
    perm: permissions.Permissions,
    CONSTANTS: CONSTANTS,
    FOUNDER_ID: int,
) -> bool:
    # CPU
    cpu_usage = psutil.cpu_percent(interval=1)
    cpu_count = get_cpu_count_container()
    
    # RAM
    ram_limit_gb = get_container_memory_limit_gb()
    ram_used_gb = get_container_memory_usage_gb()
    
    if ram_limit_gb is None or ram_used_gb is None:
        ram = psutil.virtual_memory()
        ram_used_gb = round(ram.used / 1e9, 2)
        ram_limit_gb = round(ram.total / 1e9, 2)
    
    ram_usage_percent = round((ram_used_gb / ram_limit_gb) * 100, 2)

    # Формируем ответ
    response = (
        f"✨ Статус системы контейнера ✨\n"
        f"CPU загрузка: {cpu_usage}% (доступно ядер: {cpu_count})\n"
        f"ОЗУ использовано: {ram_used_gb:.2f} ГБ / {ram_limit_gb:.2f} ГБ ({ram_usage_percent}%)\n"
    )

    bot.reply_to(message, response)
    return True

