"""Client HTTP de base pour l'API Oracle EPM Cloud."""

import logging
import httpx
from typing import Any
from config import Settings

logger = logging.getLogger(__name__)


class PBCSError(Exception):
    """Erreur retournée par l'API Oracle PBCS."""

    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"PBCS API Error {status_code}: {detail}")


class PBCSClient:
    """Client HTTP pour Oracle EPM Cloud Planning REST API v3."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self._http = httpx.AsyncClient(
            auth=settings.auth,
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            timeout=120.0,
            verify=True,
        )

    async def close(self):
        await self._http.aclose()

    # ------------------------------------------------------------------ #
    #  Planning API (HyperionPlanning/rest/v3)                            #
    # ------------------------------------------------------------------ #

    def _planning_url(self, path: str) -> str:
        app = self.settings.ORACLE_APP
        base = self.settings.planning_base_url
        return f"{base}/applications/{app}/{path.lstrip('/')}"

    async def _planning_get(self, path: str, params: dict | None = None) -> Any:
        url = self._planning_url(path)
        resp = await self._http.get(url, params=params)
        return self._handle(resp)

    async def _planning_raw_get(self, path: str, params: dict | None = None) -> Any:
        """GET sur la base Planning sans préfixer l'application courante."""
        url = f"{self.settings.planning_base_url}/{path.lstrip('/')}"
        resp = await self._http.get(url, params=params)
        return self._handle(resp)

    async def _planning_post(self, path: str, body: dict) -> Any:
        url = self._planning_url(path)
        resp = await self._http.post(url, json=body)
        return self._handle(resp)

    # ------------------------------------------------------------------ #
    #  Interop API (upload/download fichiers)                             #
    # ------------------------------------------------------------------ #

    def _interop_url(self, path: str) -> str:
        return f"{self.settings.interop_base_url}/{path.lstrip('/')}"

    async def _interop_get(self, path: str) -> httpx.Response:
        url = self._interop_url(path)
        resp = await self._http.get(url)
        if resp.status_code not in (200, 201, 204):
            raise PBCSError(resp.status_code, resp.text)
        return resp

    async def _interop_post_bytes(self, path: str, content: bytes, filename: str) -> Any:
        url = self._interop_url(path)
        resp = await self._http.post(
            url,
            content=content,
            headers={
                "Content-Type": "application/octet-stream",
                "Accept": "application/json",
            },
        )
        return self._handle(resp)

    # ------------------------------------------------------------------ #
    #  Gestion des erreurs                                                #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _handle(resp: httpx.Response) -> Any:
        if resp.status_code in (200, 201, 204):
            if resp.content:
                return resp.json()
            return {}
        try:
            detail = resp.json()
        except Exception:
            detail = resp.text
        logger.error("Oracle PBCS %s %s → %s", resp.status_code, resp.url, detail)
        raise PBCSError(resp.status_code, str(detail))
