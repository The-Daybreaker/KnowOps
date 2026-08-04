# CHANGELOG

本文件记录 obsidian-kb 的版本历史。格式遵循语义化版本；
每次发布的兼容性说明见对应条目。

> 说明：CHANGELOG 为开发期文档，随仓库（git）维护，**不随 skill 包分发**
> （v1.4.0 起打包排除）。

## [2.0.0] - 2026-08-04

### 变更（知识组织模型重构）

- **问题按「未解决 / 已解决」切分**：`问题/未解决/`、`问题/已解决/`；文件名统一
  `YYYY-MM-DD 文件名.md`（简短主题词，不用长句描述）。
- **问题两阶段生命周期**：解决（移入已解决 + `status: done` + `created`/`resolved`
  日期 + TODO 勾选）与沉淀（另行发起：agent 判定知识类型交用户审核 → 创建知识笔记
  + 双向链接回原问题）分离；原问题保留在已解决文件夹，不删除。
- **「知识与经验」改名「知识」**：子目录按知识类型切分（经验/原理/工具/设计/规范/
  案例/模板，初始 7 类，未来可动态扩展）；知识文件名 `YYYY-MM-DD 标题.md`。
- **文件类型去预设化**：剪藏 / 模板 / 附件 / Bases / Canvas 不再预设固定目录
  （原 40-Resources/50-Archive/99-Meta/Attachments 全部取消），存放位置以用户
  指令为准；**收件箱彻底移除**（inboxDir 键删除，无法判定分类时询问用户）；
  **归档移除**。
- **操作日志**：大知识库文件夹（vault 外）新增 `log/YYYY-MM/YYYY-MM-DD.md`，
  每次对知识库的操作（含读取/搜索）追加记录。
- **updated 同步**：每次修改文件后 frontmatter `updated` 必须更新，精确到分钟。
- **标签与双向链接硬性要求**：积极打层级标签；沉淀/剪藏/相关知识之间建立双向链接。

### 兼容性

- **破坏性变更**（升主版本）：配置 schema v1 → v2；`kb_config.py migrate` 自动
  删除 inboxDir/clipDir/templateDir/attachmentDir、knowledgeDir 改名「知识」
  （用户自定义值保留）、补齐 logDir。
- vault 内容不受影响（旧目录结构不强制迁移，由用户决定是否重组）；
  已生成用户手册不被覆盖（新结构仅影响新初始化与新记录）。
- Bases/Canvas 语法不变；剪藏/模板/附件位置改为用户指令驱动（旧配置中的
  对应目录键在迁移时移除）。

## [1.4.0] - 2026-08-04

### 变更

- **移除内置参考技能**：删除 `references/skills/`（obsidian-markdown /
  obsidian-cli / obsidian-bases / json-canvas / defuddle 五份参考技能不再
  随包分发）；SKILL.md 描述与 references 索引同步清理。
- **打包内容纯净化**：开发期文档（CHANGELOG.md / DESIGN.md / REQUIREMENTS.md /
  TEST-REPORT.md 等）不再随包分发，仅由 git 管理；分发包仅含运行时文件
  （SKILL.md、agents/、scripts/、references/、assets/）。

### 兼容性

- 配置 schema 不变（`version: 1`），旧配置无需迁移。
- vault 内容与已生成用户手册不受影响。
- 功能行为不变：移除的是内置参考资料，核心工作流（CLI 写入、分类路由、
  HTML 导出、剪藏等）无变化。

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
