import os
from config import STRATEGY_FILE, RESUME_FILE

def load_context_from_md(filepath):
    """Читает MD-файл, если он есть. Иначе возвращает пустую строку."""
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        print(f"⚠️ Файл контекста не найден: {filepath}")
        return ""

def get_strategy_context():
    """Возвращает словарь с ключами 'strategy' и 'resume', даже если файлов нет."""
    return {
        "strategy": load_context_from_md(STRATEGY_FILE),
        "resume": load_context_from_md(RESUME_FILE)
    }