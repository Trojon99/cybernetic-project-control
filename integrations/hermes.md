# Hermes：本地安装说明（未实机验证）

官方来源 H1 说明默认 skills 目录为 `~/.hermes/skills/`；命名 profile 的根位置可能不同，应先确认正在使用的 HERMES_HOME。CPC 不改变 Hermes 本身。

在 CPC 仓库根目录，默认 profile 的复制示例：

```bash
mkdir -p "$HOME/.hermes/skills"
test ! -e "$HOME/.hermes/skills/cybernetic-project-control" && \
  cp -R skills/cybernetic-project-control "$HOME/.hermes/skills/"
```

目录已存在时先检查版本/本地修改，不覆盖。随后在 host 中确认 Skill 出现；明确请求加载，并用合成项目做 advisory。

Air/Max：先验证 Hermes 的远程工具确实可读 Max 项目。指定一个权威状态位置和写入者，不在 Air、Max 各自创建可写副本。缺少 SSH/视觉能力时，提供清楚的受限行为，不装作看过远端产物。

这份说明只来自官方文档，未测你当前 Hermes 版本、profile、SSH 或图像读取。不把“已复制文件”写成“完成跨机集成”。
