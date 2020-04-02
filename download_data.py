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

if not os.path.exists(data_path): 
	os.mkdir(data_path)
    
if not os.path.exists(data_path + 'BEGES/'):
    os.mkdir(data_path + 'BEGES/')

if not os.path.exists(file_stock_etablissement):
    download_file('http://files.data.gouv.fr/insee-sirene/StockEtablissement_utf8.zip', file_stock_etablissement)
    unzip(file_stock_etablissement, data_path)

if not os.path.exists(file_stock_unite_legale):
    download_file('http://files.data.gouv.fr/insee-sirene/StockUniteLegale_utf8.zip', file_stock_unite_legale)
    unzip(file_stock_unite_legale, data_path)

if not os.path.exists(file_beges):
    download_file('https://www.data.gouv.fr/fr/datasets/r/c90e1000-d51a-4e7a-9276-f613ea8afea9', file_beges)
    unzip(file_beges, data_path + 'BEGES/')
