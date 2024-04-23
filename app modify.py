import os
import PyPDF2
import io
from PyPDF2 import PdfReader, PdfWriter
from flask import Flask, render_template, request, redirect, url_for, send_file, session

app = Flask(__name__)
app.secret_key = 'super secret key'

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'pdf' not in request.files:
            return "No file part"
        pdf_file = request.files['pdf']
        if pdf_file.filename == '':
            return "No selected file"
        keyword = request.form['keyword']
        pdf_text = extract_pdf_text(pdf_file)
        context_matches = find_context_matches(pdf_text, keyword)
        if context_matches:
            session['context_matches'] = context_matches
            session['keyword'] = keyword
            return redirect(url_for('search_results', selected_index=0))
        else:
            return "No matches found."
    return render_template('index.html')



@app.route('/search_results/<int:selected_index>', methods=['GET', 'POST'])
def search_results(selected_index):
    if request.method == 'POST':
        pdf_file = request.files['pdf']
        new_text = request.form['new_text']
        modified_pdf_text = modify_text_in_pdf_text(extract_pdf_text(pdf_file), session['context_matches'], selected_index, new_text)
        modified_pdf = create_modified_pdf(modified_pdf_text)
        return send_file(modified_pdf, as_attachment=True, attachment_filename='modified_pdf.pdf')
    else:
        context_matches = session.get('context_matches', [])
        keyword = session.get('keyword', '')
        return render_template('search_results.html', context_matches=context_matches, keyword=keyword, selected_index=selected_index)

@app.route('/modify_context', methods=['POST'])
def modify_context():
    pdf_file = request.files['pdf']
    keyword = request.form['keyword']
    selected_index = int(request.form['selected_index'])
    new_text = request.form['new_text']
    pdf_text = extract_pdf_text(pdf_file)
    context_matches = find_context_matches(pdf_text, keyword)
    modified_pdf_text = modify_text_in_pdf_text(pdf_text, context_matches, selected_index, new_text)
    return render_template('modified_context.html', modified_pdf_text=modified_pdf_text)

@app.route('/download', methods=['POST'])
def download():
    pdf_file = request.files['pdf']
    keyword = request.form['keyword']
    selected_index = int(request.form['selected_index'])
    new_text = request.form['new_text']
    modified_pdf_text = modify_text_in_pdf_text(extract_pdf_text(pdf_file), session['context_matches'], selected_index, new_text)
    modified_pdf = create_modified_pdf(modified_pdf_text)
    return send_file(modified_pdf, as_attachment=True, attachment_filename='modified_pdf.pdf')

def extract_pdf_text(pdf_file):
    pdf_bytes = pdf_file.read()
    if len(pdf_bytes) == 0:
        raise ValueError("El archivo PDF ta vacio")
    
    pdf_reader = PdfReader(io.BytesIO(pdf_bytes))
    text = ""
    for page_num in range(len(pdf_reader.pages)):
        text += pdf_reader.pages[page_num].extract_text()
    return text

def find_context_matches(pdf_text, keyword):
    matches = []
    clean_text = pdf_text.strip().replace('\n', ' ')
    words = clean_text.split()
    for i, word in enumerate(words):
        if word.lower() == keyword.lower():
            start_index = max(0, i - 20)
            end_index = min(len(words), i + 20)
            context = ' '.join(words[start_index:end_index])
            matches.append({'context': context, 'index': i})
    return matches

def modify_text_in_pdf_text(pdf_text, context_matches, selected_index, new_text):
    context_match = context_matches[selected_index]
    words = pdf_text.split()
    start_index = context_match['index'] - 20
    end_index = context_match['index'] + 20
    words[start_index:end_index] = new_text.split()
    modified_pdf_text = ' '.join(words)
    return modified_pdf_text

def create_modified_pdf(modified_pdf_text):
    output = io.BytesIO()
    pdf_writer = PdfWriter()
    pdf_writer.add_page(PdfReader('').pages[0])
    pdf_writer.add_page(PdfReader(io.BytesIO(modified_pdf_text.encode())).pages[0])
    pdf_writer.write(output)
    output.seek(0)
    return output

if __name__ == '__main__':
    app.run(debug=True)