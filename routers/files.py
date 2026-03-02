"""Routes FastAPI : gestion des fichiers Oracle EPM Cloud (inbox/outbox)."""

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import Response
from config import Settings, get_settings
from pbcs.client import PBCSClient, PBCSError
from pbcs import files as file_service

router = APIRouter(prefix="/files", tags=["Fichiers"])


@router.get("", summary="Lister les fichiers Oracle")
async def list_files(settings: Settings = Depends(get_settings)):
    """Liste tous les fichiers disponibles dans l'inbox/outbox Oracle EPM Cloud."""
    client = PBCSClient(settings)
    return await file_service.list_files(client)


@router.post("/upload", summary="Uploader un fichier vers Oracle")
async def upload_file(
    file: UploadFile = File(..., description="Fichier à uploader (CSV, txt, zip...)"),
    settings: Settings = Depends(get_settings),
):
    """
    Uploade un fichier dans l'inbox Oracle EPM Cloud.

    Le fichier sera disponible dans l'inbox pour les jobs d'import de données
    ou de métadonnées.
    """
    content = await file.read()
    client = PBCSClient(settings)
    try:
        result = await file_service.upload_file(client, file.filename, content)
        return {"message": f"Fichier '{file.filename}' uploadé avec succès", "details": result}
    except PBCSError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.get("/download/{filename}", summary="Télécharger un fichier depuis Oracle")
async def download_file(
    filename: str,
    settings: Settings = Depends(get_settings),
):
    """
    Télécharge un fichier depuis l'outbox Oracle EPM Cloud.

    Utile après un job d'export de données ou de métadonnées.
    """
    client = PBCSClient(settings)
    try:
        content = await file_service.download_file(client, filename)
        return Response(
            content=content,
            media_type="application/octet-stream",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except PBCSError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
