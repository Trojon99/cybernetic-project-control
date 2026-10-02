# Architecture

Cybernetic Project Control is deliberately thin. The **project** is the controlled object; the Agent is a controller operating under human authority.

```text
Human objective / authority
          │
          ▼
Existing project state + evidence
          │
          ▼
  CPC project-control policy
Observe → Diagnose → Choose → Predict feedback
          │
          ▼
Agent / tools / workers execute bounded work
          │
          ▼
Logs · tests · tables · figures · documents
          │
          ▼
Evaluate real feedback
          │
          └──────────────→ update state / replan
```

## Four layers

### 1. Project state

Use the project's existing source of truth whenever possible: Git files, issues, lab records, LoopX, Project State Governor, APM, or another backend.

CPC does not require a second state database. The optional `.project-control/` JSON adapter exists only for projects with no durable state system and for reproducible examples/tests.

### 2. Project-control policy

The installable Skill implements the management judgment layer:

- recover objective and evidence;
- distinguish observation from inference;
- identify bottlenecks and coupled dependencies;
- choose one bounded next action;
- model delayed feedback;
- inspect real results;
- revise project beliefs and the working management model;
- stop or escalate when appropriate.

### 3. Execution

CPC does not execute work by itself. Hermes, Codex, Evo, Claude Code, local tools, CI, Stata, Python, physical test rigs, or humans may execute the chosen action if the host and user authorize it.

### 4. Human supervisory control

Humans retain authority over strategic goals, acceptance criteria, major risk acceptance, public release, destructive operations and other protected actions.

CPC is designed to reduce micro-management **inside an approved boundary**, not to replace scientific or engineering authority.

## Same Agent or different Agent

Continuity comes from durable project state, not chat memory.

```text
Day 1: Agent A reads project → acts → records evidence/state
                     │
                 project pauses
                     │
Day 10: Agent A or Agent B reads the same state
                     │
              CPC re-estimates context
                     │
              chooses the next action
```

A new Agent does not inherit the old Agent's private chain of thought or tool permissions. It inherits only the project records it can actually access, plus the CPC policy if installed/read.

## Core management modes

| Mode | Meaning |
|---|---|
| observe | obtain decision-relevant evidence |
| act | execute/delegate/coordinate within scope |
| wait | let pending feedback mature |
| escalate | ask a human to decide a protected trade-off |
| stop | finish because the objective/budget/decision boundary is reached |

These modes are management semantics, not a replacement for a runtime's own task lifecycle.

## Relationship to Engineering Cybernetics

CPC borrows a way of thinking about dynamic systems: state, observation, feedback, delay, coupling, performance criteria, adaptation and coordination.

The mapping is **operational and heuristic unless formal conditions are explicitly modeled**. CPC does not claim that arbitrary research projects have proven controllability, observability, optimality or Lyapunov stability.

See [source audit](../theory/source-audit.md) and [traceability](../theory/traceability.md).
