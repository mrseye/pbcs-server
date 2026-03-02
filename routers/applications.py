"""Routes FastAPI : liste des applications, cubes, dimensions et membres Oracle PBCS."""

from fastapi import APIRouter, Depends, Query
from config import Settings, get_settings
from pbcs.client import PBCSClient
from pbcs import applications as app_service

router = APIRouter(prefix="/applications", tags=["Applications"])


@router.get("", summary="Lister les applications disponibles")
async def list_applications(settings: Settings = Depends(get_settings)):
    """
    Retourne la liste de toutes les applications Planning accessibles
    avec les identifiants configurés dans le `.env`.
    """
    client = PBCSClient(settings)
    try:
        return await app_service.list_applications(client)
    finally:
        await client.close()


@router.get("/{app_name}/cubes", summary="Lister les cubes d'une application")
async def list_cubes(app_name: str, settings: Settings = Depends(get_settings)):
    """
    Retourne les cubes (plan types) disponibles pour l'application spécifiée.

    - **app_name** : nom exact de l'application PBCS (ex: `EPBCS`)

    Chaque cube expose son `name`, son `type` (BSO/ASO) et ses propriétés.
    """
    client = PBCSClient(settings)
    try:
        return await app_service.list_cubes(client, app_name)
    finally:
        await client.close()


@router.get("/dimensions", summary="Lister les dimensions de l'application")
async def list_dimensions(settings: Settings = Depends(get_settings)):
    """
    Retourne la liste de toutes les dimensions de l'application configurée dans `.env`.

    Utile pour connaître les dimensions disponibles avant d'importer/exporter des métadonnées.
    """
    client = PBCSClient(settings)
    try:
        return await app_service.list_dimensions(client)
    finally:
        await client.close()


@router.get("/dimensions/{dimension}/members", summary="Lister les membres d'une dimension")
async def list_members(
    dimension: str,
    parent: str | None = Query(None, description="Membre parent pour filtrer les enfants directs"),
    limit: int = Query(100, ge=1, le=1000, description="Nombre maximum de membres"),
    settings: Settings = Depends(get_settings),
):
    """
    Retourne les membres d'une dimension de l'application.

    - **dimension** : nom de la dimension (ex: `Entity`, `Account`, `Period`, `Scenario`)
    - **parent** : filtre les enfants directs d'un membre parent (optionnel)
    - **limit** : nombre maximum de membres retournés (max 1000)
    """
    client = PBCSClient(settings)
    try:
        return await app_service.list_members(client, dimension, parent=parent, limit=limit)
    finally:
        await client.close()
