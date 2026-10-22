---
name: gemini-call
description: 通过原生 agy CLI 调用 Gemini 完成独立任务、第二意见、文本分析或续聊。用户要求“调用 Gemini”“让 Gemini 看一下”或用 Gemini 协助时使用；不用于修改 Codex 模型桥接或修复原生子代理协议。
---

# Gemini 调用

直接使用原生 `agy` CLI。默认模型为 `gemini-3.8-flash-high`；这是独立 CLI 会话，不是 Codex 原生 `spawn_agent`。

## 最简调用

```bash
agy --model gemini-3.8-flash-high -p '任务内容'
```

为分析、问答和第二意见使用非编辑模式，并给等待设置上限：

```bash
agy --model gemini-3.8-flash-high --mode plan --print-timeout 3m -p '任务内容'
```

- 在任务工作目录执行；`agy` 可使用该目录及其项目上下文。只需文本回答时，在任务中明确“不要调用工具或读取文件”。
- 父会话不会自动传入：提供具体目标、必要材料和期望输出，不只写“处理上面的问题”。
- 只有任务明确要求修改文件时才选择 `--mode accept-edits`。`plan` 是执行模式，不应当作文件系统隔离。保留 CLI 权限检查，不默认加 `--dangerously-skip-permissions`。
- 本机优先入口为 `~/.local/bin/agy`。先用 `command -v agy` 确认；缺失或参数不匹配时查看 `agy --help`。模型不可用时查 `agy models`，不要静默换成其他模型。

## 返回结果与续聊

需要程序化读取、计时或续聊时添加 `--output-format json`：

```bash
agy --model gemini-3.8-flash-high --mode plan --print-timeout 3m --output-format json -p '任务内容'
```

JSON 包含 `conversation_id`、`status`、`response`、`duration_seconds` 和 `usage`。同时检查退出码、stderr 与实际 `response`：本机实测超时会返回退出码 0 和 `SUCCESS`，却只有空答案，stderr 含 `print timeout ... turn in progress`，这种情况不能报告成功。保存返回的会话 ID 供后续追问：

```bash
agy --model gemini-3.8-flash-high --mode plan --print-timeout 3m --conversation '<conversation_id>' -p '后续问题'
```

不要默认使用 `--continue` / `-c`，它会续接最近会话，并发任务可能串线。报告速度时测量整个进程的耗时；JSON 中的 `duration_seconds` 不等于端到端耗时。

## 材料输入

多行任务或材料先写入文件，再作为一个完整参数传入；不要用管道或裸 `-p` 假定 stdin 会作为提示词：

```bash
agy --model gemini-3.8-flash-high --mode plan --print-timeout 3m -p "$(cat work/gemini-prompt.txt)"
```

通过 Python 调用时，用 `subprocess` 参数列表，将文件内容作为 `-p` 后的单个参数；不拼接 shell 命令。

## 失败处理

超时、登录或配额错误时如实报告，不自动改凭据、升级 CLI、改模型或修改共享桥接。需要重试时优先沿用已知会话 ID，避免重复启动可能修改文件的任务。
