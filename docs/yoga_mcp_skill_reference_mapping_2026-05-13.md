# Yoga MCP And Skill Reference Mapping - 2026-05-13

## Scope

The user asked to reference Yoga `/vol1/maint` when configuring local coding-agent MCP and skill support for this project.

This document records what was observed from Yoga and what was safely mapped locally.

## Yoga Practices To Adopt

### 1. Agent Entry Files Are Contracts

Yoga keeps strong `CLAUDE.md` / `AGENTS.md` instructions:

- read the right entry docs first;
- protect credentials;
- verify live facts before changing system surfaces;
- update docs when changing tooling;
- keep agent behavior narrow and auditable.

Local mapping:

- `CLAUDE.md`
- `GEMINI.md`
- `AGENTS.md`
- `.claude/agents/*.md`
- `.claude/skills/local-3d-asset-factory-orchestrator/SKILL.md`
- `.kimi/skills/local-3d-asset-factory-orchestrator/SKILL.md`

### 2. MCP Stdio Must Not Pollute stdout

Yoga's MiniMax MCP maintenance notes identified stdout pollution as a real MCP failure mode. Local custom MCP servers therefore write protocol data only to stdout and trace/log only to optional files.

Local mapping:

- `/Users/yuanshaochen/Projects/local-coding-runners/bin/managed-artifact-mcp`
- `/Users/yuanshaochen/Projects/local-coding-runners/bin/managed-game-factory-mcp`

### 3. MiniMax Endpoint Boundaries Matter

Yoga records that MiniMax Anthropic-compatible endpoint and MiniMax MCP endpoint are different:

- Anthropic-compatible model calls may use a `/anthropic` base URL.
- MiniMax MCP host must not reuse the `/anthropic` path.

Local mapping:

- `claudeminmax` remains an Anthropic-compatible Claude Code wrapper.
- No direct MiniMax coding-plan MCP is enabled locally until a local wrapper is created and verified with the correct host and secret handling.

### 4. Use Capability Snapshots

Yoga keeps runner capability snapshots and validation summaries, rather than relying on memory.

Local mapping:

- `docs/runner_control_readiness_2026-05-13.md`
- `config/lanes_visual_upgrade_2026-05-13.yaml`
- `tasks/visual_upgrade/`

### 5. Skills Should Be Live, Not Just Mentioned

Yoga has repo-local `.claude/skills/gitnexus/*/SKILL.md` and entry docs that tell agents when to use them.

Local mapping:

- Project-local Claude skill: `.claude/skills/local-3d-asset-factory-orchestrator/SKILL.md`
- Project-local Kimi skill: `.kimi/skills/local-3d-asset-factory-orchestrator/SKILL.md`
- Gemini-linked skill: `/Users/yuanshaochen/.gemini/skills/local-3d-asset-factory-orchestrator`

## Yoga MCPs Not Blindly Copied

These Yoga MCPs are useful but not blindly enabled locally because they require live local services, keys, or browser surfaces:

- `context7`
- `gitnexus`
- `chatgptrest`
- `playwright`
- `chrome-devtools`
- `tavily`
- `brave-search`
- `MiniMax` direct MCP
- `glm-router`

## Local MCPs Enabled Now

### `managed-artifact-verifier`

Purpose:

- verify artifact hash manifests.

Status:

- Connected in Claude-compatible workers.
- Connected in Gemini.

### `managed-game-factory`

Purpose:

- `repo_status_summary`
- `list_visual_upgrade_tasks`
- `validate_asset_packet`
- `validate_no_proxy_download_record`
- `verify_artifact_hashes`

Status:

- Connected in Claude-compatible workers.
- Connected in Gemini.
- Offline and read-only.
- Restricted to `/Users/yuanshaochen/Projects/ai-game-generation-research`.

## Candidate Next MCPs

### GitNexus

Useful for:

- code impact analysis;
- refactor safety;
- execution-flow understanding.

Current local status:

- `npx` exists on Mac.
- No local GitNexus MCP has been enabled yet.

Next safe step:

- create a separate task to test GitNexus indexing of this repo;
- do not add it to all runners until the index exists and MCP health passes.

### Search MCPs

Useful for:

- tool research;
- package/doc discovery.

Current local status:

- no local Brave/Tavily MCP wrapper verified;
- no local keys should be copied or printed in this repo.

Next safe step:

- use Codex web search for current research unless a no-secret local search MCP wrapper is explicitly configured.

### Browser MCPs

Useful for:

- browser/CDP screenshot gates;
- runtime UI testing.

Current local status:

- this repo already has local CDP evidence scripts;
- no project-scoped external browser MCP is required yet.

Next safe step:

- keep browser/CDP gates as repo scripts first;
- only add external browser MCP if a concrete task needs it.

