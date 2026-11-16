# 后编辑指引

先用 `node show` 或 `resource get` 检查媒体状态和参数。图片/视频媒体字段为可选值，缺失表示未知，不能按 0 理解。
视频 `fps` 沿用现有资源查询口径，可能来自交付档；`effectiveFps` 还会考虑成功补帧产物已达到的目标。执行准入由服务端读取权威原片信息。
使用 `node upscale video --resolution 2K|4K`、`node cutout image` 或 `node interpolate video --fps 30|60`，均需传 `--node-id`。
后编辑默认不要带 `--title`。只有用户明确要求完整自定义产物标题时才传入。
这些命令提交即执行，没有 `--run`；`--dry-run` 仅检查本地参数。

重复传 1..20 个唯一 `--node-id` 可批量执行同一操作和目标参数。
`--submit-id` 必须唯一、等长同序，省略时 CLI 逐项生成。
需要确认时沿用现有积分批准流程，批准整批消费上限。凭证隔离到具体后编辑操作。
任一报价 unknown/blocked 时整批停止；不能按免费处理，也不能擅自删掉失败成员后继续消费。
服务端在 quote、confirm 和首次 run 重新读取当前来源并校验。
读取 typed `preflight` 事实和可选 `diagnostics[].detail` 原因，不解析 message，也不上报客户端自算的媒体事实。

30 FPS 请求补到 60 FPS，在会员权益等条件满足时可继续；请求 30 FPS 会被阻断。
既有 1 FPS 容差将 29/59 FPS 视为已达到 30/60 FPS。
受理后异步完成。中断或 UNKNOWN 时保留每项 submitId，用 `operation status|wait` 恢复，不自动换身份重发。
批量 run 不是原子事务，需要逐项检查产物。
服务端明确在受理前拒绝积分批准时，可用原 submitId 和不变参数重新执行同一后编辑命令，CLI 会重新报价并按原已知批准上限重新确认。过期的不透明凭证需重新取得后编辑凭证或显式提供已批准的上限，不能猜测或自动提高额度。超时、断连、UNKNOWN 或 ABSENT 均不构成重新提交的依据。

## 会员免费补帧

报价或提交明确说明当前区域不支持该操作时，不要重试或请求积分确认。已受理任务沿用原恢复链路。

会员有效且来源合格，完整 ready 报价为 0 且 `confirmationRequired=false` 时，跳过积分询问和确认接口。
默认使用 `node interpolate video --node-id <nodeId> --fps 60 --wait`，不附加积分上限或凭证。
显式 `--credit-ceiling 0` 仍走现有零上限确认分支。
零金额不代表可执行：blocked、unknown、缺字段或报价失败都在提交前停止。
执行时服务端再次核实会员和免费权益；免费权益不可用时拒绝，不能转为付费生成。
