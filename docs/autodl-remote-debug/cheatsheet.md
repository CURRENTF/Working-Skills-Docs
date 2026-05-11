# AutoDL/GPUHub Debug

## 核心规则

- 支持两种场景：通过 SSH 操作远程服务器，或已经在远程服务器上直接运行 Codex。
- 避免写系统盘：代码、clone 的项目和临时中间文件优先放 `/root/autodl-tmp`；需要长期保留或体积较大的产物放 `/root/autodl-fs`。
- 路径约定：预训练模型 ckpt 放 `/root/autodl-fs/models/`，数据集放 `/root/autodl-fs/datasets/`，自己训练产生的 ckpt 放 `/root/autodl-fs/checkpoints/`，logs 放 `/root/autodl-fs/logs/`，其他输出放 `/root/autodl-fs/outputs/`。
- Git 或下载前，先检查是否已有 Clash 等代理；已有可用代理时，不需要 `source /etc/network_turbo`。
- conda 环境要先检查项目文件和 `conda env list`，不确定就问用户。
- 长指令写到 `scripts/tmp/*.sh` 再执行，并确保 `scripts/tmp/` 被 `.gitignore` 忽略。

## 常用命令

```bash
pwd
hostname
ls /root/autodl-tmp /root/autodl-fs 2>/dev/null
/root/miniconda3/bin/conda env list
```

```bash
env | grep -Ei '^(http|https|all)_proxy='
curl -I --max-time 5 https://github.com
```

```bash
mkdir -p scripts/tmp
$EDITOR scripts/tmp/run_task.sh
bash scripts/tmp/run_task.sh
```
