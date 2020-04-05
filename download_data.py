import os
import requests
import shutil
import zipfile


data_path = './data/'
file_stock_etablissement = data_path + 'StockEtablissement.zip'
file_stock_unite_legale = data_path + 'StockUniteLegale.zip'
file_beges = data_path + 'BEGES/beges.zip'

def download_file(url, local_filename):
    with requests.get(url, stream=True) as r:
        with open(local_filename, 'wb') as f:
            shutil.copyfileobj(r.raw, f)


def unzip(zip_name, path):
    with zipfile.ZipFile(zip_name, 'r') as zip_ref:
        zip_ref.extractall(path)

if not os.path.exists(data_path + 'INSEE/'): 
	os.makedirs(data_path + 'INSEE/')
    
if not os.path.exists(data_path + 'BEGES/'):
    os.makedirs(data_path + 'BEGES/')

if not os.path.exists(file_stock_etablissement):
    download_file('http://files.data.gouv.fr/insee-sirene/StockEtablissement_utf8.zip', file_stock_etablissement)
    unzip(file_stock_etablissement, data_path)

if not os.path.exists(file_stock_unite_legale):
    download_file('http://files.data.gouv.fr/insee-sirene/StockUniteLegale_utf8.zip', file_stock_unite_legale)
    unzip(file_stock_unite_legale, data_path)

if not os.path.exists(file_beges):
    download_file('https://www.data.gouv.fr/fr/datasets/r/c90e1000-d51a-4e7a-9276-f613ea8afea9', file_beges)
    unzip(file_beges, data_path + 'BEGES/')

download_file('https://www.insee.fr/fr/statistiques/fichier/4265429/ensemble.xls', data_path + 'INSEE/ensemble.xls')
download_file('https://www.insee.fr/fr/statistiques/fichier/2510634/Intercommunalite-Metropole_au_01-01-2020.zip', data_path + 'INSEE/Intercommunalité - Métropole au 01-01-2020.zip')
unzip(data_path + 'INSEE/Intercommunalité - Métropole au 01-01-2020.zip', data_path + 'INSEE/')
download_file('https://www.data.gouv.fr/fr/datasets/r/7bb2184b-88cb-4c6c-a408-5a0081816dcd', data_path + 'INSEE/naf2008-listes-completes-5-niveaux.csv')
