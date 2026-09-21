# Working Skills

## 安装范围

- `skills/`：通用 skills，可同步到桌面或无头 Linux。
- `desktop-skills/`：桌面端选装，不纳入服务器同步。当前包括 `ego-browser` 和 `pptx-editability`。

这是本仓库的部署策略，不代表 `pptx-editability` 技术上不支持 Linux。
克隆仓库只保存文件；不要把整个仓库递归安装到 skill 搜索目录。

## 同步通用 skills

在仓库根目录执行。先预览，确认后移除 `n`：

```bash
rsync -ani skills/ "${CODEX_HOME:-$HOME/.codex}/skills/"
rsync -ai skills/ "${CODEX_HOME:-$HOME/.codex}/skills/"
```

从本机同步到本项目使用的无头 Linux 服务器：

```bash
rsync -ani -e 'ssh -J root@8.134.70.136 -p 22022' skills/ haojitai@127.0.0.1:.codex/skills/
rsync -ai -e 'ssh -J root@8.134.70.136 -p 22022' skills/ haojitai@127.0.0.1:.codex/skills/
```

不要添加 `--delete`：目标可能含系统、插件或桌面专用 skills。
安装器或自动化只枚举 `skills/*/SKILL.md`，不能递归扫描整个仓库。

## 桌面端选装

仅在用户的桌面工作环境中按需安装；无头 Linux 跳过整个 `desktop-skills/`。

```bash
rsync -ai desktop-skills/pptx-editability/ "${CODEX_HOME:-$HOME/.codex}/skills/pptx-editability/"
```

`ego-browser` 是本机 Ego 安装所提供 skill 的内容快照。现有
`~/.agents/skills/ego-browser` 若链接到 Ego 管理的目录，保留其链接和管理方式，
不要再往 `~/.codex/skills/` 安装重复副本。新桌面环境先按
`desktop-skills/ego-browser/references/install.md` 安装浏览器及其 skill；
仓库快照不等于浏览器运行环境，不能用于向无头服务器自动安装 Ego。
