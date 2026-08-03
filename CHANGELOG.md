# CHANGELOG

本文件记录 obsidian-kb 的版本历史。格式遵循语义化版本；
每次发布的兼容性说明见对应条目。

## [1.3.0] - 2026-08-03

### 变更

- **取消"普通笔记 → 收件箱"兜底**：判断不出类型时，agent 必须询问用户归属，
  由用户决策后按选定模块路由；不得静默写入 `inboxDir`（配置键仅保留兼容）。
- **超长文本两步写入**：内容 >4000 字符时，先用 CLI `create` 创建占位文件
  （创建动作仍走 CLI），再直接写入完整内容并回读校验（CLI 参数长度受限，
  例外清单第 5 条）；普通长度内容仍全走 CLI。
- **HTML 镜像只保留 vault 级索引**：不再生成导出根级 `index.html`
  （历史上已生成的根级索引在下次导出时自动清理）；深层 `index.html` 即完整
  详细索引。
- **用户手册复制流程显式化**：初始化向导第 9 步明确为"必做流程规范"——
  复制到**大知识库文件夹根目录**（与配置同层），默认名 `用户手册.md`，
  已存在绝不覆盖。

### 兼容性

- 配置 schema 不变（`version: 1`）；`inboxDir` 键保留，旧配置无需迁移。
- 导出目录中已生成的根级 `index.html` 会被自动移除（尽力而为，失败不阻断）。
- vault 内容与已生成用户手册不受影响。

## [1.2.0] - 2026-08-03

### 新增

- **创建笔记自动分类路由**：记录请求先判定模块类型再路由，不再一律进收件箱——
  问题 → `问题/`（纯文字单文件；含图片等资源建同名文件夹）；项目 → `项目/<项目名>/`；
  剪藏 → `clipDir`；日记 → 原生日记；普通 → 收件箱兜底。
- **联动动作**：记录问题 / 项目后自动写一行当日日志，并向 vault 根目录唯一
  待办文件 `TODO.md` 追加 `- [ ]` 待办（附双链，TODO.md 不存在自动创建）。
- **问题沉淀工作流**：问题解决后移入 `知识与经验/`（先展示方案征得同意），
  属性标注 `resolved`（解决日期，`created` 为出现日期）、`status: done`，
  正文追加经验总结，TODO 对应条目用 `task path=TODO.md line=<n> done` 勾选。
- 配置偏好新键：`questionDir`（问题）、`projectsDir`（项目）、
  `knowledgeDir`（知识与经验）、`todoFile`（TODO.md）；
  `dailyFolder` 默认值由 `10-Daily` 改为 `日志`。
- 用户手册更新：模块目录结构、问题生命周期说明。

### 兼容性

- 配置 schema 不变（`version: 1`）；旧配置运行 `kb_config.py migrate` 可自动
  补齐新偏好键（**缺省补齐，不覆盖已有值**——旧配置的 `dailyFolder` 等保持原样）。
- vault 存量内容不受影响；已生成用户手册不被覆盖（新结构仅影响新初始化）。

## [1.1.0] - 2026-08-03

### 新增

- 内置五份参考技能到 `references/skills/`（渐进披露，编写对应内容时按需加载）：
  `obsidian-markdown`（含 CALLOUTS / EMBEDS / PROPERTIES 细节文档）、
  `obsidian-cli`、`obsidian-bases`（含 FUNCTIONS_REFERENCE 函数全集）、
  `json-canvas`（含 EXAMPLES）、`defuddle`。
- SKILL.md 描述与 references 索引同步收录上述技能。

### 兼容性

- 向后兼容：仅新增 references 内容，配置 schema 不变（`version: 1`），
  旧配置直接可读；vault 内容与已生成用户手册不受影响。
- 打包文件名时间戳改为分钟精度（`obsidian-kb-vX.Y.Z-<yyyymmdd-hhmm>.zip`）。

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
