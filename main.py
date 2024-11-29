from load_files import xml_folder_to_json, get_json_data
from validate import validate_json
from queries import general_query, specific_NFE_query, detailed_tax_query, get_supplier_data, get_transp_data

folder_path = './NotasFiscais'
output_folder = './NotasFiscais_Json'
schema_path = './schema.json'

xml_folder_to_json(folder_path, output_folder)
validate_json(output_folder, schema_path)
json_data = get_json_data(output_folder)

general_data = general_query(json_data)
specific_data = specific_NFE_query(json_data)
sum_tax, detailed_tax_data = detailed_tax_query(json_data)
supplier_data = get_supplier_data(json_data)
transporter_data = get_transp_data(json_data)