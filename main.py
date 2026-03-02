"""Serveur FastAPI - Oracle PBCS REST API Wrapper."""

import logging
import socket
import httpx
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

logging.basicConfig(level=logging.INFO, format="%(levelname)s:  [%(name)s] %(message)s")

from config import get_settings
from pbcs.client import PBCSError
from routers import jobs, rules, data, metadata, files, applications


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    print(f"Oracle PBCS Server démarré")
    print(f"  Host    : {settings.ORACLE_HOST}")
    print(f"  App     : {settings.ORACLE_APP}")
    print(f"  API     : {settings.planning_base_url}")
    print(f"  Docs    : http://localhost:8000/docs")
    yield


app = FastAPI(
    title="Oracle PBCS API",
    description="""
## Serveur Python pour Oracle Planning & Budgeting Cloud (PBCS)

Interagissez avec votre environnement Oracle PBCS via une API REST locale.

### Fonctionnalités
- **Règles** : Lancer des règles métier et des rulesets
- **Données** : Importer et exporter des données
- **Métadonnées** : Importer/exporter dimensions et membres
- **Fichiers** : Uploader/télécharger des fichiers (inbox/outbox)
- **Jobs** : Suivre le statut des jobs en temps réel
- **Cube** : Rafraîchir le cube (agrégations)

### Utilisation
1. Configurez votre `.env` avec vos identifiants Oracle
2. Lancez le serveur : `uvicorn main:app --reload`
3. Ouvrez [Swagger UI](http://localhost:8000/docs) ou utilisez l'extension REST Client de VS Code
    """,
    version="1.0.0",
    lifespan=lifespan,
)

# Gestion globale des erreurs PBCS
@app.exception_handler(PBCSError)
async def pbcs_error_handler(request: Request, exc: PBCSError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "PBCS API Error", "detail": exc.detail},
    )

@app.exception_handler(TimeoutError)
async def timeout_error_handler(request: Request, exc: TimeoutError):
    return JSONResponse(
        status_code=504,
        content={"error": "Job timeout", "detail": str(exc)},
    )

# Inclusion des routers
app.include_router(applications.router)
app.include_router(jobs.router)
app.include_router(rules.router)
app.include_router(data.router)
app.include_router(metadata.router)
app.include_router(files.router)


@app.get("/health", tags=["Info"])
async def health_check():
    """
    Diagnostic de connexion vers Oracle PBCS.

    Teste 3 niveaux :
    1. **DNS** — résolution du nom d'hôte Oracle
    2. **HTTPS** — connexion TCP/TLS sans authentification
    3. **Auth** — appel authentifié à l'API Oracle (`GET /applications`)
    """
    settings = get_settings()
    host = settings.ORACLE_HOST
    result = {
        "config": {
            "host": host,
            "username": settings.ORACLE_USERNAME,
            "application": settings.ORACLE_APP,
            "api_url": settings.planning_base_url,
        },
        "checks": {}
    }

    # ── 1. Résolution DNS ────────────────────────────────────────────────
    try:
        ip = socket.gethostbyname(host)
        result["checks"]["dns"] = {"ok": True, "ip": ip}
    except socket.gaierror as e:
        result["checks"]["dns"] = {"ok": False, "error": str(e)}
        result["status"] = "dns_failure"
        return JSONResponse(status_code=503, content=result)

    # ── 2. Connexion HTTPS (sans auth) ───────────────────────────────────
    ping_url = f"https://{host}/HyperionPlanning/rest/v3/applications"
    try:
        async with httpx.AsyncClient(timeout=10.0, verify=True) as client:
            resp = await client.get(ping_url)
        # 401 = serveur accessible, juste pas encore authentifié → OK réseau
        result["checks"]["https"] = {"ok": True, "http_status": resp.status_code}
    except httpx.ConnectError as e:
        result["checks"]["https"] = {"ok": False, "error": f"Connexion refusée : {e}"}
        result["status"] = "network_failure"
        return JSONResponse(status_code=503, content=result)
    except httpx.TimeoutException:
        result["checks"]["https"] = {"ok": False, "error": "Timeout (10 s)"}
        result["status"] = "timeout"
        return JSONResponse(status_code=503, content=result)

    # ── 3. Appel authentifié ─────────────────────────────────────────────
    try:
        async with httpx.AsyncClient(
            auth=settings.auth,
            headers={"Accept": "application/json"},
            timeout=15.0,
            verify=True,
        ) as client:
            resp = await client.get(ping_url)

        if resp.status_code == 200:
            data = resp.json()
            apps = [a.get("name", a) for a in data.get("items", [])] if isinstance(data, dict) else []
            result["checks"]["auth"] = {"ok": True, "applications": apps}
            result["status"] = "ok"
        elif resp.status_code == 401:
            result["checks"]["auth"] = {
                "ok": False,
                "error": "401 Unauthorized — identifiants incorrects ou compte verrouillé",
                "oracle_detail": resp.text[:500],
            }
            result["status"] = "auth_failure"
            return JSONResponse(status_code=401, content=result)
        else:
            result["checks"]["auth"] = {
                "ok": False,
                "http_status": resp.status_code,
                "oracle_detail": resp.text[:500],
            }
            result["status"] = "oracle_error"
            return JSONResponse(status_code=502, content=result)

    except Exception as e:
        result["checks"]["auth"] = {"ok": False, "error": str(e)}
        result["status"] = "error"
        return JSONResponse(status_code=503, content=result)

    return result


@app.get("/", tags=["Info"])
async def root():
    """Informations sur le serveur."""
    settings = get_settings()
    return {
        "service": "Oracle PBCS API",
        "version": "1.0.0",
        "host": settings.ORACLE_HOST,
        "application": settings.ORACLE_APP,
        "docs": "/docs",
        "endpoints": {
            "applications_list": "/applications",
            "cubes_list": "/applications/{app_name}/cubes",
            "jobs": "/jobs",
            "rules": "/rules/run",
            "ruleset": "/rules/ruleset/run",
            "data_import": "/data/import",
            "data_export": "/data/export",
            "metadata_import": "/metadata/import",
            "metadata_export": "/metadata/export",
            "cube_refresh": "/metadata/cube/refresh",
            "files_list": "/files",
            "file_upload": "/files/upload",
            "file_download": "/files/download/{filename}",
        },
    }
