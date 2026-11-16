# 团队发现与空间选择

## 适用范围与能力边界

已安装 `schema` 提供 `team ls` 和 `space use/current` 时读取本指引。明确选择用户要使用的空间；发现团队不等于选中空间、获得权限或批准积分。不要通过原始请求绕过拒绝，也不要改用个人扣费。

## 发现与选择

`auth login` / `auth wait` 完成、复用登录以及 `auth account` 可以返回 `teamSpaceDiscovery`。直接使用该结果，不为展示相同选项再次调用 `team ls`。已有登录态且本次没有该结果时，执行 `auth account`。

- `status=known, hasTeamSpace=true`：展示个人空间及返回的团队名称、ID。用户已明确空间时直接遵从，否则询问使用哪个空间；不默认选第一项，也不悄悄沿用记忆中的团队。
- `status=known, hasTeamSpace=false`：继续个人流程，不改写已有选择，也不绕过先前的访问拒绝。
- `status=unknown`：登录可能已完成，但发现失败。按嵌套错误处理，允许时重新执行 `auth account`；不能当成无团队，也不因非认证错误重新登录。
- 字段缺席时核对已安装 schema，并按需要处理升级；不要编造空列表。

用户选择团队后，使用返回的 ID：

```bash
dreamina-canvas space use team "$TEAM_ID"
dreamina-canvas canvas ls
dreamina-canvas canvas use "$PROJECT_ID"
```

用户明确选择个人空间时执行 `space use personal`。用户要求查看目录或详情时用 `team ls`；按其 `hasMore/nextCursor` 原样传入 `--cursor` 翻页。名称与 ID 一起展示，大团队 ID 保留十进制字符串，空名称团队仍可按 ID 选择。列举不改变选择。

## 操作目标画布

- `space use` 核验所选空间，并保留各空间记忆的画布。`canvas use` 在该空间核验画布；选择其他空间的画布前，先显式选择目标空间。
- `canvas create` 使用当前空间；只有 `--use` 才选中新画布。节点保存不加 `--run` 时不会生成媒体。
- 显式 `--project-id` 只指定目标画布，不改变本地选择。读取、写入和生成均要求当前空间与画布所属空间一致，个人访问团队画布也不例外。不匹配时停止，请用户明确选择目标空间，再显式执行 `space use team <team-id>` 或 `space use personal` 后重试；不要修改请求头或静默切换空间。
- 按目标核验权限及 CLI 资格。`resource upload` 在传文件前检查编辑权限，不能因访问失败就改传到其他画布。共享节点、素材命令以当前 schema 为准。

## 消费与原身份恢复

遵循[积分批准](credits-and-hitl.md)。批准前核对返回的 `consumptionSubject` 是否匹配目标账号和画布；含团队时展示团队名称、ID。`userId` 是发起账号，不是团队所有者。归属缺失或冲突时，先明确归属再消费。

个人空间要求有效个人会员，或用户是至少一个付费订阅有效团队的有效成员。团队空间选择及业务访问要求当前团队成员和订阅均有效；个人 VIP 或其他团队订阅不能代替。团队资格放行个人空间，不会授予个人模型权益，也不改变个人积分的消费主体。

原账号、上下文和 ID 的处理遵循[操作恢复](recovery-and-idempotency.md)，删除批次遵循[节点删除](node-deletion.md)。本地切换不能改变已受理操作的扣费、核销或退款主体；不通过切空间或钱包走恢复捷径。

## 拒绝与下一步

- 成员、订阅、席位或消费拒绝按结构化错误，由有权限的团队成员解决所述条件。没有认证失败时不反复登录。
- 团队事实暂不可查时，仅在允许时重试同一读取；不报告空列表，也不切空间绕过。
- 选择期间其他本地进程改变了上下文时，先查看 `space current`，再显式选择预期目标，不覆盖另一进程的选择。
- 本地记录错误遵循[认证与执行权限](authentication.md)，保留已有状态，不通过清空记录让重试通过。

## 团队列表详情

`team ls` 可返回创建者名称、订阅快照及当前成员可用积分。需要详情时再查询；登录发现已有基本选项。

详情字段缺席表示信息暂不可用，不等于未订阅或零积分；保留已知的 `isVip=false`、`available="0"`。`role=owner` 表示现任所有者，`isCreator` 是另一个事实。积分 `scope=team_member` 表示当前成员额度，不是团队总池。这些快照不能代替消费批准，也不保证下次请求一定成功。

## 查看当前上下文

用 `space current`、`canvas current` 查询实时服务端事实，重新执行同一命令即可再次核验，无需 `--refresh`。`checkedAt` 是核验时间，不是权限或订阅到期时间。核验失败保留原选择，各账号分别记忆自己的选择；没有当前画布时按主 Skill 的选择步骤处理。

`auth account` 始终查询个人账号的会员与积分；`space current` / `canvas current` 查询当前空间，`team ls` 查询团队详情。会员时间表示当前档位的生效区间，与积分有效期独立。具体字段查询已安装版本的 `schema`。
