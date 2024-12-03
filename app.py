from flask import Flask, request, render_template, redirect, url_for, send_from_directory, flash
import os
from load_files import xml_folder_to_json, get_json_data
from validate import validate_json
from queries import general_query, specific_NFE_query, detailed_tax_query, get_supplier_nfe_links, get_transp_nfe_links
from transformation import specific_nfe_transformations

app = Flask(__name__)
app.secret_key = 'projeto_xml_json'

# Configuração de diretórios
UPLOAD_FOLDER = './uploads'  # Diretório para upload de XMLs
OUTPUT_FOLDER = './NotasFiscais_Json'  # Diretório para os JSONs gerados
TRANSFORMATION_FOLDER = './Transformacoes' # Diretório para as transformações de arquivos
SCHEMA_PATH = './schema.json'  # Esquema de validação JSON
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['TRANSFORMATION_FOLDER'] = TRANSFORMATION_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(TRANSFORMATION_FOLDER, exist_ok=True)

# Dados processados
processed_data = {
    "general_data": None,
    "specific_data": None,
    "detailed_tax_data": None,
    "supplier_data": None,
    "transporter_data": None
}

transformations = {
    "specific_file_transformations": None
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
        processed_data["supplier_data"] = get_supplier_nfe_links(json_data, UPLOAD_FOLDER)
        processed_data["transporter_data"] = get_transp_nfe_links(json_data, UPLOAD_FOLDER)

        # Transformações de Arquivos
        transformations["specific_file_transformations"] = specific_nfe_transformations(UPLOAD_FOLDER, OUTPUT_FOLDER, TRANSFORMATION_FOLDER)
        

    except Exception as e:
        print(f"Erro ao processar arquivos existentes: {e}")

@app.route('/')
def index():
    return render_template('index.html', results=processed_data)

@app.route('/file_view')
def file_view():
    return render_template('file_view.html', results=transformations)

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'files' not in request.files:
        return "Nenhum arquivo enviado!", 400

    files = request.files.getlist('files')
    if not files:
        return "Nenhum arquivo selecionado!", 400

    invalid_files = 0
    try:
        # Process uploaded files
        for file in files:
            if file.filename:
                # Check if the file is XML
                if not file.filename.lower().endswith('.xml'):
                    invalid_files += 1
                    continue
                
                # Save the XML file to the upload folder
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(file_path)

        # Convert XML files to JSON
        invalid_xml_files = xml_folder_to_json(app.config['UPLOAD_FOLDER'], OUTPUT_FOLDER)

        # Delete invalid XML files
        for invalid_file in invalid_xml_files:
            invalid_files += 1
            invalid_file_path = os.path.join(app.config['UPLOAD_FOLDER'], invalid_file)
            if os.path.exists(invalid_file_path):
                os.remove(invalid_file_path)
        
        # Validate the generated JSON files
        invalid_json_files = validate_json(OUTPUT_FOLDER, SCHEMA_PATH)
        
        # Delete invalid XML files
        for invalid_file in invalid_json_files:
            invalid_files += 1
            invalid_file_path = os.path.join(app.config['UPLOAD_FOLDER'], invalid_file)
            if os.path.exists(invalid_file_path):
                os.remove(invalid_file_path)

        if invalid_files > 0:
            flash(f"{invalid_files} arquivo(s) inválidos removidos!\nPor favor, selecione arquivos .xml de notas fiscais válidas.", "warning")

        # Process the validated JSON files
        process_existing_files()

    except Exception as e:
        return f"Erro ao processar os dados: {e}", 500

    return redirect(url_for('index'))

@app.route('/delete/<xml_path>', methods=['POST'])
def delete_files(xml_path):
    # Define the paths for the files to be deleted
    nfe_json_path = os.path.join(OUTPUT_FOLDER, os.path.splitext(os.path.basename(xml_path))[0] + '.json')
    produtos_json_path = os.path.join(TRANSFORMATION_FOLDER, os.path.splitext(os.path.basename(xml_path))[0] + '_produtos.json')
    
    # Delete the files if they exist
    try:
        if os.path.exists(xml_path):
            os.remove(xml_path)
        if os.path.exists(nfe_json_path):
            os.remove(nfe_json_path)
        if os.path.exists(produtos_json_path):
            os.remove(produtos_json_path)
        
        # Flash success message
        flash(f"Arquivos da NFE excluídos com sucesso!", "success")
    except Exception as e:
        flash(f"Erro ao excluir arquivos da NFE: {str(e)}", "danger")

    process_existing_files()

    return redirect(url_for('file_view'))

@app.route('/uploads/<path:filename>')
def view_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/NotasFiscais_Json/<path:filename>')
def view_json_file(filename):
    return send_from_directory(OUTPUT_FOLDER, filename)

@app.route('/Transformacoes/<path:filename>')
def view_transformation_file(filename):
    return send_from_directory(TRANSFORMATION_FOLDER, filename)


if __name__ == '__main__':
    # Processa os arquivos já existentes na pasta OUTPUT_FOLDER no início
    process_existing_files()
    app.run(debug=True)
