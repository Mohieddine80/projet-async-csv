Mohieddine Hamoudi Dev1.2


# Projet Traitement CSV Asynchrone 

Ce projet permet d'uploader un fichier CSV et de l'insérer en base de données de manière asynchrone avec suivi en temps réel.

## Architecture
- **Frontend** : HTML/JS (Port 3000)
- **Backend Traitement** : Python Flask (Port 5000)
- **Backend BDD** : C# .NET 8 API (Port 8080)
- **Base de données** : MongoDB (Port 27017)

##  Comment lancer le projet
1. S'assurer que Docker Desktop est lancé.
2. Ouvrir un terminal dans ce dossier.
3. Lancer la commande :
   docker-compose up --build
4.   Attendre quelques minutes.

5. Ouvrir le navigateur sur : http://localhost:3000