---
name: research-vault-docs
description: Search, create, update, and sync private Markdown records in the user's GitHub-backed Research-Vault. Use for dated experiment/evaluation records, repository operations, troubleshooting, investigations, private project history, and cross-project lessons. Keep stable project documentation in the project repo instead.
---

# Research Vault Docs

Use the private filesystem-first vault as the source of truth for dated or
private research history. Domain skills such as `experiment-run-docs` and
`repo-ops-docs` decide what facts matter; this skill handles locating, searching,
placing, editing, and syncing the records.

## Locate Or Clone The Vault

The canonical checkout is `~/Documents/Codex/Research-Vault` and its remote is
`git@github.com:CURRENTF/Research-Vault.git`.

1. Check whether `~/Documents/Codex/Research-Vault/.git` exists.
2. If the checkout is absent, create `~/Documents/Codex` and clone the remote to
   exactly `~/Documents/Codex/Research-Vault`.
3. If the target exists but is not a Git repository, or its `origin` points to a
   different remote, stop without deleting or overwriting it and report the
   conflict.
4. Do not add the vault as a submodule of a project repository.

The clone step is part of this workflow and needs no separate service password
or API configuration. If GitHub authentication, network access, or cloning fails,
preserve the record in the run output directory when possible and report that
the private vault was not updated.

## Placement Boundary

- Put dated experiments, failed attempts, transient machine state, exact local
  paths, private project history, operational incidents, and cross-project
  lessons in the vault.
- Put stable setup, launch instructions, architecture, parameter semantics,
  reproducibility guidance, and public runbooks in the corresponding project
  repository.
- Do not add vault paths, links, indexes, or Git metadata to project repos unless
  the user explicitly asks for a private integration.

## Search And Place

Before writing, inspect the vault worktree and search by project, run root,
config path, artifact path, error phrase, and method or benchmark name. Reuse an
existing record when those fields identify the same event.

Use these paths, creating directories only when a real record needs them:

```text
projects/<project>/experiments/<YYYY>/<MM>/<slug>.md
projects/<project>/operations/<YYYY>/<MM>/<slug>.md
projects/<project>/investigations/<YYYY>/<MM>/<slug>.md
shared/<topic>/<slug>.md
```

Use the repository's established project spelling when it exists. Prefer one
file per distinct run, incident, or investigation; append progress and final
results to that file instead of creating retry duplicates or editing a global
index.

Include a compact identity block near the top with the applicable project,
record kind, date, status, and a stable fingerprint such as run root, config,
result path, or issue identity. A timestamp alone is not a sufficient
fingerprint. Write `TBD` or `not captured` rather than inventing missing facts.
For imported records, treat the YAML `status` as authoritative when an older
status remains in the preserved historical body, and retain
`legacy_leafwiki_*` fields as provenance.

## Evidence And Safety

- Support claims with actual commands, configs, logs, result artifacts, Git
  state, or user-provided facts.
- Store paths and concise evidence summaries, not large logs, datasets, model
  weights, checkpoints, or generated binaries.
- Never store credentials, API keys, access tokens, tokenized URLs, or other
  unredacted secrets.
- Inspect `git status` before editing and preserve unrelated work. If the vault
  is dirty, do not pull, rebase, or mix unrelated files into a commit.
- If the worktree is clean and an upstream exists, update it with a non-rewriting
  pull before writing. Never force-push the vault.

## Persist And Report

When the active task includes persisting an experiment or operations record,
validate the touched Markdown, commit only the record files owned by that task,
and perform a normal push. If unrelated changes, a conflict, or a push failure
prevents safe syncing, leave the record recoverable locally and report its exact
state instead of discarding or overwriting work.

In the final response, name the vault record path, its status, and whether it was
pushed. Also point to the main log/result artifacts outside the vault when they
matter.
