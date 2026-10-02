# LoopX contract sketch — guidance_only

来源 R2 的文档显示 LoopX 本身已有长期目标、证据、门槛、配额、bounded continuation，并覆盖部分进度审查与探索。不要将它描述成“不做判断”的数据库。

CPC 可作为可选管理策略，用于组织状态估计、候选比较、反馈分支和领域审查。LoopX 继续拥有任务状态、claims/leases、quota、gates 和写入权。

| CPC 逻辑对象 | 应复用的后端信息 |
|---|---|
| 目标和权限 | 当前 goal、scope、gate |
| 已知/未知与近期变化 | 当前 evidence、decision context、相关领域状态 |
| 待反馈 | 后端已有运行、监测或 continuation 信息 |
| 预算 | 后端 quota，而非再建本包计数器 |
| 行动结果 | 后端允许的 writeback 与回读 |

实施顺序：确认实际安装版本 → 只读提取 → 映射并保留原引用 → 生成控制建议 → 用后端原机制校验/写入 → 回读确认。

本版没有可运行 LoopX adapter，没有固定 CLI 参数，未做端到端测试。不要运行 CPC init 在其旁边创建第二个 state kernel。
