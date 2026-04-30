#// Responsibility: Керування базою даних використаних авто та зчитування налаштувань дня.
import json
import os
import datetime

HISTORY_FILE = "used_cars.json"

def get_today_file():
    """Визначає, який файл промпту зчитувати сьогодні."""
    days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    day_name = datetime.datetime.now().strftime('%A').lower()
    return f"prompts/{day_name}.json"

def load_history():
    """Завантажує історію з файлу."""
    if not os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'w') as f:
            json.dump([], f)
        return []
    with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_to_history(car_data):
    """Додає нове авто в історію (ID вже згенеровано в main.py)."""
    history = load_history()
    
    car_data['date'] = datetime.datetime.now().strftime('%Y-%m-%d')
    history.append(car_data)
    
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
    
    return car_data['id']

def is_duplicate(model_name):
    """Перевіряє, чи була така машина раніше."""
    history = load_history()
    return any(item['model'].lower() == model_name.lower() for item in history)
