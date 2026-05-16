# Documentation Structure

Use this guide when a repository's `docs/` directory is becoming a mix of
public instructions, architecture notes, runbooks, experiment records, and
dated implementation history.

## Core Rule

Keep stable user-facing docs separate from development notes.

- Stable docs explain the current system in present tense.
- Development notes preserve history, exact local runs, failed attempts, and
  dated implementation context.
- Historical detail is valuable, but it should not be the first thing a new
  user, reviewer, or reproducer sees.

## Recommended Layout

```text
docs/
  README.md
  architecture.md
  reproducibility.md
  runtime-parameters.md
  setup.md
  datasets.md
  benchmarks/
    <benchmark-runbook>.md
  dev-notes/
    experiment-records.md
    code-change-history/
      <dated-note>.md
    investigations/
      <dated-note>.md
```

Use only the files that fit the repo. Do not create empty sections just to
match the template.

## What Belongs In Stable Docs

- Installation and environment setup.
- Model, dataset, checkpoint, and artifact download instructions.
- Architecture and runtime flow.
- Canonical parameter names and compatibility rules.
- Reproducibility checklist and smoke tests.
- Stable benchmark entrypoints and expected outputs.
- Troubleshooting for current supported workflows.

Stable docs should be concise, actionable, and current. They should avoid long
chronological narratives.

## What Belongs In `dev-notes/`

- Exact local experiment records with timestamps, branch/commit, logs, paths,
  and results.
- Dated code change notes.
- Failed attempts and diagnostic traces.
- Machine-specific observations.
- Temporary implementation rationale that is useful for future debugging but
  not required for ordinary use.

Prefer preserving these notes over deleting them. Move them out of the main
docs index when they start to make the project look like an uncurated work log.

## Indexing Rules

Every repo with substantial docs should have `docs/README.md`.

The index should:

- Put stable docs first.
- Group benchmark runbooks separately.
- Put `dev-notes/` last with a clear label such as "historical records" or
  "development notes".
- Say which document is the source of truth for parameters, setup, or
  reproducibility.

## Writing Style

- Use present tense for stable docs: "Use `sparse_method`", not "We changed to
  `sparse_method`".
- Move change explanations to dated notes unless they explain a current
  compatibility constraint.
- Mark untested steps as `From project docs`, `User-provided`, or `TBD`.
- Do not claim a command works unless it was run or the source repo clearly
  documents it.
- Keep exact machine-local paths in run records; use placeholders in stable
  docs.

## Refactor Checklist

When reorganizing existing docs:

1. Read the current `README.md`, `docs/`, scripts, and benchmark commands.
2. Identify stable user-facing content versus historical run/change records.
3. Create or update `docs/README.md`.
4. Move dated records under `docs/dev-notes/`.
5. Add or update stable `architecture.md` and `reproducibility.md` when the repo
   lacks a clear public entrypoint.
6. Fix all moved relative links.
7. Search for old paths such as `docs/experiments.md` or
   `docs/code_change_history/`.
8. Preserve exact historical records unless the user explicitly asks to delete
   them.
