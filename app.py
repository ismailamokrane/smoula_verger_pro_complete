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

# Données temporaires
users = {'admin': '1234'}
parcelles = []

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if users.get(username) == password:
            session['user'] = username
            return redirect(url_for('dashboard'))
        error = 'Identifiants incorrects'
    return render_template('login.html', error=error)

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', parcelles=parcelles)

@app.route('/surveillance', methods=['GET', 'POST'])
def surveillance():
    if 'user' not in session:
        return redirect(url_for('login'))

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
            'date': date,
            'type': type_probleme,
            'produit': produit,
            'description': description,
            'recommandation': recommandation,
            'photo': filename
        }

        for p in parcelles:
            if p['name'] == parcelle:
                p['observations'].append(observation)

        return redirect(url_for('surveillance'))

    return render_template('surveillance.html', parcelles=parcelles)

@app.route('/add_parcelle', methods=['POST'])
def add_parcelle():
    name = request.form['name']
    parcelles.append({'name': name, 'observations': []})
    return redirect(url_for('dashboard'))

@app.route('/parcelle/<name>')
def parcelle(name):
    parcelle = next((p for p in parcelles if p['name'] == name), None)
    return render_template('parcelle.html', parcelle=parcelle)

@app.route('/export_pdf/<name>')
def export_pdf(name):
    parcelle = next((p for p in parcelles if p['name'] == name), None)
    if not parcelle:
        return "Parcelle non trouvée", 404

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Rapport de Surveillance - {name}", ln=1, align='C')
    pdf.ln(5)
    count = 1
    for obs in parcelle['observations']:
        pdf.multi_cell(0, 10, txt=f"{count}. Date: {obs['date']}, Observation: {obs['description']} (Photo {count})")
        pdf.multi_cell(0, 10, txt=f"   Recommandation: {obs['recommandation']}")
        pdf.ln(2)
        count += 1
    filepath = f"{name}_rapport.pdf"
    pdf.output(filepath)
    return send_file(filepath, as_attachment=True)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    PORT = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=PORT)
