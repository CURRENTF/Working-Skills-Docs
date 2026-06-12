#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import re
import shlex
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


ALERT_PATTERNS = [
    ("nan", re.compile(r"(^|[^a-z])nan([^a-z]|$)", re.IGNORECASE)),
    ("oom", re.compile(r"(cuda )?out of memory", re.IGNORECASE)),
    ("traceback", re.compile(r"traceback \(most recent call last\)", re.IGNORECASE)),
    ("exception", re.compile(r"\bexception\b", re.IGNORECASE)),
    ("killed", re.compile(r"\bkilled\b", re.IGNORECASE)),
]

METRIC_KEY_VALUE = re.compile(
    r"(?P<name>train_loss|val_loss|loss|lr|learning_rate|step|epoch|acc|accuracy)"
    r"\s*[:=]\s*"
    r"(?P<value>[-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?)",
    re.IGNORECASE,
)
STEP_FALLBACK = re.compile(r"\bstep\s+(?P<value>\d+)\b", re.IGNORECASE)
EPOCH_FALLBACK = re.compile(r"\bepoch\s+(?P<value>\d+(?:\.\d+)?)\b", re.IGNORECASE)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run a local or SSH command on a fixed cadence and record the results.",
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--local-cmd", help="Local shell command to run with 'bash -lc'.")
    mode.add_argument("--remote-cmd", help="Remote shell command to run over SSH.")
    parser.add_argument("--host", help="SSH host for --remote-cmd.")
    parser.add_argument("--port", type=int, default=22, help="SSH port for --remote-cmd.")
    parser.add_argument("--user", help="SSH user for --remote-cmd.")
    parser.add_argument("--workdir", help="Working directory before running the command.")
    parser.add_argument("--interval", type=float, default=600, help="Seconds between polls.")
    parser.add_argument(
        "--iterations",
        type=int,
        default=1,
        help="Number of checks to run. Use 0 for an open-ended loop.",
    )
    parser.add_argument(
        "--until-local-pid",
        type=int,
        help="Stop before the next iteration once this local PID no longer exists.",
    )
    parser.add_argument(
        "--connect-timeout",
        type=int,
        default=15,
        help="SSH connection timeout in seconds.",
    )
    parser.add_argument(
        "--command-timeout",
        type=int,
        default=120,
        help="Timeout for each command execution in seconds.",
    )
    parser.add_argument(
        "--ssh-opt",
        action="append",
        default=[],
        help="Extra SSH option. Repeat for multiple options.",
    )
    parser.add_argument(
        "--no-hostkey",
        action="store_true",
        help="Disable host key checking for ephemeral/debug hosts.",
    )
    parser.add_argument(
        "--output-dir",
        default="./watch-output",
        help="Directory for raw outputs and JSONL records.",
    )
    parser.add_argument(
        "--label",
        default="probe",
        help="Short label used in console output and metadata.",
    )
    args = parser.parse_args()

    if args.remote_cmd and (not args.host or not args.user):
        parser.error("--remote-cmd requires --host and --user.")
    if args.iterations < 0:
        parser.error("--iterations must be >= 0.")
    if args.interval < 0:
        parser.error("--interval must be >= 0.")
    return args


def utc_now():
    return datetime.now(timezone.utc)


def timestamp_slug(dt):
    return dt.strftime("%Y%m%dT%H%M%S.%fZ")


def pid_exists(pid):
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        pass

    try:
        result = subprocess.run(
            ["ps", "-o", "stat=", "-p", str(pid)],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return True

    if result.returncode != 0:
        return False

    state = result.stdout.strip()
    if not state:
        return False
    if "Z" in state:
        return False
    return True


def normalize_metric_name(name):
    lowered = name.lower()
    aliases = {
        "learning_rate": "lr",
        "accuracy": "acc",
    }
    return aliases.get(lowered, lowered)


def maybe_number(value):
    try:
        number = float(value)
    except ValueError:
        return value
    if number.is_integer():
        return int(number)
    return number


def extract_metrics(text):
    metrics = {}
    for line in reversed(text.splitlines()):
        for match in METRIC_KEY_VALUE.finditer(line):
            name = normalize_metric_name(match.group("name"))
            if name not in metrics:
                metrics[name] = maybe_number(match.group("value"))
        if "step" not in metrics:
            step_match = STEP_FALLBACK.search(line)
            if step_match:
                metrics["step"] = int(step_match.group("value"))
        if "epoch" not in metrics:
            epoch_match = EPOCH_FALLBACK.search(line)
            if epoch_match:
                metrics["epoch"] = maybe_number(epoch_match.group("value"))
    return metrics


def detect_alerts(text):
    alerts = []
    for name, pattern in ALERT_PATTERNS:
        if pattern.search(text):
            alerts.append(name)
    return alerts


def build_remote_command(args):
    remote_cmd = args.remote_cmd
    if args.workdir:
        remote_cmd = f"cd {shlex.quote(args.workdir)} && {remote_cmd}"

    command = ["ssh", "-p", str(args.port), "-o", f"ConnectTimeout={args.connect_timeout}"]
    if args.no_hostkey:
        command.extend(["-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null"])
    for opt in args.ssh_opt:
        command.append(opt)
    command.extend([f"{args.user}@{args.host}", "bash", "-lc", remote_cmd])
    return command


def build_local_command(args):
    local_cmd = args.local_cmd
    if args.workdir:
        local_cmd = f"cd {shlex.quote(args.workdir)} && {local_cmd}"
    return ["bash", "-lc", local_cmd]


def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()


def run_once(args):
    started_at = utc_now()
    command = build_local_command(args) if args.local_cmd else build_remote_command(args)
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=args.command_timeout,
            check=False,
        )
        timeout_hit = False
        return_code = result.returncode
        stdout = result.stdout
        stderr = result.stderr
    except subprocess.TimeoutExpired as exc:
        timeout_hit = True
        return_code = 124
        stdout = exc.stdout or ""
        stderr = exc.stderr or ""

    finished_at = utc_now()
    combined = "\n".join(part for part in (stdout, stderr) if part)
    record = {
        "label": args.label,
        "started_at": started_at.isoformat(),
        "finished_at": finished_at.isoformat(),
        "duration_seconds": round((finished_at - started_at).total_seconds(), 3),
        "command_kind": "local" if args.local_cmd else "remote",
        "return_code": return_code,
        "timeout": timeout_hit,
        "metrics": extract_metrics(combined),
        "alerts": detect_alerts(combined),
    }
    return record, stdout, stderr


def format_summary(record, changed):
    parts = [
        record["finished_at"],
        f"label={record['label']}",
        f"rc={record['return_code']}",
        f"changed={'yes' if changed else 'no'}",
    ]
    for key in ("step", "epoch", "loss", "train_loss", "val_loss", "lr", "acc"):
        if key in record["metrics"]:
            parts.append(f"{key}={record['metrics'][key]}")
    if record["timeout"]:
        parts.append("timeout=yes")
    if record["alerts"]:
        parts.append("alerts=" + ",".join(record["alerts"]))
    return " | ".join(parts)


def ensure_output_paths(output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)
    raw_dir = output_dir / "raw"
    raw_dir.mkdir(exist_ok=True)
    records_path = output_dir / "records.jsonl"
    return raw_dir, records_path


def write_record(paths, record, stdout, stderr):
    raw_dir, records_path = paths
    stamp = timestamp_slug(datetime.fromisoformat(record["finished_at"]))
    stdout_path = raw_dir / f"{stamp}.stdout.txt"
    stderr_path = raw_dir / f"{stamp}.stderr.txt"
    stdout_path.write_text(stdout, encoding="utf-8")
    stderr_path.write_text(stderr, encoding="utf-8")

    persisted = dict(record)
    persisted["stdout_path"] = str(stdout_path)
    persisted["stderr_path"] = str(stderr_path)
    with records_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(persisted, ensure_ascii=True) + "\n")
    return persisted


def install_signal_handlers():
    def handle_signal(signum, _frame):
        name = signal.Signals(signum).name
        print(f"received signal {name}; exiting", flush=True)
        raise KeyboardInterrupt

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)


def main():
    args = parse_args()
    output_dir = Path(args.output_dir).expanduser().resolve()
    paths = ensure_output_paths(output_dir)
    install_signal_handlers()

    previous_hash = None
    iteration = 0

    while True:
        if args.until_local_pid and not pid_exists(args.until_local_pid):
            print(
                f"stop condition met: local pid {args.until_local_pid} no longer exists",
                flush=True,
            )
            break

        iteration += 1
        record, stdout, stderr = run_once(args)
        text_hash = sha256_text(stdout)
        changed = previous_hash != text_hash
        previous_hash = text_hash
        record["iteration"] = iteration
        record["changed"] = changed
        persisted = write_record(paths, record, stdout, stderr)
        print(format_summary(persisted, changed), flush=True)

        if args.iterations and iteration >= args.iterations:
            break

        try:
            time.sleep(args.interval)
        except KeyboardInterrupt:
            print("sleep interrupted; exiting", flush=True)
            break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
