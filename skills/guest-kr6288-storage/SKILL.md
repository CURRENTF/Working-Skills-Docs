---
name: guest-kr6288-storage
description: guest-KR6288 本机存储布局规则。Use when working on machines whose hostname starts with `guest-KR6288`, especially for running code, training/evaluation, downloading datasets/checkpoints, saving logs, or producing experiment outputs. Keep `~/` for code only; keep checkpoints and data under `/data2/haojitai`; keep logs and generated outputs under `/data2/haojitai/outputs`.
---

# guest-KR6288 Storage Rules

## 触发判断

- 如果当前机器 `hostname` 以 `guest-KR6288` 开头，执行本 skill 的路径规则。
- 如果是通过 SSH 操作远程机器，先在远程执行 `hostname`，不要用本地机器名推断。

## 核心规则

- 系统盘 `~/` 只放代码、轻量配置和小型临时脚本；不要把数据集、模型权重、训练 ckpt、日志或大输出写到 `~/`。
- 数据集、模型权重、训练 ckpt、缓存的大文件统一放在 `/data2/haojitai` 下；优先沿用项目已有的清晰子目录，例如 `/data2/haojitai/datasets`、`/data2/haojitai/checkpoints`、`/data2/haojitai/models`。
- 日志、评测结果、生成结果、可视化、wandb 本地目录、临时导出和其他运行输出统一放在 `/data2/haojitai/outputs` 下；按项目名和实验名再分子目录。
- 运行训练、评测、下载或转换脚本前，检查命令里的 `--output_dir`、`--logging_dir`、`--cache_dir`、`--save_path`、`--ckpt_dir`、`WANDB_DIR` 等路径，不要默认落到当前 repo 或 `~/`。
- 如果某个工具必须在 repo 内写小文件，确认它不是大体积产物；大产物应改到 `/data2/haojitai/outputs/<project>/<run>`。

## 常用检查

```bash
hostname
pwd
df -h ~ /data2
ls /data2/haojitai /data2/haojitai/outputs 2>/dev/null
```

## 路径习惯

```bash
mkdir -p /data2/haojitai/outputs/<project>/<run>
```

长命令建议先写到 repo 的 `scripts/tmp/*.sh`，但脚本内的大文件路径仍应指向 `/data2/haojitai` 或 `/data2/haojitai/outputs`。
