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
        f"Ти — авто-експерт Turbo Shadow. Відповідь строго в JSON.\n"
        f"Поля: 'model', 'specs' (словник з ключами: 'hp', 'engine', '0_100', 'top_speed'), 'image_prompt'.\n"
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
    full_prompt = f"{image_prompt}, photorealistic, 8k, cinematic lighting"
    print("🚀 Генерація картинки через gemini-2.5-flash-image...")
    
    response = client.models.generate_content(
        model='gemini-2.5-flash-image',
        contents=full_prompt,
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE"],
            image_config=types.ImageConfig(aspect_ratio="4:3")
        )
    )
    
    for part in response.candidates[0].content.parts:
        if part.inline_data:
             return part.inline_data.data
             
    raise Exception("Google API не повернув зображення у відповіді.")
