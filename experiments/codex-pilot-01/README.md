# Codex Pilot 0.1（协调者工具）

本目录准备 CPC 的首个受控评估，复用 `evals/run.py` 的 `public_packet` 与 `score`，不是第二套评分系统。**当前仅准备，实际受测运行数为 0。** 不可把本目录、源仓库或 manifest 给受测者。

## 冻结设计

使用 E02、E05、E07、E10、E17、E19、E24、E25，四个条件 A-control / B-memory / C-generic-pm / D-cpc，每个配对一个独立运行，共 32 个、每个只尝试一次。固定随机种子 20261003；随机顺序记录于协调者 manifest，编号 run-001 至 run-032 不包含条件。

A 无指导；B/C 原样复制现有 baseline；D 原样复制完整 CPC 包（排除解释器缓存）。每个 bundle 的 TASK、schema 和主提示词相同，同一案例的可见输入相同。按要求保留 public_packet 的案例 ID；不声称公开案例身份已隐藏。包自身名称/文风与长度可能使受测者推断条件，这是干预无法完全盲化的局限。不得隐藏不利回答或通过修改基线/答案来提高 CPC 分数。

默认共同预算：600 秒、40 次工具调用、4096 输出 token。模型/版本、推理配置、上下文预算、温度与模型 seed 均待真正执行平台冻结，不用伪造值填充；配置中 null 表示未知。启动前必须记录能落实的相同设置，保留所有超时、错误和人工介入。若平台不能落实预算，记录偏差，不能将其隐去。Pilot 的主提示词本身包含若干 CPC 相似原则，可能减少组间差异；按用户要求不改写它。

## 严格扫描的真实冲突

用户要求逐字保留的 subject-prompt.md 第 3 条含 `oracle`；完整 CPC 包 references/04-feedback-and-replan.md 也含 `eval oracle`。因此字面禁止任何 `oracle` 的规则会阻止 **全部 32 个 bundle**（共 40 处文件级命中）。当前保留两份原文，验证如实失败，`begin` 拒绝启动。没有擅自添加扫描豁免或修改 Skill。必须由实验所有者明确解决这个规格冲突后才能启动；不得把这些说明文字当作真的泄露了答案，也不得把失败写成通过。

扫描还核对精确文件清单、文件哈希、可见输入、两份 baseline 和完整包，拒绝符号链接、额外文件及评估路径。扫描不能证明 OS 沙箱、模型上下文隔离、外部网络禁用或训练数据未见过公开案例。

## 当前主机与隔离判定

Codex desktop 暴露 fresh task 和 fork/sub-agent 能力；这并不能强制每个受测任务只读一个 bundle。这里的工具/文件权限可访问源仓库、父目录和其他运行；协作者共享文件系统。fresh context 或独立目录本身不够。因此不调用受测子代理、不用协调者上下文模拟 A/B/C/D、不创建假 task ID。沙箱中 GitHub DNS 不通，获得批准的克隆成功，网络不能简单标为“完全禁用”。本地 manifest 记录真实源 SHA、Skill SHA-256、Python 和平台；不提交本地环境数据。

## 准备与验证

从仓库根运行 Python 3.11+（本轮使用本地 .venv 的 3.12）：

```bash
.venv/bin/python experiments/codex-pilot-01/prepare.py
.venv/bin/python experiments/codex-pilot-01/verify_blinding.py
.venv/bin/python experiments/codex-pilot-01/report.py
```

prepare 拒绝覆盖现有实验。manifest、bundles、轨迹未来阶段、原始结果与报告均忽略提交。report 生成包含全部 32 行的 reports/results.csv、summary.json、STATUS.md、blind-review/ 和协调者专用 review-map.json。当前严格验证预期退出 1；报告可以记录未执行状态，不能据此启动。重复 report 前将已有 blind-review 包移到独立存档位置，避免覆盖已审阅材料。

## 真正执行时的精确操作

1. 在**另外的隔离 Codex 执行平台**选定并冻结同一模型/版本、工具、系统指令、推理配置与预算。禁止自动挂载全局技能、memory、联网及其他项目。单独设置 OS 用户/容器或等价强制访问控制：每个 worker 的根仅含一个 bundle，无法读协调者树、父目录、源仓库、其他 worker 或结果。部署前用实际权限探测验证拒绝这些路径，并记录证据。只写本 worker 的 response.json；网络关闭。提示词限制不能代替这个控制。
2. 先解决严格扫描冲突，运行 verify 并要求退出 0。按 manifest 的 run 顺序逐个复制**仅** bundles/run-NNN 的内容到新 worker 根；不要复制 manifest、condition 目录、协调者代码或 Git 元数据。每次创建全新模型上下文；提交 bundle 内 subject-prompt.md 的逐字文本。一个任务只见一个案例/条件。此 harness 不提供假装可落实沙箱的自动启动器。
3. 平台真正启动后，将真实元数据写在协调者侧 begin.json：必须包含 model、host、start_time（ISO 时间）、task_id、workspace_id、isolation_evidence 与 budget；可包含 model_version、推理参数。用以下命令记账（这不是启动工具）：

```bash
.venv/bin/python experiments/codex-pilot-01/collect.py begin --run run-001 --metadata /coordinator/begin.json
```

4. 确认该任务终止后，收集**仅** response.json。end.json 可记录平台实际暴露的 end_time、elapsed_seconds、input_tokens、output_tokens、tool_calls、human_intervention 和 notes。未暴露项保留 null。失败/超时也必须调用 finish，不删行、不重试：

```bash
.venv/bin/python experiments/codex-pilot-01/collect.py finish --run run-001 --status completed --subject-stopped --response /isolated/run-001/response.json --metadata /coordinator/end.json
# 没有响应的失败：
.venv/bin/python experiments/codex-pilot-01/collect.py finish --run run-002 --status timeout --subject-stopped --metadata /coordinator/end-002.json
```

5. 所有 worker 停止并完成记账后运行 score.py / report.py。生命周期检查和协调者锁是合作式约束，不是进程沙箱；外部执行平台负责真实终止与隔离。score 永远不打开 subject workspace，只读已复制结果；running 状态阻止评分。来源哈希变化阻止评分，不更改 oracle。任何已尝试但缺失/非法响应的运行计失败；未执行的运行保留 NA。完成状态、契约指标和实际行为评分独立展示。

## 人工盲评与分析

只把 reports/blind-review/ 给两名独立评审；不要给 summary、results.csv、review-map 或 manifest。每个随机 review 编号附相同案例证据和原始响应，无条件或主机元数据。评审按现有 evals/rubric.md 的五项 0–2 打分，ratings-template.json 单列六类 hard failure，包含严重漏升级。保留分歧和裁决理由。原始 prose 若自行提及 CPC 会泄露身份，应记录盲评局限，不静默删改。

自动评分保留 behavioral_success = not_assessed；invalid schema 的选择检查计失败，无法解析的发明证据/违规行为保留 NA。明确引用不存在 ID 可标 hard_failure；自动 forbidden_action 是案例选择禁止项，不直接推断真实破坏性行为。summary 给所有组原始计数、已尝试分母、比例、逐案例所有组间配对差、失败列表及可用时间/token 差；资源均值显示有数据的样本数。未运行时不会填虚构的成功率或资源零值。人工评分模板供后续独立审查，不自动冒充人评结果。

## 四个轨迹环境（仅准备）

trajectory/ 是**协调者私有存储**，T1 科研校准撤回/部分恢复，T2 接口变化/过期延迟反馈，T3 两项小修复/验收/停止，T4 接力/记录版本变化。每个三阶段，输入明确标作确定性模拟材料；它们没有真的运行科研、设备或交付任务，也不提供新的 oracle。当前机制只模拟事件释放，不验证真正执行产物，不能据此声称 trajectory efficacy。

release_stage.py 一次复制一个阶段到源仓库和协调者目录之外的新路径；后续阶段只有 prior decision 保存、schema 与动作/证据检查通过且操作者确认 worker 停止后才能释放。旧 workspace 必须撤销读取权限，再给同一轨迹 worker 绑定新阶段根；不要让 worker 读取 trajectory/。阶段序号严格递增，决策在协调者存档。阶段 1 示例：

```bash
.venv/bin/python experiments/codex-pilot-01/release_stage.py --task T1 --stage 1 --target /private/tmp/cpc-T1-stage1
.venv/bin/python experiments/codex-pilot-01/release_stage.py --task T1 --stage 2 --target /private/tmp/cpc-T1-stage2 --prior /coordinator/T1/response.json --prior-subject-stopped
```

T4 stage 2 必须启动**新的 Agent B 上下文**；不得转发 A 聊天、response 或推理。--handoff 的 JSON 只允许 project_record 与 current_artifacts 两个字段；由协调者人工核对其内容确实只有持久项目记录与当前产物，结构校验无法证明自由文字没有泄漏聊天。例如 `{ "project_record": {"revision":"r1"}, "current_artifacts": [{"revision":"r2"}] }`。同样的记录后端应跨条件保持相同。阶段 3 可继续 Agent B。此命令不创建 worker，也不证明 OS 隔离；轨迹执行仍需独立平台。

## 证据边界

公开案例是开发 fixtures，非私有 held-out benchmark。Pilot 只能检查管道行为及机制信号；结果不证明通用 Agent 改善。静态选择题弱于真正轨迹任务；同模型结果不能证明跨模型可移植。CPC 可能增加 token/时间成本，基线文本长度未匹配；如无 tokenizer/usage 就保持 unknown。好结果不能靠无必要等待或过度请求人类判断。命令成功、哈希、JSON 和本仓库工程单测均不证明科学有效性或真实权限。

## 工程验证

```bash
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python tools/check_repository.py
.venv/bin/python tools/demo.py
```

新增测试覆盖 32 个配对包、基线/完整技能不变、确定性、opaque IDs、字段剥离、严格扫描冲突、注入文件、评分 running 防护、缺失响应保留、全部报告行、轨迹释放与接力边界。测试使用合成 lifecycle records，绝非受测 Agent 输出。
