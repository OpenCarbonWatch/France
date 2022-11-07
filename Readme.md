# Données en France

Ce dépôt contient des codes **Python** permettant de consolider les données sur les organisations et leurs bilans d'émissions de gaz à effet de serre pour la France. Des travaux sur d'autres pays pourront être entrepris par la suite.

Les données consolidées proviennent essentiellement de l'INSEE, pour la liste des personnes morales (entreprises, collectivités, services de l'état, associations) et leurs caractéristiques, et de l'ADEME, pour les bilans d'émissions publiés par les organisations.

Les données consolidées sont ensuite utilisées dans la section France de notre site : https://opencarbonwatch.org/fr/france.

## Comment aider ?

Les contributions pour intégrer de nouvelles données pertinentes sont les bienvenues. Quelques propositions d'améliorations sont décrites dans les tickets déjà créés. Ne pas hésiter à en créer de nouveaux pour lancer les discussions.

## Mode d'emploi

### Téléchargements automatisés

Exécuter le script `download_data.py` . Celui-ci crée un sous-dossier `input` dans lequel il télécharge les fichiers déjà disponibles publiquement en *open data* sur des sites de référence :
* les unités légales et les établissements de la [base Sirene](https://www.data.gouv.fr/fr/datasets/base-sirene-des-entreprises-et-de-leurs-etablissements-siren-siret/) de l'INSEE,
* la [composition des intercommunalités](https://www.insee.fr/fr/information/2510634) consolidée l'INSEE,
* les [populations légales par commune](https://www.insee.fr/fr/statistiques/6011070?sommaire=6011075) établies par l'INSEE,
* la [nomenclature d'activités française (NAF)](https://www.data.gouv.fr/fr/datasets/r/7bb2184b-88cb-4c6c-a408-5a0081816dcd),
* les [bilans d'émissions de gaz à effet de serre](https://www.data.gouv.fr/fr/datasets/bilans-demissions-de-ges-publies-sur-le-site-de-lademe-1/) publiés via l'ADEME.

### Consolidation

* Exécuter le script `find_populations.py` qui construit un fichier `output/populations.csv` avec les populations légales des régions, départements, communes, intercommunalités et autres collectivités territoriales. Ces populations sont utilisées pour déterminer les collectivités territoriales concernées par l'obligation de réaliser et publier leur bilan.
* Exécuter le script `curate_organizations.py` qui construit un fichier `output/organizations.csv` avec les données sur les personnes morales nécessaires à la suite du traitement.
* Exécuter le script `collate_assessments.py` qui consolide les bilans publiés.

## Notes sur les données fait-maison embarquées

Le dossier `/data/` contient des données fait-maison embarquées avec le code source.

Le fichier `manual_assessment_organization.csv` a été construit manuellement. Il donne les liens entre un numéro de bilan d'émissions (identifiant sur le site de l'ADEME) et un numéro SIREN de l'organisation à laquelle il correspond. C'est un travail conséquent (environ 300 correspondances) qui provient d'une interprétation reposant sur le nom de l'entité ayant soumis le bilan. Il peut contenir des erreurs (ouvrir un ticket pour nous l'indiquer). Sur la plateforme de l'ADEME, la saisie d'un numéro SIREN n'est notamment pas obligatoire pour les services de l'Etat, qui sont donc sur-représentés dans ce fichier.

Le fichier `manual_populations.csv` a été construit manuellement. Il donne les populations pour les collectivités territoriales qui ont été créées récemment et ne figurent pas encore dans les fichiers consolidés de l'INSEE. Les données ont été trouvées sur Wikipédia.

Le fichier `manual_regions_siren.csv` a été construit manuellement. Il donne la correspondance entre les codes des régions et le numéro SIREN de la personne morale associée. Les données ont été trouvées sur Wikipédia.

Le fichier `mayotte_2017.csv` a été construit à partir des données de populations légales 2017 de Mayotte produites par l'INSEE et disponibles sur la page https://www.insee.fr/fr/statistiques/3291775.
