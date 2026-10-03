# Required execution isolation / 实验隔离要求

**Separate Codex tasks are necessary but not sufficient if their environment contains the source repository.**

导出包是唯一的项目文件 payload。导出验证检查字节、结构和清单，不能证明下述平台隔离。当前仅准备，受测运行与 sacrificial test task 均未执行。

## A. Task-context isolation

每个 run 是全新 conversation/model context，只接收该包中的 identical subject-prompt.md。不得 fork 协调者聊天，不继承其任务总结、oracle、其他条件提示词或结果，不延续 sacrificial probe 的聊天。禁用额外 memory、自动技能/Start skill、插件和连接器；保留执行所需的同一套工具与系统约束，记录无法控制的宿主指令。

## B. Filesystem isolation

每个 worker 只得到一个 run-NNN.tar.gz **解压后的内容**，不是包含 32 个包的目录。项目工作区初始清单和 SHA-256 必须与协调者记录一致；导出包的归档、checksum/mapping 文件都不需要放入工作区。不同 worker 使用独立 VM/容器或可验证的强制访问控制。没有可读 CPC checkout、协调者 mount、个人 home、共享缓存或其他实验项目。普通运行时/系统库可以保持各组相同，但其中不能藏有额外项目、凭据或答案；无法审计的可读 mount 必须视为未通过。只在工作区写 response.json，不给予解除沙箱或挂载其他目录的权限。

## C. Repository/history isolation

不附加原 CPC repository，也不从该仓库建 branch/worktree/shallow clone 作为 subject 环境。导出包不含 `.git`、remote、Git object、bundle、pack 或 source path。工作区和其他可读位置不能有包含 evals/cases、评分器或历史答案的 Git 数据。即使删除当前文件或只保留 subject 目录，Git history/缓存仍可能恢复答案。若云平台必须从仓库准备环境，只能由管理员另建一个从零开始、仅有单运行 payload 的暂存来源；交付给 worker 前移除 Git metadata/其他项目文件，且自动 repository refresh 不能重新增加这些材料。是否可落实须实测，不能按文档或环境名称推定。

## D. Network isolation

本静态 pilot 不需要联网。关闭 agent internet、浏览器/托管 web search、远程 apps/MCP、VPN/外部服务和可用凭据；这些通道不一定由 VM 网络开关一起控制。平台内部模型/执行控制通道不算 subject 查询外部材料的权限，但不能向 subject 暴露可复用凭据。设置期间如需传入单包，可由协调者在 agent 启动前完成；关闭网络后重新发布并用新任务探测。不得在 worker 能读到 source 时让它用网络“帮忙清理环境”。

## E. Result isolation

worker 无法读取其他 worker 输出、results、review map、manifest 或 scorer。平台存储和下载访问也须保持隔离。worker 完成并终止后，协调者复制**仅** response.json 到 coordinator/results/run-NNN/，记录真实 task ID/用量等可用信息；未暴露值保留 null。进行中不得收集或评分；失败照样记录，不选择性重试。不得把评分反馈发回已评分 worker 再换答案。

## 启动验收与证据

运行非计分 sacrificial task，列出其工作区**所有**可读文件，包括 dotfiles、空目录和链接，并返回 SHA-256、文件类型、可读 mount/项目路径和网络/tool 能力探测。与该包的协调者清单逐项比对；预期文件以外出现 CPC source、eval oracle、scorer、coordinator、Git metadata 或其他 run 即失败。列举工作区只是必要的 smoke check：还须由管理员确认 mount、共享缓存、托管工具和历史读取权限。可读项目 mount 无法枚举或隔离时不能启动。

probe 使用与待执行环境相同的已发布配置，不生成 response.json、不算 32 个 scored runs，不复用该 conversation。配置变更后重测，每个单包环境在实际启动前由协调者核对 initial payload inventory。保存探测输出、配置快照、平台/模型版本和批准边界到 coordinator/；本轮不执行该 probe。详见 [云端 runbook](CODEX-CLOUD-RUNBOOK.md)。

## 已实现与未证明

已实现：32 个独立最小归档、确定性打包、协调者 checksum、所有归档重新解压后用同一严格验证器检查。未证明：此本地主机或任何实际云账号是否已配置满足以上隔离。准备完成不表示可以立即启动。
