---
name: periodic-remote-check
description: Periodic remote experiment monitoring via a long-lived Codex request or a local background loop. Use when Codex needs to poll a server on a fixed cadence, inspect training logs/loss/checkpoints/GPU state over SSH, wait for a local process to end before continuing, or turn a repeated SSH status check into a reusable workflow.
---

# Periodic Remote Check

## Overview

Keep one Codex request alive while polling a local or remote command on a fixed cadence. Use the bundled script for deterministic loops and file-backed logs, then summarize deltas, newest metrics, and anomalies instead of repeating raw output.

## Operating Modes

### Same Request, Continuous Monitoring

Use this mode when the user means "do not end this request yet; wait and continue later."

- Start the helper in a long-lived exec session with `--iterations 0` or `--until-local-pid`.
- Do not send the final answer until the stop condition is met or the user asks to stop.
- Poll the session periodically and report only meaningful changes.
- A local `sleep` PID is a valid stop condition. Start `sleep 3600` locally, pass its PID via `--until-local-pid`, and keep checking the remote job every 600 seconds until the timer exits.

### Detached Local Watcher

Use this mode when the user wants monitoring outside the current reply.

- Run the helper under `nohup`, `tmux`, or an OS scheduler.
- Write artifacts to a stable output directory so later turns can inspect them.
- If the requested cadence is finer than the product's built-in automation supports, prefer this mode.

Read `references/run-modes.md` only when the user needs examples for background execution or scheduler setup.

## Workflow

1. Define the probe.

- Prefer one shell snippet that returns everything needed in one round trip: recent log tail, checkpoint timestamps, GPU/process state, and optional custom markers.
- Keep the probe read-only unless the user explicitly asks to modify remote state.

2. Define the stop condition.

- Choose one: fixed iterations, `--until-local-pid`, or manual stop.
- Default to finite iterations if the user did not explicitly ask for an open-ended watcher.

3. Run the helper.

- Use `scripts/periodic_check.py` for repeatable polling and JSONL records.
- If the remote host is AutoDL/GPUHub, also apply `$autodl-remote-debug` before deciding SSH options, paths, proxy, conda, or `PYTHONPATH`.

4. Summarize results.

- Lead with the current status: progressing, stalled, failed, or ambiguous.
- Include the newest extracted metrics, last update time, and anomalies such as `nan`, OOM, traceback, or no output change across checks.
- Reference the newest raw log file when the user needs detail.
- If the watcher is monitoring an experiment run or benchmark, hand the status change to `$experiment-run-docs` so the LeafWiki research vault or fallback repo docs record the launch, progress, completion, or failure.

## Probe Recipes

- Training log tail:
  `tail -n 200 /path/to/train.log`
- Log and checkpoints:
  `bash -lc 'tail -n 120 logs/train.log; printf "\n=== checkpoints ===\n"; ls -lt ckpts | head'`
- Log, GPU, and process state:
  `bash -lc 'tail -n 80 train.log; printf "\n=== gpu ===\n"; nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader; printf "\n=== ps ===\n"; pgrep -af python || true'`

## Helper Usage

```bash
# Single check
python3 scripts/periodic_check.py \
  --host server.example.com \
  --user root \
  --remote-cmd 'tail -n 120 /srv/run/train.log' \
  --iterations 1 \
  --output-dir ./watch-output

# Keep the current request alive for one hour by tying the loop to a local sleep process
sleep 3600 &
TIMER_PID=$!

python3 scripts/periodic_check.py \
  --host server.example.com \
  --user root \
  --remote-cmd 'bash -lc "tail -n 120 train.log; ls -lt ckpts | head"' \
  --interval 600 \
  --iterations 0 \
  --until-local-pid "$TIMER_PID" \
  --output-dir ./watch-output
```

## Resources

- `scripts/periodic_check.py`: run local or SSH-based periodic probes, write raw stdout/stderr files, append JSONL records, and extract common metrics and alerts.
- `references/run-modes.md`: choose between same-request monitoring, background loops, and local schedulers.
