---
name: tmux-experiment-runner
description: Robust tmux workflow for launching, monitoring, and auditing long local or remote ML experiments and benchmark tests. Use when running training/evaluation/smoke/full experiments that should survive Codex tool sessions, when nohup/background jobs produce empty logs or disappear, when the user asks to run on specific GPUs and later query progress/results, or when remote SSH/tmux experiment launch needs quote-safe scripts and durable status records.
---

# Tmux Experiment Runner

Use this skill for long local experiments, benchmark suites, smoke tests, and GPU jobs that must keep running after the current command returns. Prefer it over plain `nohup` when the run is expensive or the user will ask for progress later.

## Principles

- Run a short foreground smoke first when feasible; only launch the long run after smoke proves model loading, config parsing, and the target backend path.
- Put data, logs, predictions, and outputs under the machine's large output volume, not the repo or home directory. On `guest-KR6288*`, use `/data2/haojitai/outputs/...`.
- Write a run script in `scripts/tmp/*.sh` for long commands. Avoid hand-running huge one-liners that cannot be audited.
- Do not put a long Python command directly inside nested `ssh 'tmux "python ..."'` quoting. For remote runs, write the launcher on the remote host first, then start tmux with only `cd`, `RUN_TAG`/env vars, and `bash scripts/tmp/<run>.sh`.
- Do not inline JSON or large hyperparameter dictionaries on the shell command line. Write `hparams.json` or config files from the launcher, preferably with a single-quoted heredoc such as `<<'PY'` so shell variables, quotes, and backslashes are not expanded accidentally.
- Every run must have a stable `RUN_ROOT`, `run.log`, `status.tsv`, config copy/path, expected result path, and exact command.
- Use `tmux new-session -d -s <session>` for durable execution. In Codex desktop sessions, plain `nohup ... &` can exit immediately with empty logs; if this happens, switch to tmux.
- Pair this skill with `experiment-run-docs` whenever the run starts, finishes, fails, or is resumed. That skill should prefer the LeafWiki research vault for dated run records when available, with repo docs only as fallback or stable runbook material.
- Failed, aborted, superseded, and workaround runs are first-class records. Preserve their artifacts and status rows, and mark them clearly so they are not later confused with comparable scored results.

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

3. Run a foreground smoke for the riskiest path, usually one task or a few samples:

```bash
CUDA_VISIBLE_DEVICES=<gpu> PYTHONPATH=$PWD:$PWD/src \
conda run --no-capture-output -n <env> python -u <entrypoint> ... \
  2>&1 | tee /data2/haojitai/outputs/<project>/<run>/smoke.log
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
tail -n 120 /data2/haojitai/outputs/<project>/<run>/run.log
nvidia-smi --query-gpu=index,memory.used,memory.total,utilization.gpu,power.draw --format=csv,noheader,nounits
```

6. Record the launch with `experiment-run-docs`, including the LeafWiki experiment id/path if the vault was updated.

## Launcher Requirements

A good launcher should:

- use `set -euo pipefail`;
- export `CUDA_VISIBLE_DEVICES`, `PYTHONPATH`, dataset paths, and output roots explicitly;
- write `status.tsv` with `stage`, `status`, start/end time, GPU, config, log path, and result path;
- record `hostname`, `pwd`, `git rev-parse HEAD`, `git status --short`, model/checkpoint paths, and resolved runtime knobs before launch, especially on remote hosts where local/remote confusion is possible;
- run smoke before full unless the user explicitly asks to skip smoke;
- validate expected output row counts or sample counts before marking `completed`;
- write all stdout/stderr into `run.log`;
- return nonzero on missing result files, bad row counts, parse errors, OOM, CUDA errors, or failed metrics.

## Monitoring

Use compact status probes:

```bash
RUN_ROOT=/data2/haojitai/outputs/<project>/<run>
cat "$RUN_ROOT/status.tsv"
tail -n 80 "$RUN_ROOT/run.log"
for f in "$RUN_ROOT"/full_pred/*.jsonl; do n=$(wc -l < "$f"); [ "$n" -gt 0 ] && printf '%s %s\n' "$(basename "$f")" "$n"; done
rg -n "Traceback|RuntimeError|CUDA|illegal memory access|OOM|failed|bounds check" "$RUN_ROOT/run.log" || true
nvidia-smi --query-gpu=index,memory.used,memory.total,utilization.gpu,power.draw --format=csv,noheader,nounits
```

When reporting progress, state exact task/row counts, whether the tmux session still exists, GPU utilization, and the latest error grep result.

## Completion

Before saying a run completed:

- confirm the tmux session exited or is idle after printing `EXIT_CODE=0`;
- confirm the result file exists and is nonempty;
- validate all expected prediction/sample counts;
- inspect the final log tail and grep for errors;
- update the experiment record with command, config, run root, logs, metrics, failure notes, and code/worktree state.

If a run fails, preserve the failed artifacts. Do not silently relaunch with changed hyperparameters; document the failed config and only change the smallest needed runtime knob for recovery.
