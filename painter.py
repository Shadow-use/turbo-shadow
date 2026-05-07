import os
import io
import datetime
from PIL import Image, ImageDraw, ImageFont

CANVAS_SIZE = (1080, 1230)
IMPACT_FONT_PATH = "impact.ttf"
LOGO_PATH = "ts_logo.png"
BACKGROUNDS_DIR = "backgrounds"

def generate_card(car_data, image_bytes):
    canvas = Image.new("RGBA", CANVAS_SIZE, (0, 0, 0, 0))
    
    day_name = datetime.datetime.now().strftime('%A').lower()
    bg_path = f"{BACKGROUNDS_DIR}/{day_name}.png"
    if os.path.exists(bg_path):
        bg_img = Image.open(bg_path).convert("RGBA").resize(CANVAS_SIZE)
        canvas.paste(bg_img, (0, 0))
    else:
        canvas.paste((30, 30, 30, 255), (0, 0, 1080, 1230))

    car_img = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
    car_img = car_img.resize((1000, 700))
    ImageDraw.Draw(canvas).rectangle([38, 148, 1042, 852], outline="white", width=4)
    canvas.paste(car_img, (40, 150))

    logo_img = Image.open(LOGO_PATH).convert("RGBA")
    target_width = 230
    target_height = int(logo_img.height * (target_width / logo_img.width))
    logo_img = logo_img.resize((target_width, target_height))
    canvas.paste(logo_img, (30, 30), logo_img)

    font = ImageFont.truetype(IMPACT_FONT_PATH, 50)
    draw = ImageDraw.Draw(canvas)
    
    global_id = f"№{car_data['id']:03} | Series: {car_data['series']}"
    draw.text((1040, 90), global_id, fill="white", font=font, anchor="rm", stroke_width=3, stroke_fill="black")

    y_start = 900
    # Безпечне отримання даних через .get()
    specs = car_data.get('specs', {})
    
    draw.text((60, y_start), f"Engine: {specs.get('engine', 'N/A')}", fill="yellow", font=font, stroke_width=3, stroke_fill="black")
    draw.text((60, y_start + 70), f"Power: {specs.get('hp', 'N/A')} HP", fill="yellow", font=font, stroke_width=3, stroke_fill="black")
    draw.text((60, y_start + 140), f"Top Speed: {specs.get('top_speed', 'N/A')}", fill="yellow", font=font, stroke_width=3, stroke_fill="black")
    draw.text((60, y_start + 210), f"Car Model: {car_data.get('model', 'Unknown')}", fill="white", font=font, stroke_width=3, stroke_fill="black")

    img_byte_arr = io.BytesIO()
    canvas.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()
