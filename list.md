
### 📂 FILE: ./brain.py
```
# Responsibility: Логіка ШІ (PAID PLAN). Діагностика та генерація.
import os
import json
import datetime
from google import genai
from google.genai import types

# Підстраховка: шукаємо ключ під різними можливими назвами у GitHub Secrets
api_key = os.getenv("GOOGLE_AI_KEY") or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

# Ініціалізація клієнта. Використовуємо v1alpha, де зазвичай знаходяться нові моделі Imagen.
client = genai.Client(
    api_key=api_key,
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
        f"Поля: 'model', 'specs' (словник, ОБОВ'ЯЗКОВО з ключами: 'hp', 'engine', '0_100', 'top_speed'), 'image_prompt'.\n"
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
    Етап 2: Генерація картинки за допомогою правильного методу для моделі image.
    """
    full_prompt = f"{image_prompt}, photorealistic, 8k, cinematic lighting"
    print("🚀 Генерація картинки через gemini-2.5-flash-image...")
    
    # ПРАВИЛЬНИЙ виклик з документації Google (через generate_content)
    response = client.models.generate_content(
        model='gemini-2.5-flash-image',
        contents=full_prompt,
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE"],
            image_config=types.ImageConfig(aspect_ratio="4:3")
        )
    )
    
    # Витягуємо байти зображення з відповіді
    for part in response.candidates[0].content.parts:
        if part.inline_data:
             return part.inline_data.data
             
    raise Exception("Google API не повернув зображення у відповіді.")
```

### 📂 FILE: ./main.py
```
#// Responsibility: Головний керуючий скрипт. Збирає дані, запускає малювання та відправку в Telegram.
import os
import storage
import brain
import painter
import requests
import json

def send_to_tg(image_bytes, car_data, chat_id):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    # Використовуємо HTML для захисту від помилок із дефісами та дужками
    caption = f"🔥 <b>TURBO SHADOW #{car_data['id']:03}</b>\n\n" \
              f"🚗 <b>Модель:</b> {car_data['model']}\n" \
              f"📦 <b>Серія:</b> {car_data['series']}"
              
    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    files = {"photo": ("card.png", image_bytes, "image/png")}
    data = {"chat_id": chat_id, "caption": caption, "parse_mode": "HTML"}
    
    response = requests.post(url, files=files, data=data)
    # Якщо Телеграм повертає помилку, скрипт зупиниться і не запише авто в базу
    response.raise_for_status() 

def send_document_to_tg(image_bytes, model_name, chat_id):
    """Відправка чистого фото файлом без втрати якості."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    url = f"https://api.telegram.org/bot{token}/sendDocument"
    # Очищуємо ім'я файлу від можливих спецсимволів
    safe_name = "".join([c for c in model_name if c.isalpha() or c.isdigit() or c==' ']).rstrip()
    files = {"document": (f"{safe_name}.png", image_bytes, "image/png")}
    
    try:
        response = requests.post(url, data={"chat_id": chat_id}, files=files)
        response.raise_for_status()
        print(f"Оригінал {safe_name}.png відправлено документом.")
    except Exception as e:
        print(f"Помилка відправки документа (не критично): {e}")

def main():
    # Визначаємо режим роботи (Test або Prod)
    is_test = os.getenv("APP_MODE") == "test"
    
    if is_test:
        chat_id = os.getenv("TELEGRAM_CHAT_ID_TEST")
        print("🚀 ЗАПУСК У ТЕСТОВОМУ РЕЖИМІ")
    else:
        chat_id = os.getenv("TELEGRAM_CHAT_ID")
        
    if not chat_id:
        raise Exception("Не знайдено chat_id! Перевір змінні TELEGRAM_CHAT_ID або TELEGRAM_CHAT_ID_TEST.")

    # 1. Завантажуємо налаштування та історію
    history = storage.load_history()
    theme_file = storage.get_today_file()
    
    with open(theme_file, 'r', encoding='utf-8') as f:
        theme_data = json.load(f)
        
    # 2. Генеруємо тачку (Brainstorm)
    car_data = brain.get_car_brainstorm(theme_data, history)
    car_data['series'] = theme_data['series']
    
    # 3. Визначаємо ID (В тестовому режимі ставимо 999)
    new_id = 999 if is_test else len(history) + 1
    car_data['id'] = new_id
    
    # 4. Генеруємо фото та малюємо фантик
    img_bytes = brain.generate_image(car_data['image_prompt'])
    final_card = painter.generate_card(car_data, img_bytes)
    
    # 5. Публікація в Телеграм (спочатку фантик, потім оригінал)
    send_to_tg(final_card, car_data, chat_id)
    send_document_to_tg(img_bytes, car_data['model'], chat_id)
    
    # 6. Збереження в історію ТІЛЬКИ після успішного поста та ЯКЩО ЦЕ НЕ ТЕСТ
    if not is_test:
        storage.save_to_history(car_data)
        print(f"Успішно опубліковано фантик №{new_id}")
    else:
        print(f"Тестовий запуск завершено. Фантик №{new_id} відправлено в тест-канал. Історія не змінена.")

if __name__ == "__main__":
    main()
```

### 📂 FILE: ./storage.py
```
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
```

### 📂 FILE: ./painter.py
```
#// Responsibility: Генерація фінального макета фантика Turbo Shadow, склеювання фото з логотипом, таблицею ТТХ та номером.
import os
import io
import datetime
from PIL import Image, ImageDraw, ImageFont

CANVAS_SIZE = (1080, 1230)
IMPACT_FONT_PATH = "impact.ttf"
LOGO_PATH = "ts_logo.png"
BACKGROUNDS_DIR = "backgrounds"

def generate_card(car_data, image_bytes):
    """
    Збирає повний фантик на основі daily-фону.
    """
    canvas = Image.new("RGBA", CANVAS_SIZE, (0, 0, 0, 0))
    
    # 1. ШАР 1: Background на весь екран
    day_name = datetime.datetime.now().strftime('%A').lower()
    bg_path = f"{BACKGROUNDS_DIR}/{day_name}.png"
    if os.path.exists(bg_path):
        bg_img = Image.open(bg_path).convert("RGBA").resize(CANVAS_SIZE)
        canvas.paste(bg_img, (0, 0))
    else:
        # Fallback на темний фон, якщо файлу немає
        canvas.paste((30, 30, 30, 255), (0, 0, 1080, 1230))

    # 2. ШАР 2: Фото авто від ШІ
    car_img = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
    car_img = car_img.resize((1000, 700)) # Ресайз
    # Додамо тонкий бордюр
    ImageDraw.Draw(canvas).rectangle([38, 148, 1042, 852], outline="white", width=4)
    canvas.paste(car_img, (40, 150))

    # 3. ШАР 3: Логотип Turbo Shadow
    logo_img = Image.open(LOGO_PATH).convert("RGBA")
    
    # Зменшуємо логотип (90 пікселів у ширину, висота підлаштується пропорційно)
    target_width = 230
    target_height = int(logo_img.height * (target_width / logo_img.width))
    logo_img = logo_img.resize((target_width, target_height))
    
    # Координати: зміщуємо правіше і вище
    canvas.paste(logo_img, (30, 30), logo_img)

    # 4. ШАР 4: Текст (IMPACT) з чорною облямівкою
    font = ImageFont.truetype(IMPACT_FONT_PATH, 50)
    draw = ImageDraw.Draw(canvas)
    
    # Нумерація (Impact, Top Right)
    global_id = f"№{car_data['id']:03} | Series: {car_data['series']}"
    draw.text((1040, 90), global_id, fill="white", font=font, anchor="rm", stroke_width=3, stroke_fill="black")

    # Таблиця ТТХ (Bottom)
    y_start = 900
    specs = car_data['specs']
    draw.text((60, y_start), f"Engine: {specs['engine']}", fill="yellow", font=font, stroke_width=3, stroke_fill="black")
    draw.text((60, y_start + 70), f"Power: {specs['hp']} HP", fill="yellow", font=font, stroke_width=3, stroke_fill="black")
    draw.text((60, y_start + 140), f"Top Speed: {specs['top_speed']}", fill="yellow", font=font, stroke_width=3, stroke_fill="black")
    draw.text((60, y_start + 210), f"Car Model: {car_data['model']}", fill="white", font=font, stroke_width=3, stroke_fill="black")

    # Збереження
    img_byte_arr = io.BytesIO()
    canvas.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()
```
