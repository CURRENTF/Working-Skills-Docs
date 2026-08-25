---
name: repo-ops-docs
description: 非代码运行经验与流程沉淀规则。Use when discovering, running, or documenting repository-specific operational workflows such as training servers, inference/API servers, Unreal Engine data generation, dataset/model downloads, environment setup, launch commands, ports, proxies, storage paths, and recurring troubleshooting. Keep stable runbooks in the project repo and dated or private history in Research-Vault.
---

# Repo Ops Docs

Use this skill when operational knowledge matters more than code changes: how to start services, run training, generate data, download datasets/models, choose paths, configure proxies, or recover from common runtime failures. Use `research-vault-docs` for private-vault discovery, de-duplication, file placement, and Git synchronization.

## Placement Boundary

- Put stable, current runbooks that should travel with the code in the project repo: setup, launch, verify, stop, reproducibility, and current troubleshooting.
- Put dated operational observations, failed attempts, one-off server state, exact private paths, and cross-project lessons in `~/Documents/Codex/Research-Vault`.
- Keep project docs self-contained. Do not commit private-vault paths, links, indexes, or Git metadata into project repos unless the user explicitly requests a private integration.
- Promote reusable agent guidance to the relevant skill in `Working-Skills-Docs`, not to a second top-level documentation tree.

## Core Workflow

1. Read the repo first: `README*`, `docs/`, launch scripts, config files, `.env.example`, `scripts/`, `Makefile`, and recent logs if relevant.
2. Distinguish facts from guesses. Document only commands, paths, ports, env vars, assumptions, and failure modes that were observed, tested, or explicitly provided by the user.
3. Put stable project-specific knowledge in the current repo, usually under `docs/`.
4. Put dated run history, transient server state, failed attempts, private context, and cross-project lessons in Research-Vault using `research-vault-docs`.
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
- If docs contain many dated run records or change logs, move the private or transient records to Research-Vault. Keep repo `docs/dev-notes/` only when repo-local history is useful to all repo readers or explains a current compatibility constraint.
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
- Mention uncertainty explicitly with `TBD` or `Observed on <date>` rather than smoothing it over.
- Stable docs should describe the current workflow in present tense. Put chronological "what changed" detail in Research-Vault, or in `docs/dev-notes/` only when repo-local history is explicitly useful to all repo readers or explains a current compatibility constraint.
- When guidance becomes generally useful across repositories, propose or add a concise generalized version to the relevant skill in `Working-Skills-Docs`.
