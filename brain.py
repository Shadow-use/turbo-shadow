# Responsibility: Логіка ШІ. Вибір авто (Gemini 2.5 Flash) та генерація фото (Imagen 4.0).
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
    """Вибирає нову машину за допомогою Gemini 2.5 Flash."""
    excluded = ", ".join([item['model'] for item in history[-30:]]) 
    holiday_addon = get_holiday_addon()
    holiday_text = f" ОБОВ'ЯЗКОВО додай елементи стилю: {holiday_addon}." if holiday_addon else ""
    
    prompt = (
        f"Ти — авто-експерт Turbo Shadow. Твоя відповідь має бути строго в форматі JSON.\n"
        f"Поля: model (до 30 симв), specs (engine, hp, top_speed), image_prompt (детальний опис для фото).\n"
        f"Тема серії: {theme_data['series']}. {theme_data['ai_instruction']}\n"
        f"НЕ ОБИРАЙ: [{excluded}]. Вигадай щось нове та круте.{holiday_text}"
    )

    # Для тексту використовуємо generate_content
    response = client.models.generate_content(
        model='gemini-2.5-flash', 
        config=types.GenerateContentConfig(response_mime_type='application/json'),
        contents=prompt
    )
    
    return json.loads(response.text)

def generate_image(image_prompt):
    """Генерує зображення через спеціалізований метод Imagen 4.0."""
    full_prompt = f"{image_prompt}, high resolution car photography, professional lighting, 8k, photorealistic"
    
    print(f"Запит до Imagen 4.0 (Метод: generate_image)...")
    
    # ПРАВИЛЬНИЙ МЕТОД ДЛЯ КАРТИНОК:
    response = client.models.generate_image(
        model='imagen-4.0-generate-001',
        prompt=full_prompt,
        config=types.GenerateImageConfig(
            number_of_images=1,
            include_rai_reason=True,
            output_mime_type='image/png'
        )
    )
    
    # Витягуємо байти згенерованого зображення
    try:
        # У новому SDK картинка лежить у response.generated_images[0].image.image_bytes
        # або безпосередньо в inline_data залежно від версії
        image_data = response.generated_images[0].image.image_bytes
        return image_data
    except Exception as e:
        print(f"Помилка Imagen 4.0: {e}")
        # Запасний варіант для Imagen 3.0, якщо 4.0 відмовить
        print("Спроба відкату до Imagen 3.0...")
        resp_fallback = client.models.generate_image(
            model='imagen-3.0-generate-001',
            prompt=full_prompt,
            config=types.GenerateImageConfig(number_of_images=1)
        )
        return resp_fallback.generated_images[0].image.image_bytes
