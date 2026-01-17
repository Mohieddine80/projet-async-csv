# Projet – Traitement Asynchrone de Fichiers CSV

Mohieddine Hamoudi – Dev 1.2

---

## Description du projet

Application web permettant le traitement asynchrone de fichiers CSV volumineux
(jusqu’à 100 000 lignes et plus), avec :

- Détection automatique des doublons
- Suivi en temps réel de la progression
- Gestion des erreurs côté serveur et côté utilisateur

---

## Architecture technique

### Stack technologique

- Frontend : HTML, CSS, JavaScript
- Backend de traitement : Python 3.14, Flask, Flask-SocketIO
- API Backend : C# (.NET 8.0), ASP.NET Core
- Base de données : MongoDB (NoSQL)
- Conteneurisation : Docker, Docker Compose
- Communication temps réel : WebSocket (Socket.IO)

---

### Schéma d’architecture



┌─────────────┐      ┌──────────────┐      ┌─────────────┐      ┌──────────┐
│  Frontend   │─────▶│ Flask Service│─────▶│  API C#     │─────▶│ MongoDB  │
│  (Nginx)    │      │   (Python)   │      │  (.NET 8)   │      │ (NoSQL)  │
│  Port 8000  │      │   Port 5000  │      │  Port 5001  │      │Port 27017│
└─────────────┘      └──────────────┘      └─────────────┘      └──────────┘


---

## Fonctionnalités principales

### 1. Upload et traitement de CSV

- Support de fichiers CSV jusqu’à 100 000+ lignes
- Détection automatique du séparateur (`;` ou `,`)
- Traitement asynchrone ligne par ligne

---

### 2. Détection des doublons

- Identification unique basée sur un hash MD5 de l’ensemble des colonnes
- Vérification via index unique MongoDB
- Insertion conditionnelle (ligne ignorée si doublon détecté)

---

### 3. Suivi en temps réel

- Barre de progression dynamique via WebSocket
- Affichage du pourcentage de traitement
- Compteurs en direct :
  - Lignes totales
  - Lignes insérées
  - Lignes ignorées (doublons)

---

### 4. Gestion des erreurs

- Système de retry automatique (3 tentatives par ligne)
- Logs détaillés côté serveur
- Messages d’erreur clairs côté utilisateur

---

## Tests et validation

### Scénarios testés

- Gros fichiers CSV
- Fichiers avec doublons
- Séparateurs mixtes (`;` dans l’en-tête, `,` dans les données)
- Arrêt et relance pendant le traitement
- Fichiers corrompus avec gestion d’erreurs

---

## Installation et lancement

### Prérequis

- Docker Desktop installé et démarré
- Minimum 4 Go de RAM disponible
- Ports libres : 8000, 5000, 5001, 27017

---

## Comment lancer le projet

1. S’assurer que Docker Desktop est lancé
2. Ouvrir un terminal à la racine du projet
3. Lancer la commande suivante :

docker-compose up --build

5. Accéder à l'interface : http://localhost:8000
6. Sélectionner un fichier CSV : Glisser-déposer ou cliquer pour parcourir
7. Lancer le traitement : Cliquer sur "Lancer le traitement"

Observer la progression : Barre de progression + statistiques en temps réel
Résultat : Message de confirmation une fois terminé