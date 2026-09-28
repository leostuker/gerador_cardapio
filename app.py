import os
import random
import unicodedata
from PIL import Image, ImageDraw, ImageFont, ImageChops, ImageColor

FONTS_DIR = 'static/fonts'

# =========================================================
# CONFIGURAÇÃO DO LAYOUT (mesma proporção da imagem-objetivo)
# =========================================================
WIDTH, HEIGHT = 1236, 1600
HEADER_H = 300                 # altura da faixa branca do topo

COLOR_BG = '#fffdf6'           # fundo do cabeçalho
COLOR_GREEN = '#4a6b2c'        # textos, linhas e carimbo
COLOR_ORANGE = '#f6931d'       # título
COLOR_YELLOW = '#f2ae1c'       # caixas amarelas
COLOR_CREAM = '#fdecc8'        # caixas creme

LOGO_POS = (68, 80)            # canto superior esquerdo do logo
LOGO_MAX = (150, 150)          # tamanho máximo do logo (largura, altura)

MAX_SCALE = 1.3                # limite superior do aumento automático da fonte
MIN_SCALE = 0.5                # limite inferior (se o cardápio for enorme)
DAY_HEADER_BOLD = True         # títulos dos dias (SEGUNDA...) em negrito

ITEM_SIZE = 28                 # tamanho base da fonte dos itens
LINE_PITCH = 39                # distância entre linhas dos itens
MEAL_GAP = 18                  # espaço extra entre Lanche e Almoço
BOTTOM_PAD = 22                # folga mínima no fim da caixa
CELL_TEXT_PAD = 34             # margem lateral do texto nas caixas
CELL_LINE_PAD = 42             # margem lateral das linhas decorativas

AVISOS_LINES = [
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

_font_cache = {}


def get_font(name, size):
    """Load font by name. Maps logical names to actual font files."""
    key = (name, size)
    if key in _font_cache:
        return _font_cache[key]
    font_map = {
        'title': 'Martel-Bold.ttf',
        'assistant': 'assistant-latin-500-normal.ttf',
        'assistant_bold': 'Assistant-Bold.ttf',
        'stamp': 'Balmy Beta.ttf',
    }
    path = os.path.join(FONTS_DIR, font_map.get(name, name))
    font = ImageFont.truetype(path, size)
    _font_cache[key] = font
    return font


def font_for_width(name, text, target_w):
    """Return the font whose rendering of `text` is ~target_w pixels wide."""
    probe = get_font(name, 100)
    size = max(8, int(100 * target_w / probe.getlength(text)))
    return get_font(name, size)


def text_width(text, font, tracking=0):
    if not text:
        return 0
    if tracking == 0:
        return font.getlength(text)
    return sum(font.getlength(c) for c in text) + tracking * (len(text) - 1)


def draw_centered(draw, text, cx, baseline, font, fill, tracking=0):
    """Draw text horizontally centered on cx, sitting on the given baseline.
    `tracking` adds extra letter-spacing (px)."""
    if tracking == 0:
        draw.text((cx, baseline), text, font=font, fill=fill, anchor='ms')
        return
    x = cx - text_width(text, font, tracking) / 2
    for ch in text:
        draw.text((x, baseline), ch, font=font, fill=fill, anchor='ls')
        x += font.getlength(ch) + tracking


def wrap_text(text, font, max_width):
    """Break text into lines that fit within max_width pixels."""
    words = text.split()
    if not words:
        return ['']
    lines = []
    current = []
    for word in words:
        test = ' '.join(current + [word])
        if font.getlength(test) <= max_width:
            current.append(word)
        else:
            if current:
                lines.append(' '.join(current))
            current = [word]
    if current:
        lines.append(' '.join(current))
    return lines or ['']


def _norm(s):
    """lowercase + sem acentos, para comparar nomes de dias."""
    s = unicodedata.normalize('NFD', s.lower())
    return ''.join(c for c in s if unicodedata.category(c) != 'Mn')


# =========================================================
# CARIMBO (INTEGRAL / DANIEL)
# =========================================================
def make_stamp(text, color, angle=-12, seed=7):
    """Retângulo com borda dupla + texto, com desgaste de carimbo, já girado."""
    # tamanho fixado pela largura de "INTEGRAL" (~215px) -> igual p/ Daniel e Integral
    font = font_for_width('stamp', 'INTEGRAL', 215)
    bbox = font.getbbox(text)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    pad_x, pad_y, margin = 30, 20, 12
    bw, bh = tw + 2 * pad_x, th + 2 * pad_y
    size = (bw + 2 * margin, bh + 2 * margin)

    rgb = ImageColor.getrgb(color)
    layer = Image.new('RGBA', size, rgb + (0,))
    d = ImageDraw.Draw(layer)
    d.rectangle([margin, margin, margin + bw, margin + bh], outline=color, width=6)
    d.rectangle([margin + 11, margin + 11, margin + bw - 11, margin + bh - 11],
                outline=color, width=2)
    d.text((margin + pad_x - bbox[0], margin + pad_y - bbox[1]), text,
           font=font, fill=color)

    # desgaste: pontinhos e riscos transparentes (determinístico)
    rng = random.Random(seed)
    mask = Image.new('L', size, 255)
    md = ImageDraw.Draw(mask)
    for _ in range((size[0] * size[1]) // 90):
        x, y = rng.randrange(size[0]), rng.randrange(size[1])
        r = rng.choice((1, 1, 1, 2, 2, 3))
        md.ellipse([x - r, y - r, x + r, y + r], fill=0)
    for _ in range(12):
        x, y = rng.randrange(size[0]), rng.randrange(size[1])
        md.line([(x, y), (x + rng.randint(-25, 25), y + rng.randint(-6, 6))],
                fill=0, width=rng.choice((1, 2)))
    layer.putalpha(ImageChops.multiply(layer.getchannel('A'), mask))

    return layer.rotate(angle, expand=True, resample=Image.BICUBIC,
                        fillcolor=rgb + (0,))


# =========================================================
# LAYOUT DAS CAIXAS DOS DIAS
# =========================================================
def layout_day(day_data, scale, max_w):
    size = max(12, round(ITEM_SIZE * scale))
    f_item = get_font('assistant', size)
    f_label = get_font('assistant_bold', size)
    lines = []
    for meal, items in day_data.items():
        if lines:
            lines.append(('gap', ''))
        lines.append(('label', meal))
        for item in items:
            for l in wrap_text(item, f_item, max_w):
                lines.append(('item', l))
    return lines, f_item, f_label, size


def first_baseline(size):
    """1ª linha de texto (a partir do topo da caixa), sempre abaixo da linha do título."""
    return round(168 + size * 0.9)


def day_fits(lines, size, scale, cell_h):
    pitch, gap = LINE_PITCH * scale, MEAL_GAP * scale
    y = first_baseline(size)
    last = y
    for kind, _ in lines:
        if kind == 'gap':
            y += gap
        else:
            last = y
            y += pitch
    return last + size * 0.28 <= cell_h - BOTTOM_PAD


def find_scale(days_data, max_w, cell_h):
    """Maior escala em que TODOS os dias cabem dentro da caixa (altura e largura).
    Usa a mesma fonte em todas as caixas; o dia com mais itens define o limite."""
    scale = MAX_SCALE
    while scale >= MIN_SCALE:
        ok = True
        for dd in days_data:
            lines, f_item, f_label, size = layout_day(dd, scale, max_w)
            if not day_fits(lines, size, scale, cell_h):
                ok = False
                break
            for kind, txt in lines:
                if kind == 'gap':
                    continue
                f = f_label if kind == 'label' else f_item
                if text_width(txt, f) > max_w:
                    ok = False
                    break
            if not ok:
                break
        if ok:
            return scale
        scale -= 0.02
    return MIN_SCALE


# =========================================================
# IMAGEM PRINCIPAL
# =========================================================
def generate_menu_image(menu_title, date_str, menu_data, output_path):
    W, H = WIDTH, HEIGHT
    img = Image.new('RGB', (W, H), color=COLOR_BG)
    draw = ImageDraw.Draw(img)

    # ---------- CABEÇALHO ----------
    # Título
    title_text = "Cardápio Semanal"
    title_cx, title_baseline = 646, 148
    font_title = font_for_width('title', title_text, 768)
    draw.text((title_cx, title_baseline), title_text, font=font_title,
              fill=COLOR_ORANGE, anchor='ms')

    # Data (caixa alta, com espaçamento entre letras; encolhe se ficar longa)
    date_text = date_str.upper()
    date_size, date_tracking = 40, 3
    font_date = get_font('assistant', date_size)
    while text_width(date_text, font_date, date_tracking) > 640 and date_size > 20:
        date_size -= 2
        font_date = get_font('assistant', date_size)
    draw_centered(draw, date_text, title_cx, 216, font_date, COLOR_GREEN,
                  tracking=date_tracking)

    # Logo
    try:
        logo = Image.open('static/logo.png').convert("RGBA")
        logo.thumbnail(LOGO_MAX)
        img.paste(logo, LOGO_POS, logo)
    except Exception as e:
        print("Logo not found or error:", e)

    # Carimbo — só para Daniel ou Integral
    upper_title = menu_title.upper()
    stamp_text = None
    if 'DANIEL' in upper_title:
        stamp_text = 'DANIEL'
    elif 'INTEGRAL' in upper_title:
        stamp_text = 'INTEGRAL'
    if stamp_text:
        stamp = make_stamp(stamp_text, COLOR_GREEN)
        sx = int(W - 131 - stamp.width / 2)
        sy = int(195 - stamp.height / 2)
        img.paste(stamp, (sx, sy), stamp)

    # ---------- GRADE (sem margens, colada nas bordas) ----------
    row_h = (H - HEADER_H) / 2
    days = ['Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 'Sexta-feira']
    keys = list(menu_data.keys())

    # associa cada dia a uma chave do texto colado (ignora acentos)
    day_datas = []
    for day in days:
        prefix = _norm(day.split('-')[0])
        match = next((k for k in keys if _norm(k).startswith(prefix)), None)
        day_datas.append(menu_data.get(match, {}) if match else {})

    cell_w = W / 3
    cell_h = int(row_h)
    max_text_w = cell_w - 2 * CELL_TEXT_PAD
    scale = find_scale(day_datas, max_text_w, cell_h)

    font_day = get_font('assistant_bold' if DAY_HEADER_BOLD else 'assistant', 44)

    for i in range(6):
        col, row = i % 3, i // 3
        x0, x1 = round(col * cell_w), round((col + 1) * cell_w)
        y0 = HEADER_H + round(row * row_h)
        y1 = HEADER_H + round((row + 1) * row_h)
        cx = (x0 + x1) / 2

        bg = COLOR_YELLOW if (col + row) % 2 == 0 else COLOR_CREAM
        draw.rectangle([x0, y0, x1 - 1, y1 - 1], fill=bg)

        if i < 5:
            # cabeçalho do dia: linha, nome, linha
            draw.line([(x0 + CELL_LINE_PAD, y0 + 44), (x1 - CELL_LINE_PAD, y0 + 44)],
                      fill=COLOR_GREEN, width=6)
            draw_centered(draw, days[i].split('-')[0].upper(), cx, y0 + 110,
                          font_day, COLOR_GREEN, tracking=3)
            draw.line([(x0 + CELL_LINE_PAD, y0 + 142), (x1 - CELL_LINE_PAD, y0 + 142)],
                      fill=COLOR_GREEN, width=6)

            # refeições
            lines, f_item, f_label, fsize = layout_day(day_datas[i], scale, max_text_w)
            pitch, gap = LINE_PITCH * scale, MEAL_GAP * scale
            y = y0 + first_baseline(fsize)
            for kind, txt in lines:
                if kind == 'gap':
                    y += gap
                    continue
                font = f_label if kind == 'label' else f_item
                draw.text((cx, round(y)), txt, font=font, fill=COLOR_GREEN, anchor='ms')
                y += pitch
        else:
            # avisos importantes
            f_av_title = font_for_width('assistant_bold', "Avisos importantes",
                                        min(350, cell_w - 40))
            draw.text((cx, y0 + 88), "Avisos importantes", font=f_av_title,
                      fill=COLOR_GREEN, anchor='ms')
            f_av = get_font('assistant', 30)
            ay = y0 + 192
            for line in AVISOS_LINES:
                if line:
                    draw.text((cx, ay), line, font=f_av, fill=COLOR_GREEN, anchor='ms')
                ay += 44

    img.save(output_path)
