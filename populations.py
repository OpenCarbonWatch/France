import os
import pandas as pd

# Directories

input_path = '../data/INSEE/'
output_path = '../data/output/'

if not os.path.exists(output_path):
    os.mkdir(output_path)

filename_populations = input_path + 'ensemble.xls'
filename_compositions = input_path + 'Intercommunalité - Métropole au 01-01-2019.xls'

# See the page https://www.ecologique-solidaire.gouv.fr/actions-des-entreprises-et-des-collectivites-climat
# which clearly states that the legal population to be taken into account is the total one.

pop_field = 'Population totale'

# Legal unit types, as in https://www.insee.fr/fr/information/2028129

LEGAL_UNIT_TYPE_CITY = '7210'
LEGAL_UNIT_TYPE_DEPARTMENT = '7220'
LEGAL_UNIT_TYPE_OTHER_TERRITORIAL_COLLECTIVITY = '7229'
LEGAL_UNIT_TYPE_REGION = '7230'
LEGAL_UNIT_TYPE_CITY_GROUP = {'CA': '7348', 'CC': '7346', 'CU': '7343', 'ME': '7344'}

# Load data

cities_main = pd.read_excel(filename_populations, sheetname='Communes', skiprows=7, converters={col: str for col in range(10)})
cities_main = cities_main[['Code département', 'Code commune', pop_field]]
cities_mayotte = pd.read_csv('mayotte_2017.csv', encoding='UTF-8', dtype='str')
cities_mayotte = cities_mayotte[['Code département', 'Code commune', pop_field]]
cities = cities_main.append(cities_mayotte, ignore_index=True)
cities = cities.rename(columns={pop_field: 'population'})
cities['population'] = pd.to_numeric(cities['population'])
# Keep only 2 digits (overseas have 3 digits, the last one being in common with the first digit of city code)
cities['id'] = cities['Code département'].str.slice(stop=2) + cities['Code commune']

# Lyon, Marseille and Paris are split by "arrondissements", so we have to compute their total population by summing
# other the codes of their parts. We associate the total population to the code of the city.

cities['id'].replace(regex={
    '132((0[1-9])|(1[0-6]))': '13055',
    '6938[1-9]': '69123',
    '75[0-9]{3}': '75056'
    }, inplace=True)
cities = cities.groupby(['id'])['population'].sum().reset_index()
cities['legal_unit_type_id'] = LEGAL_UNIT_TYPE_CITY

# Departments

departments = cities.copy()
departments['id'] = departments['id'].map(lambda x: x[:3] if x.startswith('97') else x[:2])
departments = departments.groupby(['id'])['population'].sum().reset_index()
departments['legal_unit_type_id'] = LEGAL_UNIT_TYPE_DEPARTMENT

# Regions

regions = pd.read_excel(filename_populations, sheetname='Régions', skiprows=7, converters={col: str for col in range(7)})
regions = regions[['Code région', pop_field]]
regions_codes = pd.read_csv('regions_siren.csv', encoding='UTF-8', dtype=str)
regions = regions.merge(regions_codes, how='left', on='Code région')
regions = regions.rename(columns={'SIREN': 'id', pop_field: 'population'})
regions = regions[['id', 'population']]
regions['legal_unit_type_id'] = LEGAL_UNIT_TYPE_REGION

# Gather all populations

populations = cities.append(departments, ignore_index=True)
populations = populations.append(regions, ignore_index=True)
populations['legal_unit_type_id'][populations['id'] == '200055507'] = LEGAL_UNIT_TYPE_OTHER_TERRITORIAL_COLLECTIVITY
populations['legal_unit_type_id'][populations['id'] == '200076958'] = LEGAL_UNIT_TYPE_OTHER_TERRITORIAL_COLLECTIVITY
populations['legal_unit_type_id'][populations['id'] == '200052678'] = LEGAL_UNIT_TYPE_OTHER_TERRITORIAL_COLLECTIVITY
populations['legal_unit_type_id'][populations['id'] == '75056'] = LEGAL_UNIT_TYPE_OTHER_TERRITORIAL_COLLECTIVITY
populations['id'][populations['id'] == '75056'] = '217500016'

# Compute large city groups

groups = pd.read_excel(filename_compositions, sheetname='EPCI', skiprows=5, converters={col: str for col in range(4)})
groups = groups[groups['NATURE_EPCI'] != 'ZZ'].copy()
groups['id'] = groups['EPCI']
groups['legal_unit_type_id'] = groups['NATURE_EPCI'].map(lambda x: LEGAL_UNIT_TYPE_CITY_GROUP[x])
groups['legal_unit_type_id'][groups['id'] == '200046977'] = LEGAL_UNIT_TYPE_OTHER_TERRITORIAL_COLLECTIVITY  # Lyon has a special status
groups['legal_unit_type_id'][groups['id'] == '242500361'] = LEGAL_UNIT_TYPE_CITY_GROUP['CU']  # "Grand Besançon" was a CA, became CU on 2019-07-01

compositions = pd.read_excel(filename_compositions, sheetname='Composition_communale', skiprows=5, converters={col: str for col in range(6)})
compositions = compositions.merge(cities, how='left', left_on='CODGEO', right_on='id')
compositions = compositions.groupby(['EPCI'])['population'].sum().reset_index()
compositions = compositions.rename({'EPCI': 'id'})
groups = groups.merge(compositions, how='left')

# Save all populations

populations = populations.append(groups, ignore_index=True)
populations = populations[['legal_unit_type_id', 'id', 'population']]
populations.to_csv(output_path + 'populations.csv', index=False, encoding='UTF-8')
