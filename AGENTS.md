# AGENTS.md — KnowOps（发布仓公开版）

> 本文件随发布仓发布到 GitHub，面向使用者与安装者，只承载可公开内容。开发与
> 维护的完整规范位于私有协作层（不在本仓库内，也不在本机仓库目录之外公开；
> 其冷启动入口为协作层根的 `AGENTS.md` 协作总纲）。本文件与协作层规范冲突时，
> 以协作层为准。

## 项目概览

- **定位**：面向 AI agent 的 Obsidian 知识管理 skill 包，单仓库两 skill，统一版本号
  一起发布。
- `skills/knowops/`：桌面端统一入口（知识库怎么组织 + Obsidian 怎么操作）。
- `skills/everywhere-note/`：随身端捕获（手机 @ 即记，生成规范 md + 22:00 提醒；
  可选 GitHub 暂存库同步）。
- `skills/automation-prompt-template.md`：自动化入库提示词模板（设置定时自动化时
  使用；随 GitHub Release 一并分发）。
- **版本**：两 skill 统一版本号，以各 SKILL.md frontmatter 的 `metadata.version`
  为准。
- 同一设备不要同时安装两个 skill（触发竞争），README 已注明。

## 仓库布局

git 跟踪：`README.md`、`README.en.md`、`LICENSE`、`.gitignore`、`AGENTS.md`
（本文件）、`skills/`（两 skill 的全部运行时文件 + automation-prompt-template.md）、
`tools/`（开发期校验脚本 check.py）、`.github/workflows/`（CI）。

克隆本仓库后，把 `skills/` 下对应 skill 目录复制到 agent 的用户级 skill 目录即可
安装（详见 README）。

## 架构要点

- **库的定义**：知识库只收「没有更具体去处」的内容——待办有待办软件、项目文件
  有项目文件夹、可执行资产有所属仓库，都不进库。信息进库须过两道门：**归宿门**
  （库外没有更合适的家）与**形态门**（md 原生承载；由模块准入条件在架构上保证）。
- **单 vault 配置**：`<vault>/.config/knowops.config.json`，由 agent 直接读写；
  schema 为 `version / vaultPath / exportRoot / exportEnabled / preferences`
  （preferences 含 `modules` 模块登记索引与日记/模板目录），可选顶层键
  `githubSync`（GitHub 暂存库同步：`enabled/repo/branch/folder`）。
- **每次对话前置（bootstrap）**：检测官方工具 skill 可用性 → 定位 vault → 读配置
  → 读 `03 系统/用户手册.md` 的「模块规则」「agent 约束」两章 → 缺配置则按
  `references/init-config.md` 初始化。任何新对话都能从零接手知识库。
- **单一事实来源**：各模块装什么、怎么入库、怎么分类、怎么命名，唯一落点是
  库内 `03 系统/用户手册.md` 的「模块规则」章节——用户可见可编辑，同时是
  agent 必读的执行依据；config 只存机器索引（modules），不存规则副本。agent
  发现未登记的模块文件夹时，问清规则写进手册，此后按手册执行；模块目录被
  删除时问询注销（含手册章节同步处理）。
- **agent 工作范围与审计闭环**：agent 只做格式整理 + 系统运营 + 按用户指令的
  内容写入，不代运营内容；内容写入后日记详细记录（分「用户/agent」两章）＋
  收件箱建待审阅文件（用户审阅后删除）；用户无日记的改动由 agent 依文件历史
  与 git 补记；**用户原话完整记录，不改写、不压缩**。
- **库内脚本**：`html_export.py`（HTML 镜像导出，与 `html-export.json` 配对，
  导出默认启用，日记/模板/待审阅/白板默认不导出）与 `vault_check.py`（结构面
  校验：frontmatter 可解析/必填属性/type——基础枚举硬校验、登记模块按 config
  校验、未登记只警告；收件箱豁免、非 md 跳过），均自包含（标准库），初始化
  复制到 `.config/scripts/`。
- **模块结构（通用地基 + 扩展模块登记制）**：基础模块四个——00 收件箱（平铺
  序号命名，宽进严出，校验豁免）、01 知识（主题文档，先单体涨破再拆）、
  03 系统（Daily notes 日记两章节、模板、看板.base、用户手册）、04 归档
  （中文补零日期）；系统、归档固定末两位，新模块插入其前顺延编号；根目录
  `看板.md` 一屏总览（不是模块）；摘录为预置登记的扩展模块（初始化询问启用，
  可停用），其余业务模块由用户建文件夹登记产生，规则全在用户手册。
- **两 skill 依赖方向**：knowops 解析 everywhere-note 的 capture 产物（字段契约
  `type/created/tags/标题`，一句话标题不带日期，随身端不做任何入库判断、不写
  归属指向；历史字段如 `capture_kind` 容忍但不依赖）；everywhere-note 不依赖
  knowops，且不内嵌任何桌面库结构信息（桌面结构变更不要求随身端重装）。
  **改契约必须两端同步**（desktop-ingest.md ↔ everywhere-note SKILL.md）。
- **GitHub 暂存库同步（可选）**：手机端在用户指定暂存库且具备 GitHub 能力时上传
  条目到暂存库 `<folder>/`；knowops 入库时拉取新条目、并把源文件归档到暂存库
  `<folder>/归档/<入库日期>/`。暂存库目录约定两端同步。
- **操作后核验**：每次写入/修改/移动/删除/归档后核验，缺失即补正——结构面
  （frontmatter 可解析/必填属性/type 校验口径）由库内脚本 `vault_check.py` 输出
  键值摘要、agent 扫读（批量 ≥3 篇时抽 1 篇全文回读）；语义面（原话完整/双链/
  日记与待审阅/插件与导出）由 agent 回读核验。
- 工具型 skill（obsidian-cli / obsidian-markdown / obsidian-bases / json-canvas /
  defuddle）来自 [kepano/obsidian-skills](https://github.com/kepano/obsidian-skills)，
  不随本项目打包；knowops 只引用、不复制其内容。

## skill 内部结构约定

- knowops 的 SKILL.md 只承载触发、前置引导、加载规则与通用红线；references 按需
  加载（workflow / redlines / init-config / desktop-ingest / properties）。
- workflow.md 保持**工具无关的中立规范**视角，不写工具名/命令/委托链。
- `assets/system-manage/` 是库自身文档模板（用户手册——含**模块规则**与
  **agent 约束**（唯一事实来源，agent 必读）/记录/整理/查找/质量参考的总手册，
  初始化进 `03 系统/`；变更记录，初始化进 `.config/`）；初始化复制、已存在
  不覆盖。
- `assets/templates/` 是供 Obsidian Templates 插件使用的笔记模板（主题文档）。
- `everywhere-note` 单文件自洽：仅 SKILL.md（流程、条目形状与红线全部内嵌）。
- 两 skill 的 SKILL.md frontmatter 均含 `metadata.version`，跟随当前版本。

## 通用红线（对知识库操作）

1. **删除永远进系统回收站且可恢复**。
2. **变更分级**：高风险操作先展示方案、征得同意后执行；低风险先执行、随后记录。
3. **不代为 `git init`**。
4. **信息以用户给出为准**；**用户原话完整记录，不改写、不压缩**。
5. **创建前相似检查**。
6. **重要写入后回读校验**。
7. **变更操作前读取用户手册「模块规则」与「agent 约束」两章**。
8. **Obsidian 操作以官方工具 skill 为准**：前置检测可用性并记录；已安装则加载
   遵循其语法，未安装先与用户确认兜底（安装或 help.obsidian.md），不自行猜测
   命令、不以网络搜索替代。
