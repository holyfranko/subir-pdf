import os
from flask import Flask, render_template, request, redirect, url_for
from PyPDF2 import PdfReader

#indicando en que carpeta guardar los pdf y creandola por si noe xiste
app = Flask(__name__)
upload_folder = 'uploads'
os.makedirs(upload_folder, exist_ok=True)

#renderizando index
@app.route('/')
def index():
    return render_template('index.html')

#definiendo ruta y recibe pdf mediante POST, despues redirecciona a search
@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        pdf_file = request.files['pdf_file']
        pdf_file.save(os.path.join(upload_folder, pdf_file.filename))
        return redirect(url_for('search_word', filename=pdf_file.filename))

#definiendo ruta en la cual se preguntara que palabra buscar, luego lee el pedf se busca la palabra y muestra los 50 caracteres si es que coinside la busqueda
@app.route('/search/<filename>', methods=['GET', 'POST'])
def search_word(filename):
    if request.method == 'POST':
        word = request.form['word']
        pdf_path = os.path.join(upload_folder, filename)
        with open(pdf_path, 'rb') as file:
            reader = PdfReader(file)
            text = reader.pages[0].extract_text()
            matches = find_matches(text, word)[:20]
            return render_template('results.html', filename=filename, word=word, matches=matches, text=text)
    else:
        return render_template('search.html', filename=filename, text='')

#definiendo funcion para encontrar los match entre la busqueda de usuario y el pdf, luego devuelve una lista con los match
def find_matches(text, word, context_size=50):
    start_index = 0
    matches = []
    while True:
        start_index = text.find(word, start_index)
        if start_index == -1:
            break
        match_text = text[start_index:start_index + len(word) + context_size]
        matches.append(match_text)
        start_index += len(word)
    return matches

#debug
if __name__ == '__main__':
    app.run(debug=True)