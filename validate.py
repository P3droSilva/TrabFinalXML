import json
import jsonschema
import os

def validate_json(folder_path, schema_path):
    with open(schema_path, 'r', encoding='utf-8') as file:
        schema = json.load(file)
    
    for filename in os.listdir(folder_path):
        if filename.endswith('.json'):
            json_file_path = os.path.join(folder_path, filename)
            with open(json_file_path, 'r', encoding='utf-8') as file:
                json_data = json.load(file)
            
            try:
                jsonschema.validate(json_data, schema)
                print(f"Válido: {filename}")
            except jsonschema.exceptions.ValidationError as e:
                print(f"Inválido: {filename}")
                print(e.message)
            except jsonschema.exceptions.SchemaError as e:
                print(f"Erro no schema: {filename}")
                print(e.message)