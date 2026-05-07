#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
autodl_run.sh: Run a command on AutoDL with sane defaults

Goals:
  - Avoid writing system disk: use /root/autodl-tmp and /root/autodl-fs
  - Optionally enable proxy (/etc/network_turbo) for git/HF
  - Optionally redirect caches to /root/autodl-fs/.cache
  - Optionally add PYTHONPATH=/root/autodl-tmp/PROJECT_NAME/src
  - Avoid fragile nested quoting by sending a small bash script over SSH

Defaults (override via env or flags):
  AUTODL_HOST=connect.westc.gpuhub.com
  AUTODL_PORT=42141
  AUTODL_USER=root
  AUTODL_PROJECT=""          # if set, workdir defaults to /root/autodl-tmp/$AUTODL_PROJECT
  AUTODL_WORKDIR=""          # override remote working directory
  AUTODL_CONDA_ENV=""        # if empty and --conda-run is set, auto-detect remotely
  AUTODL_SSH_OPTS=""         # extra ssh args, space-separated (e.g. "-oStrictHostKeyChecking=no -oUserKnownHostsFile=/dev/null")

Usage:
  bash scripts/autodl_run.sh --project PROJECT -- <cmd...>
  bash scripts/autodl_run.sh --workdir /root/autodl-tmp/PROJECT -- <cmd...>
  bash scripts/autodl_run.sh --project PROJECT --conda-run -- python -V
  bash scripts/autodl_run.sh --project PROJECT --conda-run -- python your_script.py --arg 1

Flags:
  --host <host>
  --port <port>
  --user <user>
  --project <name>           # sets workdir=/root/autodl-tmp/<name> (unless --workdir is set)
  --workdir <path>
  --pythonpath-add <path>    # repeatable; default: <workdir>/src
  --no-pythonpath
  --no-proxy                 # do not source /etc/network_turbo
  --no-cache-env             # do not export XDG_CACHE_HOME/HF_HOME/TORCH_HOME
  --conda-env <name>         # explicit env; otherwise auto-detect when --conda-run is set
  --conda-run                # wrap command with /root/miniconda3/bin/conda run -n <env> --no-capture-output
  --ssh-opt <opt>            # repeatable; pass one ssh arg per flag (e.g. --ssh-opt -oStrictHostKeyChecking=no)
  --no-hostkey               # disable host key checking (ephemeral/debug use only)
  --print                    # print the ssh command (best-effort) and exit
  -h, --help

Notes:
  - If you run this from Codex and see "Operation not permitted", you likely need to rerun with network escalation.
EOF
}

host="${AUTODL_HOST:-connect.westc.gpuhub.com}"
port="${AUTODL_PORT:-42141}"
user="${AUTODL_USER:-root}"
project="${AUTODL_PROJECT:-}"
workdir="${AUTODL_WORKDIR:-}"
conda_env="${AUTODL_CONDA_ENV:-}"

use_proxy=1
use_cache_env=1
use_pythonpath=1
conda_run=0
do_print=0
no_hostkey="${AUTODL_NO_HOSTKEY:-0}"

ssh_opts=()
pythonpath_adds=()

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
    --project)
      project="${2:?missing value for --project}"
      shift 2
      ;;
    --workdir)
      workdir="${2:?missing value for --workdir}"
      shift 2
      ;;
    --pythonpath-add)
      pythonpath_adds+=("${2:?missing value for --pythonpath-add}")
      shift 2
      ;;
    --no-pythonpath)
      use_pythonpath=0
      shift
      ;;
    --no-proxy)
      use_proxy=0
      shift
      ;;
    --no-cache-env)
      use_cache_env=0
      shift
      ;;
    --conda-env)
      conda_env="${2:?missing value for --conda-env}"
      shift 2
      ;;
    --conda-run)
      conda_run=1
      shift
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

if [[ -z "$workdir" && -n "$project" ]]; then
  workdir="/root/autodl-tmp/$project"
fi

if [[ "$use_pythonpath" -eq 1 && "${#pythonpath_adds[@]}" -eq 0 && -n "$workdir" ]]; then
  pythonpath_adds+=("$workdir/src")
fi

if [[ $# -lt 1 ]]; then
  echo "Missing remote command. Use: bash scripts/autodl_run.sh --project PROJECT -- <cmd...>" >&2
  echo >&2
  usage >&2
  exit 2
fi

if [[ "$no_hostkey" == "1" ]]; then
  ssh_opts+=("-oStrictHostKeyChecking=no" "-oUserKnownHostsFile=/dev/null")
fi

pythonpath_joined=""
if [[ "$use_pythonpath" -eq 1 && "${#pythonpath_adds[@]}" -gt 0 ]]; then
  pythonpath_joined="$(IFS=:; echo "${pythonpath_adds[*]}")"
fi

ssh_cmd=(ssh)
if [[ "${#ssh_opts[@]}" -gt 0 ]]; then
  ssh_cmd+=("${ssh_opts[@]}")
fi
ssh_cmd+=(-p "$port" "$user@$host")

if [[ "$do_print" -eq 1 ]]; then
  printf '%q ' "${ssh_cmd[@]}"
  printf '%q ' bash -s -- "$workdir" "$use_proxy" "$use_cache_env" "$pythonpath_joined" "$conda_run" "$conda_env" -- "$@"
  printf '\n'
  exit 0
fi

exec "${ssh_cmd[@]}" bash -s -- "$workdir" "$use_proxy" "$use_cache_env" "$pythonpath_joined" "$conda_run" "$conda_env" -- "$@" <<'REMOTE_BASH'
set -euo pipefail

workdir="$1"; shift
use_proxy="$1"; shift
use_cache_env="$1"; shift
pythonpath_add="$1"; shift
conda_run="$1"; shift
conda_env="$1"; shift

conda_bin="/root/miniconda3/bin/conda"

if [[ "${1:-}" == "--" ]]; then
  shift
fi

if [[ -n "$workdir" ]]; then
  cd "$workdir"
fi

if [[ "$use_proxy" == "1" && -f /etc/network_turbo ]]; then
  # shellcheck disable=SC1091
  source /etc/network_turbo
fi

if [[ "$use_cache_env" == "1" ]]; then
  export XDG_CACHE_HOME=/root/autodl-fs/.cache
  export HF_HOME=/root/autodl-fs/.cache/huggingface
  export TORCH_HOME=/root/autodl-fs/.cache/torch
  mkdir -p "$HF_HOME" "$TORCH_HOME"
fi

if [[ -n "$pythonpath_add" ]]; then
  export PYTHONPATH="${PYTHONPATH:+$PYTHONPATH:}$pythonpath_add"
fi

list_conda_envs() {
  "$conda_bin" env list 2>/dev/null | awk 'NF && $1 !~ /^#/ {print $1}'
}

env_exists() {
  local needle="$1"
  shift || true
  local env_name
  for env_name in "$@"; do
    if [[ "$env_name" == "$needle" ]]; then
      return 0
    fi
  done
  return 1
}

detect_conda_env() {
  local spec_file=""
  local parsed_name=""
  local project_name=""
  local non_base=()
  local env_name=""
  local env_names=()

  if [[ ! -x "$conda_bin" ]]; then
    echo "AutoDL conda auto-detect failed: $conda_bin not found or not executable." >&2
    return 2
  fi

  while IFS= read -r env_name; do
    env_names+=("$env_name")
  done < <(list_conda_envs)
  if [[ "${#env_names[@]}" -eq 0 ]]; then
    echo "AutoDL conda auto-detect failed: no environments reported by $conda_bin env list." >&2
    return 2
  fi

  if [[ -n "$workdir" ]]; then
    for spec_file in \
      "$workdir/environment.yml" \
      "$workdir/environment.yaml" \
      "$workdir/conda.yml" \
      "$workdir/conda.yaml"
    do
      if [[ -f "$spec_file" ]]; then
        parsed_name="$(sed -nE 's/^[[:space:]]*name:[[:space:]]*["'"'"']?([^"'"'"'[:space:]]+)["'"'"']?[[:space:]]*$/\1/p' "$spec_file" | head -n 1)"
        if [[ -n "$parsed_name" ]] && env_exists "$parsed_name" "${env_names[@]}"; then
          printf '%s\n' "$parsed_name"
          return 0
        fi
      fi
    done

    project_name="$(basename "$workdir")"
    if [[ -n "$project_name" ]] && env_exists "$project_name" "${env_names[@]}"; then
      printf '%s\n' "$project_name"
      return 0
    fi
  fi

  for env_name in "${env_names[@]}"; do
    if [[ "$env_name" != "base" ]]; then
      non_base+=("$env_name")
    fi
  done

  if [[ "${#non_base[@]}" -eq 1 ]]; then
    printf '%s\n' "${non_base[0]}"
    return 0
  fi

  echo "AutoDL conda auto-detect is ambiguous." >&2
  if [[ -n "$workdir" ]]; then
    echo "Workdir: $workdir" >&2
  fi
  echo "Available environments: ${env_names[*]}" >&2
  echo "Specify --conda-env <name> or AUTODL_CONDA_ENV=<name> after confirming with the user." >&2
  return 2
}

if [[ "$conda_run" == "1" ]]; then
  if [[ -z "$conda_env" ]]; then
    conda_env="$(detect_conda_env)"
  fi
  exec /root/miniconda3/bin/conda run -n "$conda_env" --no-capture-output "$@"
fi

exec "$@"
REMOTE_BASH
