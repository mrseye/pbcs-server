"""Import et export de données Oracle PBCS."""

from pbcs.client import PBCSClient


async def import_data(
    client: PBCSClient,
    job_name: str,
    import_file: str | None = None,
    clear_data: bool = False,
) -> dict:
    """
    Lance un import de données.

    Args:
        job_name: Nom du job d'import défini dans PBCS.
        import_file: Nom du fichier dans l'inbox Oracle (optionnel si configuré dans le job).
        clear_data: Si True, efface les données avant l'import.
    """
    body: dict = {"jobType": "IMPORT_DATA", "jobName": job_name}
    params: dict = {}
    if import_file:
        params["importFileName"] = import_file
    if clear_data:
        params["clearData"] = True
    if params:
        body["parameters"] = params
    return await client._planning_post("jobs", body)


async def export_data(
    client: PBCSClient,
    job_name: str,
    export_file: str | None = None,
) -> dict:
    """
    Lance un export de données.

    Args:
        job_name: Nom du job d'export défini dans PBCS.
        export_file: Nom du fichier de sortie dans l'outbox Oracle (optionnel).
    """
    body: dict = {"jobType": "EXPORT_DATA", "jobName": job_name}
    if export_file:
        body["parameters"] = {"exportFileName": export_file}
    return await client._planning_post("jobs", body)
