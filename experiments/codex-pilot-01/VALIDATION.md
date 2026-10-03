# 工程验证记录

本次全套 **129 项单元测试通过**（106 项原有 + 23 项 pilot tests）；仓库检查和 synthetic offline demo 通过。此类工程验证不证明 Agent 管理效果。

结构验证允许普通 “do not search for the oracle” 与完整 Skill 的方法警告；拒绝递归 JSON 答案键、显式文本答案结构、评估器路径、超出 allowlist 的任意文件/目录、变更的冻结字节和危险归档条目。32 个单运行 tar.gz 在独立临时目录逐个解压，并使用同一严格验证器重新检查；均通过。归档 SHA-256 只保存在 coordinator/export-manifest.json 和 export-checksums.sha256。

相对于 384972c，没有更改案例、oracle、CPC Skill、baseline、schema、subject-prompt、seed、预算或实验问题。上一轮严格词扫描失败记录保留在本地协调者归档，属于历史问题；不再被当作当前验证结论。准备/报告/归档均排除于 Git 与 source release。

真实受测运行与 sacrificial isolation probe 均为 **0**，实际 results/ 中没有 response.json。工程 unit tests 的临时 fixtures 不计入运行、不用于展示已执行 pipeline。下一 gate 是实际 Cloud 单包环境、上下文/文件/历史/网络/结果隔离配置与非计分探测；尚未验证任何账号的 archive-only environment 导入能力。

可复现检查/导出命令见 README，隔离政策见 ISOLATION.md，未来操作步骤与官方引用见 CODEX-CLOUD-RUNBOOK.md。文档完成不等于 Cloud 集成已运行。
