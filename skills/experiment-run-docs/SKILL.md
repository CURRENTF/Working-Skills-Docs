---
name: experiment-run-docs
description: Compact experiment-run documentation rules. Use when Codex runs, resumes, evaluates, benchmarks, or analyzes ML/research experiments and must preserve decisive execution identity, provenance, artifacts, results, and failures without duplicating logs or narrating result tables. Put dated or private records in the Git-backed Research-Vault and keep repo docs for stable project documentation.
---

# Experiment Run Docs

Leave a compact, auditable trail after running or analyzing an experiment. The
record is an index into decisive evidence, not a copy of configs, manifests,
logs, or terminal narrative.

## Placement

- Put dated runs, failed attempts, transient machine state, private paths, and
  raw benchmark or profiling results in `~/Documents/Codex/Research-Vault`
  through `research-vault-docs`.
- Keep repo `docs/` for stable setup, runbooks, reproducibility instructions,
  architecture, parameter semantics, and concise public summaries. Do not put
  chronological history or one-off result tables there unless asked.
- Do not add private-vault paths, links, indexes, or Git metadata to a project
  repo unless the user explicitly requests that integration.
- If the vault is unavailable, preserve the record beside the run artifacts in
  a manifest, status file, or launcher log and report that it is unsynced.

## Workflow

1. Inspect the actual command, config, logs, results, checkpoints, and terminal
   evidence, but record only what is needed to identify, reproduce, and
   interpret the run.
2. Search the vault and update the existing record when a run root, config,
   command identity, result path, or other stable fingerprint matches. Keep one
   file per distinct run or variant under
   `projects/<project>/experiments/<YYYY>/<MM>/`.
3. For a long job, record `running` after launch and update the same file after
   completion with a concise final state. Preserve progress and failure details
   already written; do not delete or rewrite them merely to shorten the record.
4. Keep large logs and artifacts outside the vault and point to their exact
   paths. Separately update repo docs only when the result establishes stable
   project behavior worth documenting.

## Compact Record

New prose in a routine completed record should usually fit in about 10-30 lines,
excluding frontmatter, tables, and a necessary exact command. This is a writing
target, not a retrospective cleanup rule. Include only applicable fields; write
`TBD` or `not captured` instead of inventing facts.

- **Identity:** date, status, project, and a stable fingerprint.
- **Question:** one sentence. Do not narrate task history or predecessor jobs
  unless they affect validity.
- **Run:** working directory plus the exact command, or a canonical
  launcher/config path and material overrides when sufficient. Do not copy a
  config into prose.
- **Provenance:** branch/commit and only relevant worktree changes.
- **Environment:** normally one compact line or table row per system: host/GPU
  topology, environment path, model/data identity, and only versions or backend
  choices that affect reproduction or interpretation. Leave package inventories,
  cache/proxy setup, and routine resource checks in the manifest or log.
- **Protocol:** only comparison-affecting data, model, checkpoint,
  hyperparameter, decoding, and repeat/statistic choices. Prefer one compact
  table for multiple variants.
- **Evidence:** output root plus canonical summary, config, log, checkpoint, or
  manifest paths.
- **Failure:** for a failed or inconclusive run, record the first failing step,
  concise error, partial artifacts, and next diagnostic. Preserve recovered
  attempts already present in a completed record. When adding the final state,
  avoid repeating them and call out only changes to the final protocol or a
  remaining material limitation.

Expand beyond the default only when mechanistic evidence, a complex incident,
or a load-bearing caveat would otherwise be lost.

## Results

- Every metric must point to a source artifact and retain its source metric and
  split names.
- Prefer a self-contained table whose heading and columns identify the variant,
  statistic, unit, baseline, and comparison direction.
- Treat the table as the result. Do not repeat its values, rankings, trends,
  speedups, or statements such as "faster in every row" in prose.
- After a table, add text only for a non-obvious validity limit, interpretation
  caveat, or next decision that the table cannot express. Otherwise end with
  the canonical source path.
- Use compact tables to map multiple systems or variants to their run/config,
  environment identity, artifacts, and results instead of separate prose
  subsections.
- Never paste large logs or unredacted secrets, tokens, private URLs, or
  credentials.

## Compact Template

```markdown
---
project: <project>
record_kind: experiment
date: <YYYY-MM-DD>
status: <running | completed | failed | aborted | inconclusive>
fingerprint: <run root, config, or result identity>
---

# <short run name>

- Question: <one sentence>
- Run: `<working dir>`; `<launcher/config or concise exact command>`
- Code: `<branch>@<commit>`; <relevant dirty state only>
- Environment: <host/GPU topology>; `<env>`; <model/data>; <material backend>
- Artifacts: `<output root>`; summary `<result file>`; log `<log file>`

## Protocol

<one compact table or at most a few material bullets>

## Results

<self-contained table>

Source: `<canonical result artifact>`

<Optional one-line caveat only when the table could otherwise be misread.>
```

## Final Response

When Codex ran or analyzed an experiment, report the Research-Vault record path,
its push state, and the key external log/result paths. Mention repo docs only
when they were intentionally updated. If the vault could not be synced, point
to the recoverable output-root record instead.
