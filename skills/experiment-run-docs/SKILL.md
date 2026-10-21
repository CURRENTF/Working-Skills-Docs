---
name: experiment-run-docs
description: Maintain experiment records limited to the launch command, code Git commit, and final results. Use for research experiments whose results affect a decision; skip routine smoke runs and one-off diagnostics.
---

# Experiment Run Docs

## Value Threshold

Keep a record only when it changes a future decision, prevents a repeated
mistake, or documents a currently useful workflow. Running or analyzing an
experiment does not by itself require a new record.

Before adding content, find the existing relevant record. Merge duplicates and
remove content confirmed to be outdated or inconsistent with established facts.
Leave content of uncertain validity unchanged.

## Record Content

Use only these fields:

- Launch command, including the working directory and arguments needed to run it.
- The code's Git commit.
- Final experimental results, including an unsuccessful outcome when applicable.

Intermediate records use the same fields. Leave results empty until final
results are available, then update the same record. Do not append progress,
retry history, environment inventories, or execution diaries.

Do not archive source code, worktree patches, source snapshots, or per-file
source hashes. A dirty worktree does not block running or recording an
experiment. Do not require a clean commit, source equality, or source recovery.

## Placement

- If the project defines an official result location, keep its final record there.
- Use `research-vault-docs` for a private record that meets the value threshold;
  do not duplicate a repository-owned result in the vault.
- Keep stable setup, runbooks, architecture, and parameter semantics in the repo.
- Do not add private-vault paths or links to public project documentation.

## Template

```markdown
- Launch: `cd <project> && <command with arguments>`
- Git commit: `<commit>`
- Final results:
```

For multiple variants, a result table may replace the last field. Identify the
metric and unit in that table; do not repeat its contents in prose. Never record
credentials, tokens, or unredacted secrets.

## Final Response

Name the record path only when a record was created or updated. Report its Git
state accurately; this skill does not authorize committing or pushing.
