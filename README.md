# Cybernetic Project Control (CPC)

[![CI](https://github.com/Trojon99/cybernetic-project-control/actions/workflows/check.yml/badge.svg)](https://github.com/Trojon99/cybernetic-project-control/actions/workflows/check.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status: alpha](https://img.shields.io/badge/status-alpha-orange.svg)](reports/STATUS.md)
[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-compatible-blue.svg)](https://agentskills.io/)

**Teach AI agents to manage long-running research and engineering projects — not merely remember them.**

[中文](README.zh-CN.md) · [Quick start](docs/quickstart.en.md) · [Agent Skill](skills/cybernetic-project-control/SKILL.md) · [Design](docs/design.md) · [Theory traceability](theory/traceability.md) · [Evaluation](evals/PROTOCOL.md) · [Current status](reports/STATUS.md)

Cybernetic Project Control is a **portable, Git-native Agent Skill and project-control framework** for evidence-grounded, human-supervised management of long-running projects. It helps a general-purpose agent recover project state, diagnose the real bottleneck, choose a bounded next action, account for delayed feedback and coupled dependencies, evaluate what actually happened, and replan without silently changing the human-approved objective.

CPC is inspired by **Engineering Cybernetics (工程控制论)**, especially the use of state, observation, feedback, performance criteria, coordination, delay, filtering, adaptation and large-system thinking. The project turns those ideas into operational rules for modern AI agents. It does **not** claim that Qian Xuesen (钱学森) and Song Jian (宋健) designed an AI-agent project-management framework; that translation is CPC's modern interpretation and must be evaluated on its own merits.

> **Project memory answers:** “What happened?”  
> **Project control asks:** “Given the evidence, what should we do next — and why?”

## Why CPC exists

Long-running AI-assisted projects often fail in ways that ordinary task lists or chat memory do not solve:

- an agent resumes after days or weeks but optimizes the wrong next step;
- many tasks are “done” while the critical project uncertainty is unchanged;
- delayed feedback is mistaken for failure, causing duplicate work or oscillating plans;
- local progress hides a coupled interface, dependency or long-lead risk;
- executors over-interpret their own outputs and silently promote tentative evidence into project truth;
- a new agent can recover history but still needs a human to micro-manage every next move.

CPC focuses on the missing **project-control judgment layer**.

## What the skill teaches an agent

CPC uses a closed-loop project-management cycle:

```text
Recover objective and evidence
          ↓
Observe / estimate current state
          ↓
Diagnose the critical gap or risk
          ↓
Choose one bounded action
          ↓
Predict feedback and stopping conditions
          ↓
Execute / delegate / wait / escalate
          ↓
Inspect real outputs and evidence
          ↓
Update the project model and replan
          ↺
```

The agent learns to distinguish:

- **task completion** from **project progress**;
- **observed facts** from **state estimates** and assumptions;
- **execution success** from **scientific or engineering validity**;
- **missing feedback** from **confirmed failure**;
- **local optimization** from **project-level bottlenecks**;
- **bounded autonomous action** from decisions that require human authority.

## Five management modes

For each meaningful next step, CPC asks the agent to choose among five modes:

| Mode | Meaning |
|---|---|
| `observe` | Measure, inspect, reproduce or gather information that can change a decision. |
| `act` | Execute, delegate, coordinate or locally replan within an approved scope. |
| `wait` | Do not duplicate intervention while relevant feedback is still maturing. |
| `escalate` | Ask a human to decide a goal, authority, major risk or value trade-off. |
| `stop` | Stop because the acceptance condition is met, the budget is exhausted, or no justified next action remains. |

## Research and engineering profiles

The core model is domain-neutral. Profiles add domain-specific checks without replacing specialist methods.

**Research projects** add questions about evidence quality, measurement, identification, competing explanations, negative results, reproducibility, model uncertainty and research drift.

**Engineering projects** add requirements, interfaces, verification, failure modes, long-lead dependencies, safety constraints and coupled subsystem risks.

Software and learning profiles are included as additional examples. CPC does not replace econometrics, experimental design, systems engineering standards, safety engineering or domain expertise.

## Quick start

### 1. Give an agent the skill

Copy the **entire** directory below into a skills-compatible agent host, or explicitly ask a file-capable agent to read it:

```text
skills/cybernetic-project-control/
├── SKILL.md
├── references/
├── assets/
└── scripts/
```

Do not copy only `SKILL.md`; the skill uses progressive disclosure and loads focused references when needed. The format follows the open [Agent Skills](https://agentskills.io/) convention.

### 2. Start in advisory mode

A simple prompt is enough:

> Read the Cybernetic Project Control skill and inspect this project in read-only mode. Reuse the existing project records. Tell me the verified current state, the critical gap, the best next action and why, the feedback you expect, and any decision that still requires me.

### 3. Authorize bounded execution

After reviewing the control card, approve a scope and budget. The agent may then execute low-risk actions within that boundary without asking you to micro-manage every step. Strategic goal changes, major unresolved-risk acceptance, destructive operations and public release remain human-gated by default.

See [Quick Start](docs/quickstart.en.md) and [integration guidance](integrations/README.md).

## Same agent, different agent, same project

CPC is designed so that project continuity does not depend on one model's chat memory. If the project already has an authoritative state system, CPC reuses it. If a project pauses for ten days, the same agent or a different agent can recover the project's evidence and current state, then apply the same control rules to decide where to continue.

CPC itself is **not** a memory database, scheduler, message bus or multi-agent runtime. It can sit above existing tools such as Git, project-state files, issue trackers or long-horizon agent runtimes.

## Interoperability and existing systems

CPC intentionally avoids rebuilding infrastructure that already exists. Integration notes currently cover:

- generic file-reading agents;
- Hermes;
- Codex;
- Evo / local-model workflows;
- LoopX;
- existing project-state backends.

These are **guidance-only** until an integration has been exercised against a recorded host/version. See [integration status](reports/STATUS.md).

## Evaluation: the contribution must be measurable

CPC does not claim that “cybernetics” automatically makes an agent a better manager. The repository includes public behavioral cases and an evaluation protocol intended to test the incremental effect of the skill.

Recommended comparisons use the same model, tools and budget across:

1. no project-management skill;
2. project memory only;
3. a matched generic project-management baseline;
4. CPC.

Target behaviors include:

- project-state recovery;
- bottleneck detection;
- evidence grounding;
- prioritization quality;
- delayed-feedback handling;
- drift detection;
- redundant-work avoidance;
- replanning after contradictory evidence;
- human-gate compliance;
- cross-agent handoff quality.

The current release contains **engineering tests and synthetic development cases**, not a published cross-agent efficacy result. See [evaluation protocol](evals/PROTOCOL.md) and [status](reports/STATUS.md).

## Repository layout

```text
.
├── AGENTS.md                         # instructions for agents contributing to this repo
├── skills/cybernetic-project-control # self-contained installable Agent Skill
├── theory/                           # source boundaries and theory → rule → test traceability
├── docs/                             # design, scope, standards, roadmap and related work
├── integrations/                     # host/backend integration guidance
├── examples/                         # synthetic research / engineering / software projects
├── evals/                            # behavioral cases, baselines and scoring protocol
├── tests/                            # deterministic engineering tests
├── tools/                            # offline validation and packaging utilities
└── reports/                          # verification status and design review
```

## Local engineering checks

Python 3.11+ is recommended. Optional validators use `jsonschema` and `PyYAML`.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
python tools/check_repository.py
python tools/demo.py
```

The optional utilities do not call a model, connect to a remote service, execute commands embedded in project records, or publish repositories. Passing these tests proves repository consistency — **not** scientific validity, authorization, or agent-management effectiveness.

## Theory lineage and source boundaries

CPC's primary theoretical reference is Qian Xuesen and Song Jian, *Engineering Cybernetics (Revised Edition)*, Science Press, 1983 (钱学森、宋健《工程控制论（修订版）》). The repository does not redistribute the book or its scan.

CPC separates three layers:

1. **source concepts** from the book;
2. **modern control / systems interpretation**;
3. **CPC's project-management design choices**.

See [source audit](theory/source-audit.md), [book map](theory/book-map.md), and [traceability](theory/traceability.md).

## Related work and non-goals

Existing work already covers substantial parts of long-horizon agent planning, project state, handoff and control. CPC does not claim to be the first “agent project manager” or the first application of cybernetics to agents. Its narrower contribution hypothesis is a **portable project-control judgment skill** that combines evidence-grounded state estimation, delayed feedback, coupling, bounded action, model revision and human authority across research and engineering projects.

See [Related Work](docs/related-work.md).

CPC deliberately does **not** build a new:

- LLM or agent runtime;
- scheduler or durable task queue;
- vector database or project-memory service;
- MCP or A2A replacement;
- multi-agent message bus;
- IDE or dashboard.

## Project status

Current version: **0.1.0-alpha.1**.

This is an experimental research prototype. The repository contains a self-contained skill, offline validation utilities, synthetic examples, public evaluation cases and CI. Cross-host / cross-agent management improvements have not yet been demonstrated. See [Status](reports/STATUS.md) and [Roadmap](docs/roadmap.md).

## Contributing

Contributions are welcome, especially:

- reproducible failure cases;
- adversarial or negative examples;
- research and engineering project trajectories;
- evaluations against strong baselines;
- integration reports with exact host/model versions;
- corrections to theory/source traceability.

Please read [CONTRIBUTING.md](CONTRIBUTING.md) and the [Code of Conduct](CODE_OF_CONDUCT.md).

## Citation

If CPC is useful in research, please cite the repository using [`CITATION.cff`](CITATION.cff). GitHub can render the citation in APA and BibTeX formats.

## License

Original CPC code and documentation are released under the [MIT License](LICENSE). The cited book and external projects retain their own copyrights and licenses; see [NOTICE.md](NOTICE.md).

## Related concepts / search terms

AI agent project management · agentic project management · Agent Skills · long-running agents · research project management · engineering project management · project control · project continuity · project state · evidence-grounded planning · human-in-the-loop AI · multi-agent coordination · cybernetics · Engineering Cybernetics · 工程控制论 · AI 智能体 · 科研项目管理 · 工程项目管理
