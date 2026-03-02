"""Routes FastAPI : exécution de règles Oracle PBCS."""

from fastapi import APIRouter, Depends, Body
from pydantic import BaseModel
from typing import Any
from config import Settings, get_settings
from pbcs.client import PBCSClient
from pbcs import rules as rule_service
from pbcs import jobs as job_service

router = APIRouter(prefix="/rules", tags=["Règles métier"])


class RunRuleRequest(BaseModel):
    rule_name: str
    parameters: dict[str, Any] | None = None
    wait: bool = False
    poll_interval: float = 5.0
    timeout: float = 600.0

    model_config = {
        "json_schema_extra": {
            "example": {
                "rule_name": "Calculate_FY2024",
                "parameters": {"Scenario": "Actual", "Year": "FY2024"},
                "wait": True,
            }
        }
    }


class RunRulesetRequest(BaseModel):
    ruleset_name: str
    parameters: dict[str, Any] | None = None
    wait: bool = False
    poll_interval: float = 5.0
    timeout: float = 600.0


@router.post("/run", summary="Lancer une règle métier")
async def run_rule(
    request: RunRuleRequest,
    settings: Settings = Depends(get_settings),
):
    """
    Lance une règle métier Oracle PBCS.

    - **rule_name**: Nom exact de la règle dans PBCS.
    - **parameters**: Variables de substitution (optionnel).
    - **wait**: Si True, attend la fin de l'exécution avant de répondre.
    """
    client = PBCSClient(settings)
    result = await rule_service.run_rule(
        client, request.rule_name, request.parameters
    )
    if request.wait and "jobId" in result:
        return await job_service.wait_for_job(
            client,
            result["jobId"],
            poll_interval=request.poll_interval,
            timeout=request.timeout,
        )
    return result


@router.post("/ruleset/run", summary="Lancer un ruleset")
async def run_ruleset(
    request: RunRulesetRequest,
    settings: Settings = Depends(get_settings),
):
    """
    Lance un ruleset Oracle PBCS.

    - **ruleset_name**: Nom du ruleset dans PBCS.
    - **parameters**: Variables de substitution (optionnel).
    - **wait**: Si True, attend la fin de l'exécution avant de répondre.
    """
    client = PBCSClient(settings)
    result = await rule_service.run_ruleset(
        client, request.ruleset_name, request.parameters
    )
    if request.wait and "jobId" in result:
        return await job_service.wait_for_job(
            client,
            result["jobId"],
            poll_interval=request.poll_interval,
            timeout=request.timeout,
        )
    return result
