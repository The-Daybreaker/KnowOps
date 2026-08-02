# CHANGELOG

本文件记录 obsidian-kb 的版本历史。格式遵循语义化版本；
每次发布的兼容性说明见对应条目。

## [1.0.0] - 2026-08-03

首个版本，全新开发。

### 新增

- 基于 Obsidian CLI 的知识库管理能力：笔记创建 / 读取 / 搜索 / 整理（移动、
  重命名、归档）、原生日记（按月切分 `YYYY-MM/YYYY-MM-DD`）、任务、属性与标签、
  Bases 视图、Canvas 画布、附件、模板、网页剪藏（defuddle）。
- HTML 镜像导出：vault 外目录、相对路径镜像、mtime 增量、删除同步移除、
  索引页生成；自写轻量 Markdown 转换器（双链 / Callout / 表格 / 任务列表 /
  Mermaid CDN 渲染离线降级 / 附件复制）。
- 配置驱动与多 vault：配置文件默认写入大知识库文件夹（vault 上级目录），
  按项目隔离；支持注册 / 列出 / 移除 / 默认切换 / 按名解析 / 路径校验。
- 首次初始化向导：确认实际 vault 路径与名称（不假设固定名）、复制用户手册
  （不覆盖）、确认 HTML 导出目录。
- 安全机制：删除仅走 CLI（系统回收站，禁用 `permanent`）；修改 / 删除前用户同意；
  创建前相似检查；Git 仅提交不建仓。
- 脚本：`kb_config.py`（配置）、`kb_env.py`（环境自检与拉起）、
  `html_export.py`（镜像导出）、`update_skill.py`（发布辅助）。
- 文档：`SKILL.md`（中文，渐进披露）、`references/`（CLI 速查、属性约定、
  Bases / Canvas 要点、回收站验证）、`assets/user-manual.md`（用户手册模板）、
  `DESIGN.md`（架构决策）。

### 兼容性

- 初始版本，无历史配置需迁移；配置 schema `version: 1`。
- vault 内容与用户手册不受 skill 安装 / 升级影响。
