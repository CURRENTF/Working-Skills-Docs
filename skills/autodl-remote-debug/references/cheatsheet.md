# AutoDL Remote Debug Cheatsheet

## SSH（地址/端口可能更新）

```bash
ssh -p <PORT> root@connect.westc.gpuhub.com
```

如果你用 `scripts/autodl_ssh.sh`：

```bash
bash scripts/autodl_ssh.sh --print
AUTODL_PORT=<PORT> AUTODL_HOST=connect.westc.gpuhub.com bash scripts/autodl_ssh.sh --print
AUTODL_PORT=<PORT> bash scripts/autodl_ssh.sh --no-hostkey --print
```

常见：非交互环境为了避免 host key 交互卡住（仅建议临时/调试环境）：

```bash
AUTODL_PORT=<PORT> AUTODL_SSH_OPTS="-oStrictHostKeyChecking=no -oUserKnownHostsFile=/dev/null" \
  bash scripts/autodl_ssh.sh --print
```

## 路径约定（避免写系统盘）

- 临时本机盘：`/root/autodl-tmp`（项目/中间产物）
- 共享持久盘：`/root/autodl-fs`（权重/数据/缓存/长期日志）

常用结构示例：

```text
/root/autodl-tmp/PROJECT_NAME/         # 代码与短期产物
/root/autodl-fs/PROJECT_NAME/          # 权重/数据集/日志
/root/autodl-fs/models/               # 模型 ckpt（统一位置）
/root/autodl-fs/datasets/             # 数据集（统一位置）
/root/autodl-fs/.cache/               # 缓存根目录（推荐）
```

## 代理（Git / 下载前）

```bash
source /etc/network_turbo
```

## conda（先探测，再选 env）

conda 路径：

```bash
/root/miniconda3/bin/conda --version
```

先列出远端现有环境：

```bash
/root/miniconda3/bin/conda env list
```

优先看项目线索：

```bash
cd /root/autodl-tmp/PROJECT_NAME
ls
sed -n '1,80p' environment.yml
sed -n '1,80p' conda.yaml
sed -n '1,120p' pyproject.toml
sed -n '1,120p' requirements.txt
```

推荐选择顺序：

- 项目文件里写明且远端已存在的环境
- 与 `PROJECT_NAME` 同名的环境
- 唯一的非 `base` 环境
- 如果有多个候选都合理，先问用户

如果远端 shell 提示 `python: command not found`，优先用：

```bash
/root/miniconda3/bin/python -V
```

交互式运行：

```bash
source /root/miniconda3/etc/profile.d/conda.sh
conda activate <ENV_NAME>
python -V
```

非交互式运行（推荐用于脚本/自动化）：

```bash
/root/miniconda3/bin/conda run -n <ENV_NAME> --no-capture-output python -V
/root/miniconda3/bin/conda run -n <ENV_NAME> --no-capture-output python your_script.py
```

如果非交互式 shell 找不到 `conda activate`：

```bash
source /root/miniconda3/etc/profile.d/conda.sh
conda activate <ENV_NAME>
```

## SSH 一行命令跑任务（非交互式）

```bash
ssh -p <PORT> root@connect.westc.gpuhub.com \
  "bash -lc 'cd /root/autodl-tmp/PROJECT_NAME && \
  source /etc/network_turbo && \
  export PYTHONPATH=\$PYTHONPATH:/root/autodl-tmp/PROJECT_NAME/src && \
  /root/miniconda3/bin/conda run -n <ENV_NAME> python -V'"
```

## 更稳的一键执行（推荐：避免嵌套引号/JSON 转义）

用本 skill 自带的 `scripts/autodl_run.sh`，把“cd / 代理 / cache / PYTHONPATH / conda run”做成固定流程：

```bash
AUTODL_PORT=<PORT> bash scripts/autodl_run.sh --project PROJECT_NAME --conda-env <ENV_NAME> --conda-run -- python -V
AUTODL_PORT=<PORT> bash scripts/autodl_run.sh --project PROJECT_NAME --conda-env <ENV_NAME> --conda-run -- \
  python your_script.py --arg 1 --json '{"a": 1, "b": 2}'
```

如果不传 `--conda-env` / `AUTODL_CONDA_ENV`，脚本会自动探测：

- 先读项目里的 `environment.yml` / `conda.yaml` 的 `name:`
- 再尝试项目目录同名环境
- 再尝试唯一的非 `base` 环境
- 如果仍然不唯一，会直接报错并提示你指定环境名

## PYTHONPATH（推荐）

```bash
export PYTHONPATH="$PYTHONPATH:/root/autodl-tmp/PROJECT_NAME/src"
```

## 常见缓存重定向（可选，但强烈建议）

```bash
export XDG_CACHE_HOME=/root/autodl-fs/.cache
export HF_HOME=/root/autodl-fs/.cache/huggingface
export TORCH_HOME=/root/autodl-fs/.cache/torch
```

如目录不存在：

```bash
mkdir -p /root/autodl-fs/.cache/huggingface /root/autodl-fs/.cache/torch
```

## GPU 快速检查（排障）

```bash
nvidia-smi -L
nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv,noheader
```

## 模型 ckpt（本地优先）

ckpt 统一存放：

```bash
ls -lh /root/autodl-fs/models/
```

运行时尽量传本地路径（避免外网下载）：

```bash
python your_script.py --model /root/autodl-fs/models/MODEL_NAME_OR_DIR
```

如果你确认所有依赖都已在本地，且不希望任何 HuggingFace 联网行为（可选）：

```bash
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
export HF_DATASETS_OFFLINE=1
```

## 数据集（本地优先）

数据集一般存放：

```bash
ls -lh /root/autodl-fs/datasets/
```

运行时尽量传本地路径（避免外网下载）：

```bash
python your_script.py --data /root/autodl-fs/datasets/DATASET_NAME_OR_DIR
```

## Git 同步（推荐节奏）

本机：

```bash
git status
git commit -am "wip: debug on autodl"
git push
```

远端：

```bash
source /etc/network_turbo
git pull
```

## 运行长任务（tmux）

```bash
tmux new -s work
# ... run commands ...
# detach: Ctrl+b then d
tmux a -t work
```
