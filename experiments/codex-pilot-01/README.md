# Codex Pilot 0.1（协调者工具）

本目录复用 `evals/run.py` 的 public_packet/score，准备受控 CPC 评估。**真实模型运行为 0**，不自动启动任务；本目录、源仓库和协调者数据均不可提供给受测者。

## Pilot 0.1 execution status

Verified on 2026-10-03:

- Pilot 0.1 harness: **READY**
- 32 blinded exports: **PASS**
- Repository tests: **129 PASS**
- Real isolation probes: **0**
- Real scored runs: **0/32**
- Efficacy: **NOT ASSESSED**
- Real evaluation: **DEFERRED**

**Reason:** No verified subscription-included execution environment currently guarantees single-bundle filesystem isolation from the CPC source repository and other runs.

The subject-visible experiment is frozen at commit `b073cc8`. Passing deterministic tests and export validation establishes harness consistency, not CPC management efficacy. No API execution runner or separately billed OpenAI API / Agents API backend was added. Generated exports, coordinator metadata and private outputs remain local and excluded from Git.

## 冻结设计

案例仍为 E02、E05、E07、E10、E17、E19、E24、E25。A 无 PM 指导；B 原 memory-only baseline；C 原 strong generic-PM baseline；D 完整 CPC 包。8 × 4 = 32 个独立运行，每个只尝试一次；随机 seed 20261003，run-001 至 run-032 与之前顺序一致。案例、oracle、Skill、两份 baseline、schema、实验问题和 subject-prompt.md 均未修改。

默认共同预算 600 秒、40 tool calls、4096 输出 tokens。真实执行时冻结同一模型/版本、reasoning/tools/system instructions 与预算；平台未暴露的参数/用量保持 null。Skill 名称、内容/长度可能让受测者推断干预，不能宣称完全干预盲化；公开案例 ID 按 public_packet 保留。相同提示词内已有若干 CPC 相似原则，可能缩小组间差异，按要求不改写。

## 文件边界与新的验证规则

```text
coordinator/                 # 私有协调者树，忽略提交
  manifest.json              # opaque ID → case → condition，来源哈希
  bundles/run-NNN/           # 生成前审核材料，不整树发给 worker
  results/                   # 只接收终止后的真实 response.json
  reports/                   # CSV、paired summary、人工盲评
  trajectory/                # future stages，不能挂载给 worker
  export-manifest.json       # 每归档 SHA-256，解压验证结果
  export-checksums.sha256
subject-exports/             # 仅 32 个 opaque tar.gz，忽略提交
  run-001.tar.gz … run-032.tar.gz
```

A 仅 TASK.md、input.json、response.schema.json、subject-prompt.md。B/C 增加 condition/INSTRUCTIONS.md，字节和冻结 baseline SHA-256 完全一致。D 增加相同中性路径的 instruction（指向 Skill），以及完整 skills/cybernetic-project-control/；逐文件哈希与协调者记录的 frozen package manifest 相符，包含 references/assets/scripts/requirements/LICENSE，排除解释器缓存。不使用 A/B/C/D 标签作 subject 目录名。

**lexical occurrence != answer leakage**：普通 “do not search for the oracle” 及 Skill 方法警告不泄露答案。验证器递归解析 JSON，拒绝 oracle/acceptable_actions/forbidden_actions/human_review_note **键**（包括嵌套、Unicode 转义）；对文本拒绝显式序列化答案结构和 evaluator-only 路径，不禁止孤立的普通英文词。独立文件/目录 allowlist 和冻结 SHA-256 拒绝任何额外材料、prior response、其他 run、Git、scorer 或被篡改允许文件。不是仅列几个坏词。

每个 tar.gz 只含该 run 的允许文件，没有 outer run 目录、source path、ownership/timestamps、Git 或 mapping。每个归档在新的临时目录解压，用**同一验证器**重验；checksum 全留在 coordinator，不插入 payload。提取工具拒绝绝对路径、穿越、重复条目、链接、非普通文件、PAX metadata 和过大内容。归档验证不能证明外部文件系统、上下文或工具隔离。

## 准备、导出与核验

Python 3.11+；从 repository 根运行：

```bash
.venv/bin/python experiments/codex-pilot-01/prepare.py
.venv/bin/python experiments/codex-pilot-01/verify_blinding.py
.venv/bin/python experiments/codex-pilot-01/export_subjects.py
.venv/bin/python experiments/codex-pilot-01/verify_blinding.py --exports
```

prepare/export 拒绝覆盖。需要独立新准备可给所有命令相同 --root /private/tmp/cpc-preparation-new；这个参数是包含 coordinator/ 和 subject-exports/ 的存储根，不是直接 coordinator 目录。旧 384972c 本地准备材料在 coordinator/previous-preparation-384972c/ 保留，不被当作当前运行结果。

source commit、Skill SHA-256、完整技能/基线/输入/工具哈希和真实主机信息记在忽略提交的 coordinator/manifest.json。来源变化阻止继续评估，不能看到结果后悄悄换答案。网络与 host 能力未知时使用 not_probed/not_assessed，可通过 prepare.py --environment 提供真实操作员观察。

## 真正执行的必要 gate

遵循 [ISOLATION.md](ISOLATION.md) 的 context/filesystem/history/network/result 五种隔离和 [CODEX-CLOUD-RUNBOOK.md](CODEX-CLOUD-RUNBOOK.md)。当前 desktop task 工具不能强制每个 worker 只读单包；独立 task 或 context 本身不够。新的 exports 解决了交付材料混杂问题，**没有**声称本地或云端强制隔离已成立。

未来每个 Cloud task 只接收一个解压包，不附加 CPC source repository，不读 Git/oracle/scorer/coordinator/他组结果；网络和其他外部工具关闭，同一模型/推理设置。先用非计分 fresh sacrificial task 列举所有可读 workspace 文件/哈希并核对外部读通道；与管理员的 mount/cache/tool 审计一起通过才可启动。官方文档没有证明本账号支持 archive-only/no-repository 导入，本 runbook 明确对此保留平台 gate。这一轮不执行 probe 或 32 个任务。

## 收集、评分与人工盲评

未来实际启动后用 collect.py begin --run run-NNN --metadata /coordinator/begin-NNN.json 记账；必须提供真实模型/host/start/task/workspace/isolation/budget。任务停止后 collect.py finish --run run-NNN --status completed --subject-stopped --response /download/run-NNN/response.json --metadata /coordinator/end-NNN.json。失败/超时没有 response 时省略 --response，保留失败，不选择性重试。

score.py/report.py 只读 coordinator/results/，running 状态阻止评分。缺失/非法响应是失败，未执行保持 NA；行为成功保留 not_assessed，自动契约得分不判断 prose 或实际管理正确性。报告给全部 32 行、每组计数/已尝试分母/比例、逐案例所有组间差、失败和可用资源差；没有数据不捏造零用量。report 重复运行前须把旧 blind-review 包移到独立存档，防止覆盖人评。

只给两名独立评审 coordinator/reports/blind-review/，隐藏 condition/model/host/mapping；复用现有 rubric 五项 0–2，六类 hard failure 独立记录，包含严重漏升级。保留分歧与裁决理由，响应自称 CPC 等盲评局限如实记录，不静默删改。人工评分模板不是已完成的评分。

## 轨迹准备

T1 科研校准撤回/恢复，T2 集成/延迟/过期结果，T3 小修复/验收/停止，T4 durable-record 接力/版本变化，每个三阶段，均是明确的 deterministic simulation 材料，非真实工程/科研执行。future stages 只保存在 coordinator/trajectory/。

release_stage.py --task T1 --stage 1 --target /private/tmp/cpc-T1-stage1 只复制一个阶段到新的外部 workspace。后续阶段须 --prior /coordinator/T1/response.json --prior-subject-stopped，检查已保存决策后严格顺序释放。旧 workspace 必须撤销读权限，不能让 worker 读整个 trajectory tree。T4 stage 2 使用新的 Agent B context，仅 --handoff 的 project_record/current_artifacts，绝不传 A 聊天/response；自由文字是否混入聊天由协调者人工核对。此工具不创建 worker，不证明 OS 隔离。

## 限制与工程验证

公开案例是开发 fixtures，不是私有 held-out benchmark；只能测管道行为/机制信号，不证明普遍改善。静态选择题弱于真实轨迹任务；同模型不能证明跨模型 portability；CPC 可能增加 token/时间，baseline 长度未匹配。好结果不能来自无必要等待/过度人类升级。文件哈希、JSON、命令成功、单测不能代替科学有效性、真实授权或 Agent efficacy。

```bash
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python tools/check_repository.py
.venv/bin/python tools/demo.py
```

回归覆盖普通 oracle 警告、嵌套答案键/文本结构、路径与任意额外条目、冻结 baseline/完整 Skill、32 exports 解压验证、确定性 tar/gzip、无 Git/他组文件，以及既有评分/缺失响应/轨迹边界。unit fixtures 只在临时目录测试工具，不作为真实受测结果或用于管道演示。当前实际结果目录没有 response.json。
