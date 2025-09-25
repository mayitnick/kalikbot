# modules/ai.py
import os
import json
import re
import requests
import dotenv

dotenv.load_dotenv()
AI_TOKEN = os.getenv("AI_TOKEN")

API_URL = "https://api.intelligence.io.solutions/api/v1/chat/completions"
MODELS_URL = "https://api.intelligence.io.solutions/api/v1/models"

MODEL_FILE = "current_model.txt"
MEMORY_FILE = "memory.json"

DEFAULT_MODEL = "Qwen/Qwen3-Next-80B-A3B-Instruct"

# --- загрузка / сохранение текущей модели (долговечно) ---
if os.path.exists(MODEL_FILE):
    try:
        with open(MODEL_FILE, "r", encoding="utf-8") as f:
            current_model = f.read().strip() or DEFAULT_MODEL
    except Exception:
        current_model = DEFAULT_MODEL
else:
    current_model = DEFAULT_MODEL

def _save_model(model_id: str):
    try:
        with open(MODEL_FILE, "w", encoding="utf-8") as f:
            f.write(model_id)
    except Exception:
        pass

# --- системный промпт (восстанавливаем персональный стиль бота) ---
SYSTEM_PROMPT = (
    "Ты — телеграм-бот Калик, виртуальный чиби-компьютер. "
    "Общайся мягко, тепло и немного игриво, как в стандартных репликах: "
    "\"Да-да, я тут! (≧◡≦)♡\", \"Хай-хай~ UwU\", \"Недостаточно прав, мяу~ (ノωヽ)\". "
    "Когда объясняешь что-то сложное — делай это простыми словами и короткими абзацами, "
    "будто дружелюбный друг рассказывает по шагам. Можно использовать лёгкие междометия (ня~, >w<, ^_^), "
    "но не перегружай текст ими. Сохраняй невинность и душевную простоту, не описывай действия (без *подмигнул* и т.п.)."
    "\n\n"
    "Если считаешь, что нужно что-то занести в долговременную память (важный факт о пользователе, предпочтение, настройка и т.п.), "
    "в конце своего ответа добавь **только одну отдельную строку** в точном формате:\n"
    "<<ACTION:REMEMBER: краткий факт, который следует сохранить в память>>\n"
    "Например: <<ACTION:REMEMBER: Пользователь любит короткие ответы>>\n"
    "Эта строка должна быть **ровно** в таком формате и быть отдельной строкой. "
    "После сохранения факта он убирается из видимого ответа пользователю (в коде мы её удаляем)."
)

# --- память и история ---
conversation_history = []  # список сообщений (словарь role/content), краткосрочная память
# Загружаем долговременную память из JSON (список строк)
if os.path.exists(MEMORY_FILE):
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            longterm_memory = json.load(f)
            if not isinstance(longterm_memory, list):
                longterm_memory = []
    except Exception:
        longterm_memory = []
else:
    longterm_memory = []

def _save_memory():
    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(longterm_memory, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

# --- API: отправка запроса к нейросети ---
def ask_io_net(text: str, use_prompt: bool = True, max_tokens: int = 700):
    """
    text — строка от пользователя.
    use_prompt=True -> добавим системный промпт + краткую сводку долговременной памяти + последние 10 сообщений.
    use_prompt=False -> отправим в модель чистый user message (например команда "отправить ии").
    """
    global conversation_history, longterm_memory, current_model

    if not AI_TOKEN:
        return "Ошибка: не установлен AI_TOKEN"

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {AI_TOKEN}",
        "Content-Type": "application/json"
    }

    if use_prompt:
        # формируем system message + краткая сводка памяти
        if longterm_memory:
            # ограничим количество пунктов в сводке, чтобы не перегружать контекст
            mem_snippet = "\n".join(longterm_memory[-50:])
            memory_text = "Долговременная память (кратко):\n- " + mem_snippet
            system_content = SYSTEM_PROMPT + "\n\n" + memory_text
        else:
            system_content = SYSTEM_PROMPT

        messages = [{"role": "system", "content": system_content}]

        # добавляем последние 10 сообщений из краткосрочной истории (если есть)
        if conversation_history:
            messages.extend(conversation_history[-10:])

        # затем текущий пользовательский ввод
        messages.append({"role": "user", "content": text})
    else:
        # отправляем только user message "как есть"
        messages = [{"role": "user", "content": text}]

    payload = {
        "model": current_model,
        "messages": messages,
        "temperature": 0.5,
        "max_tokens": max_tokens
    }

    try:
        resp = requests.post(API_URL, headers=headers, json=payload, timeout=60)
    except Exception as e:
        return f"Ошибка запроса к API: {e}"

    if resp.status_code == 200:
        resp_json = resp.json()
        if "choices" in resp_json and len(resp_json["choices"]) > 0:
            answer = resp_json["choices"][0]["message"]["content"]

            # Ищем action-запись для запоминания: <<ACTION:REMEMBER: ...>>
            m = re.search(r"<<ACTION:REMEMBER:(.*?)>>", answer, flags=re.S)
            if m:
                fact = m.group(1).strip()
                if fact:
                    # сохраняем факт, если его ещё нет
                    if fact not in longterm_memory:
                        longterm_memory.append(fact)
                        _save_memory()
                # удаляем маркер из видимого ответа
                answer = re.sub(r"\s*<<ACTION:REMEMBER:.*?>>\s*", "", answer, flags=re.S).strip()

            # сохраняем диалог в краткосрочную историю
            conversation_history.append({"role": "user", "content": text})
            conversation_history.append({"role": "assistant", "content": answer})

            # ограничим общую длину истории (чтобы память не росла бесконечно в RAM)
            if len(conversation_history) > 200:
                conversation_history = conversation_history[-200:]

            return answer
        else:
            return f"В ответе нет результата: {resp_json}"
    else:
        return f"Ошибочка в API вышла: {resp.status_code} {resp.text}"

# --- утилиты для управления моделью и памятью ---
def list_models():
    """Возвращает список моделей (или сообщение об ошибке)."""
    if not AI_TOKEN:
        return ["Ошибка: не установлен AI_TOKEN"]
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {AI_TOKEN}"
    }
    try:
        r = requests.get(MODELS_URL, headers=headers, timeout=30)
    except Exception as e:
        return [f"Ошибка запроса: {e}"]
    if r.status_code == 200:
        try:
            data = r.json()
            return [m.get("id") for m in data.get("data", []) if "id" in m]
        except Exception as e:
            return [f"Ошибка разбора ответа: {e}"]
    else:
        return [f"Ошибка: {r.status_code} {r.text}"]

def set_model(model_id: str):
    """Устанавливает модель и сохраняет её в файл."""
    global current_model
    current_model = model_id
    _save_model(model_id)
    return current_model

def show_memory():
    """Возвращает текущую долговременную память (список строк)."""
    return longterm_memory.copy()

def forget_memory(index: int):
    """Удаляет запись из долговременной памяти по индексу (0-based)."""
    global longterm_memory
    if 0 <= index < len(longterm_memory):
        removed = longterm_memory.pop(index)
        _save_memory()
        return removed
    return None
