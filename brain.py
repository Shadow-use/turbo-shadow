# Responsibility: Логіка ШІ. Вибір авто (Gemini 3 Flash) та генерація фото (Imagen 3).
import os
import json
import datetime
from google import genai
from google.genai import types

# Ініціалізація клієнта нового покоління Google GenAI
client = genai.Client(api_key=os.getenv("GOOGLE_AI_KEY"))

def get_holiday_addon():
    """Безпечно зчитує святковий промпт з файлу holidays.json."""
    holiday_file = "holidays.json"
    if not os.path.exists(holiday_file):
        return ""
    try:
        with open(holiday_file, "r", encoding="utf-8") as f:
            holidays = json.load(f)
        # Отримуємо сьогоднішню дату у форматі ММ-ДД
        today_str = datetime.datetime.now().strftime("%m-%d")
        return holidays.get(today_str, "")
    except Exception as e:
        print(f"Помилка зчитування {holiday_file}: {e}")
        return ""

def get_car_brainstorm(theme_data, history):
    """Вибирає нову машину за допомогою Gemini 3 Flash."""
    # Отримуємо список останніх 30 моделей, щоб не повторюватись
    excluded = ", ".join([item['model'] for item in history[-30:]]) 
    
    # Перевірка на свята
    holiday_addon = get_holiday_addon()
    holiday_text = f" ОБОВ'ЯЗКОВО додай елементи стилю: {holiday_addon}." if holiday_addon else ""
    
    prompt = (
        f"Ти — авто-експерт Turbo Shadow. Твоя відповідь має бути строго в форматі JSON.\n"
        f"Поля: model (до 30 симв), specs (engine, hp, top_speed), image_prompt (детальний опис для фото).\n"
        f"Тема серії: {theme_data['series']}. {theme_data['ai_instruction']}\n"
        f"НЕ ОБИРАЙ: [{excluded}]. Вигадай щось нове та круте.{holiday_text}"
    )

    # Використовуємо актуальну стабільну модель Gemini 3 Flash з вимогою JSON-відповіді
    response = client.models.generate_content(
        model='gemini-3-flash', 
        config=types.GenerateContentConfig(response_mime_type='application/json'),
        contents=prompt
    )
    
    # Парсимо отриманий JSON
    try:
        return json.loads(response.text)
    except Exception as e:
        print(f"Помилка парсингу відповіді ШІ: {e}")
        raise

def generate_image(image_prompt):
    """Генерує зображення через Imagen 3 (1500x1050)."""
    # Додаємо технічні параметри для кращої якості
    full_prompt = f"{image_prompt}, high resolution car photography, professional lighting, 8k, photorealistic"
    
    print(f"Запит до Imagen (Google GenAI)...")
    
    # Imagen викликається через той самий клієнт зі специфічним конфігом
    response = client.models.generate_content(
        model='imagen-3',
        contents=full_prompt,
        config=types.GenerateContentConfig(
            # Вказуємо формат повернення - байти картинки
            response_mime_type='image/png'
        )
    )
    
    # Повертаємо байти зображення безпосередньо для подальшої обробки в painter.py
    try:
        return response.candidates[0].content.parts[0].inline_data.data
    except Exception as e:
        print(f"Критична помилка Imagen: {e}")
        raise Exception("Не вдалося отримати дані зображення від Google API.")
