---
name: research-vault-docs
description: Search, create, update, and sync compact private Markdown records in the user's GitHub-backed Research-Vault. Use for dated experiment/evaluation records, repository operations, troubleshooting, investigations, private project history, and cross-project lessons. Keep stable project documentation in the project repo instead.
---

# Research Vault Docs

Use the private filesystem-first vault as the source of truth for dated or
private research history. Domain skills decide what evidence matters; this
skill handles locating, placing, writing, and syncing records.

## Locate Or Clone

The canonical checkout is `~/Documents/Codex/Research-Vault`; its remote is
`git@github.com:CURRENTF/Research-Vault.git`.

1. If `~/Documents/Codex/Research-Vault/.git` exists, verify that `origin`
   matches the canonical remote.
2. If the checkout is absent, create `~/Documents/Codex` and clone the remote to
   exactly `~/Documents/Codex/Research-Vault`.
3. If the target exists but is not a Git repository, or has another origin,
   stop without deleting or overwriting it and report the conflict.

Use a normal clone, not a project submodule. If GitHub authentication, network
access, or cloning fails, preserve the record in the run output directory when
possible and report that the vault was not updated.

## Boundary And Placement

- Put dated experiments, failed attempts, transient machine state, exact local
  paths, private history, operational incidents, and cross-project lessons in
  the vault.
- Keep stable setup, launch instructions, architecture, parameter semantics,
  reproducibility guidance, and public runbooks in the project repo. Do not add
  vault links or Git metadata there unless explicitly asked.
- Before writing, inspect the vault worktree and search by project, run root,
  config, artifact path, error phrase, and method or benchmark name. Update an
  existing record when those fields identify the same event.

Use the established project spelling and these paths:

```text
projects/<project>/experiments/<YYYY>/<MM>/<slug>.md
projects/<project>/operations/<YYYY>/<MM>/<slug>.md
projects/<project>/investigations/<YYYY>/<MM>/<slug>.md
shared/<topic>/<slug>.md
```

Prefer one file per distinct run, incident, or investigation; update it rather
than creating retry duplicates or maintaining a frequently edited global index.
Include a compact identity block with project, kind, date, status, and a stable
fingerprint such as run root, config, result path, or issue identity. Write
`TBD` or `not captured` rather than inventing facts. For imported records, YAML
`status` is authoritative; preserve `legacy_leafwiki_*` provenance fields.

## Concise By Default

Treat a record as an evidence index; durable detail belongs in referenced
configs, manifests, summaries, logs, checkpoints, or result artifacts.

- State status and purpose in one or two lines. Do not reconstruct the
  conversation, predecessor-job history, routine resource gate, or execution
  diary.
- Keep environment description to one compact line per system or a comparison
  table when practical. Record only what affects reproduction or interpretation
  and link a manifest for package inventories and setup history.
- Prefer tables for protocols, variants, environments, failures, and results
  when they replace repeated prose.
- A self-contained result table is authoritative. Do not explain the same
  values, rankings, trends, or speedups below it. Add prose only for a necessary
  caveat or conclusion not already visible in the table.
- Preserve intermediate progress and recovered attempts already written. On
  completion, add a concise final state without deleting or rewriting the
  existing history; avoid repeating it unless it changed the final protocol or
  leaves a material limitation.
- New prose for a routine experiment record should usually fit in about 10-30
  lines, excluding frontmatter, tables, and a necessary exact command. This is
  not a cleanup target for existing content. Expand for load-bearing mechanistic
  evidence, complex incidents, or caveats.

## Evidence, Safety, And Sync

- Support claims with actual commands, configs, logs, result artifacts, Git
  state, or user-provided facts. Store concise pointers, not duplicated config
  contents, package inventories, large logs, datasets, weights, checkpoints, or
  generated binaries.
- Never store credentials, API keys, access tokens, tokenized URLs, or other
  unredacted secrets.
- Inspect `git status` before editing. If the vault is dirty, do not pull,
  rebase, or mix unrelated files into a commit. If clean and tracking an
  upstream, use a non-rewriting pull before writing. Never force-push.
- When the active task includes persisting a record, validate the touched
  Markdown, commit only that task's files, and normally push. On unrelated
  changes, conflict, or push failure, leave the record recoverable locally and
  report its exact state.

In the final response, name the record path, status, push state, and important
external log/result artifacts.
