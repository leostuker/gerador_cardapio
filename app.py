import os
import datetime
from flask import Flask, render_template, request, send_from_directory
from parser import parse_menu
from image_generator import generate_menu_image

app = Flask(__name__)

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
        raw_text = request.form.get('menu_text')
        date_str = request.form.get('date_str')
        
        # Parse data
        data = parse_menu(raw_text)
        
        # Generate images
        os.makedirs('static/output', exist_ok=True)
        generated_files = []
        
        for menu_name, menu_data in data.items():
            safe_name = "".join([c for c in menu_name if c.isalpha() or c.isdigit() or c==' ']).strip()
            filename = f"{safe_name.replace(' ', '_')}.png"
            output_path = os.path.join('static/output', filename)
            
            generate_menu_image(menu_name, date_str, menu_data, output_path)
            generated_files.append(filename)
            
        return render_template('result.html', files=generated_files)

    # GET
    next_monday = get_next_monday()
    date_str = format_date_range(next_monday)
    return render_template('index.html', date_str=date_str)

@app.route('/download/<filename>')
def download(filename):
    return send_from_directory('static/output', filename, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
