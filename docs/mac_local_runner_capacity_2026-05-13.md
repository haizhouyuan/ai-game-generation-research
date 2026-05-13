# Mac Local Runner Capacity - 2026-05-13

## Purpose

This records Route G / W10 for the full PUBG-like local AI 3D asset factory
goal. The Mac M2 Max 96GB should be useful as a control plane and possible
overflow local inference worker, but it must not block the HomePC GPU asset
production lanes.

## Current Hardware

Observed locally:

```text
CPU: Apple M2 Max
RAM: 103079215104 bytes
```

This is enough memory for useful local text/vision helper models if the runtime
is installed.

## Current Runtime Availability

Current shell probe:

```text
mlx: missing
mlx_lm: missing
torch: missing
transformers: missing
ollama: not found
llama-cli: not found
llama-server: not found
```

So the Mac is currently ready as Codex/control-plane/browser-evidence host, but
not yet ready as a local model worker.

## Recommendation

Do not spend the next critical path on Mac model setup while HomePC Hunyuan,
ComfyUI, TRELLIS, and Blender routes are active.

Use the Mac for:

- Codex orchestration and merge review;
- GitHub push/checkpoint work;
- browser/CDP evidence;
- task packet creation;
- Kimi/Gemini/MiniMax runner control;
- local file validation and hash manifests.

When local model capacity is needed, install in this order:

1. Ollama for quick low-friction local summarization/classification workers.
2. MLX / `mlx-lm` for Apple Silicon-native local LLM experiments.
3. `llama.cpp` only if GGUF model serving/control is needed.

## Non-Blocking Dry-Run

The dry-run conclusion is explicit: no local model command was run because no
local model runtime is currently installed. This is not a blocker for the asset
factory because HomePC GPU and external coding runners are already active.

## Next Action When Needed

Create a separate bounded setup packet:

```text
tasks/pubg_like_full_rebuild/mac_local_runner_setup_00X.md
```

Acceptance should be one local summarization/classification task over an asset
packet report, not a heavy 3D generation job.
