#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
autodl_ssh.sh: AutoDL SSH wrapper

Defaults (override via env or flags):
  AUTODL_HOST=connect.westc.gpuhub.com
  AUTODL_PORT=42141
  AUTODL_USER=root
  AUTODL_SSH_OPTS=""   # extra ssh args, space-separated (e.g. "-oStrictHostKeyChecking=no -oUserKnownHostsFile=/dev/null")

Usage:
  bash scripts/autodl_ssh.sh                       # open interactive shell
  bash scripts/autodl_ssh.sh -- <remote command>   # run remote command
  bash scripts/autodl_ssh.sh --print [-- ...]      # print ssh command only

Flags:
  --host <host>
  --port <port>
  --user <user>
  --ssh-opt <opt>        # repeatable; pass one ssh arg per flag (e.g. --ssh-opt -oStrictHostKeyChecking=no)
  --no-hostkey           # disable host key checking (ephemeral/debug use only)
  --print
  -h, --help
EOF
}

host="${AUTODL_HOST:-connect.westc.gpuhub.com}"
port="${AUTODL_PORT:-42141}"
user="${AUTODL_USER:-root}"
do_print=0
no_hostkey="${AUTODL_NO_HOSTKEY:-0}"
ssh_opts=()

if [[ -n "${AUTODL_SSH_OPTS:-}" ]]; then
  # Split on spaces intentionally (keep it simple for common "-oX=Y" style options).
  # shellcheck disable=SC2206
  ssh_opts+=(${AUTODL_SSH_OPTS})
fi

while [[ $# -gt 0 ]]; do
  case "$1" in
    --host)
      host="${2:?missing value for --host}"
      shift 2
      ;;
    --port)
      port="${2:?missing value for --port}"
      shift 2
      ;;
    --user)
      user="${2:?missing value for --user}"
      shift 2
      ;;
    --ssh-opt)
      ssh_opts+=("${2:?missing value for --ssh-opt}")
      shift 2
      ;;
    --no-hostkey)
      no_hostkey=1
      shift
      ;;
    --print)
      do_print=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    --)
      shift
      break
      ;;
    *)
      echo "Unknown arg: $1" >&2
      echo >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ "$no_hostkey" == "1" ]]; then
  ssh_opts+=("-oStrictHostKeyChecking=no" "-oUserKnownHostsFile=/dev/null")
fi

cmd=(ssh "${ssh_opts[@]}" -p "$port" "$user@$host")
if [[ $# -gt 0 ]]; then
  cmd+=("$@")
fi

if [[ "$do_print" -eq 1 ]]; then
  printf '%q ' "${cmd[@]}"
  printf '\n'
  exit 0
fi

exec "${cmd[@]}"
