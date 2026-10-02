# Current status / 当前状态

Version: **0.1.0-alpha.1**

## Published

The source repository is now published at:

`https://github.com/Trojon99/cybernetic-project-control`

It contains the self-contained Agent Skill, theory/source boundaries, domain guidance, optional reference schemas/tools, synthetic examples, public development cases, deterministic engineering tests and CI configuration.

## Verified before publication

The local release build recorded **106 deterministic engineering tests passing**, plus repository/package checks and a synthetic offline demo. The exact pre-publication environment and limits are preserved in [build-verification.json](build-verification.json).

Those checks establish internal engineering consistency of the tested build. They do **not** establish scientific validity, real authorization, or improved project-management behavior.

## Not yet demonstrated

- no published controlled efficacy experiment on real Hermes, Codex, Evo or other agent hosts;
- no live Air↔Max SSH integration;
- no verified write adapter for LoopX / Project State Governor / APM;
- no private held-out benchmark result;
- no independent audit;
- no formal proof that arbitrary research or engineering projects are stable, controllable or optimal under CPC.

Integration documents are therefore **guidance-only** unless a later report names an exact host/model/version and records an end-to-end run.

## Next evidence gate

Freeze a skill revision and run paired evaluations against:
1. no PM skill;
2. project-memory-only;
3. a strong generic PM baseline;
4. CPC.

Measure decision quality, redundant work, delayed-feedback handling, coupling/interface errors, human-gate compliance, delivery cost and cross-agent handoff. Publish null or negative results as well as positive ones.

中文要点：代码已经公开，但“工程测试通过”与“Agent 学会更好地管理项目”是两回事。后者仍需真实对照实验。
