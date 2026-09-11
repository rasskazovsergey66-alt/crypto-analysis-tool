import os
from dotenv import load_dotenv

# Загружаем переменные из .env (ищем в текущей папке)
load_dotenv()

# ------------------- КЛЮЧИ (загружаются из .env) -------------------
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("❌ GEMINI_API_KEY не найден в .env. Создайте файл .env и укажите его.")

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
# Токен GitHub не обязателен, но повышает лимиты. Если не указан – работаем анонимно (60 запросов/час).
if not GITHUB_TOKEN:
    print("⚠️ GITHUB_TOKEN не найден. Лимит запросов к GitHub API будет 60/час.")

# ------------------- НАСТРОЙКИ МОДЕЛЕЙ -------------------
AVAILABLE_MODELS = {
    "flash_3.8": "gemini-3.8-flash",
    "flash_3.6": "gemini-3.6-flash",
    "flash_3.5": "gemini-3.5-flash",
    "flash_2.5": "gemini-2.5-flash",
    "flash_lite": "gemini-2.5-flash-lite",
    "gemma_4_31b": "gemma-4-31b-it",
    "gemma_4_26b": "gemma-4-26b-a4b-it",
}

# Приоритетный порядок (от самой мощной к более лёгким)
PRIORITY_MODELS = ["flash_3.8", "flash_3.6", "flash_3.5", "flash_2.5", "gemma_4_31b", "flash_lite"]

# Модель по умолчанию, если не указана
DEFAULT_MODEL = "flash_3.8"

# ------------------- РЕПОЗИТОРИЙ С CSV -------------------
REPO_OWNER = "rasskazovsergey66-alt"
REPO_NAME = "crypto-screener"

# ------------------- ПУТИ К КОНТЕКСТУ (по желанию) -------------------
STRATEGY_FILE = "context/analiz_epohi_62_75_i_model_66.md"
RESUME_FILE = "context/rezume_chata_srez112.md"