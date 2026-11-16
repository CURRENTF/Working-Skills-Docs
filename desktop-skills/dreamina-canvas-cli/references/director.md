# 导演台

## 可用范围

导演台由服务端按区域开放。命令返回服务码 `20078` 时，表示服务端尚未在当前区域开放导演台，未读取或修改任何内容：告知用户所在区域暂未开放导演台，不要重试或绕过。其他画布命令不受影响。

导演台与其他 CLI 命令使用同一份使用资格，只操作本地文件的命令也需要登录并联网。返回 `vip_membership_required` 时，告知用户需要有效的个人会员或付费团队成员身份，未读取或修改任何内容；不要重试，也不要改用其他方式离线创作或渲染。

## 画布交付要求

用户要求在画布创建或修改导演台时，交付目标是该画布中的可编辑导演台。优先使用带 `--project-id` 和 `--node-id` 的命令，目标采用用户指定的画布或已选定的项目；两者都不明确时，先确定目标再写入。

允许用本地文件搭景和预览。最终本地修改后执行 `director push --file scene.json --project-id <uuid>`，再用 `director show --project-id <uuid> --node-id <id>` 读取已保存导演台。之后每次本地修改都须再次 push 才能完成画布交付。本地 MP4 或本地预分配的 `nodeId` 不能证明导演台已保存。

报告完成前，检查保存回执中的目标 `projectId`、非空 `versionId` 和大于零的 `savedDraftVersion`。使用同一账号、profile、区域、环境和项目从画布读回节点，核对保存版本及最终场景/关键帧。向用户交付画布链接和导演台节点 ID；画布链接使用 create、apply、push、show（或 canvas 命令）返回的 `webUrl`，不自行拼接。

保存或读回失败时，保留工作文件和返回的 `operationRef`，明确报告画布交付尚未完成，并按下文恢复流程处理。不要静默改成本地视频交付，也不要另建导演台绕过失败。导出的图片/视频是否也要上传到画布，按用户要求决定；媒体节点不能代替可编辑导演台的保存。

## 发现与创作

完整 `schema` 只把 `director` 列为一项并给出 `detailCommand`；执行 `schema director` 查看其子命令。再查看 `director catalog --kind builtin`，仅使用返回的几何体、预设 ID 和命令；`commandFields` 按命令类型列出每个字段的类型、是否必填、可选值和结构说明，使用没有示例的命令前先查它；其中 `rendering.available` 表示本机能否预览或渲染。创建、读取、编辑、校验、目录和 FBX 操作由安装的 CLI 执行，无需 Chrome、Node 或源码。预览、截图/视频渲染和动画定格需要本机 Chrome/Chromium 或 Edge 及可用的 WebGL；MP4 还需浏览器 H.264 编码能力。这些命令不使用服务端渲染，也不需要打开画布页面。

用 `director create --project-id <uuid> --title "Scene"` 创建真实可编辑的画布导演台。用 `director show --project-id <uuid> --node-id <id>` 查看；用 `director apply --project-id <uuid> --node-id <id> --input commands.json` 应用有序 JSON 命令数组。每次直接修改先读取当前版本，再比较版本保存，不会静默覆盖并发编辑。

`director create` 总是先在画布上创建导演台。加 `--file scene.json` 会另存一份绑定该节点的新工作文件；之后可用 `director show --file scene.json`、`director apply --file scene.json --input commands.json` 修改，本地修改须 push 才会发布。整批失败时文件保持原样。

命令覆盖对象、组合、相机、环境、姿势、动作、属性关键帧和分镜。`workspace.performance` 从摆拍创建/替换动画工作区，只有确实需要时才使用。每次直接读取画布默认进入摆拍；编辑既有动画时，命令数组第一项使用 `workspace.select`。预设是固定目录项。单位为米、XYZ 欧拉角度；时间线使用当前显示帧率下的整数帧。

物体运动和相机运镜优先使用默认的 `linear` 插值。新建 `camera.keyframe` / `keyframe.set` 关键帧默认使用 `linear`。编辑已有关键帧且省略 `interpolation` 时会保留原曲线，要切换为线性须显式传 `interpolation: "linear"`。

用关键帧的时间间隔和数值变化表达速度。同样的时间间隔内，位移逐渐增大表示加速，逐渐减小表示减速，保持相同表示匀速。例如向上加速时，可在第 0、6、12、18、24 帧将 `position.y` 依次设为 0、0.1、0.4、0.9、1.6 米，全部使用 `linear`。相机的位置和目标点也按这一方法安排。需要更细腻的变速或转弯时，在变化明显处补充关键帧，再连续播放检查衔接，按效果决定密度。

只在确实需要停顿、起步或收尾缓动时选择 `smooth`。未指定切线的 `smooth` 会在每段两端缓入缓出，连续运动逐段使用会产生反复减速、再起步的顿挫。线性插值也需合理安排路径点和时间，关键帧太稀或相邻段速度、方向变化太大会出现突变。

```json
[
  {"type":"object.primitive","primitive":"cube","id":"prop","name":"Prop"},
  {"type":"workspace.performance","copyStaging":true},
  {"type":"timeline.set","durationFrames":60},
  {"type":"keyframe.set","id":"prop","channel":"rotation.y","frame":0,"value":0},
  {"type":"keyframe.set","id":"prop","channel":"rotation.y","frame":60,"value":180}
]
```

官方素材通过 `director catalog --kind character|motion` 查询，`hasMore` 为真时沿 `nextOffset` 继续翻页。引用仅含稳定 ID，不写签名 URL。本地动作库独立于画布正文，跨设备渲染时保留工作文件。不支持的本地媒体会明确失败。

角色沿位置关键帧行走或跑步时，先用 `director catalog --kind motion --motion-usage path-traversal` 查找路径动作；该查询会遍历完整目录，`offset/count` 针对匹配结果分页。普通表演动作使用 `direct`，不要仅凭名称含“走路”就拿来配路径，也不要把普通动作手动标成路径动作。`motion.add` 会从所选官方目录项补齐用途和步幅；省略 `motionName` 时，Web 按当前语言显示目录名称，仅需自定义名称时才填写该字段。路径动作使用原地步态，并按路径距离推进；设置 `loop: true`，动作片段覆盖走位时间，角色按需开启 `pathFacingEnabled`。检查起步、转弯、停步和动作切换的连续播放，静帧不能证明没有滑步。

## 放置物体与管理组合

坐标单位为米，Y 向上。移动已有物体前，用 `director show` 读取其 `placementAnchor`、可选 `pivotOffset` 和完整 `transform`。通过 `object.primitive` 或 `object.preset` 创建的物体使用 `bottom-center-v1`，局部原点位于模型包围盒的底部中心。物体保持直立、缩放为正数、使用默认锚点，且承载面为世界高度 H 的水平面时，把 `transform.position.y` 设为 H。地面高度为 0，桌面高度为 0.8 米时设 Y = 0.8，无需再加物体自身半高。X、Z 应落在承载面范围内。

`object.set` 会整体替换传入的顶层字段。修改位置时，从 `show` 复制完整 `transform`，修改目标坐标，并一起传回 position、rotation 和 scale。下面的示例创建一个直立物体，将底部放到 0.8 米高处，前提是该高度已有承载面。

```json
[
  {"type":"object.primitive","primitive":"cube","id":"tabletop-prop","name":"桌面物体"},
  {"type":"object.set","id":"tabletop-prop","patch":{"transform":{"position":{"x":0,"y":0.8,"z":0},"rotation":{"x":0,"y":0,"z":0},"scale":{"x":0.2,"y":0.2,"z":0.2}}}}
]
```

`object.ground` 接收 `ids`，将符合条件、未锁定且使用 `bottom-center-v1` 的模型 Y 设为 0。其他物体可能保持原位，执行后应读回确认。放到另一物体上时，先确定承载面的世界高度，再用 `object.set` 放置。`placementAnchor` 缺失或取其他值、物体倾斜或倒置、动画姿势以及斜面场景，都需要检查实际包围盒和接触位置。通过预览检查悬空、穿插和超出承载面的情况，调整后再次查看。

用 `group.create` 的 `id`、`name` 和至少两个成员 `ids` 保存选择组合。成员各自保留变换和动画轨道，移动时对成员物体 ID 操作。

## 合并零件后统一制作动画

多个零件需要一起运动时，用 `object.merge` 传入成员 `ids`、新对象 `id` 和 `name`，至少需要两个不同物体。合并保留世界位置，新对象原点位于整体底部中心。原成员成为私有组件，后续变换和关键帧使用新 ID。合并在安装的 CLI 中执行，无需浏览器。

支持基础几何体、内置道具，以及仅包含这些来源的合并对象。成员须可见、未锁定、无骨骼，且没有动作片段和属性关键帧。导入模型或其他不支持的成员会让整批 apply 失败并保留原内容。先搭建并合并零件，再添加动画。编辑既有动画工作区时，先选择工作区并读取当前物体。

```json
[
  {"type":"object.primitive","primitive":"cube","id":"body"},
  {"type":"object.primitive","primitive":"sphere","id":"detail"},
  {"type":"object.set","id":"detail","patch":{"transform":{"position":{"x":1,"y":1,"z":0},"rotation":{"x":0,"y":0,"z":0},"scale":{"x":0.2,"y":0.2,"z":0.2}}}},
  {"type":"object.merge","ids":["body","detail"],"id":"assembly","name":"整体物体"},
  {"type":"workspace.performance","copyStaging":true},
  {"type":"keyframe.set","id":"assembly","channel":"rotation.y","frame":0,"value":0},
  {"type":"keyframe.set","id":"assembly","channel":"rotation.y","frame":30,"value":90}
]
```

上例为整体物体创建动画工作区。通过 `show` 读回新对象和轨道，再预览运动，检查整个物体的运动和旋转中心。

## 制作动画前设置自定义锚点

用 `object.pivot` 的 `id` 和 `offset: {x,y,z}` 设置相对物体原放置策略原点的局部米制偏移。底部中心锚点物体设置 `{x:0,y:1,z:0}`，表示锚点向上移动一个局部米。重复设置同一偏移不会累加，`{x:0,y:0,z:0}` 恢复原放置策略的原点。

命令自动补偿位置，已有旋转和非均匀缩放下也保持物体画面位置。后续旋转和缩放围绕新锚点进行，`transform.position` 表示该锚点的世界坐标。对于直立的底部中心锚点物体，放到水平面时，Y 应设为承载面高度加 `pivotOffset.y * transform.scale.y`，放到地面可使用 `object.ground`。

先设置锚点，再添加动画。目标须为可见、未锁定、无骨骼且没有动作片段或属性关键帧的模型，包含符合条件的合并对象。命令被拒绝时整批 apply 回滚。通过 `show` 核对偏移与补偿后坐标，再预览运动。

```json
[
  {"type":"object.primitive","primitive":"cube","id":"door","name":"门板"},
  {"type":"object.pivot","id":"door","offset":{"x":-0.5,"y":0,"z":0}},
  {"type":"workspace.performance","copyStaging":true},
  {"type":"keyframe.set","id":"door","channel":"rotation.y","frame":0,"value":0},
  {"type":"keyframe.set","id":"door","channel":"rotation.y","frame":30,"value":90}
]
```

自定义锚点需要配套的画布读者和后端版本。旧画布版本会拒绝读取此类场景，请使用兼容版本查看和编辑。

## 查看效果与迭代

初步搭景后、每次重要场景/相机修改后，执行 `director preview --project-id <uuid> --node-id <id> --workspace performance --storyboard --frame 30`，或 `director preview --file scene.json --camera-id scene-camera`。`--camera-id` 与 `--storyboard` 二选一。省略 `--output` 会自动生成新的 PNG。必须用自己的看图工具打开返回的绝对 `path`，JSON 成功不等于已经目视检查。

结果包含 `source.nodeId`、基线 `source.versionId`、`source.contentSha256` 和渲染 `options`。本地修改可能不同于基线版本，摘要包含实际正文、动作库与会话。`--workspace staging|performance` 仅选择本次渲染工作区。预览不修改画布。

检查构图、尺度、遮挡、空间关系、人物走位和相机方向。每个镜头至少查看起/中/末帧，以及切镜两侧。用少量类型化命令修正，再预览并查看新图。静帧不足以判断运镜连续性时导出短视频。反解参考视频时用简易人体或预设角色，优先还原抽象布景、走位和运镜；外观细节及人物动作服从视频生成参考素材的目标。

没有浏览器/渲染条件时继续数据创作，明确尚未完成视觉检查。此时预览、截图/视频导出和定格会返回 `error.code=40022`。错误含 `canvasHandoff` 时，把 `canvasHandoff.webUrl` 和 `canvasHandoff.nodeId` 交给用户，请用户在画布中打开该导演台，自行导出截图或视频（或定格该帧）。画布显示的是最近一次 push 的版本，本地修改须先 push。没有 `canvasHandoff` 说明工作文件尚未保存到画布，先 push 再重试以取得链接。用户确认前不得声称已经导出。没有看图能力时把路径交给有能力的用户/Agent，不得声称已经看过。缺少渲染条件不会阻断数据编辑，也不会创建空画布节点。

## 同步与恢复

用 `director push --file scene.json --project-id <uuid>` 发布本地导演台。push 保留画布上的节点名称，只有用 `document.title` 改过标题时才改名。`director pull --file fresh.json --project-id <uuid> --node-id <id>` 读取到新文件。发布时工作文件绑定账号、profile、区域、环境和项目。internal 生产写入仍被禁止，public 写入仍由服务端授权裁决。

直接 create/apply 返回 `file`（自动管理；create 传了 `--file` 时为该路径）。直接写入失败且返回 `operationRef` 时，用 `director push --file <operationRef>` 恢复，不要重复 create/apply 生成新写入。push 中断后原样重复 push。保留 `pending`、`writeId`、`updateId` 和正文。冲突（`error.code=7`）同时带有 `directorConflict` 时，说明画布版本已变化：把 `directorConflict.latestVersionId` 对应的最新版本 pull 到另一文件，再重放有意保留的修改。只有用户明确要求用本文件覆盖时才用 `push --force`，并把回执中的 `overwrittenVersionId` 告诉用户。文件旁的 `.lock` 在命令退出（含被中断）时自动释放，不要删除；`error.code=40020` 表示仍有命令在使用该文件。

## 导出与交付

本地交付：`director export --file scene.json --type image --output shot.png`，或 `--type video --workspace performance --output film.mp4`。可以用 `--project-id <uuid> --node-id <id>` 替代 `--file`。`--frame` 选择截图帧，`--long-edge` 为 1280 或 1920。输出必须是新路径。结果包含大小、SHA-256、来源和参数。

画布交付：`director export --project-id <uuid> --node-id <id> --workspace performance --type video --storyboard --to-canvas`。PNG 使用 `--type image` 和目标帧。`--to-canvas` 自动管理文件，不要传 `--output`。它在本地渲染、复用媒体上传链路、登记资源并创建真实图片/视频节点。核对 `canvas.nodeId`、`canvas.resourceId`、`canvas.savedDraftVersion`，再用 `node show` 检查保存结果。原导演台保持可编辑。工作文件有未 push 的修改时，`--file` 导出到画布返回 `error.code=7` 和来源尚未保存的原因，先 push 再导出。

交付失败时，用返回的引用执行 `director resume-export --operation-ref <path>`，不要重新发起 export。恢复冻结来源、参数、产物与资源/节点身份，接续已完成阶段，成功后重复恢复返回同一回执。账号/环境变化或产物被修改会被拒绝。不要传播恢复文件中的私有存储句柄。导演台恢复路径不能当作生成任务 ID 交给 `operation status/wait`。

错误指出原区域不可验证（`code=40003`）时，表示无法确认工作文件或导出记录的原区域，即使其中已有完成回执也一样。停止自动恢复并保留原文件，不要修改其中的区域字段。先在原画布核对已有结果，用 `node find` 检索节点；已有节点 ID 时用 `node show` 检查，再决定后续处理。不要自动重复保存或导出。

## 动作文件与动画定格

`director freeze --file scene.json --frame 30` 把求值后的动画帧复制到摆拍，需要渲染器。用 `motion.import`（`id,file`）导入动作 JSON，或 `motion.import-fbx`（`id,name,contentBase64`）导入 FBX。用 `director export --file scene.json --type fbx --motion-id <id> --output motion.fbx` 导出，不需要浏览器。FBX 内容是动画，不能作为图片/视频节点回画布。
