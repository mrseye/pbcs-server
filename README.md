# Oracle PBCS API Server

Serveur FastAPI local pour interagir avec Oracle Planning & Budgeting Cloud (PBCS).

## Installation

```bash
cd C:\Users\sseye\pbcs-server

# Créer un environnement virtuel
python -m venv .venv
.venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt
```

## Configuration

Éditez le fichier `.env` avec vos identifiants Oracle :

```env
ORACLE_HOST=your-instance.pbcs.oraclecloud.com
ORACLE_USERNAME=your.email@company.com
ORACLE_PASSWORD=your_password
ORACLE_APP=your_application_name
```

## Démarrage

```bash
uvicorn main:app --reload
```

Le serveur démarre sur `http://localhost:8000`.

## Utilisation depuis VS Code

### Option 1 : Swagger UI (recommandé pour débuter)
Ouvrez `http://localhost:8000/docs` dans votre navigateur.

### Option 2 : REST Client (VS Code)
1. Installez l'extension **REST Client** (Huachao Mao)
2. Ouvrez le fichier `pbcs-api.http`
3. Cliquez sur **"Send Request"** au-dessus de chaque requête

## Endpoints disponibles

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/` | Infos du serveur |
| GET | `/jobs` | Lister les jobs récents |
| GET | `/jobs/{id}` | Statut d'un job |
| GET | `/jobs/{id}/wait` | Attendre la fin d'un job |
| POST | `/rules/run` | Lancer une règle métier |
| POST | `/rules/ruleset/run` | Lancer un ruleset |
| POST | `/data/import` | Importer des données |
| POST | `/data/export` | Exporter des données |
| POST | `/metadata/import` | Importer des métadonnées |
| POST | `/metadata/export` | Exporter des métadonnées |
| POST | `/metadata/cube/refresh` | Rafraîchir le cube |
| GET | `/files` | Lister les fichiers Oracle |
| POST | `/files/upload` | Uploader un fichier |
| GET | `/files/download/{nom}` | Télécharger un fichier |

## Workflow typique : Chargement de données

```
1. POST /files/upload        → Uploader votre CSV dans l'inbox Oracle
2. POST /data/import         → Lancer le job d'import (avec wait=true)
3. GET  /jobs/{jobId}        → Vérifier le statut si wait=false
```

## Workflow typique : Lancer un calcul

```
1. POST /rules/run           → Lancer la règle (avec wait=true pour attendre)
2. GET  /jobs/{jobId}        → Consulter les logs si besoin
```
