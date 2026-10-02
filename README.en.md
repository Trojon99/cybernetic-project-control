# Cybernetic Project Control

**Teach an agent to manage a project, not merely remember it.**

A portable Agent Skill for evidence-grounded, human-supervised management of long-running research and engineering projects. It guides observation, provisional state estimation, bounded action selection, feedback interpretation and replanning.

Version **0.1.0-alpha.1** is an executable research prototype. Cross-host effectiveness has **not** been demonstrated. Existing systems already implement substantial planning and control; novelty and benefit remain hypotheses to test.

## What ships

- A self-contained `skills/cybernetic-project-control/` package in the Agent Skills format.
- Concrete rules for insufficient observation, delayed effects, coupling, stale evidence, oscillating plans, budgets and human authority.
- Research, engineering, software and learning guidance loaded on demand.
- A small optional file-backed reference adapter, JSON Schemas and offline validation utilities.
- Synthetic examples, public behavioral development cases, an evaluation preparation/scoring utility, tests and CI.
- A source-to-mechanism-to-test mapping to Qian Xuesen and Song Jian's *Engineering Cybernetics*, revised edition, 1983.

## Start

Copy the **entire** skill directory into your agent host's documented skill location. Alternatively, explicitly ask a file-capable agent to read its `SKILL.md`. Begin in advisory mode, reuse existing project state and approve bounded execution separately. See [integration notes](integrations/README.md).

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
python tools/check_repository.py
python tools/demo.py
```

The optional tools never call a model, invoke shell commands from artifacts, contact a server, or push a repository. They check recorded structure and some consistency rules, **not scientific truth, human identity or actual host permissions**.

## Design in one paragraph

Use project evidence to maintain a provisional state estimate; identify which gap actually blocks the agreed outcome; compare feasible actions including measuring, waiting and stopping; choose one authorized bounded step; record predicted feedback before execution; review what actually happened; revise both project beliefs and the working model when warranted. Keep strategic goal changes with humans. Preserve existing state infrastructure rather than duplicating it.

This is an operational interpretation inspired by control theory, not a claim of a proven Lyapunov function, controllability, globally optimal policy or stability of arbitrary research projects.

[Main English README](README.md) · [中文](README.zh-CN.md) · [Design](docs/design.md) · [Traceability](theory/traceability.md) · [Evaluation protocol](evals/PROTOCOL.md) · [Status](reports/STATUS.md)
