---
name: experiment-run-docs
description: Experiment run documentation rules. Use when Codex runs, resumes, evaluates, benchmarks, or analyzes ML/research experiments and must record in the repo docs what experiment was run, command/config, hyperparameters, data and splits, model and checkpoints, code version, artifacts, final metrics/results, failure status, and corresponding logs.
---

# Experiment Run Docs

Use this skill to make every experiment auditable after Codex runs or analyzes it. The output is a concise record in the current repository's `docs/` directory that links commands, configs, data, checkpoints, logs, and results.

## Workflow

1. Before finishing the user turn, identify every experiment run, resumed run, evaluation, benchmark, or analysis performed in this session.
2. Inspect the actual command, config, logs, result files, checkpoint directories, and terminal output that support the record.
3. Update an existing experiment doc if one exists, preferring `docs/dev-notes/experiment-records.md` or a topic-specific file under `docs/dev-notes/` when the repo separates stable docs from historical records.
4. If no suitable doc exists, create `docs/dev-notes/experiment-records.md` when the repo has a substantial public `docs/` tree; otherwise create `docs/experiments.md`. If the repo has `docs/README.md`, add the experiment doc under a "Development Notes" or "Historical Records" section, not before stable setup/architecture/reproducibility docs.
5. Add one entry per distinct run or variant. Use stable run names, timestamps, or log/checkpoint directory names so entries can be matched back to artifacts.
6. After a long-running job is launched but before it finishes, record a `running` entry with the command, working directory, PID/session if available, expected outputs, and log path. Update the same entry after completion.

## Required Fields

Include the fields that apply. Write `TBD` or `not captured` instead of inventing missing values.

- Date/time observed and run status: `running`, `completed`, `failed`, `aborted`, or `inconclusive`.
- Goal: the experiment question, hypothesis, benchmark target, or bug being tested.
- Working directory and exact command. Include important env vars, config files, overrides, launch scripts, and resume flags.
- Code version: branch, commit hash if available, and whether the worktree had relevant uncommitted changes.
- Environment: host if relevant, conda/env name, Python/CUDA/library versions, GPU ids/type/count, and distributed settings.
- Data: dataset names/paths, splits, sample counts, preprocessing, filtering, seed, and any generated data sources.
- Model: architecture/base model, tokenizer/processor, pretrained weights, adapters, quantization, precision, and important backend choices.
- Checkpoints: checkpoints loaded/resumed from, checkpoints written, best checkpoint selection rule, and retention or cleanup notes.
- Hyperparameters: learning rate, optimizer, scheduler, warmup, batch size, effective batch size, gradient accumulation, epochs/steps, max length/resolution, loss weights, decoding/eval parameters, and early stopping.
- Outputs and artifacts: log files, result files, metrics tables, predictions, TensorBoard/WandB runs, plots, generated samples, and checkpoint directories.
- Results: final and best metrics with split, step/epoch, metric direction, and baseline/comparison when known.
- Failure notes: exit code, failing step, key error summary, partial outputs, and next diagnostic step for failed or inconclusive runs.

## Log And Result Mapping

- Every reported metric must point to a source log or result artifact.
- Preserve metric names and split names from the source files. Do not silently rename metrics in a way that changes their meaning.
- For multiple variants, use a table that maps run id to command/config, log path, checkpoint path, and final result.
- Do not paste large logs into docs. Summarize the relevant lines and link or path to the full log.
- Redact secrets, tokens, private URLs, and credentials from recorded commands and logs.
- Keep exact run records, failed attempts, and dated implementation context out of the main public docs flow when possible. Stable docs should link to historical records rather than embed long chronological change logs.

## Suggested Entry Template

````markdown
### <YYYY-MM-DD HH:MM UTC> - <run id or short name>

- Status: <running | completed | failed | aborted | inconclusive>
- Goal: <what this run tested>
- Working dir: `<path>`
- Command:

```bash
<exact command with secrets redacted>
```

- Code: `<branch>` / `<commit>`; worktree: <clean | relevant changes noted>
- Data: <dataset paths, split, sample count, preprocessing, seed>
- Model: <base model/architecture, tokenizer, loaded checkpoint/adapters, precision/backend>
- Hyperparameters: <lr, batch/effective batch, epochs/steps, optimizer, scheduler, max length, eval/decoding params>
- Checkpoints: loaded `<path>`; saved `<path>`; best selection <rule>
- Logs: `<path>`; <TensorBoard/WandB URL or directory if any>
- Results: <metric=value on split at step/epoch>; source `<result file or log>`
- Notes: <failure reason, caveats, follow-up, or comparison>
````

## Final Response

When the user asked Codex to run or analyze experiments, mention the doc path updated and the key log/result paths in the final response. If docs were not updated because no experiment actually ran or no artifacts were produced, say that explicitly.
