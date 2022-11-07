import csv
import os
import pandas as pd

# Directories

data_path = '../data/'
input_path = '../input/'
output_path = '../output/'

if not os.path.exists(output_path):
    os.mkdir(output_path)

filename_legal_units = input_path + 'StockUniteLegale_utf8.csv'
filename_establishments = input_path + 'StockEtablissement_utf8.csv'

populations = pd.read_csv(output_path + 'populations.csv', dtype=str)

log_chunk_size = 1000000

# Utility functions


class Organization:

    def __init__(self, id, name, type_id):
        self.id = id
        self.name = name
        self.type_id = type_id
        self.min_staff_1 = 0
        self.min_staff_2 = 0
        self.max_staff_1 = None
        self.max_staff_2 = 0
        self.population = 0
        self.city_id = None
        self.active = False
        self.regulation = None


def is_concerned(some_type_id):
    # Keep only organizations of which the type is known, and exclude
    # 1: Natural persons
    # 2: Organizations with no moral personality
    # 7190: "Ecole nationale non dotée de la personnalité morale" > we only want juridical persons
    # 7312: "Commune associée" > the main city will do the reporting
    # 7225: "Collectivité et territoire d'Outre Mer" > follow local legislation
    return (len(some_type_id) == 4) and not (some_type_id[0] in ['1', '2']) and not (some_type_id in ['7190', '7225', '7312'])


def is_private(some_type_id):
    return some_type_id[0] in ['3', '5', '6', '8', '9']


def is_population_based(some_type_id):
    return some_type_id in ['7210', '7220', '7229', '7230', '7343', '7344', '7346', '7348']


def is_city(some_type_id):
    return some_type_id == '7210'


def is_department(some_type_id):
    return some_type_id == '7220'


def get_min_staff(staff_code):
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


def get_max_staff(staff_code):
    staff_codes = {
        '': None,
        'NN': 0,
        '00': 0,
        '01': 2,
        '02': 5,
        '03': 9,
        '11': 19,
        '12': 49,
        '21': 99,
        '22': 199,
        '31': 249,
        '32': 499,
        '41': 999,
        '42': 1999,
        '51': 4999,
        '52': 9999,
        '53': None
    }
    return staff_codes[staff_code]


def staff_max_sum(a, b):
    if a is None or b is None:
        return None
    return a + b


def staff_max_min(a, b):
    if a is None:
        return b
    if b is None:
        return a
    return min(a, b)


print('INFO: Processing legal units file (~ 21M records).')
organizations = {}
with open(filename_legal_units, 'r', encoding='UTF-8') as input_file:
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
                name = cells[header['denominationUniteLegale']]
                org = Organization(code, name, type_id)
                org.min_staff_1 = get_min_staff(cells[header['trancheEffectifsUniteLegale']])
                org.max_staff_1 = get_max_staff(cells[header['trancheEffectifsUniteLegale']])
                org.activity_id = cells[header['activitePrincipaleUniteLegale']]
                organizations[code] = org
            index += 1
            if index % log_chunk_size == 0:
                if index >= 100 * log_chunk_size:
                    break
                print(index)

print('INFO: Preparing population by organization id.')
population_dict = {}
for i in range(populations.shape[0]):
    id = populations.at[i, 'id']
    value = populations.at[i, 'population']
    type_id = populations.at[i, 'legal_type_id']
    population_dict[type_id + '|' + id] = int(value)

print('INFO: Processing sites file (~ 29M records).')
with open(filename_establishments, encoding='UTF-8') as input_file:
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
                org = organizations[code]
                if cells[header['etatAdministratifEtablissement']] == 'A':
                    org.active = True
                    org.min_staff_2 = org.min_staff_2 + get_min_staff(cells[header['trancheEffectifsEtablissement']])
                    org.max_staff_2 = staff_max_sum(org.max_staff_2, get_max_staff(cells[header['trancheEffectifsEtablissement']]))
                if cells[header['etablissementSiege']] == 'true':
                    city_id = cells[header['codeCommuneEtablissement']]
                    if len(city_id) != 5:
                        city_id = None
                    if (city_id is not None) and (cells[header['etatAdministratifEtablissement']] == 'A' or org.city_id is None):
                        org.city_id = city_id
                        if is_population_based(org.type_id):
                            if is_department(org.type_id):
                                department_code = city_id[:3] if city_id.startswith('97') else city_id[:2]
                                pop_id = org.type_id + '|' + department_code
                            elif is_city(org.type_id):
                                # For Lyon and Marseille, redirect city hall code to city code
                                if city_id == '69381':
                                    city_id = '69123'
                                if city_id == '13202':
                                    city_id = '13055'
                                pop_id = org.type_id + '|' + city_id
                            else:
                                pop_id = org.type_id + '|' + org.id
                            if pop_id in population_dict:
                                org.population = population_dict[pop_id]
                organizations[code] = org
            index += 1
            if index % log_chunk_size == 0:
                if index >= 100 * log_chunk_size:
                    break
                print(index)

# SIREN codes for 6 cities part of the "Zone Rouge" in Meuse departement, with 0 population
zone_rouge = ['215502394', '215500398', '215500505', '215503079', '215501891', '215501396']
# SIREN codes of city groups which are closed, but have not yet been removed from the SIRENE database
old_groups = [
    '200097673', # Weird case of "La société publique des écoles marseillaises", which we exclude
    '229840004', # Weird case of "Terres australes et antarctiques françaises", which we exclude
    '242010098'  # Case of "Communauté de communes de la côte de nacres", which is now closed
]

manual_populations_csv = pd.read_csv(data_path + 'manual_populations.csv', encoding='UTF-8', dtype=str)
manual_populations_dict = {}
for i in range(manual_populations_csv.shape[0]):
    id = manual_populations_csv.at[i, 'organization_id']
    value = manual_populations_csv.at[i, 'population']
    manual_populations_dict[id] = int(value)

all = organizations.values()
organizations = []
for org in all:
    overseas = ['975', '977', '978', '984', '986', '987', '988', '989']
    keep = True
    if (org.id in zone_rouge) or (org.id in old_groups):
        keep = False
    if not org.active:
        keep = False
    # Exclude overseas-based organizations
    for code in overseas:
        if org.city_id is not None and org.city_id.startswith(code):
            keep = False
    # Use manual populations if provided
    if org.id in manual_populations_dict:
        org.population = manual_populations_dict[org.id]
    if keep:
        organizations.append(org)
        if is_population_based(org.type_id) and org.population == 0:
            print('WARNING: No population found for ' + str(org.id))

# Determine regulation
for org in organizations:
    if is_private(org.type_id):
        if org.city_id is not None and (not org.city_id.startswith('97')) and (max(org.min_staff_1, org.min_staff_2) >= 500):
            org.regulation = 1
        if org.city_id is not None and (org.city_id.startswith('97')) and (max(org.min_staff_1, org.min_staff_2) >= 250):
            org.regulation = 2
    else:
        if org.type_id.startswith('71'):
            # City is not defined for state services that are installed abroad (e.g. ambassies in foreign countries)
            if org.city_id is not None:
                org.regulation = 3
        elif is_population_based(org.type_id):
            if org.population >= 50000:
                org.regulation = 4
        elif max(org.min_staff_1, org.min_staff_2) >= 250:
            org.regulation = 5

with open(output_path + 'organizations.csv', 'w', encoding='UTF-8') as file:
    file.write('id,name,min_staff,max_staff,population,city_id,legal_type_id,regulation,activity_id\n')
    for org in organizations:
        ms = staff_max_min(org.max_staff_1, org.max_staff_2)
        ms = '' if ms is None else str(ms)
        regulation = '' if org.regulation is None else str(org.regulation)
        file.write('%s,"%s",%d,%s,%d,%s,%s,%s,%s\n' % (org.id, org.name.replace('"', '""'),
                                                 max(org.min_staff_1, org.min_staff_2), ms,
                                                 org.population, org.city_id, org.type_id, regulation, org.activity_id))
