"""Routes FastAPI : gestion des jobs Oracle PBCS."""

from fastapi import APIRouter, Depends, Query
from config import Settings, get_settings
from pbcs.client import PBCSClient
from pbcs import jobs as job_service

router = APIRouter(prefix="/jobs", tags=["Jobs"])


def get_client(settings: Settings = Depends(get_settings)) -> PBCSClient:
    return PBCSClient(settings)


@router.get("", summary="Lister les jobs récents")
async def list_jobs(
    limit: int = Query(50, ge=1, le=500, description="Nombre de jobs à retourner"),
    settings: Settings = Depends(get_settings),
):
    """Retourne la liste des jobs récents de l'application."""
    client = PBCSClient(settings)
    return await job_service.list_jobs(client, limit=limit)


@router.get("/{job_id}", summary="Statut d'un job")
async def get_job(job_id: int, settings: Settings = Depends(get_settings)):
    """Retourne le statut et les détails d'un job par son ID."""
    client = PBCSClient(settings)
    return await job_service.get_job(client, job_id)


@router.get("/{job_id}/wait", summary="Attendre la fin d'un job")
async def wait_job(
    job_id: int,
    poll_interval: float = Query(5.0, description="Intervalle de polling en secondes"),
    timeout: float = Query(600.0, description="Timeout en secondes"),
    settings: Settings = Depends(get_settings),
):
    """
    Attend la fin d'un job et retourne son statut final.
    Utile pour vérifier le résultat d'un job déjà lancé.
    """
    client = PBCSClient(settings)
    return await job_service.wait_for_job(
        client, job_id, poll_interval=poll_interval, timeout=timeout
    )
