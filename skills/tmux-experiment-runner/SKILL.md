---
name: tmux-experiment-runner
description: Robust tmux workflow for launching, monitoring, and auditing long local or remote ML experiments and benchmark tests. Use when running training/evaluation/smoke/full experiments that should survive Codex tool sessions, when nohup/background jobs produce empty logs or disappear, when the user asks to run on specific GPUs and later query progress/results, or when remote SSH/tmux experiment launch needs quote-safe scripts and durable status records.
---

# Tmux Experiment Runner

Use this skill for long local experiments, benchmark suites, smoke tests, and GPU jobs that must keep running after the current command returns. Prefer it over plain `nohup` when the run is expensive or the user will ask for progress later.

## Principles

- Only add or run tests that prevent P0/P1 consequences; prioritize end-to-end tests. Reuse relevant passing checks rather than repeating smoke runs.
- Put data, logs, predictions, and outputs under the machine's large output volume, not the repo or home directory. On `guest-KR6288*`, follow `guest-kr6288-storage`: prefer `/data2/haojitai/outputs/...` and use `/data1/haojitai/outputs/...` when `/data2` is full or unhealthy.
- Write a run script in `scripts/tmp/*.sh` for long commands. Avoid hand-running huge one-liners that cannot be audited.
- Do not put a long Python command directly inside nested `ssh 'tmux "python ..."'` quoting. For remote runs, write the launcher on the remote host first, then start tmux with only `cd`, `RUN_TAG`/env vars, and `bash scripts/tmp/<run>.sh`.
- Do not inline JSON or large hyperparameter dictionaries on the shell command line. Write `hparams.json` or config files from the launcher, preferably with a single-quoted heredoc such as `<<'PY'` so shell variables, quotes, and backslashes are not expanded accidentally.
- Use a stable run root and the launcher's existing process status for monitoring.
- Use `tmux new-session -d -s <session>` for durable execution. In Codex desktop sessions, plain `nohup ... &` can exit immediately with empty logs; if this happens, switch to tmux.
- Apply `experiment-run-docs` only when the run meets its value threshold. Records contain only the launch command, code Git commit, and final results; intermediate records use the same fields with results empty until available. Update the same record and remove confirmed obsolete or inconsistent content; leave uncertain content unchanged.
- Do not archive source code, patches, source snapshots, or per-file source hashes. A dirty worktree does not block running or recording an experiment.

## Delegation

If the current user request explicitly asks for subagent launch/monitoring, delegate the launch-and-watch sidecar to a `worker` subagent with model `gpt-5.5` and medium reasoning. Keep the main agent responsible for deciding the experiment semantics, checking the exact command/config, and reporting final results. The subagent should only:

- start or monitor the named run using the agreed launcher and GPU;
- write/read `status.tsv`, logs, row counts, and GPU/process state;
- report progress, failure, or completion with artifact paths.

Do not let the subagent silently change hyperparameters, switch GPUs, relaunch failed runs with a workaround, edit source code, or update result tables unless the user explicitly asked for that.

## Launch Workflow

1. Check resources before launch:

```bash
hostname
pwd
git rev-parse HEAD
git status --short
nvidia-smi --query-gpu=index,memory.used,memory.total,utilization.gpu --format=csv,noheader,nounits
tmux ls 2>/dev/null || true
```

2. Create or inspect the config and launcher:

```bash
bash -n scripts/tmp/<run>.sh
python -m json.tool scripts/tmp/<config>.json >/dev/null
git diff --check -- scripts/tmp/<run>.sh scripts/tmp/<config>.json
```

3. Run an end-to-end smoke only when needed to prevent a P0/P1 consequence and existing checks do not cover it:

```bash
GUEST_DATA_ROOT=/data2/haojitai  # use /data1/haojitai when the storage check requires fallback
CUDA_VISIBLE_DEVICES=<gpu> PYTHONPATH=$PWD:$PWD/src \
conda run --no-capture-output -n <env> python -u <entrypoint> ...
```

4. Launch the full run in tmux:

```bash
tmux new-session -d -s <session_name> \
  "cd /abs/repo && RUN_TAG=<tag> CUDA_VISIBLE_DEVICES=<gpu> <env vars> scripts/tmp/<run>.sh; echo EXIT_CODE=\$?; sleep 300"
```

5. Immediately verify that it actually started:

```bash
tmux ls | rg '<session_name>' || true
tmux capture-pane -pt <session_name> -S -80
nvidia-smi --query-gpu=index,memory.used,memory.total,utilization.gpu,power.draw --format=csv,noheader,nounits
```

6. If a record meets the value threshold, keep only the launch command, Git commit, and final results; leave results empty until available.

## Launcher Requirements

A good launcher should:

- use `set -euo pipefail`;
- export `CUDA_VISIBLE_DEVICES`, `PYTHONPATH`, dataset paths, and output roots explicitly;
- expose process completion and exit status for monitoring;
- verify the target host and working directory before launch;
- avoid repeating a smoke already covered by relevant passing checks;
- validate expected output row counts or sample counts before marking `completed`;
- return nonzero on missing result files, bad row counts, parse errors, OOM, CUDA errors, or failed metrics.

## Monitoring

Use compact status probes:

```bash
GUEST_DATA_ROOT=/data2/haojitai  # use the root selected before launch
RUN_ROOT="$GUEST_DATA_ROOT/outputs/<project>/<run>"
tmux capture-pane -pt <session_name> -S -80
nvidia-smi --query-gpu=index,memory.used,memory.total,utilization.gpu,power.draw --format=csv,noheader,nounits
```

Use existing runner status, results, or logs when available. Report progress in the conversation: task/sample counts, process state, GPU utilization, and observed errors. Do not append monitoring output to the experiment record.

## Completion

Before saying a run completed:

- confirm the tmux session exited or is idle after printing `EXIT_CODE=0`;
- confirm the result file exists and is nonempty;
- validate all expected prediction/sample counts;
- inspect the terminal state and existing runner diagnostics for errors;
- update a valuable experiment record with only the launch command, code Git commit, and final results.

Report failures explicitly. Do not silently relaunch with changed hyperparameters; keep recovery within the authorized protocol.
