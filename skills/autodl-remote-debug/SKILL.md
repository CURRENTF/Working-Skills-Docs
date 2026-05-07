---
name: autodl-remote-debug
description: AutoDL/GPUHub 调试与运行工作流：支持 SSH 操作远程服务器，也支持在远程服务器上直接运行 Codex；避免写系统盘；优先使用 /root/autodl-tmp 与 /root/autodl-fs；网络操作前先检查已有代理；动态选择 conda 环境；长命令写入 scripts/tmp/*.sh 避免引号转义问题。Use when debugging or running projects in an AutoDL/GPUHub environment.
---

# AutoDL/GPUHub Debug

## 核心规则

- 可能通过 SSH 操作远程服务器，也可能已经在远程服务器上直接运行 Codex；先判断当前执行位置。
- 避免写系统盘：代码和中间产物优先放 `/root/autodl-tmp`，权重、数据集、缓存和长期日志优先放 `/root/autodl-fs`。
- 模型优先使用 `/root/autodl-fs/models/` 下的本地 ckpt；数据集优先使用 `/root/autodl-fs/datasets/` 下的本地路径。
- Git、下载权重、下载数据集前，先检查是否已有 Clash 等代理；如果已有可用代理，不需要再 `source /etc/network_turbo`。
- 先检查项目文件和 `conda env list`，再选择 conda 环境；不确定时先问用户。
- 确定环境后，用 `conda activate <ENV_NAME>`，或用 `/root/miniconda3/bin/conda run -n <ENV_NAME> --no-capture-output <cmd>` 运行命令。
- SSH 连接信息以 AutoDL/GPUHub 页面显示为准，端口可能变化。
- 写长指令时，把命令写到 `scripts/tmp/*.sh` 后执行，避免复杂引号转义出错；确认 `scripts/tmp/` 被 `.gitignore` 忽略，防止临时脚本被误提交或上传。

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
