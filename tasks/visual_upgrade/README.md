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

