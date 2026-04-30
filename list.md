
### 📂 FILE: ./main.py
```
#// Responsibility: Головний керуючий скрипт. Збирає дані, запускає малювання та відправку в Telegram.

import os
import storage
import brain
import painter
import requests
import json

def send_to_tg(image_bytes, car_data):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    caption = f"🔥 *TURBO SHADOW #{car_data['id']:03}*\n\n" \
              f"🚗 *Модель:* {car_data['model']}\n" \
              f"📦 *Серія:* {car_data['series']}"
              
    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    files = {"photo": ("card.png", image_bytes, "image/png")}
    data = {"chat_id": chat_id, "caption": caption, "parse_mode": "Markdown"}
    
    requests.post(url, files=files, data=data)

def main():
    # 1. Завантажуємо налаштування та історію
    history = storage.load_history()
    theme_file = storage.get_today_file()
    
    with open(theme_file, 'r', encoding='utf-8') as f:
        theme_data = json.load(f)
        
    # 2. Генеруємо тачку (Brainstorm)
    car_data = brain.get_car_brainstorm(theme_data, history)
    car_data['series'] = theme_data['series']
    
    # 3. Зберігаємо в історію (отримуємо ID)
    new_id = storage.save_to_history(car_data)
    car_data['id'] = new_id
    
    # 4. Генеруємо фото та малюємо фантик
    img_bytes = brain.generate_image(car_data['image_prompt'])
    final_card = painter.generate_card(car_data, img_bytes)
    
    # 5. Публікація
    send_to_tg(final_card, car_data)
    print(f"Успішно опубліковано фантик №{new_id}")

if __name__ == "__main__":
    main()
```

### 📂 FILE: ./brain.py
```
# Responsibility: Логіка ШІ. Вибір авто (GitHub Models) та генерація фото (Pollinations.ai через офіційний API).

import os
import requests
import json
import urllib.parse
import time

def get_car_brainstorm(theme_data, history):
    """Вибирає нову машину за допомогою gpt-4o-mini."""
    token = os.getenv("GH_MODELS_TOKEN")
    endpoint = "https://models.inference.ai.azure.com/chat/completions"
    
    excluded = ", ".join([item['model'] for item in history[-30:]]) 
    
    system_msg = (
        "Ти — авто-експерт Turbo Shadow. Твоя відповідь має бути строго в форматі JSON. "
        "Поля: model (до 30 симв), specs (engine, hp, top_speed), image_prompt (детальний опис для фото)."
    )
    
    user_msg = (
        f"Тема серії: {theme_data['series']}. {theme_data['ai_instruction']}\n"
        f"НЕ ОБИРАЙ: [{excluded}]. Вигадай щось нове та круте."
    )

    headers = {
        "Authorization": f"Bearer {token}", 
        "Content-Type": "application/json"
    }
    
    response = requests.post(endpoint, headers=headers, json={
        "messages": [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg}
        ],
        "model": "gpt-4o-mini",
        "temperature": 0.8
    })
    
    if response.status_code != 200:
        raise Exception(f"Помилка текстового API: {response.text}")

    content = response.json()['choices'][0]['message']['content']
    clean_json = content.replace('```json', '').replace('```', '').strip()
    return json.loads(clean_json)

def generate_image(image_prompt):
    """Генерує зображення через Pollinations.ai з використанням офіційного ключа."""
    api_key = os.getenv("POLLINATIONS_API_KEY")
    if not api_key:
        raise Exception("Не знайдено POLLINATIONS_API_KEY! Додай його в Secrets.")

    full_prompt = f"{image_prompt}, high resolution car photography, professional lighting, 8k"
    encoded_prompt = urllib.parse.quote(full_prompt)
    endpoint = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true"
    
    # Головна магія: передаємо твій ключ, щоб сервер знав, що ти не анонімний спамер
    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    print("Запит до Pollinations.ai (через API-ключ)...")
    
    for attempt in range(3):
        response = requests.get(endpoint, headers=headers)
        
        if response.status_code == 200:
            return response.content
        else:
            print(f"Сервер зайнятий або помилка {response.status_code}. Чекаємо 5 секунд...")
            time.sleep(5)
            
    raise Exception("Не вдалося отримати картинку. Можливо, закінчився денний ліміт (Pollen).")
```

### 📂 FILE: ./painter.py
```
# Responsibility: Генерація фінального макета фантика Turbo Shadow, склеювання фото з логотипом, таблицею ТТХ та номером.

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
        canvas.paste((30, 30, 30, 255), (0, 0, 1080, 1350))

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
    """Додає нове авто в історію та присвоює йому порядковий номер."""
    history = load_history()
    
    # Визначаємо новий ID (номер фантика)
    new_id = len(history) + 1
    car_data['id'] = new_id
    car_data['date'] = datetime.datetime.now().strftime('%Y-%m-%d')
    
    history.append(car_data)
    
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
    
    return new_id

def is_duplicate(model_name):
    """Перевіряє, чи була така машина раніше."""
    history = load_history()
    return any(item['model'].lower() == model_name.lower() for item in history)
```
