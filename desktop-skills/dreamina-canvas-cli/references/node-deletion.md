# 删除节点

删除前读取本文件。参数以当前 CLI 的 `schema "node delete"` 及其 `confirm`、`status` 子命令为准；共享的批准和错误处理规则见[主 Skill](../SKILL.md)。

## 支持范围

- 支持 `image`、`video`、`audio`、`element`、`text`、`timeline`、`file`。
- 每批最多 100 个不同 Node ID，重复 ID 自动去重。可用逗号分隔或重复传入 `--node-id`。
- 不支持删除群组；可删除组内普通节点，保留父群组和未选节点。任一群组、缺失或非法目标使整批拒绝。
- 删除指定节点时会清理相关连线和引用；不会删除素材资源、取消已受理的生成任务或退还积分。

## 展示摘要，等待批准

先查询待删节点，例如删除当前画布的两个节点：

```bash
dreamina-canvas node delete --node-id node_0000000001,node_0000000002 --format json
```

该调用只查询摘要，退出码为 `10`，stdout 为空，stderr 的 `deletionConfirmation` 返回待确认信息。其他画布需显式传入 `--project-id`。

向用户展示画布、节点名称，以及每个节点当前的子节点数、连线数、引用数，等待其明确批准。不要展开相关节点清单；合计直接使用 `totals`，不要把连线数与引用数相加。数量可能随画布变化，执行时仍只删除批准的 Node ID 列表，并清理当时的关联关系。

保存摘要中的 `projectId`、`nodeIds`、`updateId`，分别作为后续示例的 `PROJECT_ID`、逗号分隔的 `NODE_IDS` 和 `UPDATE_ID`。这些值用于确认、执行和查询同一批删除。

**未获明确批准，不得调用 `confirm` 或代替用户回答终端提示。** 表格交互终端由用户输入 `y` 后确认并执行；`N` 或 EOF 不删除。单独 `--yes` 不能替代批准和删除凭证。

## 批准后确认并执行

使用已批准的原项目、节点列表和批次：

```bash
dreamina-canvas node delete confirm --project-id "$PROJECT_ID" --node-id "$NODE_IDS" --update-id "$UPDATE_ID" --format json
```

该命令不删除节点。把返回的 `data.deleteConfirmationToken` 作为 `DELETE_TOKEN`，在 `data.expiresAtMs` 前执行：

```bash
dreamina-canvas node delete --project-id "$PROJECT_ID" --node-id "$NODE_IDS" --update-id "$UPDATE_ID" --delete-token "$DELETE_TOKEN" --format json
```

凭证仅用于连接这两步，不展示给用户、不写入日志或长期记录。成功后报告本批删除结果；`idempotentReplay=true` 表示读取了原结果，不是又删除一次。

## 结果不确定或目标有误

超时、响应丢失或执行结果无法确认时，先查询原批次；也可从错误的 `deletionRecovery` 取回项目、节点列表和 `updateId`。查询不需要删除凭证：

```bash
dreamina-canvas node delete status --project-id "$PROJECT_ID" --node-id "$NODE_IDS" --update-id "$UPDATE_ID" --format json
```

| 查询结果 | 下一步 |
| --- | --- |
| `found=true`、`result=accepted` | 报告原批次已成功，不再删除或重复计数。 |
| `found=true`、`result=rejected` | 说明整批被拒绝，不自动重试；按可选 `data.error` 定位问题，没有详情时不猜原因。 |
| `found=false` | 未找到结果，不能报告成功或自动新建批次。需要重试时复用原项目、列表、`updateId` 和有效凭证；凭证过期则对同一已批准批次重新调用 `confirm`。 |

其他错误按结构化字段和[共享错误处理规则](../SKILL.md)处理。阅读 `diagnostics[].detail` 中已知的问题节点和原输入位置，再通过 `node show` 按节点 ID 核实；**改变目标列表后，重新展示摘要、取得批准并使用新 `updateId`。** 超过 100 个不同 ID 时拆批，每批分别展示摘要并取得批准。

该批次保持原账号和画布；上下文或记录不可用时，遵循[身份与本地记录恢复](recovery-and-idempotency.md)。删除用原 `projectId/nodeIds/updateId` 执行 `node delete status`，不要调用生成任务的等待命令。成功 data 带 `localStorageWarning` 时仍保留成功，查询原批次，不重复删除。

原批次已完成后再调用 `node delete confirm` 会返回 `error.code=5` 和批次已完成的原因，不签发新凭证；原批次被拒绝则保留原拒绝详情。用 `node delete status` 核对结果，不重新确认已完成批次。
