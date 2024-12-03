import os
import xmltodict
import json


def specific_nfe_transformations(xml_path, json_path, output_folder):
    transformed_files = {}

    for file in os.listdir(xml_path):
        if file.endswith('.xml'):
            xml_file_path = os.path.join(xml_path, file)
            with open(xml_file_path, 'r', encoding='utf-8') as file:
                xml_data = file.read()

            try:
                data_dict = xmltodict.parse(xml_data)
            except Exception as e:
                print(f"Erro ao processar o arquivo {file}: {e}")
                continue

            nfe_number = data_dict['nfeProc']['NFe']['infNFe']['ide']['nNF']

            if nfe_number not in transformed_files:
                transformed_files[nfe_number] = [xml_file_path]
            else:
                transformed_files[nfe_number].append(xml_file_path)

    for filename in os.listdir(json_path):
        if filename.endswith('.json'):
            json_file_path = os.path.join(json_path, filename)
            with open(json_file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

                nfe_number = data['nfeProc']['NFe']['infNFe']['ide']['nNF']

                if nfe_number not in transformed_files:
                    transformed_files[nfe_number] = [json_file_path]
                else:
                    transformed_files[nfe_number].append(json_file_path)

                product_only_file = product_only_json(data, filename, output_folder)

                transformed_files[nfe_number].append(product_only_file)

    return transformed_files
                


    

def product_only_json(nfe_data, filename, path): #create a new json file with only the product session of the nfe
    new_json = {}
    new_json['produtos'] = nfe_data['nfeProc']['NFe']['infNFe']['det']
    
    #save the file as a new json file
    new_json_filename = os.path.splitext(filename)[0] + '_produtos.json'

    new_json_file_path = os.path.join(path, new_json_filename)

    with open(new_json_file_path, 'w', encoding='utf-8') as new_json_file:
        json.dump(new_json, new_json_file, indent=4, ensure_ascii=False)

    return new_json_file_path



            
            
            





