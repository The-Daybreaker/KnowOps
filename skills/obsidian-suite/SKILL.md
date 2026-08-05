---
name: obsidian-suite
description: Obsidian 工具套件调度入口。当任务涉及 Obsidian 笔记/知识库（记录、检索、整理 vault、Canvas、Bases、Markdown、网页抓取）时，先调用本 skill 了解应加载哪些子 skill、加载顺序与存储位置。调度双 skill 体系：knowledge-workflow（知识库工作流程规范，业务流程层）+ kb-obsidian（Obsidian 操作规范与红线，执行层）+ 工具型 skill（按需加载）。
agent_created: true
---

# Obsidian 工具套件（调度入口）

本 skill 是一个**调度入口**，本身不直接干活，只负责告诉你要用哪些 Obsidian 相关
skill，以及它们的调用方式与加载顺序。各 skill 统一用 `Skill` 工具、以
`skill: "<name>"` 的方式加载；安装后位于当前平台 / 工具的用户级 skill 目录
（下称 `<skills-dir>`，即各 skill 实际安装的位置）。

## 双 skill 体系（核心，按顺序加载）

知识库管理拆分为**两个互补的 skill**，职责边界分明、依赖方向单向
（**kb-obsidian 依赖 knowledge-workflow；knowledge-workflow 不依赖、不提及
kb-obsidian**）：

1. **knowledge-workflow** —— 知识库**工作流程规范**（业务流程层）。
   定义知识库内容如何组织与流转：问题（未解决/已解决、解决与沉淀分离）、知识
   沉淀（按类型归档）、项目、日程、任务（TODO）、原生日记、网页剪藏、看板、
   自动化提醒、操作日志、初始化向导、配置与 HTML 导出策略。
   - 调用：`Skill` 工具，`skill: "knowledge-workflow"`
   - 位置：`<skills-dir>/knowledge-workflow/SKILL.md`
   - **规则：任何"记录/管理知识库内容"的任务都必须先加载它，严格按其流程规范
     执行。它是给用户与工具共同遵守的中立规范，不包含任何工具操作细节。**

2. **kb-obsidian** —— Obsidian **操作规范**（执行层）。
   承载所有对工具的要求：Part 1 对所有工具的统一规范与红线（改删前征求同意、
   永不 git init、删除进回收站、记录归属询问用户、信息以用户给出为准、直写例外
   清单等）；Part 2 Obsidian 专有操作（CLI 使用与怪癖、笔记读写改删、日记设置、
   Markdown/Bases/Canvas 要点、剪藏、两步写入、回读校验）。
   - 调用：`Skill` 工具，`skill: "kb-obsidian"`
   - 位置：`<skills-dir>/kb-obsidian/SKILL.md`
   - **规则：执行具体 Obsidian 操作（读写改删、搜索、移动、删除）前必须加载它，
     严格遵循其红线与操作规范；业务流程以 knowledge-workflow 规范为准。**

## 按需加载（工具型 skill，仅在当前任务确实用到对应能力时再加载，避免无谓占用上下文）

以下工具型 skill 均为 **Obsidian 官方技能仓库 [kepano/obsidian-skills](https://github.com/kepano/obsidian-skills)**
（含 obsidian-cli / obsidian-markdown / obsidian-bases / json-canvas / defuddle）
的安装副本，可随官方仓库更新：

- **defuddle** —— 从网页提取干净 Markdown（替代 WebFetch，去噪省 token）。
  - 调用：`Skill` 工具，`skill: "defuddle"`；位置：`<skills-dir>/defuddle/SKILL.md`
- **json-canvas** —— 创建/编辑 `.canvas` 画布文件。
  - 调用：`Skill` 工具，`skill: "json-canvas"`；位置：`<skills-dir>/json-canvas/SKILL.md`
- **obsidian-cli** —— 直接调用 Obsidian CLI 做底层读写/搜索/管理。
  - 调用：`Skill` 工具，`skill: "obsidian-cli"`；位置：`<skills-dir>/obsidian-cli/SKILL.md`
- **obsidian-bases** —— 创建/编辑 `.base` 数据库视图。
  - 调用：`Skill` 工具，`skill: "obsidian-bases"`；位置：`<skills-dir>/obsidian-bases/SKILL.md`
- **obsidian-markdown** —— Obsidian Flavored Markdown 语法（wikilinks、callouts、属性等）。
  - 调用：`Skill` 工具，`skill: "obsidian-markdown"`；位置：`<skills-dir>/obsidian-markdown/SKILL.md`

## 调用约定

1. 接到知识库管理任务 → 先 `Skill` 加载 **knowledge-workflow**（业务流程规范，必读）。
2. 需要执行 Obsidian 操作 → 再加载 **kb-obsidian**（操作规范与红线，必读）。
3. 根据任务实际需要，按需加载上方工具型 skill。
4. 不要一次性把所有 skill 都加载进来；工具型 skill 仅在用到时才加载。
