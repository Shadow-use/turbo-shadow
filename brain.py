# Responsibility: Логіка ШІ. Вибір авто (Gemini 2.5 Flash) та генерація фото (Imagen 4.0 Ultra).
import os
import json
import datetime
from google import genai
from google.genai import types

# Ініціалізація клієнта
client = genai.Client(api_key=os.getenv("GOOGLE_AI_KEY"))

def get_holiday_addon():
    holiday_file = "holidays.json"
    if not os.path.exists(holiday_file): return ""
    try:
        with open(holiday_file, "r", encoding="utf-8") as f:
            holidays = json.load(f)
        today_str = datetime.datetime.now().strftime("%m-%d")
        return holidays.get(today_str, "")
    except: return ""

def get_car_brainstorm(theme_data, history):
    """Вибирає нову машину за допомогою Gemini 2.5 Flash (найстабільніша у списку)."""
    excluded = ", ".join([item['model'] for item in history[-30:]]) 
    holiday_addon = get_holiday_addon()
    holiday_text = f" ОБОВ'ЯЗКОВО додай елементи стилю: {holiday_addon}." if holiday_addon else ""
    
    prompt = (
        f"Ти — авто-експерт Turbo Shadow. Твоя відповідь має бути строго в форматі JSON.\n"
        f"Поля: model (до 30 симв), specs (engine, hp, top_speed), image_prompt (детальний опис для фото).\n"
        f"Тема серії: {theme_data['series']}. {theme_data['ai_instruction']}\n"
        f"НЕ ОБИРАЙ: [{excluded}]. Вигадай щось нове та круте.{holiday_text}"
    )

    # Використовуємо точну назву з твого списку
    response = client.models.generate_content(
        model='gemini-2.5-flash', 
        config=types.GenerateContentConfig(response_mime_type='application/json'),
        contents=prompt
    )
    
    return json.loads(response.text)

def generate_image(image_prompt):
    """Генерує зображення через Imagen 4.0 (найпотужніша у списку)."""
    full_prompt = f"{image_prompt}, high resolution car photography, professional lighting, 8k, photorealistic"
    
    print(f"Запит до Imagen 4.0 (Google GenAI)...")
    
    # Використовуємо точну назву моделі з твого curl-запиту
    response = client.models.generate_content(
        model='imagen-4.0-generate-001',
        contents=full_prompt,
        config=types.GenerateContentConfig(response_mime_type='image/png')
    )
    
    try:
        return response.candidates[0].content.parts[0].inline_data.data
    except Exception as e:
        print(f"Помилка Imagen 4.0: {e}")
        # Спроба використати Imagen 3 як запасний варіант, якщо 4.0 має обмеження квоти
        return client.models.generate_content(
            model='imagen-3.0-generate-001', # Якщо вона є у списку (зазвичай є)
            contents=full_prompt,
            config=types.GenerateContentConfig(response_mime_type='image/png')
        ).candidates[0].content.parts[0].inline_data.data
