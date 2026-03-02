"""Upload et download de fichiers vers l'inbox/outbox Oracle EPM Cloud."""

from pbcs.client import PBCSClient


async def upload_file(client: PBCSClient, filename: str, content: bytes) -> dict:
    """
    Uploade un fichier dans l'inbox Oracle EPM Cloud.

    Args:
        filename: Nom du fichier dans Oracle (ex: data_load.csv).
        content: Contenu binaire du fichier.
    """
    path = f"applicationsnapshots/{filename}/contents"
    return await client._interop_post_bytes(path, content, filename)


async def download_file(client: PBCSClient, filename: str) -> bytes:
    """
    Télécharge un fichier depuis l'outbox Oracle EPM Cloud.

    Args:
        filename: Nom du fichier dans Oracle.

    Returns:
        Contenu binaire du fichier.
    """
    path = f"applicationsnapshots/{filename}/contents"
    resp = await client._interop_get(path)
    return resp.content


async def list_files(client: PBCSClient) -> list[dict]:
    """Liste les fichiers disponibles dans Oracle EPM Cloud (inbox/outbox)."""
    resp = await client._interop_get("applicationsnapshots")
    data = resp.json()
    items = data.get("items", data) if isinstance(data, dict) else data
    return items
