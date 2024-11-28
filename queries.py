import json


def get_product_tax(product):
    taxValue = 0

    try:
        taxValue += float(product['imposto']['vTotTrib']) #algumas notas nao possuem esse campo, entao tenta pegar cada imposto individualmente
    except KeyError:
        icms = product.get('imposto', {}).get('ICMS', {}).get('ICMS00', {})
        if icms:
            taxValue += float(icms.get('vICMS', 0))
        elif product.get('imposto', {}).get('ICMS', {}).get('ICMS60', {}):
            taxValue += float(product['imposto']['ICMS']['ICMS60']['vICMSEfet'])
        
        ipi = product.get('imposto', {}).get('IPI', {}).get('IPITrib', {})
        if ipi:
            taxValue += float(ipi.get('vIPI', 0))

        pis = product.get('imposto', {}).get('PIS', {}).get('PISAliq', {})
        if pis:
            taxValue += float(pis.get('vPIS', 0))

        cofins = product.get('imposto', {}).get('COFINS', {}).get('COFINSAliq', {})
        if cofins:
            taxValue += float(cofins.get('vCOFINS', 0))

    return taxValue


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
            totalTaxesValue += get_product_tax(product)
        else:
            for product in products:
                totalProducts += 1
                totalProductsValue += float(product['prod']['vProd'])
                totalTaxesValue += get_product_tax(product)

    return {
        'totalNFE': totalNFE,
        'totalProducts': totalProducts,
        'totalProductsValue': totalProductsValue,
        'totalTaxesValue': totalTaxesValue,
        'totalValue': totalValue
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
            productsValue.append(float(prod['vProd']))
            productsTaxes.append(get_product_tax(prod))
            totalProducts += 1
        else:
            for product in products:
                productsNames.append(product['prod']['xProd'])
                productsValue.append(float(product['prod']['vProd']))
                productsTaxes.append(get_product_tax(product))
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
            # Em caso de ausência de impostos, atribuir zero
            icms = ipi = pis = cofins = 0.0

        # Calcular total de impostos da nota
        total_taxes = icms + ipi + pis + cofins
        total_taxes_all_notes += total_taxes

        # Armazenar os detalhes da nota
        nfe_data = {
            "NFe": data['nfeProc']["NFe"]["infNFe"]["ide"]["nNF"],
            "ICMS": icms,
            "IPI": ipi,
            "PIS": pis,
            "COFINS": cofins,
            "TotalTaxes": total_taxes
        }
        all_nfe_taxes.append(nfe_data)

    # Ordenar as notas por impostos totais em ordem decrescente
    all_nfe_taxes_sorted = sorted(all_nfe_taxes, key=lambda x: x["TotalTaxes"], reverse=True)

    return {
        "TotalTaxesAllNotes": total_taxes_all_notes,
        "SortedNotesByTaxes": all_nfe_taxes_sorted
    }

