"""Routes FastAPI : import/export de données Oracle PBCS."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from config import Settings, get_settings
from pbcs.client import PBCSClient
from pbcs import data as data_service
from pbcs import jobs as job_service

router = APIRouter(prefix="/data", tags=["Données"])


class ImportDataRequest(BaseModel):
    job_name: str
    import_file: str | None = None
    clear_data: bool = False
    wait: bool = False
    poll_interval: float = 5.0
    timeout: float = 600.0

    model_config = {
        "json_schema_extra": {
            "example": {
                "job_name": "Load_Actuals",
                "import_file": "actuals_2024.csv",
                "clear_data": False,
                "wait": True,
            }
        }
    }


class ExportDataRequest(BaseModel):
    job_name: str
    export_file: str | None = None
    wait: bool = False
    poll_interval: float = 5.0
    timeout: float = 600.0

    model_config = {
        "json_schema_extra": {
            "example": {
                "job_name": "Export_Actuals",
                "export_file": "export_actuals.csv",
                "wait": True,
            }
        }
    }


@router.post("/import", summary="Importer des données")
async def import_data(
    request: ImportDataRequest,
    settings: Settings = Depends(get_settings),
):
    """
    Lance un job d'import de données dans Oracle PBCS.

    Le fichier doit être préalablement uploadé via `POST /files/upload`.
    """
    client = PBCSClient(settings)
    result = await data_service.import_data(
        client,
        request.job_name,
        import_file=request.import_file,
        clear_data=request.clear_data,
    )
    if request.wait and "jobId" in result:
        return await job_service.wait_for_job(
            client,
            result["jobId"],
            poll_interval=request.poll_interval,
            timeout=request.timeout,
        )
    return result


@router.post("/export", summary="Exporter des données")
async def export_data(
    request: ExportDataRequest,
    settings: Settings = Depends(get_settings),
):
    """
    Lance un job d'export de données depuis Oracle PBCS.

    Après l'export, téléchargez le fichier via `GET /files/download/{filename}`.
    """
    client = PBCSClient(settings)
    result = await data_service.export_data(
        client,
        request.job_name,
        export_file=request.export_file,
    )
    if request.wait and "jobId" in result:
        return await job_service.wait_for_job(
            client,
            result["jobId"],
            poll_interval=request.poll_interval,
            timeout=request.timeout,
        )
    return result
