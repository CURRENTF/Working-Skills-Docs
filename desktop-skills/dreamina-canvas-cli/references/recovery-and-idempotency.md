# 恢复与幂等

超时、进程中断、传输丢失、批量响应不完整或终态不确定时，读取本文件。

认证失败时，先遵循[认证恢复流程](authentication.md)，再续跑同一操作。

## 副作用前冻结身份

- node save：保存 release 声明的 Node ID 与 update ID；
- node run：为每个输入 item 保存一个 submit ID；
- 长 operation：保存返回的 operation reference；
- 最终选片：保存选中的 Resource ID。

不能因为第一次响应丢失就换新 identity。

`node run` 的每个 `data.items[].submitId`，就是 `operation status` / `operation wait` 接受的
`<operation-ref>`。用 `operation wait <submitId> --project-id <projectId>` 观察同一次工作；不要传
Node ID，也不要另造 UUID。

## 恢复决策表

| 观测 | 动作 |
| --- | --- |
| operation 仍为 `running` | 继续观察同一个 operation reference |
| 本地 wait 时间预算耗尽 | 返回可恢复状态（退出码 `20`）；服务端任务可能仍在运行 |
| 媒体 `--run --wait` 已受理，但 status 查询失败 | 保留 `partialData.items[0]` 的 `nodeId`、`submitId` 和 `state=ACCEPTED`；执行 `operation wait <submitId> --project-id <projectId>`，不要重跑 create/edit/run |
| 纯保存 node create/edit 失败或响应丢失 | 先回读节点和草稿，再带原 node/update 身份及来源声明重试。草稿未保存时目标关联也可能已留下；不要自动解绑。 |
| **媒体 `--run` 报价后退出 `10`** | 节点已保存且没有扣费。复用 `partialData.items[0]` 里的 **两个**身份（`nodeId` 与 `submitId`），补上批准方式重跑 |
| submit 响应丢失 | 用同一个 submit ID 做只读检查，**不要重放运行**——原请求可能从未到达服务端，重放会成为首次提交并真实扣费 |
| submission 已 `completed` / `in_progress` | 重放记录结果，不重新索要确认 |
| `operation status` 返回 `state=awaiting_confirmation`，即使资源为空、没有 `submissionOutcome` | 节点已保存，运行尚未提交。`submission.resubmittable=true` 时保留原节点和 submit ID，在原批准范围内继续。批准不足时先取得用户批准。旧记录无法确认原身份时只能查看。 |
| item 终态 `rejected`（如时间轴片段超上限、音频重叠或素材/类型不匹配） | 修正输入或方案，盲目重试无效 |
| 引用的上游素材已有生成任务、仍在生成中（生成节点引用、时间轴片段都可能遇到） | 保留原 submit ID，用 `--wait` / `operation wait` 等待该任务产出可直接使用的产物；不要重新提交该来源的生成 |
| 引用的上游节点从未提交生成且没有产物 | 此时没有 submit ID，等待无效；在用户已授权范围内先生成该来源，取得可直接使用的产物后再继续下游操作 |
| **submission 状态为 `absent`** | 不可据此断定没有运行：记录可能已过期。任何重提前先核对画布或积分账本 |
| identity 暂时无法解析且 submission 已 `accepted` | 保持 `unknown` 并要求 resume，绝不能返回空成功，也不要重新提交 |

如果已尝试提交但结果无法确认，或查询返回 `error.code=40012`、退出 `20`，保留原身份，用 `operation status/wait` 只读核对。若仍无法确认，将未知状态告知用户即可停止轮询。远端查不到记录不能作为重新提交的依据。

wait 对瞬态 status 查询失败按轮询间隔最多额外重试两次，共享原 timeout；绝不重复执行
save、quote、confirm 或 run。`--timeout 0` 只查一次。媒体提交已受理后，瞬态重试耗尽、
等待超时或中断返回 `ok=false`、退出码 `20`，保留原身份和已知原因。这表示不能重跑原 create/edit/run；
可以用返回的 submit ID 发起新的只读 `operation wait`。保持原区域与环境。已受理不等于
生成完成，status 错误码及可获得的日志关联 ID 仍用于诊断。登录、权限、升级及无效响应
不自动重试，也不统一改成等待超时：先处理真实认证、访问、升级或响应问题，再观察同一个 submit ID。

**`absent` 与 `unknown` 不是同义词，也分属不同维度，但两者都不能单独授权自动重提**：`absent`
是提交事实维度（这次提交在服务端存不存在），可能是记录已过期；`unknown` 是逐项裁决维度
（这份产物这次被受理还是被拒），表示服务端无法建立安全结论。必须结合完整提交事实与外部
证据决策，不能猜。

## 批量恢复

发请求前先为整个 batch 创建 submit ID，并保存等长同序的结果向量。传输失败不能让后续 item 的身份丢失。

批量运行的 submit ID **逐项可显式指定**，与节点清单按顺序一一对应。CLI 会在提交前记录生成身份，进程中断后按原 ID 观察。保留返回的 ID；需要在首次响应前由调用方掌握身份时，显式指定这些 ID。本地记录缺失时，带 `--project-id` 查询已知的原 submit ID；不能猜测未执行或另建一次尝试。

数量不匹配、有重复、有空值或不是合法 UUID 时，命令在**发出运行请求之前**就以参数错误退出：
一次运行都不会触发，一分钱都不会花。所以这类输入错误不需要走恢复流程，直接修参数重跑。

逐项区分 `accepted`、`rejected`、`unknown`（run 裁决维度），以及 `pending` / `running` /
`succeeded` / `failed`（资源维度）。这些是不同维度的观测，不是同一个枚举。
`unknown` item 用原 submit ID 恢复；不能用新 ID 重跑已受理 item。

## 本地 job state

恢复保持原认证账号和画布。遇到 `error.code=40016` 时停止并显式恢复预期上下文，不悄悄切换；错误明确指出记录的原身份不可验证（`code=40003`）时，可按当前权限观察记录，但不能认领为当前身份继续批准或提交。组合 `--run` 已尝试提交的操作先用 `operation status/wait` 查询，不重新保存或提交。存储错误和警告按[认证与本地状态恢复](authentication.md)处理；成功结果中的 `localStorageWarning` 不改变远端成功。

使用 CLI 的恢复记录，不手工改写。宿主另记任务进度时，只保留恢复所需的 region、canvas、Node ID、update ID、submit ID、operation reference 和选中 Resource ID，并仅允许当前用户读取。

不得保存凭据、signed URL、provider payload、访问材料或 credit-confirmation token。

## 完成规则

资源集合为空不等于“全部成功”。每个必要输出都必须有明确的终态资源事实。
详见 [completion-and-validation.md](completion-and-validation.md)。

## 样片转正片

生成样片前，以及向用户交付样片结果时，都必须明确提醒：**样片最长存储 7 天，过期后不可再生成正片。** 用户需要正片交付时，提醒其在有效期内完成转正，不等到转正失败后才告知期限。

具体截止时间以服务端为准。工具明确返回截止时间时，连同时区告知用户；未返回时只说明最长 7 天，不编造日期或倒计时，也不从本次查看或交付时间重新起算。样片已过期时，说明需重新生成样片后再尝试转正；不能通过重试延长原样片的有效期，重新生成仍遵循已有积分授权规则。

先用 `model list --type video` 选择 canonical model，再用 `model <canonical-model> --type video` 查看完整规格中的 `generationKind=sample` 和 `draftPromotion.params`。提交 `node promote video-sample --node-id <nodeId> --resolution <resolution> --credit-ceiling <credits>`。受理后创建新产物节点，来源仍为样片。超时后使用同一 `submitId` 执行 `operation status/wait`，不要更换提交 ID 来消除歧义。确认凭证仅用于该操作及目标分辨率；可用性和过期判断以服务端为准。
