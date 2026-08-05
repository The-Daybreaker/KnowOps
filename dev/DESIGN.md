# DESIGN — knowledge-workflow / kb-obsidian / obsidian-suite 设计文档（v0.10.0）

## 0. skill 组合架构（2026-08-05 v0.6.0 起，v0.10.0 加入调度入口，覆盖后续章节的旧单 skill 描述）

- **skill 组合**：`knowledge-workflow`（Skill A，原 knowledge-base）= 工作流程
  规范（workflow），只描述知识库流程"应该怎么走"，**不提及任何工具名/命令/
  委托链**；`kb-obsidian`（Skill B，原 obsidian-kb → knowledge-manager-obsidian）=
  工具操作规范，含 Part 1 对所有工具的统一红线（改删前征求同意、永不 git init、
  删除进回收站、记录归属询问用户、直写例外清单）与 Part 2 Obsidian 专有操作
  （CLI 使用与怪癖、笔记操作、日记设置、Markdown/Bases/Canvas 要点、剪藏、
  两步写入、回读校验）；`obsidian-suite`（Skill C，v0.10.0 加入）= 调度入口，
  指引加载顺序（knowledge-workflow → kb-obsidian → 工具型按需）。依赖方向单向：
  **kb-obsidian 依赖 knowledge-workflow；knowledge-workflow 不提及任何其他 skill**。
  工具层连接由用户另行编排。
- **后续章节定位**：§1.1–§1.6 的架构决策（Vault 唯一数据源、CLI 唯一写入口、
  配置驱动等）在拆分后归属 Skill B（工具操作层）或双 skill 共用原则；
  §2 模块职责归属 Skill A 的流程规范。凡与本 §0 冲突之处以 §0 为准。
- **知识库无关文件位置**（v5 配置）：默认 vault 内隐藏目录 `.config/`
  （配置/log/手册/HTML 导出）；红线修订为"允许隐藏目录，不写入用户笔记区"。
- **配置文件名**：`obsidian-kb.config.json`（v≤3）/ `knowledge-base.config.json`
  （v4）→ `knowledge-workflow.config.json`（v5，迁移函数见 kb_config.py
  MIGRATIONS[3]/[4]，旧名 find 兼容并引导迁移）。
- **发布形态**：单仓库双 skill 统一版本，双 zip；旧版归档 `legacy/obsidian-kb/`
  （内容不改），旧发布包归档 `legacy/dist-archive/`。

## 0.5 拆分重构决策记录（原 refactor-v3.0-plan.md 并入，2026-08-05）

> 原独立方案文档 `refactor-v3.0-plan.md` 已完成使命，要点并入本节后删除。

**背景与动机**：原 obsidian-kb 单 skill 混了两类知识（知识库管理逻辑 + Obsidian
操作知识），职责边界模糊；references 大量本机实测表述，通用性差，不便发布。

**已确认决策**（2026-08-05 多轮用户确认）：
1. 拆两个 skill，能力边界：A 管"流程怎么走"（纯 workflow 规范，不放 agent 行为
   纪律、不写任何工具名/命令/委托链，仅保留"创建前相似检查"流程环节）；
   B 管"工具怎么用/行为红线"（所有对工具的要求都放 B，分统一红线 + Obsidian
   专有两部分）。
2. 单仓库双 skill，一起发布一起升级（统一版本号）。
3. 知识库无关文件默认 vault 内隐藏目录 `.config/`（配置/log/手册/HTML 导出），
   红线修订为"允许隐藏目录、不写入用户笔记区"；HTML 镜像导出改初始化可选。
4. 配置文件名随 skill 名：obsidian-kb → knowledge-base → knowledge-workflow
   （schema v3→v4→v5，缺省补齐不覆盖自定义值）。
5. 发布范围：仅本地（双 zip + git 提交），GitHub 仓库结构（双语 README + MIT
   LICENSE + .gitignore）就位备用；统一版本号 0.6.0 起。
6. 旧版文件原样归档 `legacy/obsidian-kb/`（内容一字不改，git 历史保留）；
   新两个 skill 从零构建，不复用旧文件。

**通用化处理清单**：references 去除设备经验（1.13.4/Windows/bash/回收站路径/
受管运行时）；Python 解释器发现改通用探测链（python → py -3 → 提示安装 3.10+）；
测试库路径只存开发文档与记忆，不进包。

**实施九步**（v0.6.0 已全部完成）：归档 legacy → 从零建 A → 从零建 B → 配置
迁移 → 发布工具双打包 → 仓库根件 → 开发文档 → 测试（quick_validate + 脚本级
18/18 + 真实 forward-test 6/6）→ 发布 0.6.0（双 zip + commit）。
**v0.7.0 整理**：双 skill 改名（knowledge-workflow / knowledge-manager-obsidian）、
配置 v5、根目录开发文档归类 dev/、方案并入本节、dist 旧包归档 legacy/dist-archive/。

## 1. 架构决策

### 1.1 Vault 是唯一数据源

不构建任何自研引擎：无 SQLite 索引、无同步映射表、无冲突副本、无守护进程、
无数据库。所有知识状态以 vault 内文件为准，Obsidian 本体负责索引与渲染。

### 1.2 操作通道：Obsidian CLI 唯一写入口

- 写入 / 修改 / 移动 / 重命名 / 删除：只走 Obsidian CLI；
- 读取：优先 CLI（`read` / `search` / `tasks` / `tags` / `backlinks` 等）；
- 直接文件访问仅限例外清单（见 `references/cli-commands.md` 末尾）：
  CLI 不可用且用户同意、格式校验、二进制附件、HTML 导出读源文件；
  每次例外使用必须在回复中说明原因。

理由：CLI 会维护 Obsidian 的索引、链接更新、模板展开与回收站语义；绕过 CLI
写文件会造成索引滞后与链接断裂。

### 1.3 配置驱动，零硬编码

- 配置文件 `obsidian-kb.config.json` 保存：vault 名→路径映射、默认 vault、
  HTML 导出根目录、CLI 路径、偏好（日记格式、目录、Git 开关等），带 `version` 字段；
- 发现顺序：会话显式指定 → 从当前目录向上查找 → 首次初始化向导；
- 默认写入**大知识库文件夹（vault 上级目录）**，绝不写入 vault 内部，
  不写入系统环境变量 / 全局用户目录 → 多个 agent / 项目并行管理不同知识库时
  配置互相隔离；
- vault 在 agent 项目之前已由用户创建、名称不统一，skill 不假设任何固定名称，
  初始化必须读取用户确认的实际路径与名称。

### 1.4 搜索不封装

CLI `search` 已完备，由 agent 直接调用；skill 不提供搜索工具。

### 1.4.1 知识模型：模块路由，无收件箱（v1.2.0 起，v2.0.0 修订）

创建动作先判定模块类型再路由：问题（`questionDir`，v2.0 起内部按「未解决 /
已解决」切分）、项目（`projectsDir/<项目名>/`）、剪藏（位置由用户指令决定）、
日记、知识沉淀（`knowledgeDir/<类型>/`，类型由 agent 判定并交用户审核）。
**无收件箱**——判断不出类型时 agent 必须询问用户决策归属。
记录问题 / 项目联动写当日日志并追加根目录唯一待办文件（`todoFile`）。

问题具有**两阶段生命周期**（v2.0.0）：
- **解决**：从 `问题/未解决/` 移入 `问题/已解决/`（文件名 `YYYY-MM-DD 文件名.md`
  不变），标注 `created`（记录日期）/ `resolved`（解决日期）/ `status: done`，
  TODO 同步勾选（`task` 命令按行号操作）；
- **沉淀**（另行发起）：agent 判定知识类型交用户审核 → 创建 `知识/<类型>/`
  知识笔记（`YYYY-MM-DD 标题.md`，`type: knowledge` + `knowledge_type`），
  双向链接回原问题；原问题保留在已解决文件夹，不删除。

知识类型初始 7 类（经验 / 原理 / 工具 / 设计 / 规范 / 案例 / 模板），
**用到才建子目录**，未来可由 agent 动态添加并向用户确认。目录约定默认纯中文，
全部配置驱动可改。

### 1.4.2 操作日志（v2.0.0）

- 大知识库文件夹（vault 外）`log/YYYY-MM/YYYY-MM-DD.md`（配置 `logDir`）；
- **每次对知识库的操作**（新增 / 修改 / 删除 / 移动 / 沉淀 / 剪藏 / 读取 / 搜索）
  后追加一行记录；vault 外文件直接写，不纳入 HTML 镜像导出。

### 1.4.3 写入通道分层（v1.3.0）

- 常规长度内容：全量走 CLI（保持索引一致）；
- 超长内容（>4000 字符）：**创建动作仍走 CLI**（`create` 占位文件，注册索引），
  内容本体直接写文件（CLI 参数长度受限，例外清单第 5 条），随后回读校验；
- 二进制附件：直接复制（例外第 3 条）；JSON（.canvas）：直接写（例外第 1/2 条）。

### 1.5 HTML 镜像导出

- 每次写操作后的固定流程（新增 / 修改 → `export-one`；删除 / 移动 → `export` 含清理）；
- 镜像位置：`<exportRoot>/<vault名>/<相对路径>.html`，默认导出根在大知识库文件夹内；
- **仅生成 vault 级索引 `index.html`**（v1.3.0 起不再生成导出根级索引，历史残留
  自动清理）；
- 自写轻量 Markdown 转换器（Python 标准库）：覆盖 Obsidian Flavored Markdown
  常用子集；Mermaid 用 CDN 渲染、离线降级为可读代码块；目标"跨设备可读"，
  不追求与 Obsidian 渲染一致；
- 不依赖 Obsidian 运行（例外清单第 4 条）。

### 1.6 安全模型

| 动作 | 规则 |
|---|---|
| 创建 | 无需同意；写前 CLI search 相似检查，高相似交用户决策 |
| 修改 / 移动 / 重命名 | 先展示方案，用户同意后执行；优先 CLI 原生命令（链接自动更新） |
| 删除 | 仅 CLI `delete`（系统回收站）；禁用 `permanent`；前同意、后同步镜像 |
| Git | 仅提交（`git add -A -- .` + 中文简述）；永不 `git init`；非仓库跳过并提示 |

## 2. 模块职责

| 模块 | 职责 | 关键设计 |
|---|---|---|
| `scripts/kb_config.py` | 配置发现与读写、多 vault 管理、schema 迁移 | 原子写（临时文件 + replace）；init 拒绝写入 vault 内；validate 区分问题与警告 |
| `scripts/kb_env.py` | CLI 发现、Obsidian 运行检查与拉起、配置 / vault 校验 | CLI 发现顺序：配置 cliPath → PATH → 平台常见位置；拉起用 cliPath 同级 `Obsidian.exe`（macOS 用 `open -a`），轮询等待就绪 |
| `scripts/html_export.py` | MD→HTML 转换、镜像导出、索引生成、附件复制、孤儿清理 | 增量按 mtime；wikilink 以 basename→路径映射解析；Markdown 相对资源按 笔记相对→vault 相对→basename 解析 |
| `scripts/update_skill.py` | 发布辅助：检查 / 打包 / 提交 | 提交要求 skill 目录本身是仓库根（防止污染上层仓库）；永不 `git init`；打包仅含运行时文件，排除开发期文档（REQUIREMENTS.md / TEST-REPORT.md / CHANGELOG.md / DESIGN.md / .test-env / dist） |
| `assets/user-manual.md` | 最终用户手册模板 | 初始化复制到大知识库文件夹，已存在不覆盖 |
| `references/` | 渐进披露的细节文档 | CLI 速查、属性约定、Bases / Canvas 要点、回收站实测 |

数据流：用户意图 → agent 按 SKILL.md 工作流 → CLI（写）/ 脚本（配置、导出）→
vault → 操作后流程（updated 同步 → HTML 镜像 → 操作日志 → 看板反映确认 →
Git 提交 → 反馈）。

## 3. 兼容性策略

- 语义化版本；配置 schema 带 `version`，变更在 `kb_config.MIGRATIONS` 注册迁移函数；
- 每次发布前置条件：`CHANGELOG.md` 与 `DESIGN.md` 同步更新、兼容性检查通过
  （旧配置可读取或可迁移、vault 内容不受影响、已生成的用户手册不被覆盖）；
- 破坏性变更必须升主版本，并在 CHANGELOG / DESIGN 中说明迁移方案；
- 配置新增偏好键时，迁移逻辑做"缺省补齐、不覆盖用户已有值"。

## 4. 发布约定（§12）

1. 更新 `CHANGELOG.md` 与 `DESIGN.md`（`vX.Y.Z - 描述`，含兼容性说明）；
2. 兼容性检查（见上节）；
3. 测试：`quick_validate.py` + 脚本自测 + 真实场景 forward-test；
4. 打包：`update_skill.py package` 生成 `dist/obsidian-kb-vX.Y.Z-<timestamp>.zip`
   （仅运行时文件，开发期文档 CHANGELOG / DESIGN / REQUIREMENTS / TEST-REPORT 不随包分发）；
5. Git 提交：`feat:/fix:/docs: vX.Y.Z - 描述`（`update_skill.py commit`）；
6. **每次改动完成后自动执行发布（v2.0.1 起，用户拍板）**：完成任何变更后
   立即执行 `update_skill.py release`（check → package → commit），不再等待用户
   明确要求；版本号按语义化版本推进（patch：文档/小修正；minor：新功能；
   major：破坏性变更）。

## 5. 已知限制与决策备忘（v1.0.0）

- **打包纯净（v1.4.0 决策）**：分发包仅含运行时文件（SKILL.md、agents/、
  scripts/、references/、assets/）；CHANGELOG / DESIGN / REQUIREMENTS /
  TEST-REPORT 为开发期文档，由 git 管理，不随包分发（打包排除项见
  `update_skill.py` EXCLUDE_*）。内置参考技能 `references/skills/`
  （obsidian-markdown / obsidian-cli / obsidian-bases / json-canvas / defuddle）
  自 v1.4.0 起移除，能力说明收敛于 SKILL.md 与顶层 references/ 文档。
- **知识组织模型（v2.0.0 决策）**：问题按未解决/已解决切分，解决与沉淀分离；
  知识模块按类型子目录切分；剪藏/模板/附件/Bases/Canvas 为文件类型分类，
  位置以用户指令为准（不预设目录）；无收件箱、无归档；操作日志在 vault 外
  `log/` 按月/日切分；updated 精确到分钟；标签与双向链接为硬性要求。
- **TODO 折叠归档（v2.1.0 决策）**：勾选完成后条目移入 TODO.md 底部「已完成」
  折叠块（callout `[!success]-` 默认折叠），最新完成排最上；实现为 SKILL.md
  内联工作流（CLI read → 对比定位 → 重组 → `create overwrite`），不新增脚本。
- **自动化提醒（v2.2.0 决策）**：待办/日程含时间信号时自动创建定时提醒；**平台
  无关**——SKILL.md 只描述"用当前 agent 平台可用的自动化能力"，不写死任何工具
  （WorkBuddy 用其自动化工具，其他平台用等价能力）；强信号直接创建、弱信号询问。
- **日程模块（v2.2.0 决策）**：`日程/` 为内容模块（与问题/项目/日志/知识同级，
  scheduleDir 键）；日程笔记 `type: event` + `date`/`end`/`location`/`status` +
  `日程` 标签；状态变更即时写入（Bases 视图自动实时反映，及时更新）。
- **看板总览（v2.2.0 决策，v2.3.2 定稿）**：vault 根目录**「看板.md」+「看板.base」**
  两个文件（dashboardFile 键默认看板.md），命名统一为「看板」；`看板.base` 是数据源
  （`views` 数组承载各板块视图），看板.md 嵌入 `![[看板.base#视图名]]`；**Bases 是
  Obsidian 原生唯一实时聚合方案，必须有 .base 数据源**（看板.md 只是嵌入容器，
  无 .base 的实时聚合需第三方插件 Dataview 或手工维护静态列表，均不采用）；为
  **初始化可选组件**（用户同意才建）；**动态板块**——生成时只加载已有内容的模块，
  板块首次出现内容时自动增补视图；交互全 Bases 原生不依赖插件；数据随笔记属性
  实时反映、无需重建；美化用 CSS snippet（`.obsidian/snippets/`，编辑/阅读
  都生效，写 `.obsidian` 前征得同意）；**Bases 不支持 calendar 视图类型**
  （实测 1.13.4），日程一律 table；与"agent 日常按需创建 Bases 不固化模板"决策并行。
- **Obsidian 操作委托（v2.3.0 决策）**：SKILL.md 不编写 Obsidian 操作规范，改为由
  `@skill:obsidian-suite` 调度指导，各子领域查看 obsidian-cli / obsidian-markdown /
  obsidian-bases / json-canvas / defuddle 专用 skill（外部维护可及时更新）；
  references 仅保留实测经验与领域约定（标注仅供参考、需自行验证）；避免在本 skill
  内复制易过时的操作教程。
- **自测约定（v2.3.0 决策）**：测试库
  `D:\Peojects\MyProject\Skills\知识库skill测试\Obsidian测试知识库`（已注册）；
  每次更新后发布前跑真实 forward-test（见发布约定第 3 条）。
- CLI 非 headless：写操作需要 Obsidian 运行；`kb_env.py` 显式拉起兜底，
  失败时提示用户手动打开；
- Daily Notes 格式无专用 CLI 设置项：初始化用 `eval` 写插件设置并验证，
  失败给一次性人工指引；
- `.base` / `.canvas` 创建优先走 CLI `create path=...`；CLI 不支持时直接写文件
  （例外并说明），再用 `base:query` / `json.load` 校验；
- Markdown 转换器为子集实现：脚注定义为纯文本降级、数学式等宽降级；
- 本机系统 `python` 可能不存在：SKILL.md 规定解释器发现顺序
  （PATH → `py -3` → WorkBuddy 受管运行时）。
