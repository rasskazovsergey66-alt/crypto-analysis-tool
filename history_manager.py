import json
import os
from datetime import datetime

HISTORY_FILE = "history/trades_history.json"

def load_history():
    """Загружает историю сделок из JSON-файла. Если файл пуст или повреждён, возвращает []."""
    if not os.path.exists(HISTORY_FILE):
        # Если файла нет, создаём папку и пустой файл
        os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
        save_history([])   # создаст файл с []
        return []
    
    with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
        content = f.read().strip()
        if not content:
            # Файл пуст – записываем []
            save_history([])
            return []
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # Файл повреждён – пересоздаём
            print("⚠️ Файл истории повреждён, создаём новый.")
            save_history([])
            return []

def save_history(history):
    """Сохраняет историю в JSON-файл."""
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

def save_trade(trade_data):
    """Добавляет новую сделку в историю."""
    history = load_history()
    trade_data['timestamp'] = datetime.now().isoformat()
    history.append(trade_data)
    save_history(history)