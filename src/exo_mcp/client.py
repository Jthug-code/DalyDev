from __future__ import annotations

import json
from typing import Any

import httpx
from mcp.server.fastmcp.exceptions import ToolError

from exo_mcp.config import Settings


class ExoClient:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        headers: dict[str, str] = {"Accept": "application/json"}
        if settings.api_token:
            headers["Authorization"] = f"Bearer {settings.api_token}"
        timeout = httpx.Timeout(
            settings.timeout_seconds,
            connect=settings.connect_timeout_seconds,
        )
        self._http = httpx.AsyncClient(
            base_url=settings.base_url,
            headers=headers,
            timeout=timeout,
        )

    async def aclose(self) -> None:
        await self._http.aclose()

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
    ) -> Any:
        try:
            response = await self._http.request(method, path, params=params, json=json_body)
        except httpx.ConnectError as exc:
            raise ToolError(
                f"Cannot reach exo at {self._settings.base_url}. "
                "Check EXO_BASE_URL, Tailscale, and that the master is running."
            ) from exc
        except httpx.TimeoutException as exc:
            raise ToolError(
                f"Request to exo timed out ({method} {path}). "
                "Increase EXO_REQUEST_TIMEOUT for long inference."
            ) from exc

        if response.status_code >= 400:
            detail = response.text.strip() or response.reason_phrase
            raise ToolError(f"exo API error {response.status_code} on {method} {path}: {detail}")

        if not response.content:
            return None
        content_type = response.headers.get("content-type", "")
        if "application/json" in content_type:
            return response.json()
        return response.text

    async def get_node_id(self) -> Any:
        return await self.request("GET", "/node_id")

    async def get_state(self) -> Any:
        return await self.request("GET", "/state")

    async def get_events(self) -> Any:
        return await self.request("GET", "/events")

    async def list_models(self, *, status: str | None = None) -> Any:
        params = {"status": status} if status else None
        return await self.request("GET", "/models", params=params)

    async def search_models(self, *, query: str | None, limit: int) -> Any:
        params: dict[str, Any] = {"limit": limit}
        if query:
            params["query"] = query
        return await self.request("GET", "/models/search", params=params)

    async def add_custom_model(self, model_id: str) -> Any:
        return await self.request("POST", "/models/add", json_body={"model_id": model_id})

    async def delete_custom_model(self, model_id: str) -> Any:
        path = f"/models/custom/{model_id}"
        return await self.request("DELETE", path)

    async def preview_placements(self, model_id: str) -> Any:
        return await self.request(
            "GET",
            "/instance/previews",
            params={"model_id": model_id},
        )

    async def compute_placement(
        self,
        *,
        model_id: str,
        sharding: str | None,
        min_nodes: int | None,
        instance_meta: dict[str, Any] | None,
    ) -> Any:
        params: dict[str, Any] = {"model_id": model_id}
        if sharding:
            params["sharding"] = sharding
        if min_nodes is not None:
            params["min_nodes"] = min_nodes
        if instance_meta is not None:
            params["instance_meta"] = json.dumps(instance_meta)
        return await self.request("GET", "/instance/placement", params=params)

    async def create_instance(self, instance: dict[str, Any]) -> Any:
        return await self.request("POST", "/instance", json_body={"instance": instance})

    async def get_instance(self, instance_id: str) -> Any:
        return await self.request("GET", f"/instance/{instance_id}")

    async def delete_instance(self, instance_id: str) -> Any:
        return await self.request("DELETE", f"/instance/{instance_id}")

    async def chat_completions(self, body: dict[str, Any]) -> Any:
        body = {**body, "stream": False}
        return await self.request("POST", "/v1/chat/completions", json_body=body)

    async def cancel_command(self, command_id: str) -> Any:
        return await self.request("POST", f"/v1/cancel/{command_id}")
