"""Exécution de règles et rulesets Oracle PBCS."""

from pbcs.client import PBCSClient


async def run_rule(
    client: PBCSClient,
    rule_name: str,
    parameters: dict | None = None,
) -> dict:
    """Lance une règle métier. Retourne le jobId immédiatement."""
    body: dict = {"jobType": "RULES", "jobName": rule_name}
    if parameters:
        body["parameters"] = parameters
    return await client._planning_post("jobs", body)


async def run_ruleset(
    client: PBCSClient,
    ruleset_name: str,
    parameters: dict | None = None,
) -> dict:
    """Lance un ruleset. Retourne le jobId immédiatement."""
    body: dict = {"jobType": "RULESET", "jobName": ruleset_name}
    if parameters:
        body["parameters"] = parameters
    return await client._planning_post("jobs", body)
