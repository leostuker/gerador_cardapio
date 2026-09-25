import os
from PIL import Image, ImageDraw, ImageFont

FONTS_DIR = 'static/fonts'

def get_font(name, size):
    """Load font by name. Maps logical names to actual font files."""
    font_map = {
        'title': 'Martel-Bold.ttf',
        'assistant': 'assistant-latin-500-normal.ttf',
        'assistant_bold': 'Assistant-Bold.ttf',
        'stamp': 'Balmy Beta.ttf',
    }
    path = os.path.join(FONTS_DIR, font_map.get(name, name))
    return ImageFont.truetype(path, size)


def draw_text_centered(draw, text, box, font, fill):
    """Draw text centered within a box (x, y, w, h). y is top of text."""
    x, y, w, h = box
    bbox = font.getbbox(text)
    tw = bbox[2] - bbox[0]
    tx = x + (w - tw) / 2
    draw.text((tx, y), text, font=font, fill=fill)


def wrap_text(text, font, max_width):
    """Break text into lines that fit within max_width pixels."""
    words = text.split()
    if not words:
        return ['']
    lines = []
    current_line = []
    for word in words:
        test_line = ' '.join(current_line + [word])
        bbox = font.getbbox(test_line)
        w = bbox[2] - bbox[0]
        if w <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
    if current_line:
        lines.append(' '.join(current_line))
    return lines if lines else ['']


def generate_menu_image(menu_title, date_str, menu_data, output_path):
    # === Canvas ===
    width, height = 1080, 1350
    bg_color = '#fdf8f0'
    img = Image.new('RGB', (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)

    # === Load fonts ===
    font_title = get_font('title', 60)
    font_date = get_font('assistant', 24)
    font_day_header = get_font('assistant', 34)
    font_meal_label = get_font('assistant_bold', 22)
    font_meal_item = get_font('assistant', 20)
    font_stamp = get_font('stamp', 44)
    font_avisos_title = get_font('assistant_bold', 24)
    font_avisos_text = get_font('assistant', 20)

    # === Colors ===
    color_green = '#1b5a32'
    color_orange = '#e28b17'
    color_yellow = '#f0b731'
    color_cream = '#faf0d8'
    color_stamp_green = '#2d6b3f'

    # =========================================================
    # HEADER AREA (top ~210px)
    # =========================================================

    # Logo (small, top-left)
    try:
        logo = Image.open('static/logo.png').convert("RGBA")
        logo.thumbnail((110, 110))
        img.paste(logo, (35, 25), logo)
    except Exception as e:
        print("Logo not found or error:", e)

    # Title "Cardápio Semanal" (Centered)
    title_text = "Cardápio Semanal"
    title_bbox = font_title.getbbox(title_text)
    title_w = title_bbox[2] - title_bbox[0]
    title_x = (width - title_w) / 2
    draw.text((title_x, 35), title_text, font=font_title, fill=color_orange)

    # Date string below title (Centered)
    date_text = date_str.upper()
    date_bbox = font_date.getbbox(date_text)
    date_w = date_bbox[2] - date_bbox[0]
    date_x = (width - date_w) / 2
    draw.text((date_x, 110), date_text, font=font_date, fill=color_green)

    # Stamp (tag style) — only for Daniel or Integral
    is_daniel = 'DANIEL' in menu_title.upper()
    is_integral = 'INTEGRAL' in menu_title.upper()

    if is_daniel or is_integral:
        stamp_text = 'DANIEL' if is_daniel else 'INTEGRAL'
        txt_img = Image.new('RGBA', (350, 80), (255, 255, 255, 0))
        txt_draw = ImageDraw.Draw(txt_img)
        txt_draw.text((5, 5), stamp_text, font=font_stamp, fill=color_stamp_green)
        rotated = txt_img.rotate(-15, expand=True, resample=Image.BICUBIC)
        # Position: top-right corner, between title and date, clear of everything
        stamp_x = width - rotated.width - 80
        stamp_y = 55
        img.paste(rotated, (stamp_x, stamp_y), rotated)

    # =========================================================
    # GRID AREA — NO GAPS between columns or rows
    # =========================================================
    grid_top = 200
    grid_left = 35
    grid_right = width - 35
    grid_total_w = grid_right - grid_left
    num_cols = 3
    col_w = grid_total_w / num_cols
    row_gap = 0
    total_grid_h = height - grid_top - 30
    row_h = total_grid_h / 2

    days = ['Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 'Sexta-feira']
    actual_days = list(menu_data.keys())

    grid_positions = [
        (0, 0), (1, 0), (2, 0),
        (0, 1), (1, 1), (2, 1),
    ]

    def get_box_color(col, row):
        if (col + row) % 2 == 0:
            return color_yellow
        return color_cream

    text_padding = 18

    for i, (col, row) in enumerate(grid_positions):
        # Columns and rows touching perfectly
        bx = grid_left + int(col * col_w)
        bx_next = grid_left + int((col + 1) * col_w)
        bw = bx_next - bx
        
        by = grid_top + int(row * row_h)
        by_next = grid_top + int((row + 1) * row_h)
        bh = by_next - by

        box_bg = get_box_color(col, row)
        draw.rectangle([bx, by, bx + bw, by + bh], fill=box_bg)

        inner_left = bx + text_padding
        inner_right = bx + bw - text_padding
        inner_w = inner_right - inner_left

        if i < 5:
            # === DAY COLUMN ===
            day_key = days[i]
            matched_key = None
            for k in actual_days:
                day_prefix = day_key.split('-')[0].lower()
                if k.lower().startswith(day_prefix):
                    matched_key = k
                    break

            day_label = day_key.split('-')[0].upper()

            # Decorative lines + day name
            line_y_top = by + 22
            draw.line([(inner_left, line_y_top), (inner_right, line_y_top)],
                      fill=color_green, width=3)

            day_label_y = line_y_top + 8
            draw_text_centered(draw, day_label, (bx, day_label_y, bw, 40),
                               font_day_header, color_green)

            line_y_bot = day_label_y + 44
            draw.line([(inner_left, line_y_bot), (inner_right, line_y_bot)],
                      fill=color_green, width=3)

            # Meal content
            content_y = line_y_bot + 12
            max_y = by + bh - 8

            if matched_key and matched_key in menu_data:
                day_data = menu_data[matched_key]
                for meal_name, items in day_data.items():
                    if content_y >= max_y:
                        break
                    draw_text_centered(draw, meal_name, (bx, content_y, bw, 26),
                                       font_meal_label, color_green)
                    content_y += 28

                    for item in items:
                        if content_y >= max_y:
                            break
                        wrapped = wrap_text(item, font_meal_item, inner_w)
                        for line in wrapped:
                            if content_y >= max_y:
                                break
                            draw_text_centered(draw, line,
                                               (bx, content_y, bw, 22),
                                               font_meal_item, color_green)
                            content_y += 24
                    content_y += 6

        else:
            # === AVISOS IMPORTANTES ===
            # No lines at the top or bottom
            title_y = by + 30
            draw_text_centered(draw, "Avisos importantes",
                               (bx, title_y, bw, 40),
                               font_avisos_title, color_green)

            avisos_lines = [
                "O cardápio está sujeito",
                "a ser alterado sem",
                "aviso prévio, pois",
                "dependemos da",
                "entrega dos alimentos",
                "frescos.",
                "",
                "Os lanches da manhã e",
                "da tarde são o mesmo",
            ]
            ay = title_y + 44 + 18
            for line in avisos_lines:
                if line == "":
                    ay += 14
                    continue
                draw_text_centered(draw, line, (bx, ay, bw, 22),
                                   font_avisos_text, color_green)
                ay += 26

    img.save(output_path, quality=95)
