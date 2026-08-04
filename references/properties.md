# 属性、标签与目录结构约定（均为可配置默认值，非强制规范）

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
| `date` / `end` | 日程开始 / 结束时间（仅日程笔记，ISO 格式，Bases 日期类型） | `2026-08-07T15:00` / `2026-08-07T16:30` |
| `location` | 日程地点（仅日程笔记，可选） | `会议室A` |
| `tags` | 标签（也可用行内 `#tag`） | `[fpga, 日程, 知识/经验]` |
| `aliases` | 别名 | `[异步复位问题记录]` |

用户可自由增删；skill 不强制任何属性存在（`updated` 更新为例外，见上）。

## 标签与双向链接约定（v2.0 硬性要求）

- **积极打标签**：创建笔记时根据内容主动打层级标签，如 `#领域/fpga`、
  `#知识/经验`、`#课程/小梅哥`、`#项目/xxx`；
- 状态类信息优先用 `status` 属性（便于 Bases 过滤），状态标签不强制；
- **双向链接**：知识沉淀时知识笔记必须链接原问题；剪藏链接相关笔记；
  相关知识之间互相链接，确保知识索引；
- 标签与双向链接是 Bases 聚合与检索的基础（v2.0 起为硬性要求）。

## 默认目录模板（首次初始化时展示，用户确认后写入配置）

```
大知识库文件夹/                     ← vault 上级目录
├── obsidian-kb.config.json        # skill 配置（vault 外）
├── 用户手册.md                    # 用户手册（vault 外）
├── log/                           # 操作日志（vault 外，preferences.logDir）
│   └── YYYY-MM/YYYY-MM-DD.md      # 按年月/日切分，每次操作追加记录
├── HTML-Export/                   # HTML 导出（vault 外，名称可改）
└── <Obsidian Vault>/              # 名称由用户创建时自定，skill 不假设
    ├── 问题/                      # 问题管理（preferences.questionDir）
    │   ├── 未解决/                # 进行中（YYYY-MM-DD 文件名.md）
    │   └── 已解决/                # 已完成（YYYY-MM-DD 文件名.md，status=done + created/resolved）
    ├── 项目/                      # 项目（preferences.projectsDir）
    │   └── <项目名>/<记录>.md
    ├── 日志/                      # 原生日记（preferences.dailyFolder）
    │   └── YYYY-MM/YYYY-MM-DD.md  # 年月/日 两层（preferences.dailyFormat）
    ├── 日程/                      # 日程管理（v2.2.0，preferences.scheduleDir）
    │   └── YYYY-MM-DD 标题.md     # 每条日程一篇笔记（type: event + date/end/location/status）
    ├── 知识/                      # 知识沉淀（preferences.knowledgeDir，原「知识与经验」）
    │   ├── 经验/                  # 知识类型子目录（YYYY-MM-DD 标题.md，用到才建）
    │   ├── 原理/
    │   ├── 工具/
    │   ├── 设计/
    │   ├── 规范/
    │   ├── 案例/
    │   └── 模板/
    ├── 看板.md                    # 看板总览（v2.2.0 可选组件，preferences.dashboardFile，嵌入 Bases 视图）
    └── TODO.md                    # 唯一待办文件（preferences.todoFile，vault 根）
```

> **v2.0 变化**：
> - 剪藏 / 模板 / 附件 / Bases / Canvas 为**文件类型分类**，不再预设目录，
>   存放位置**以用户指令为准**（用户可能分散存放于多个文件夹）；
> - **无收件箱**：判断不出类型时询问用户归属，不静默写入；
> - **无归档目录**；问题内部按「未解决 / 已解决」切分；
> - 知识类型初始 7 类，未来可由 agent 动态添加并向用户确认。
>
> **v2.2.0 变化**：新增 `日程/` 内容模块（scheduleDir）与 `看板.md` 可选组件
> （dashboardFile，嵌入 Bases 视图）；日程带 `日程` 标签 + `date` 属性供 Bases 聚合；
> 待办/日程含时间信号时自动创建定时提醒（平台无关，见 SKILL.md「自动化提醒」）。

### 模块生命周期

- **问题**：记录于 `问题/未解决/`（`YYYY-MM-DD 文件名.md`，`status: pending`）；
  解决后移入 `问题/已解决/`（文件名不变），`status: done` + `created`（记录日期）+
  `resolved`（解决日期），TODO 勾选；沉淀时创建 `知识/<类型>/` 笔记并双向链接回原问题
  （原问题保留在已解决文件夹，不删除）。
- **知识**：`知识/<类型>/YYYY-MM-DD 标题.md`；属性 `type: knowledge` +
  `knowledge_type` + `created` + `resolved`（沉淀日期）；类型由 agent 判定并交用户审核。
- **日程**：`日程/YYYY-MM-DD 标题.md`；属性 `type: event` + `date`（开始时间 ISO）+
  `end` / `location`（可选）+ `status`（scheduled / done / cancelled）+ `日程` 标签；
  完成/取消只改 status 与 updated（不移动）；Bases 日历/表格视图自动聚合，
  改属性即时反映（及时更新）。
- **TODO.md**：问题 / 项目记录时自动追加
  `- [ ] [类型] 标题 → [[链接]]（YYYY-MM-DD 记录）`；人工待办也可直接写入；
  全库任务仍可用 `tasks` 与 Bases 视图聚合；
  **勾选完成后（v2.1.0）**：条目自动移入 TODO.md 底部「已完成」折叠块
  （callout `> [!success]- 已完成`，默认折叠），最新完成排最上、完成越久越靠下；
  **含时间信号的待办（v2.2.0）**：自动创建定时提醒，条目旁标注「已设提醒」。

配置键见 `kb_config.py list` 输出的 `preferences`；修改用
`kb_config.py set preferences.<键> <值>`（用户知情后进行）。
旧配置（v1）用 `kb_config.py migrate` 迁移（自动移除收件箱/文件类型目录键，
knowledgeDir 改名「知识」，补齐 logDir）。
