import os
import xmltodict
import json
import random
import copy

def specific_nfe_transformations(xml_folder, json_folder, output_folder):
    transformed_files = {}

    for file in os.listdir(xml_folder):
        if file.endswith('.xml'):
            xml_file_path = os.path.join(xml_folder, file)
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

    for filename in os.listdir(json_folder):
        if filename.endswith('.json'):
            json_file_path = os.path.join(json_folder, filename)
            with open(json_file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

                nfe_number = data['nfeProc']['NFe']['infNFe']['ide']['nNF']

                if nfe_number not in transformed_files:
                    transformed_files[nfe_number] = [json_file_path]
                else:
                    transformed_files[nfe_number].append(json_file_path)

                product_only_file = product_only_json(data, filename, output_folder)
                alphabetical_order_file = alphabetical_order_products(data, filename, output_folder)

                transformed_files[nfe_number].append(product_only_file)
                transformed_files[nfe_number].append(alphabetical_order_file)

    return transformed_files


def alphabetical_order_products(nfe_data, filename, path): 
    json_copy = nfe_data.copy()
    json_det = json_copy['nfeProc']['NFe']['infNFe']['det']

    if isinstance(json_det, list):
        json_det.sort(key=lambda x: x['prod']['xProd'].lower())

    new_json_filename = os.path.splitext(filename)[0] + '_produtos_ordenados.json'
    new_json_file_path = os.path.join(path, new_json_filename)

    if os.path.exists(new_json_file_path):
        os.remove(new_json_file_path)

    with open(new_json_file_path, 'w', encoding='utf-8') as new_json_file:
        json.dump(json_copy, new_json_file, indent=4, ensure_ascii=False)

    return new_json_file_path


def product_only_json(nfe_data, filename, path): 
    new_json = {}
    new_json['produtos'] = nfe_data['nfeProc']['NFe']['infNFe']['det']
    
    new_json_filename = os.path.splitext(filename)[0] + '_produtos.json'
    new_json_file_path = os.path.join(path, new_json_filename)

    if os.path.exists(new_json_file_path):
        os.remove(new_json_file_path)

    with open(new_json_file_path, 'w', encoding='utf-8') as new_json_file:
        json.dump(new_json, new_json_file, indent=4, ensure_ascii=False)

    return new_json_file_path


def all_products_json(json_data, path):
    new_json = {}
    new_json['produtos'] = []
    nItem = 1

    for nfe_data in json_data:
        json_copy = copy.deepcopy(nfe_data)
        json_det = json_copy['nfeProc']['NFe']['infNFe']['det']

        if isinstance(json_det, dict):
            json_det['@nItem'] = nItem
            new_json['produtos'].append(json_det)
            nItem += 1

        else:
            for product in json_det:
                product['@nItem'] = nItem
                new_json['produtos'].append(product)
                nItem += 1

    new_json_filename = 'all_products.json'
    new_json_file_path = os.path.join(path, new_json_filename)

    if os.path.exists(new_json_file_path):
        os.remove(new_json_file_path)

    with open(new_json_file_path, 'w', encoding='utf-8') as new_json_file:
        json.dump(new_json, new_json_file, indent=4, ensure_ascii=False)

    return new_json_file_path


def all_products_ordered_nfe(json_data, path):
    json_len = len(json_data)
    random_index = random.randint(0, json_len - 1)
    random_nfe = json_data[random_index]

    new_json = copy.deepcopy(random_nfe)
    new_json['nfeProc']['NFe']['infNFe']['det'] = []

    for nfe in json_data:
        json_det = nfe['nfeProc']['NFe']['infNFe']['det']
        print(json_det)
        print("\n\n")
        if isinstance(json_det, dict):
            new_json['nfeProc']['NFe']['infNFe']['det'].append(json_det)
        elif isinstance(json_det, list):
            for product in json_det:
                new_json['nfeProc']['NFe']['infNFe']['det'].append(product)


    new_json['nfeProc']['NFe']['infNFe']['det'].sort(key=lambda x: x['prod']['xProd'].lower())
    nItem = 1
    for product in new_json['nfeProc']['NFe']['infNFe']['det']:
        product['@nItem'] = nItem
        nItem += 1

    new_json['nfeProc']['NFe']['infNFe']['total']['ICMSTot'] = {}
    new_json['nfeProc']['NFe']['infNFe']['total']['ICMSTot']['vICMS'] = "0.00"
    new_json['nfeProc']['NFe']['infNFe']['total']['ICMSTot']['vIPI'] = "0.00"
    new_json['nfeProc']['NFe']['infNFe']['total']['ICMSTot']['vPIS'] = "0.00"
    new_json['nfeProc']['NFe']['infNFe']['total']['ICMSTot']['vCOFINS'] = "0.00"
    new_json['nfeProc']['NFe']['infNFe']['total']['ICMSTot']['vTotTrib'] = "0.00"
    new_json['nfeProc']['NFe']['infNFe']['total']['ICMSTot']['vProd'] = "0.00"
    new_json['nfeProc']['NFe']['infNFe']['total']['ICMSTot']['vNF'] = "0.00"

    for nfe in json_data:
        nfe_total = nfe['nfeProc']['NFe']['infNFe']['total']['ICMSTot']

        icms = float(nfe_total.get('vICMS', 0.0))
        ipi = float(nfe_total.get('vIPI', 0.0))
        pis = float(nfe_total.get('vPIS', 0.0))
        cofins = float(nfe_total.get('vCOFINS', 0.0))

        vTotTrib = float(nfe_total.get('vTotTrib', icms + ipi + pis + cofins))
        vProd = float(nfe_total.get('vProd', 0.0))
        vNf = float(nfe_total.get('vNF', 0.0))

        new_json['nfeProc']['NFe']['infNFe']['total']['ICMSTot']['vICMS'] = "{:.2f}".format(icms + float(new_json['nfeProc']['NFe']['infNFe']['total']['ICMSTot']['vICMS']))
        new_json['nfeProc']['NFe']['infNFe']['total']['ICMSTot']['vIPI'] = "{:.2f}".format(ipi + float(new_json['nfeProc']['NFe']['infNFe']['total']['ICMSTot']['vIPI']))
        new_json['nfeProc']['NFe']['infNFe']['total']['ICMSTot']['vPIS'] = "{:.2f}".format(pis + float(new_json['nfeProc']['NFe']['infNFe']['total']['ICMSTot']['vPIS']))
        new_json['nfeProc']['NFe']['infNFe']['total']['ICMSTot']['vCOFINS'] = "{:.2f}".format(cofins + float(new_json['nfeProc']['NFe']['infNFe']['total']['ICMSTot']['vCOFINS']))
        new_json['nfeProc']['NFe']['infNFe']['total']['ICMSTot']['vTotTrib'] = "{:.2f}".format(vTotTrib + float(new_json['nfeProc']['NFe']['infNFe']['total']['ICMSTot']['vTotTrib']))
        new_json['nfeProc']['NFe']['infNFe']['total']['ICMSTot']['vProd'] = "{:.2f}".format(vProd + float(new_json['nfeProc']['NFe']['infNFe']['total']['ICMSTot']['vProd']))
        new_json['nfeProc']['NFe']['infNFe']['total']['ICMSTot']['vNF'] = "{:.2f}".format(vNf + float(new_json['nfeProc']['NFe']['infNFe']['total']['ICMSTot']['vNF']))
        
    nfe_pag = new_json['nfeProc']['NFe']['infNFe'].get('pag', [])
    if nfe_pag:
        del new_json['nfeProc']['NFe']['infNFe']['pag']

    nfe_cobr = new_json['nfeProc']['NFe']['infNFe'].get('cobr', [])
    if nfe_cobr:
        del new_json['nfeProc']['NFe']['infNFe']['cobr']


    new_json_filename = 'all_products_ordered_nfe.json'
    new_json_file_path = os.path.join(path, new_json_filename)

    if os.path.exists(new_json_file_path):
        os.remove(new_json_file_path)

    with open(new_json_file_path, 'w', encoding='utf-8') as new_json_file:
        json.dump(new_json, new_json_file, indent=4, ensure_ascii=False)

    return new_json_file_path



            
            
            





