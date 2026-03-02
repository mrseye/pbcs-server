"""Routes FastAPI : liste des applications et cubes Oracle PBCS."""

from fastapi import APIRouter, Depends
from config import Settings, get_settings
from pbcs.client import PBCSClient
from pbcs import applications as app_service

router = APIRouter(prefix="/applications", tags=["Applications"])


@router.get("", summary="Lister les applications disponibles")
async def list_applications(settings: Settings = Depends(get_settings)):
    """
    Retourne la liste de toutes les applications Planning accessibles
    avec les identifiants configurés dans le `.env`.

    La réponse Oracle contient notamment `name`, `type`, et `links` pour chaque application.
    """
    client = PBCSClient(settings)
    return await app_service.list_applications(client)


@router.get("/{app_name}/cubes", summary="Lister les cubes d'une application")
async def list_cubes(app_name: str, settings: Settings = Depends(get_settings)):
    """
    Retourne les cubes (plan types) disponibles pour l'application spécifiée.

    - **app_name** : nom exact de l'application PBCS (ex: `Vision`, `PBCS_App`)

    Chaque cube expose son `name`, son `type` (BSO/ASO) et ses propriétés.
    """
    client = PBCSClient(settings)
    return await app_service.list_cubes(client, app_name)
