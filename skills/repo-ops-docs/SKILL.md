---
name: repo-ops-docs
description: 非代码运行经验与流程沉淀规则。Use when discovering, running, or documenting repository-specific operational workflows such as training servers, inference/API servers, Unreal Engine data-generation servers, dataset/model downloads, environment setup, launch commands, ports, proxies, storage paths, and recurring troubleshooting. Capture project-specific knowledge in that repo's docs, and promote reusable patterns to Working-Skills-Docs docs when appropriate.
---

# Repo Ops Docs

Use this skill when operational knowledge matters more than code changes: how to start services, run training, generate data, download datasets/models, choose paths, configure proxies, or recover from common runtime failures.

## Core Workflow

1. Read the repo first: `README*`, `docs/`, launch scripts, config files, `.env.example`, `scripts/`, `Makefile`, and recent logs if relevant.
2. Distinguish facts from guesses. Document only commands, paths, ports, env vars, assumptions, and failure modes that were observed, tested, or explicitly provided by the user.
3. Put project-specific knowledge in the current repo, usually under `docs/`.
4. Put reusable cross-repo patterns in this `Working-Skills-Docs` repo when it is the current repo or when the user explicitly asks to update it.
5. Keep docs actionable: exact commands, working directory, required environment, expected outputs, where artifacts land, and how to stop or clean up.
6. Prefer updating an existing relevant doc over creating a new one. Create a new doc only when no suitable location exists.

## What To Capture

- Training server startup: environment, command, config, GPU requirements, ports, log paths, checkpoints, resume behavior, and stop procedure.
- Inference/API server startup: model path, host/port, health check, request example, logs, and common startup failures.
- UE or simulator data-generation server startup: editor/headless mode, map/scene, RPC or streaming ports, asset/data output path, synchronization with Python clients, and shutdown.
- Dataset/model download: source, target directory, checksum or integrity check if available, proxy requirements, resume strategy, and expected disk usage.
- Runtime conventions: conda env, Python/UE version, CUDA version, cache dirs, storage policy, temporary script location, and long-running process management.
- Troubleshooting: symptom, likely cause, quick check, fix, and how to verify.

## Doc Placement

- If the repo already has `docs/`, add or update a focused file there.
- If the repo lacks docs, create `docs/README.md` for an index and one focused doc such as `docs/training.md`, `docs/data-generation.md`, or `docs/datasets.md`.
- If knowledge spans multiple operations, prefer small topic docs plus an index instead of one long catch-all page.
- In `Working-Skills-Docs`, place human-readable references under `docs/<skill-or-topic>/` and update `docs/README.md`.

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
- Mention uncertainty explicitly with `TBD` or `Observed on <date>` rather than smoothing it over.
- When docs become generally useful, propose or add a concise generalized version to `Working-Skills-Docs/docs/`.
