import csv
import pandas as pd

size = 100000
max = 1000

large_cities = pd.read_csv('../data/output/large_cities.csv', dtype=str)
large_groups = pd.read_csv('../data/output/large_groups.csv', dtype=str)


def is_concerned(some_type_id):
    # Keep only organizations of which the type is known, and exclude
    # 1: Natural persons
    # 2: Organizations with no moral personality
    # 7190: "Ecole nationale non dotée de la personnalité morale"
    return (len(some_type_id) == 4) and not (some_type_id[0] in ['1', '2']) and not (some_type_id == '7190')


def is_private(some_type_id):
    return some_type_id[0] in ['3', '5', '6', '8', '9']


def is_large(some_type_id):
    return some_type_id in ['7220', '7229', '7230']


def is_city(some_type_id):
    return some_type_id in ['7210']


def is_city_group(some_type_id):
    return some_type_id in ['7343', '7344', '7346', '7348']


def get_staff(staff_code):
    staff_codes = {
        '': 0,
        'NN': 0,
        '00': 0,
        '01': 1,
        '02': 3,
        '03': 6,
        '11': 10,
        '12': 20,
        '21': 50,
        '22': 100,
        '31': 200,
        '32': 250,
        '41': 500,
        '42': 1000,
        '51': 2000,
        '52': 5000,
        '53': 10000
    }
    return staff_codes[staff_code]


print('INFO: Processing legal units file (~ 21M records).')
organizations = {}
with open('../data/SIRENE/StockUniteLegale_utf8.csv', 'r', encoding='UTF-8') as input_file:
    index = 0
    for line in input_file:
        if index == 0:
            header = {k: v for v, k in enumerate(line.split(','))}
            columns_count = len(line.split(','))
            index = 1
        else:
            cells = line.split(',')
            if len(cells) != columns_count:
                # Complex CSV string
                cells = list(csv.reader([line]))[0]
            active = cells[header['etatAdministratifUniteLegale']]
            type_id = cells[header['categorieJuridiqueUniteLegale']]
            if active == 'A' and is_concerned(type_id):
                code = cells[header['siren']]
                staff = get_staff(cells[header['trancheEffectifsUniteLegale']])
                concerned = False
                if is_private(type_id):
                    concerned = staff >= 250
                else:
                    if is_city(type_id) or is_city_group(type_id):
                        concerned = True
                    elif is_large(type_id):
                        concerned = True
                    else:
                        concerned = staff >= 250
                # Exclude overseas particular cases
                # > TERRITOIRE DE NOUVELLE-CALEDONIE
                # > CONSEIL TERRITORIAL ST BARTHELEMY
                # > PROVINCE DES ILES
                if concerned and not (code in ['229880018', '200015816', '200012979']):
                    organizations[code] = ({
                        'type_id': type_id,
                        'id': code,
                        'name': cells[header['denominationUniteLegale']],
                        'staff': staff,
                    })
            index += 1
            if index % (1 * size) == 0:
                if index > max * size:
                    break
                print(index)

print('INFO: Processing sites file (~ 29M records).')
with open('../data/SIRENE/StockEtablissement_utf8.csv', encoding='UTF-8') as input_file:
    index = 0
    for line in input_file:
        if index == 0:
            header = {k: v for v, k in enumerate(line.split(','))}
            columns_count = len(line.split(','))
            index = 1
        else:
            cells = line.split(',')
            if len(cells) != columns_count:
                # Complex CSV string
                cells = list(csv.reader([line]))[0]
            code = cells[header['siren']]
            if code in organizations:
                if cells[header['etablissementSiege']] == 'true' and cells[header['etatAdministratifEtablissement']] == 'A':
                    org = organizations[code]
                    org['city_id'] = cells[header['codeCommuneEtablissement']]
                    organizations[code] = org
            index += 1
            if index % (1 * size) == 0:
                if index > max * size:
                    break
                print(index)

legal_unit_types = pd.read_csv('legal_unit_types.csv', encoding='UTF-8', dtype=str)

organizations = list(organizations.values())
organizations = pd.DataFrame.from_dict(organizations, dtype=str)
organizations = organizations.merge(legal_unit_types, how='left', left_on='type_id', right_on='type_id')
organizations = organizations.fillna('')
organizations['staff'] = pd.to_numeric(organizations['staff'])

organizations['is_concerned'] = False
organizations['is_private'] = False
for i in range(organizations.shape[0]):
    type_id = organizations.at[i, 'type_id']
    organizations.at[i, 'is_private'] = is_private(type_id)
    if is_private(type_id):
        city_id = organizations.at[i, 'city_id']
        if len(city_id) == 5 and city_id[:2] in ['96', '97', '98', '99']:
            organizations.at[i, 'is_concerned'] = organizations.at[i, 'staff'] >= 250
        else:
            organizations.at[i, 'is_concerned'] = organizations.at[i, 'staff'] >= 500
    else:
        if is_city(type_id):
            organizations.at[i, 'is_concerned'] = organizations.at[i, 'city_id'] in large_cities['CODGEO'].tolist()
            # City of Marseille is large but population is split by arrondissements. Force Marseille in our list.
            if organizations.at[i, 'id'] in ['211300553']:
                organizations.at[i, 'is_concerned'] = True
        elif is_city_group(type_id):
            organizations.at[i, 'is_concerned'] = organizations.at[i, 'id'] in large_groups['EPCI'].tolist()
        else:
            organizations.at[i, 'is_concerned'] = True

organizations = organizations[organizations['is_concerned']]
organizations = organizations[['id', 'name', 'staff', 'city_id',
                               'is_private', 'type_id', 'type_label_1', 'type_label_2', 'type_label_3']]
organizations.to_csv('../data/output/organizations.csv', index=False, encoding='UTF-8')
