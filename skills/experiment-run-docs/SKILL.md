---
name: experiment-run-docs
description: Experiment run documentation rules. Use when Codex runs, resumes, evaluates, benchmarks, or analyzes ML/research experiments and must record what experiment was run, command/config, hyperparameters, data and splits, model and checkpoints, code version, artifacts, final metrics/results, failure status, and corresponding logs, preferring the LeafWiki research vault when available and repo docs as fallback or stable runbook material.
---

# Experiment Run Docs

Use this skill to make every experiment auditable after Codex runs or analyzes it. Prefer recording dated run history in the LeafWiki research vault when it is reachable; use repo `docs/` for stable runbooks, reproducibility notes, paper-facing summaries, or fallback when the vault is unavailable.

## LeafWiki Research Vault

- Default base URL: `http://8.134.70.136:8080`. Override with `LEAFWIKI_RESEARCH_BASE_URL` when set.
- Authenticate with `LEAFWIKI_RESEARCH_API_PASSWORD` or `LEAFWIKI_RESEARCH_API_TOKEN` when present. Do not print secrets. On the user's trusted workstation, if env vars are missing and SSH is available, load the password into a shell variable without echoing it:

```bash
LEAFWIKI_RESEARCH_API_PASSWORD=$(ssh root@8.134.70.136 "sed -n 's/^LEAFWIKI_RESEARCH_API_PASSWORD=//p' /opt/leafwiki/.env")
```

- Before creating a new record, search existing context:

```bash
curl -fsS "${LEAFWIKI_RESEARCH_BASE_URL:-http://8.134.70.136:8080}/api/research/docs/search?q=<topic>&project=<project>&kind=page&limit=10" \
  -H "X-Research-Password: $LEAFWIKI_RESEARCH_API_PASSWORD"
```

- Create or reuse an experiment record with `POST /api/research/experiments`. Use a human-readable `slugHint`; the server generates and de-duplicates the canonical ID. Put run root, config path, command identity, or result path in `fingerprint` so retries can be matched safely.
- Update the same record with `/events`, `/status`, and `/results` as the run starts, progresses, finishes, fails, or is superseded.
- Use `/api/research/docs/tree?project=...&kind=page` to browse the project document hierarchy before search/read when the relevant path is unknown.
- Use `/api/research/docs/read?path=...` to read full Markdown only after search returns a relevant path.
- For exact endpoint shapes, curl examples, and response fields, read `references/leafwiki-research-api.md` before calling or changing the LeafWiki API.

## Workflow

1. Before finishing the user turn, identify every experiment run, resumed run, evaluation, benchmark, or analysis performed in this session.
2. Inspect the actual command, config, logs, result files, checkpoint directories, and terminal output that support the record.
3. If LeafWiki is reachable and credentials are available, search for an existing experiment/context page, then create or update the vault record. Keep the returned `id` and `path` in your working notes and final response.
4. If LeafWiki is unavailable, update an existing experiment doc if one exists, preferring `docs/dev-notes/experiment-records.md` or a topic-specific file under `docs/dev-notes/` when the repo separates stable docs from historical records.
5. If no suitable fallback doc exists, create `docs/dev-notes/experiment-records.md` when the repo has a substantial public `docs/` tree; otherwise create `docs/experiments.md`. If the repo has `docs/README.md`, add the experiment doc under a "Development Notes" or "Historical Records" section, not before stable setup/architecture/reproducibility docs.
6. Add one entry per distinct run or variant. Use stable run names, timestamps, or log/checkpoint directory names so entries can be matched back to artifacts.
7. After a long-running job is launched but before it finishes, record a `running` entry with the command, working directory, PID/session if available, expected outputs, and log path. Update the same entry after completion.

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

When the user asked Codex to run or analyze experiments, mention the LeafWiki experiment id/path or repo doc path updated and the key log/result paths in the final response. If no record was updated because no experiment actually ran, no artifacts were produced, or credentials were unavailable, say that explicitly.
