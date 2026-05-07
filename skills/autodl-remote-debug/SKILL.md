---
name: autodl-remote-debug
description: AutoDL/GPUHub 远程服务器调试与开发工作流：SSH 登录、避免写系统盘（只用 /root/autodl-tmp 与 /root/autodl-fs）、登录后动态探测并选择最合适的 conda 环境（不确定时先问用户）、git 同步（commit/push/pull）、Git/下载权重前启用 /etc/network_turbo 代理、运行脚本前设置 PYTHONPATH 指向 /root/autodl-tmp/PROJECT_NAME/src。Use when you need to debug or run code on an AutoDL remote server and must follow these environment/path rules.
---

# AutoDL Remote Debug（AutoDL 远程调试）

## 快速开始（每天）

1) SSH 登录（地址/端口可能变化，以 AutoDL 页面显示为准）  
`ssh -p <PORT> root@connect.westc.gpuhub.com`

2) 进入项目目录（项目建议放在 `/root/autodl-tmp/`）  
`cd /root/autodl-tmp/PROJECT_NAME`

3) 操作 Git / 下载权重前先开代理  
`source /etc/network_turbo`

4) 登录后先探测 conda 环境，不要默认假设是 `kv`
- 看项目线索：优先检查 `environment.yml`、`conda.yaml`、`pyproject.toml`、`requirements.txt`、`README`，确认项目是否明确写了环境名或 Python/依赖约束。
- 看远端已有环境：`/root/miniconda3/bin/conda env list`
- 选择顺序：
  - 项目文件明确声明且远端存在的环境
  - 与项目目录同名的环境
  - 唯一的非 `base` 环境
  - 如果有多个都像候选，先问用户要用哪个；不要擅自猜

5) 选定环境后再执行（两种任选其一）
- 交互式：`conda activate <ENV_NAME>`
- 非交互式（更稳）：`/root/miniconda3/bin/conda run -n <ENV_NAME> --no-capture-output <cmd>`

6) 跑脚本前设置 PYTHONPATH（推荐）  
`export PYTHONPATH="$PYTHONPATH:/root/autodl-tmp/PROJECT_NAME/src"`

## 关键规则（必须遵守）

- 系统盘很小：不要把模型权重、数据集、缓存、日志写到系统盘。
- 只在这些路径写入：
  - 临时本机盘：`/root/autodl-tmp`（放代码/中间产物）
  - 服务器间共享持久盘：`/root/autodl-fs`（放权重/数据集/缓存/长期日志）
- 模型 ckpt 统一放在：`/root/autodl-fs/models/`，网络慢/外网不畅时优先使用本地已下载 ckpt（传本地路径，不要反复下载）。
- 数据集一般存放在：`/root/autodl-fs/datasets/`，优先使用本地已有数据集路径（避免外网下载/反复拉取）。
- 没确认前不要默认用某个 conda 环境，也不要擅自创建/删除/重装环境；如果探测结果不唯一，先问用户。

可选：把常见缓存挪到 `/root/autodl-fs`（避免把系统盘写满）：

```bash
export XDG_CACHE_HOME=/root/autodl-fs/.cache
export HF_HOME=/root/autodl-fs/.cache/huggingface
export TORCH_HOME=/root/autodl-fs/.cache/torch
```

## 常用工作流

### SSH 连接（可脚本化）

- 默认命令（可能随时更新）：`ssh -p <PORT> root@connect.westc.gpuhub.com`
- 用本 skill 自带的 `scripts/autodl_ssh.sh` 统一管理 host/port/user（支持 `AUTODL_PORT=<PORT>` / `--print` / `--no-hostkey`）。
- 跑复杂命令（带 JSON/多层引号）优先用 `scripts/autodl_run.sh`，避免嵌套转义。

### 在 Codex 中减少权限请求

- 第一次连远端时，优先开一个长期交互式 SSH 会话；后续所有远端命令都复用这个会话，不要为 `ps` / `tail` / `cat` / `python` 反复新建 `ssh`。
- 长任务优先放到远端 `tmux` 里；后续只需 `attach`、看日志、取结果，不需要重复启动新连接。
- 状态检查尽量合并成一次远端 shell 片段，例如把 `ps`、`tail -n 50`、`cat result.json` 放到同一个 SSH 命令里返回。
- 需要权限批准时，优先申请“窄范围、可复用”的 SSH 前缀（固定 `host + port + user`），避免为同一台机器的多条命令反复弹窗。
- 代码同步尽量批量化：一次性传多个文件，或先本地 `git push` 再远端 `git pull`，避免碎片化 `scp/ssh`。

### 代码同步（git）

- 在本机或远端执行 `git` 前：`source /etc/network_turbo`
- 推荐同步方式：
  - 本机：`git status && git commit -am "..." && git push`
  - 远端：`git pull`

### 运行/调试

- 推荐在 `tmux` 里跑长任务，避免 SSH 断开：
  - `tmux new -s work`
  - 断开后：`tmux a -t work`
- 日志/输出文件尽量写到：`/root/autodl-fs/...`（跨机器持久保留）
- 用 `scripts/autodl_run.sh --conda-run` 时：
  - 显式传 `--conda-env <ENV_NAME>` / `AUTODL_CONDA_ENV=<ENV_NAME>` 最稳。
  - 不传时，脚本会按“项目环境名 -> 项目目录同名 -> 唯一非 base 环境”自动探测。
  - 如果脚本判断不出唯一候选，会直接报错并要求指定环境；此时先问用户，不要继续猜。

## 参考资料

- `references/cheatsheet.md`：可复制的一键命令与排障清单
