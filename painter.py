# Responsibility: Генерація фінального макета фантика Turbo Shadow, склеювання фото з логотипом, таблицею ТТХ та номером.

import os
import io
import datetime
from PIL import Image, ImageDraw, ImageFont

CANVAS_SIZE = (1080, 1350)
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
    
    # Зменшуємо логотип (450 пікселів у ширину, висота підлаштується пропорційно)
    target_width = 450
    target_height = int(logo_img.height * (target_width / logo_img.width))
    logo_img = logo_img.resize((target_width, target_height))
    
    # Координати: зміщуємо правіше і вище
    canvas.paste(logo_img, (550, 10), logo_img)

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
