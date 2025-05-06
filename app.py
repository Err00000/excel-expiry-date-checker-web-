from flask import Flask, request, jsonify, render_template
import pandas as pd
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "Fișierul nu a fost trimis."}), 400

    file = request.files['file']
    name_column = request.form.get('name_column')
    date_column = request.form.get('date_column')

    if not file.filename.endswith('.xlsx'):
        return jsonify({"error": "Fișierul trebuie să fie în format .xlsx"}), 400

    try:
        # Citește fișierul Excel
        df = pd.read_excel(file)

        # Normalizează numele coloanelor (case insensitive)
        df.columns = [str(col).strip().lower() for col in df.columns]
        name_column = name_column.strip().lower()
        date_column = date_column.strip().lower()

        if name_column not in df.columns or date_column not in df.columns:
            return jsonify({"error": "Coloanele specificate nu există în fișier."}), 400

        today = datetime.now().date()
        results = []

        for _, row in df.iterrows():
            name = row.get(name_column)
            date_raw = row.get(date_column)

            if pd.isna(name) or pd.isna(date_raw):
                continue

            try:
                # Conversie corectă a datei, forțând dayfirst=True
                expiry_date = pd.to_datetime(str(date_raw), dayfirst=True).date()
            except Exception:
                continue  # Ignoră dacă data nu e validă

            days_diff = (expiry_date - today).days

            # Determinăm status
            if days_diff < 0:
                status = f"Expirat de {abs(days_diff)} zile"
            elif days_diff == 0:
                status = "Expiră astazi"
            elif days_diff == 1:
                status = "Expiră mâine"
            elif days_diff <= 7:
                status = f"Expiră în {days_diff} zile"
            else:
                continue  # Nu afișăm dacă expiră peste mai mult de 7 zile

            results.append({
                "name": str(name),
                "date": expiry_date.strftime("%d/%m/%Y"),  # FORȚAT zi/lună/an
                "status": status
            })

        return jsonify(results)

    except Exception as e:
        return jsonify({"error": f"Eroare la procesarea fișierului: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
