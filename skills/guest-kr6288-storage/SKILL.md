---
name: guest-kr6288-storage
description: guest-KR6288 本机存储布局和磁盘回退规则。Use when working on machines whose hostname starts with `guest-KR6288`, especially for running code, training/evaluation, downloading datasets/checkpoints, saving logs, or producing experiment outputs. Keep `~/` for code only; prefer `/data2/haojitai` for large files and outputs, and fall back to `/data1/haojitai` when `/data2` is full, unavailable, read-only, or unhealthy.
---

# guest-KR6288 Storage Rules

## 触发判断

- 如果当前机器 `hostname` 以 `guest-KR6288` 开头，执行本 skill 的路径规则。
- 如果是通过 SSH 操作远程机器，先在远程执行 `hostname`，不要用本地机器名推断。

## 核心规则

- 系统盘 `~/` 只放代码、轻量配置和小型临时脚本；不要把数据集、模型权重、训练 ckpt、日志或大输出写到 `~/`。
- 新增数据集、模型权重、训练 ckpt、缓存和运行输出优先写到 `/data2/haojitai`；如果 `/data2` 满盘、空间不足以完成任务、不可访问、只读或出现挂载/IO 异常，则改用 `/data1/haojitai`。
- 选择一次运行的根目录后保持一致，不要把同一次运行的日志、结果和 ckpt 分散到两个盘。把实际选择记录到命令、manifest、`status.tsv` 或运行日志中。
- 已存在的模型和数据从其现有路径读取；不要仅因为本次输出回退到 `/data1` 就复制或迁移已有输入。
- 日志、评测结果、生成结果、可视化、wandb 本地目录、临时导出和其他运行输出放在所选根目录的 `outputs/<project>/<run>` 下。
- 运行训练、评测、下载或转换脚本前，检查命令里的 `--output_dir`、`--logging_dir`、`--cache_dir`、`--save_path`、`--ckpt_dir`、`WANDB_DIR` 等路径，不要默认落到当前 repo 或 `~/`。
- 如果某个工具必须在 repo 内写小文件，确认它不是大体积产物；大产物应写到所选数据根目录。

## 根目录选择

1. 在启动任务前检查 `/data2` 和 `/data1` 的挂载、可写性、可用空间以及近期内核/文件系统错误。
2. `/data2` 健康、可写且剩余空间足够完成任务时，设置 `GUEST_DATA_ROOT=/data2/haojitai`。
3. `/data2` 满盘、余量不足、不可访问、只读或出现 IO/文件系统错误时，设置 `GUEST_DATA_ROOT=/data1/haojitai`，并在运行记录中注明回退原因。
4. 两个数据盘都不可用或空间都不足时停止，不要回退到系统盘。
5. 如果运行中途因磁盘故障失败，保留并标记原产物；在另一个盘使用新的运行目录恢复或重跑，不要静默覆盖或把两个目录合并成一个结果。

## 常用检查

```bash
hostname
pwd
df -h ~ /data2 /data1
findmnt -no TARGET,OPTIONS /data2 /data1
ls -ld /data2/haojitai /data1/haojitai 2>/dev/null
```

## 路径习惯

```bash
GUEST_DATA_ROOT=/data2/haojitai  # /data2 不可用时改为 /data1/haojitai
mkdir -p "$GUEST_DATA_ROOT/outputs/<project>/<run>"
```

长命令建议先写到 repo 的 `scripts/tmp/*.sh`，但脚本内的大文件路径仍应指向本次选定的 `GUEST_DATA_ROOT`。
