# AGENTS.md

## Cursor Cloud specific instructions

### Project overview

TowerCombatSlice is a Godot 4.3 game prototype (GDScript). It has no web services, databases, or package managers — the only runtime dependency is the Godot engine binary.

### Running the game

```bash
# Start Xvfb (if not already running)
Xvfb :99 -screen 0 1280x720x24 &
export DISPLAY=:99

# Run the game with software rendering (no GPU available in Cloud VMs)
cd /workspace && godot --rendering-driver opengl3
```

- `--rendering-driver opengl3` is required because Cloud VMs lack a GPU; Vulkan/Forward+ will not work. Mesa llvmpipe provides software OpenGL.
- ALSA audio errors and the SSAO warning are expected and harmless — no audio hardware exists, and SSAO requires Forward+.

### Headless mode (no display needed)

```bash
godot --headless --quit-after 5
```

Useful for CI or quick validation. Mesh null-parameter errors are expected in headless/dummy rendering.

### Linting / script validation

```bash
godot --headless --check-only --script <path_to_gd_file>
```

Scripts that reference the `CombatDirector` autoload singleton (`scripts/combat_ui.gd`, `scripts/tower_floor_controller.gd`) will fail `--check-only` in isolation because autoloads are only registered when running the full project. This is expected; those scripts work correctly when the project runs.

### Project import (resource cache rebuild)

```bash
godot --headless --import
```

Run this after pulling changes that add/modify `.tscn`, `.tres`, or texture files. Mesh null errors in headless import are expected.

### No automated test framework

This project does not include a test runner or unit-test framework. Validation is done by running the game and checking GDScript compilation.

### Optional: Godot Catalyst MCP addon

See `tools/CATALYST_MCP.txt`. Install with `bash tools/install_catalyst_addon.sh`. This is purely optional editor tooling for Cursor integration.
