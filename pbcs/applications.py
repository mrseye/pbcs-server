"""Liste des applications et cubes disponibles sur Oracle PBCS."""

from pbcs.client import PBCSClient


async def list_applications(client: PBCSClient) -> dict:
    """
    Retourne la liste de toutes les applications Planning disponibles.

    Endpoint Oracle : GET /HyperionPlanning/rest/v3/applications
    """
    return await client._planning_raw_get("applications")


async def list_cubes(client: PBCSClient, app_name: str) -> dict:
    """
    Retourne les cubes (plan types) d'une application donnée.

    Endpoint Oracle : GET /HyperionPlanning/rest/v3/applications/{app}/plantypes

    Args:
        app_name: Nom de l'application PBCS (ex: "Vision", "PBCS_App").
    """
    return await client._planning_raw_get(f"applications/{app_name}/plantypes")
