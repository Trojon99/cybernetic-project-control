# 集成状态

| 对象 | 本版提供 | 状态 |
|---|---|---|
| 通用文件型 Agent | 自包含 Skill 和接入检查表 | package_checked；模型效果未测试 |
| Hermes | 基于官方 skills 文档的本地复制/显式调用说明 | guidance_only；未连接用户 Air |
| Codex | 基于官方文档的 `.agents/skills` 安装说明 | guidance_only；未运行用户 Codex |
| Evo / 本地模型 | 显式读取入口、能力探测和精简模式 | guidance_only；不假设未知配置格式 |
| LoopX | 复用状态/配额/门槛的映射 contract | guidance_only；没有 adapter 代码 |
| PSG / APM | 现有记录与角色映射建议 | guidance_only；没有迁移或写入插件 |

## 共同接入清单

确认用户选定的项目；读取其原有指令；确认 Skill 和相对资源能完整读取；识别权威状态；探测实际工具权限；确认工作模式、预算和受保护动作；用一个合成案例检查输出；再用小范围真实任务评估。

读取 Markdown 只让规则可用，不保证模型执行质量。不会自动获得 GitHub、SSH、文件、图像、MCP 或 scheduler。

对真实项目的写入、宿主配置和 GitHub 发布，本包都不自动操作。
