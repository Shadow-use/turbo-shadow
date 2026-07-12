# Responsibility: Головний модуль генерації концептів авто та промптів через Gemini API з обробкою блокувань.
import os
import json
import datetime
from google import genai
from google.genai import types

api_key = os.getenv("GOOGLE_AI_KEY") or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

client = genai.Client(
    api_key=api_key,
    http_options={'api_version': 'v1alpha'}
)

def get_holiday_addon():
    holiday_file = "holidays.json"
    if not os.path.exists(holiday_file):
        return ""
    try:
        with open(holiday_file, "r", encoding="utf-8") as f:
            holidays = json.load(f)
        today_str = datetime.datetime.now().strftime("%m-%d")
        return holidays.get(today_str, "")
    except Exception as e:
        print(f"Помилка зчитування свят: {e}")
        return ""

def get_car_brainstorm(theme_data, history):
    excluded = ", ".join([item['model'] for item in history[-30:]]) 
    holiday_addon = get_holiday_addon()
    holiday_text = f" ОБОВ'ЯЗКОВО додай елементи стилю: {holiday_addon}." if holiday_addon else ""
    
    prompt = (
        f"Ти — авто-експерт Turbo Shadow. Відповідь строго в JSON без маркдауну.\n"
        f"Тема: {theme_data['series']}. {theme_data['ai_instruction']}\n\n"
        f"СУВОРІ ВИМОГИ ДО ПОЛІВ JSON:\n"
        f"1. 'model': Повна назва авто (наприклад, 'Toyota Supra (A80)').\n"
        f"2. 'specs': Словник з ТТХ:\n"
        f"   - 'hp': ТІЛЬКИ ЦИФРИ (наприклад, '280', '1500'). Жодних букв 'hp', 'к.с.' чи пробілів! Скрипт сам додасть 'HP'.\n"
        f"   - 'engine': Короткий опис двигуна англійською або українською. МАКСИМУМ 35 символів (наприклад, '3.0L Twin-Turbo I6' або 'Електрична трансмісія').\n"
        f"   - '0_100': Час розгону, тільки цифри та 's' (наприклад, '3.2s').\n"
        f"   - 'top_speed': Тільки цифри та одиниці виміру. МАКСИМУМ 12 символів (наприклад, '250 km/h' або '320 км/год'). ЗАБОРОНЕНО писати уточнення в дужках (limited, projected і т.д.).\n"
        f"3. 'image_prompt': Детальний промпт для генератора зображень англійською мовою. Описуй лише візуал, погоду та освітлення. НЕ ПИШИ сюди характеристики.\n\n"
        f"НЕ ОБИРАЙ: [{excluded}].{holiday_text}"
    )

    response = client.models.generate_content(
        model='gemini-2.5-flash', 
        config=types.GenerateContentConfig(
            response_mime_type='application/json',
            temperature=0.8
        ),
        contents=prompt
    )
    return json.loads(response.text)

def generate_image(image_prompt):
    full_prompt = f"{image_prompt}, photorealistic, 8k, cinematic lighting"
    print("🚀 Генерація картинки через gemini-2.5-flash-image...")
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash-image',
            contents=full_prompt,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
                image_config=types.ImageConfig(aspect_ratio="4:3")
            )
        )
        
        # Перевірка на блокування безпеки
        if response.candidates and not response.candidates[0].content:
            finish_reason = getattr(response.candidates[0], 'finish_reason', 'НЕВІДОМО')
            error_msg = f"БЛОКУВАННЯ БЕЗПЕКИ! Причина: {finish_reason}. Промпт: {full_prompt}"
            print(error_msg)
            raise Exception(error_msg)
            
        # Нормальна генерація
        if response.candidates and response.candidates[0].content:
            for part in response.candidates[0].content.parts:
                if part.inline_data:
                     return part.inline_data.data
                     
        raise Exception("Google API не повернув зображення у відповіді.")
        
    except Exception as e:
        print(f"Помилка генерації зображення: {e}")
        raise e
