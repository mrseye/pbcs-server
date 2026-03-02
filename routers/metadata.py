"""Routes FastAPI : import/export de métadonnées Oracle PBCS."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from config import Settings, get_settings
from pbcs.client import PBCSClient
from pbcs import metadata as meta_service
from pbcs import jobs as job_service

router = APIRouter(prefix="/metadata", tags=["Métadonnées"])


class ImportMetaRequest(BaseModel):
    job_name: str
    import_file: str | None = None
    dimension: str | None = None
    wait: bool = False
    poll_interval: float = 5.0
    timeout: float = 600.0

    model_config = {
        "json_schema_extra": {
            "example": {
                "job_name": "Import_Entity",
                "import_file": "entity_metadata.csv",
                "dimension": "Entity",
                "wait": True,
            }
        }
    }


class ExportMetaRequest(BaseModel):
    job_name: str
    export_file: str | None = None
    dimension: str | None = None
    wait: bool = False
    poll_interval: float = 5.0
    timeout: float = 600.0


@router.post("/import", summary="Importer des métadonnées")
async def import_metadata(
    request: ImportMetaRequest,
    settings: Settings = Depends(get_settings),
):
    """Lance un import de métadonnées (dimensions, membres, etc.)."""
    client = PBCSClient(settings)
    result = await meta_service.import_metadata(
        client,
        request.job_name,
        import_file=request.import_file,
        dimension=request.dimension,
    )
    if request.wait and "jobId" in result:
        return await job_service.wait_for_job(
            client,
            result["jobId"],
            poll_interval=request.poll_interval,
            timeout=request.timeout,
        )
    return result


@router.post("/export", summary="Exporter des métadonnées")
async def export_metadata(
    request: ExportMetaRequest,
    settings: Settings = Depends(get_settings),
):
    """Lance un export de métadonnées."""
    client = PBCSClient(settings)
    result = await meta_service.export_metadata(
        client,
        request.job_name,
        export_file=request.export_file,
        dimension=request.dimension,
    )
    if request.wait and "jobId" in result:
        return await job_service.wait_for_job(
            client,
            result["jobId"],
            poll_interval=request.poll_interval,
            timeout=request.timeout,
        )
    return result


@router.post("/cube/refresh", summary="Rafraîchir le cube")
async def refresh_cube(
    wait: bool = False,
    poll_interval: float = 5.0,
    timeout: float = 600.0,
    settings: Settings = Depends(get_settings),
):
    """Lance un refresh du cube Oracle PBCS (recalcul des agrégations)."""
    client = PBCSClient(settings)
    result = await meta_service.refresh_cube(client)
    if wait and "jobId" in result:
        return await job_service.wait_for_job(
            client, result["jobId"], poll_interval=poll_interval, timeout=timeout
        )
    return result
