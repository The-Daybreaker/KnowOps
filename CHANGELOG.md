# CHANGELOG

本文件记录本仓库的版本历史。格式遵循语义化版本；每次发布的兼容性说明见对应条目。
（v1.0.0 之前及旧版 obsidian-kb 时期的条目已删除，不再保留；早期演进可从 git
历史追溯。）

> 说明：本文件是 KnowOps 的完整版本历史，随发布仓公开；格式遵循语义化版本，
> 每次发布的兼容性说明见对应条目。

## [3.0.6] - 2026-09-06

### 知识条目形状定版：编号段落式（用户拍板，文档全链对齐）

- **决策**：v3.0.4 挂账的条目形状不一致，用户拍板以编号段落式为准——章节下
  每段「一、二、三、」编号，一段写一条经验或结论（写清结论、动机与背景）；
  不分「原话」和「补充」，原话原样保留、不提炼、不改写；agent 补写背景或
  动机经用户同意后作为后续编号段落写入；单章约 30 段涨破。
- **对齐范围**：workflow.md「文档形状」「原话完整」（废除「### 条目标题」
  「补充」小节与「与原话在文内可区分」条款）、properties.md「知识」、用户
  手册模板「分类规则」「条目写法」等四处，测试库手册副本与变更记录同步；
  原话完整原则不变。
- **既有文档不做迁移**：用户数据不动；写入前健康检查兜底（发现旧形状先问
  用户是否整理）。

## [3.0.5] - 2026-09-06

### 仓库结构迁移：通用项目模板 + skills-dev spec（产品内容零改动）

- **动机**：通用项目模板（init-project / project-spec v1.0.0）发布，本项目结构
  先于模板形成；按用户指示整体迁移到模板结构并接入 skills-dev 工作流。
- **双层结构**：仓库根 = 协作层（私有 git，无远端，冷启动入口 AGENTS.md 协作
  总纲）；`workspace/` = 发布层（嵌套公开仓，即本仓库；公开内容路径零变化——
  README / skills / tools / .github 对使用者与 CI 完全同构）。
- **落点迁移**（按 skills-dev spec 落点）：决策记录 `context/adr`、设计
  `context/design/design.md`、测试记录 `context/test/TEST-NNNN`、想法池
  `context/vision.md`、讨论与过程留档 `archive/discussion` 与 `archive/design`、
  审计归档 `archive/audit`、agent 记忆 `process/memory.md`；发布脚本
  `tools/release.py`（协作层，含机器专属安装清单，不入公开仓）；版本历史
  （本文件）转入发布仓公开。
- **工作流**：拉取 `spec/skills-dev`（vision → design → development → test →
  audit → release，adr 横切），release 阶段项目化填充 KnowOps 自动发布链。
- **脚本适配**：check.py（探测逻辑改为「协作层 test/ 可达性」决定全量/核心
  模式；P1 分档对象与审计护栏路径、P5 dist 路径、C7 必备忽略条目更新）；
  release.py（协作层/发布层双锚点，dist 落点 `workspace/dist/`）。
- **产品（skills/）内容零改动**：本版无任何 skill 行为变化；v3.0.4 挂账事项
  （模板示例与 workflow/手册条目形状描述不一致）仍待用户决策。

## [3.0.4] - 2026-09-06

### 主题文档模板示例段改写（用户上会话改动，本版按用户指示提交发布）

- **改动**：`assets/templates/主题文档模板.md` 示例段由「结论标题条目 + 原话/
  补充分节 + 用法注释块」改为「编号段落式」——正文每段用一、二、三编号，一段
  写一条经验或结论（写清结论、动机与背景）；不分「原话」和「补充」，怎么说的
  就怎么记，原样保留，不提炼、不改写；单章超过约 30 段时 agent 提议拆分。
  原话完整原则不变；frontmatter 与 `{{date}}` 占位符未动。
- **已知不一致（挂账待用户决策）**：workflow.md / 用户手册 / properties.md /
  SKILL.md 中知识条目形状仍描述「结论标题 + 原话 + 可选补充小节」，与新模板
  示例的编号段落式不一致。对齐属产品语义变更，本版按用户指示原样发布模板
  改动、不连带改运行时文档；后续是否对齐、向哪边对齐由用户定。
- 测试库模板副本已同步（P4 逐字一致联动）。

## [3.0.3] - 2026-08-30

### 全面审查修复：文档同步收口 + 发布链分支推送核验实化（用户确认执行）

- **动机**：全面审查（逐文件通读 + 脚本实测）发现 v3.0.1/v3.0.2 两轮快速发布
  遗留两类问题——文档同步滞后（含 1 处运行时文本）与「声明已做、实现无落点」，
  本版一次收口。
- **修复**：
  - **R1 运行时文本**：init-config 初始化向导第 2 步懒加载句残留「01 知识
    （示例主题文档）」（v3.0.1 已删示例主题，CHANGELOG 当时声称已同步
    init-config，实际漏改），改为与 workflow/properties 一致口径——初始化
    预置 03 系统（用户手册、模板），01 知识、收件箱、归档首次写入时自动
    出现（01 知识起步为空，按模板形状创建）；
  - **D1 审计档案断链**：v3.0.2 声明「文本一致性审计归档 dev/AUDIT.md
    [3.0.2]」但 AUDIT.md 实际无该节——本版依 CHANGELOG 在案记录补建 [3.0.2]
    节（附补记说明），并在 check.py P1 新增护栏：CHANGELOG 条目引用的
    AUDIT.md [版本] 章节必须存在，缺失即 error；
  - **D2/D3 开发文档滞后**：private/AGENTS.md（正文当前版本 3.0.1→3.0.3、
    测试库基建行去除 agent-rules.md、发布流程与文档职责表去除
    knowledge-example）；DESIGN.md（模块预置表述改「01 知识起步为空」、
    模板联动清单与开发规范 10 去除示例主题/knowledge-example、打包描述改
    「everywhere-note 单文件」、文档职责表称谓对齐）；
  - **D4 check.py 输出文案**：P4 通过文案「笔记模板 2 份 + 示例主题」与实际
    校验（1 份模板 + 防复现护栏）不符——模板清单提为 P4_NOTE_TEMPLATES 常量
    （循环与文案共用），文案如实化；文件头检查项清单同步；
  - **X1 发布链实化**：release.py 新增发布收尾步骤「推送当前分支并核验远端
    HEAD 与本地一致」（SSH 失败降级 HTTPS + GH_TOKEN；--skip-push 一并跳过；
    push 对已同步分支天然幂等；核验不等即报错停）。v3.0.2 曾声明「本版起
    发布收尾固定执行分支推送并核验」，实际无落点，本版补实；DESIGN 工作流
    与 private/AGENTS.md 发布流程步骤清单同步；
  - **TEST-REPORT 历史清空**（用户要求）：删除 v3.0.2 及更早的历史测试记录，
    本文档只保留当前版本——与头注「只记录当前版本」声明一致（顺带消除
    v2.0.3 重复标题行）；
  - **发布实战修复**：install() 安装目录替换对 OSError 无防护（既有缺口，
    发布实跑中千问办公目录被占用 WinError 5 显形）——修复为优雅 die（替换
    半途失败先回滚恢复旧安装，附幂等重跑指引），旧版本清理失败降级 WARN。
- **涉及文件**：skills/knowops/references/init-config.md、tools/check.py、
  private/dev/tools/release.py、private/AGENTS.md、private/dev/DESIGN.md、
  private/dev/AUDIT.md（[3.0.2] 补记 + [3.0.3] 审计节）、CHANGELOG、
  TEST-REPORT、两 SKILL.md（版本 3.0.3）、测试库 config（版本 3.0.3）。
- **兼容性**：无破坏性变更。init-config 为初始化向导描述性文本修正；
  check.py 为输出文案 + P1 新增护栏（私有检查项，CI --core 不受影响）；
  release.py 新增收尾步骤（行为新增非破坏，--skip-push 可跳过）。
- **测试**：check.py 全绿（版本链 3.0.3，含 P1 新护栏）；skills/ 内
  「示例主题」grep 零命中；测试库 vault_check 巡检 error 0；release.py
  --dry-run 与发布实跑（分支推送 + 远端 HEAD 核验）通过；--dist 3.0.3 复核。
  代码审计（check.py + release.py，1 中危 + 4 低危全部当场修复）归档
  dev/AUDIT.md [3.0.3]。

## [3.0.2] - 2026-08-30

### agent-rules 并入用户手册「agent 约束」章节（用户提出）+ 分支推送遗漏修复

- **动机**：`.config/agent-rules.md` 在隐藏目录，用户看不到也难改；用户要求
  并入用户手册单开一章，方便了解和修改——与「单一事实来源」理念一致。
- **变更**：
  - 用户手册模板新增**「八、agent 约束」章节**（插件集成规则 / 本库额外红线 /
    默认流程之外的操作要求 / 旧库/特殊结构约定，头注说明与第二章的分工）；
    手册自此同册承载内容规则（模块规则）与行为约束（agent 约束）；
  - `.config/agent-rules.md` **废除**（skill 资产 `assets/agent-rules.md`
    删除）；bootstrap（SKILL 前置第 4 步）、红线 7、workflow「03 系统」与
    「操作后流程」、redlines（配置引导/git/插件规则/安全边界）、init-config
    （向导第 7 步、插件集成、旧库接入结论落点）、desktop-ingest 头注与写入、
    automation-prompt-template 全部改为读/写手册「agent 约束」章；旧库遗留
    该文件走现场确认并入手册，不自动迁移；
  - check.py P4 用户手册校验从逐字改为**章节锚点**（模板全部 `## ` 标题须在
    副本逐一存在）——副本是初始化填充形态，逐字比对不再成立；agent-rules
    资产加入防复现清单；README 双语、根 AGENTS.md、DESIGN 同步。
- **发布链修复**：v3.0.0/v3.0.1 两次**分支推送遗漏**（release.py 只推 tag，
  分支 push 按工作流由 agent 完成，此前漏推导致 GitHub README 未更新）——
  已补推 master；本版起发布收尾固定执行分支推送并核验。
- **测试**：check.py 全绿；测试库手册并入章节八（8 章锚点校验通过）+ 隐藏
  agent-rules.md 删除；grep 全仓无 agent-rules 引用残留（防复现清单除外）；
  文本一致性审计归档 dev/AUDIT.md [3.0.2]。

## [3.0.1] - 2026-08-30

### 用户复核反馈修复：随身材料精简 + Release 产物补全（8 项，用户逐条提出）

- **automation-prompt-template 随 Release 分发**：release.py 打包步骤新增
  `pack_automation`——把 `skills/automation-prompt-template.md` 复制为 dist
  附件 `automation-prompt-template-v<version>.md` 随 Release 上传（幂等补传）；
  check.py P5 新增校验（存在 + 与源一致）。README/根 AGENTS 同步注明。
- **随身端不做任何入库判断（契约收紧）**：`capture_kind` 字段从随身端流程与
  属性约定中整体移除（v2 起为「松提示」，用户裁决其仍属入库判断）——
  everywhere-note 重构为**单文件 SKILL.md**（流程/条目形状/红线全部内嵌，
  删除 references/mobile-capture.md 与 assets/capture-template.md）；
  desktop-ingest 契约头注改为 `type/created/tags/标题`，历史字段
  （capture_kind）容忍照读、缺失不补、不作任何判定；properties 属性表移除
  capture_kind 行；测试库收件箱既有 capture_kind 条目保留作兼容回归样本
  （实测新旧两格式均正常入库/豁免）；看板「收件箱-待沉淀」视图移除
  capture_kind 列。契约同步对象由 mobile-capture.md 改为 everywhere-note
  SKILL.md。
- **skill 资产精简**：删除 `assets/knowledge-example/`（示例主题与
  主题文档模板重复）与 `assets/templates/摘录长篇模板.md`（摘录是登记的扩展
  模块，skill 不预置其工具件）；`assets/templates/` 只留主题文档模板；
  知识模块起步改为「为空，首次写入时按模板形状创建」（workflow/properties/
  init-config/手册/check.py P4 同步，P4 另加「已移除资产不得复现」护栏）。
- **README 清理**：删除 Roadmap（未来方向迁入 DESIGN「未来方向」节，不再
  写入用户可见文档）；模板/目录树/快速开始等残留更新；双语同步。
- **官方工具 skill 安装指引入文**：SKILL.md 前置第 1 步与红线 8、redlines
  「工具纪律」补安装来源——kepano/obsidian-skills 仓库，把对应 skill 目录
  复制到用户级 skill 目录（与 knowops 安装方式相同），用户同意安装时按此执行。
- **__pycache__ 排查**：zip 产物与 6 平台安装目录实测干净（release.py 打包与
  安装拷贝本就双向排除）；源目录一处 `skills/knowops/scripts/__pycache__` 为
  审计实验 import 产生的字节码缓存，已删除（未跟踪、不进 git/zip）。
- **测试**：契约回归（新格式入库 + 旧格式容忍）、check.py 全绿、发布后
  `--dist 3.0.1` 复核（含自动化模板附件）；审计见 dev/AUDIT.md [3.0.1] 节。

## [3.0.0] - 2026-08-30

### 单一事实来源改造：模块定义从 skill 移入知识库（用户提出的理念改造）

- **动机**：v2 的模块定义（职责/流程/属性枚举/命名）内置在 skill 每一层，
  库结构每动一次就要发一版 skill。v3 把 skill 收敛为「通用工作流 + 基础框架」，
  模块规则的唯一事实来源改为库内用户手册——改规则只改手册，不发新 skill。
- **核心变更**：
  - **通用地基 + 扩展模块登记制**：基础模块削为四个（收件箱/知识/系统/归档）+
    根目录看板；新增模块 = 用户在库里新建文件夹 → agent 问清规则 → 写进用户
    手册「模块规则」章节 + config `preferences.modules` 登记 + 看板补视图 +
    编号顺延（用户坚持原名以用户为准）；agent 以库中实际存在且已登记的文件夹
    为准；未登记目录不动不判错（vault_check 只 warning）；模块目录被删除时
    问询注销（手册章节同步删除或标注停用由用户定）。
  - **用户手册 = 单一事实来源**：手册「模块规则」章节置于第二章（用户要求
    靠前），每模块固定四小节（职责/入库规则/分类规则/命名约定），条目式短句
    可对照执行；用户可见可编辑且 **agent 必读**（bootstrap 第 4 步改写），
    「用户手册 agent 不读」条款废除；摘录规则整块从 skill 迁入手册摘录节。
  - **摘录降级为第一个扩展模块**（方案 A）：规则预写进手册模板标注示例；
    初始化询问是否启用，不启用则不建目录不登记（手册节保留作示例）。
  - **agent 职责边界**：格式整理 + 系统运营 + 按用户指令的内容写入，不代运营
    内容；分类按手册规则执行，规则覆盖不了才问用户。
  - **写入审计闭环**：内容写入后两笔账——日记详细记录 + 收件箱
    `待审阅-YYYY-MM-DD.md`（一批/一次对话一份、`type: capture`、看板不排除、
    删除后视图行自动消失、HTML 不导出、沉淀跳过、不参与序号计算）。
  - **原话不可侵犯**（两 skill 一致）：不得改写/压缩用户原话，原话完整记录；
    知识条目「提炼一层（不存对话原文）」废除，改为原话完整 + 可选「补充」
    小节（按用户要求/经同意）；语音转文字明显错字修正是唯一例外。
  - **日记改版**：遵循 Obsidian Daily notes 核心插件规则（位置+日期格式按插件
    设置，年切分用 `YYYY/YYYY-MM-DD`）；每日一文件分「用户/agent」两章，agent
    章固定七小节（入库/沉淀/整理/归档/删除/补记/系统）；用户无日记的改动由
    agent 依文件历史与 git 补记（注明推断依据）。
  - **类型校验口径**：基础枚举收缩为五值（capture/knowledge/daily/archive/
    system，excerpt 随登记）硬校验；登记模块按 config type 校验；未登记目录/
    type 只 warning。
- **破坏性**：config schema（preferences 五个目录键收敛进 `modules`
  `{dir,name,type,base}`）；日记格式改两章节；知识条目形状改原话制；type 枚举
  收缩；**不做迁移兼容**（沿用 v2.0.0 先例，旧库接入走现场确认安全底线；
  README 不写不兼容字眼）。
- **涉及文件**：knowops（SKILL.md、references 5 份、用户手册/主题文档模板/
  示例主题、vault_check.py、html-export.json）；everywhere-note（SKILL.md、
  mobile-capture.md、capture-template.md）；automation-prompt-template.md；
  tools/check.py（C2 基础骨架/C6 收缩/P2 modules/P3 登记类型放行/P4 modules
  取目录）；根 AGENTS.md、README 双语；测试库整体升级（config modules、手册
  副本、日记两章节、daily-notes.json 修正——其 v1 残留指向
  `01 生活系统/日记` 已改为 `03 系统/日记`）。
- **测试**：check.py 全绿；测试库 vault_check 巡检（含未登记目录 warning 注入
  实验）；真实场景测试见 TEST-REPORT v3.0.0；审计归档 dev/AUDIT.md。

## [2.0.3] - 2026-08-29

### 变更记录迁入 .config（用户提出）+ 归档记录边界收窄

- **动机**：变更记录与日记作用看似重合的根源，是「归档动作记入变更记录」这条
  与其章程（只记结构与规则的重要变更）矛盾的规则；同时变更记录是低频文件，
  不应占用 `03 系统/` 的用户可见空间。用户确认两项调整：
  - **变更记录迁入 `.config/变更记录.md`**：`03 系统/` 用户文档只留用户手册
    （1 份）。隐藏目录使变更记录不进 Obsidian 文件树、不参与 HTML 导出、不被
    vault_check 扫描（均由既有规则天然生效，脚本无改动）；`assets/system-manage/`
    定位改为「库自身文档模板」（用户手册 → `03 系统/`；变更记录 → `.config/`），
    模板头注更新（说明位置与维护方式，并顺带修正「改为版本号」的悬空指引）。
  - **归档记录边界收窄**：单篇归档只记日记；仅**结构性调整**（整目录批量调整、
    模块级变化）另记 `.config/变更记录.md`。workflow/properties 同步。
- **涉及文件**：workflow.md（4 处）、properties.md（目录模板/要点/生命周期）、
  init-config.md（初始化第 7 步拆分两处复制、导出说明、反馈汇总）、redlines.md
  （安全边界 2 处）、用户手册模板（「结构变更有据可查」改新位置）、变更记录
  模板（头注重写）、根 AGENTS.md（约束收口/skill 结构约定）、README 双语
  （目录树注释）；tools/check.py P4（变更记录比对目标改 `.config/`）；测试库
  （变更记录 mv 至 `.config/`、手册副本同步、日记与变更记录各补一条、config
  version 2.0.3）。
- **兼容性**：无配置 schema 变化、无契约变化。旧库的 `03 系统/变更记录.md`
  不自动迁移（沿用「不自动迁移、现场确认」安全底线）；升级后建议现场与用户
  确认是否移动。`03 系统/` 从 2 份用户文档变 1 份，属布局变化非破坏性。
- **测试**：check.py 全绿（P4 改 `.config` 比对目标后）；测试库 vault_check
  巡检、全量导出回归（变更记录不再出现在镜像、用户手册正常导出）；子 agent
  代码审计（check.py P4 改动）+ 文本一致性核查。详见 TEST-REPORT v2.0.3。

## [2.0.2] - 2026-08-28

### 第二轮对抗性审计修复（三红队子代理）+ 安装目标候选清单规范

- **审计**：用户发起的第二轮全面对抗性审计。三个红队子代理并行——红队 A 攻击
  规范流（10 攻击角度，纯文本）、红队 B 攻击运行期脚本边界（10 项实验，
  vault_check/html_export）、红队 C 攻击开发链（10 攻击角度，check.py/release.py/
  ci.yml/隐私门禁，含实验）。全部发现由 agent 逐条甄别（A 队引文逐条比对原文；
  B/C 队实验证据复核），成立 31 项全部修复（文本 14、运行期脚本 10、开发链 7），
  处置归档 `dev/AUDIT.md`。
- **文本修复（要点）**：desktop-ingest 入库核验与「收件箱豁免」表述统一
  （[EXEMPT] 摘要照常扫读＋回读）；旧格式条目解析通路裁决（有 frontmatter 走
  规范条目、无则按非规范文本包装）；短篇四分类「固定」改「默认可扩展」，集合类
  改动落点改库内本体＋变更记录（不再发明配置键）；「沉淀后删除原收件箱文件」
  限定已离箱条目；随身端删除「收件箱平铺」结构内嵌；SKILL.md 前置步骤重排
  （工具 skill 可用性检测提前至第 1 步，消除与红线 8 的顺序矛盾）＋加载表补
  redlines 必读情形；automation 模板补序号 99 三位与配置化路径、红线与移动操作
  冲突消除；README 双语入库表述与加载链对齐。
- **运行期脚本修复（随 skill 分发）**：html_export——BOM 击穿 frontmatter
  （改 utf-8-sig）、export-one 绕过导出范围（被排除文件返回 excluded 不落盘）、
  exportRoot 在 vault 内时镜像自吞（扫描排除镜像根子树）、GBK 控制台崩溃
  （stdout/stderr reconfigure）、表格转义竖线切列、标点标题锚点落空、图片 alt
  引号注入（全局转义补 quote）、exclude 反斜杠跨平台归一、单篇读取失败不中断
  （failed 列表）；vault_check——中文属性键整篇误判（键名正则放宽 Unicode）、
  check 传目录/不存在路径静默豁免改 fail-closed。
- **开发链修复**：check.py C6 扩展为「type 枚举＋必填表」双源同步
  （properties.md「必填与自由」结构化为权威定义表，修复 DESIGN 声称与实现漂移）；
  C7 隐私门禁补 UNC 路径、sk-proj/sk-ant 形态、正斜杠豁免归一、退化扫描按目录
  排除；P5 源清单与 release.py 打包排除口径对齐（.DS_Store 等 junk 文件）；
  release.py——git porcelain 引号形态绕过（改 -z 解析）、zip 复用改清单级校验、
  同版本旧附件告警。
- **安装目标候选清单规范（用户提出）**：安装目标改「候选清单（全集）＋安装时
  探测」——release.py 按清单逐个探测 agent 主目录，不存在的 agent 自动跳过
  （不报错、不创建目录）；清单列全本机 agent 平台（开始菜单＋主目录盘点：
  ZCode/Codex/WorkBuddy/Trae CN/Qoder CN/千问办公 安装，DSH/QoderWork 标记
  不安装），增删流程成文（private/AGENTS.md「安装目标」）。
- **兼容性**：无配置 schema 变化、无模块/契约变化。两处行为变化均属缺陷修复：
  vault_check check 对目录/不存在路径从静默豁免改为 FAIL（fail-closed）；
  export-one 对被导出范围排除的文件从照常导出改为 no-op（status=excluded）。
- **测试**：check.py 全绿；C6 必填表漂移注入实验检出；脚本回归（BOM/excluded/
  镜像自吞/GBK 控制台/中文键/退出码契约）全过；测试库 vault_check 巡检 error 0；
  测试库脚本副本与模板同步。详见 TEST-REPORT v2.0.2。

## [2.0.1] - 2026-08-28

### 对抗性审计修订（双红队子代理，甄别后两处成立）

- **背景**：v2.0.0 发布后按用户要求做全面对抗性审计——两个轻量模型红队子代理
  并行（规范流矛盾攻击 / 脚本边界攻击），报告由 agent 逐条实验甄别，处置归档
  `dev/AUDIT.md`。
- **成立并修复（2 处，均在工作流文档）**：
  - 涨破拆分补命名约定：文件夹＝主题名、主文档保留原名移入（`主题名/主题名.md`）、
    拆出文档以章节名命名、来源小注为纯文本无断链风险；
  - 晋升条目合并补同名冲突裁决：库内多份同名主题文档时不猜、交用户定夺。
- **证伪/驳回要点**：脚本类指控两项经实验证伪（绝对路径+中文+空格全过；
  --json 错误输出为合法 JSON 且 exit 1）；收件箱子目录豁免属宽进设计意图；
  C6 枚举正则已有 fail-loud 兜底；`{{date}}` 替换在 init-config 第 9 步已明示
  由执行者完成；序号「最大值＋1」定义上不可能冲突。
- **兼容性**：无破坏性变更；纯文档措辞澄清，无流程/结构/契约变化。
- **测试**：拆分场景回归——测试库既有拆分产物（拆分测试/拆分测试.md +
  拆分测试/大章节.md）与新命名约定逐字吻合；check.py 全绿；四平台重装校验。

## [2.0.0] - 2026-08-28

### 全面改造：十模块体系削为五模块轻量体系（破坏性变更，用户逐节确认）

- **背景与动机**：真实使用中「不知道往哪放就不放了」——写入时要求太多（切场所、
  判归属、守规范、欠整理债），且生活/资产/规范/项目等模块的内容在库外都有更合适
  的家，库内副本付同步成本还会过时。改造主线：库只收「没有更具体去处」的内容。
  完整需求与设计过程见 `dev/` 下四份过程文档：两轮讨论记录（项目锚定沉淀、
  全面改造第二轮）、《SPEC-2026-08-28-全面改造设计-v2》、
  《PLAN-2026-08-28-v2全面改造》。
- **宪法原则确立**：两道门（归宿门/形态门；形态门由模块准入五条件在架构根源保证：
  规模/生命周期/工作流/可 md 原生承载/符合用户心智）；宽进严出（规范只约束
  agent，用户手写零要求）；先单体、涨破再拆；记录质量把关（详实通俗、写明动机、
  不精简用户信息、无 AI 味）；保留判据（真实数据流）。
- **模块体系**：00 收件箱（平铺、序号命名、校验豁免）/ 01 知识（主题文档、章节制、
  单章约 30 条涨破拆分）/ 02 摘录（机制不变）/ 03 系统（日记＝操作日志按年切分、
  模板、看板.base、用户文档）/ 04 归档；系统、归档固定末两位；根目录 `看板.md`
  一屏总览（看板不再是模块）。**移除**：生活系统（任务/问题/日程/手写日记）、
  资产系统、规范系统、项目系统、任务双轨。
- **收件箱**：子目录（随手记/灵感/待整理内容/摘录）废除；文件名 `序号-内容简述`；
  沉淀五去向（知识/摘录/归档/删除/保留）由内容判定。
- **类型系统**：type 枚举 16 → 6（capture/knowledge/excerpt/daily/archive/system）；
  capture_kind 降级为松提示；知识属性载体改为主题文档（knowledge_type/domain 退场）。
- **系统模块**：日记＝操作日志（`.config/log` 撤销）；用户文档 5 并 2（总用户
  手册——按认知规律编排的质量点名工程——＋变更记录）；新增 `03 系统/模板/`
  （主题文档/摘录长篇模板，接 Obsidian 核心插件 Templates，`{{date}}` 变量）与
  知识模块示例主题文档（通用去个人化）。
- **脚本**：vault_check 收件箱豁免、非 md（含 .canvas）跳过、模板目录跳过、
  末两位校验；html_export 默认排除日记/模板/白板；check.py 模块/配置键/模板联动
  （含笔记模板与示例主题）全面跟随。
- **随身端契约**：文件名契约改一句话标题（无日期前缀）；废除「建议归属」；
  确立随身端稳定原则（不内嵌任何桌面库结构信息，桌面结构变更不要求随身端重装）。
- **兼容性**：不做任何迁移兼容——无迁移对照表、无旧格式兼容逻辑；旧库接入走既有
  「不自动迁移、现场确认」安全底线；README 不写不兼容字眼（用户决定）。
- **文档**：README 双语、根 AGENTS、automation-prompt-template、private 开发文档
  全套同步；测试知识库按新骨架整体重建，暂存库按新契约重造。
- **测试**：见 TEST-REPORT v2.0.0（场景清单 11 项；Obsidian CLI 场景待发布前
  补测，本轮环境未运行）。

## [1.2.14] - 2026-08-27

### 全面审计后的文档一致性修正（用户提出）

- **背景**：对仓库做全面审计（不依赖 git），确认删除敏感信息未造成功能破坏；但发现
  若干历史遗留的文档编号/版本滞后（v1.2.9 模块重编号、v1.2.12/1.2.13 发布时个别
  文档正文未同步）。
- **修正**：
  - 根 AGENTS.md「skill 内部结构约定」：`assets/system-manage/` 模板归属由
    「08 系统管理」更正为「09 系统管理」（2 处）；
  - properties.md GitHub 暂存库说明：「本地 07 归档 不重复存放」更正为
    「本地 08 归档 不重复存放」；
  - private/AGENTS.md 正文「当前版本：1.2.11」同步为 1.2.14（frontmatter 已升）；
  - .workbuddy/memory/MEMORY.md（C 区）刷新：当前版本 v1.2.14、通用红线 8 条、
    脚本清单（html_export.py + vault_check.py）、09 系统管理编号、结构校验改
    tools/check.py；
  - 测试库 HTML 镜像：全量导出清理 3 个已删除测试笔记的残留页面。
- 两 SKILL.md 版本 1.2.14。
- **兼容性**：无破坏性变更；纯文档/编号一致性修正，无流程/结构/契约变化。
- **测试**：确定性校验 tools/check.py 全绿；本次涉及 skills/ 运行时文件
  （properties.md），真实场景测试按规则待发布前执行（本轮未发布）。

## [1.2.13] - 2026-08-20

### 工具纪律 --help 措辞歧义修正（用户提出）

- **问题**：v1.2.12 redlines.md「不用 `--help` 试探」把 `--help` 本身列为禁项，
  与官方 obsidian-cli skill 自身「用 `--help` 查看具体命令语法」的指引冲突，
  agent 读到两条冲突指令时可能困惑或按偏好绕过闸门。
- **修正**：语义分层——「官方 skill 已加载且其指导用 `--help` 查语法」属遵循
  官方指引，照做即可；禁止的是**绕过 skill 的自行探索**（未加载 skill 就凭
  记忆猜参数、以 `--help` 试探代替加载 skill、网络搜索替代官方指引）。
- 两 SKILL.md 版本 1.2.13。
- **兼容性**：无破坏性变更；纯措辞澄清，无流程/结构变化。

## [1.2.12] - 2026-08-20

### 官方工具 skill 约束改程序性闸门（用户提出）

- **问题**：「具体语法与命令以官方工具 skill 为准」原为声明式软约束，agent 执行
  Obsidian 操作时常跳过加载规则、凭记忆或网络搜索自行猜测 CLI 语法，约束失效。
- **改法（声明式 → 程序性，三处闸门）**：
  - SKILL.md 前置新增第 5 步「检测官方工具 skill 可用性」：从环境 skill 列表
    或安装目录确认 obsidian-cli 等 5 个官方 skill 哪些可用并记录，检测不到时
    问用户（不默认未安装）；
  - SKILL.md 通用红线新增第 8 条「Obsidian 操作以官方工具 skill 为准」：操作前
    核对可用性记录——已安装必须加载遵循；未安装先与用户确认兜底（安装或
    help.obsidian.md），确认前不开始操作；根 AGENTS.md 红线清单同步第 8 条；
  - redlines.md 新增「工具纪律（官方 skill 优先）」小节：已安装 skill 时禁止
    凭记忆猜参数 / `--help` 试探 / 网络搜索替代；用户明确同意自行探索时按指示
    执行、失败即回报不重试轰炸。
- 两 SKILL.md 版本 1.2.12。
- **兼容性**：无破坏性变更；纯流程纪律强化，无目录/属性/契约变化。

## [1.2.11] - 2026-08-20

### 全方位审计修复 + 审计环节固化（用户提出）

- **审计（子 agent 并行：代码 / skill 文本 / 结构）**：对 v1.2.10 新增的 4 个
  脚本/流程文件（check.py / vault_check.py / release.py / ci.yml）与 skill 文本
  做全方位审计，发现 7 高危 + 13 中危，全部修复；skill 文本审计发现 4 处，全部
  修复；报告归档 `dev/AUDIT.md`（新增文档，触发式更新、版本允许滞后）。
- **release.py（高危修复）**：凭据改经 GIT_CONFIG 环境变量传递、输出统一脱敏；
  版本参数与 SKILL.md 一致性前置检查；幂等改「完成即跳过」（zip 完整性复用/
  Release 附件补传）；--proxy/KNOWOPS_PROXY 代理注入；原子打包与安装前临时
  目录校验。
- **check.py（高危修复）**：C2 模块表重号检测（原始行序查重）；C6/P3 枚举提取
  单一定义点 load_type_enum()，失败即报错不再静默空集；safe_read/read_fm 统一
  读取异常处理；P1 严格/滞后分档并纳入 AUDIT.md；P2 编号重复与后三位名称错位
  检测；P5 全量 zip 逐份校验 + --dist 版本格式校验。
- **vault_check.py（随 skill 分发，高危修复）**：UnicodeDecodeError 捕获（坏编码
  文件不再使巡检崩溃）；frontmatter 支持块式列表（`tags:` 换行 `- 项`）；解析
  错误带行号；必填属性非空检查（缺失与空值都算问题）；check-vault 增加必填属性
  覆盖（与 check 模式同一套规则）。
- **ci.yml**：timeout-minutes、permissions: contents: read、workflow_dispatch。
- **skill 文本修复**：workflow.md「07 归档」笔误更正、短篇四分类统一为可配置；
  知识库架构.md 移除 agent 侧文档交叉引用（用户文档自洽）；提示词模板示例去
  个人 GitHub 用户名。
- **工作流固化（用户确认）**：开发工作流第 5 步新增触发式审计环节——涉及脚本/
  代码时派子 agent 代码审计、skill 文本大范围调整时加文本审计，报告归档
  dev/AUDIT.md；完成检查清单与 private/AGENTS.md 同步更新。
- 两 SKILL.md 版本 1.2.11。

## [1.2.10] - 2026-08-20

### 确定性校验体系 + 规范/配置分层（用户提出）

- **开发期脚本政策更新（用户确认）**：md 驱动为主、确定性脚本辅助；开发期保留
  必要且有效的脚本，不再严格要求无脚本；发布机械动作脚本化的前提是副作用可控
  （dry-run 预演、幂等前置检查、失败即停、绝不覆盖已有产物）。
- **`tools/check.py`（A 区，开发期校验，PyYAML）**：核心项 C1–C6（CI 可跑：两
  skill 版本一致、模块表编号与后三位、引用完整性、JSON 可解析、README 双语模块
  引用、vault_check/properties 枚举同步）+ 私有项 P1–P4（版本链与开发期文档
  frontmatter 分档、测试库目录与 config 匹配、测试库笔记扫描、模板联动）+
  `--dist` 打包完整性复核；private/ 不存在时自动按核心模式运行（CI 用）。
- **`skills/knowops/scripts/vault_check.py`（运行期，随 skill 分发，标准库）**：
  操作后核验的结构面（frontmatter 可解析/必填属性/type 枚举）交脚本输出键值
  摘要，agent 扫读摘要 + 批量（≥3 篇）时抽 1 篇全文回读；`check-vault` 全库
  巡检用于巡检/迁移前/升级后；语义面维持 agent 原要求（结构面/语义面分工为
  用户确认）。
- **CI（`.github/workflows/ci.yml`）**：push/PR 触发 `check.py --core`，兜底拦截
  agent 忘跑校验或换机提交；不替代本地全量与真实场景测试。
- **`dev/tools/release.py`（B 区发布脚本）**：从 tag 开始的机械动作（tag/push/
  打包/Release/四平台安装），dry-run 预演、幂等前置检查、失败即停、绝不覆盖
  已有产物；git commit（主仓库与 private 子 git）仍由 agent 完成。
- **规范/配置分层声明（用户确认归属）**：workflow.md 新增「规范与配置的边界」
  小节、知识库架构.md（模板与测试库副本）新增「固定规范与可配置项」、
  properties.md 增分层标注——规范层（固定，改动即破坏性变更）：模块编号规则
  与后三位、收件箱优先路由与分类原则、懒加载策略、操作后流程与红线、type
  枚举语义与必填纪律、任务双轨、短篇「分类聚合+超量拆分」机制、归档按日期
  切分（中文补零）；配置层（确认即改并记变更记录）：preferences 目录名、
  日记日期格式、导出开关与位置、githubSync、看板视图集合、短篇四分类集合、
  长篇分类文件夹集合。
- **开发期文档 frontmatter 化（用户确认）**：private/AGENTS.md、dev/DESIGN.md、
  dev/TEST-REPORT.md 顶部 frontmatter 记录 `version`（= 当前版本）；CHANGELOG
  以顶部条目为准；DESIGN 允许滞后（warning 提示）。
- **文档与流程接入**：workflow.md 操作后核验流程改写（结构面脚本摘要 + 语义面
  agent）；init-config.md 脚本复制步骤接入 vault_check.py；desktop-ingest.md
  核验话术同步；两 SKILL.md 版本 1.2.10。
- **测试库**：config version 1.2.10；`.config/scripts/vault_check.py` 副本；
  09 系统管理/知识库架构.md 副本同步分层小节。
- **涉及文件**：新增 tools/check.py、skills/knowops/scripts/vault_check.py、
  .github/workflows/ci.yml、private/dev/tools/release.py；修改两 SKILL.md、
  knowops 4 references、system-manage 知识库架构模板、private 开发文档 4 份、
  测试库 3 处。
- **兼容性**：无破坏性变更；旧库升级后建议执行一次 `check-vault` 全库巡检。

## [1.2.9] - 2026-08-20

### 新增摘录系统（06 摘录系统）（用户提出）

- **新增一级模块 `06 摘录系统`**：
  - 长篇（诗词/文言/文学/网络分类文件夹，用到才建）：一篇作品一篇笔记，
    `作品名.md` 命名，同名不同作者加作者后缀（作品名始终在前）；文学属性集
    `author`/`dynasty`（诗词文言）/`source`；
  - 短篇（名言/警句/思考/摘抄固定四分类，每类一个聚合文件）：条目带日期标注
    追加到文件末尾；任一分类超 **100 条**后拆分为文件夹——原文件移入改名
    `<分类>/<分类> 01.md`，新开 `<分类>/<分类> 02.md`，新条目写入序号最大文件；
  - 笔记含可选「感想」区；未成型的想法（灵感）仍走 00 收件箱，不进摘录系统。
- **编号规则变更**：**看板、归档与系统管理固定位于最后三位**（原规则：归档与
  系统管理固定最后两位）；原 06/07/08 顺延为 07 看板 / 08 归档 / 09 系统管理；
  项目内 6 处旧规则表述全部更新（DESIGN / workflow / properties / 知识库架构 /
  记录规范 / 变更记录模板）。
- **新属性**：`type` 枚举新增 `excerpt`；`excerpt_kind`（长篇/短篇）、`category`
  （长篇：诗词/文言/文学/网络；短篇：名言/警句/思考/摘抄）、`author`、`dynasty`；
  excerpt 必填 `type/excerpt_kind/category/created/标签`，长篇另加 `source`。
- **捕获路径**：桌面端"摘录：……"直达（长篇建笔记/短篇追加，相似检查照常）；
  随身端 `capture_kind` 枚举新增 `摘录`（三分类变四分类，单一值，具体分类写
  tags 与建议归属行）；入库写入 `00 收件箱/摘录/`（收件箱新增第四子目录），
  审阅沉淀到 06 摘录系统。契约两端同步（desktop-ingest.md ↔ mobile-capture.md
  ↔ capture-template.md ↔ automation-prompt-template.md）。
- **看板**：默认视图新增「摘录-最近添加」（type: excerpt，created 倒序）；
  workflow / init-config / 测试库看板.base 同步。
- **配置**：preferences 新增 `excerptDir`（默认 `06 摘录系统`）；
  `dashboardDir`/`archiveDir`/`systemDir` 默认值改为 `07 看板`/`08 归档`/
  `09 系统管理`。
- **分类原则**新增第 6 条：用于收藏（回顾、引用、欣赏的摘抄句子或作品）→
  06 摘录系统；分类规则路由表同步加两行（长篇/短篇）。
- **根 AGENTS.md**：新增 private/ 文件夹适度提及（不涉本机信息与内部文件结构，
  防止 agent 遗漏阅读）；架构要点补模块结构与 capture_kind 摘录。
- **涉及文件**：两 SKILL.md（版本 1.2.9）+ knowops 5 references + system-manage
  5 模板 + everywhere-note 2 文件 + README 双语 + 根 AGENTS.md +
  automation-prompt-template.md + private 开发文档（本文件/DESIGN/TEST-REPORT/
  private AGENTS）+ 测试库（目录重命名 06→07/07→08/08→09、config 刷新、
  系统管理文档刷新、看板.base 新视图）。
- **兼容性**：旧库（已按 00–08 初始化）**不自动迁移、不写入内置迁移流程**；
  agent 遇旧结构时现场与用户协商处理（遵循"信息以用户给出为准"红线）。

## [1.2.8] - 2026-08-14

### 安装目标扩展 + 用户文档同步纳入发布流程（用户提出）

- **knowops 安装目标新增 DeepSeek Harness（DSH，当前开发环境）**：安装目标列表与
  发布流程第 6 步补充 `~/.dsh/skills/`（只装 knowops）；DESIGN / private AGENTS /
  MEMORY 同步。
- **用户可见文档纳入发布流程**：开发工作流、发布流程第 2 步、DESIGN 完成检查清单
  新增「受影响用户文档（08 系统管理模板 assets/system-manage/ 与测试库副本）
  同步修改」；文档职责表补充 08 系统管理模板行。
- **08 系统管理模板同步**：用户手册（「入库今天手机记的」用法行 + GitHub 暂存库
  FAQ）、知识库架构（设计原则第 8 条：可选外部输入）、记录规范（暂存库条目命名
  约定）补充 GitHub 暂存库说明；测试库 08 系统管理 副本刷新、变更记录追加
  2026-08-14 条目。
- 版本标识：两 skill 的 SKILL.md `metadata.version` 升至 1.2.8（private/AGENTS.md、
  DESIGN 头、测试库 config 版本同步）。
- 兼容性：无配置 schema 变化；纯文档 + 安装目标变化。
- 测试：quick_validate 两 skill；测试库 08 系统管理 副本核对；回归（CLI 创建/回读、
  操作日志、HTML 导出、删除进回收站）。

## [1.2.7] - 2026-08-14

### GitHub 暂存库同步 + 操作后核验 + 自动化模板（用户多轮确认）

- **everywhere-note 可选 GitHub 暂存库同步**：用户指定暂存库（仓库 / 分支 / 目标
  知识库目录）且平台具备 GitHub 能力（gh CLI / git / GitHub MCP 等，agent 自行
  判断）时，把生成的条目上传到暂存库 `<知识库目录>/`；配置只存对话上下文，新对话
  重新询问；上传结果如实反馈（同步不撒谎）、只上传本次条目文件；提醒文案区分
  已同步 / 未同步。
- **knowops 暂存库拉取入库**：初始化向导新增「GitHub 暂存库同步配置」步骤，写入
  配置可选顶层键 `githubSync`（`enabled/repo/branch/folder`，缺失视为未启用，
  旧配置兼容）；收到入库指令按优先级处理：用户提供的内容 → GitHub 暂存库新条目 →
  询问用户（本地 00 收件箱是写入目标，不是检查来源）；拉取 → 解析校验 → 写入
  00 收件箱 → 源文件移动到暂存库 `<folder>/归档/<入库当天日期>/`（中文补零，与
  07 归档约定一致；本地不重复存放）；失败条目保留原位可重试。
- **自动化提示词模板**：新增 `skills/automation-prompt-template.md`（与两 skill
  同级，随仓库发布），设置定时自动化时复制为提示词，指导 agent 自动完成暂存库
  拉取入库（含红线与失败处理）。
- **操作后核验**：workflow.md 操作后流程新增第 7 步「核验」——回读核验必填属性
  （frontmatter）/ 命名 / 双向链接 / 操作日志与日记同步 / 任务双轨 / 插件与
  HTML 导出执行情况，缺失即补正并告知用户。
- **发布流程简化**：不再额外留存 everywhere-note zip（`dist/<version>/` 正常
  打包产物即用）；DESIGN / private AGENTS 同步。
- 版本标识：两 skill 的 SKILL.md `metadata.version` 升至 1.2.7（private/AGENTS.md、
  DESIGN 头、测试库 config 版本同步）。
- 兼容性：配置新增可选顶层键 `githubSync`；旧配置无此键时行为不变（跳过 GitHub
  检查），无破坏性变化。
- 测试：quick_validate 两 skill；暂存库拉取入库用 `private/test/staging-repo/`
  （本地 git 仓库模拟）真实场景测试（拉取 → 入库 → 归档移动 → 无新内容跳过）；
  测试库回归（CLI 创建/回读、操作日志、HTML 导出、删除进回收站）。

## [1.2.6] - 2026-08-13

### 审计修订 + 文档对齐（用户确认）

- README.en.md 与中文版/实际规则对齐三处：增长触发补「接近 50 经确认建二级」前提；
  数据安全红线改为「高风险先征求同意、低风险先执行后记录」（变更分级）；
  HTML 镜像导出由「可选」改为「默认启用」。
- README 双语目录结构补 AGENTS.md（公开版随仓库发布）。
- DESIGN.md 安全模型表：修改/移动/重命名行改为与 SKILL.md 通用红线 2（变更分级）
  一致的表述（低风险先执行、随后记录并给回退方案）。
- `.workbuddy/memory/MEMORY.md` 更新至当前状态（AGENTS 公开版入 git、dev/test 迁入
  private/、安装目标 Codex/WorkBuddy/Trae）。
- 版本标识：两 skill 的 SKILL.md `metadata.version` 升至 1.2.6（private/AGENTS.md、
  DESIGN 头、测试库 config 版本同步）。
- 兼容性：无配置 schema 变化；纯文档修订 + 版本标识，无脚本逻辑变化。
- 测试：quick_validate 两 skill；无运行时逻辑变化，真实场景结论沿用 v1.2.5
  （用户确认）。

## [1.2.5] - 2026-08-13

### 任务双轨同步规则澄清（用户确认）

- workflow.md 任务段补充明确规则：**勾选完成 → 该行移入「已完成」折叠块**，并同步
  任务笔记 `status: done` + `finished_date`；取消勾选 → 移回未完成列表，并同步任务
  笔记状态与完成时间（工具无关表述）。
- properties.md 任务段补「取消勾选移回未完成列表」，与 workflow 对齐。
- 测试库 TODO.md 按正确示范修正，并做勾选/取消双向回归验证。
- 版本标识：两 skill 的 SKILL.md `metadata.version` 升至 1.2.5（private/AGENTS.md、
  DESIGN 头、测试库 config 版本同步）。
- 兼容性：无配置 schema 变化；纯文档澄清，无脚本逻辑变化。
- 测试：quick_validate 两 skill；任务双轨同步回归（勾选 → 移入折叠块 + done；
  取消 → 移回列表 + pending；CLI 回读核对）。

## [1.2.4] - 2026-08-13

### 结构重构 + html_export 修复 + 版本标识（用户确认）

- **文件结构**：`dev/`、`test/` 迁入新 `private/` 目录（整体写入根 .gitignore、
  不进 GitHub）；`private/` 内部初始化子 git（无远端）做版本管理，发布前检查并
  提交子 git；`private/AGENTS.md` 承载开发指引（开发工作流/发布流程/个人与机器
  专属信息）；根 AGENTS.md 拆分为公开版（不含开发期内容）并重新纳入 git 跟踪；
  `.workbuddy/` 不放入 private，测试库生成物不提交子 git。
- **文件分类归属**：DESIGN 新增三区矩阵（A GitHub 公开 / B private 子 git /
  C 不版本管理），归属规则写入开发规范。
- **发布流程**：打包暂存改为 `private/dist/<version>/`（排除 `__pycache__`、
  `*.pyc`）；everywhere-note 不安装本机，zip 留存 `private/dist/` 供随身端分发；
  明文规则：仅「无运行时变化 + 用户明确确认」可沿用测试结论，须在 TEST-REPORT
  注明「用户确认沿用」。
- **版本标识**：两 skill 的 SKILL.md frontmatter 新增 `metadata.version`
  （quick_validate 允许的 frontmatter 键），跟随当前版本。
- **html_export.py 修复**：① wikilink/embed 显示文字与 alt 双重 HTML 转义；
  ② export-one 增加路径越界校验（必须落在 vault 内）；③ `_all_files` 类属性改
  实例属性；④ `--vault` 目录名做路径分隔符消毒。
- 兼容性：配置 schema 无变化；测试库随迁 `private/test/`（Obsidian 注册路径与
  vaultPath 同步更新）。
- 测试：quick_validate 两 skill；html_export 回归（全量/单篇/越界拒绝/特殊字符）；
  测试库真实场景测试。

## [1.2.3] - 2026-08-13

### 测试方式调整 + GitHub Release 纳入发布流程（用户提出）

- **删除 .test-env/**（kb_test.py / forward_test.py）：脚本作用有限，真实测试改由
  agent 按 dev/DESIGN.md 场景清单在 `test/Obsidian测试知识库` 直接执行并核对。
- **GitHub Release 纳入发布流程**：每次发布打 tag `vX.Y.Z` 并创建 GitHub Release，
  附带两 skill 的 zip 安装包（只含运行时文件）；本地 `dist/<version>/` 仅作上传
  中转，上传后可清理。
- 兼容性：无 skill 运行时变化；配置 schema 无变化。

## [1.2.2] - 2026-08-13

### 收尾整理：AGENTS.md 本地化 + 移除 dist + CHANGELOG 精简（用户提出）

- **AGENTS.md 改为本地维护**：加入 .gitignore、从 git 跟踪移除（1.2.1 曾随 git
  发布，本版撤销）；README 目录树同步移除。
- **移除本地 dist/**：发布不再打包 zip（安装直接复制 `skills/` 目录，git 历史即
  版本备份）；AGENTS.md / DESIGN.md 的发布流程去掉打包步骤。
- **CHANGELOG 精简**：删除 <1.0.0 及旧版 obsidian-kb 时期条目（省 token，无保留
  价值）。
- 兼容性：无 skill 运行时变化；配置 schema 无变化。

## [1.2.1] - 2026-08-13

### 项目重构：AGENTS.md 开发入口 + 开发文档精简 + 工作流去脚本化（用户确认）

- **新增 AGENTS.md（仓库根，随 git 发布）**：统一开发入口，承载项目状态、架构要点、
  开发工作流、开发规范、测试与发布流程、环境已知坑；新对话/新 agent 读它即可从零
  接手，不再依赖任何 agent 私有记忆。
- **开发工作流制度化**（写入 dev/DESIGN.md）：需求提出 → 讨论对齐+复述 → 用户确认 →
  实施（同步更新 CHANGELOG/DESIGN/README/TEST-REPORT）→ 验证 → 展示成果 + 自动
  打包发布安装；完成检查清单为每次交付必填部分。
- **发布前真实测试纳入流程**：发布前必须在 `test/Obsidian测试知识库` 执行实际场景
  测试（CLI 创建/回读、操作日志、HTML 导出、删除进回收站）。
- **版本规则强化**：默认只升最后一位；第一位/中间位仅用户要求时升。
- **去脚本化**：删除 `dev/scripts/update_skill.py`，打包/提交/安装全部由 agent 按
  md 规范执行；`.test-env/` 测试脚本保留为验证工具。
- **dev 文档精简**：DESIGN.md / TEST-REPORT.md 只保留当前状态；历史章节直接删除，
  不再保留归档。
- **08 系统管理模板 6 → 5 份**：合并 命名规范.md + Frontmatter规范.md →
  记录规范.md；5 份文档自洽自足（只引用 08 系统管理 内部文档与知识库本身，不依赖
  skill 侧给 agent 读的文档）；用户手册去掉重复小节、FAQ 同步；workflow.md /
  properties.md / README 双语同步文档清单。
- **测试库同步**：`test/Obsidian测试知识库` 08 系统管理刷新为新模板集，补
  `.config/agent-rules.md`，移除 v1.0.0 遗留 Agent规则.md；配置版本升 1.2.1。
- 兼容性：配置 schema 无变化（1.2.0 配置兼容，无需迁移）；旧库已生成的 08 系统管理
  文档不自动迁移，按需自行合并。
- 测试：quick_validate 两 skill；kb_test.py 脚本级；test/ 测试知识库真实测试。

## [1.2.0] - 2026-08-13

### 去脚本化 + 配置/约束收口到 .config（用户确认）

- **删除 kb_config.py / kb_env.py**：废除多 vault，改为「一个知识库一个配置文件」；
  配置读写交由 agent 直接读写 `.config/knowops.config.json`（单 vault）。CLI 语法/
  环境细节交由 agent 自行探索，不再用脚本写死固定经验。
- **新增每次对话前置引导（bootstrap）**：SKILL.md 增加「每次对话前置」步骤，保证
  任何新对话、任何任务开始前都先定位 vault → 读配置 → 读 agent-rules → 缺配置则
  初始化，不再依赖脚本/记忆。
- **agent 读的个性化约束收口到 `.config/agent-rules.md`**：插件集成规则、额外红线、
  额外操作要求、旧库/特殊结构约定统一迁入隐藏配置；`08 系统管理/` 删掉 `Agent规则.md`，
  只保留 6 份用户文档，agent 不读。
- **HTML 导出接入操作后流程**：workflow.md 操作后流程补「HTML 镜像导出（若
  exportEnabled）」，修复「声明默认启用但无触发」的缺口；配置新增 `exportEnabled`。
- **html_export.py 自包含**：去掉 kb_config 依赖，改由 `--vault-path/--export-root` 或
  同库 `../knowops.config.json` 解析路径。
- **修词**：用户手册「逐条五问判断」→「逐条判断价值」；properties 去掉「剪藏取消」
  历史表述。
- **配置 schema（破坏性）**：单 vault，键为 `version / vaultPath / exportRoot /
  exportEnabled / preferences`；移除 `vaults / defaultVault / cliPath / configDir /
  exportDirName`。旧配置不兼容，旧库接入现场询问用户。
- 测试：html_export.py py_compile 通过。

### 发布/安装/同步约定（固定流程）

- `dev/scripts/update_skill.py release --version <X.Y.Z> --type <feat|fix|docs> --msg ...`
  （check → package → commit）→ `git push`。
- 安装/同步：把 `skills/knowops` 与 `skills/everywhere-note` 复制到各平台用户级 skill
  目录（覆盖旧内容）：Codex `~/.codex/skills/`、WorkBuddy `~/.workbuddy/skills/`、
  TraeWork `~/.qoderwork/skills/`（待确认）。详见 DESIGN §0 v1.2.0。

## [1.1.1] - 2026-08-13

### 引用结构精简（仅 knowops 内部）

- **拆分 references/workflow.md**：日常流程（知识库模型/分类原则/模块流程/操作日志/操作后流程）保留在 workflow.md；初始化向导/插件集成/配置与 HTML 导出/脚本一览拆至新增 references/init-config.md。
- **SKILL.md 加载表按任务拆分**：日常记录读 workflow.md；初始化/配置/导出读 init-config.md；暂存入库的 workflow.md + redlines.md 由「按需」改为「必读」，与 desktop-ingest.md 一致。
- **redlines.md 去重**：删除与 SKILL.md 通用红线重复的「变更分级」「回读校验」，只保留执行层细节（删除纪律/git/配置驱动/直写例外/插件规则/安全边界）。
- 无功能行为变化；everywhere-note 未改动。

## [1.1.0] - 2026-08-12

### 架构重构：四 skill → 两 skill（用户确认）

- **knowops（桌面端统一入口）**：合并 knowops-workflow / knowops-obsidian /
  knowops-navigator 与 everywhere-note 桌面部分；SKILL.md 只保留触发、加载规则
  与通用红线；业务流程（references/workflow.md）、执行层红线
  （references/redlines.md）、桌面入库（references/desktop-ingest.md）与属性约定
  （references/properties.md）按需加载。
- **工具内容去重**：删除 cli / markdown / bases / canvas 同名 references，具体
  语法与命令交由官方工具 skill（obsidian-cli / obsidian-markdown / obsidian-bases /
  json-canvas / defuddle）。
- **everywhere-note（随身端）**：只保留手机/随身端捕获；references/mobile-capture.md
  与 assets/capture-template.md 独立保留。
- **旧目录归档**：四个旧 skill 目录归档至 legacy/1.0.2/（不随 git 发布）。
- **修复**：properties.md 必填属性矛盾、20/50 增长阈值冲突、操作日志范围
  （读取/搜索不记）、「联动动作」与「操作后流程」合并、初始化向导 git 步骤并入
  通用红线。
- **配置 schema**：SCHEMA_VERSION 1.0.2 → 1.1.0；配置文件名升级为 knowops.config.json，移除旧版兼容。
- 测试：quick_validate 两 skill 通过。

## [1.0.2] - 2026-08-12

### 调整（需求对齐：独立可用口径 + 开发期约束收口）

- **knowops-workflow 定位明确为可独立使用**：人机共读中立规范；单装即可使用，执行由 agent 通用能力完成；skill 内不写工具操作方式。
- **workflow 红线收敛为 4 条（工具无关）**：删除永远进系统回收站且可恢复；新建并初始化知识库时优先使用 git 管理；创建前相似检查；尽量使用已有模块。执行层红线（信息以用户为准、不静默放置/不自创模块、改删前征求同意等）归 knowops-obsidian。
- **knowops-navigator 入口语义**：大部分知识库任务以 navigator 为入口；用户直接 @ knowops-workflow 也可正常使用。
- **开发期约束收口**：从 skill 内部移除“不包含工具操作细节 / 不依赖不提及 / 不随本项目打包 / 通用化表述 / 不追求穷举 / 不重复标准 Markdown / 不重复实现”等作者/开发视角表述，统一收口到 dev/DESIGN.md；B 类（依赖/范围/设计决策）与 Agent规则.md 相关表述保持不动。
- **README 双语同步**：skill 表、特性、快速开始、数据安全红线（git 正面表述 + 红线归属拆分）。
- **配置 schema**：SCHEMA_VERSION 1.0.1 → 1.0.2（兼容 1.0.1 / 1.0.0）。
- 测试：quick_validate 四 skill 通过。

## [1.0.1] - 2026-08-10

### 新增 everywhere-note 随身记录配套 skill（用户多轮确认）

- **单 skill 双部分、渐进式按需加载**：SKILL.md 按运行环境（移动/随身 vs 桌面）路由到 references/mobile-capture.md 或 references/desktop-ingest.md。
- **随身端捕获**（独立自洽，手机端只装本 skill）：@ 即记、三分类（灵感/随手记/待整理内容）、输出符合知识库格式的 markdown（支持生成文件）、不依赖传输通道、当天有记录才设 22:00 提醒（合并一次、已过 22:00 顺延次日、平台不支持则如实说明）。
- **桌面端入库**：由 obsidian-suite 路由进入；解析用户提供的暂存文本/文件 → 相似检查 → 写入 00 收件箱 → 回读校验 → 操作日志 → 汇总；不设提醒、不负责审阅沉淀。
- **obsidian-suite 增强**：新增「随身端捕获配套 skill」小节与调用约定第 6 条；依赖方向 obsidian-suite → everywhere-note。
- **README 双语更新**：四 skill 说明、安装、快速开始、目录结构与 Roadmap（未来方向：手机端 git/坚果云自动同步 + 电脑端定时拉取；手机向电脑发提醒触发自动化）。
- **版本统一**：四个 skill 统一 1.0.1；config schema 1.0.1，兼容 1.0.0（结构未变，不做迁移）。
- 测试：quick_validate 四 skill 通过；打包 dist/1.0.1 四个 zip。

## [1.0.0] - 2026-08-10

### 全面重构（用户多轮确认，破坏性变更）

- **新模块体系**：00 收件箱 / 01 生活系统 / 02 知识系统 / 03 资产系统 / 04 规范系统 / 05 项目系统 / 06 看板 / 07 归档 / 08 系统管理；归档与系统管理固定最后两位，新模块顺延。
- **收件箱工作流**：简短/零碎/临时内容默认捕获（随手记/灵感/待整理内容）；审阅时按"五问法"沉淀/删除/归档；归档按中文补零日期文件夹（如 2026年08月09日/）。
- **问题四态**：未解决 → 研究中 → 已解决 → 已沉淀；沉淀后原问题移入已沉淀并双向链接。
- **知识系统四类**：概念原理 / 经验方法 / 方案 / 案例；领域二级目录增长触发（<50 不拆 / 50~150 建二级 / >150 评估三级）；剪藏模块取消（URL 素材入收件箱待整理）。
- **任务双轨**：任务笔记（type: task）为看板数据源 + TODO.md 人工清单双向同步；冲突询问用户不静默覆盖。
- **看板默认创建**：06 看板/看板.md + 看板.base，默认 7 视图，可扩展。
- **08 系统管理**：7 个模板存于 skill `assets/system-manage/`，初始化复制进库，替代 knowledge-rules.md；用户手册并入。
- **插件集成**：初始化扫描插件并确认规则，写入 Agent规则.md，每次操作前必读、操作后执行；不写死插件名与流程。
- **配置 schema 跟随 skill 版本**（version = "1.0.0"）；删除 kb_config migrate 命令；不做旧配置迁移。
- **破坏性变更**：旧目录（问题/知识/项目/日志/日程/看板.md/TODO.md 等）不再兼容；旧库接入由 agent 现场询问用户处理。
- 测试：quick_validate 三 skill + 脚本级测试 + 测试库按新结构重建 forward-test（结果见 TEST-REPORT.md）；发布待用户审核后决定。
