# 工程验证记录

本次新增 16 项 harness 单测，连同既有 106 项共 **122 项通过**。仓库检查和 synthetic offline demo 通过；全部为工程验证，没有被评估 Agent 运行。

验证发现两处必须保留的固定原文含禁止扫描词：相同主提示词中的 `oracle` 和完整 CPC reference 中的 `eval oracle`。严格扫描对 32 个包给出 40 个文件命中，必须报告失败并阻止启动。未改任何案例 oracle、baseline 或 Skill 文本；没有将这些说明文字误称为答案泄漏。

可复现命令见 README。生成 bundle、逐运行元数据、manifest、报告和本地主机记录被排除于 Git 与 source release；source release 包含可复用 harness，以保持其测试依赖可用。实际环境版本、源 commit 和 SHA-256 记录在本地忽略提交的 manifest。
