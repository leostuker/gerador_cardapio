import os
import time
import datetime
from flask import Flask, render_template, request, send_from_directory
from parser import parse_menu
from image_generator import generate_menu_image

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

OUTPUT_DIR = 'static/output'


@app.after_request
def no_cache(response):
    """Evita o navegador mostrar imagens antigas (mesmo nome de arquivo)."""
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    return response


def get_next_monday():
    today = datetime.date.today()
    days_ahead = 0 - today.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    return today + datetime.timedelta(days_ahead)


def format_date_range(start_date):
    end_date = start_date + datetime.timedelta(days=4)
    months = ["", "JANEIRO", "FEVEREIRO", "MARÇO", "ABRIL", "MAIO", "JUNHO",
              "JULHO", "AGOSTO", "SETEMBRO", "OUTUBRO", "NOVEMBRO", "DEZEMBRO"]

    s_day, s_month = start_date.day, start_date.month
    e_day, e_month = end_date.day, end_date.month

    if s_month == e_month:
        return f"SEMANA DE {s_day} A {e_day} DE {months[s_month]}"
    else:
        return f"SEMANA DE {s_day} DE {months[s_month]} A {e_day} DE {months[e_month]}"


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        raw_text = request.form.get('menu_text', '')
        date_str = request.form.get('date_str', '')

        data = parse_menu(raw_text)

        os.makedirs(OUTPUT_DIR, exist_ok=True)

        # remove imagens de gerações anteriores para não sobrar arquivo velho
        for old in os.listdir(OUTPUT_DIR):
            if old.lower().endswith('.png'):
                try:
                    os.remove(os.path.join(OUTPUT_DIR, old))
                except OSError:
                    pass

        generated_files = []
        for menu_name, menu_data in data.items():
            safe_name = "".join([c for c in menu_name if c.isalpha() or c.isdigit() or c == ' ']).strip()
            filename = f"{safe_name.replace(' ', '_')}.png"
            output_path = os.path.join(OUTPUT_DIR, filename)

            generate_menu_image(menu_name, date_str, menu_data, output_path)
            generated_files.append(filename)

        # "v" muda a cada geração -> o navegador é forçado a recarregar a imagem
        return render_template('result.html', files=generated_files, v=int(time.time()))

    next_monday = get_next_monday()
    date_str = format_date_range(next_monday)
    return render_template('index.html', date_str=date_str)


@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(OUTPUT_DIR, filename, as_attachment=True, max_age=0)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
