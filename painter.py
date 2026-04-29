// Responsibility: Генерація фінального макета фантика Turbo Shadow, склеювання фото з логотипом, таблицею ТТХ та номером.

import os
import io
import datetime
import requests
from PIL import Image, ImageDraw, ImageFont

CANVAS_SIZE = (1080, 1350)
IMPACT_FONT_PATH = "fonts/impact.ttf" # Завантаж шрифт у цю папку
LOGO_PATH = "ts_logo.png" # Твоє image_4.png
BACKGROUNDS_DIR = "backgrounds" # Створи папку з monday.png...

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

    # 3. ШАР 3: Логотип Turbo Shadow (з image_4.png)
    logo_img = Image.open(LOGO_PATH).convert("RGBA")
    # Python НЕ пише текст TURBO SHADOW, лого стоїть сам по собі
    canvas.paste(logo_img, (340, 20), logo_img) # Центруємо, logo_img як маска

    # 4. ШАР 4: Текст (IMPACT)
    font = ImageFont.truetype(IMPACT_FONT_PATH, 50)
    draw = ImageDraw.Draw(canvas)
    
    # Нумерація (Impact, Top Right)
    global_id = f"№{car_data['id']:03} | Series: {car_data['series']}"
    draw.text((1040, 90), global_id, fill="white", font=font, anchor="rm")

    # Таблиця ТТХ (Bottom)
    y_start = 900
    specs = car_data['specs']
    draw.text((60, y_start), f"Engine: {specs['engine']}", fill="yellow", font=font)
    draw.text((60, y_start + 70), f"Power: {specs['hp']} HP", fill="yellow", font=font)
    draw.text((60, y_start + 140), f"Top Speed: {specs['top_speed']} km/h", fill="yellow", font=font)
    draw.text((60, y_start + 210), f"Car Model: {car_data['model']}", fill="white", font=font)

    # Збереження
    img_byte_arr = io.BytesIO()
    canvas.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()
