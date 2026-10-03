# Codex Cloud Pilot 0.1 runbook（启动准备，尚未执行）

本轮真实模型运行为 **0**，包括 sacrificial probe。本工具只准备/验证导出文件，不自动创建 Codex Cloud tasks；没有调用 Cloud API、建立远程环境、上传、推送或假造 task ID。以下步骤供未来经另行授权的执行轮次使用。

## 当前官方产品模型与证据边界

2026-10-03 核对的当前官方文档说明：新任务从**已发布环境的 prepared filesystem**开始，现有任务继续自己的状态；启动入口是 Work in > Cloud，选择已发布环境。参见 [Cloud environments](https://learn.chatgpt.com/docs/environments/cloud-environments)。新 conversation 并不清空环境内容，因此完整 CPC source environment 不合格。

VM internet 设置和可用托管工具需分别审查；开关关闭不能自行证明 apps/web search/MCP 也被关闭。官方网络/工具控制边界见 [legacy cloud environment security notes](https://learn.chatgpt.com/docs/environments/cloud-environment)。本文从该边界推导额外验收要求，不将 legacy 操作步骤冒充当前 UI。

官方创建流程以选择 repositories 为起点，文档没有确认本账号可用的“直接以 tar.gz 作为唯一项目文件、无 repository”导入入口。本文不虚构上传按钮或 API。操作者必须核实如何在 agent 开始前提供**仅一个**导出包并限制其可读项目文件；如果当前界面只能附加原 CPC repository，停止，使用满足隔离的受管环境，不把 source 附上后靠提示词约束。仅有 [独立 task workspace](https://learn.chatgpt.com/docs/cloud) 仍不足以证明其 payload 干净。

模型不按页面示例或“current”字样猜测：实际启动时选定该账号可用的一个模型/版本和 reasoning configuration，冻结后全部 32 运行相同，记录平台无法暴露的版本/temperature/seed 为 null。不得各组使用不同默认模型或额外 Start skill。

## 1. 协调者本地准备

在 repository 根运行（已有准备不覆盖；--root 可指定另一个全新 storage root）：

```bash
.venv/bin/python experiments/codex-pilot-01/prepare.py
.venv/bin/python experiments/codex-pilot-01/verify_blinding.py
.venv/bin/python experiments/codex-pilot-01/export_subjects.py
.venv/bin/python experiments/codex-pilot-01/verify_blinding.py --exports
```

要求后两次验证退出 0，32 个 exports 全部通过。coordinator/export-manifest.json 和 export-checksums.sha256 留在协调者侧；subject-exports/ 仅有 run-001.tar.gz … run-032.tar.gz。不要上传此整个目录，每个环境只传一个包，传完解压并移出原归档，清单必须与该 run 的 bundle_hashes 一致。

## 2. 由操作员准备单运行环境

阅读 [ISOLATION.md](ISOLATION.md)，核实 A–E 五种隔离。环境需要一致的 OS/runtime、模型工具和预算：600 秒、40 tool calls、4096 输出 tokens 的既定目标；平台无法强制时先记录限制，不假装落实。

在 web/desktop 的 Work in > Cloud > Select environment 中准备**单包专用**环境。不得选择 Trojon99/cybernetic-project-control。若环境配置需要 repository，由管理员另建一个没有 CPC 祖先历史、没有其他 run、仅单包文件的暂存来源，之后在 prepared filesystem 移除 Git metadata 并防止自动 refresh 再引入它。没有实际确认这种控制可行前，该路线仍是未解决的平台能力前提；本轮不创建/推送这些暂存仓库。

设置 network/internet 关闭，无 VPN、network secrets、额外插件/apps、web search 或远程 MCP；审查统一宿主 instructions，取消会注入 PM 指导或协调者历史的 Start skill/memory。检查项目文件后 Publish。记录配置快照、发布版本和完整允许 payload 的 SHA-256；同一环境不得在 scored tasks 间反复换入其他 run 并保留旧缓存。首选一 run 一干净环境。

## 3. Sacrificial isolation probe（未来操作；不计分）

启动一个 fresh task，使用待验收的单包已发布环境，发送以下 probe 指令。只检查边界，不让它答案例：

```text
This is an unscored isolation probe, not a management evaluation.
Do not answer TASK.md or create response.json.
List every readable file in the project workspace recursively, including
hidden files, empty directories, file types and symlink targets. Return each
regular file's relative path and SHA-256. Report permission-denied entries.
Report readable project mounts and additional repository roots outside the
workspace without printing secrets or private contents. Check whether any
source CPC checkout, evals/cases files, evals/run.py, scorer, coordinator
manifest, Git history, other run archives or results are accessible.
Report which external tools/network channels are exposed and whether an
operator-approved benign connectivity probe is denied. Do not query the
benchmark or fetch external project information. Return the inventory and
observed access results, then stop. Do not generate a management response.
```

操作者逐项比对允许清单/哈希；只有预期 blinded bundle、没有 source/oracle/scorer/coordinator/其他 run 才通过工作区探测。probe 看不到更多目录不代表不存在；管理员另核对 mounts、Git/cache、共享文件和托管工具访问政策。如无法检查或确认任一读通道，失败并停止。配置有变必须重测。保存 probe task ID、原始工具观察和审计记录到 coordinator/；不放回 subject 环境。**不要继续这个 probe conversation 来做计分运行。**

为避免不同 payload 环境配置漂移，每个正式环境还应由可信准备流程复核清单及配置。若只能使用模型任务复核，则这些都是非计分 sacrificial tasks，单独留档，不减去或计入 32 个 run。

## 4. 后续经授权才启动计分任务

按 coordinator/manifest.json 的 opaque run 顺序，一次一个 fresh task、新 context。每个任务只接收其包；主用户提示词逐字来自该包的 subject-prompt.md，不附加 A/B/C/D、case mapping、协调者 reasoning 或本 runbook。给全部组相同模型/reasoning/tools/budget；固定的工具安全设置在宿主侧实施。

运行开始后用真实平台元数据做本地记账，collect.py 本身**不会创建/启动任务**：

```bash
.venv/bin/python experiments/codex-pilot-01/collect.py begin --run run-001 --metadata /coordinator/begin-001.json
```

begin-001.json 必须来自实际运行，包含 model、host、start_time、task_id、workspace_id、isolation_evidence、budget；仅记录暴露的 model_version/reasoning 设置，不造值。记录失败、超时、人工介入，不在看到答案后重跑某个条件。

## 5. 终止后收集与协调者评分

确认任务完成/超时并停止后，只把 response.json 复制回协调者机器。不要把 scorer 装到 worker 上，不把评分或他组结果发给它。真实用量/时间在 finish metadata 中保存，未知为 null：

```bash
.venv/bin/python experiments/codex-pilot-01/collect.py finish --run run-001 --status completed --subject-stopped --response /download/run-001/response.json --metadata /coordinator/end-001.json
# 没有输出的真实失败仍保留这一行：
.venv/bin/python experiments/codex-pilot-01/collect.py finish --run run-002 --status timeout --subject-stopped --metadata /coordinator/end-002.json
```

所有 worker 停止后在本地执行 score.py/report.py；任何 running 状态会阻止评分。评分仅使用 coordinator/results/；不存在模型输出时保持 not_executed 与 NA。发给人工评审的只有 coordinator/reports/blind-review/；mapping 与条件标签不发给评审。

## 当前剩余 gate

32 个 exports 通过结构/清单/哈希验证并不解锁执行。本轮尚未配置或实测一个符合单包、无 source/history、无额外工具网络通道的 Cloud 环境，也没有 sacrificial probe；这两项加上未来明确执行授权，是首个 scored run 的 gate。文档准备完成不应写成已验证 Cloud 集成。
