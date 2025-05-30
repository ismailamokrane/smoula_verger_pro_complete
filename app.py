from flask import Flask, render_template, request, redirect, url_for, session, send_file
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from fpdf import FPDF

app = Flask(__name__)
app.secret_key = 'verger-secret'
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

observations = []

@app.route('/')
def home():
    return redirect(url_for('surveillance'))

@app.route('/surveillance', methods=['GET', 'POST'])
def surveillance():
    global observations
    if request.method == 'POST':
        parcelle = request.form['parcelle']
        date = request.form['date']
        type_probleme = request.form['type_probleme']
        produit = request.form.get('produit', '')
        description = request.form['description']
        recommandation = request.form['recommandation']
        photo = request.files['photo']

        filename = ''
        if photo and photo.filename != '':
            filename = secure_filename(photo.filename)
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        observation = {
            'id': len(observations) + 1,
            'parcelle': parcelle,
            'date': date,
            'type': type_probleme,
            'produit': produit,
            'description': description,
            'recommandation': recommandation,
            'photo': filename
        }
        observations.append(observation)
        return redirect(url_for('surveillance'))

    return render_template('surveillance.html', observations=observations)

@app.route('/delete_observation/<int:id>')
def delete_observation(id):
    global observations
    observations = [obs for obs in observations if obs['id'] != id]
    return redirect(url_for('surveillance'))

@app.route('/rapports')
def rapports():
    return render_template('rapports.html', observations=observations)

@app.route('/export_pdf')
def export_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Rapport de Surveillance", ln=1, align='C')
    pdf.ln(5)
    for obs in observations:
        pdf.cell(200, 10, txt=f"Parcelle: {obs['parcelle']} - {obs['date']}", ln=1)
        pdf.multi_cell(0, 10, txt=f"Observation: {obs['description']}")
        pdf.multi_cell(0, 10, txt=f"Recommandation: {obs['recommandation']}")
        pdf.ln(5)
    filepath = "rapport_observations.pdf"
    pdf.output(filepath)
    return send_file(filepath, as_attachment=True)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

