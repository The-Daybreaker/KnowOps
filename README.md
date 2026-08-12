# KnowOps：Obsidian 知识管理 Skills

KnowOps 是一套面向 **AI agent** 的 **Obsidian 知识管理技能包**：用四个 skill 让 agent 帮你把
知识库管得井井有条——**业务流程规范 + 工具操作规范 + 调度入口 + 随身端捕获**，能力边界清晰、
配套使用。

## 这是什么

在 Obsidian 里管理个人知识库（收件箱捕获、问题跟踪、知识沉淀、项目、日程、任务、
看板、归档……）时，agent 需要两样东西：一是**内容怎么组织**（知识库有哪些模块、
收件箱如何审阅、问题如何从"未解决"走到"已沉淀"、知识与项目如何区分），二是
**怎么操作 Obsidian**（用官方 CLI 读写笔记、尊重删除红线、处理各种使用怪癖）。
本仓库把这两件事拆成两个互补的 skill，另加一个调度入口告诉 agent 按什么顺序加载，再加一个随身端捕获配套 skill：

| Skill | 定位 | 一句话 |
|---|---|---|
| **knowops-workflow** | 工作流程规范 | 知识库应该长什么样、流程怎么走——用户与 agent 共同遵守的中立规范 |
| **knowops-obsidian** | 工具操作规范 | "怎么操作 Obsidian"——CLI 用法、操作红线、语法要点 |
| **knowops-navigator** | 调度入口 | "按什么顺序加载"——先定流程、再定操作、工具按需 |
| **everywhere-note** | 随身端捕获与统一入库 | 手机 @ 即记，生成规范 md 并设 22:00 提醒；电脑端统一入库 |

## 特性

- **收件箱捕获与审阅**：顿悟、灵感、想法等简短零碎内容默认进 `00 收件箱`
  （随手记 / 灵感 / 待整理内容）；审阅时按"未来怎么用"沉淀、删除或归档；
- **随身端捕获与统一入库**：手机/随身设备上 @ everywhere-note 直接口述记录，生成符合知识库格式的 md（支持生成文件）并设 22:00 提醒；回到电脑后由 knowops-navigator 路由批量写入 `00 收件箱`；手机端只装这一个 skill 即可独立使用，不依赖传输通道；
- **问题全生命周期**：未解决 → 研究中 → 已解决 → 已沉淀；沉淀后原问题移入
  已沉淀并**双向链接**回知识笔记；
- **知识沉淀**：按类型归类（概念原理 / 经验方法 / 方案 / 案例），领域二级目录
  **用到才建**，增长触发拆分（<50 不拆 / 50~150 建二级 / >150 评估三级）；
- **资产与规范系统**：模板 / 工作流可复用，原则 / 标准规范 / 检查清单应遵守；
- **项目系统**：进行中 / 已完成 / 项目复盘，项目六文件模板；
- **日程 + 自动化提醒**：一句话录入，含明确时间信号自动创建定时提醒；
- **任务双轨同步**：任务笔记为看板数据源，TODO.md 为人工快捷清单，两边互为
  镜像、双向同步；
- **看板默认创建**：Bases 数据库驱动，改状态 / 标签即实时更新，可扩展视图；
- **归档与系统管理**：`07 归档` 按中文补零日期切分；`08 系统管理` 承载架构、
  分类、命名、Frontmatter、Agent 规则、变更记录与用户手册；
- **插件集成规则**：初始化扫描插件、由用户确认规则写入 `08 系统管理/Agent规则.md`，
  每次操作前必读、操作后按规则执行（如先版本提交、再云同步）；
- **配置驱动、版本跟随**：目录与偏好全在配置中，schema 版本跟随 skill 版本；
- **数据安全红线**：改删前征求同意、删除永远进系统回收站、**永不做彻底删除**、
  永不代用户初始化仓库。

## 安装

把 `skills/` 下的四个 skill（`knowops-workflow`、`knowops-obsidian`、
`knowops-navigator`、`everywhere-note`）复制到你的 agent 的**用户级 skill 目录**（位置因平台而异，按
你所使用平台的 skill 安装说明为准；一般形如 `~/.<平台>/skills/`），或直接克隆
本仓库：

```sh
git clone https://github.com/The-Daybreaker/KnowOps.git
# 然后把 skills/ 下四个目录复制到用户级 skill 目录
```

> **随身端**：手机/随身设备端可只安装 `everywhere-note`（其随身端部分独立自洽，不依赖本套件）。

> **依赖**：`knowops-obsidian` 引用的工具型 skill（obsidian-cli / obsidian-markdown /
> obsidian-bases / json-canvas / defuddle）来自 Obsidian 官方技能仓库
> [kepano/obsidian-skills](https://github.com/kepano/obsidian-skills)，需另行安装
> （见「相关项目」）。

## 快速开始

1. 加载 `knowops-navigator`（调度入口），再加载 `knowops-workflow`，运行**初始化向导**：
   - 确认 vault 实际路径与名称；
   - 确认 8+1 模块默认目录结构与配置位置（默认 vault 内隐藏目录 `.config/`）；
   - 扫描已安装插件，逐个确认集成规则（是否纳入、时机与顺序），写入
     `08 系统管理/Agent规则.md`；
   - 复制 `08 系统管理` 全套模板；默认创建 `06 看板`；可选启用 HTML 镜像导出。
2. 操作 Obsidian 时，遵循 `knowops-obsidian` 的红线与操作规范（CLI 用法、删除纪律、
   回读校验等）。
3. 用到具体能力（CLI / Markdown / Bases / Canvas / 网页提取）时，按需加载对应
   工具型 skill。

日常用法示例：

| 你说 | agent 做 |
|---|---|
| 手机：记一下：XXX | 生成规范 md 条目 + 设置当晚 22:00 提醒 |
| 入库今天手机记的 | knowops-navigator 路由加载 everywhere-note 桌面部分，解析暂存内容写入 `00 收件箱` |
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
├── README.md / README.en.md / LICENSE / .gitignore
└── skills/
    ├── knowops-workflow/          # Skill A：工作流程规范
    │   ├── SKILL.md
    │   ├── references/properties.md   # 属性/命名/目录/生命周期设计
    │   ├── scripts/                  # kb_config / kb_env / html_export
    │   └── assets/
    │       ├── system-manage/        # 08 系统管理初始化模板（7 文件）
    │       └── html-export.json      # HTML 导出范围配置模板
    ├── knowops-obsidian/                  # Skill B：Obsidian 操作规范与红线
    │   ├── SKILL.md
    │   └── references/              # redlines / cli / markdown / bases / canvas
    ├── knowops-navigator/               # Skill C：调度入口（加载顺序指引）
    │   └── SKILL.md
    └── everywhere-note/              # Skill D：随身端捕获与电脑端入库
        ├── SKILL.md
        ├── references/              # mobile-capture / desktop-ingest
        └── assets/capture-template.md
```

## Roadmap（未来方向）

- 手机端 agent 若获得 GitHub / 坚果云等文件同步能力：随身端自动把暂存条目同步到对应平台，电脑端设定时任务拉取并写入知识库；
- 手机端向电脑端发送提醒，触发电脑端自动化执行收集入库。

以上为未实现的未来方向，已记录于开发文档，供后续实现。

## 相关项目

工具型 skill 是 **Obsidian 官方技能仓库**的安装副本，可随官方更新：

- [kepano/obsidian-skills](https://github.com/kepano/obsidian-skills) ——
  Obsidian 官方 agent skills（obsidian-cli / obsidian-markdown / obsidian-bases /
  json-canvas / defuddle）
- [kepano/defuddle](https://github.com/kepano/defuddle) —— 网页正文提取库

## 许可证

MIT License，见 [LICENSE](LICENSE)。