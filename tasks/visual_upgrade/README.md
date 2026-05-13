# Visual Upgrade Task Board

Each task file is a bounded worker packet. Workers may only edit the declared write scope.

## Required Fields

- Task id
- Goal
- Host
- Runner route
- Read scope
- Write scope
- Forbidden paths
- Verification command
- Expected artifacts
- Acceptance gate
- Output summary format

## Safety

- Do not read secrets.
- Do not run package installs unless explicitly authorized.
- Do not download files over 100MB without no-proxy command-local evidence.
- Do not download files over 1GB without explicit user approval.
- Do not modify global proxy settings.
- Do not use destructive git commands.

## Initial Packets

- `review_plan_packet_001.md` - read-only external review for runner/control readiness.
- `asset_registry_v2_001.md` - asset packet schema, registry v2, validator, and tests.
- `threejs_loader_migration_001.md` - official Three.js GLTFLoader/KTX2/Meshopt-ready runtime path.
- `hero_rifle_v2_001.md` - first hero weapon PBR asset route.
- `rainy_checkpoint_scene_001.md` - 12m x 18m rainy checkpoint scene module.
- `homepc_gpu_job_contract.md` - HomePC GPU job packet contract and no-proxy download record shape.
