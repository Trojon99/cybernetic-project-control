# Cybernetic Project Control（CPC）

[![CI](https://github.com/Trojon99/cybernetic-project-control/actions/workflows/check.yml/badge.svg)](https://github.com/Trojon99/cybernetic-project-control/actions/workflows/check.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status: alpha](https://img.shields.io/badge/status-alpha-orange.svg)](reports/STATUS.md)
[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-compatible-blue.svg)](https://agentskills.io/)

**教 AI Agent 管理长期科研和工程项目，而不只是记住项目。**

[English](README.md) · [快速开始](docs/quickstart.md) · [核心 Skill](skills/cybernetic-project-control/SKILL.md) · [设计](docs/design.md) · [理论追溯](theory/traceability.md) · [评测协议](evals/PROTOCOL.md) · [当前状态](reports/STATUS.md)

Cybernetic Project Control 是一个**可移植、Git-native 的 Agent Skill 与项目控制框架**。它让通用 Agent 能够恢复项目状态、判断真正瓶颈、选择有界的下一步、处理反馈时滞和系统耦合、检查真实结果，并在不擅自修改人类批准目标的前提下重新规划。

CPC 的方法论受到钱学森、宋健《工程控制论（修订版）》启发，重点吸收**状态、观测、反馈、质量指标、协调、时滞、过滤、自适应和大系统**等思想，再把它们转译为现代 AI Agent 可以执行的项目管理规则。我们不会把这种现代转译冒充成原书直接提出的 AI Agent 理论。

> **项目记忆回答：**“发生过什么？”  
> **项目控制回答：**“根据现在的证据，接下来最应该做什么，为什么？”

## 为什么需要 CPC

长期 AI 辅助项目经常出现这样的失败：

- 十天后 Agent 虽然恢复了历史，却不知道真正应该从哪里继续；
- 做完很多任务，但决定项目成败的关键不确定性没有减少；
- 把尚未成熟的反馈误判为失败，导致重复运行或来回改计划；
- 只看到局部模块完成率，没有看到接口、依赖和长提前期风险；
- 执行 Agent 把自己的运行结果直接升级成“项目事实”或“科学结论”；
- 换一个 Agent 后可以读懂历史，却仍需要人逐步告诉它下一步做什么。

CPC 专门解决这个缺少的 **project-control judgment（项目控制判断）层**。

## Agent 学到的核心循环

```text
恢复目标与证据
      ↓
观察 / 估计当前状态
      ↓
诊断关键缺口或风险
      ↓
选择一个有界行动
      ↓
预先约定反馈与停止条件
      ↓
执行 / 委派 / 等待 / 请求人决策
      ↓
检查真实输出与证据
      ↓
更新项目模型并重新规划
      ↺
```

它要求 Agent 区分：

- **任务完成** 与 **项目真正推进**；
- **已观察事实** 与 **暂定状态估计/假设**；
- **程序执行成功** 与 **科研/工程有效性**；
- **反馈还没回来** 与 **已经确认失败**；
- **局部优化** 与 **项目级瓶颈**；
- **有界自主执行** 与 **必须由人决定的事项**。

## 五种管理动作

| 模式 | 含义 |
|---|---|
| `observe` | 查证、测量、复现，获取真正能改变决策的信息。 |
| `act` | 在已授权范围内执行、委派、协调或局部重规划。 |
| `wait` | 关键反馈仍在成熟时不重复干预。 |
| `escalate` | 目标、权限、重大风险或价值取舍必须交给人。 |
| `stop` | 已达到验收条件、预算耗尽或不存在合理下一步。 |

## 科研与工程 Profile

核心模型保持通用，领域 profile 再加入专门检查。

**科研项目**重点检查证据质量、测量、识别、替代解释、负面结果、可复现性、模型不确定性和 research drift。

**工程项目**重点检查需求、接口、验证、失效模式、长提前期依赖、安全约束和子系统耦合风险。

软件与学习 profile 也作为额外示例提供。CPC 不替代 econometrics、实验设计、专业工程标准、安全规范或人的科学判断。

## 快速开始

### 1. 把完整 Skill 给 Agent

复制完整目录，而不是只复制 `SKILL.md`：

```text
skills/cybernetic-project-control/
├── SKILL.md
├── references/
├── assets/
└── scripts/
```

该结构遵循开放的 [Agent Skills](https://agentskills.io/) 形式，并使用 progressive disclosure：Agent 只在需要时加载具体 reference。

### 2. 先让 Agent 只读诊断

可以直接说：

> 读取 Cybernetic Project Control Skill，以只读方式检查这个项目。复用已有项目记录。告诉我已经核实的当前状态、关键缺口、最值得做的下一步及理由、预期反馈，以及仍需要我决定的事情。

### 3. 再批准有界执行

确认控制卡之后，一次性批准工作范围和预算。Agent 可以在范围内自主推进低风险动作，不需要你每一步都重新安排；核心目标变更、重大未解决风险接受、破坏性操作和公开发布等默认仍需 human gate。

参见 [快速开始](docs/quickstart.md) 与 [集成说明](integrations/README.md)。

## 同一个 Agent / 不同 Agent，都能接着做

CPC 的目标是让项目连续性不依赖某一个模型的聊天记忆。项目已经有权威状态系统时，CPC 直接复用。项目暂停十天以后，无论还是原来的 Agent，还是换成新的 Agent，都可以先恢复项目事实与证据，再按同一套控制规则判断从哪里继续。

CPC 自己**不是**项目记忆数据库、scheduler、消息总线或 multi-agent runtime。它可以工作在 Git、项目状态文件、Issue tracker、长期 Agent runtime 等已有基础设施之上。

## 不重复造轮子

CPC 不试图重做 Agent runtime、长期状态内核、消息协议或通用项目记忆。仓库提供 Generic Agent、Hermes、Codex、Evo、本地模型、LoopX 和已有项目状态系统的接入说明。

这些目前属于 **guidance-only**；只有真正以明确 host/version 做过端到端测试后才会标记为 verified。参见 [当前状态](reports/STATUS.md)。

## 贡献必须用评测证明

CPC 不会宣称“用了工程控制论，所以一定更好”。仓库包含公开行为案例和评测协议，用来比较：

1. 不加载项目管理 Skill；
2. 只有 project memory；
3. 篇幅匹配的通用 PM Skill；
4. CPC。

重点测试：状态恢复、瓶颈识别、证据依赖、优先级判断、反馈时滞、drift detection、避免重复工作、矛盾证据后的重规划、human gate、跨 Agent 接力。

当前版本有**工程测试和合成开发案例**，但还没有发布跨 Agent 管理能力提升数字。参见 [评测协议](evals/PROTOCOL.md) 和 [状态](reports/STATUS.md)。

## 仓库结构

```text
.
├── AGENTS.md                         # Agent 修改本仓库时的入口规则
├── skills/cybernetic-project-control # 可独立安装的 Skill
├── theory/                           # 原书边界与 theory → rule → test 追溯
├── docs/                             # 设计、范围、标准、路线图、相关工作
├── integrations/                     # 各 Agent / 后端接入说明
├── examples/                         # 科研、工程、软件合成案例
├── evals/                            # 行为案例、基线、评分协议
├── tests/                            # 确定性工程测试
├── tools/                            # 离线校验与打包工具
└── reports/                          # 验证状态和设计复核
```

## 本地检查

推荐 Python 3.11+；可选校验器依赖 `jsonschema` 和 `PyYAML`。

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
python tools/check_repository.py
python tools/demo.py
```

这些工具不会调用模型、联网、执行项目记录里的命令或替你发布仓库。测试通过只证明仓库内部工程一致性，**不证明科学有效性、真实授权或 Agent 管理能力提升**。

## 与《工程控制论》的关系

主要理论参考为钱学森、宋健《工程控制论（修订版）》，科学出版社，1983。本仓库不分发原书或扫描件。

CPC 严格区分：

1. **原书概念**；
2. **现代控制/系统解释**；
3. **CPC 自己的项目管理设计**。

参见 [来源审计](theory/source-audit.md)、[原书地图](theory/book-map.md) 和 [理论追溯](theory/traceability.md)。

## 与现有工作的区别

APM、LoopX、Project State Governor 以及已有控制论 Agent 项目已经覆盖了长期规划、项目状态、接力和控制中的大量机制。CPC 不宣称自己是第一个“AI 项目经理”，也不宣称第一次把控制论用于 Agent。

CPC 的待验证贡献更窄：**把 evidence-grounded state estimation、feedback delay、coupling、bounded action、model revision、human authority 组合成一个可移植的 project-control judgment skill，并同时服务科研与工程项目。**

参见 [相关工作](docs/related-work.md)。

## 当前状态

版本：**0.1.0-alpha.1**。

当前是实验性研究原型：已有自包含 Skill、离线校验工具、合成案例、公开 eval cases 和 CI；尚未证明跨 host / 跨 Agent 的管理效果。参见 [STATUS](reports/STATUS.md) 和 [Roadmap](docs/roadmap.md)。

## 贡献

欢迎贡献，尤其是：失败案例、反例、真实项目轨迹、强基线对照实验、明确 host/model 版本的集成报告，以及理论追溯纠错。

请阅读 [CONTRIBUTING.md](CONTRIBUTING.md) 与 [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)。

## 引用

科研使用时可通过 [`CITATION.cff`](CITATION.cff) 引用。GitHub 会自动生成 APA / BibTeX 格式。

## License

CPC 原创代码和文档采用 [MIT License](LICENSE)。引用书籍与外部项目保留各自版权与许可，详见 [NOTICE.md](NOTICE.md)。

## 相关概念 / 搜索关键词

AI Agent 项目管理 · 科研项目管理 · 工程项目管理 · Agent Skills · 长期 Agent · 项目连续性 · 项目状态 · evidence-grounded planning · human-in-the-loop AI · multi-agent coordination · cybernetics · Engineering Cybernetics · 工程控制论 · 钱学森 · 宋健 · research project management · engineering project management · agentic project management · project control
