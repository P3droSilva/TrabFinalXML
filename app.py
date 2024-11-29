from flask import Flask, request, render_template, redirect, url_for
import os
import json
from load_files import xml_folder_to_json, get_json_data
from validate import validate_json
from queries import general_query, specific_NFE_query, detailed_tax_query, get_supplier_data, get_transp_data

app = Flask(__name__)

# Configuração de diretórios
UPLOAD_FOLDER = './uploads'  # Diretório para upload de XMLs
OUTPUT_FOLDER = './NotasFiscais_Json'  # Diretório para os JSONs gerados
SCHEMA_PATH = './schema.json'  # Esquema de validação JSON
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Dados processados
processed_data = {
    "general_data": None,
    "specific_data": None,
    "detailed_tax_data": None,
    "supplier_data": None,
    "transporter_data": None,
}

def process_existing_files():
    """Processa os arquivos JSON existentes na pasta OUTPUT_FOLDER."""
    try:
        # Carrega os dados JSON
        json_data = get_json_data(OUTPUT_FOLDER)

        # Executa as consultas e salva os resultados
        processed_data["general_data"] = general_query(json_data)
        processed_data["specific_data"] = specific_NFE_query(json_data)
        sum_tax, detailed_tax_data = detailed_tax_query(json_data)
        processed_data["detailed_tax_data"] = {
            "sum_tax": sum_tax,
            "details": detailed_tax_data
        }
        processed_data["supplier_data"] = get_supplier_data(json_data)
        processed_data["transporter_data"] = get_transp_data(json_data)

    except Exception as e:
        print(f"Erro ao processar arquivos existentes: {e}")

@app.route('/')
def index():
    return render_template('index.html', results=processed_data)

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'files' not in request.files:
        return "Nenhum arquivo enviado!", 400

    files = request.files.getlist('files')
    if not files:
        return "Nenhum arquivo selecionado!", 400

    try:
        # Salva os arquivos XML na pasta de upload
        for file in files:
            if file.filename:
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(file_path)

        # Converte os XMLs para JSON
        xml_folder_to_json(app.config['UPLOAD_FOLDER'], OUTPUT_FOLDER)
        
        # Valida os JSONs gerados
        validate_json(OUTPUT_FOLDER, SCHEMA_PATH)
        
        # Processa os novos JSONs
        process_existing_files()

    except Exception as e:
        return f"Erro ao processar os dados: {e}", 500

    return redirect(url_for('index'))

if __name__ == '__main__':
    # Processa os arquivos já existentes na pasta OUTPUT_FOLDER no início
    process_existing_files()
    app.run(debug=True)
