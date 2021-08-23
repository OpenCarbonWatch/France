import os
import pandas as pd

# Directories

data_path = '../data/'
input_path = '../input/'
output_path = '../output/'

if not os.path.exists(output_path):
    os.mkdir(output_path)

filename_populations = input_path + 'INSEE/ensemble.xls'
filename_compositions = input_path + 'INSEE/Intercommunalite-Metropole_au_01-01-2021.xlsx'

# See the page https://www.ecologique-solidaire.gouv.fr/actions-des-entreprises-et-des-collectivites-climat
# which clearly states that the legal population to be taken into account is the total one.

pop_field = 'Population totale'

# Legal unit types, as in https://www.insee.fr/fr/information/2028129

LEGAL_TYPE_CITY = '7210'
LEGAL_TYPE_DEPARTMENT = '7220'
LEGAL_TYPE_OTHER_TERRITORIAL_COLLECTIVITY = '7229'
LEGAL_TYPE_REGION = '7230'
LEGAL_TYPE_CITY_GROUP = {'CA': '7348', 'CC': '7346', 'CU': '7343', 'ME': '7344'}

# Load data

cities_main = pd.read_excel(filename_populations, sheet_name='Communes', skiprows=7, converters={col: str for col in range(10)})
cities_main = cities_main[['Code département', 'Code commune', 'Nom de la commune', 'Nom de la région', pop_field]]
cities_mayotte = pd.read_csv(data_path + 'mayotte_2017.csv', encoding='UTF-8', dtype='str')
cities_mayotte = cities_mayotte[['Code département', 'Code commune', 'Nom de la commune', 'Nom de la région', pop_field]]
cities = cities_main.append(cities_mayotte, ignore_index=True)
cities = cities.rename(columns={pop_field: 'population'})
cities['population'] = pd.to_numeric(cities['population'])
# Keep only 2 digits (overseas have 3 digits, the last one being in common with the first digit of city code)
cities['id'] = cities['Code département'].str.slice(stop=2) + cities['Code commune']

department_names = pd.read_excel(filename_populations, sheet_name='Départements', skiprows=7, converters={col: str for col in range(9)})
department_names = department_names[['Code département', 'Nom du département']].copy()
department_names.loc[department_names.shape[1]] = ['976', 'Mayotte']
output_cities = cities.merge(department_names)
output_cities = output_cities.rename(columns={'Nom de la commune': 'city_name', 'Nom de la région': 'region_name', 'Nom du département': 'department_name'})
output_cities = output_cities[['id', 'city_name', 'department_name', 'region_name']]
output_cities.to_csv(output_path + 'cities.csv', index=False, encoding='UTF-8')

# Lyon, Marseille and Paris are split by "arrondissements", so we have to compute their total population by summing
# other the codes of their parts. We associate the total population to the code of the city.

cities['id'].replace(regex={
    '132((0[1-9])|(1[0-6]))': '13055',
    '6938[1-9]': '69123',
    '75[0-9]{3}': '75056'
    }, inplace=True)
cities = cities.groupby(['id'])['population'].sum().reset_index()
cities['legal_type_id'] = LEGAL_TYPE_CITY

# Departments

departments = cities.copy()
departments['id'] = departments['id'].map(lambda x: x[:3] if x.startswith('97') else x[:2])
departments = departments.groupby(['id'])['population'].sum().reset_index()
departments['legal_type_id'] = LEGAL_TYPE_DEPARTMENT

# Regions

regions = pd.read_excel(filename_populations, sheet_name='Régions', skiprows=7, converters={col: str for col in range(7)})
regions = regions[['Code région', pop_field]]
regions_codes = pd.read_csv(data_path + 'manual_regions_siren.csv', encoding='UTF-8', dtype=str)
regions = regions.merge(regions_codes, how='left', on='Code région')
regions = regions.rename(columns={'SIREN': 'id', pop_field: 'population'})
regions = regions[['id', 'population']]
regions['legal_type_id'] = LEGAL_TYPE_REGION

# Gather all populations

populations = cities.append(departments, ignore_index=True, sort=True)
populations = populations.append(regions, ignore_index=True, sort=True)
populations['legal_type_id'][populations['id'] == '200055507'] = LEGAL_TYPE_OTHER_TERRITORIAL_COLLECTIVITY
populations['legal_type_id'][populations['id'] == '200076958'] = LEGAL_TYPE_OTHER_TERRITORIAL_COLLECTIVITY
populations['legal_type_id'][populations['id'] == '200052678'] = LEGAL_TYPE_OTHER_TERRITORIAL_COLLECTIVITY
populations['legal_type_id'][populations['id'] == '976'] = LEGAL_TYPE_OTHER_TERRITORIAL_COLLECTIVITY
populations['id'][populations['id'] == '976'] = '229850003'
populations['legal_type_id'][populations['id'] == '75056'] = LEGAL_TYPE_OTHER_TERRITORIAL_COLLECTIVITY
populations['id'][populations['id'] == '75056'] = '217500016'

# Compute large city groups

groups = pd.read_excel(filename_compositions, sheet_name='EPCI', skiprows=5, converters={col: str for col in range(4)})
groups = groups[groups['NATURE_EPCI'] != 'ZZ'].copy()
groups['id'] = groups['EPCI']
groups['legal_type_id'] = groups['NATURE_EPCI'].map(lambda x: LEGAL_TYPE_CITY_GROUP[x])
groups['legal_type_id'][groups['id'] == '200046977'] = LEGAL_TYPE_OTHER_TERRITORIAL_COLLECTIVITY  # Lyon has a special status
groups['legal_type_id'][groups['id'] == '200060465'] = '7348' # Grand Nord de Mayotte changed on 2021-01-01 but change is not yet reflected in the composition file

compositions = pd.read_excel(filename_compositions, sheet_name='Composition_communale', skiprows=5, converters={col: str for col in range(6)})
compositions = compositions.merge(cities, how='left', left_on='CODGEO', right_on='id')
compositions = compositions.groupby(['EPCI'])['population'].sum().reset_index()
compositions = compositions.rename({'EPCI': 'id'})
groups = groups.merge(compositions, how='left')

# Save all populations

populations = populations.append(groups, ignore_index=True, sort=True)
populations = populations[['legal_type_id', 'id', 'population']]
populations['population'] = populations['population'].map(lambda x: str(int(x)))
populations.to_csv(output_path + 'populations.csv', index=False, encoding='UTF-8')
