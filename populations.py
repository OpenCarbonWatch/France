import os
import pandas as pd

# See https://www.ecologique-solidaire.gouv.fr/actions-des-entreprises-et-des-collectivites-climat
pop_field = 'Population totale'
pop_threshold = 50000

# Directories
input_path = '../data/INSEE/'
output_path = '../data/output/'

# Load data
populations_main = pd.read_csv(input_path + 'Communes.csv', encoding='UTF-8', dtype='str')
populations_main = populations_main[['Code département', 'Code commune', pop_field]]
populations_mayotte = pd.read_csv('mayotte_2017.csv', encoding='UTF-8', dtype='str')
populations_mayotte = populations_mayotte[['Code département', 'Code commune', pop_field]]
populations = populations_main.append(populations_mayotte, ignore_index=True)
compositions = pd.read_csv(input_path + 'Composition_communale.csv', encoding='UTF-8')

if not os.path.exists(output_path):
    os.mkdir(output_path)

# Compute large cities
populations['CODGEO'] = ''
for i in range(populations.shape[0]):
    # Keep only 2 digits (beware of overseas which have 3 digits...)
    populations.at[i, 'CODGEO'] = populations.at[i, 'Code département'][:2] + populations.at[i, 'Code commune']
populations[pop_field] = pd.to_numeric(populations[pop_field])
large_cities = populations[populations[pop_field] >= pop_threshold]
large_cities = large_cities[['CODGEO']]
large_cities.to_csv(output_path + 'large_cities.csv', index=False, encoding='UTF-8')

# Compute large city groups
compositions = compositions.merge(populations, how='left', left_on='CODGEO', right_on='CODGEO')
city_groups = compositions.groupby(['EPCI'])[pop_field].sum().reset_index()
large_groups = city_groups[city_groups[pop_field] >= pop_threshold]
large_groups = large_groups[['EPCI']]
large_groups.to_csv(output_path + 'large_groups.csv', index=False, encoding='UTF-8')

