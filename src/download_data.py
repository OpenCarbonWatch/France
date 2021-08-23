import os
import requests
import shutil
import zipfile


input_path = '../input/'
file_stock_etablissement = input_path + 'StockEtablissement.zip'
file_stock_unite_legale = input_path + 'StockUniteLegale.zip'
file_beges = input_path + 'BEGES/beges.zip'

def download_file(url, local_filename):
    with requests.get(url, stream=True) as r:
        with open(local_filename, 'wb') as f:
            shutil.copyfileobj(r.raw, f)


def unzip(zip_name, path):
    with zipfile.ZipFile(zip_name, 'r') as zip_ref:
        zip_ref.extractall(path)

if not os.path.exists(input_path + 'INSEE/'): 
	os.makedirs(input_path + 'INSEE/')
    
if not os.path.exists(input_path + 'BEGES/'):
    os.makedirs(input_path + 'BEGES/')

if not os.path.exists(file_stock_etablissement):
    download_file('http://files.data.gouv.fr/insee-sirene/StockEtablissement_utf8.zip', file_stock_etablissement)
    unzip(file_stock_etablissement, input_path)

if not os.path.exists(file_stock_unite_legale):
    download_file('http://files.data.gouv.fr/insee-sirene/StockUniteLegale_utf8.zip', file_stock_unite_legale)
    unzip(file_stock_unite_legale, input_path)

if not os.path.exists(file_beges):
    download_file('https://www.data.gouv.fr/fr/datasets/r/c90e1000-d51a-4e7a-9276-f613ea8afea9', file_beges)
    unzip(file_beges, input_path + 'BEGES/')

download_file('https://www.insee.fr/fr/statistiques/fichier/4989724/ensemble.xlsx', input_path + 'INSEE/ensemble.xls')
download_file('https://www.insee.fr/fr/statistiques/fichier/2510634/Intercommunalite_Metropole_au_01-01-2021.zip', input_path + 'INSEE/Intercommunalite-Metropole_au_01-01-2021.zip')
unzip(input_path + 'INSEE/Intercommunalite-Metropole_au_01-01-2021.zip', input_path + 'INSEE/')
download_file('https://www.data.gouv.fr/fr/datasets/r/7bb2184b-88cb-4c6c-a408-5a0081816dcd', input_path + 'INSEE/naf2008-listes-completes-5-niveaux.csv')
