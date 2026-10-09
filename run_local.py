import os
from parser import parse_menu
from image_generator import generate_menu_image

text = """**Cardápio Integral**

**Terça-feira**

Lanche da Manhã
* Leite
* Cuca
* Fruta

Almoço
* Arroz
* Lentilha
* Ovo
* Salada
* Fruta

**Quarta-feira**

Lanche da Manhã
* Torta de legumes
* Suco de uva
* Fruta

Almoço
* Polenta com carne em cubos
* Feijão
* Salada
* Fruta

**Quinta-feira**

Lanche da Manhã
* Bolo de milho
* Leite
* Fruta

Almoço
* Massa
* Aipim
* Frango
* Salada
* Fruta

**Sexta-feira**

Lanche da Manhã
* Leite com chocolate
* Biscoito de leite
* Fruta

Almoço
* Arroz
* Feijão
* Bolinho de peixe
* Farofa
* Salada
* Fruta

**Cardápio Parcial**

**Terça-feira**

Almoço
* Arroz
* Lentilha
* Ovo
* Salada
* Fruta

**Quarta-feira**

Almoço
* Polenta com carne em cubos
* Feijão
* Salada
* Fruta

**Quinta-feira**

Almoço
* Massa
* Aipim
* Frango
* Salada
* Fruta

**Sexta-feira**

Almoço
* Arroz
* Feijão
* Bolinho de peixe
* Farofa
* Salada
* Fruta

**Cardápio Daniel**

**Terça-feira**

Lanche da Manhã
* Leite
* Pão de aveia
* Fruta

Almoço
* Arroz
* Lentilha
* Frango
* Salada
* Fruta

**Quarta-feira**

Lanche da Manhã
* Leite
* Frutas

Almoço
* Polenta com carne em cubos
* Feijão
* Salada
* Fruta

**Quinta-feira**

Lanche da Manhã
* Bolo
* Suco de uva
* Fruta

Almoço
* Massa
* Aipim
* Frango
* Salada
* Fruta

**Sexta-feira**

Lanche da Manhã
* Leite
* Biscoito de aveia
* Fruta

Almoço
* Arroz
* Feijão
* Bolinho de peixe
* Farofa
* Salada
* Fruta"""

data = parse_menu(text)
os.makedirs('static/output', exist_ok=True)
date_str = "SEMANA DE 13 A 16 DE OUTUBRO" # Just an arbitrary date, or leave it empty? Let's leave it empty or use format_date_range

for menu_name, menu_data in data.items():
    safe_name = "".join([c for c in menu_name if c.isalpha() or c.isdigit() or c == ' ']).strip()
    filename = f"{safe_name.replace(' ', '_')}.png"
    output_path = os.path.join('static/output', filename)
    print(f"Generating {output_path}...")
    generate_menu_image(menu_name, date_str, menu_data, output_path)
