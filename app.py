from flask import Flask, request, jsonify, render_template
import pandas as pd
from datetime import datetime
import os  # Pentru a prelua portul din variabilele de mediu (pe Render)

app = Flask(__name__)

@app.route('/')
def index():
    # Randează prima pagină HTML (formularul de upload)
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    # Verificăm dacă fișierul a fost trimis
    if 'file' not in request.files:
        return jsonify({"error": "Fișierul nu a fost trimis."}), 400

    file = request.files['file']
    name_column = request.form.get('name_column')
    date_column = request.form.get('date_column')

    # Verificăm extensia fișierului
    if not file.filename.endswith('.xlsx'):
        return jsonify({"error": "Fișierul trebuie să fie în format .xlsx"}), 400

    try:
        # Citește fișierul Excel într-un DataFrame
        df = pd.read_excel(file)

        # Normalizează numele coloanelor pentru a nu fi case-sensitive
        df.columns = [str(col).strip().lower() for col in df.columns]
        name_column = name_column.strip().lower()
        date_column = date_column.strip().lower()

        # Verificăm dacă coloanele introduse există în fișier
        if name_column not in df.columns or date_column not in df.columns:
            return jsonify({"error": "Coloanele specificate nu există în fișier."}), 400

        today = datetime.now().date()
        results = []

        for _, row in df.iterrows():
            name = row.get(name_column)
            date_raw = row.get(date_column)

            # Dacă lipsesc datele, trecem peste rând
            if pd.isna(name) or pd.isna(date_raw):
                continue

            try:
                # Conversie corectă a datei folosind zi/lună/an (dayfirst=True)
                expiry_date = pd.to_datetime(str(date_raw), dayfirst=True).date()
            except Exception:
                continue  # Ignorăm dacă data nu e validă

            # Calculăm diferența de zile între azi și data expirării
            days_diff = (expiry_date - today).days

            # Determinăm statusul în funcție de câte zile au rămas
            if days_diff < 0:
                if days_diff == -1:
                    status = "Expirat de ieri"
                else:
                    status = f"Expirat de {abs(days_diff)} zile"
            elif days_diff == 0:
                status = "Expiră astăzi"
            elif days_diff == 1:
                status = "Expiră mâine"
            elif days_diff <= 7:
                status = f"Expiră în {days_diff} zile"
            else:
                continue  # Nu afișăm dacă expiră peste mai mult de 7 zile

            # Adăugăm rezultatul în lista finală
            results.append({
                "name": str(name),
                "date": expiry_date.strftime("%d/%m/%Y"),  # Format zi/lună/an
                "status": status
            })

        # Returnăm rezultatele în format JSON
        return jsonify(results)

    except Exception as e:
        # În caz de eroare, returnăm mesajul corespunzător
        return jsonify({"error": f"Eroare la procesarea fișierului: {str(e)}"}), 500


# Pornim aplicația Flask, fie local, fie pe Render (cu PORT din variabile de mediu)
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
