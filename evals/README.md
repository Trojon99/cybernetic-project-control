# Public development cases

26 个原创合成案例覆盖状态恢复、任务/项目进展、观测不足、时滞、接口耦合、重规划、科研负结果、权限、预算与不过度触发。

```bash
# 只为一个案例准备受测输入；不会调用模型
python evals/run.py prepare --case E07 --output /tmp/cpc-case-E07

# 由真实 Agent 在隔离会话中回答，保存为 response.json 后：
python evals/run.py score --case E07 --response /tmp/response.json
```

评分只检查结构、候选选择、mode 与证据 ID。理由的真实性/质量、是否真实读取文件和执行行为需人工/轨迹审查。不要把这部分分数当学术结果。

[完整协议](PROTOCOL.md) · [人工 rubric](rubric.md) · [轨迹任务](trajectory-tasks.md)
