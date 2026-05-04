# Responsibility: Логіка ШІ (PAID PLAN). Brainstorm (Gemini 2.5) + Visualization (Imagen 3.0).
import os
import json
import datetime
from google import genai
from google.genai import types

# Ініціалізація клієнта нового покоління Google GenAI
# Вказуємо v1alpha для доступу до моделей Imagen 3
client = genai.Client(
    api_key=os.getenv("GOOGLE_AI_KEY"),
    http_options={'api_version': 'v1alpha'}
)

def get_holiday_addon():
    """Зчитує святкові промпти, якщо сьогодні особливий день."""
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
    """
    Етап 1: Вибір автомобіля. 
    Використовуємо Gemini 2.5 Flash у режимі JSON для ідеальної структури.
    """
    # Складаємо список останніх моделей, щоб не повторюватися
    excluded = ", ".join([item['model'] for item in history[-30:]]) 
    
    holiday_addon = get_holiday_addon()
    holiday_text = f" ОБОВ'ЯЗКОВО додай елементи стилю: {holiday_addon}." if holiday_addon else ""
    
    prompt = (
        f"Ти — авто-експерт Turbo Shadow. Твоя відповідь має бути строго в форматі JSON.\n"
        f"Поля: model (до 30 симв), specs (engine, hp, top_speed), image_prompt (детальний опис для фото).\n"
        f"Тема серії: {theme_data['series']}. {theme_data['ai_instruction']}\n"
        f"НЕ ОБИРАЙ: [{excluded}]. Вигадай щось нове та круте.{holiday_text}"
    )

    # Запит до текстової моделі
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
    """
    Етап 2: Генерація зображення.
    Використовуємо Imagen 3.0 (Paid Tier), як вказано в акаунті.
    """
    # Додаємо стилістичні підсилювачі для фотореалізму
    full_prompt = f"{image_prompt}, high resolution photography, car magazine style, 8k, photorealistic, cinematic lighting"
    
    print(f"Запит до Imagen 3.0 (Model: imagen-3.0-generate-001)...")
    
    # Використовуємо спеціалізований метод generate_images для картинок
    response_img = client.models.generate_images(
        model="imagen-3.0-generate-001",
        prompt=full_prompt,
        config=types.GenerateImagesConfig(
            number_of_images=1,
            aspect_ratio="4:3",  # Один із 5 дозволених форматів
            output_mime_type="image/png",
            # Налаштування безпеки, обов'язкове для Imagen
            safety_filter_level="BLOCK_LOW_AND_ABOVE" 
        )
    )
    
    # Повертаємо чисті байти зображення для обробки в painter.py
    try:
        image_bytes = response_img.generated_images[0].image.image_bytes
        return image_bytes
    except Exception as e:
        print(f"Помилка при отриманні байтів Imagen 3.0: {e}")
        raise Exception("Google API не повернув дані зображення. Перевірте статус оплати.")
