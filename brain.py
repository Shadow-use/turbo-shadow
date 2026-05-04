# Responsibility: Логіка ШІ (PAID PLAN). Діагностика та генерація.
import os
import json
import datetime
from google import genai
from google.genai import types

# Ініціалізація клієнта. Використовуємо v1alpha, де зазвичай знаходяться нові моделі Imagen.
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
    Етап 1: Вибір автомобіля через Gemini 2.5 Flash.
    """
    excluded = ", ".join([item['model'] for item in history[-30:]]) 
    holiday_addon = get_holiday_addon()
    holiday_text = f" ОБОВ'ЯЗКОВО додай елементи стилю: {holiday_addon}." if holiday_addon else ""
    
    prompt = (
        f"Ти — авто-експерт Turbo Shadow. Відповідь строго в JSON.\n"
        f"Поля: model, specs, image_prompt.\n"
        f"Тема: {theme_data['series']}. {theme_data['ai_instruction']}\n"
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
    """
    Етап 2: Детекція доступних моделей та спроба генерації.
    """
    print("\n🔍 === ДЕТЕКТОР МОДЕЛЕЙ GOOGLE AI === 🔍")
    found_models = []
    try:
        # Запитуємо у сервера список усіх моделей, доступних цьому ключу
        for m in client.models.list():
            # Нам цікаві моделі, що вміють малювати (метод generateImages або imagen у назві)
            if 'image' in m.name.lower() or 'imagen' in m.name.lower():
                status = "✅ ДОСТУПНА"
                found_models.append(m.name)
                print(f"{status}: {m.name}")
                print(f"      Методи: {m.supported_generation_methods}")
    except Exception as e:
        print(f"❌ Не вдалося отримати список моделей: {e}")

    print("======================================\n")

    if not found_models:
        print("⚠ УВАГА: Список моделей порожній. Перевірте, чи активовано Imagen у Google Cloud Console.")
        raise Exception("Imagen не знайдено для цього API-ключа.")

    # Спроба генерації через першу знайдену модель зі списку
    target_model = found_models[0]
    print(f"🚀 Спроба генерації через: {target_model}...")
    
    full_prompt = f"{image_prompt}, photorealistic, 8k, cinematic lighting"
    
    try:
        response_img = client.models.generate_images(
            model=target_model,
            prompt=full_prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio="4:3",
                output_mime_type="image/png",
                safety_filter_level="BLOCK_LOW_AND_ABOVE"
            )
        )
        return response_img.generated_images[0].image.image_bytes
    except Exception as e:
        print(f"❌ Помилка генерації через {target_model}: {e}")
        # Зупиняємо процес, щоб ми могли прочитати лог списку моделей
        raise Exception("Аналіз завершено. Дивіться список моделей вище.")
