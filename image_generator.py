import os
from PIL import Image, ImageDraw, ImageFont

def draw_text_centered(draw, text, box, font, fill):
    x, y, w, h = box
    # get bbox
    bbox = font.getbbox(text)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = x + (w - tw) / 2
    ty = y + (h - th) / 2 - bbox[1]
    draw.text((tx, ty), text, font=font, fill=fill)

def generate_menu_image(menu_title, date_str, menu_data, output_path):
    width, height = 1080, 1350
    bg_color = '#fdf8f5'
    img = Image.new('RGB', (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)

    # Load fonts
    font_title = ImageFont.truetype('static/fonts/Martel-Bold.ttf', 70)
    font_date = ImageFont.truetype('static/fonts/Assistant-Bold.ttf', 30)
    font_day = ImageFont.truetype('static/fonts/Assistant-Regular.ttf', 40)
    font_meal_title = ImageFont.truetype('static/fonts/Assistant-Bold.ttf', 28)
    font_meal_item = ImageFont.truetype('static/fonts/Assistant-Regular.ttf', 26)
    font_stamp = ImageFont.truetype('static/fonts/Balmy.ttf', 60)

    # Colors
    color_green = '#1b5a32'
    color_orange = '#e28b17'
    color_yellow = '#edb933'
    color_cream = '#fcf2d9'

    # Draw Header
    # Logo
    try:
        logo = Image.open('static/logo.png').convert("RGBA")
        logo.thumbnail((250, 250))
        img.paste(logo, (50, 30), logo)
    except Exception as e:
        print("Logo not found or error:", e)

    # Title
    draw.text((320, 70), "Cardápio Semanal", font=font_title, fill=color_orange)
    draw.text((330, 160), date_str.upper(), font=font_date, fill=color_green)

    # Stamp for Daniel or Integral
    if 'DANIEL' in menu_title.upper() or 'INTEGRAL' in menu_title.upper():
        stamp_text = 'DANIEL' if 'DANIEL' in menu_title.upper() else 'INTEGRAL'
        # Create transparent image for rotated text
        txt_img = Image.new('RGBA', (300, 100), (255,255,255,0))
        txt_draw = ImageDraw.Draw(txt_img)
        txt_draw.text((10, 10), stamp_text, font=font_stamp, fill=color_green)
        rotated = txt_img.rotate(15, expand=1)
        img.paste(rotated, (750, 50), rotated)

    # Grid settings
    margin_x, margin_y = 50, 260
    col_w, col_h = 310, 520
    gap_x, gap_y = 25, 25

    days = ['Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 'Sexta-feira']
    # If the text has only "Segunda-feira", etc, we must map them
    # the parser might have captured them exactly as they are.
    
    # Let's find the actual keys in menu_data
    actual_days = list(menu_data.keys())

    boxes = [
        (0, 0), (1, 0), (2, 0),
        (0, 1), (1, 1), (2, 1)
    ]

    for i, (col, row) in enumerate(boxes):
        x = margin_x + col * (col_w + gap_x)
        y = margin_y + row * (col_h + gap_y)
        
        is_yellow = (col + row) % 2 == 0
        box_bg = color_yellow if is_yellow else color_cream

        draw.rectangle([x, y, x + col_w, y + col_h], fill=box_bg)

        if i < 5:
            # It's a day
            day_key = days[i]
            # Try to match day_key loosely
            matched_key = None
            for k in actual_days:
                if k.lower().startswith(day_key.split('-')[0].lower()):
                    matched_key = k
                    break
            
            day_label = day_key.split('-')[0].upper()
            
            # Draw day title and lines
            draw.line([(x + 20, y + 30), (x + col_w - 20, y + 30)], fill=color_green, width=3)
            draw_text_centered(draw, day_label, (x, y + 40, col_w, 50), font_day, color_green)
            draw.line([(x + 20, y + 100), (x + col_w - 20, y + 100)], fill=color_green, width=3)

            current_y = y + 120
            if matched_key and matched_key in menu_data:
                day_data = menu_data[matched_key]
                for meal, items in day_data.items():
                    draw_text_centered(draw, meal, (x, current_y, col_w, 30), font_meal_title, color_green)
                    current_y += 35
                    for item in items:
                        # centered item text
                        draw_text_centered(draw, item, (x, current_y, col_w, 30), font_meal_item, color_green)
                        current_y += 30
                    current_y += 10
        else:
            # Avisos importantes
            draw.line([(x + 20, y + 30), (x + col_w - 20, y + 30)], fill=color_green, width=3)
            draw_text_centered(draw, "Avisos importantes", (x, y + 40, col_w, 50), font_meal_title, color_green)
            draw.line([(x + 20, y + 100), (x + col_w - 20, y + 100)], fill=color_green, width=3)
            
            avisos_text = (
                "O cardápio está sujeito\n"
                "a ser alterado sem\n"
                "aviso prévio, pois\n"
                "dependemos da\n"
                "entrega dos alimentos\n"
                "frescos.\n\n"
                "Os lanches da manhã e\n"
                "da tarde são o mesmo."
            )
            # draw multi-line centered
            ay = y + 130
            for line in avisos_text.split('\n'):
                draw_text_centered(draw, line, (x, ay, col_w, 30), font_meal_item, color_green)
                ay += 30

    img.save(output_path)
