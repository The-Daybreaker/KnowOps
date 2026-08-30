# KnowOps：Obsidian 知识管理 Skills

KnowOps 是一套面向 **AI agent** 的 **Obsidian 知识管理技能包**：两个 skill 让 agent 帮你把
知识库管得井井有条——**桌面端统一入口 + 随身端捕获**，按设备分开安装、配套使用。

## 这是什么

在 Obsidian 里管理个人知识库时，agent 需要两样东西：一是**内容怎么组织**（知识库
有哪些模块、收件箱怎么沉淀、知识按什么轴积累），二是**怎么操作 Obsidian**（用官方
CLI 读写笔记、尊重删除红线）。本仓库把这两件事放进一个桌面端 skill（`knowops`），
通过 references 按需加载；另配一个随身端 skill（`everywhere-note`）负责手机/平板上
的快速记录。

这个库只收「没有更具体去处」的内容：待办有待办软件、项目文件有项目文件夹、可执行
的脚本模板有它们所属的仓库——这些都不进库。库里放的是摘抄、验证过的经验、还没想
清楚的念头。

| Skill | 定位 | 一句话 |
|---|---|---|
| **knowops** | 桌面端统一入口 | 知识库怎么组织 + Obsidian 怎么操作，按 references 渐进式加载；单装即可管理知识库 |
| **everywhere-note** | 随身端捕获 | 手机 @ 即记，生成规范 md 并设 22:00 提醒 |

## 特性

- **通用地基 + 扩展模块登记制**：skill 只预置基础骨架——`00 收件箱`（没想清楚的）/
  `01 知识`（验证过的）/ `03 系统`（库自己的痕迹和说明书）/ `04 归档`（不再活跃
  的）四个基础模块＋根目录一份 `看板.md` 一屏总览；系统与归档固定末两位。**新增
  模块 = 你在库里新建文件夹**，agent 来问规则、写进用户手册，此后按手册执行——
  知识库怎么长，由你说了算，不用等 skill 发版；
- **单一事实来源**：各模块装什么、怎么入库、怎么分类、怎么命名，唯一落点是库内
  `03 系统/用户手册.md` 的「模块规则」章节（用户可见可编辑，agent 必读按它执行）；
  config 只存机器可读索引，没有规则副本、没有漂移；
- **收件箱宽进严出**：平铺、序号命名，没有子目录；你可以随手建文件、不写任何
  格式——规范只约束 agent，沉淀时由 agent 补全；收件箱是校验豁免区；
- **知识按主题积累、原话完整**：一个主题一份文档，条目按章节组织；条目正文
  **完整保留你的原话**（agent 不改写、不压缩，补充说明经你同意才写）；单章超过
  约 30 条时提议拆分——先单体、涨破再拆，不提前设计层级；
- **摘录＝预置的扩展模块**：初始化时问你是否启用；启用后长篇摘抄一篇一笔记、
  短句按分类聚合（超 100 条自动拆分），全部规则登记在用户手册，整模块可停用；
- **写入审计闭环**：agent 每批内容写入（入库/沉淀/归档/删除）后，在收件箱留一份
  `待审阅-日期.md` 账单（看板可见、审阅后即删），并在日记里详细记录改动；
- **日记分「用户 / agent」两章**：每天一个文件（遵循 Obsidian Daily notes 规则，
  按年存放于 `03 系统/日记/`）；agent 的动作按类型记在 agent 章，你手动改动的
  部分由 agent 依文件历史与 git **补记**（注明推断依据）——谁做的，一翻便知；
- **Obsidian 模板接入**：`03 系统/模板/` 提供主题文档模板，
  配合 Obsidian 核心插件 Templates 套用；
- **渐进式加载**：`knowops` 的 SKILL.md 只承载触发、加载规则与通用红线；业务流程
  （workflow.md）、执行层红线（redlines.md）、桌面入库（desktop-ingest.md）按需读取；
- **随身端捕获与统一入库**：手机/随身设备上 @ everywhere-note 直接口述记录，生成
  符合知识库格式的 md（支持生成文件）并设 22:00 提醒；回到电脑后由 knowops 解析
  暂存内容批量写入 `00 收件箱`；手机端只装这一个 skill 即可独立使用，不依赖传输
  通道；随身端不内嵌任何桌面库结构信息，桌面库结构调整不要求随身端重装；
- **GitHub 暂存库同步（可选）**：用户指定一个 GitHub 暂存库；手机端在具备 GitHub
  能力（gh CLI / git / GitHub MCP 等）时把条目上传到暂存库中本知识库的目录；电脑端
  入库时自动拉取新条目写入 `00 收件箱`，并把源文件归档到暂存库
  `<知识库名>/归档/<日期>/`（按入库日期切分）；多个知识库可共用同一暂存库互不冲突；
- **看板**：根目录 `看板.md` 嵌入 `03 系统/看板.base` 的实时视图（收件箱待沉淀、
  知识最近更新等），模块登记/注销时同步增减；
- **归档**：`04 归档` 按中文补零日期切分；
- **白板自由空间**：你在库里建的 canvas 不会被管理、校验或导出；
- **插件集成规则**：初始化扫描插件、由用户确认规则写入隐藏配置 `.config/agent-rules.md`，
  每次变更操作前读取、操作后按规则执行（如先版本提交、再云同步）；
- **配置驱动、版本跟随**：模块索引与偏好全在 `.config/knowops.config.json`
  （单 vault），schema 版本跟随 skill 版本；
- **数据安全红线**：删除永远进系统回收站且可恢复、高风险改删移前征求同意、不代为
  git init、创建前相似检查、信息以用户为准（原话不改写不压缩）、重要写入后回读校验。

## 安装

按设备类型安装，**不要在同一设备上同时安装两个 skill**（会互相竞争触发）：

| 设备 | 安装 |
|---|---|
| 桌面电脑（可操作知识库） | `skills/knowops/` |
| 手机/平板等随身设备 | `skills/everywhere-note/` |

把对应目录复制到你的 agent 的**用户级 skill 目录**（位置因平台而异，按你所使用
平台的 skill 安装说明为准；一般形如 `~/.<平台>/skills/`），或直接克隆本仓库：

```sh
git clone https://github.com/The-Daybreaker/KnowOps.git
# 然后把 skills/ 下对应目录复制到用户级 skill 目录
```

> 也可以从 GitHub Releases 下载 `<skill>-vX.Y.Z.zip` 安装包（每次发布自动生成，
> zip 内以 skill 名为根目录）。

> **依赖**：`knowops` 的具体语法与命令交由官方工具型 skill（obsidian-cli /
> obsidian-markdown / obsidian-bases / json-canvas / defuddle），它们来自 Obsidian
> 官方技能仓库 [kepano/obsidian-skills](https://github.com/kepano/obsidian-skills)，
> 需另行安装（见「相关项目」）；未安装时 knowops 会用官方文档兜底。

## 快速开始

1. 桌面端任务命中 `knowops` 后，按 SKILL.md 的加载规则先读 references：
   - 记录/管理/整理内容 → 先读 `references/workflow.md`，需要时运行**初始化向导**；
   - 执行 Obsidian 操作 → 先读 `references/redlines.md`；
   - 暂存内容入库 → 读 `references/desktop-ingest.md`，并按其头注加载
     `references/workflow.md` 与 `references/redlines.md`。
2. 初始化向导会逐步确认：vault 路径与名称、基础骨架四个模块（懒加载：收件箱/
   归档首次写入时才出现）、是否启用摘录模块（预置扩展模块，不启用可跳过）、
   GitHub 暂存库同步（可选）、插件集成规则（写入 `.config/agent-rules.md`）、
   `03 系统` 的用户手册与模板（手册「模块规则」章节是 agent 的执行依据）、
   根目录看板、Daily notes 日记配置；配置固定写入 vault 内隐藏
   目录 `.config/`，HTML 镜像导出默认启用（`<vault>/.config/HTML-Export/`）。
3. 用到具体能力（CLI / Markdown / Bases / Canvas / 网页提取）时，按需加载对应
   工具型 skill。

日常用法示例：

| 你说 | agent 做 |
|---|---|
| 手机：记一下：XXX | everywhere-note 生成规范 md 条目 + 设置当晚 22:00 提醒；指定了暂存库且具备 GitHub 能力时同步上传 |
| 入库今天手机记的 | knowops 加载 desktop-ingest.md：优先收用户提供的内容；未提供内容且配置了暂存库时，自动拉取 GitHub 新条目，序号命名写入 `00 收件箱`，源文件归档至暂存库 |
| "记一下：……" | 写入 `00 收件箱/`（序号命名，补属性和标签） |
| "摘录：将进酒……" | 按用户手册摘录节规则入库：长篇作品建独立笔记（作品名命名），短句追加到对应分类聚合文件 |
| "这条经验入库，主题是架构设计" | 合并进 `01 知识/` 对应主题文档的对应章节（正文保留你的原话） |
| "审阅收件箱" | 逐条按用户手册模块规则定去向：归属模块 / 归档 / 删除 / 保留 |
| "我建了个「读书」文件夹，以后书摘放这里" | agent 问清该模块的入库与分类规则 → 写进用户手册「模块规则」章节 → 此后按手册执行 |
| "把这篇归档" | 移入 `04 归档/<当天日期>/` |

## 目录结构

```
KnowOps/
├── README.md / README.en.md / LICENSE / .gitignore / AGENTS.md
├── tools/                        # 开发期校验脚本（check.py）
├── .github/workflows/            # CI（推送/PR 触发核心校验）
└── skills/
    ├── knowops/                     # 桌面端统一入口
    │   ├── SKILL.md                 # 触发 + 加载规则 + 通用红线
    │   ├── references/
    │   │   ├── workflow.md          # 业务流程规范（两道门/模块流程/日记/操作后流程）
    │   │   ├── init-config.md       # 初始化向导/GitHub暂存库/插件集成/配置与HTML导出/脚本
    │   │   ├── properties.md        # 属性/命名/目录/生命周期设计
    │   │   ├── redlines.md          # 执行层红线 + 直写例外
    │   │   └── desktop-ingest.md    # 暂存内容/GitHub暂存库拉取 → 00 收件箱
    │   ├── scripts/                 # html_export / vault_check
    │   └── assets/
    │       ├── system-manage/       # 库自身文档模板（用户手册→03 系统；变更记录→.config）
    │       ├── templates/           # 笔记模板（主题文档，供 Obsidian Templates 插件）
    │       ├── agent-rules.md       # .config/agent-rules.md 模板
    │       └── html-export.json     # HTML 导出范围配置模板
    ├── everywhere-note/             # 随身端捕获（可选 GitHub 暂存库同步；单文件自洽）
    │   └── SKILL.md
    └── automation-prompt-template.md  # 自动化入库提示词模板（设置定时自动化时使用）
```

## 相关项目

工具型 skill 是 **Obsidian 官方技能仓库**的安装副本，可随官方更新：

- [kepano/obsidian-skills](https://github.com/kepano/obsidian-skills) ——
  Obsidian 官方 agent skills（obsidian-cli / obsidian-markdown / obsidian-bases /
  json-canvas / defuddle）
- [kepano/defuddle](https://github.com/kepano/defuddle) —— 网页正文提取库

## 许可证

MIT License，见 [LICENSE](LICENSE)。
