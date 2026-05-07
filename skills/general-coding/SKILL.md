---
name: general-coding
description: Research code reliability rules for coding in experimental or evaluation codebases. Use when editing research code, training/evaluation scripts, metrics, parsers, model calls, datasets, configs, or experiment logging where trustworthy results matter.
---

# General Coding

Use this skill for research codebases where experimental results must be auditable and failures must stay visible.

## Rules

- Make the smallest correct change. Avoid unrelated refactors, renamed interfaces, and new dependencies unless explicitly requested.
- Do not hide failures. Missing files, invalid configs, failed API calls, parse errors, and metric errors must be explicit.
- Do not add fallback behavior unless requested. Any fallback must be opt-in, logged, and reflected in final results.
- Bound retries, loops, API calls, parsing attempts, and long-running jobs.
- Validate inputs at config, dataset, model-loading, parsing, and metric boundaries.
- Preserve existing metric definitions and sample inclusion rules unless the user explicitly asks to change them.

## Evaluation Results

Every evaluated sample must have one explicit status:

- `success`
- `invalid_input`
- `model_failed`
- `parse_failed`
- `metric_failed`
- `skipped_by_policy`

Save these artifacts separately when the code evaluates samples:

- raw model outputs
- parsed outputs
- per-sample results with status
- aggregate metrics

## Reproducibility

Record enough run information to reproduce the experiment:

- config and command
- model and dataset split
- prompt and decoding parameters
- seed and sample count

## Final Checks

Before finishing, check that failures remain observable, no silent fallback was introduced, all loops/retries are bounded, and result files separate raw outputs, parsed outputs, per-sample records, and aggregate metrics.
