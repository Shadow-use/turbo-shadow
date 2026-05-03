# // Responsibility: Логіка ШІ. Вибір авто (Gemini 3.1 Flash) та генерація фото (Imagen 4.0 Ultra).
import os
import json
import random
import datetime
import time
import google.generativeai as genai
from PIL import Image
import io

# Налаштування нового API
API_KEY = os.getenv("GOOGLE_AI_KEY")
genai.configure(api_key=API_KEY)

def get_holiday_addon():
    """Безпечно зчитує святковий промпт з файлу."""
    holiday_file = "holidays.json"
    if not os.path.exists(holiday_file):
        return ""
    try:
        with open(holiday_file, "r", encoding="utf-8") as f:
            holidays = json.load(f)
        today_str = datetime.datetime.now().strftime("%m-%d")
        return holidays.get(today_str, "")
    except Exception as e:
        print(f"Помилка зчитування {holiday_file}: {e}")
        return ""

def get_car_brainstorm(theme_data, history):
    """Вибирає нову машину за допомогою Gemini 3.1 Flash."""
    # Використовуємо одну з топових моделей твого списку
    model = genai.GenerativeModel('models/gemini-3.1-flash-preview')
    
    excluded = ", ".join([item['model'] for item in history[-30:]]) 
    holiday_addon = get_holiday_addon()
    holiday_text = f" ОБОВ'ЯЗКОВО додай елементи стилю: {holiday_addon}." if holiday_addon else ""

    system_msg = (
        "Ти — авто-експерт Turbo Shadow. Твоя відповідь має бути строго в форматі JSON. "
        "Поля: model (до 30 симв), specs (engine, hp, top_speed), image_prompt (детальний опис для фото)."
    )
    
    user_msg = (
        f"Тема серії: {theme_data['series']}. {theme_data['ai_instruction']}\n"
        f"НЕ ОБИРАЙ: [{excluded}]. Вигадай щось нове та круте.{holiday_text}"
    )

    # Виклик Gemini замість requests
    response = model.generate_content(f"{system_msg}\n\n{user_msg}")
    
    # Очищення відповіді від маркдауну ```json ... ```
    content = response.text
    clean_json = content.replace('```json', '').replace('```', '').strip()
    return json.loads(clean_json)

def generate_image(image_prompt):
    """Генерує зображення через Imagen 4.0 Ultra."""
    # Використовуємо найпотужнішу модель для графіки
    image_model = genai.ImageGenerationModel("models/imagen-4.0-ultra-generate-001")
    
    full_prompt = f"{image_prompt}, high resolution car photography, professional lighting, 8k, highly detailed"
    
    print(f"Запит до Imagen 4.0 Ultra...")
    
    # Imagen повертає об'єкт зображення, який ми конвертуємо в байти для сумісності з твоїм main.py
    for attempt in range(3):
        try:
            result = image_model.generate_images(
                prompt=full_prompt,
                number_of_images=1,
                aspect_ratio="16:9", # Це дасть приблизно 1500+ по ширині
                safety_filter_level="block_few"
            )
            # Конвертуємо зображення в байти (щоб main.py не помітив підміни)
            img_byte_arr = io.BytesIO()
            result[0]._image_bytes # Google SDK зберігає байти тут
            return result[0]._image_bytes
        except Exception as e:
            print(f"Спроба {attempt+1} не вдалася: {e}. Чекаємо...")
            time.sleep(5)
            
    raise Exception("Не вдалося отримати картинку від Imagen 4.0 Ultra.")
