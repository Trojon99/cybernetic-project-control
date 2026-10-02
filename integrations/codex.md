# Codex：本地 Skill（未实机验证）

来源 H2：官方文档列出仓库 `.agents/skills` 和用户 `$HOME/.agents/skills` 等读取位置。以下以项目作用域为例，在目标项目目录中执行，CPC 源目录按实际位置设置：

```bash
CPC_SOURCE=/path/to/cybernetic-project-control
mkdir -p .agents/skills
test ! -e .agents/skills/cybernetic-project-control && \
  cp -R "$CPC_SOURCE/skills/cybernetic-project-control" .agents/skills/
```

不要覆盖项目已有 `AGENTS.md`。阅读 Skill 内 `assets/AGENTS.snippet.md`，经检查后合并必要入口规则。

可明确说：“使用 $cybernetic-project-control，先只读恢复这个项目并提出下一步及验收反馈。”若 host 未显示 Skill，按当前官方文档刷新/重启确认；不能仅凭本说明推断已安装。

不指定固定模型名、隐藏模式、自动 SSH 命令或账号路径。本版只提供格式与行为接入，尚未在用户 Max 上实测。
