# myges-icalendar-website
Création de calendrier MyGES au format ICS avec interface web  

Le code est disponible publiquement, cependant une version publique est disponible sur ce lien :  
[https://ges-calendar.unbonwhisky.fr/](https://ges-calendar.unbonwhisky.fr/)

## Comment l'installer
1. Compiler les 2 Dockerfile disponibles dans les dossiers `website` et `api-python`  
  La commande à taper est `docker build --pull --rm -f "Dockerfile" -t myges-calendar:latest .` pour le website, et `docker build --pull --rm -f "Dockerfile" -t myges-calendar-python:latest .` pour le python

2. Lancer le compose situé dans le dossier `website` avec `docker compose up -d`

3. Ouvrir les ports ou gérer avec un reverse proxy pour accéder au site depuis l'extérieur. (optionnel)

## Informations complémentaires
Avec l'aide d'un professeur de l'ESGI, j'ai pu faire des tests et développer une version fonctionnelle pour les professeurs également. Coté API, un champs est vide pour les étudiants, mais présent (si renseigné) pour les professeurs.  

Cette version s'adresse donc à tous, étudiants comme professeurs.  

Je ne suis pas étudiant dans tous les campus du réseau GES donc il est possible que des erreurs soient présentes dans le code.  
Dans le cas où ça arriverait, merci de m'envoyer un mail avec un maximum d'infos à [contact@unbonwhisky.fr](mailto:contact@unbonwhisky.fr)