"""Gestion des jobs Oracle PBCS (statut, liste, polling)."""

import asyncio
from typing import Any
from pbcs.client import PBCSClient

# Statuts Oracle PBCS
JOB_STATUS = {
    -1: "En cours",
    0: "Succès",
    1: "Erreur",
    2: "Annulé",
    3: "Application invalide",
}


def format_job(job: dict) -> dict:
    status_code = job.get("status", -1)
    return {
        "jobId": job.get("jobId"),
        "jobName": job.get("jobName"),
        "jobType": job.get("jobType"),
        "status": status_code,
        "statusLabel": JOB_STATUS.get(status_code, "Inconnu"),
        "completedTime": job.get("completedTime"),
        "details": job.get("details"),
        "descriptiveStatus": job.get("descriptiveStatus"),
    }


async def get_job(client: PBCSClient, job_id: int) -> dict:
    """Récupère le statut d'un job par son ID."""
    data = await client._planning_get(f"jobs/{job_id}")
    return format_job(data)


async def list_jobs(client: PBCSClient, limit: int = 50) -> list[dict]:
    """Liste les jobs récents de l'application."""
    data = await client._planning_get("jobs", params={"limit": limit})
    jobs = data.get("items", data) if isinstance(data, dict) else data
    return [format_job(j) for j in jobs]


async def wait_for_job(
    client: PBCSClient,
    job_id: int,
    poll_interval: float = 5.0,
    timeout: float = 600.0,
) -> dict:
    """Attend la fin d'un job en faisant du polling. Lève une exception si timeout."""
    elapsed = 0.0
    while elapsed < timeout:
        job = await get_job(client, job_id)
        if job["status"] != -1:
            return job
        await asyncio.sleep(poll_interval)
        elapsed += poll_interval
    raise TimeoutError(f"Job {job_id} non terminé après {timeout}s")
