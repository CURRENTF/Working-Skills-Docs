# 身份与引用

判断该持久化什么身份、下游应如何消费上游素材时，读取本文件。

## 先选来源节点，再看产物

目标画布已有来源节点时，下游生成、主体(Element)绑定和时间轴片段都使用其 Node ID。
不要仅为了构建引用而读取或复制它的 Resource ID，生成成功后也一样。节点引用保留上游连线，
使用来源节点的选中产物；资源引用冻结素材，不会反查来源节点并连线。

| 用途 | 画布已有来源节点时的默认写法 |
| --- | --- |
| 图片/视频生成，包括首尾帧 | `--ref node:<node-id>` |
| 正文中的媒体占位符 | `{{node:<node-id>}}` |
| 主体的主素材/音色/辅助素材 | `--main <node-id>`、`--voice <node-id>`、`--auxiliary <node-id>` |
| 时间轴视觉/音频片段 | `--clip <node-id>,kind=canvas_node`、`--audio-clip <node-id>,kind=canvas_node` |

节点返回的 Resource ID 标识具体产物，供资源状态和元信息查询、下载与选片记录使用。
操作轮询本身使用 `operation status|wait <submitId>`，不要求 Agent 先从节点取 Resource ID。

资源引用只用于资产库/上传后尚无来源节点的素材，或用户明确要求固定某一产物、不跟随后续选片。
适用例外时记录原因及选中的 Resource ID；其他情况保留 Node ID。导入资源一旦已有画布节点，
后续优先引用该节点。保持一致性、生成成功或响应包含 `resources[]` 都不是冻结理由。

需要确认引用结构或排查连线时，可按 [completion-and-validation.md](completion-and-validation.md)
校验保存后的来源身份和上游连线。没有引用的生成无需执行这些检查。
生成成功或出现参考缩略图，不能证明节点关系存在。

## 公开身份模型

生成引用有四个显式协议类型，其中只有两类当前会解析成业务对象：

| 身份 | 书写形态 | 含义 | 适用场景 |
| --- | --- | --- | --- |
| Node ID | `node:node_xxx` | 画布节点，其选中媒体产物或 Text 内容可能变化 | 画布已有来源节点时的默认选择，保留上游连线 |
| Resource ID | `res:<resourceId>` | 某一份具体素材结果 | 无来源节点，或用户明确要求冻结；不反查节点连线 |
| URI / VID | `uri:<value>` / `vid:<value>` | 仅预留协议值，当前不解析 | 只用于对象与枚举表达 |

生成引用 flag 与正文占位符使用 `type:value` / `{{type:value}}`。主体(Element)和时间轴(timeline)
selector 沿用现有裸 Node ID / Resource ID 契约，它们不是本次生成引用协议。

其余形态由 CLI 在**本地**拒绝并以参数错误退出，**不会发出请求**：

- `uri` / `vid` 可以作为带类型的协议值传输，但服务端会明确返回暂不支持；不要在 CLI
  解析或当作访问能力。
- Resource ID 接受规范小写 UUID 或工作流返回的 `resource_<正整数>[-<非负索引>]`，索引 0 合法。
  原样使用返回的身份，不自行添加前缀或转换 UUID；UUID 的大写、`urn:uuid:` 前缀和去掉连字符形式均被拒。
  项目 ID 与上传创建幂等键仍使用 UUID。

存在性、类型、状态、项目关系和授权仍由服务端权威判断：形态合法只说明「写法对」，不代表可用。

## 解析规则

1. 每次解引用都针对已认证 actor 和目标画布/项目实时判断。
2. 仅知道 ID 不代表可用；无权、不存在或关系已失效的素材不能继续引用。
3. 主体(Element)绑定使用的 Node ID 必须属于目标主体(Element)所在画布；跨画布、不存在与无权 Node ID
   在公开面返回同形错误。
4. 保存 Resource 引用时，目标项目必须已有有效关联；缺少关联时按下文显式声明来源，仅知道资源 ID 不够。
5. 语法或 capability hint 不是授权快照。
6. 临时访问材料只能在内存中立即消费，永远不是持久身份。
7. 引用什么决定何时校验终态：`res:`（Resource ID）引用要求素材已达成功终态，还在生成中就在
   **保存期**被拒；`node:`（画布节点）引用则**允许指向还在生成中的上游节点**，其终态留到
   **run 期**才校验。所以想承接一个尚未出图的上游产物，应该引用它的节点（`node:node_xxx`），
   不要用它尚不存在的 Resource ID。Text 上下文不要求先生成 Resource，但源节点必须可访问、
   内容必须可读（可访问性与可读性主要在 run 期兜底校验）。
   例外：时间轴的片段（`--clip` / `--audio-clip`）不能引用还没生成好的素材——即使写的是
   Node ID，被拼入的节点也必须已经生成成功、有可直接使用的产物，否则保存时间轴会被拒绝。
8. 「不存在」「无权」「已解绑」三种情形返回**同一个**错误，刻意不可区分。不要试图从错误码
   推断某个 ID 是否存在。

## 上传素材的身份

> 仅适用于 schema 暴露 `resource upload` 的制品；`schema` 中没有它时跳过本节。

`resource upload` 始终显式传 `--project-id`，即使已传 `--resource-id`；资源 ID 是重试身份，不决定上传项目。

上传身份冻结后的失败保留 `error.resourceId` 和 `error.projectId`。它们说明本次使用的身份，不证明存储或登记已成功。响应丢失时保留原身份，在可以核实时查询原资源，不自动换新 ID 上传。码 `40012` 表示结果无法确认，不是确定被拒绝。

注册了 `resource upload` 的制品会在 `schema` 中暴露它；本地文件上传是受限的运行时能力，并非每个
这类制品都装配。未装配时以服务端准入为准。本地图片、视频与音频都直传后登记为项目资源；
图片 `--source-url` 仍由服务端抓取转存。结果始终包含 `resourceId + mediaType`，不按 `--import-kind`
区分，也不下发服务端存储句柄；`resourceId` 可用于 `res:<resourceId>`、`resource get/download`
与 `node create --resource-id`。用 `--resource-id` 导入已登记资源时，必须同时声明 `--import-kind`，
取值与登记意图同一套词汇：
`local_upload` 表示本地上传素材，`external_generated` 表示外部平台生成产物。
两种取值也都可不绑定 Resource 单独声明。`--resource-id` 接受其中任一种 import kind；该值只作为
创建意图消费，不进草稿。坐标与 import kind 独立。

`resourceId` 同时是 `node create image|video|audio --resource-id` 的入参：创建时声明「这些已登记
资源属于本节点」，让节点落地即带产物。用于把本地上传或外部平台已生成的产物导入画布，同时带上
原平台的 prompt 与模型参数以便继续改、再生成。多个 resourceId 视为同一批次内的候选，顺序即候选
顺序，首个为主选；仅 create 支持，仅媒体节点支持资源声明。`text` / `element` / `timeline` 也可声明
同一组 `--import-kind` 取值，但不得传 `--resource-id`。

资源归属、状态与类型匹配由服务端裁决且拒绝而非静默丢弃；节点 source 由服务端物化，调用方无法指定。

批次身份取同一条命令的 `--submit-id`（省略则自动生成）：重试复用同一值即批次身份稳定。
这是 `--submit-id` 唯一能脱离 `--run` 使用的场景——导入走纯保存链，但同样需要提交身份。

## 节点位置与避让

`--x --y` 是可选参数，默认不传；任务有明确的位置或布局需求时再指定，
例如移动节点、整理画布、外部导入时控制落点，或复刻画布时保留原布局。
外部导入没有位置要求时，也可沿用智能布局。
六类 `node create` 与 `node edit`（含导入）均支持；指定时，两个值须同时提供且为有限值，
支持零与负数。创建时显式位置优先于智能布局，但不会自动避开已有节点；编辑时可只改坐标，也可与内容一起保存。
整组缺席时，创建保留智能布局，编辑保留原位置。移动时间轴保留原轨道。

任务需要指定位置时，使用实际保存的尺寸：

1. 从保存结果的 `data.node` 或 `node show` 的 FOUND 项读取 `layout.x/y/width/height` 和 `parentNodeId`。
   新节点尺寸未知时，先按智能布局创建并查询，再根据任务需要移动；不要假定所有节点一样大。
2. 在同一坐标空间按节点矩形分别留出横向间距 `gapX` 和纵向间距 `gapY`。
   横向排列可用 `nextX = x + width + gapX`；换行可用 `nextY = rowY + max(rowHeights) + gapY`。
   可从横向 `gapX = 160` px、纵向 `gapY = 80` px 开始，按实际尺寸调整；
   图片比例不同，时间轴也可能明显更宽，写入后须回读检查。
3. 直接比较的节点须处于同一父组，根节点属于同一画布坐标空间。跨父组比较时先换算到画布坐标；
   不把父组包含其子节点视为需要消除的重叠，不为排布改变编组关系。
4. 编辑后重新读取位置和宽高，确认非预期重叠已消除、内容和编组关系保持。生成或内容编辑后尺寸变化时，
   使用最新宽高重新检查；只移动位置时不带 `--run`。

跨项目或区域复刻画布且任务需要保留原布局时，先用 `node show` 读取每个源节点，并把 `node.layout.x/y` 原样传给
目标节点的 `--x --y`，前提是源节点为根节点。若返回 `parentNodeId`，坐标相对父组；创建目标根节点前
须加上父组坐标换算为画布坐标。编辑使用与查询相同的坐标空间，并保持编组关系；`parentNodeId` 只读。
`layout.width/height/zIndex` 用于读取和检查布局，不能作为创建或编辑参数传入。

## Prompt 引用

生成引用使用上述显式类型。当前可用公开身份是 `node` 与 `res`；`uri` 与 `vid` 仍是预留
协议值，不是 upload 结果提供的访问能力。

Prompt 中有两种不同用途，不能混淆：

- `--ref node:<node-id>` 把来源节点加入生成引用集合，提供素材槽、顺序和上游连线。
- `{{node:<node-id>}}` 将来源节点绑定到正文当前位置，相当于产品 prompt 里的对象 @ 引用。
  CLI 使用稳定的公开占位符；自然语言名称或手写的 `@名称` 不会建立节点引用。

当 prompt 同时描述多个可复用人物、物体或环境，并且这些对象在句子里承担不同动作、位置或关系时，
建议在对应词语位置使用 `{{node:<node-id>}}`。仅把同一批节点追加到 `--ref`，虽然能建立引用集合和
画布上游关系，但不会表达每个节点对应正文中的哪个对象及其动作、位置或关系。

以下为参数片段；`node_a`、`node_b` 代表已查询确认、类型适配当前 mode 的实际 Node ID，
使用时替换并补齐当前 schema 要求的字段：

```bash
--mode i2i \
--prompt "将{{node:node_a}}放在左侧，将{{node:node_b}}放在右侧" \
--ref node:node_a \
--ref node:node_b
```

同一个节点同时出现在正文占位符和 `--ref` 中时，会合并为一个引用槽；最终槽位顺序以保存后
`generation.references[]` 为准，不能仅从 flag 顺序推断。正文占位符不替代 mode 的首尾帧等槽位配置。
若该节点只作为额外风格、背景参考或 Text 前导上下文，
不需要绑定到正文位置，则可只放在 `--ref`。Text 节点仍遵守下文的限制，不能写成正文占位符。

首尾帧、主辅素材或模型 slot 的引用顺序可能有语义，必须保留用户计划与 model schema 的顺序。

读回节点时，正文以你写入时的同一套公开占位符形态返回——写 `{{node:node_xxx}}`，读出来也是
`{{node:node_xxx}}`。这条闭合正是读回结果能直接
当下一次写入输入的理由，也正是 Resource ID 只允许一种书写形态的原因：接受大写或 `urn:uuid:`
之类的等价写法，读回时就只能给规范化后的那一份，逐字闭合随即失效。

正文只从节点的 `generation` 读，不要从响应里同时存在的 opaque 画布草稿 body 读。非生成型节点没有
`generation`。它的 `references` 就是槽位序，混用正文占位符与显式引用 flag 时，读它来确认
最终顺序。

### 视频 mode 取决于解析后的来源类型

不能仅凭「恰好有一个 Node 引用」就选择帧模式。`node_` 前缀只能说明它是画布 Node，不能区分
图片、主体(Element)、Text、视频或音频。先查询被引用 Node 或 Resource 的真实类型，再根据解析后的
素材类型与实时模型能力选择公开 mode：

| 解析后的生成素材 | 公开 `--mode` | 约束 |
| --- | --- | --- |
| 没有媒体素材 | `t2v` | 不能携带媒体引用 |
| 一张图片作为锁比例首帧 | `first_last_frame` | 图片占首帧槽位并决定输出 ratio |
| 两张有序图片 | `first_last_frame` | 顺序依次为首帧、尾帧，两张原图 ratio 必须一致 |
| 单图但需保留调用方指定 ratio | `m2v` | 使用兼容的多模态模型 |
| 主体(Element)节点或混合多模态素材 | `m2v` | 使用实时模型查询返回的兼容模型 |

主体(Element)仍使用带类型的 Node 引用。通过 `--ref node:<element-node-id>` 引用，并搭配 `--mode m2v`：

```bash
--mode m2v \
--ref node:node_element \
--prompt "让{{node:node_element}}在描述的场景中动起来。"
```

`m2v` 是 CLI 对 multimodal 模式的公开写法。服务端生成规格中可能使用 `multi_modal`，但
`multi_modal` 不是 CLI `--mode` 的合法值。主体(Element)不能占用 `first_last_frame` 的帧位。

### Text 节点仅作为上下文引用

Text 不是图片/视频素材，但在所选 mode 允许时，可以通过 `--ref node:<text-node-id>` 提供
prompt 上下文。不能在 prompt 正文中写 `{{node:<text-node-id>}}` 占位符。图片、视频保存入口
都有这条限制，即使同时提供了合法图片引用也不例外。
把 Node ID 写成正文占位符前，先查询源节点类型；不能仅凭 `node_` 前缀区分
Text 与媒体节点。

运行时会读取被引用 Text 的内容，并作为上下文拼到 prompt 前面；它不占媒体素材位，也不是在
正文指定位置展开。仍须满足所选 mode 对 `--prompt` 与引用的要求。

引用位置与 mode 必须一起判断：

生成 mode 使用简短的协议名，完整含义为：`t2i` = text-to-image（文生图）、
`i2i` = image-to-image（图生图）、`t2v` = text-to-video（文生视频）、
`m2v` = multimodal-to-video（多模态生视频），视频另有 `first_last_frame`（首尾帧），
音频有 `tts`（text-to-speech，文本转语音）/ `music`（音乐）。image-to-video 不是公开 CLI 模式：
单图生视频用 `first_last_frame`（一张首帧图），图片或视频引导的生成用 `m2v`。模型发现服务可能
返回内部写法，但 CLI 始终归一回这些公开名。

| 输入 | 引用约束 |
| --- | --- |
| 图片 `t2i`：Text 放 `--ref`，正文为普通文字 | 合法的上下文形态，不要求图片素材；T2I 不等于引用列表必须为空。 |
| 图片 `i2i`：`--ref` 里只有 Text | 拒绝：Text 不能满足 I2I 至少需要一份图片、主体(Element)或图片 Resource 的要求。只有 Text 上下文时用 `t2i`。 |
| 图片 `i2i`：图片和 Text 都放 `--ref`，正文为普通文字 | 合法的混合形态：图片提供素材，Text 提供上下文。 |
| 图片 `t2i`：引用图片、主体(Element)或 Resource | mode 不匹配；图片素材输入应使用 `i2i`，额外添加 Text 不会使其变成 T2I。 |
| 图片/视频：Text 写进正文占位符 | 拒绝；即使同一个 Text 也放了 `--ref`，或者存在合法图片素材，仍然拒绝。 |
| 视频 `m2v`：图片素材加 `--ref` 中的 Text | 合法的上下文形态，仍需满足所选模型的素材与参数要求。 |
| 视频 `t2v`：存在任何引用 | 当前 CLI 拒绝，包括 `--ref` 中的 Text；不能把图片 T2I 的规则照搬到视频 T2V。 |

视频 `first_last_frame` 还有 CLI 引用数量约束：合并后必须为一条或两条。
额外添加 Text 会占用这项数量校验的条目，虽然它不算媒体素材，也不能替代帧。
不要给所有视频 mode 无差别添加 Text。

上述合法形态描述的是引用契约，不保证任意模型、制品版本或环境都能保存或运行成功。
源节点权限、媒体就绪状态和模型约束仍需满足；协议校验与实际端到端验证必须区分。

下面是参数片段，`node_text`、`node_image` 分别代表已经查询确认的真实 Text、图片 Node ID，
使用时另行补齐命令所需的其他字段。

图片只有 Text 上下文：

```bash
--mode t2i --ref node:node_text --prompt "根据参考文字生成海报。"
```

图片素材与 Text 上下文都使用引用列表：

```bash
--mode i2i --ref node:node_image --ref node:node_text \
--prompt "按参考文字修改参考图片。"
```

视频混用 Text 与图片时，只有图片可以放进正文占位符：

```bash
--mode m2v \
--ref node:node_text \
--prompt "让{{node:node_image}}中的画面动起来。"
```

需要在正文指定位置使用某段文字时，直接写普通文字，不使用 Text 节点占位符。复制后的文字
不会跟随源节点后续修改；除非确实需要它再次作为前导上下文出现，否则不要同时添加同一个 Text 引用。

### 引用拒绝的诊断边界

`error.code=2` 表示参数错误，不能证明 Text 全面不支持，也不能证明请求被生成模型拒绝。可选 `diagnostics[].detail` 说明具体输入和约束，用于理解原因；不能解析其措辞或动态值执行自动动作。数量、时长和模型上限以 `model list`、报价结果或 typed `preflight` 事实为准。细节缺席时不要从 `message` 编造原因；排障时保留本次返回的 `meta.requestId`（如有）。

下表只用于人工排查，不是稳定机器契约：

| 日志中的原始诊断（可获得时） | 含义与修正 |
| --- | --- |
| `i2i requires at least one image, subject, or resource reference` | 缺少真实 I2I 素材。只有 Text 上下文时用 `t2i`，或补充合适的图片素材。 |
| `text canvas reference must not appear in the prompt; pass it through the reference list only` | 删除正文里的 Text 占位符，把 Text 留在 `--ref`；其余输入仍须符合所选 mode。 |
| `t2i accepts only Text canvas references` | T2I 输入包含非 Text 素材；需要这些素材时应选择 `i2i`。 |

服务端先校验公开引用身份的格式，再解析节点真实类型，并在保存期校验 mode/素材及正文引用位置。
不能因为服务端返回错误，就判定是节点类型白名单拒绝 Text，或认为生成已经派发。

未加 `--run` 时，`ok=true`、保存后的 prompt parts 和 upstream 连线只证明保存成功，不证明
媒体生成成功；用户要求生成时，还需单独验证运行和 Resource 终态。

## 图片与视频生成配置编辑

`node create|edit image|video` 一旦提供任一 generation 参数，就必须显式传入非空 `--mode`：
包括 `mode`、`prompt`、`model`、`ratio`、`resolution`、`count`、`ref`，以及视频的 `duration`。
没有默认模式，edit 也不继承已保存节点的模式。缺失或空 mode 会在本地以
`error.code=2`、具体 `diagnostics` 原因和退出码 2 拒绝。

Generation 是完整替换，不是字段级 patch。需要保留原 prompt 或引用时，先读回保存的
`generation`，再提交包含 mode 与目标 prompt 的完整输入。模型规格允许时，图片/视频草稿可保存空正文；
保存成功不证明已经可以运行。服务端在 Run claim 和扣费之前校验投影后的生效正文。
空正文无法自动命名节点时，`create --run` 必须显式给标题。只改 title/tag、`--clear-tags`
或单独 `--clear-generation` 无需 mode。不能同时传 `--clear-generation` 和 generation 参数。
添加 `--run` 不改变上述输入规则。

## 音频模型与音色选择

命令参数、输出字段和分页示例见 [主 Skill 的“模型与音色发现”](../SKILL.md#模型与音色发现)。

按任务选择当前可用的方式。下表为参数片段；创建或编辑时补齐 `--project-id`、非空 `--prompt` 等必需输入。
所有音频固定单输出，不传 `--count`。

| 用途 | 生成参数 | 音色与参考素材 |
| --- | --- | --- |
| 音色配音，不指定模型 | `--mode tts --voice-name <voiceName>` | 从该入口的音色目录选择；不传 `--model`、`--scenario`、`--duration` 或 `--ref` |
| 无场景的指定模型配音 | `--mode tts --model <model> --voice-name <voiceName>` | 模型目录未声明场景时不传 `--scenario`；音色取自该模型目录 |
| 指定模型朗读 | `--mode tts --model <model> --scenario text-reading` | 必须从 `voice list --model <model>` 选择 `--voice-id` 或唯一的 `--voice-name`；不接受参考素材 |
| 全能配音 | `--mode tts --model <model> --scenario omni-dubbing` | 可选同模型目录中的一个 `--voice-id` 或唯一的 `--voice-name`，并按当前规格使用图片、音频或主体参考 |
| 音乐生成 | `--mode music --model <model> --duration <seconds>` | 从 `model list --type audio` 选择具有 `music` mode 的模型和允许的正数时长；不传音色、场景或引用 |

场景以 `model list --type audio` 返回的模型能力为准：模型有场景时必须显式选择；没有场景时不要传 `--scenario`。例如目录中的 `legacy_tts` 可直接指定模型、文本和对应音色。未知模型、错误场景或混用音色时修正输入，不自动更换模型或音色。`--dry-run` 不联网验证模型能力，执行前仍需查询目录。
优先使用查询返回的 `voiceId` 和 `--voice-id`；名称唯一时也可用 `--voice-name`，两者互斥。ID 须取自同模型目录，不使用执行配置中的 speaker ID。重名时查看标签并明确选择 ID，不自动选第一项。服务未返回 ID 时继续使用唯一名称，等待服务支持 ID 选择。选择音色不会播放音频，无需另行上传音色素材。保留选定音色以便复现创作决策。

全能配音保存示例，先替换为已查询确认的模型和音色：

```bash
dreamina-canvas node create audio \
  --project-id <projectId> --mode tts --model <model> \
  --scenario omni-dubbing --prompt "<配音内容>" \
  --voice-name "<voiceName>"
```

参考身份和正文占位符遵循本文件的[Prompt 引用](#prompt-引用)。音色作为音频参考，与普通音频共用
当前模型、场景的 `references.max` 和 audio 类型上限，也须遵守 `references.mutuallyExclusiveTypes`。
图片／音频互斥时，图片与音色也不能同时使用。以实时规格为准，不固定数量上限，不自动丢弃参考素材。

诊断明确指出素材约束冲突时，按[引用拒绝的诊断边界](#引用拒绝的诊断边界)定位冲突，调整参考或取消音色选择，
再提交完整生成配置。执行结果不确定时，先按[恢复与幂等](recovery-and-idempotency.md)查询原操作，不能换新 submit ID 重提。
上述示例只保存节点；需要生成时按[积分确认](credits-and-hitl.md)取得批准并运行，保存成功不代表音频已生成。

编辑前用 `node show` 读取当前 `generation`，保留所需的模型、场景、音色、正文及引用顺序，再完整重建生成配置。
单个未在正文引用的目录音色读回为 `voiceId` 和 `voiceName`。响应明确阻止写回时（例如 Web 多音色或正文引用音色），
保留原草稿并在 Web 编辑，不用替换或清空生成配置绕过限制；只修改标题、标签时保留原生成配置。

## 需要保存的状态

可恢复创作任务应保存：

- 画布/项目身份；
- 稳定业务键到 Node ID 的映射；
- 每次运行的 submit ID 和 operation reference；
- 选中的终态 Resource ID；
- 下游关系是跟随 Node 还是冻结 Resource。

不得持久化未公开内部标识、signed URL、provider task payload 或短期确认材料。

## 跨项目资源输入

Resource 尚未关联目标项目时，在 node create/edit 命令上添加 `--resource-source <resourceId>@<sourceProjectId>`。每个需要建联的资源各声明一次；同一资源重复使用只需一份声明，一次保存可涉及多个来源项目。原有 `--ref res:<resourceId>`、`{{res:<resourceId>}}`、导入 `--resource-id`、Element 绑定及 timeline 片段仍使用纯 ID。只声明来源不会把素材挂到节点；来源冲突或声明了本次未赋值的资源会被拒绝。Node ID、text 节点以及读取/上传命令不接受这个参数。

保存前会先准备目标关联，`--run` 随后才沿用报价、批准、运行流程；保存后的节点仍只含普通 Resource ID。`--dry-run` 只校验本地写法，不判权、不建联。保存结果不确定时，按[恢复与幂等](recovery-and-idempotency.md)处理。
