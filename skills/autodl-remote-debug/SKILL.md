---
name: autodl-remote-debug
description: AutoDL/GPUHub 调试与运行工作流：支持 SSH 操作远程服务器，也支持在远程服务器上直接运行 Codex；避免写系统盘；代码/临时中间文件优先用 /root/autodl-tmp，预训练模型、数据集、训练 ckpt、日志和输出分别放 /root/autodl-fs/models、datasets、checkpoints、logs、outputs；网络操作前先检查已有代理；动态选择 conda 环境；长命令写入 scripts/tmp/*.sh 避免引号转义问题。Use when debugging or running projects in an AutoDL/GPUHub environment.
---

# AutoDL/GPUHub Debug

## 核心规则

- 可能通过 SSH 操作远程服务器，也可能已经在远程服务器上直接运行 Codex；先判断当前执行位置。
- 避免写系统盘：代码、clone 的项目和临时中间文件优先放 `/root/autodl-tmp`；需要长期保留或体积较大的产物放 `/root/autodl-fs`。
- AutoDL/GPUHub 路径约定：预训练模型 ckpt 放 `/root/autodl-fs/models/`，数据集放 `/root/autodl-fs/datasets/`，自己训练产生的 ckpt 放 `/root/autodl-fs/checkpoints/`，logs 放 `/root/autodl-fs/logs/`，其他输出放 `/root/autodl-fs/outputs/`。
- Git、下载权重、下载数据集前，先检查是否已有 Clash 等代理；如果已有可用代理，不需要再 `source /etc/network_turbo`。
- 先检查项目文件和 `conda env list`，再选择 conda 环境；不确定时先问用户。
- 确定环境后，用 `conda activate <ENV_NAME>`，或用 `/root/miniconda3/bin/conda run -n <ENV_NAME> --no-capture-output <cmd>` 运行命令。
- SSH 连接信息以 AutoDL/GPUHub 页面显示为准，端口可能变化。
- 写长指令时，把命令写到 `scripts/tmp/*.sh` 后执行，避免复杂引号转义出错；确认 `scripts/tmp/` 被 `.gitignore` 忽略，防止临时脚本被误提交或上传。
- 不要把长实验直接写成 `ssh ... 'tmux new-session "... python ... --hyper_params {json} ..."'`。先在远端 repo 写好 quote-safe launcher，再用 SSH 只启动 `bash scripts/tmp/<run>.sh`。
- JSON/hparams 不要 inline 在 shell 命令里；在 launcher 里写 `hparams.json` 或 config 文件。需要生成 JSON 时优先使用单引号 heredoc（例如 `<<'PY'`），避免 `$VAR`、反斜杠和引号被 shell 误展开。
- 每次启动远端实验前显式打印并记录 `hostname`、`pwd`、`git rev-parse HEAD`、`git status --short`、`nvidia-smi`，避免本地/远端或错误 GPU 混淆。
- 失败、手动 abort、被 supersede 的 workaround run 也要写入 `status.tsv` 或实验文档；不要把这类 partial artifact 混入主结果表。

## 常用检查

```bash
pwd
hostname
ls /root/autodl-tmp /root/autodl-fs 2>/dev/null
/root/miniconda3/bin/conda env list
```

检查代理时，优先看当前环境是否已有可用代理：

```bash
env | grep -Ei '^(http|https|all)_proxy='
curl -I --max-time 5 https://github.com
```

只有在没有可用代理且 `/etc/network_turbo` 存在时，才考虑：

```bash
source /etc/network_turbo
```

## 长命令

复杂命令先落脚本，再运行脚本：

```bash
mkdir -p scripts/tmp
$EDITOR scripts/tmp/run_task.sh
bash scripts/tmp/run_task.sh
```

远端 tmux 启动时保持外层命令短：

```bash
ssh -p <port> root@<host> \
  'cd /root/autodl-tmp/<repo> && tmux new-session -d -s <session> "RUN_TAG=<tag> bash scripts/tmp/run_task.sh; echo EXIT_CODE=\$?; sleep 300"'
```
