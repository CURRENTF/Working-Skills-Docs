---
name: codex-post-run-review
description: Add a conditional autonomous Codex review hook to local or remote Bash experiment scripts, always invoking `codex exec --yolo` with task exit codes, validation states, and bounded log tails so Codex can diagnose failures, sanity-check results, and make a minimal repair. Use for single or multi-task training, evaluation, benchmark, and pipeline scripts that should inspect and repair themselves after a failure, anomaly, or completed batch, including remote GPU hosts where Codex is unavailable and a trusted local SSH watcher must invoke it instead.
---

# Codex Post-run Review

Add a non-interactive Codex invocation at a meaningful experiment boundary. Gate it in Bash when healthy runs should incur no Codex call.

## Choose the Review Boundary

- For one task, review after that task.
- For a dependent pipeline, check after each gating task, but invoke Codex only on failure or anomaly; do not launch downstream work that depends on a bad output.
- For independent or parallel tasks, record every status, wait for all tasks, then invoke one Codex at batch end. Avoid concurrent repair agents editing the same worktree.
- Use `on-anomaly` by default. Use `always` only when the user wants a healthy-run metric summary. Use `on-failure` only when exit status is an adequate gate.
- Always invoke the review as `codex exec --yolo`; do not substitute a sandboxed or approval-gated mode.

For each task, record `task`, `exit_code`, `validation_state`, `log_path`, and expected artifact paths. Determine `validation_state` with cheap deterministic checks for file presence, structured completion/status fields, expected sample counts, parseability, and finite metrics. Do not treat exit code zero or a naive error-string grep as proof of health.

## Single-task Template

```bash
project_root=${PROJECT_ROOT:-"$(pwd -P)"}
run_log=${RUN_LOG:-"$project_root/run.log"}

if python train.py >"$run_log" 2>&1; then
  run_ret=0
else
  run_ret=$?
fi

codex_ret=0
needs_review=0
(( run_ret != 0 )) && needs_review=1
# Set needs_review=1 here if the task-specific artifact/metric validator fails.

if (( needs_review == 1 )) && [[ ${CODEX_POST_RUN_REVIEW_ACTIVE:-0} != 1 ]]; then
  tail -n 500 -- "$run_log" | \
    CODEX_POST_RUN_REVIEW_ACTIVE=1 codex exec --yolo -C "$project_root" \
    "实验任务刚刚结束。exit code=$run_ret；完整日志=$run_log；异常门已触发；末尾 500 行通过 stdin 提供。
检查完整日志、预期产物、最终指标、实际配置和当前代码。先确认异常门是否为真阳性。
若确有异常：定位根因；只在证据充分时做最小修复，并执行低成本的针对性验证；不要自动重启完整昂贵实验。
若确认无异常：仅输出 SKIP 及误触发原因；不要修改代码或运行额外验证。
明确区分已验证事实、推测和未完成验证，并列出关键指标与产物路径。" || codex_ret=$?
fi

if (( codex_ret != 0 )); then
  printf 'post-run Codex review failed with exit code %s\n' "$codex_ret" >&2
fi
exit "$run_ret"
```

Replace only the experiment command and, when useful, the expected artifact/metric details. Keep the last command as `exit "$run_ret"` unless the user explicitly wants review failure to fail an otherwise successful job.

## Multi-task Pattern

Do not append a full `codex exec` after every independent task. Make each task wrapper capture its status without exiting under `set -e`, run its cheap validator, append one TSV/JSONL status record, and set a shared `needs_review` flag. After all independent tasks finish, invoke `codex exec --yolo` once when the flag is set and pipe the status manifest plus bounded tails from abnormal tasks.

Use this batch prompt:

```text
一组任务刚刚结束。任务状态清单和异常任务日志尾部通过 stdin 提供；每条状态包含 task、exit_code、validation_state、log_path 和 expected_artifacts。
只调查 exit_code 非零或 validation_state 非 ok 的任务。对健康任务标记 SKIP，不重复分析、不修改其代码。
先核对清单、完整日志和实际产物，再把异常按共同根因归组；同一根因只做一次最小修复，避免互相冲突的修改。
修复后只做低成本针对性验证，不自动重跑完整昂贵任务，也不静默改变数据、模型、协议或核心超参数。
若某个异常是门误报，标记 FALSE_POSITIVE 并说明证据。最后逐任务报告 VERIFIED_FIXED、FAILED、FALSE_POSITIVE、SKIP 或 UNVERIFIED，以及关键指标、产物路径和后续动作。
```

If the user requests `always` mode, invoke once at batch end and change the prompt so healthy tasks receive a compact metric/artifact summary instead of `SKIP`. For dependent tasks, use the same prompt with only the failed gate task and stop the pipeline before downstream tasks.

## Remote Host Without Codex

Do not install Codex ad hoc on a remote experiment host merely to add this hook. When `command -v codex` fails remotely but a trusted local machine has Codex and SSH access, split the lifecycle into two persistent processes:

1. Run the experiment in remote `tmux` or another persistent supervisor. Before starting the task, atomically create a lifecycle manifest containing the run identity, commit, remote working directory, PID or tmux session, expected artifacts, `state=running`, and a heartbeat timestamp. Refresh the heartbeat while the task is live, and atomically publish the terminal exit code and validation state when it ends.
2. Run a separate one-shot watcher in local `tmux` or another persistent supervisor. Every 30 seconds, use non-interactive SSH and cheap deterministic probes to classify the run as `running`, `completed`, `failed`, `stale`, `process_lost`, `invalid_artifact`, or `repeated_ssh_failure`. Do not invoke Codex for an unchanged healthy `running` state.
3. Exit the watcher normally when the run is structurally complete and valid. On the first transition into an abnormal state, replace the watcher process with local `codex exec --yolo -C <local-project-root>` so there is exactly one owner of recovery.
4. Tell the local Codex that the experiment and artifacts are remote and provide the SSH host, port, working directory, exact commit, run identity, anomaly state, and guardrails. Let it inspect the remote state over SSH instead of pretending remote paths are local.
5. The handoff prompt must require one of two outcomes: recover the same test and install its next watcher, or report `CANNOT_COMPLETE` with concrete evidence. Merely starting a replacement task is not completion.

Implement the project-specific `probe_remote_state` with bounded SSH commands. It should count consecutive SSH failures before returning `repeated_ssh_failure`, compare the heartbeat against a declared stale threshold, verify the recorded PID or tmux session, and run the cheap artifact validator only when the task claims completion. Use a local watcher shaped like this:

```bash
remote=${REMOTE:?}
port=${SSH_PORT:?}
project_root=${PROJECT_ROOT:?}
remote_status=${REMOTE_STATUS:?}
local_status=${LOCAL_STATUS:?}
remote_workdir=${REMOTE_WORKDIR:?}
poll_seconds=${POLL_SECONDS:-30}

while :; do
  # Project-specific helper. It refreshes local_status atomically and prints one
  # of: running, completed, failed, stale, process_lost, invalid_artifact,
  # repeated_ssh_failure.
  observed_state=$(probe_remote_state \
    "$remote" "$port" "$remote_status" "$local_status")

  case "$observed_state" in
    running)
      sleep "$poll_seconds"
      ;;
    completed)
      exit 0
      ;;
    failed|stale|process_lost|invalid_artifact|repeated_ssh_failure)
      if [[ ${CODEX_POST_RUN_REVIEW_ACTIVE:-0} == 1 ]]; then
        printf 'refusing recursive Codex handoff for state %s\n' "$observed_state" >&2
        exit 1
      fi

      exec env CODEX_POST_RUN_REVIEW_ACTIVE=1 codex exec --yolo \
        -C "$project_root" \
        "Read $local_status first. This is a one-shot watcher handoff for state=$observed_state.
The experiment ran on $remote over SSH port $port in $remote_workdir. Its status and artifacts are remote; do not treat remote paths as local.
Take ownership now: inspect the manifest, bounded diagnostics, remote process/tmux state, exact commit, expected coverage, and durable artifacts over SSH. First decide whether the anomaly is real.
If it is recoverable and restarting or resuming this same test is authorized, make only an evidence-backed minimal repair, run a cheap targeted validation, then restart or resume the same protocol in a new remote persistent session. Atomically initialize a fresh run_id and lifecycle manifest, and launch a replacement local persistent watcher with CODEX_POST_RUN_REVIEW_ACTIVE unset. Verify that both new sessions are alive before returning. Do not report the experiment complete merely because it was restarted.
If the test cannot be completed safely, cannot be reached, lacks restart authorization, or the cause cannot be established, do not loop or silently change the protocol. Return CANNOT_COMPLETE with verified evidence, remaining uncertainty, durable artifact paths, and the exact blocker or required human action.
End with exactly one handoff outcome: REARMED with the new run_id plus remote and local watcher session identifiers, or CANNOT_COMPLETE with the blocker."
      ;;
    *)
      printf 'invalid probe state: %s\n' "$observed_state" >&2
      exit 2
      ;;
  esac
done
```

The watcher intentionally ends when the `exec` handoff begins. Codex must not return `REARMED` until it has installed the next watcher; otherwise a restarted test would be unsupervised. Because the Codex process receives `CODEX_POST_RUN_REVIEW_ACTIVE=1`, launch the next independent watcher with that variable explicitly unset. Do not re-arm the old run identity or reuse a stale terminal manifest.

Before launching this mode:

- Verify the local repository and remote worktree refer to the intended branch/commit; record both SHAs and whether each worktree is clean.
- Verify local SSH is non-interactive and the local watcher host will remain online for at least as long as the remote experiment.
- Keep the remote run independent of the SSH control connection so a local disconnect cannot terminate it.
- Make every remote status update atomic, for example by writing a sibling temporary file and renaming it after JSON serialization completes.
- Declare heartbeat staleness and consecutive SSH-failure thresholds. A single delayed heartbeat or failed SSH probe is not enough to diagnose task failure.
- Pass only structured status and bounded safe diagnostics to Codex. Do not copy private dataset rows, raw predictions, secrets, or full logs.
- State explicitly that this is a local external guard, not a self-contained remote hook. If local watcher persistence is not reliable, report that limitation instead of claiming autonomous coverage.

## Guardrails

- Treat `--yolo` as mandatory for this skill. It grants unsandboxed, approval-free access; run the hook only in an appropriately isolated environment. If that condition is not met, stop and report the safety blocker instead of silently downgrading the invocation.
- Never include secrets, tokens, private dataset rows, or an unbounded log in stdin.
- Do not infer success from exit code alone; validate artifact completeness, sample coverage, structured error fields, and metric finiteness when applicable.
- Do not silently change the benchmark protocol, dataset split, model, checkpoint, or core hyperparameters while repairing a failure.
- Do not start another costly run unless the user explicitly authorizes it. Prefer syntax checks, unit tests, tiny smoke cases, or a resume command proposal.
- Keep the `CODEX_POST_RUN_REVIEW_ACTIVE` guard so Codex's targeted validation cannot recursively spawn another post-run agent.
- If the experiment already runs under `tee`, preserve `set -o pipefail` so `run_ret` reflects the experiment rather than `tee`.
