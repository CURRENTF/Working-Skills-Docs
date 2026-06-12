# Run Modes

Use this reference only when the user needs examples for how to keep monitoring alive.

## Same-Request Monitoring

Use a long-lived exec session when the user wants Codex to keep waiting and continue later in the same request.

Pattern:

```bash
sleep 3600 &
TIMER_PID=$!

python3 scripts/periodic_check.py \
  --host server.example.com \
  --user root \
  --remote-cmd 'tail -n 120 /srv/run/train.log' \
  --interval 600 \
  --iterations 0 \
  --until-local-pid "$TIMER_PID" \
  --output-dir ./watch-output
```

Operational guidance:

- Keep the request open until the helper exits or the user asks to stop.
- Poll the running session instead of relaunching fresh commands each time.
- Report only deltas, newest metrics, and anomalies.

## Detached Background Loop

Use this when the user wants the checker to continue after the current response ends.

With `nohup`:

```bash
nohup python3 scripts/periodic_check.py \
  --host server.example.com \
  --user root \
  --remote-cmd 'tail -n 120 /srv/run/train.log' \
  --interval 600 \
  --iterations 0 \
  --output-dir "$HOME/watch-output" \
  >"$HOME/watch-output/runner.log" 2>&1 &
```

With `tmux`:

```bash
tmux new -d -s train-watch \
  'python3 scripts/periodic_check.py --host server.example.com --user root --remote-cmd '"'"'tail -n 120 /srv/run/train.log'"'"' --interval 600 --iterations 0 --output-dir "$HOME/watch-output"'
```

## macOS `launchd`

Prefer `launchd` over a fragile login-shell background job when the user wants the Mac to keep polling after terminal restarts.

High-level steps:

1. Put the command in a small wrapper script.
2. Create a `~/Library/LaunchAgents/<label>.plist`.
3. Use `StartInterval` for minute-level cadence such as 600 seconds.
4. Load it with `launchctl bootstrap gui/$(id -u) <plist>`.

Only create the actual plist when the user explicitly asks for it, because the correct paths, environment variables, and log locations are user-specific.
