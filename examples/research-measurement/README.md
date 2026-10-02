# 合成例子：科研测量

现有校准报告曾支持测量有效；新检查明确使这一批次的旧校准失效。正确管理不是继续增加实验数量，也不是删除所有数据，而是先区分“执行过实验”和“证据仍可用于结论”，再检查受影响范围。

`state.json` 是更新前状态；`turn.json` 是一次已形成的候选记录。所有 artifacts 都是合成材料。

```bash
python tools/cpc.py validate examples/research-measurement --verify-artifacts
python tools/cpc.py check-turn examples/research-measurement examples/research-measurement/turn.json --verify-artifacts
```

在副本中 apply，勿把演示改动误当原始 fixture。
