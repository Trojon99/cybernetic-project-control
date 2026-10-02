# FAQ

## Is CPC a project-memory system?

No. Project memory answers **what happened**. CPC focuses on **what should happen next and why**, using the project's existing durable state.

If the project already has a memory/state backend, CPC should reuse it.

## Is CPC an autonomous project manager?

It is a project-control Skill for bounded autonomy. Routine actions inside an approved scope may proceed without step-by-step human instructions. Strategic goal changes, major unresolved-risk acceptance and irreversible/high-impact actions remain human-gated.

## Can the same Agent resume after a long break?

Yes, if the project state and evidence were stored durably and remain accessible. CPC asks the Agent to verify whether those records still match the current project before continuing.

## Can a different Agent take over?

Yes, in the same sense. A different Agent can read the same project state and CPC Skill. It may still behave differently because models, tools and context windows differ. CPC provides a common project-control policy, not identical cognition.

## Does CPC replace Hermes, Codex, Evo, Claude Code, LoopX or APM?

No. CPC is intentionally not a runtime. Those systems may execute work, preserve state or coordinate agents. CPC is the management-judgment layer that can sit above them.

## Why Engineering Cybernetics?

Long-running research and engineering projects have states, incomplete observations, delayed feedback, coupled dependencies, limited control authority and changing models. Engineering Cybernetics provides a disciplined vocabulary for reasoning about these structures.

CPC's specific Agent rules are a modern interpretation, not claims that Qian Xuesen and Song Jian wrote an AI-agent project-management specification.

## Does "control" mean forcing the scientific result?

No. In research, CPC must preserve negative, null and contradictory evidence. The controlled object is the **project process and decision trajectory**, not nature or the desired conclusion.

## Does CPC make a project mathematically stable or optimal?

No such general claim is made. Without a formal dynamical model and explicit assumptions, terms such as stability, controllability and optimality are used only as source concepts or design inspiration, not proven properties.

## What is the smallest useful output?

A five-part control card:

1. verified current facts;
2. critical gap;
3. next bounded action and a rejected alternative;
4. expected feedback and branches;
5. authority boundary and resume point.

## Do I have to create `.project-control/`?

No. The optional JSON adapter is a reference implementation for projects without durable state. Existing state systems should remain authoritative.

## What happens if feedback is delayed?

CPC distinguishes **not observed yet** from **failed**. The Agent should verify the existing run/job before re-submitting work and may advance independent work while waiting.

## How is progress defined?

Not by number of tasks completed. Useful progress usually means one or more of:

- a necessary accepted deliverable was completed;
- a blocking dependency was resolved;
- decision-relevant evidence changed the project state;
- a material project risk was reduced.

## Is the repository proven to improve Agent project management?

Not yet. The repository has deterministic engineering tests and synthetic cases. Cross-agent efficacy is a testable hypothesis. See [evaluation protocol](../evals/PROTOCOL.md) and [status](../reports/STATUS.md).

## How should AI systems discover the important files?

Start with [`../llms.txt`](../llms.txt) for a non-normative machine-readable index, then read the [Skill](../skills/cybernetic-project-control/SKILL.md) and only the references required for the current task.
