import os
import xmltodict
import json

def mask_cpfs(data):
    if isinstance(data, dict):
        for key, value in data.items():
            if key.upper() == 'CPF' and isinstance(value, str) and len(value) == 11 and value.isdigit():
                data[key] = '***CPF CENSURADO***'
            else:
                mask_cpfs(value)  # Recursão para processar valores dentro do dicionário
    elif isinstance(data, list):
        for item in data:
            mask_cpfs(item)  # Recursão para processar itens dentro da lista

def xml_folder_to_json(folder_path, output_folder):
    os.makedirs(output_folder, exist_ok=True)

    invalid_files = []
    
    for filename in os.listdir(folder_path):
        if filename.endswith('.xml'):
            xml_file_path = os.path.join(folder_path, filename)
            with open(xml_file_path, 'r', encoding='utf-8') as file:
                xml_data = file.read()
            
            try:
                data_dict = xmltodict.parse(xml_data)
            except Exception as e:
                print(f"Erro ao processar o arquivo {filename}: {e}")
                invalid_files.append(filename)
                continue

            mask_cpfs(data_dict)
            json_data = json.dumps(data_dict, indent=4, ensure_ascii=False)
            
            json_filename = os.path.splitext(filename)[0] + '.json'
            json_file_path = os.path.join(output_folder, json_filename)
            
            with open(json_file_path, 'w', encoding='utf-8') as json_file:
                json_file.write(json_data)
            
            print(f"Convertido: {filename} -> {json_filename}")
    
    return invalid_files

def get_json_data(folder_path):
    json_data = []
    
    for filename in os.listdir(folder_path):
        if filename.endswith('.json'):
            json_file_path = os.path.join(folder_path, filename)
            with open(json_file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                json_data.append(data)
    
    return json_data

