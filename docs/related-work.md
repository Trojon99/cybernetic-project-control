# Related work：避免虚构差异

检索日期 2026-10-02。这里是对官方仓库 README / Skill / 文档的定点复核，不是穷尽的源码审计；没有运行外部项目。可变 `main` 未锁定 commit。详细链接见 `sources.json`。

| 项目 | 本次原始材料明确包含 | 与 CPC 的关系 |
|---|---|---|
| Agentic Project Management (APM) | Planner/Manager/Workers，规划、分工、审查、外置项目状态、handoff，软件开发场景 | 已是主动管理，不可称“只会记忆”；可作为管理基线/已有执行工作流 |
| LoopX | 持久目标、证据、gates、quota、peer claims、bounded continuation；还列出 Progress-Review Sentinel、Explore、Decision Context | 与 CPC 判断层有实质重叠；不能用“runtime 不做判断”排除它；适合选择相关能力做增量/消融比较 |
| Project State Governor | evidence-backed state、修复过时记录、保留 negative evidence、下一权威步骤 | 复用现有状态；同样会影响下一步，不是被动聊天存储 |
| Engineering Cybernetics Governance | 工程控制论启发的目的/观测/干预/质量指标；预期与实际反馈、耦合/时滞、适应、memory/skill 治理 | 理论和机制明显重叠；CPC 更聚焦外部项目，但聚焦不同不自动构成独创贡献 |

## CPC 的贡献假设

不是“首次控制论 + Agent”。待验证的贡献是：把来源、决策模式、反馈成熟条件、依赖协调和授权规则变成一个自包含能力包，并用跨领域、跨 host 的机制测试衡量增量效果。

“测量不足时先观察”“出现变化后重规划”等也不是新发明。新的组合是否有价值，要看：是否减少决策错误、重复工作和人工调度负担，且没有以拖延交付或昂贵文档负担换取。

## 复用原则

不复制这些仓库的实现或状态机，不宣称 MIT/Apache 等许可可统一替换。外部接入先建立只读映射，再记录实际版本，做读 → 提案 → 后端检查 → 写入 → 回读的端到端测试。未完成时标记 guidance_only。

本次新包没有引入上述项目作为必需依赖，没有捏造兼容徽章、star 数或优越性结论。前面讨论过但本次未核实的仓库不进入权威比较表。
