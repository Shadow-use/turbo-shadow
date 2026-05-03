# Responsibility: Логіка ШІ. Brainstorm (Gemini 2.5) + Visualization (Imagen 4.0).
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
    """Етап 1: Генерація тексту через Gemini у JSON-режимі."""
    excluded = ", ".join([item['model'] for item in history[-30:]]) 
    holiday_addon = get_holiday_addon()
    holiday_text = f" ОБОВ'ЯЗКОВО додай елементи стилю: {holiday_addon}." if holiday_addon else ""
    
    prompt = (
        f"Ти — авто-експерт Turbo Shadow. Твоя відповідь має бути строго в форматі JSON.\n"
        f"Поля: model (до 30 симв), specs (engine, hp, top_speed), image_prompt (детальний опис для фото).\n"
        f"Тема серії: {theme_data['series']}. {theme_data['ai_instruction']}\n"
        f"НЕ ОБИРАЙ: [{excluded}]. Вигадай щось нове та круте.{holiday_text}"
    )

    # Використовуємо JSON-режим, як у твоєму прикладі
    response = client.models.generate_content(
        model='gemini-2.5-flash', 
        config=types.GenerateContentConfig(
            response_mime_type='application/json',
            temperature=0.8
        ),
        contents=prompt
    )
    
    # Витягуємо чистий об'єкт через .text або .parsed
    try:
        return json.loads(response.text)
    except:
        # Fallback якщо модель повернула текст з markdown-обгорткою
        clean_json = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(clean_json)

def generate_image(image_prompt):
    """Етап 2: Генерація зображення через Imagen 4.0."""
    full_prompt = f"{image_prompt}, high resolution car photography, professional lighting, 8k, photorealistic"
    
    print(f"Запит до Imagen 4.0 (Model: imagen-4.0-generate-001)...")
    
    # Використовуємо спеціалізований метод generate_images
    response_img = client.models.generate_images(
        model="imagen-4.0-generate-001",
        prompt=full_prompt,
        config=types.GenerateImagesConfig(
            number_of_images=1,
            aspect_ratio="3:2", # Це дасть нам ідеальний формат під фантик
            output_mime_type="image/png",
            # Додаємо безпеку, щоб не блокувало "кіберпанк"
            safety_filter_level="BLOCK_ONLY_HIGH" 
        )
    )
    
    # Отримуємо сирі байти для Pillow
    try:
        return response_img.generated_images[0].image_bytes
    except Exception as e:
        print(f"Критична помилка Imagen: {e}")
        # Якщо 4.0 недоступна, пробуємо Imagen 3.0 (авто-відкат)
        print("Fallback: Спроба через Imagen 3.0...")
        resp_fallback = client.models.generate_images(
            model="imagen-3.0-generate-001",
            prompt=full_prompt,
            config=types.GenerateImagesConfig(number_of_images=1, aspect_ratio="3:2")
        )
        return resp_fallback.generated_images[0].image_bytes
