import os
import xmltodict

def get_product_tax(product):
    tax = product.get('imposto', {}).get('vTotTrib', 0)

    if tax:
        return float(tax)
    
    else:
        taxValue = 0.0

        icms = product.get('imposto', {}).get('ICMS', {}).get('ICMS00', {})
        if icms:
            taxValue += float(icms.get('vICMS', 0))
        
        ipi = product.get('imposto', {}).get('IPI', {}).get('IPITrib', {})
        if ipi:
            taxValue += float(ipi.get('vIPI', 0))

        pis = product.get('imposto', {}).get('PIS', {}).get('PISAliq', {})
        if pis:
            taxValue += float(pis.get('vPIS', 0))

        cofins = product.get('imposto', {}).get('COFINS', {}).get('COFINSAliq', {})
        if cofins:
            taxValue += float(cofins.get('vCOFINS', 0))

    return round(taxValue, 2)


def general_query(json_data):
    totalNFE = 0
    totalProducts = 0
    totalProductsValue = 0
    totalTaxesValue = 0
    totalValue = 0

    for data in json_data:


        totalNFE += 1
        totalValue += float(data['nfeProc']['NFe']['infNFe']['total']['ICMSTot']['vNF'])

        products = data['nfeProc']['NFe']['infNFe']['det']

        if isinstance(products, dict):
            product = products['prod']
            totalProducts += 1
            totalProductsValue += float(product['vProd'])
            totalTaxesValue += get_product_tax(products)
        else:
            for product in products:
                totalProducts += 1
                totalProductsValue += float(product['prod']['vProd'])
                totalTaxesValue += get_product_tax(product)

    return {
        'totalNFE': totalNFE,
        'totalProducts': totalProducts,
        'totalProductsValue': "{:.2f}".format(totalProductsValue),
        'totalTaxesValue':"{:.2f}".format(totalTaxesValue),
        'totalValue': "{:.2f}".format(totalValue)
    }


def specific_NFE_query(json_data):
    specific_NFE = []

    for data in json_data:

        productsNames = []
        productsValue = []
        productsTaxes = []
        totalProducts = 0

        products = data['nfeProc']['NFe']['infNFe']['det']

        if isinstance(products, dict): #se for apenas um produto, ele vem em dicionario ao inves de lista
            prod = products['prod']
            productsNames.append(prod['xProd'])
            productsValue.append("{:.2f}".format(float(prod['vProd'])))
            productsTaxes.append("{:.2f}".format(get_product_tax(products)))
            totalProducts += 1
        else:
            for product in products:
                productsNames.append(product['prod']['xProd'])
                productsValue.append("{:.2f}".format(float(product['prod']['vProd'])))
                productsTaxes.append("{:.2f}".format(get_product_tax(product)))
                totalProducts += 1

        NFE = {
            'NFe': data['nfeProc']['NFe']['infNFe']['ide']['nNF'],
            'seller': data['nfeProc']['NFe']['infNFe']['emit']['xNome'],
            'totalValue': data['nfeProc']['NFe']['infNFe']['total']['ICMSTot']['vNF'],
            'totalProducts': totalProducts,
            'productsNames': productsNames,
            'productsValue': productsValue,
            'productsTaxes': productsTaxes
        }
        specific_NFE.append(NFE)

    return specific_NFE


def detailed_tax_query(json_data):
    all_nfe_taxes = []
    total_taxes_all_notes = 0.0

    for data in json_data:
        try:
            icms = float(data['nfeProc']["NFe"]["infNFe"]["total"]["ICMSTot"].get("vICMS", 0))
            ipi = float(data['nfeProc']["NFe"]["infNFe"]["total"]["ICMSTot"].get("vIPI", 0))
            pis = float(data['nfeProc']["NFe"]["infNFe"]["total"]["ICMSTot"].get("vPIS", 0))
            cofins = float(data['nfeProc']["NFe"]["infNFe"]["total"]["ICMSTot"].get("vCOFINS", 0))
        except KeyError:
            icms = ipi = pis = cofins = 0.0 # Caso não haja impostos especificados, atribuir 0

        sum_taxes = icms + ipi + pis + cofins

        # Verificar se há vTotTrib e comparar com a soma obtida, pois certas notas não especificam os impostos
        vTotTrib = data['nfeProc']["NFe"]["infNFe"]["total"]["ICMSTot"].get("vTotTrib", {})
        if vTotTrib:
            total_taxes = float(vTotTrib)
            if total_taxes > sum_taxes:
                sum_taxes = total_taxes

        total_taxes_all_notes += sum_taxes

        productsNames = []
        products = data['nfeProc']['NFe']['infNFe']['det']
        if isinstance(products, dict):
            productsNames.append(products['prod']['xProd'])
        else:
            for product in products:
                productsNames.append(product['prod']['xProd'])

        # Armazenar os detalhes da nota
        nfe_data = {
            "NFe": data['nfeProc']["NFe"]["infNFe"]["ide"]["nNF"],
            "productsNames": productsNames,
            "ICMS": "{:.2f}".format(icms),
            "IPI": "{:.2f}".format(ipi),
            "PIS": "{:.2f}".format(pis),
            "COFINS": "{:.2f}".format(cofins),
            "TotalTaxes": "{:.2f}".format(sum_taxes)
        }
        all_nfe_taxes.append(nfe_data)


    # Ordenar as notas por impostos totais em ordem decrescente
    all_nfe_taxes_sorted = sorted(all_nfe_taxes, key=lambda x: float(x["TotalTaxes"]), reverse=True)

    return round(total_taxes_all_notes,2), all_nfe_taxes_sorted

def get_supplier_nfe_links(json_data, folder_path):
    suppliers = {}
    for data in json_data:
        supplier = data['nfeProc']['NFe']['infNFe']['emit']['xNome']
        if supplier in suppliers:
            suppliers[supplier].append(data['nfeProc']['NFe']['infNFe']['ide']['nNF'])
        else:
            suppliers[supplier] = [data['nfeProc']['NFe']['infNFe']['ide']['nNF']]
    
    file_links = {supplier: [] for supplier in suppliers}

    for xml_name in os.listdir(folder_path):
        xml_path = os.path.join(folder_path, xml_name)
        
        if  xml_name.endswith('.xml'):
            with open(xml_path, 'r', encoding='utf-8') as file:
                xml_data = file.read()

            try:
                data_dict = xmltodict.parse(xml_data)
                nfe_number = data_dict['nfeProc']['NFe']['infNFe']['ide']['nNF']

                for transporter, nfe_list in suppliers.items():
                    if nfe_number in nfe_list:
                        file_links[transporter].append(xml_path)
                        break

            except Exception as e:
                print(f"Erro ao processar o arquivo {xml_name}: {e}")
                continue

    # Ordena os fornecedores em ordem alfabética
    supplier_data = {
        supplier: {"nfe_list": nfe_list, "file_links": file_links[supplier]} 
        for supplier, nfe_list in sorted(suppliers.items())
    }

    return supplier_data

def get_transp_nfe_links(json_data, folder_path):
    transporters = {}

    for data in json_data:
        transp = data['nfeProc']['NFe']['infNFe']['transp'].get('transporta', {})
        if not transp:
            continue
        else:
            transporter = transp.get('xNome', 'Não especificado')

            if transporter in transporters:
                transporters[transporter].append(data['nfeProc']['NFe']['infNFe']['ide']['nNF'])
            else:
                transporters[transporter] = [data['nfeProc']['NFe']['infNFe']['ide']['nNF']]

    file_links = {transporter: [] for transporter in transporters}

    for xml_name in os.listdir(folder_path):
        xml_path = os.path.join(folder_path, xml_name)
        
        if  xml_name.endswith('.xml'):
            with open(xml_path, 'r', encoding='utf-8') as file:
                xml_data = file.read()

            try:
                data_dict = xmltodict.parse(xml_data)
                nfe_number = data_dict['nfeProc']['NFe']['infNFe']['ide']['nNF']

                for transporter, nfe_list in transporters.items():
                    if nfe_number in nfe_list:
                        file_links[transporter].append(xml_path)
                        break

            except Exception as e:
                print(f"Erro ao processar o arquivo {xml_name}: {e}")
                continue

    # Ordena os transportadores em ordem alfabética
    transporter_data = {
        transporter: {"nfe_list": nfe_list, "file_links": file_links[transporter]} 
        for transporter, nfe_list in sorted(transporters.items())
    }

    return transporter_data