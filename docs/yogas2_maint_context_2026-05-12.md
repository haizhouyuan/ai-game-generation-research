# YogaS2 MAINT Context For Game-Generation Work - 2026-05-12

## Purpose

This note records the machine/network/project context learned from YogaS2's MAINT repository so future game-generation work does not guess host roles, paths, ports, or project ownership.

Source repository:

`ssh yoga:/vol1/maint`

This is a read-only summary. Secret-bearing files were not copied or quoted.

## What `/vol1/maint` Is

`/vol1/maint` is the machine hub for YogaS2, the family network, and the agent runtime environment.

It is not a normal project repository. It is the canonical entry for:

- host identity and access paths;
- home network topology;
- Tailscale, SSH, VNC, Guacamole, and router-backed exposure;
- ports, local control planes, and MCP/browser lanes;
- secret/privacy handling policy;
- repo family and worktree freshness rules;
- operations scripts, service inventory, backup routes, incidents, and historical evidence.

## Read Docs

Primary docs read or indexed:

- `/vol1/maint/README.md`
- `/vol1/maint/AGENTS.md`
- `/vol1/maint/docs/machine_agent_entry.md`
- `/vol1/maint/docs/infra_registry.md`
- `/vol1/maint/docs/project_workspace_registry.md`
- `/vol1/maint/docs/repo_governance.md`
- `/vol1/maint/docs/privacy_and_secret_governance.md` headings only / policy-level only
- `/vol1/maint/docs/ops_manual.md`
- `/vol1/maint/network/firewall.md`
- `/vol1/maint/network/mihomo.md`
- `/vol1/maint/services/autostart.md`
- `/vol1/maint/docs/2026-05-12_macbook_pro_tailscale_vnc_codex_access.md`
- `/vol1/maint/docs/2026-04-28_tailscale_external_deploy_skill_and_yogas2_port_map.md`
- `/vol1/maint/docs/2026-04-24_ax3000t_relay_topology_and_wifi_dhcp_findings.md`
- `/vol1/maint/state/agenting_snapshots/latest.json`
- `/vol1/maint/docs/superpowers/plans/2026-05-11-ai-cad-game-research-controller-plan.md`
- `/vol1/maint/docs/homepc_gpu_research_executor_20260511.md`
- `/vol1/maint/docs/m9_research_executor_readiness_20260511.md`
- `/vol1/maint/docs/managed_agents/mac_game_worker_pilot_task_20260512.md`
- `/vol1/maint/docs/managed_agents/mac_game_worker_p27_release_packet_task_20260512.md`

Observed scale:

- `docs/`: about 760 matching document/config/script files
- `network/`: about 138 matching files
- `services/`: about 54 matching files
- `memory/`: about 22 matching files
- `MAIN/`: about 9 matching files
- `state/agenting_snapshots/latest.json`: 83 repos and 175 worktrees in the latest snapshot, generated `2026-04-22 19:04:24 CST`

## Host Roles

| Host | Role | Current use for this project |
|---|---|---|
| YogaS2 | Machine hub, MAINT owner, family network/control-plane registry, public/Tailscale entrypoint | Source of truth for topology, project registry, service lanes, and future managed-agent coordination |
| MacBook Pro | Current Codex App/controller workstation for this active game-generation session | Main live workspace at `/Users/yuanshaochen/Projects/ai-game-generation-research` |
| HomePC | GPU execution node and backup peer | TRELLIS/ComfyUI/Godot/Blender/GPU asset generation and validation |
| M9 | Supporting Ubuntu GUI/browser/build/test executor | Potential non-GPU Godot/Blender/Unity/editor/browser validation host, not yet central to current work |
| YogaS2 itself | Lightweight Node/Python/git/curl host, no NVIDIA GPU | Useful for metadata/source checks, not for GPU generation |

## Current Access Facts

Mac to YogaS2:

- `ssh yoga`
- fallback: `ssh yoga-lan`
- fallback: `ssh yoga-pub`

Mac to HomePC:

- `ssh homepc`
- direct LAN target: `192.168.31.38`

YogaS2 to Mac:

- Tailscale hostname: `macbook-pro.tail594315.ts.net`
- Tailscale IP recorded in MAINT: `100.82.212.108`
- SSH and VNC were documented as available on `22` and `5900`

YogaS2 to HomePC:

- Current true HomePC LAN identity is `192.168.31.38` behind the balcony router.
- `192.168.1.17` is a historical trap: it is the balcony router WAN/DMZ entry, not HomePC's real LAN NIC identity.
- Some older YogaS2 tunnel docs still mention `192.168.1.17`; those paths are marked verify-first or disabled/on-demand.

## Home Network Topology

Confirmed high-level topology from MAINT:

```text
HS8145C optical modem / main LAN 192.168.1.0/24
├─ YogaS2: 192.168.1.7
└─ main-bedroom AX3000T relay: current admin IP 192.168.1.68
   └─ balcony router WAN/DMZ: historical 192.168.1.17
      └─ balcony LAN 192.168.31.0/24
         ├─ HomePC: 192.168.31.38
         └─ MacBook Pro: observed on balcony LAN
```

Operational warning:

- Do not rely on main-bedroom AX3000T Wi-Fi as a stable client access surface in wired relay mode.
- Do not change router mode/relay role remotely without a maintenance window.
- Prefer Tailscale or direct LAN SSH over ad-hoc router port exposure.

## Exposure And Control Planes

Important YogaS2 routes and ports from MAINT:

- Public/router-backed SSH: `22`, `2222`, `60022`
- Preferred documented remote SSH entry: `fnos.dandanbaba.xyz:60022` or `tailscale.dandanbaba.xyz:60022`
- Tailscale Serve/Funnel hostname: `yogas2.tail594315.ts.net`
- Guacamole via Tailscale Serve: `https://yogas2.tail594315.ts.net:9443/` when stack is running
- Paperclip Labebe demo via Tailscale Serve: `https://yogas2.tail594315.ts.net:9447/`
- Current Labebe DTC Funnel demo: `https://yogas2.tail594315.ts.net:10000/`
- General Codex browser CDP lane: `127.0.0.1:9222` on YogaS2 via `codex-general-chrome-cdp.service`
- ChatgptREST browser lane: `127.0.0.1:9226`, reserved for ChatgptREST
- GitNexus shared HTTP MCP: `127.0.0.1:18713`
- ChatgptREST dashboard/control surfaces: local-only ports in the `187xx` range
- Multica public backend: `:18783`

Safety rule:

- `fnos.dandanbaba.xyz:PORT` and `yogas2.tail594315.ts.net:PORT` are not interchangeable.
- For temporary demos, check localhost first, then use the documented Tailscale Serve/Funnel skill/runbook.
- Do not overwrite existing Tailscale Serve mappings casually.

## Proxy And Download Boundary

YogaS2 has Mihomo/mixed proxy infrastructure and default shell proxy variables may point at `127.0.0.1:7890`.

For this game-generation work:

- large blobs, models, and engine installers must not be downloaded through metered proxy traffic;
- use command-local proxy cleanup for downloads;
- prefer existing HomePC model caches before fetching new model weights;
- do not change Clash/Mihomo/global proxy settings as a shortcut.

This matches the local Mac policy in `docs/direct_download_policy_2026-05-12.md`.

## Project Registry

MAINT says repo/worktree truth should be resolved in this order:

1. `/vol1/maint/state/agenting_snapshots/latest.json`
2. target repo `git worktree list --porcelain`
3. target repo `git log -1 --date=iso-strict --format='%H %cI %s'`
4. target repo `git status --short`
5. repo-local `AGENTS.md`, `README.md`, docs, closeout, and dev logs

High-signal families in the snapshot:

- `ChatgptREST`
- `homeagent`
- `codexread`
- `openclaw`
- `planning`
- `tmuxagent`
- `ai-cad-research`
- `ai-game-generation-research`
- `multica`
- `paperclip` / `toyresearch`

`/vol1/1000/projects` currently contains many project repos, including:

- `/vol1/1000/projects/ai-game-generation-research`
- `/vol1/1000/projects/ai-cad-research`
- `/vol1/1000/projects/ChatgptREST`
- `/vol1/1000/projects/homeagent`
- `/vol1/1000/projects/codexread`
- `/vol1/1000/projects/openclaw`
- `/vol1/1000/projects/planning`
- `/vol1/1000/projects/multica`
- `/vol1/1000/projects/paperclip`
- `/vol1/1000/projects/toyresearch`

## Game-Generation Repo Relationship

YogaS2 has:

`/vol1/1000/projects/ai-game-generation-research`

Live check on YogaS2:

- HEAD: `eaa93af86b6125f13caad2caab9d1d01365b74ef`
- Commit date: `2026-05-12T06:26:47+08:00`
- Subject: `experiments: add P25 dependency graph validator`
- The YogaS2 repo currently has many untracked docs/experiments from earlier work.

Mac has the copied working repo:

`/Users/yuanshaochen/Projects/ai-game-generation-research`

This Mac repo is now the live lane for the current user-visible game-generation session. YogaS2 MAINT remains the machine/controller truth surface, not the place to put game-specific experiments.

MAINT already has managed-agent notes for the Mac game lane:

- `/vol1/maint/docs/managed_agents/mac_game_worker_pilot_task_20260512.md`
- `/vol1/maint/docs/managed_agents/mac_game_worker_p27_release_packet_task_20260512.md`

Those docs point to both:

- Mac project: `/Users/yuanshaochen/Projects/ai-game-generation-research`
- Yoga source repo: `/vol1/1000/projects/ai-game-generation-research`

## How This Changes My Positioning

For future game-generation work:

1. I should treat Mac as the active workspace and UX-facing controller for this thread.
2. I should treat YogaS2 MAINT as the source of truth for network, access, service, proxy, host, and project-family facts.
3. I should treat HomePC as the GPU worker, especially for TRELLIS, ComfyUI, local models, Blender/Godot/asset processing, and heavyweight experiments.
4. I should treat M9/YogaS2 as non-GPU support hosts only after install/readiness checks.
5. I should not copy secrets from MAINT, `MAIN/secrets`, browser profiles, OAuth/session files, or SSH private keys into project docs.
6. If I change host access paths, tunnels, service ports, or shared toolchain assumptions, the change belongs in MAINT canonical docs as well as the project-local closeout.

## Immediate Relevance To The Unity/AI Game Chain

- Unity MCP cannot be considered live until a Unity Editor host is verified. MAINT does not currently make YogaS2 a Unity host.
- HomePC has GPU resources and existing TRELLIS/ComfyUI assets; it is the right place for AI asset generation.
- Mac is currently the best place for Codex App orchestration and local Three.js/HTML baseline inspection.
- The original ChatGPT HTML game now captured as P0 in this repo should be treated as project evidence, while MAINT remains the machine/controller map.
- Download/no-proxy handling must respect both Mac Clash constraints and YogaS2 Mihomo constraints.

## Do Not Do

- Do not treat `/vol1/maint` dated incident docs as current truth without checking canonical docs and live state.
- Do not assume `192.168.1.17` is HomePC.
- Do not overwrite Tailscale Serve/Funnel routes without checking the current map.
- Do not use YogaS2 for GPU-heavy model work.
- Do not store game-generation artifacts in MAINT except sanitized controller evidence or explicit raw intake.
- Do not expose or quote secret values from `MAIN/secrets`, SSH configs, browser/session state, or credential inventories.
