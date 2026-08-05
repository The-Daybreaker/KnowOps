# CHANGELOG

本文件记录本仓库的版本历史。格式遵循语义化版本；
每次发布的兼容性说明见对应条目。
（v1.0.0~v2.3.3 为单 skill `obsidian-kb` 时期；v0.6.0 起为双 skill：
`knowledge-workflow` / `kb-obsidian`，共用同一版本号、一起发布。）

> 说明：CHANGELOG 为开发期文档，随仓库（git）维护，**不随 skill 包分发**
> （v1.4.0 起打包排除）。

## [0.9.1] - 2026-08-05

### 修复（真实场景测试暴露的 CLI 文档缺口）

- **cli.md 命令形态修正**（实测与文档不符）：
  - `search <关键词>` → **`search query=<关键词>`**；
  - `move file=<源> path=<目标>` → **`move file=<源> to=<目标>`**；
  - 补全局选项 **`vault=<name>`**（多 vault 指定目标库，放子命令前）；
- **cli.md 实测注意补充**：点开头**目录**（`.config/`）同样不可达（不只点开头
  文件名），隐藏目录内文件需直写（例外清单第 6 条）；`append` 只能追加到文件
  末尾，需插入中间位置时用 read → 重组 → create overwrite；
- **例外清单补第 6 条**（SKILL.md Part 1 + references/redlines.md）：隐藏目录
  （点开头）内文件工具接口无法访问，可直写（如操作日志 / 手册 / 配置）。

## [0.9.0] - 2026-08-05

### 调整（规范视角中立化 + 依赖方向明确）

- **knowledge-workflow 改写为中立规范视角**（用户拍板）：移除全部执行视角表述
  （"询问用户 / 展示给用户 / 用户口述 / 由用户决定 / 交用户审核"等），改为对
  流程本身的要求——无法判定归属改为"自行判断，可新增"；日程录入改为"记录内容"；
  初始化向导去除"告知 / 引导 / 提示用户"等执行动词；**不提及任何操作层/配套
  skill**（knowledge-workflow 不依赖、不提及 kb-obsidian）；
- **kb-obsidian 补执行条款并明确依赖**（用户拍板）：定位段点名依赖
  knowledge-workflow（"流程与规则以 knowledge-workflow 规范为准"）；Part 1
  新增第 8 条「记录归属决策」（无法判定归属时询问用户，由用户决定写入哪一模块；
  新增模块/知识类型先向用户确认）、第 9 条「信息以用户给出为准」（记录内容由
  用户给出，不自行臆造，不足时询问补齐）；references/redlines.md 同步；
- **补齐「操作后流程」小节**：消除 SKILL.md 中悬空引用（写日志 / 看板反映确认 /
  版本提交 / 反馈）；
- **测试**：脚本级 20/20；真实 forward-test 6/6（测试库全量）；双 skill
  quick_validate 通过。

## [0.8.0] - 2026-08-05

### 调整（定名 + 精简 + 发布结构）

- **Skill B 定名 `kb-obsidian`**（用户拍板）：`knowledge-manager-obsidian` →
  `kb-obsidian`（SKILL.md name、目录、发布工具 SKILLS 列表、README/DESIGN/
  REQUIREMENTS 同步）；
- **移除 Skill A 的 agents/**：`openai.yaml` 不属于通用 skill 规范，删除
  （knowledge-workflow 打包文件 7 → 6）；
- **dist 按版本分目录**：发布产物输出到 `dist/<version>/`
  （如 `dist/0.8.0/knowledge-workflow-v0.8.0-<ts>.zip`）；旧包仍归档在
  `legacy/dist-archive/`；
- **测试约定（硬性）**：「Obsidian测试知识库」为测试专用库，每次更新后发布前
  必须在该库执行**全量真实场景测试**（forward-test）；
- **测试**：脚本级 20/20；真实 forward-test 6/6（测试库 v5 配置，全量场景）；
  双 skill quick_validate 通过。

## [0.7.0] - 2026-08-05

### 调整（改名 + 目录整理 + 全面审计）

- **双 skill 改名**（用户拍板）：
  - `knowledge-base` → **`knowledge-workflow`**（Skill A：知识库管理工作流程规范）；
  - `obsidian-kb` → **`knowledge-manager-obsidian`**（Skill B：Obsidian 操作规范）；
  - 配置文件名随之更新：`knowledge-workflow.config.json`（schema **v4→v5**，
    MIGRATIONS[4]；`kb_config.py migrate` 提供迁移，旧名 find 兼容并引导迁移）。
- **根目录整理**：开发期文档与发布工具归类到 **`dev/`**（CHANGELOG / DESIGN /
  REQUIREMENTS / TEST-REPORT / scripts/update_skill.py），仓库根只保留
  skills/、legacy/、README（中英）、LICENSE、.gitignore、dist/；
- **合并冗余**：`refactor-v3.0-plan.md` 要点并入 DESIGN §0.5（拆分决策记录）后删除；
- **归档旧产物**：dist/ 全部旧发布包（v1.0.0~v2.3.3 与 v0.6.0 旧名包）移入
  `legacy/dist-archive/`；
- **审计修复**：update_skill.py 的 quick_validate 发现逻辑清理（WORKBUDDY_HOME
  直查 + 常见安装位置 + --validator 覆盖）；SKILL_ROOT 适配 dev/ 层级；
  README/CHANGELOG/REQUIREMENTS 表述同步新名；
- **测试**：脚本级 20/20（含 v3→v5、v4→v5 迁移与旧名→新名文件迁移）；真实
  forward-test 6/6（v5 配置，CLI 创建/回读/导出/删除进回收站/日志）；双 skill
  quick_validate 通过。

## [0.6.0] - 2026-08-05

### 重大变更（拆分重构，替换原规划 v3.0.0）

- **拆分为两个 skill**（单仓库双 skill，一起发布一起升级）：
  - `knowledge-base`（Skill A）：知识库管理**工作流程规范**（workflow），给
    用户与 agent 共同遵守；只描述流程，**不提及任何工具名/命令/委托链**
    （工具层连接由用户另行编排）；
  - `obsidian-kb`（Skill B，沿用原名）：**工具操作规范**——Part 1 对所有工具
    的统一规范与红线（改删前征求同意、永不 git init、删除进回收站、直写例外
    清单）；Part 2 Obsidian 专有规范（CLI 使用与怪癖、笔记读写改删、日记设置、
    Markdown/Bases/Canvas 语法要点、剪藏、两步写入、回读校验）；
  - 能力边界：A 管"流程怎么走"，B 管"工具怎么用/行为红线"，互不越界。
- **旧版存档**：原 obsidian-kb 全部文件原样归档 `legacy/obsidian-kb/`（内容
  一字不改，git 历史保留）；新两个 skill 从零构建，不复用旧文件。
- **知识库无关文件位置**：默认改为 **vault 内隐藏目录 `.config/`**（配置/log/
  手册/HTML 导出）；红线修订为"允许隐藏目录，不写入用户笔记内容区、不影响
  笔记浏览"；`.config/` 不进 HTML 导出、不参与看板聚合。
- **HTML 镜像导出改初始化可选**：不需要则跳过；默认 `<vault>/.config/HTML-Export/`。
- **配置文件名**：`obsidian-kb.config.json` → `knowledge-base.config.json`
  （schema v3→v4，`kb_config.py migrate` 提供迁移；旧文件名 find 兼容并引导迁移）。
- **通用化**：references 去除设备经验（1.13.4 / Windows / bash / 受管运行时
  路径）；Python 解释器发现改通用探测链（python → py -3 → 提示安装 3.10+）。
- **发布**：update_skill.py 改双 skill 打包；仓库根件 README（中英双语）/
  LICENSE(MIT) / .gitignore；发布范围=仅本地（双 zip + git 提交，不推 GitHub）。
- display_name：KB Manager（A）/ Obsidian Guide（B）。

## [2.3.3] - 2026-08-05

### 修复（全面审计 + 全类型测试）

- **一致性修复（10 处）**：SKILL.md 初始化向导/日程小节/操作后流程中的"各模块
  .base""日程.base"旧表述改为「看板.base」（v2.3.2 定稿形态）；references 索引
  补 canvas.md；agents/openai.yaml 补齐日程/自动化提醒/看板/obsidian-suite 委托；
  user-manual 区分"看板总览"与"按需 .base 视图"；REQUIREMENTS 初始化/目录模板/
  验收标准同步看板.base 形态；DESIGN 标题升至 v2.3.2。
- **测试**：quick_validate、4 脚本编译、kb_config 全命令端到端（init/add-vault/
  list/get/set/set-default/path/validate/migrate v1→v3/remove-vault）、html_export
  （渲染/索引/孤儿清理）、测试库真实 forward-test **12/12 通过**（问题解决/沉淀/
  TODO 折叠归档/看板动态增补/日程完成/操作日志/HTML 导出/删除回收站）。

## [2.3.2] - 2026-08-05

### 调整

- **看板形态定稿**：`看板.base` 承载数据源（单文件 `views` 数组多视图），
  `看板.md` 嵌入 `![[看板.base#视图名]]`，**两个文件命名统一为「看板」**；
  明确 .base 是 Obsidian 原生实时聚合的必需数据源（无 .base 的实时方案仅
  Dataview 插件或手工维护静态列表，均不采用）；动态板块（只加载已有模块）保留。

## [2.3.1] - 2026-08-05

### 修复与调整

- **修复：Bases 不支持 `calendar` 视图类型**（实测 Obsidian 1.13.4 报"未知视图
  类型"）——看板中日程板块一律用 `table` 视图（按 `date` 排序 +「即将到来」
  过滤 `date >= today()`），不再使用 calendar；
- **看板结构调整**：取消"总看板.base"聚合文件——**看板.md 是唯一看板文件**，
  各模块数据源为按内容命名的 .base（`问题.base` / `日程.base` / `任务.base`…，
  只建有内容的模块），看板.md 嵌入 `![[<模块>.base#视图名]]`；
- 同步更新 SKILL.md / references/bases.md / REQUIREMENTS.md / DESIGN.md。

## [2.3.0] - 2026-08-05

### 变更

- **Obsidian 操作委托（用户拍板）**：SKILL.md 移除全部 Obsidian 操作规范
  （CLI 命令、Markdown / Bases / Canvas 语法、defuddle 用法等），改为由
  `@skill:obsidian-suite` 调度指导，具体用法查看 `obsidian-cli` /
  `obsidian-markdown` / `obsidian-bases` / `json-canvas` / `defuddle` 专用 skill；
  references 四文件（cli-commands / bases / canvas / trash-verification）仅保留
  **实测经验**（盘符陷阱、CLI 写 Canvas 的坑、回收站验证、看板板块过滤设计等），
  标注"仅供参考、需自行验证、以专用 skill 为准"；properties.md 保留领域设计。
- **看板重构**：由"多个分类 .base 文件"改为**一个「总看板.base」多视图** +
  看板.md 嵌入；**只加载已有模块**（生成时检查各模块是否有笔记，只为有内容的
  模块建视图；板块首次出现内容时自动增补）；CSS 美化改用 **snippet**
  （`.obsidian/snippets/obsidian-kb-dashboard.css`，编辑/阅读模式都生效，
  `.dashboard` 前缀限定作用域，写 `.obsidian` 前征得同意）。
- **测试约定**：记录测试库
  `D:\Peojects\MyProject\Skills\知识库skill测试\Obsidian测试知识库`（已注册）；
  发布流程增加"每次更新后自测"（真实 forward-test）。

## [2.2.0] - 2026-08-05

### 新增

- **自动化提醒（平台无关）**：添加待办 / 日程后自动判断时间信号——强信号
  （"提醒我" / 具体时刻 / 周期词）直接创建定时提醒，弱信号（仅截止日期）先询问；
  使用当前 agent 平台可用的自动化能力，**不写死特定工具**；TODO 条目旁标注
  「已设提醒」，创建/取消均记入操作日志。
- **日程管理**：新增 `日程/` 内容模块（配置键 `scheduleDir`）；每条日程一篇笔记
  （`YYYY-MM-DD 标题.md`），属性 `type: event` + `date` / `end` / `location` /
  `status`（scheduled / done / cancelled）+ `日程` 标签；口述即录，完成/取消只改
  status 与 updated（不移动）；可联动自动化提醒。
- **看板总览（初始化可选组件）**：vault 根目录 `看板.md`（配置键 `dashboardFile`）
  嵌入 7 个 `.base` 板块视图（问题 / 任务 / 日程 / 知识 / 项目 / 剪藏 / 日记）；
  交互全部 Bases 原生（视图切换 / 排序 / 过滤 / 分组 / 点击打开），不依赖插件；
  数据随笔记属性实时反映，**及时更新**无需重建。
- 分类路由新增「日程」类型；操作后流程新增「看板反映确认」步骤。

### 配置变更（schema v2 → v3）

- 新增 `scheduleDir`（默认 `日程`）与 `dashboardFile`（默认 `看板.md`）；
  旧配置 `migrate` 自动补齐（缺省补齐、不覆盖自定义值），无废弃键。

## [2.1.0] - 2026-08-04

### 新增

- **已完成待办折叠归档**：勾选完成（`- [x]`）后，条目自动移入 TODO.md 底部
  「已完成」折叠块（callout `> [!success]- 已完成`，默认折叠）；**最新完成排最上、
  完成越久越靠下**，进行中条目保持原序在上。
- 实现为 SKILL.md 内联工作流（CLI 读取 → 定位刚完成行 → 重组 → `create overwrite`
  写回，全程 CLI），不新增脚本；历史遗留的块外 `- [x]` 行在下次重组时一并收进块内。

### 兼容性

- 配置 schema 不变（`version: 2`），无需迁移。
- TODO.md 既有内容不受影响（首次勾选后按新结构重组）。

## [2.0.1] - 2026-08-04

### 变更

- **文件名命名约定统一**：问题 / 知识笔记文件名由「简短主题词」改为「简短描述」
  （如 `2026-08-04 FPGA同步异步复位问题.md`），SKILL.md / REQUIREMENTS.md /
  CHANGELOG.md 同步（用户拍板）。
- **发布约定变更**：每次改动完成后自动执行发布（`update_skill.py release`：
  check → package → commit），不再等待用户明确要求（用户拍板，v2.0.1 起）；
  版本号按语义化版本推进。

### 兼容性

- 配置 schema 不变（`version: 2`），无需迁移。
- 仅文档表述与发布流程变更，功能行为不变。

## [2.0.0] - 2026-08-04

### 变更（知识组织模型重构）

- **问题按「未解决 / 已解决」切分**：`问题/未解决/`、`问题/已解决/`；文件名统一
  `YYYY-MM-DD 文件名.md`（简短描述，不用长句描述）。
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
