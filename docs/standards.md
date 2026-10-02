# 标准与非标准

| 层 | 选择 | 边界 |
|---|---|---|
| Skill 分发 | Agent Skills `SKILL.md`、frontmatter、references/assets/scripts | 核心包按已查阅规范组织；不是官方认证 |
| 仓库指令 | `AGENTS.md` | 本仓库入口管开发；应用到项目须合并自己的入口，不覆盖原规则 |
| 机器检查 | JSON Schema Draft 2020-12 | 只检查结构和声明的语义约束，不证明科学真理 |
| 状态与任务 | 优先复用现有系统 | 本包参考 JSON 是 0.1 测试 contract，不是新的行业标准 |
| 工具与跨 Agent 通信 | 使用宿主已有工具，未来按需要接 MCP/A2A | 本版没有实现，也不要求它们 |
| 溯源 | 保存本地产物路径/hash、运行来源和审查范围 | 不是完整 PROV/RO-Crate 实现；可日后导出，不冒称兼容 |
| 决策记录 | 采用 context/options/decision/consequences 的通用结构 | 不是把所有科研判断都当软件架构决策 |

规范来源记录在 `sources.json`。我们不依赖未经本次核对的 MCP/A2A 版本号或市场采用数量。
