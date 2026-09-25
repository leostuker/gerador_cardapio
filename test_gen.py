from image_generator import generate_menu_image
import os

menu_title = "Cardápio Integral"
date_str = "SEMANA DE 21 A 25 DE SETEMBRO"
menu_data = {
    "Segunda-feira": {
        "Lanche": ["Leite com chocolate", "Biscoito de Leite", "Fruta"],
        "Almoço": ["Arroz", "Lentilha", "Purê", "Bolinho de peixe", "Ovo cozido", "Salada", "Fruta"]
    },
    "Terça-feira": {
        "Lanche": ["Batida de banana", "Pão com doce de fruta", "Fruta"],
        "Almoço": ["Arroz", "Feijão", "Bolinho de peixe", "Farofa", "Salada", "Fruta"]
    },
    "Quarta-feira": {
        "Lanche": ["Torta de legumes", "Suco de uva", "Fruta"],
        "Almoço": ["Massa com carne moída", "Batata rústica", "Salada", "Fruta"]
    },
    "Quinta-feira": {
        "Lanche": ["Leite", "Bolo de milho", "Fruta"],
        "Almoço": ["Carreteiro", "Feijão", "Salada", "Fruta"]
    },
    "Sexta-feira": {
        "Lanche": ["Leite com chocolate", "Biscoito de leite", "Fruta"],
        "Almoço": ["Arroz", "Frango ao molho pomodoro", "Salada", "Fruta"]
    }
}

os.makedirs('static/output', exist_ok=True)
generate_menu_image(menu_title, date_str, menu_data, 'static/output/Cardapio_Integral.png')
print("Image generated!")
