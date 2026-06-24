---
name: repo-ops-docs
description: 非代码运行经验与流程沉淀规则。Use when discovering, running, or documenting repository-specific operational workflows such as training servers, inference/API servers, Unreal Engine data-generation servers, dataset/model downloads, environment setup, launch commands, ports, proxies, storage paths, and recurring troubleshooting. Capture stable project runbooks in repo docs, dated operational history in the LeafWiki research vault when available, and promote reusable patterns to Working-Skills-Docs docs when appropriate.
---

# Repo Ops Docs

Use this skill when operational knowledge matters more than code changes: how to start services, run training, generate data, download datasets/models, choose paths, configure proxies, or recover from common runtime failures.

## LeafWiki Research Vault

- Prefer LeafWiki for dated operational observations, failed attempts, one-off server state, and cross-project lessons that would clutter a repo. Default base URL: `${LEAFWIKI_RESEARCH_BASE_URL:-http://8.134.70.136:8080}`.
- Use repo `docs/` for stable, current runbooks that should travel with the code: setup, launch, verify, stop, reproducibility, and current troubleshooting.
- Before writing new operational notes, search LeafWiki when credentials are available:

```bash
curl -fsS "${LEAFWIKI_RESEARCH_BASE_URL:-http://8.134.70.136:8080}/api/research/docs/search?q=<topic>&project=<project>&limit=10" \
  -H "X-Research-Password: $LEAFWIKI_RESEARCH_API_PASSWORD"
```

- If credentials are missing on the user's trusted workstation and SSH is available, load them without printing:

```bash
LEAFWIKI_RESEARCH_API_PASSWORD=$(ssh root@8.134.70.136 "sed -n 's/^LEAFWIKI_RESEARCH_API_PASSWORD=//p' /opt/leafwiki/.env")
```

- For create/update/read endpoint shapes, use `../experiment-run-docs/references/leafwiki-research-api.md`.

## Core Workflow

1. Read the repo first: `README*`, `docs/`, launch scripts, config files, `.env.example`, `scripts/`, `Makefile`, and recent logs if relevant.
2. Distinguish facts from guesses. Document only commands, paths, ports, env vars, assumptions, and failure modes that were observed, tested, or explicitly provided by the user.
3. Put stable project-specific knowledge in the current repo, usually under `docs/`.
4. Put dated run history, transient server state, failed attempts, and cross-project context in LeafWiki when available.
5. Keep docs actionable: exact commands, working directory, required environment, expected outputs, where artifacts land, and how to stop or clean up.
6. Prefer updating an existing relevant doc over creating a new one. Create a new doc only when no suitable location exists.
7. Keep stable user-facing docs separate from dated development notes and experiment records. See `docs/repo-ops-docs/documentation-structure.md` in Working-Skills-Docs for the recommended layout.
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
- If docs contain many dated run records or change logs, keep them but move them under `docs/dev-notes/` and make `docs/README.md` point first to stable docs such as `architecture.md`, `reproducibility.md`, setup, datasets, and benchmark runbooks.
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
- Stable docs should describe the current workflow in present tense. Put chronological "what changed" detail in `docs/dev-notes/` unless it explains a current compatibility constraint.
- When docs become generally useful, propose or add a concise generalized version to `Working-Skills-Docs/docs/`.
