# Coding Runner MCP And Skill Control - 2026-05-13

## Purpose

This note records the local coding-agent control plane for the full PUBG-like
asset factory goal. The point is not just to have Kimi, MiniMax, and Gemini
installed; they need enough MCP and skill context to do useful bounded work
without forcing Codex to spend all tokens on mechanical tasks.

## Local Runner Root

```text
/Users/yuanshaochen/Projects/local-coding-runners
```

Private credentials and provider configs are kept outside this repository and
are intentionally not copied here.

## Yoga Reference Checked

The YogaS2 `/vol1/maint` reference was inspected for runner and MCP practice.
Relevant references found there include:

- `/vol1/maint/CLAUDE.md` with GitNexus MCP practice for code impact review;
- `/vol1/maint/skill.md` for maint operations runbook conventions;
- `/vol1/maint/docs/2026-04-07_gemini_batch_wrapper_31_preview_alignment.md`;
- `/vol1/maint/docs/2026-04-22_kimi_code_and_cli_runbook.md`;
- Kimi/MiniMax/Gemini wrapper scripts under `/vol1/maint/ops/scripts/`.

Key imported operating lessons:

- Gemini must not silently fall back to an older default model; the local review
  wrapper pins `gemini-3.1-pro-preview`.
- Kimi is the stronger complex coding/review runner.
- MiniMax is kept for simple mechanical edits, schema/report/checklist work, and
  low-risk first-pass review.
- MCP tools must be explicit and testable; wrapper availability alone is not
  enough.

## Current Local MCP State

Current runner capability audit shows these MCP servers connected for
Claude-compatible Kimi/MiniMax and Gemini:

```text
managed-artifact-verifier: connected
managed-game-factory: connected
```

The `managed-game-factory` MCP is a local read-only server for this repository.
It exposes offline helper tools for:

- repo status summary;
- visual-upgrade task packet listing;
- asset packet structure and texture-map coverage checks;
- no-proxy download record checks;
- artifact hash verification.

This is deliberately narrow. It gives external runners enough project-specific
context for this goal without giving them broad, hidden, or credential-bearing
access.

## Current Skill State

Gemini capability audit shows this project-specific skill enabled:

```text
local-3d-asset-factory-orchestrator
```

That skill encodes the current project rules:

- full local asset-factory rebuild, not light visual polish;
- no-proxy evidence for large downloads;
- PBR asset packet requirements;
- Kimi/Gemini/MiniMax routing;
- HomePC GPU for Hunyuan/ComfyUI/TRELLIS/Blender;
- Mac M2 Max as control plane and local fallback runner.

## Runner Routing

Use this default routing while the goal is active:

| Runner | Best use | Avoid |
| --- | --- | --- |
| Kimi | complex code, blocker analysis, implementation critique, Blender/Three.js integration review | vague mechanical chores with no bounded prompt |
| Gemini CLI | broad research, visual direction critique, route comparison, final review, must use `gemini-3.1-pro-preview` | default model calls |
| MiniMax | schema/report/hash/checklist/formatting and simple mechanical edits | architecture, ambiguous debugging, complex implementation |
| Codex | orchestration, merge review, evidence gates, final judgement | doing every repetitive worker task personally |
| HomePC GPU | Hunyuan3D, ComfyUI, TRELLIS, Blender render/bake | paid-proxy downloads |

## Verification Commands

```bash
/Users/yuanshaochen/Projects/local-coding-runners/bin/runner-capabilities-audit
/Users/yuanshaochen/Projects/local-coding-runners/bin/runner-gemini-review --help
/Users/yuanshaochen/Projects/local-coding-runners/bin/runner-review --help
/Users/yuanshaochen/Projects/local-coding-runners/bin/runner-worker --help
```

Last observed capability audit:

```text
Claude MiniMax MCP: managed-artifact-verifier connected, managed-game-factory connected
Claude Kimi MCP: managed-artifact-verifier connected, managed-game-factory connected
Gemini MCP: managed-artifact-verifier connected, managed-game-factory connected
Gemini skill: local-3d-asset-factory-orchestrator enabled
```

## Practical Dispatch Rule

Every external runner task must be saved as a file under
`tasks/pubg_like_full_rebuild/` or the relevant experiment report directory and
must include:

- goal;
- runner/host recommendation;
- read-only files;
- write scope;
- forbidden paths;
- commands or command placeholders;
- expected artifacts;
- acceptance gate;
- output summary format.

Runner output should also be saved to disk before Codex uses it for integration
or final judgement.
