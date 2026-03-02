# Oracle PBCS API Server

Serveur **FastAPI** local faisant passerelle entre vos outils (VS Code, scripts Python, Power Automate…) et l'API REST Oracle Planning & Budgeting Cloud (PBCS / EPM Cloud).

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        VOS OUTILS                               │
│                                                                 │
│   VS Code REST Client   │   Swagger UI   │   Script Python      │
│   (pbcs-api.http)       │   /docs        │   curl / requests    │
└───────────────┬─────────────────┬────────────────┬─────────────┘
                │                 │                │
                │    HTTP / JSON  │                │
                ▼                 ▼                ▼
┌─────────────────────────────────────────────────────────────────┐
│              SERVEUR LOCAL  FastAPI  (port 8000)                │
│                                                                 │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐  │
│  │  /jobs   │ │  /rules  │ │  /data   │ │   /applications  │  │
│  │          │ │          │ │          │ │   /metadata      │  │
│  │  /files  │ │ /health  │ │          │ │                  │  │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────────┬─────────┘  │
│       │            │            │                 │             │
│       └────────────┴────────────┴─────────────────┘            │
│                              │                                  │
│                    ┌─────────▼──────────┐                      │
│                    │    PBCSClient      │                      │
│                    │  (pbcs/client.py)  │                      │
│                    │   httpx + Basic    │                      │
│                    │   Auth             │                      │
│                    └─────────┬──────────┘                      │
└──────────────────────────────┼──────────────────────────────────┘
                               │  HTTPS + Basic Auth
                               │
                ┌──────────────▼──────────────────┐
                │       ORACLE EPM CLOUD           │
                │                                  │
                │  ┌────────────────────────────┐  │
                │  │  Planning REST API v3      │  │
                │  │  /HyperionPlanning/rest/v3 │  │
                │  │                            │  │
                │  │  • Applications & Cubes    │  │
                │  │  • Dimensions & Membres    │  │
                │  │  • Jobs (règles, imports)  │  │
                │  └────────────────────────────┘  │
                │  ┌────────────────────────────┐  │
                │  │  Interop REST API          │  │
                │  │  /interop/rest/11.x        │  │
                │  │                            │  │
                │  │  • Inbox / Outbox (fichiers│  │
                │  └────────────────────────────┘  │
                └──────────────────────────────────┘
```

---

## Prérequis

- **Python 3.11+**
- Un environnement **Oracle EPM Cloud / PBCS** accessible
- Un compte Oracle avec droits sur l'application cible

---

## Installation

```bash
# 1. Cloner le dépôt
git clone https://github.com/mrseye/pbcs-server.git
cd pbcs-server

# 2. Créer l'environnement virtuel
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux

# 3. Installer les dépendances
pip install -r requirements.txt
```

---

## Configuration

Copiez le fichier modèle et renseignez vos identifiants Oracle :

```bash
cp .env.example .env
```

Éditez `.env` :

```env
ORACLE_HOST=votre-instance.epm.region.ocs.oraclecloud.com
ORACLE_USERNAME=votre_utilisateur
ORACLE_PASSWORD="votre_mot_de_passe"
ORACLE_APP=NOM_APPLICATION

# Optionnel (valeurs par défaut)
API_VERSION=v3
INTEROP_VERSION=11.1.2.3.600
```

> **Sécurité** : le fichier `.env` est dans `.gitignore` et ne sera jamais commité.

---

## Démarrage

```bash
uvicorn main:app --reload
```

Le serveur démarre sur `http://localhost:8000`.

Au lancement, les informations de connexion s'affichent :

```
Oracle PBCS Server démarré
  Host    : votre-instance.epm.region.ocs.oraclecloud.com
  App     : NOM_APPLICATION
  API     : https://...
  Docs    : http://localhost:8000/docs
```

---

## Tester la connexion

Avant toute chose, vérifiez que la connexion à Oracle est établie :

```
GET http://localhost:8000/health
```

Réponse attendue (tout OK) :

```json
{
  "status": "ok",
  "checks": {
    "dns":   { "ok": true, "ip": "147.x.x.x" },
    "https": { "ok": true, "http_status": 401 },
    "auth":  { "ok": true, "applications": ["MON_APP"] }
  }
}
```

---

## Utilisation depuis VS Code

### Option 1 — REST Client (recommandé)

1. Installez l'extension **REST Client** (Huachao Mao)
2. Ouvrez `pbcs-api.http`
3. Cliquez **Send Request** au-dessus de chaque requête

### Option 2 — Swagger UI

Ouvrez `http://localhost:8000/docs` dans votre navigateur.

---

## Référence API

### Info & Diagnostic

| Méthode | Endpoint  | Description |
|---------|-----------|-------------|
| `GET`   | `/`       | Informations sur le serveur et liste des endpoints |
| `GET`   | `/health` | Diagnostic de connexion Oracle (DNS + HTTPS + Auth) |

---

### Applications & Structure

> Découvrez la structure de votre environnement Oracle.

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/applications` | Liste toutes les applications PBCS accessibles |
| `GET` | `/applications/{app}/cubes` | Liste les cubes (BSO/ASO) d'une application |
| `GET` | `/applications/dimensions` | Liste les dimensions de l'application configurée |
| `GET` | `/applications/dimensions/{dim}/members` | Liste les membres d'une dimension |

**Paramètres membres :**

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `parent`  | string | — | Filtre les enfants directs d'un membre |
| `limit`   | int  | 100    | Nombre max de membres (max 1000) |

**Exemple :**
```
GET /applications/dimensions/Entity/members?parent=TotalEntity&limit=50
```

---

### Jobs

> Suivez l'exécution de tous les jobs Oracle en temps réel.

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/jobs` | Liste les jobs récents (`?limit=50`) |
| `GET` | `/jobs/{id}` | Statut et détails d'un job |
| `GET` | `/jobs/{id}/wait` | Attend la fin d'un job (polling) |

**Statuts Oracle :**

| Code | Label |
|------|-------|
| `-1` | En cours |
| `0`  | Succès |
| `1`  | Erreur |
| `2`  | Annulé |
| `3`  | Application invalide |

---

### Règles métier

> Lancez des règles de calcul et des rulesets.

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `POST` | `/rules/run` | Lance une règle métier |
| `POST` | `/rules/ruleset/run` | Lance un ruleset |

**Corps de la requête :**

```json
{
  "rule_name": "Calculate_FY2025",
  "parameters": {
    "Scenario": "Budget",
    "Year": "FY2025"
  },
  "wait": true,
  "timeout": 300
}
```

| Champ | Type | Défaut | Description |
|-------|------|--------|-------------|
| `rule_name` | string | *requis* | Nom exact de la règle dans PBCS |
| `parameters` | object | `null` | Variables de substitution |
| `wait` | bool | `false` | Attendre la fin avant de répondre |
| `poll_interval` | float | `5.0` | Intervalle de polling (secondes) |
| `timeout` | float | `600.0` | Timeout max (secondes) |

---

### Données

> Importez et exportez des données via les jobs PBCS.

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `POST` | `/data/import` | Lance un job d'import de données |
| `POST` | `/data/export` | Lance un job d'export de données |

**Import :**
```json
{
  "job_name": "Load_Actuals",
  "import_file": "actuals_jan2025.csv",
  "clear_data": false,
  "wait": true
}
```

**Export :**
```json
{
  "job_name": "Export_Budget",
  "export_file": "budget_export.csv",
  "wait": true
}
```

---

### Métadonnées

> Gérez les dimensions et membres via les jobs PBCS.

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `POST` | `/metadata/import` | Import de métadonnées (dimensions, membres) |
| `POST` | `/metadata/export` | Export de métadonnées |
| `POST` | `/metadata/cube/refresh` | Rafraîchit le cube (recalcul agrégations) |

**Import métadonnées :**
```json
{
  "job_name": "Import_Entity_Members",
  "import_file": "entity_2025.csv",
  "dimension": "Entity",
  "wait": true
}
```

---

### Fichiers (Inbox / Outbox)

> Gérez les fichiers dans l'espace de stockage Oracle.

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET`  | `/files` | Liste les fichiers disponibles |
| `POST` | `/files/upload` | Uploade un fichier dans l'inbox Oracle |
| `GET`  | `/files/download/{filename}` | Télécharge un fichier depuis l'outbox |

> Pour l'upload, utilisez **Swagger UI** (`/docs`) qui propose un formulaire de sélection de fichier.

---

## Workflows typiques

### Chargement de données

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  1. POST /files/upload                                  │
│     → Déposer votre CSV dans l'inbox Oracle             │
│                                                         │
│  2. POST /data/import  { "wait": true }                 │
│     → Lancer le job d'import et attendre la fin         │
│                                                         │
│  3. GET /jobs/{jobId}                                   │
│     → Consulter les détails si une erreur est survenue  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Export de données

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  1. POST /data/export  { "wait": true }                 │
│     → Lancer le job d'export et attendre la fin         │
│                                                         │
│  2. GET /files/download/{export_file}                   │
│     → Télécharger le fichier généré dans l'outbox       │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Lancer un calcul

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  1. POST /rules/run  { "wait": true }                   │
│     → Lancer la règle et attendre le résultat           │
│                                                         │
│  2. POST /metadata/cube/refresh  (si nécessaire)        │
│     → Recalculer les agrégations du cube                │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Clôture mensuelle complète

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  1. POST /files/upload          (données réelles)       │
│  2. POST /data/import           (chargement)            │
│  3. POST /rules/ruleset/run     (calculs de clôture)    │
│  4. POST /metadata/cube/refresh (agrégations)           │
│  5. POST /data/export           (export résultats)      │
│  6. GET  /files/download/...    (récupérer le fichier)  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Structure du projet

```
pbcs-server/
│
├── main.py                  # Point d'entrée FastAPI, handlers globaux
├── config.py                # Configuration via .env (pydantic-settings)
├── requirements.txt         # Dépendances Python
├── .env                     # Credentials Oracle (non commité)
├── .env.example             # Template de configuration
├── pbcs-api.http            # Requêtes REST Client VS Code
│
├── pbcs/                    # Couche service (logique métier)
│   ├── client.py            # Client HTTP Oracle (httpx + Basic Auth)
│   ├── applications.py      # Applications, cubes, dimensions, membres
│   ├── jobs.py              # Gestion jobs (statut, polling, liste)
│   ├── rules.py             # Exécution règles et rulesets
│   ├── data.py              # Import / export de données
│   ├── metadata.py          # Import / export métadonnées + cube refresh
│   └── files.py             # Upload / download fichiers inbox/outbox
│
└── routers/                 # Couche API (routes FastAPI)
    ├── applications.py      # Routes /applications
    ├── jobs.py              # Routes /jobs
    ├── rules.py             # Routes /rules
    ├── data.py              # Routes /data
    ├── metadata.py          # Routes /metadata
    └── files.py             # Routes /files
```

---

## Gestion des erreurs

Toutes les erreurs Oracle sont propagées avec leur code HTTP original :

| Code | Signification |
|------|---------------|
| `400` | Requête invalide (nom de job inexistant, paramètre incorrect) |
| `401` | Credentials incorrects ou compte verrouillé |
| `403` | Droits insuffisants sur l'application |
| `404` | Ressource introuvable (job ID, fichier, application) |
| `504` | Timeout dépassé lors de l'attente d'un job |

**Format de réponse d'erreur :**
```json
{
  "error": "PBCS API Error",
  "detail": "Message détaillé d'Oracle"
}
```

---

## Dépendances principales

| Package | Version | Rôle |
|---------|---------|------|
| `fastapi` | 0.135+ | Framework API REST |
| `uvicorn` | 0.41+ | Serveur ASGI |
| `httpx` | 0.28+ | Client HTTP async vers Oracle |
| `pydantic-settings` | 2.13+ | Gestion configuration `.env` |
