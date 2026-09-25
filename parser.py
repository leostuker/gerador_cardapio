import re

def parse_menu(text):
    data = {}
    current_menu = None
    current_day = None
    current_meal = None

    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Check for menu type e.g. **Cardápio Integral**
        if line.startswith('**Cardápio') and line.endswith('**'):
            current_menu = line.replace('**', '').strip()
            data[current_menu] = {}
            current_day = None
            current_meal = None
            continue

        if not current_menu:
            continue

        # Check for day e.g. **Segunda-feira**
        if line.startswith('**') and line.endswith('**'):
            current_day = line.replace('**', '').strip()
            data[current_menu][current_day] = {}
            current_meal = None
            continue

        if not current_day:
            continue

        # Check for meal type e.g. Lanche or Almoço
        if not line.startswith('*'):
            current_meal = line.strip()
            if current_meal not in data[current_menu][current_day]:
                data[current_menu][current_day][current_meal] = []
            continue

        # It's a food item e.g. * Arroz
        if current_meal and line.startswith('*'):
            food = line.replace('*', '').strip()
            data[current_menu][current_day][current_meal].append(food)

    return data
