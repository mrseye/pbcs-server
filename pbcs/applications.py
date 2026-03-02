"""Liste des applications, cubes, dimensions et membres Oracle PBCS."""

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
    """
    return await client._planning_raw_get(f"applications/{app_name}/plantypes")


async def list_dimensions(client: PBCSClient) -> dict:
    """
    Retourne la liste des dimensions de l'application configurée.

    Endpoint Oracle : GET /HyperionPlanning/rest/v3/applications/{app}/dimensions
    """
    return await client._planning_get("dimensions")


async def list_members(
    client: PBCSClient,
    dimension: str,
    parent: str | None = None,
    limit: int = 100,
) -> dict:
    """
    Retourne les membres d'une dimension.

    Endpoint Oracle : GET /HyperionPlanning/rest/v3/applications/{app}/dimensions/{dim}/members

    Args:
        dimension: Nom de la dimension (ex: Entity, Account, Period...).
        parent: Membre parent pour filtrer les enfants directs (optionnel).
        limit: Nombre maximum de membres à retourner.
    """
    params: dict = {"limit": limit}
    if parent:
        params["parent"] = parent
    return await client._planning_get(f"dimensions/{dimension}/members", params=params)
