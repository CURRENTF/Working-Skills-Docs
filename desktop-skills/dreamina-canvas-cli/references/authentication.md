# 认证与执行权限

## 本地业务状态存储

`error.localStorage` 表示当前画布或任务恢复记录失败，与凭据存储独立。请检查 `reason`、`stage` 和本机 `directory`，不要据此判断服务故障或开启完全访问。通过宿主支持的流程申请该目录内的操作权限，包括临时文件、替换和清理。必要时显式设置 `DREAMINA_CANVAS_STATE_DIR`，让所有相关 CLI 调用使用已获准的私有持久目录绝对路径。该选项只改变业务记录，不改变认证凭据，且需要支持此选项的 CLI 版本。

显式 `--project-id` 指定目标画布，不改变当前选择；服务端仍核验账号、画布权限与适用的使用资格，生成仍需要恢复记录。保留原画布和提交 ID；遇到权限、损坏或空间错误，不自动清除记录或切换目录。本地失败不能证明远端生成失败。分享诊断时不要包含凭据值、记录内容或私人提示词。

根据 `error.localStorage` 区分存储类别、读写阶段、原因和 `submissionPhase`。`before_submit` 仅说明本次调用在发送前停止，仍需保留原画布和提交 ID；`after_submit` 应使用 `operation status/wait <submitId> --project-id <projectId>` 只读查询，不能重新创建或提交。只有任务恢复记录不可用、账号与所选空间仍可用时，才可继续只读查询远端；`localStorageWarning` 不否定已返回的远端结果。`canvas create --use` 返回 `current=false` 和警告时，画布已经存在：打开其 `webUrl`，后续显式传入该 `--project-id`。保留损坏记录供排查，不通过覆盖或删除记录让重试通过。

## 认证

在模型发现前，对目标 profile 执行 `auth status`。已有可用登录态则继续，否则按已安装
schema 使用 `auth login`。结合数值 `error.code`、原业务 `error.reason`、已知诊断和认证状态判断；JSON 错误消息固定英文，人类输出跟随制品 distribution。

### Device Flow：拿到链接后继续执行 `auth wait`

交互式 `auth login` 会等待授权；Agent 常用的非交互调用会先返回 challenge。**命令退出码为 0、打开授权页或用户说“已授权”，都不能单独证明 CLI 已登录。** 按本次返回的 `data.status` 分支处理：

1. `reused` 或 `logged_in`：登录已可用，继续原任务，不再发起授权。
2. `authorization_required`：保留 `data.challenge`，将 `verificationUriComplete` 发给用户；没有完整链接时，发送 `verificationUri` 和供网页输入的 `userCode`。不要将 `deviceCode` 当作用户验证码。
3. 展示链接后，立即在同一系统用户、同一二进制、同一 profile 和运行配置下执行下面的等待命令。`--device-code` 必须使用本次 `data.challenge.deviceCode` 的实际值，不是 `userCode`，也不是授权 URL。由 CLI 轮询并完成凭据交换与保存；**不能用循环 `auth status` 或仅等待用户回复来代替。**

```bash
dreamina-canvas auth wait --device-code '<data.challenge.deviceCode>' --profile '<与 auth login 相同的 profile>' --timeout 60s
```

示例中的占位符必须替换；若登录时使用默认 profile，等待时也沿用默认值。命令和字段以已安装 schema 为准。

4. 等待返回 `data.status=logged_in` 后，使用本次成功结果继续原任务。若宿主工具返回“进程仍在运行”，继续读取该进程结果，不并发启动另一个 wait，也不重跑 login。

| 等待结果 | 下一步 |
| --- | --- |
| 授权等待返回 `error.code=40011` | 只是本次等待预算用完。保留原 device code；挑战仍有效时用同一命令继续等待，不重新生成授权链接。用户暂不授权时保留恢复信息并暂停。 |
| `error.code=40014` | 本次挑战已过期；需要继续登录时，重新执行普通 `auth login` 并使用新 challenge。 |
| 其他错误 | 按下方已知原因和认证事实处理；拒绝授权或不可恢复错误时停止，不无限重试。 |

不能仅因授权尚未完成就再次登录、退登或使用 `--force`；`--force` 会清除当前 profile 登录态，不是等待授权的步骤。

| `error.reason` | 恢复方式 |
| --- | --- |
| `dns_resolution_failed` | 检查实际 CLI 进程的 DNS 和网络权限。首页 curl 成功不能证明 CLI 访问正常。 |
| `network_permission_denied` | 通过宿主支持的审批流程申请必要网络权限。 |
| `credential_store_permission_denied` | 申请必要本地凭据存储权限；仅批准网络可能不足。 |
| `credential_store_unavailable` / `credential_store_corrupt` | 检查系统存储和用户上下文；保留记录，在清除或替换前联系支持人员。 |
| `network_timeout` | 最多额外退避重试两次，仍失败则保留脱敏错误供排查。 |
| `auth_dependency_failed` | 原因尚未分类。仅做一次获批执行或普通终端对照，不据此认定服务故障。 |

DNS 或权限错误只在条件改变后验证一次。复用已获得的授权，不自动启用完全访问。如果宿主
无法授予必要访问，让用户在同一系统用户的普通终端中，用同一二进制和 profile 执行。
终端授权完成后，在 Agent 环境再次检查 `auth status`；后续请求仍可能需要权限。
错误未提供 `reason` 时，同样最多做一次对照，不猜测原因。

登录或等待授权完成后，直接使用本次成功结果，按主 Skill 和已安装 schema 提供的能力继续。已有登录态且本次没有授权结果时，用 `auth account` 获取当前账号信息。`auth status` 检查凭据状态，不能替代服务端身份查询。按返回错误和当前支持的认证命令处理，不假设一定能刷新凭据。遇到 `reason=account_changed` 时停止自动重试，用 `auth account` 核对预期账号，并保留原操作身份。

凭据存储取决于当前 CLI 和操作系统。按实际错误确认需要的权限，不根据本指南猜测内部路径或存储后端。不默认使用 sudo 或管理员模式，不导出 token、不清空凭据存储，也不把凭据迁入工作区或共享临时目录。


用户询问当前个人会员档位、积分或各自到期信息时，用 `auth account` 实时查询；字段以已安装 CLI 的 `schema` 和本次返回为准。缺失信息保持未知，不互相推算会员与积分的到期时间，也不以展示信息代替生成报价、积分批准或服务端准入。


## 安装与升级权限

安装器需要二进制安装目录和 Skill 目标目录内的写入权限；首次创建目标目录时，还需要父目录的创建权限。升级会保留 `dreamina-canvas-cli` 根目录，只更新其内容，不需要移动或删除该根目录。

权限被拒绝时，对实际安装命令申请宿主支持的单次批准；宿主无法授予时，在同一系统用户的普通终端完成安装。安装失败不需要注销账号或清理钥匙串。已有安装锁时先检查是否仍有安装进程；若输出备份保留位置，先恢复或核对该备份，不重复清理。安装过程中不要加载该 Skill，完成后在新会话中使用。

安装提供的完整包时，解压后执行其中的 `install.sh`，或通过 `DREAMINA_CANVAS_PAYLOAD_DIR` 指定包目录的绝对路径。保留同目录的 `payload.sha256`、匹配平台二进制、`skill.tar.gz` 与 `version.json`；包不完整或不匹配时不能回退到 CDN。按安装器输出的目标绝对路径和版本核对实际 CLI，并在新会话加载更新的 Skill。PATH 警告不代表安装失败。

错误携带 `clientUpgrade` 升级要求时，如有 `clientUpgrade.installCommands`，按操作系统和终端选择对应命令；Windows PowerShell 与 CMD 的命令不同。缺少该字段时遵循 `upgradeUrl` 指引，不自行推断其他脚本路径。升级响应本身不是执行命令的授权。更新后验证 CLI 版本并读取更新的 Skill，保留当前 profile 和凭据；已有 `operationRef` 时继续原任务，不重复提交。
