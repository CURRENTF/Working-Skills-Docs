---
name: research-vault-docs
description: Search and maintain valuable private research records in Research-Vault. Write only findings that change future decisions, prevent repeated mistakes, or document a currently useful workflow; keep experiment records to launch command, Git commit, and final results.
---

# Research Vault Docs

## Value Threshold And Maintenance

Search without creating a record when existing knowledge answers the question.
Create or update a record only for content that changes future decisions,
prevents repeated mistakes, or documents a currently useful workflow.
Routine checks, failed attempts, and transient machine state alone do not qualify.

Before adding content, search for the same topic or experiment. Update the
existing record, merge duplicates, and remove content confirmed to be outdated
or inconsistent with established facts. Leave content of uncertain validity
unchanged. Do not append execution diaries or preserve superseded content just
because it was previously recorded.

## Locate Or Clone

The canonical checkout is `~/Documents/Codex/Research-Vault`; its remote is
`git@github.com:CURRENTF/Research-Vault.git`.

- Verify an existing checkout has the canonical origin.
- Clone to that location only when the task needs the vault and it is absent.
- If the target is not a Git repository or has another origin, report the
  conflict without deleting or overwriting it.
- If access fails, report the limitation without creating substitute records.

## Placement

- Keep stable project runbooks, architecture, and parameter semantics in the
  project repository. Do not add private-vault links to public docs.
- Keep an official experiment record in its project-designated location rather
  than duplicating it in the vault.
- Use the established project spelling and existing relevant file. For a new
  record, use the appropriate `projects/<project>/experiments/`, `operations/`,
  or `investigations/` directory, or `shared/<topic>/` for cross-project lessons.

## Experiment Records

Record only:

- The launch command, including the working directory and required arguments.
- The code's Git commit.
- Final experimental results, including an unsuccessful outcome when applicable.

Intermediate records use the same fields; leave results empty until available.
Update the same record when final results arrive. Do not add progress logs,
retry histories, environment inventories, artifact indexes, or extra metadata.

Do not archive source code, worktree patches, source snapshots, or per-file
source hashes. A dirty worktree does not block running or recording an
experiment; do not require source equality or a clean commit.

## Safety And Git

- Base new content on observed facts and keep it concise. Never store credentials,
  tokens, tokenized URLs, or other unredacted secrets.
- Inspect Git status before editing. Preserve unrelated changes; do not pull or
  rebase a dirty vault. If clean and tracking an upstream, use `git pull --ff-only`
  before writing. Never force-push.
- Commit or push only when authorized by the user. Keep unrelated files out of
  any authorized commit and report conflicts or failures explicitly.

Name the record path and its actual Git state only when it was created or updated.
