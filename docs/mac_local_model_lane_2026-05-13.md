# Mac Local Model Lane - 2026-05-13

## Objective

Use the Mac M2 Max 96GB as a budget-saving local inference lane for lightweight parallel work, while keeping heavy 3D model generation on HomePC/dual-3090.

This lane is not the main asset-generation route. It is for:

- task summarization;
- screenshot-project triage after OCR text exists;
- worker prompt drafting;
- local review/classification;
- fallback when paid provider tokens should be conserved.

## Decision

Start with `mlx-lm` as the preferred Mac-native route, keep `llama.cpp` as the compatibility/server fallback, and use LM Studio/Ollama only when their UI/server wrappers reduce friction.

## Why MLX First

The official `ml-explore/mlx-lm` project is built for Apple Silicon. It supports Hugging Face model loading, quantization, streaming generation, prompt caching, and MLX-native execution.

For this Mac M2 Max 96GB, MLX is the best first candidate for local lightweight text work because it uses the Apple Silicon path directly and has prompt-cache features useful for repeated task packets.

## Why Keep llama.cpp

`llama.cpp` is the broad GGUF compatibility fallback. It supports Apple Silicon/Metal, many quantization formats, and `llama-server` for an OpenAI-compatible local HTTP API.

Use it when:

- a desired model is only available as GGUF;
- an OpenAI-compatible local endpoint is easier to wire into a runner;
- MLX conversion is inconvenient.

## Why Not Make LM Studio/Ollama The Core

LM Studio is useful because it supports local model downloads, Apple Silicon, llama.cpp, MLX models, MCP, and local OpenAI-compatible APIs. It is a good operator-facing wrapper.

Ollama is useful for simple model management and local serving.

But for reproducible runner automation, prefer scriptable low-level routes first:

1. `mlx-lm`;
2. `llama.cpp` / `llama-server`;
3. LM Studio/Ollama wrapper when convenient.

## Download Policy

No model download was performed while creating this plan.

Rules:

- Any single model file over 100MB must be downloaded with command-local no-proxy settings.
- Any single model file over 1GB requires explicit user approval before download.
- Do not change global proxy settings.
- Record URL, expected size, SHA256, command, and no-proxy evidence.

Template:

```bash
env -u http_proxy -u https_proxy -u all_proxy -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY \
  curl --noproxy '*' -L --fail --continue-at - --output OUTPUT URL
```

## First Proof Plan

1. Install/check `mlx-lm` only if not already available.
2. Select a small MLX-compatible instruct model first.
3. If model is over 100MB, use no-proxy download evidence.
4. Run a task-packet summarization prompt.
5. Record latency, memory, output quality, and whether it can replace paid runner usage for this kind of work.

## Acceptance

The Mac local model lane is ready only when:

- one local command runs successfully;
- no large-download rule is violated;
- a report shows the model can summarize or classify a visual-upgrade task packet;
- the route is documented as either useful, too slow, or not worth continuing.

