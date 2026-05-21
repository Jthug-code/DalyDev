# exo-mcp — Cursor MCP bridge for exo clusters

MCP server that lets Cursor agents **inspect**, **manage**, and **run inference** on an [exo](https://github.com/exo-explore/exo) cluster. Run this on any machine that can reach your exo master (typically a always-on box on Tailscale).

## Architecture

```mermaid
flowchart LR
  Cursor[Cursor IDE / Cloud Agent]
  MCP[exo-mcp on tailnet host]
  Master[exo master :52415]
  Workers[Work machines / exo nodes]

  Cursor -->|stdio MCP| MCP
  MCP -->|HTTP REST| Master
  Master --> Workers
```

The cloud agent does not join Tailscale. **You** run `exo-mcp` on a host that can hit the master (localhost or `100.x.x.x`), then point Cursor’s MCP config at that process.

## Requirements

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- exo master running and reachable from this machine
- exo nodes on Tailscale (or LAN) as you already have

## Your master (Tailscale)

exo master Tailscale IP: **`100.88.30.110`**

- **Cursor on the master machine:** `EXO_BASE_URL=http://127.0.0.1:52415` (see `cursor-mcp.master-local.json`)
- **Cursor on another tailnet device:** `EXO_BASE_URL=http://100.88.30.110:52415` (see `cursor-mcp.example.json`)

## Quick start

1. Install dependencies:

```bash
cd tools/exo-mcp
uv sync
```

2. Set the master URL (Tailscale IP of the machine running exo master):

```bash
export EXO_BASE_URL=http://100.88.30.110:52415
uv run exo-mcp
```

3. Add to Cursor MCP settings (merge into your MCP config):

Copy `cursor-mcp.example.json` and replace:

- `/ABSOLUTE/PATH/TO/dalydev/tools/exo-mcp` with your repo path
- `EXO_BASE_URL` with your master’s Tailscale IP or `http://127.0.0.1:52415` if Cursor runs on the same host

Restart Cursor (or reload MCP). You should see tools prefixed with `exo_`.

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `EXO_BASE_URL` | `http://127.0.0.1:52415` | exo master REST base URL |
| `EXO_API_TOKEN` | (empty) | Optional `Authorization: Bearer` if you add auth in front of exo |
| `EXO_REQUEST_TIMEOUT` | `600` | HTTP timeout for long inference (seconds) |
| `EXO_CONNECT_TIMEOUT` | `10` | Connection timeout (seconds) |
| `EXO_MAX_EVENTS` | `50` | Max events returned by `exo_cluster_events` |

See `.env.example`.

## MCP tools

| Tool | Purpose |
|------|---------|
| `exo_ping` | Connectivity check + master `node_id` |
| `exo_cluster_state` | Full cluster state |
| `exo_cluster_events` | Recent master events |
| `exo_list_models` | Available / downloaded models |
| `exo_search_models` | Search HuggingFace mlx-community |
| `exo_add_custom_model` | Register custom HF model |
| `exo_delete_custom_model` | Remove custom model card |
| `exo_preview_placements` | Placement previews for a model |
| `exo_compute_placement` | Optimal placement without creating |
| `exo_create_instance` | Load model instance on cluster |
| `exo_get_instance` | Instance details |
| `exo_delete_instance` | Unload instance |
| `exo_chat_completion` | Simple chat completion |
| `exo_chat_completion_raw` | Full OpenAI-style request JSON |
| `exo_cancel_command` | Cancel in-flight generation |

Resources: `exo://cluster/state`, `exo://cluster/models`

## Typical agent workflow

1. `exo_ping` — confirm reachability
2. `exo_cluster_state` — see nodes and running instances
3. `exo_list_models` — pick a model id
4. `exo_compute_placement` → `exo_create_instance` — load on cluster
5. `exo_chat_completion` — run inference
6. `exo_delete_instance` — unload when done

## Tailscale notes

- Point `EXO_BASE_URL` at the **master** node’s Tailscale IP (port `52415` unless you changed it).
- Prefer running `exo-mcp` on the same machine as Cursor **or** on a small always-on tailnet host with ACLs allowing only that host → master:52415.
- High latency over Tailscale is fine for management and pipeline-style workloads; tensor-parallel across remote nodes may be slower than LAN.

### Optional: Tailscale Serve (remote Cursor only)

If Cursor runs on a laptop **not** on the tailnet, expose the master only to your tailnet via Serve, or run `exo-mcp` on a tailnet VPS and use stdio locally on that box with SSH Remote — **do not** expose `:52415` to the public internet without authentication.

## Security

- Treat `EXO_BASE_URL` like admin access: load/unload models and run arbitrary prompts on your hardware.
- Use Tailscale ACLs to limit who can reach port 52415.
- Set `EXO_API_TOKEN` if you put a reverse proxy with bearer auth in front of exo.

## Development

```bash
cd tools/exo-mcp
uv sync
uv run exo-mcp
```

Test with the MCP inspector (optional):

```bash
npx @modelcontextprotocol/inspector uv run --directory . exo-mcp
```

## Related

- [exo API reference](https://github.com/exo-explore/exo/blob/main/docs/api.md)
- Godot Catalyst MCP in `tools/CATALYST_MCP.txt` (separate integration)


## Standalone repository

This project lives in its own GitHub repo: **https://github.com/Jthug-code/exo-mcp**

To create and push it (requires your GitHub account, not the Cursor app token):

```bash
git clone -b exo-mcp-standalone https://github.com/Jthug-code/DalyDev.git exo-mcp
cd exo-mcp
./scripts/publish-to-github.sh
```

Or clone from a bundle: `git clone exo-mcp.bundle exo-mcp`
