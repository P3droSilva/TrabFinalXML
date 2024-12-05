from load_files import xml_folder_to_json, get_json_data
from validate import validate_json
from queries import general_query, specific_NFE_query, detailed_tax_query
from transformation import specific_nfe_transformations, all_products_json, all_procuts_ordered_nfe

folder_path = './uploads'
output_folder = './NotasFiscais_Json'
transformations_folder = './Transformacoes'
schema_path = './schema.json'

json_data = get_json_data(output_folder)

all_procuts_ordered_nfe(json_data, transformations_folder)
