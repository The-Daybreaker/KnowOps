# 属性、标签与目录结构约定（knowledge-workflow 领域设计，均为可配置默认值）

> 本文档描述知识库的**领域设计**：属性含义、目录模板、模块生命周期。
> 属性的**写法**（frontmatter 语法）等具体形式不在本规范范围，本文不涉及。

## 默认核心属性集（frontmatter）

| 属性 | 说明 | 示例 |
|---|---|---|
| `type` | 笔记类型 | `question` / `knowledge` / `clip` / `project` / `daily` / `event` / `note` |
| `status` | 状态 | `pending` / `in-progress` / `done` / `scheduled` / `cancelled` |
| `knowledge_type` | 知识类型（仅知识笔记） | `经验` / `原理` / `工具` / `设计` / `规范` / `案例` / `模板` |
| `source` | 来源（课程/文章/人物） | `小梅哥 2024 FPGA 教程` |
| `source_url` / `source_domain` | 网页剪藏来源 | `https://…` / `www.bilibili.com` |
| `clipped_at` | 剪藏时间（ISO） | `2026-08-03T10:00:00+08:00` |
| `created` / `updated` | 创建 / 更新时间（**updated 每次修改必须更新，精确到分钟**） | `2026-08-04` / `2026-08-04T12:55` |
| `resolved` | 问题解决日期 / 知识沉淀日期 | `2026-08-15` |
| `due` / `finished_date` | 任务截止 / 完成时间 | `2026-08-10` |
| `date` / `end` | 日程开始 / 结束时间（仅日程笔记，ISO 格式） | `2026-08-07T15:00` / `2026-08-07T16:30` |
| `location` | 日程地点（仅日程笔记，可选） | `会议室A` |
| `tags` | 标签（也可用行内 `#tag`） | `[fpga, 日程, 知识/经验]` |
| `aliases` | 别名 | `[异步复位问题记录]` |

用户可自由增删；不强制任何属性存在（`updated` 更新为例外，见上）。

## 标签与双向链接约定（硬性要求）

- **积极打标签**：创建笔记时根据内容主动打层级标签，如 `#领域/fpga`、
  `#知识/经验`、`#课程/小梅哥`、`#项目/xxx`；
- 状态类信息优先用 `status` 属性（便于聚合过滤），状态标签不强制；
- **双向链接**：知识沉淀时知识笔记必须链接原问题；剪藏链接相关笔记；
  相关知识之间互相链接，确保知识索引；
- 标签与双向链接是聚合与检索的基础。

## 默认目录模板（首次初始化时展示，用户确认后写入配置）

```
<vault>/.config/                     ← vault 内隐藏目录（知识库无关文件默认存放处）
├── knowledge-workflow.config.json      # skill 配置（默认位置）
├── 用户手册.md                      # 用户手册（初始化时复制）
├── log/                            # 操作日志（preferences.logDir）
│   └── YYYY-MM/YYYY-MM-DD.md       # 按年月/日切分，每次操作追加记录
└── HTML-Export/                    # HTML 镜像导出（可选组件，preferences.exportDirName）
                                    # 默认 <vault>/.config/HTML-Export/，未启用则不建

<Obsidian Vault>/                   # 名称由用户创建时自定，流程不假设
├── 问题/                          # 问题管理（preferences.questionDir）
│   ├── 未解决/                    # 进行中（YYYY-MM-DD 文件名.md）
│   └── 已解决/                    # 已完成（YYYY-MM-DD 文件名.md，status=done + created/resolved）
├── 项目/                          # 项目（preferences.projectsDir）
│   └── <项目名>/<记录>.md
├── 日志/                          # 原生日记（preferences.dailyFolder）
│   └── YYYY-MM/YYYY-MM-DD.md      # 年月/日 两层（preferences.dailyFormat）
├── 日程/                          # 日程管理（preferences.scheduleDir）
│   └── YYYY-MM-DD 标题.md         # 每条日程一篇笔记（type: event + date/end/location/status）
├── 知识/                          # 知识沉淀（preferences.knowledgeDir）
│   ├── 经验/                      # 知识类型子目录（YYYY-MM-DD 标题.md，用到才建）
│   ├── 原理/
│   ├── 工具/
│   ├── 设计/
│   ├── 规范/
│   ├── 案例/
│   └── 模板/
├── 看板.md                        # 看板总览（可选组件，preferences.dashboardFile，嵌入 Bases 视图）
└── TODO.md                        # 唯一待办文件（preferences.todoFile，vault 根）
```

> 约定要点：
> - **知识库无关文件默认放 vault 内隐藏目录 `.config/`**（可改选其他位置）；
>   写入规则：允许隐藏目录，不写入用户笔记内容区；`.config/` 整体不进 HTML
>   导出、不参与看板聚合。
> - 剪藏 / 模板 / 附件 / Bases / Canvas 为**文件类型分类**，不预设目录，
>   存放位置**以用户指令为准**；
> - **无收件箱**：判断不出类型时自行判断归属（可新增模块），不静默写入；
> - **无归档目录**；问题内部按「未解决 / 已解决」切分；
> - 知识类型初始 7 类，未来可动态扩展（新增需经确认）。

## 模块生命周期

- **问题**：记录于 `问题/未解决/`（`YYYY-MM-DD 文件名.md`，`status: pending`）；
  解决后移入 `问题/已解决/`（文件名不变），`status: done` + `created`（记录日期）+
  `resolved`（解决日期），TODO 勾选；沉淀时创建 `知识/<类型>/` 笔记并双向链接回原问题
  （原问题保留在已解决文件夹，不删除）。
- **知识**：`知识/<类型>/YYYY-MM-DD 标题.md`；属性 `type: knowledge` +
  `knowledge_type` + `created` + `resolved`（沉淀日期）；类型在沉淀时判定
  （新增类型需经确认）。
- **日程**：`日程/YYYY-MM-DD 标题.md`；属性 `type: event` + `date`（开始时间 ISO）+
  `end` / `location`（可选）+ `status`（scheduled / done / cancelled）+ `日程` 标签；
  完成/取消只改 status 与 updated（不移动）。
- **TODO.md**：问题 / 项目记录时自动追加
  `- [ ] [类型] 标题 → [[链接]]（YYYY-MM-DD 记录）`；人工待办也可直接写入；
  **勾选完成后**：条目自动移入 TODO.md 底部「已完成」折叠块（默认折叠），
  最新完成排最上、完成越久越靠下；
  **含时间信号的待办**：自动创建定时提醒，条目旁标注「已设提醒」。

配置键见 `kb_config.py list` 输出的 `preferences`（kb_config 为 skill 自带脚本）；
修改用 `kb_config.py set preferences.<键> <值>`（用户知情后进行）。
旧配置用 `kb_config.py migrate` 迁移（自动补齐新键、移除废弃键；旧文件名
`obsidian-kb.config.json` 一并迁移到新文件名 `knowledge-workflow.config.json`）。
