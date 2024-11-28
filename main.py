from load_files import xml_folder_to_json, get_json_data
from validate import validate_json
from queries import general_query, specific_NFE_query, detailed_tax_query

folder_path = './NotasFiscais'
output_folder = './NotasFiscais_Json'
schema_path = './schema.json'

xml_folder_to_json(folder_path, output_folder)
validate_json(output_folder, schema_path)
json_data = get_json_data(output_folder)

data = general_query(json_data)
data2 = specific_NFE_query(json_data)
print('\n\n')
print(data)
print('\n\n')
for d in data2:
    print(d)
    print('\n')
print('\n\n')