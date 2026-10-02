# 可选离线工具

依赖：Python 3.11+，`jsonschema>=4.23,<5`。完整技能复制后可从本包根目录运行：

```bash
python scripts/cpc.py --help
python scripts/cpc.py validate /path/to/project --verify-artifacts
python scripts/cpc.py snapshot /path/to/project
python scripts/cpc.py check-turn /path/to/project /path/to/turn.json --verify-artifacts
python scripts/cpc.py apply /path/to/project /path/to/turn.json --expect-revision 0
```

`apply` **不执行 turn 中描述的工作**；它检查已经提交的记录，验证相关本地产物，创建 receipt 并更新参考状态。它既不是 scheduler，也不是授权认证系统。执行动作应通过宿主已批准工具完成。

本地参考模式仅支持一个合作式写入者、普通本地文件系统。`apply` 使用排他锁与 expected revision；重复相同 turn 幂等，重复 ID 但内容不同拒绝。receipt 先写、state 原子替换；崩溃遗留的孤立 receipt 不算已接受。锁不自动过期，人工确认没有 writer 后才处理遗留锁。

已看到 `.loopx/`、`.apm/`、`.project/`、`PROJECT_STATE.md` 等状态时，`init` 拒绝创建第二套。探测不是穷尽的，Agent 仍需先检查其他现有状态系统。

`--verify-artifacts` 检查路径存在和 SHA-256；单个产物上限 128 MiB。大数据可通过用户认可的 manifest 来记录版本，但检查 manifest 本身不等于重算整个数据集。

拒绝路径穿越、绝对路径、符号链接、重复 JSON keys、NaN/Infinity、过大的记录、不认识的 schema_version。不会联网、执行记录内的 shell、读取凭据或自动推送 Git。

参考工具不提供通用 migrate/approve/force 命令。目标或权限变更先由所有者审查，按项目既有流程留痕；不要用编辑一个 approved 字符串假装获得真实授权。
