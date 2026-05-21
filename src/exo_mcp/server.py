from __future__ import annotations

import json
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any

from mcp.server.fastmcp import Context, FastMCP
from mcp.server.fastmcp.exceptions import ToolError
from mcp.server.session import ServerSession

from exo_mcp.client import ExoClient
from exo_mcp.config import Settings, max_events


@dataclass
class AppContext:
    settings: Settings
    exo: ExoClient


@asynccontextmanager
async def app_lifespan(_server: FastMCP) -> AsyncIterator[AppContext]:
    settings = Settings.from_env()
    exo = ExoClient(settings)
    try:
        yield AppContext(settings=settings, exo=exo)
    finally:
        await exo.aclose()


mcp = FastMCP(
    "exo-cluster",
    instructions=(
        "Tools for managing an exo distributed inference cluster and running chat completions "
        "on loaded models. Configure EXO_BASE_URL to the exo master (Tailscale IP or localhost)."
    ),
    lifespan=app_lifespan,
)


def _ctx(ctx: Context[ServerSession, AppContext]) -> AppContext:
    return ctx.request_context.lifespan_context


def _dump(data: Any) -> str:
    return json.dumps(data, indent=2, default=str)


@mcp.tool()
async def exo_ping(ctx: Context[ServerSession, AppContext]) -> str:
    """Check connectivity to the exo master and return its node id."""
    app = _ctx(ctx)
    data = await app.exo.get_node_id()
    return _dump({"base_url": app.settings.base_url, "node": data})


@mcp.tool()
async def exo_cluster_state(ctx: Context[ServerSession, AppContext]) -> str:
    """Return full cluster state: topology, nodes, and active instances."""
    data = await _ctx(ctx).exo.get_state()
    return _dump(data)


@mcp.tool()
async def exo_cluster_events(
    ctx: Context[ServerSession, AppContext],
    limit: int = 25,
) -> str:
    """Return recent exo master events (debugging and observability)."""
    cap = max(1, min(limit, max_events()))
    data = await _ctx(ctx).exo.get_events()
    if isinstance(data, list):
        data = data[-cap:]
    return _dump(data)


@mcp.tool()
async def exo_list_models(
    ctx: Context[ServerSession, AppContext],
    downloaded_only: bool = False,
) -> str:
    """List models known to the cluster. Set downloaded_only to filter to downloaded models."""
    status = "downloaded" if downloaded_only else None
    data = await _ctx(ctx).exo.list_models(status=status)
    return _dump(data)


@mcp.tool()
async def exo_search_models(
    ctx: Context[ServerSession, AppContext],
    query: str = "",
    limit: int = 20,
) -> str:
    """Search HuggingFace mlx-community models available to add to exo."""
    data = await _ctx(ctx).exo.search_models(
        query=query or None,
        limit=max(1, min(limit, 50)),
    )
    return _dump(data)


@mcp.tool()
async def exo_add_custom_model(
    ctx: Context[ServerSession, AppContext],
    model_id: str,
) -> str:
    """Register a custom HuggingFace model id (e.g. mlx-community/my-model)."""
    data = await _ctx(ctx).exo.add_custom_model(model_id)
    return _dump(data)


@mcp.tool()
async def exo_delete_custom_model(
    ctx: Context[ServerSession, AppContext],
    model_id: str,
) -> str:
    """Remove a user-added custom model card from exo."""
    data = await _ctx(ctx).exo.delete_custom_model(model_id)
    return _dump(data)


@mcp.tool()
async def exo_preview_placements(
    ctx: Context[ServerSession, AppContext],
    model_id: str,
) -> str:
    """Preview possible instance placements for a model without creating one."""
    data = await _ctx(ctx).exo.preview_placements(model_id)
    return _dump(data)


@mcp.tool()
async def exo_compute_placement(
    ctx: Context[ServerSession, AppContext],
    model_id: str,
    sharding: str = "",
    min_nodes: int = 0,
    instance_meta_json: str = "",
) -> str:
    """Compute optimal placement for a model. instance_meta_json is optional JSON metadata."""
    meta: dict[str, Any] | None = None
    if instance_meta_json.strip():
        try:
            parsed = json.loads(instance_meta_json)
        except json.JSONDecodeError as exc:
            raise ToolError("instance_meta_json must be valid JSON") from exc
        if not isinstance(parsed, dict):
            raise ToolError("instance_meta_json must be a JSON object")
        meta = parsed
    data = await _ctx(ctx).exo.compute_placement(
        model_id=model_id,
        sharding=sharding or None,
        min_nodes=min_nodes if min_nodes > 0 else None,
        instance_meta=meta,
    )
    return _dump(data)


@mcp.tool()
async def exo_create_instance(
    ctx: Context[ServerSession, AppContext],
    model_id: str,
    placement_json: str = "",
) -> str:
    """Create and load a model instance. placement_json is optional JSON placement from exo_compute_placement."""
    placement: dict[str, Any] = {}
    if placement_json.strip():
        try:
            parsed = json.loads(placement_json)
        except json.JSONDecodeError as exc:
            raise ToolError("placement_json must be valid JSON") from exc
        if not isinstance(parsed, dict):
            raise ToolError("placement_json must be a JSON object")
        placement = parsed
    instance = {"model_id": model_id, "placement": placement}
    data = await _ctx(ctx).exo.create_instance(instance)
    return _dump(data)


@mcp.tool()
async def exo_get_instance(
    ctx: Context[ServerSession, AppContext],
    instance_id: str,
) -> str:
    """Get details for a running model instance."""
    data = await _ctx(ctx).exo.get_instance(instance_id)
    return _dump(data)


@mcp.tool()
async def exo_delete_instance(
    ctx: Context[ServerSession, AppContext],
    instance_id: str,
) -> str:
    """Unload and delete a model instance by id."""
    data = await _ctx(ctx).exo.delete_instance(instance_id)
    return _dump(data)


@mcp.tool()
async def exo_chat_completion(
    ctx: Context[ServerSession, AppContext],
    model: str,
    user_message: str,
    system_message: str = "",
    max_tokens: int = 0,
    temperature: float = -1.0,
) -> str:
    """Run a non-streaming chat completion on an exo-loaded model (OpenAI-compatible API)."""
    messages: list[dict[str, str]] = []
    if system_message.strip():
        messages.append({"role": "system", "content": system_message})
    messages.append({"role": "user", "content": user_message})

    body: dict[str, Any] = {"model": model, "messages": messages}
    if max_tokens > 0:
        body["max_tokens"] = max_tokens
    if temperature >= 0:
        body["temperature"] = temperature

    await ctx.info(f"exo inference: model={model}")
    data = await _ctx(ctx).exo.chat_completions(body)
    return _dump(data)


@mcp.tool()
async def exo_chat_completion_raw(
    ctx: Context[ServerSession, AppContext],
    request_json: str,
) -> str:
    """Run chat completion with a full OpenAI-style request body as JSON (stream forced off)."""
    try:
        body = json.loads(request_json)
    except json.JSONDecodeError as exc:
        raise ToolError("request_json must be valid JSON") from exc
    if not isinstance(body, dict):
        raise ToolError("request_json must be a JSON object")
    if "model" not in body or "messages" not in body:
        raise ToolError("request_json must include model and messages")
    data = await _ctx(ctx).exo.chat_completions(body)
    return _dump(data)


@mcp.tool()
async def exo_cancel_command(
    ctx: Context[ServerSession, AppContext],
    command_id: str,
) -> str:
    """Cancel an in-flight generation by command id."""
    data = await _ctx(ctx).exo.cancel_command(command_id)
    return _dump(data)


@mcp.resource("exo://cluster/state")
async def resource_cluster_state(ctx: Context[ServerSession, AppContext]) -> str:
    """Live cluster state from the exo master."""
    data = await _ctx(ctx).exo.get_state()
    return _dump(data)


@mcp.resource("exo://cluster/models")
async def resource_cluster_models(ctx: Context[ServerSession, AppContext]) -> str:
    """Models visible to the exo master."""
    data = await _ctx(ctx).exo.list_models()
    return _dump(data)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
