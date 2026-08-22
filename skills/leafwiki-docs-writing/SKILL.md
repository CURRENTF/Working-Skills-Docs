---
name: leafwiki-docs-writing
description: Write and maintain private LeafWiki research-vault records for experiments, evaluations, repo operations, troubleshooting, and cross-project lessons while keeping repo docs self-contained. Use when Codex needs to search LeafWiki before writing, create or update dated LeafWiki records, decide whether information belongs in LeafWiki or repo docs, avoid duplicate private records, or answer from LeafWiki context.
---

# LeafWiki Docs Writing

Use this skill for the mechanics and writing policy of the private LeafWiki
research vault. It complements domain skills such as `experiment-run-docs` and
`repo-ops-docs`: those skills decide what domain facts matter; this skill
decides how to search, de-duplicate, place, and write LeafWiki records.

## Placement Boundary

- Put dated experiment runs, failed attempts, transient machine state, exact
  local paths, private project history, and cross-project lessons in LeafWiki.
- Put stable setup, launch, troubleshooting, architecture, parameter semantics,
  and public runbooks in repo `docs/`.
- Do not commit LeafWiki ids, paths, links, or index tables into repo docs
  unless the user explicitly asks for a private/internal repo index.
- Repo docs should only reference repo-local docs, public URLs, and artifact
  paths that are meaningful to other repo readers.
- If the task is plain local Obsidian note organization rather than LeafWiki
  research records, use `obsidian-vault` instead.

## Workflow

1. Identify the project, record type, and durable identity:
   repository, run id, model, dataset, benchmark, method, config path, output
   root, issue, error signature, or operational workflow.
2. Load LeafWiki credentials only from process environment variables, the
   user-global `/home/haojitai/.env`, or the trusted SSH command in the API
   reference. Never print secrets.
3. Search before writing. Use several narrow queries: project + run id, project
   + method, artifact path, error phrase, and config name.
4. Read full Markdown only for relevant search hits. Do not open every result.
5. Reuse an existing record when the same fingerprint, run root, command/config,
   result path, or issue identity matches. Create a new record only when no
   existing note clearly covers the same event.
6. Write one record per distinct run, operational incident, or reusable lesson.
   For partial progress, append events to the same record rather than creating
   a new near-duplicate.
7. After writing, keep the returned LeafWiki id/path in the final response or
   working notes, but do not copy it into repo files by default.

For endpoint details and curl examples, read
`references/leafwiki-research-api.md` before calling or changing the API.

## Fingerprints

Use a stable `fingerprint` so retries and resumed runs de-duplicate safely.
Good fingerprint fields include:

- `run_root`, `output_dir`, `log_path`, or `result_path`
- `config_path`, `manifest_path`, or script path
- `repo`, `branch`, `commit`, and working directory
- `model`, `dataset`, `benchmark`, `method`, and important runtime knobs
- `issue_id`, error signature, port, host, or service name for ops notes

Avoid using only timestamps as identity. They are useful in titles, but weak
for de-duplication.

## Writing Shape

Use concise Markdown with exact evidence. Prefer `TBD` or `not captured` over
inventing missing details.

For experiment or evaluation records, capture:

- status, goal, working directory, exact command, and relevant env vars
- code version, branch, commit, and relevant uncommitted changes
- host, environment, GPU/TP/distributed settings, model, checkpoint, and data
- hyperparameters or runtime knobs that affect results
- logs, result files, raw outputs, parsed outputs, metrics, and artifacts
- final/partial metrics with source paths
- failure reason, exit code, key error line, and next diagnostic step

For operational records, capture:

- workflow or incident name, observed date, host, repo, service, and ports
- start/verify/stop commands, paths, logs, outputs, and cleanup
- symptom, cause, fix, and verification evidence
- whether the fact is stable runbook material or dated local history

For general research context, capture the claim, evidence, affected projects,
related records, and why the note should stay private rather than in repo docs.

## Final Response

When a LeafWiki record was created or updated, say which private record id/path
was touched and summarize the key artifact paths. If LeafWiki was unavailable,
credentials were missing, or no experiment/ops event occurred, say no LeafWiki
record was written. Do not create a repo-local private index as a fallback
unless the user explicitly asks for one.
