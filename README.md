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

- **五个模块，各装什么一目了然**：`00 收件箱`（没想清楚的）/ `01 知识`（验证过的）/
  `02 摘录`（抄来收藏的）/ `03 系统`（库自己的痕迹和说明书）/ `04 归档`（不再活跃
  的）；系统与归档固定末两位，根目录一份 `看板.md` 一屏总览；
- **收件箱宽进严出**：平铺、序号命名，没有子目录；你可以随手建文件、不写任何
  格式——规范只约束 agent，沉淀时由 agent 补全；收件箱是校验豁免区；
- **知识按主题积累**：一个主题一份文档，条目按章节组织；单章超过约 30 条时提议
  拆分，原文档升级为文件夹——先单体、涨破再拆，不提前设计层级；
- **摘录**：诗词、文言等长篇摘抄一篇一笔记（作品名命名，作者/朝代/出处
  属性），名言、警句、思考等短句按分类聚合（超 100 条自动拆分序号文件）；
  桌面端"摘录：……"直达，随身端摘录经收件箱审阅沉淀；
- **日记＝操作记录**：每次写入/修改/移动/删除/归档自动追加一行，按年存放在
  `03 系统/日记/`，不用你写，随时可翻；
- **Obsidian 模板接入**：`03 系统/模板/` 提供主题文档与摘录长篇两份模板，
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
- **看板**：根目录 `看板.md` 嵌入 `03 系统/看板.base` 的视图（收件箱待沉淀、知识
  最近更新、摘录最近添加），可扩展；
- **归档**：`04 归档` 按中文补零日期切分；
- **白板自由空间**：你在库里建的 canvas 不会被管理、校验或导出；
- **插件集成规则**：初始化扫描插件、由用户确认规则写入隐藏配置 `.config/agent-rules.md`，
  每次变更操作前读取、操作后按规则执行（如先版本提交、再云同步）；
- **配置驱动、版本跟随**：目录与偏好全在 `.config/knowops.config.json`（单 vault），
  schema 版本跟随 skill 版本；
- **数据安全红线**：删除永远进系统回收站且可恢复、高风险改删移前征求同意、不代为
  git init、创建前相似检查、信息以用户为准、重要写入后回读校验。

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
   - 暂存内容入库 → 读 `references/desktop-ingest.md`。
2. 初始化向导会逐步确认：vault 路径与名称、五个模块的默认目录结构（懒加载：
   收件箱/摘录/归档首次写入时才出现）、GitHub 暂存库同步（可选）、插件集成规则
   （写入 `.config/agent-rules.md`）、`03 系统` 的用户文档与模板、示例主题文档、
   根目录看板；配置固定写入 vault 内隐藏目录 `.config/`，HTML 镜像导出默认启用
   （`<vault>/.config/HTML-Export/`）。
3. 用到具体能力（CLI / Markdown / Bases / Canvas / 网页提取）时，按需加载对应
   工具型 skill。

日常用法示例：

| 你说 | agent 做 |
|---|---|
| 手机：记一下：XXX | everywhere-note 生成规范 md 条目 + 设置当晚 22:00 提醒；指定了暂存库且具备 GitHub 能力时同步上传 |
| 入库今天手机记的 | knowops 加载 desktop-ingest.md：优先收用户提供的内容；配置了暂存库时自动拉取 GitHub 新条目，序号命名写入 `00 收件箱`，源文件归档至暂存库 |
| "记一下：……" | 写入 `00 收件箱/`（序号命名，补属性和标签） |
| "摘录：将进酒……" | 长篇作品建独立笔记到 `02 摘录/长篇/诗词/`（作品名命名）；短句追加到 `02 摘录/短篇/` 对应分类文件 |
| "这条经验入库，主题是架构设计" | 合并进 `01 知识/` 对应主题文档的对应章节 |
| "审阅收件箱" | 逐条判断五去向：知识 / 摘录 / 归档 / 删除 / 保留 |
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
    │       ├── system-manage/       # 03 系统初始化用户文档（2 文件：用户手册/变更记录）
    │       ├── templates/           # 笔记模板（主题文档/摘录长篇，供 Obsidian Templates 插件）
    │       ├── knowledge-example/   # 知识模块示例主题文档
    │       ├── agent-rules.md       # .config/agent-rules.md 模板
    │       └── html-export.json     # HTML 导出范围配置模板
    ├── everywhere-note/             # 随身端捕获（可选 GitHub 暂存库同步）
    │   ├── SKILL.md
    │   ├── references/mobile-capture.md
    │   └── assets/capture-template.md
    └── automation-prompt-template.md  # 自动化入库提示词模板（设置定时自动化时使用）
```

## Roadmap（未来方向）

- 坚果云等其他文件同步通道（GitHub 暂存库同步已实现，见上）；
- 手机端向电脑端发送提醒，触发电脑端自动化执行收集入库（自动入库可通过
  `skills/automation-prompt-template.md` 配置定时自动化实现）。

以上为未实现的未来方向，已记录于开发文档，供后续实现。

## 相关项目

工具型 skill 是 **Obsidian 官方技能仓库**的安装副本，可随官方更新：

- [kepano/obsidian-skills](https://github.com/kepano/obsidian-skills) ——
  Obsidian 官方 agent skills（obsidian-cli / obsidian-markdown / obsidian-bases /
  json-canvas / defuddle）
- [kepano/defuddle](https://github.com/kepano/defuddle) —— 网页正文提取库

## 许可证

MIT License，见 [LICENSE](LICENSE)。
