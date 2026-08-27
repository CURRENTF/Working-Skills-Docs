---
name: autodl-remote-debug
description: AutoDL/GPUHub 调试与运行工作流：支持 SSH 操作远程服务器，也支持在远程服务器上直接运行 Codex；以 cgroup 而非 lscpu/free 判断实际 CPU 和内存配额；避免写系统盘；代码/临时中间文件优先用 /root/autodl-tmp，预训练模型、数据集、训练 ckpt、日志和输出分别放 /root/autodl-fs/models、datasets、checkpoints、logs、outputs；网络操作前先检查已有代理；动态选择 conda 环境；长命令写入 scripts/tmp/*.sh 避免引号转义问题。Use when debugging or running projects in an AutoDL/GPUHub environment.
---

# AutoDL/GPUHub Debug

## 核心规则

- 可能通过 SSH 操作远程服务器，也可能已经在远程服务器上直接运行 Codex；先判断当前执行位置。
- AutoDL 容器中的 `lscpu`、`nproc`、`free` 和 `/proc/meminfo` 可能显示整台宿主机，而不是实例购买的配额。规划 worker、线程池、共享内存、缓存和批量大小时必须读取当前 cgroup 的 CPU/内存限制；`lscpu` 只用于确认 CPU 型号和宿主机拓扑。
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
- 涉及实验、评测、远程服务或排障记录时，同时应用 `$experiment-run-docs` 或 `$repo-ops-docs`。这些 dated/private records 优先写入 Git-backed Research-Vault；repo `docs/` 只保留稳定 runbook、复现实验说明或用户明确要求的兜底记录。

## CPU 和内存配额

AutoDL 通常通过 cgroup quota 限制购买的 vCPU 和内存，但仍把宿主机的全部 CPU 拓扑和物理内存暴露给容器。因此，进程 affinity、`nproc` 或 `free` 也可能高估可用资源，不能作为并发或内存预算的唯一依据。

在 cgroup v2 容器中先读取：

```bash
cgroup_root=/sys/fs/cgroup

printf 'cpu.max='; cat "$cgroup_root/cpu.max"
printf 'cpuset.cpus.effective='; cat "$cgroup_root/cpuset.cpus.effective"
awk '/^(Cpus_allowed_list|Mems_allowed_list):/ {print}' /proc/self/status

printf 'memory.max='; cat "$cgroup_root/memory.max"
printf 'memory.current='; cat "$cgroup_root/memory.current"
```

- `cpu.max` 是 `<quota> <period>`；当 quota 不是 `max` 时，实际 CPU 容量为 `quota / period`。例如 `2500000 100000` 表示 25 vCPU，即使 `lscpu`、`nproc`、cpuset 和 affinity 显示更多 CPU。
- 有效 CPU 上限取 quota 容量、`cpuset.cpus.effective` 数量和进程 affinity 数量的最小值。多个进程和各自线程池共享该上限；不要让每个 worker 都按完整配额创建线程。
- `memory.max` 是容器内所有进程与 page cache 共享的硬上限；`memory.current` 是动态当前占用。值为 `max` 才表示该层没有设置硬限制。规划内存时应预留并发进程和运行时开销，不要把整个 `memory.max` 分配给单个程序。
- 不要根据 `os.cpu_count()`、`psutil.cpu_count()`、`nproc` 或 `free` 自动设置 DataLoader workers、并行任务数或缓存大小，除非已经确认它们受当前 cgroup 限制。
- 设置 `OMP_NUM_THREADS`、`MKL_NUM_THREADS`、`OPENBLAS_NUM_THREADS` 等线程池时，以有效 CPU 上限为总预算，并考虑进程数，避免乘法式超额并发。

遇到性能骤降、内存分配失败或进程异常退出时，读取累计限制事件：

```bash
cat /sys/fs/cgroup/cpu.stat
cat /sys/fs/cgroup/memory.events
```

`cpu.stat` 中的 `nr_throttled`/`throttled_usec` 表示 CPU quota 限流；`memory.events` 中的 `max`、`oom` 和 `oom_kill` 分别帮助判断是否触及内存上限及是否发生 cgroup OOM。计数是当前 cgroup 生命周期内的累计值，不要误当作单次任务结果。

如果 `cpu.max` 或 `memory.max` 不存在，先通过 `/proc/self/cgroup` 和 cgroup mounts 确认是否为 cgroup v1，再读取对应 controller 的 `cpu.cfs_quota_us`、`cpu.cfs_period_us` 和 `memory.limit_in_bytes`；不要静默回退到 `lscpu` 或 `free`。

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
