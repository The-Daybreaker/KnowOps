---
name: knowops-navigator
description: KnowOps 导航（调度入口）。当任务涉及 Obsidian 笔记/知识库（记录、捕获、检索、整理 vault、Canvas、Bases、Markdown、网页素材提取、插件控制、随身端暂存内容入库）时，先调用本 skill 了解应加载哪些子 skill、加载顺序、存储位置，以及外部工具型 skill 的安装检查方式。调度三部分：knowops-workflow（知识库工作流程规范，业务流程层）+ knowops-obsidian（Obsidian 操作规范与红线，执行层）+ 外部工具型 skill（按需加载，来自 kepano/obsidian-skills）；随身端捕获与暂存入库由 everywhere-note 配套 skill 负责。
---

# KnowOps 导航（调度入口）

本 skill 是一个**调度入口**，本身不直接干活，只负责告诉你要用哪些 Obsidian 相关
skill、它们的职责与调用方式，以及**外部工具型 skill 的安装检查流程**。各 skill
统一用当前平台的 skill 加载机制（如 `Skill` 工具）加载；安装后位于当前平台 / 工具
的用户级 skill 目录（下称 `<skills-dir>`，即各 skill 实际安装的位置）。

## 一、双 skill 体系（核心，按顺序加载）

知识库管理拆分为**两个互补的 skill**：**knowops-workflow** 是独立可用的流程规范，
**knowops-obsidian** 是 Obsidian 执行层，经本 navigator 路由加载。大部分知识库
任务以本 navigator 为入口；用户直接调用 knowops-workflow 时也可正常使用。

1. **knowops-workflow** —— 知识库**工作流程规范**（独立可用）。
   定义知识库内容如何组织与流转：00 收件箱（随手记/灵感/待整理内容，捕获与
   审阅沉淀）、01 生活系统（日记/日程/任务/问题）、02 知识系统（概念原理/
   经验方法/方案/案例）、03 资产系统（模板/工作流）、04 规范系统（原则/标准
   规范/检查清单）、05 项目系统（进行中/已完成/项目复盘）、06 看板（Bases
   数据库驱动）、07 归档、08 系统管理（架构/分类/命名/Frontmatter/Agent规则/
   变更记录/用户手册）、插件集成规则、操作日志、初始化向导、配置与 HTML 导出。
   - 调用：`skill: "knowops-workflow"`；位置：`<skills-dir>/knowops-workflow/SKILL.md`
   - **规则：任何"记录 / 管理知识库内容"的任务都必须先加载它，严格按其流程规范
     执行；只安装它即可独立使用，具体执行由 agent 的通用能力完成。**

2. **knowops-obsidian** —— Obsidian **操作规范**（执行层，经本 navigator 路由加载）。
   承载所有对工具的要求：Part 1 对所有工具的统一规范与红线（改删前征求同意、
   永不 git init、删除进回收站、记录归属询问用户、信息以用户给出为准、直写
   例外清单等）；Part 2 Obsidian 专有操作（CLI 使用与怪癖、笔记读写改删、日记
   设置、Markdown/Bases/Canvas 要点、网页素材提取、插件控制、两步写入、回读
   校验）。
   - 调用：`skill: "knowops-obsidian"`；位置：`<skills-dir>/knowops-obsidian/SKILL.md`
   - **规则：执行具体 Obsidian 操作（读写改删、搜索、移动、删除、插件控制）前
     必须加载它，严格遵循其红线与操作规范；业务流程以 knowops-workflow 规范
     为准。**

## 二、外部工具型 skill（按需加载）

以下 skill 是 **Obsidian 官方技能仓库
[kepano/obsidian-skills](https://github.com/kepano/obsidian-skills)** 提供的工具型
skill（仓库内含 obsidian-cli / obsidian-markdown / obsidian-bases / json-canvas /
defuddle 五个），需要用户自行安装后才可用。

### 安装检查（每次需要用到工具型能力时先做）

1. 检查用户级 skill 目录是否存在对应子目录（如 `<skills-dir>/obsidian-cli/`，
   即 `<skills-dir>/<name>/SKILL.md` 是否存在）；存在即已安装。
2. **已安装** → 直接按下方「按需调用指引」加载使用。
3. **未安装** → 询问用户是否安装：
   - 用户同意 → 按当前平台的 skill 安装流程安装（来源：
     https://github.com/kepano/obsidian-skills ；defuddle 需额外
     `npm install -g defuddle`，见其 skill 说明）。
   - 用户拒绝或无法安装 → **改用 Obsidian 官方文档兜底**：
     Obsidian 帮助中心 https://help.obsidian.md （CLI 用法见
     https://help.obsidian.md/cli ），按官方文档完成等价操作。

### 各 skill 功能与触发场景

| skill | 功能 | 何时用（触发） | 关键要点 |
|---|---|---|---|
| **obsidian-cli** | 用 `obsidian` CLI 与**运行中的 Obsidian** 交互：读写/创建/搜索笔记、任务、属性；插件控制（查询/启用/重载/执行插件动作）；主题开发调试 | 需要对 vault 做底层命令式操作；需要控制插件；需要确保 Obsidian 已打开 | 参数用 `name=`/`file=`/`path=`/`vault=`（`vault=<名称>` 放首位）；完整命令以 `obsidian help` 为准；文档 https://help.obsidian.md/cli |
| **obsidian-markdown** | Obsidian Flavored Markdown 语法：wikilinks、embeds、callouts、properties、comments 等扩展 | 编写/编辑 Obsidian 笔记时涉及这些专用语法（标准 Markdown 是常识，无需加载） | 只覆盖 Obsidian 特有扩展；内链用 wikilink、外链用标准链接；细节见其 references/ |
| **obsidian-bases** | 创建/编辑 `.base` 文件：views / filters / formulas / summaries，聚合笔记为 table / cards / list / map 视图 | 任务提到 Bases、数据库式视图、按属性/标签/目录聚合过滤（含看板） | `.base` 是 YAML；filters 作用于全部视图，可组合 and/or/not；properties 里配置显示名 |
| **json-canvas** | 创建/编辑 `.canvas` 画布：nodes / edges / groups，思维导图、流程图 | 任务提到 Canvas 画布、可视化连接图 | JSON Canvas Spec 1.0；节点需唯一 16 位 hex id；edges 引用有效节点 id；写后校验 JSON |
| **defuddle** | 从网页提取干净 Markdown（去导航/广告，省 token），替代通用网页抓取 | 捕获/分析网页文章、博客、文档页面（URL 不以 .md 结尾），素材进收件箱待整理 | `defuddle parse <url> --md`；**.md 结尾的 URL 不要用它**，直接抓原文 |

### 按需调用指引（Obsidian 知识库相关操作，优先查看对应 skill）

接到知识库任务后，按以下链条决定加载哪个：

1. **记录 / 管理内容**（收件箱捕获与审阅、问题、知识、日程、任务、看板、归档）
   → 加载 **knowops-workflow**（流程规范，必读；独立可用）。
2. **执行 vault 操作**（创建/读写/搜索/移动/删除笔记、日记、素材落库、插件控制）
   → 加载 **knowops-obsidian**（操作规范与红线，必读）——其中涉及的**具体语法与命令
   形态**，**优先查看对应工具型 skill**：CLI 命令看 `obsidian-cli`、Markdown
   语法看 `obsidian-markdown`、聚合视图看 `obsidian-bases`、画布看
   `json-canvas`、网页提取看 `defuddle`。
3. 工具型 skill 仅在实际用到对应能力时加载，**不要一次性全部加载**（避免占用
   上下文）；未安装的先按「安装检查」流程处理。
4. 兜底：工具型 skill 不可用且用户不安装时，按 Obsidian 官方文档
   （https://help.obsidian.md ）完成等价操作，并在回复中说明所用文档来源。

## 三、随身端捕获配套 skill（everywhere-note）

本仓库第四个 skill **everywhere-note**（随身记录与统一入库）与套件配套，分两个
能力部分、渐进式按需加载：

1. **随身端捕获**（手机/平板等）：手机端只安装 everywhere-note 即可，用户
   @ 本 skill 后直接口述内容，生成符合知识库格式的 markdown 条目并设置当晚
   22:00 提醒；其 `references/mobile-capture.md` **独立自洽，不依赖本套件**。
2. **桌面端入库**（电脑）：本套件收到“入库今天手机记的 / 把暂存内容存进知识库”
   等请求时，加载 everywhere-note 的 `references/desktop-ingest.md`，并按
   knowops-workflow → knowops-obsidian → 工具型按需的既有顺序执行落库。

依赖方向：**knowops-navigator → everywhere-note（桌面部分）**；everywhere-note
不反向路由回本套件。桌面端直接说“记一下……”仍由 knowops-workflow 处理。

## 四、调用约定（汇总）

1. 接到知识库管理任务 → 先加载 **knowops-workflow**（流程规范，独立可用；执行由 agent 通用能力完成）。
2. 需要执行 Obsidian 操作 → 再加载 **knowops-obsidian**（操作规范与红线）。
3. 具体操作涉及语法/命令 → 按「按需调用指引」加载对应**工具型 skill**（先检查
   是否已安装；未装则询问用户，附 kepano/obsidian-skills 仓库地址；用户不装则
   用 Obsidian 官方文档兜底）。
4. 工具型 skill 按需加载，不一次全载。
5. 插件集成：插件规则以 `08 系统管理/Agent规则.md` 为准，操作前读取、操作后
   按规则执行；插件一般由 agent 经 CLI 控制。
6. 随身端捕获 / 暂存内容入库：手机/随身设备上直接使用 everywhere-note
   （`references/mobile-capture.md`）；电脑端接收暂存内容/文件要求入库时，加载
   everywhere-note 的 `references/desktop-ingest.md`，并遵循本约定第 1–5 条执行。
