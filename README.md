# KnowOps：Obsidian 知识管理 Skills

KnowOps 是一套面向 **AI agent** 的 **Obsidian 知识管理技能包**：两个 skill 让 agent 帮你把
知识库管得井井有条——**桌面端统一入口 + 随身端捕获**，按设备分开安装、配套使用。

## 这是什么

在 Obsidian 里管理个人知识库（收件箱捕获、问题跟踪、知识沉淀、项目、日程、任务、
看板、归档……）时，agent 需要两样东西：一是**内容怎么组织**（知识库有哪些模块、
收件箱如何审阅、问题如何从"未解决"走到"已沉淀"、知识与项目如何区分），二是
**怎么操作 Obsidian**（用官方 CLI 读写笔记、尊重删除红线）。本仓库把这两件事
放进一个桌面端 skill（`knowops`），通过 references 按需加载；另配一个随身端
skill（`everywhere-note`）负责手机/平板上的快速记录。

| Skill | 定位 | 一句话 |
|---|---|---|
| **knowops** | 桌面端统一入口 | 知识库怎么组织 + Obsidian 怎么操作，按 references 渐进式加载；单装即可管理知识库 |
| **everywhere-note** | 随身端捕获 | 手机 @ 即记，生成规范 md 并设 22:00 提醒 |

## 特性

- **收件箱捕获与审阅**：顿悟、灵感、想法等简短零碎内容默认进 `00 收件箱`
  （随手记 / 灵感 / 待整理内容）；审阅时按"未来怎么用"沉淀、删除或归档；
- **渐进式加载**：`knowops` 的 SKILL.md 只承载触发、加载规则与通用红线；业务流程
  （workflow.md）、执行层红线（redlines.md）、桌面入库（desktop-ingest.md）按需读取；
- **随身端捕获与统一入库**：手机/随身设备上 @ everywhere-note 直接口述记录，生成
  符合知识库格式的 md（支持生成文件）并设 22:00 提醒；回到电脑后由 knowops 解析
  暂存内容批量写入 `00 收件箱`；手机端只装这一个 skill 即可独立使用，不依赖传输通道；
- **GitHub 暂存库同步（可选）**：用户指定一个 GitHub 暂存库；手机端在具备 GitHub
  能力（gh CLI / git / GitHub MCP 等）时把条目上传到暂存库中本知识库的目录；电脑端
  入库时自动拉取新条目写入 `00 收件箱`，并把源文件归档到暂存库
  `<知识库名>/归档/<日期>/`（按入库日期切分）；多个知识库可共用同一暂存库互不冲突；
- **问题全生命周期**：未解决 → 研究中 → 已解决 → 已沉淀；沉淀后原问题移入
  已沉淀并**双向链接**回知识笔记；
- **知识沉淀**：按类型归类（概念原理 / 经验方法 / 方案 / 案例），领域二级目录
  **用到才建**，增长触发拆分（<50 不拆 / 接近 50 经确认建二级 / >150 评估三级）；
- **资产与规范系统**：模板 / 工作流可复用，原则 / 标准规范 / 检查清单应遵守；
- **项目系统**：进行中 / 已完成 / 项目复盘，项目六文件模板；
- **日程 + 自动化提醒**：一句话录入，含明确时间信号自动创建定时提醒；
- **任务双轨同步**：任务笔记为看板数据源，TODO.md 为人工快捷清单，两边互为
  镜像、双向同步；
- **看板默认创建**：Bases 数据库驱动，改状态 / 标签即实时更新，可扩展视图；
- **归档与系统管理**：`07 归档` 按中文补零日期切分；`08 系统管理` 承载架构、
  分类、命名、Frontmatter、变更记录与用户手册；
- **插件集成规则**：初始化扫描插件、由用户确认规则写入隐藏配置 `.config/agent-rules.md`，
  每次变更操作前读取、操作后按规则执行（如先版本提交、再云同步）；
- **配置驱动、版本跟随**：目录与偏好全在 `.config/knowops.config.json`（单 vault），schema 版本跟随 skill 版本；
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
2. 初始化向导会逐步确认：vault 路径与名称、00–08 九个模块默认目录结构、GitHub
   暂存库同步（可选）、插件集成规则（写入 `.config/agent-rules.md`）、08 系统管理
   模板、06 看板；配置与日志固定写入 vault 内隐藏目录 `.config/`，HTML 镜像导出
   默认启用（`<vault>/.config/HTML-Export/`）。
3. 用到具体能力（CLI / Markdown / Bases / Canvas / 网页提取）时，按需加载对应
   工具型 skill。

日常用法示例：

| 你说 | agent 做 |
|---|---|
| 手机：记一下：XXX | everywhere-note 生成规范 md 条目 + 设置当晚 22:00 提醒；指定了暂存库且具备 GitHub 能力时同步上传 |
| 入库今天手机记的 | knowops 加载 desktop-ingest.md：优先收用户提供的内容；配置了暂存库时自动拉取 GitHub 新条目写入 `00 收件箱`，源文件归档至暂存库 |
| "记一个灵感：……" | 写入 `00 收件箱/灵感/`，补属性和标签 |
| "记录一个问题：FPGA 跨时钟域怎么处理" | 建问题笔记（`01 生活系统/问题/未解决/`），联动任务与日志 |
| "周五下午 3 点项目评审" | 建日程笔记 + 自动创建定时提醒 |
| "这个问题解决了" | 移入 `已解决`，更新属性，勾选任务 |
| "沉淀这个问题" | 判定知识类型交你确认 → 在 `02 知识系统` 建知识笔记并双向链接 |
| "审阅收件箱" | 逐条判断：沉淀到对应模块 / 删除 / 归档 |
| "建一个项目：xxx" | 在 `05 项目系统/进行中/xxx/` 建项目六文件 |

## 目录结构

```
KnowOps/
├── README.md / README.en.md / LICENSE / .gitignore / AGENTS.md
└── skills/
    ├── knowops/                     # 桌面端统一入口
    │   ├── SKILL.md                 # 触发 + 加载规则 + 通用红线
    │   ├── references/
    │   │   ├── workflow.md          # 业务流程规范（模型/分类/模块流程/日志/操作后流程）
    │   │   ├── init-config.md       # 初始化向导/GitHub暂存库/插件集成/配置与HTML导出/脚本
    │   │   ├── properties.md        # 属性/命名/目录/生命周期设计
    │   │   ├── redlines.md          # 执行层红线 + 直写例外
    │   │   └── desktop-ingest.md    # 暂存内容/GitHub暂存库拉取 → 00 收件箱
    │   ├── scripts/                 # html_export
    │   └── assets/
    │       ├── system-manage/       # 08 系统管理初始化模板（5 文件）
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
