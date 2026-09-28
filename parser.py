import re

DAY_RE = re.compile(r'^(segunda|ter[cç]a|quarta|quinta|sexta|s[aá]bado|domingo)', re.IGNORECASE)
SEPARATOR_RE = re.compile(r'^[\s\-–—_=*#~]{3,}$')      # ---, ***, ___, ===
BULLET_RE = re.compile(r'^[\*\-•]\s+(.*)$')            # "* item", "- item", "• item"


def _clean(text):
    """Remove marcadores markdown (**, #) e espaços."""
    return text.replace('**', '').lstrip('#').strip()


def parse_menu(text):
    data = {}
    current_menu = None
    current_day = None
    current_meal = None

    for raw in text.splitlines():
        line = raw.strip()
        if not line or SEPARATOR_RE.match(line):
            continue

        bullet = BULLET_RE.match(line)

        # Item de comida: "* Arroz"
        if bullet:
            food = _clean(bullet.group(1))
            if food and current_menu and current_day and current_meal:
                data[current_menu][current_day][current_meal].append(food)
            continue

        title = _clean(line).rstrip(':').strip()
        if not title:
            continue

        # Tipo de cardápio: **Cardápio Integral**
        if title.lower().startswith(('cardápio', 'cardapio')):
            current_menu = title
            data[current_menu] = {}
            current_day = None
            current_meal = None
            continue

        # Sem cabeçalho de cardápio: usa um nome padrão
        if current_menu is None:
            current_menu = 'Cardápio'
            data[current_menu] = {}

        # Dia da semana: **Segunda-feira**
        if DAY_RE.match(title):
            current_day = title
            data[current_menu][current_day] = {}
            current_meal = None
            continue

        # Refeição: Lanche / Almoço (com ou sem **)
        if current_day:
            current_meal = title
            data[current_menu][current_day].setdefault(current_meal, [])

    return data
