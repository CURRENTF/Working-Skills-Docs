# Research Code Rules

## AI 模型训练与推理

- 跑模型训练或推理时，先用小样本验证 batch 推理正确性：至少检查 `bs=1` 和 `bs>1` 的输出或关键指标是否几乎一致。
- 一致性验证通过后，在显存允许范围内使用较大的 batch size，提高 GPU 利用率；不要长期用 `bs=1` 跑大规模推理浪费时间。
- 做吞吐、延迟、GPU 利用率或功耗 benchmark 前，必须先确认实际命令使用的是目标性能 backend，例如 attention implementation、量化模式、batch size、可见 GPU、profiler/debug flag 和 CPU 预处理策略。不要把为了稳定对齐分数临时使用的保守 baseline，例如 `sdpa`、eager attention、`bs=1` 或在线 CPU 抽帧，直接沿用到性能 benchmark。
- 大规模 benchmark 前，先用小样本对目标 backend 和 batch size 做 sanity 对比；只有输出或关键指标对齐后，才用最快且正确的配置跑全量。
- 如果 GPU 利用率或吞吐明显不合理，先检查实际命令、解析后的 config 和运行日志，再判断是不是模型或方法本身的问题。
- 记录最终使用的 batch size、样本数、模型、数据 split、seed、attention backend、可见 GPU 和关键推理参数，保证结果可复现。
