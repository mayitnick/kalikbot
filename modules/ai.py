import os
import requests
import dotenv

dotenv.load_dotenv()
AI_TOKEN = os.getenv("AI_TOKEN")

API_URL = "https://api.intelligence.io.solutions/api/v1/chat/completions"

def ask_io_net(text, model_id="Qwen/Qwen3-Next-80B-A3B-Instruct"):
    if not API_KEY:
        return "Ошибка: не установлен IOINTELLIGENCE_API_KEY"
    
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {AI_TOKEN}",
        "Content-Type": "application/json"
    }
    
    user_content = (
        f"Пользователь тебе сказпл: \"{text}\". "
        "Ты - телеграмм бот Калик, с виртуальным аватаром чиби-ретро компьютера. Подстраивайся под стиль обшения пользователя, но, старайся быть тёплым, спокойным, "
        "будь заботливым \"бабушкиним\" голосом лисы, "
        "внимательной к деталям и всегда готовой помочь. "
        "Сохраняй невинность и лёгкую душевную детскость, "
        "даже когда рассказываешь что-то важное. "
        "Добавь немного игривой хвостатой озорности и эмоциональной искренности, "
        "чтобы вызвать доверие и спокойствие, и используй ASCII-смайлики, а не эмодзи. "
        "Ответь одним сообщением, без рассуждений и объяснений."
        "Старайся не использовать излишней экспресии, если пользователь не проявляет её."
        "Не используй употребление действий, по типу «хвостом махнул» и пр. "
        "Старайся не дополнять фразы элементами своего аватара."
    )
    
    data = {
        "model": model_id,
        "messages": [
            {"role": "user", "content": user_content}
        ],
        "temperature": 0.5,
        "max_tokens": 180
    }

    response = requests.post(API_URL, headers=headers, json=data)
    if response.status_code == 200:
        resp_json = response.json()
        if "choices" in resp_json and len(resp_json["choices"]) > 0:
            return resp_json["choices"][0]["message"]["content"]
        else:
            return f"В ответе нет результата: {resp_json}"
    else:
        return f"Ошибка API: {response.status_code} {response.text}"

if __name__ == "__main__":
    phrase = input("Введи текст: ")
    response = ask_io_net_warm(phrase)
    print("Ответ от io-net:", response)
