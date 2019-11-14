## France

## Mode d'emploi

### Calcul des populations légales

* Créer un dossier `data/INSEE` avec

  * un fichier `Intercommunalité - Métropole au 01-01-2019.xls` reprenant la composition des intercommunalités au 2019-01-01
fournie par l'INSEE et téléchargé depuis
https://www.insee.fr/fr/statistiques/fichier/2510634/Intercommunalite-Metropole_au_01-01-2019.zip

  * un fichier `ensemble.xls` reprenant les populations légales 2016 de l'INSEE, téléchargé depuis
https://www.insee.fr/fr/statistiques/fichier/3677785/ensemble.xls

Le fichier `mayotte_2017.csv` a été construit à partir des données de populations légales 2017 de Mayotte produites par
l'INSEE et disponibles sur la page https://www.insee.fr/fr/statistiques/3291775.

Le fichier `regions_siren.csv` a été construit manuellement. Il donne la correspondance entre les codes des régions et
le numéro SIREN de la personne morale associée.

* Exécuter le script `populations.py`, qui construit un fichier `output/populations.csv` avec les populations légales
des régions, départements, communes, intercommunalités et autres collectivités territoriales.

### Liste des personnes morales

* Créer un dossier `data/SIRENE`avec les fichiers CSV issus de
https://www.data.gouv.fr/fr/datasets/base-sirene-des-entreprises-et-de-leurs-etablissements-siren-siret/

