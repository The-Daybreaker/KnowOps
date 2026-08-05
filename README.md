# Obsidian 知识库管理 Skills

一套面向 AI agent 的 **Obsidian 知识库管理技能包**：用三个 skill 让 agent 帮你把
知识库管得井井有条——**业务流程规范 + 工具操作规范 + 调度入口**，能力边界清晰、
配套使用。

## 这是什么

在 Obsidian 里管理个人知识库（问题跟踪、知识沉淀、日程、待办、看板……）时，
agent 需要两样东西：一是**内容怎么组织**（知识库该有哪些模块、问题怎么从
"未解决"走到"已解决"再到"沉淀成知识"），二是**怎么操作 Obsidian**（用官方 CLI
读写笔记、遵守删除红线、处理各种使用怪癖）。本仓库把这两件事拆成两个互补的
skill，另加一个调度入口告诉 agent 按什么顺序加载：

| Skill | 定位 | 一句话 |
|---|---|---|
| **knowledge-workflow** | 工作流程规范 | 知识库"该长什么样、流程怎么走"——用户与 agent 共同遵守的中立规范 |
| **kb-obsidian** | 工具操作规范 | "怎么操作 Obsidian"——CLI 用法、操作红线、语法要点 |
| **obsidian-suite** | 调度入口 | "按什么顺序加载"——先定流程、再定操作、工具按需 |

## 特性

- **问题全生命周期**：未解决 → 已解决 → 沉淀分离；解决后沉淀为知识笔记并**双向链接回原问题**（原问题保留）；
- **知识沉淀**：按类型归档（经验 / 原理 / 工具 / 设计 / 规范 / 案例 / 模板），**用到才建**、可动态扩展；
- **日程 + 自动化提醒**：一句话录入（"周五下午 3 点项目评审"），含明确时间信号自动创建定时提醒；
- **TODO 统一管理**：集中待办文件，勾选完成自动归入「已完成」折叠块，最新完成排最上；
- **看板实时聚合**：Bases 视图读取笔记属性，改状态/标签即自动更新，无需手动刷新；
- **网页剪藏 / 原生日记 / 操作日志**：每次操作（含读取/搜索）都留痕；
- **配置驱动、可迁移**：不假设任何 vault 名/路径，一切以配置为准，旧配置一键迁移；
- **数据安全红线**：改删前征求同意、删除永远进系统回收站、**永不永久删除**、永不代初始化仓库。

## 安装

将 `skills/` 目录下的三个 skill（`knowledge-workflow`、`kb-obsidian`、
`obsidian-suite`）复制到你的 agent 的**用户级 skill 目录**（位置因平台而异，
以你所使用平台的 skill 安装说明为准；一般形如 `~/.<平台>/skills/`），或直接
clone 本仓库：

```sh
git clone https://github.com/The-Daybreaker/knowledge-base.git
# 然后把 skills/ 下三个目录复制到用户级 skill 目录
```

> **依赖**：`kb-obsidian` 引用的工具型 skill（obsidian-cli / obsidian-markdown /
> obsidian-bases / json-canvas / defuddle）来自 Obsidian 官方技能仓库
> [kepano/obsidian-skills](https://github.com/kepano/obsidian-skills)，需另行安装
> （见「相关项目」）。

## 快速开始

1. 加载 `obsidian-suite`（调度入口），按指引加载 `knowledge-workflow`，运行
   **初始化向导**接入知识库：
   - 确认 vault 实际路径与名称；
   - 配置默认写入 vault 内隐藏目录 `.config/`（可改选其他位置）；
   - 按需启用 HTML 镜像导出、创建看板。
2. 操作 Obsidian 时，遵循 `kb-obsidian` 的红线与操作规范（CLI 用法、删除纪律、
   回读校验等）。
3. 用到具体能力（CLI / Markdown / Bases / Canvas / 网页提取）时，按需加载
   对应工具型 skill。

日常用法示例：

| 你说 | agent 做 |
|---|---|
| "记录一个问题：FPGA 跨时钟域怎么处理" | 建问题笔记（`问题/未解决/`），补属性标签，联动 TODO 与日志 |
| "周五下午 3 点项目评审" | 建日程笔记 + 自动创建定时提醒 |
| "这个问题解决了" | 移入 `问题/已解决/`，更新属性，勾选 TODO |
| "沉淀这个问题" | 判定知识类型，创建知识笔记并双向链接回原问题 |

## 目录结构

```
knowledge-base/
├── README.md / README.en.md / LICENSE / .gitignore
└── skills/
    ├── knowledge-workflow/          # Skill A：工作流程规范
    │   ├── SKILL.md
    │   ├── references/properties.md   # 属性/目录/生命周期领域设计
    │   ├── scripts/                  # kb_config / kb_env / html_export
    │   └── assets/user-manual.md     # 用户手册模板
    ├── kb-obsidian/                  # Skill B：Obsidian 操作规范与红线
    │   ├── SKILL.md
    │   └── references/              # redlines / cli / markdown / bases / canvas
    └── obsidian-suite/               # Skill C：调度入口（加载顺序指引）
        └── SKILL.md
```

## 相关项目

工具型 skill 为 **Obsidian 官方技能仓库**的安装副本，可随官方更新：

- [kepano/obsidian-skills](https://github.com/kepano/obsidian-skills) ——
  Obsidian 官方 agent skills（obsidian-cli / obsidian-markdown / obsidian-bases /
  json-canvas / defuddle）
- [kepano/defuddle](https://github.com/kepano/defuddle) —— 网页正文提取库

## 许可证

MIT License，见 [LICENSE](LICENSE)。
