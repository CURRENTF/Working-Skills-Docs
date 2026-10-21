---
name: repo-ops-docs
description: Maintain useful, current repository runbooks and reusable operational lessons. Use when setup, launch, or troubleshooting work produces knowledge that changes future decisions or prevents repeated mistakes; skip routine observations and one-off diagnostics.
---

# Repo Ops Docs

Use this skill when operational knowledge matters more than code changes: how to start services, run training, generate data, download datasets/models, choose paths, configure proxies, or recover from common runtime failures. Use `research-vault-docs` for private-vault discovery, de-duplication, file placement, and Git synchronization.

## Value Threshold And Maintenance

Document only information that changes future decisions, prevents repeated
mistakes, or describes a currently useful workflow. A successful command,
one-off server state, or failed attempt alone does not justify a record.

When adding content, update the relevant existing document, merge duplicates,
and remove content confirmed to be outdated or inconsistent with established
facts. Leave content of uncertain validity unchanged.

Experiment records, including intermediate records, contain only the launch
command, the code's Git commit, and final results. Leave results empty until
available and update the same record. Do not archive source code, worktree
patches, source snapshots, or per-file source hashes; a dirty worktree is allowed.

## Placement Boundary

- Put stable, current runbooks that should travel with the code in the project repo: setup, launch, verify, stop, reproducibility, and current troubleshooting.
- Put finalized official results in the repository's designated official
  experiment directory, using only the launch command, Git commit, and final results.
- Put private operational lessons that meet the value threshold in Research-Vault.
- Keep project docs self-contained. Do not commit private-vault paths, links, indexes, or Git metadata into project repos unless the user explicitly requests a private integration.
- Promote reusable agent guidance to the relevant skill in `Working-Skills-Docs`, not to a second top-level documentation tree.

## Core Workflow

1. Read the repo first: `README*`, `docs/`, launch scripts, config files, `.env.example`, `scripts/`, `Makefile`, and recent logs if relevant.
2. Distinguish facts from guesses. Document only commands, paths, ports, env vars, assumptions, and failure modes that were observed, tested, or explicitly provided by the user.
3. Put stable project-specific knowledge in the current repo, usually under `docs/`.
4. Use `research-vault-docs` only for valuable private lessons; do not create routine operational histories or duplicate repository-owned results.
5. Keep docs actionable: exact commands, working directory, required environment, expected outputs, where artifacts land, and how to stop or clean up.
6. Prefer updating an existing relevant doc over creating a new one. Create a new doc only when no suitable location exists.
7. Keep stable user-facing docs separate from dated development notes and experiment records.
8. Put reusable cross-repo patterns in this `Working-Skills-Docs` repo when it is the current repo or when the user explicitly asks to update it.

## What To Capture

- Training server startup: environment, command, config, GPU requirements, ports, log paths, checkpoints, resume behavior, and stop procedure.
- Inference/API server startup: model path, host/port, health check, request example, logs, and common startup failures.
- UE or simulator data-generation server startup: editor/headless mode, map/scene, RPC or streaming ports, asset/data output path, synchronization with Python clients, and shutdown.
- Dataset/model download: source, target directory, checksum or integrity check if available, proxy requirements, resume strategy, and expected disk usage.
- Runtime conventions: conda env, Python/UE version, CUDA version, cache dirs, storage policy, temporary script location, and long-running process management.
- Troubleshooting: symptom, likely cause, quick check, fix, and how to verify.

## Doc Placement

- If the repo already has `docs/`, add or update a focused file there only for stable current workflow.
- If the repo lacks docs, create `docs/README.md` for an index and one focused doc such as `docs/training.md`, `docs/data-generation.md`, or `docs/datasets.md`.
- If knowledge spans multiple operations, prefer small topic docs plus an index instead of one long catch-all page.
- Do not move dated histories to Research-Vault merely because they exist. Apply the value threshold and remove confirmed obsolete or inconsistent content when updating the relevant document.
- In `Working-Skills-Docs`, place supporting references under the owning `skills/<skill>/references/` directory and link them from that skill when they are needed.

## Suggested Doc Shape

Use the sections that fit; omit irrelevant ones.

```markdown
# <Workflow Name>

## Purpose

## Prerequisites

## Paths

## Start

## Verify

## Stop

## Outputs

## Troubleshooting

## Notes
```

## Quality Bar

- Commands must include the working directory when it matters.
- Long or fragile commands should be converted into repo-local scripts only if the user wants automation; otherwise document them as commands.
- Do not claim a command works unless it was run or the source repo clearly documents it.
- Keep secrets out of docs. Use placeholder names for tokens, private URLs, and credentials.
- Do not invent facts when documenting new knowledge. Leave existing content of uncertain validity unchanged.
- Stable docs should describe the current workflow in present tense. Do not append chronological execution history.
- Update cross-repository guidance in `Working-Skills-Docs` only within the authorized task scope.
