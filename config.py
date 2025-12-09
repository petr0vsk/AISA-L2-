import os
from dotenv import load_dotenv

load_dotenv()

def get_openrouter_api_key() -> str:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY не найден. Установите его в .env или переменные окружения.")
    return api_key

DEFAULT_SYSTEM_PROMPT = (
    "Отвечайте сухим официальным языком. "
    "Если нет прямых инструкций – отвечайте кратко: два-три абзаца."
)
