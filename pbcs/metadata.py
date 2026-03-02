"""Import et export de métadonnées Oracle PBCS."""

from pbcs.client import PBCSClient


async def import_metadata(
    client: PBCSClient,
    job_name: str,
    import_file: str | None = None,
    dimension: str | None = None,
) -> dict:
    """
    Lance un import de métadonnées.

    Args:
        job_name: Nom du job d'import défini dans PBCS.
        import_file: Nom du fichier dans l'inbox Oracle.
        dimension: Dimension cible (ex: Entity, Account, Period...).
    """
    body: dict = {"jobType": "IMPORT_METADATA", "jobName": job_name}
    params: dict = {}
    if import_file:
        params["importFileName"] = import_file
    if dimension:
        params["dimension"] = dimension
    if params:
        body["parameters"] = params
    return await client._planning_post("jobs", body)


async def export_metadata(
    client: PBCSClient,
    job_name: str,
    export_file: str | None = None,
    dimension: str | None = None,
) -> dict:
    """
    Lance un export de métadonnées.

    Args:
        job_name: Nom du job d'export défini dans PBCS.
        export_file: Nom du fichier de sortie.
        dimension: Dimension à exporter.
    """
    body: dict = {"jobType": "EXPORT_METADATA", "jobName": job_name}
    params: dict = {}
    if export_file:
        params["exportFileName"] = export_file
    if dimension:
        params["dimension"] = dimension
    if params:
        body["parameters"] = params
    return await client._planning_post("jobs", body)


async def refresh_cube(client: PBCSClient) -> dict:
    """Rafraîchit le cube (recalcul des agrégations)."""
    return await client._planning_post("jobs", {"jobType": "CUBE_REFRESH"})
