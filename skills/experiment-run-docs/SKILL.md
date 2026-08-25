---
name: experiment-run-docs
description: Experiment run documentation rules. Use when Codex runs, resumes, evaluates, benchmarks, or analyzes ML/research experiments and must record the command/config, hyperparameters, data and splits, model/checkpoints, code version, artifacts, metrics, failures, and logs. Put dated or private records in the Git-backed Research-Vault and keep repo docs for stable project documentation.
---

# Experiment Run Docs

Use this skill to make every experiment auditable after Codex runs or analyzes it. Record dated or private run history in Research-Vault by default. Use repo `docs/` only for stable runbooks, reproducibility instructions, architecture or parameter semantics, public paper-facing summaries, or a repo-local fallback the user explicitly requested.

## Placement Boundary

- Put dated experiment runs, failed attempts, transient machine state, exact local paths, GPU occupancy, private project history, and raw benchmark/profiling records in `~/Documents/Codex/Research-Vault` using `research-vault-docs`.
- Do not append chronological run logs, one-off result tables, local output roots, failed attempt notes, or "what changed today" implementation history to repo `docs/` unless the user explicitly asks for a repo-local record.
- Repo docs may be updated when the content is stable and useful to future repo readers without private context: setup, launch/verify commands, reproducibility instructions, architecture, configuration/parameter semantics, or concise public benchmark summaries.
- If a code change needs a repo-doc update, write the current stable behavior in present tense. Keep dated evidence and private artifact paths in Research-Vault or the run output directory.
- Do not commit private-vault paths, links, indexes, or Git metadata into repo docs unless the user explicitly asks for a private integration.
- If the vault cannot be cloned, opened, or safely updated, preserve auditability with the run's output-root manifest/logs and report that the private record remains unsynced. Do not create a repo-local private experiment log unless the user explicitly asks for one.

## Private Research Vault

- The canonical checkout is `~/Documents/Codex/Research-Vault`; `research-vault-docs` clones `git@github.com:CURRENTF/Research-Vault.git` there when it is absent.
- Search existing records before writing. Reuse the same file when the run root, config, command identity, result path, or another stable fingerprint matches.
- Store one distinct run or variant per file under `projects/<project>/experiments/<YYYY>/<MM>/` and update that file as the run starts, progresses, finishes, fails, or is superseded.
- Keep large logs and result artifacts outside the vault. Record their exact paths and the evidence extracted from them.

## Workflow

1. Before finishing the user turn, identify every experiment run, resumed run, evaluation, benchmark, or analysis performed in this session.
2. Inspect the actual command, config, logs, result files, checkpoint directories, and terminal output that support the record.
3. Use `research-vault-docs` to locate or clone the private vault, search for a matching record, and create or update it.
4. If the vault is unavailable, keep the record in the run output directory when possible, for example `run_manifest.md`, `status.tsv`, `hparams.json`, or the launcher log. Do not write a repo-local private record unless the user explicitly asks for one.
5. Use stable run names, run roots, result paths, config paths, or log/checkpoint directories so retries and resumed runs can be matched back to the same file.
6. After a long-running job is launched but before it finishes, record its `running` state in the vault when safely possible and ensure the output root has a durable status file. Update the same record after completion.
7. Separately decide whether the repo docs need a stable update. If yes, keep it short, present-tense, and free of dated local run history; put detailed evidence in Research-Vault or the run artifacts.

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
- Keep exact run records, failed attempts, and dated implementation context out of repo docs by default. Stable repo docs should describe current behavior rather than embed long chronological change logs.

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

When the user asked Codex to run or analyze experiments, mention the Research-Vault record path, whether it was pushed, and the key log/result paths. If the vault was unavailable or could not be safely synced, say so and point to the output-root manifest/logs instead. Mention a repo doc path only when a stable repo doc was intentionally updated or the user explicitly requested a repo-local fallback note.
