# 属性、标签与目录结构约定（均为可配置默认值，非强制规范）

## 默认核心属性集（frontmatter）

| 属性 | 说明 | 示例 |
|---|---|---|
| `type` | 笔记类型 | `question` / `note` / `clip` / `project` / `daily` |
| `status` | 状态 | `pending` / `in-progress` / `done` / `archive` |
| `source` | 来源（课程/文章/人物） | `小梅哥 2024 FPGA 教程` |
| `source_url` / `source_domain` | 网页剪藏来源 | `https://…` / `www.bilibili.com` |
| `clipped_at` | 剪藏时间（ISO） | `2026-08-03T10:00:00+08:00` |
| `created` / `updated` | 创建 / 更新时间 | `2026-08-03` |
| `resolved` | 问题解决日期（沉淀时标注） | `2026-08-15` |
| `due` / `finished_date` | 任务截止 / 完成时间 | `2026-08-10` |
| `tags` | 标签（也可用行内 `#tag`） | `[fpga, 课程/小梅哥]` |
| `aliases` | 别名 | `[异步复位问题记录]` |

用户可自由增删；skill 不强制任何属性存在。

## 标签约定建议

- 层级标签：`#课程/小梅哥`、`#fpga/复位`、`#项目/xxx`
- 状态类信息优先用 `status` 属性（便于 Bases 过滤），状态标签不强制
- 行内标签与 frontmatter `tags` 等效，按场景混用

## 默认目录模板（首次初始化时展示，用户确认后写入配置）

```
大知识库文件夹/                     ← vault 上级目录
├── obsidian-kb.config.json        # skill 配置（vault 外）
├── 用户手册.md                    # 用户手册（vault 外）
├── HTML-Export/                   # HTML 导出（vault 外，名称可改）
└── <Obsidian Vault>/              # 名称由用户创建时自定，skill 不假设
    ├── 问题/                      # 进行中的问题（preferences.questionDir）
    │   ├── <纯文字问题>.md        # 纯文字：单文件
    │   └── <含资源问题>/          # 含图片等资源：整个文件夹存放
    ├── 项目/                      # 项目（preferences.projectsDir）
    │   └── <项目名>/<记录>.md
    ├── 日志/                      # 原生日记（preferences.dailyFolder）
    │   └── YYYY-MM/YYYY-MM-DD.md  # 年月/日 两层（preferences.dailyFormat）
    ├── 知识与经验/                # 已解决问题的沉淀（preferences.knowledgeDir）
    ├── TODO.md                    # 唯一待办文件（preferences.todoFile，vault 根）
    ├── 40-Resources/Clips/        # 网页剪藏（preferences.clipDir）
    ├── 50-Archive/                # 归档
    ├── 99-Meta/
    │   ├── Templates/             # 模板（preferences.templateDir）
    │   ├── Bases/                 # .base 视图
    │   └── Canvas/                # .canvas 画布
    └── Attachments/               # 附件（preferences.attachmentDir）
```

> v1.3.0 起**不再有"普通笔记 → 收件箱"兜底**：判断不出类型时由 agent 询问用户
> 决策归属，不得静默写入。`inboxDir`（00-Inbox）配置键仅保留兼容，不再作为
> 默认路由目标。

### 模块生命周期

- **问题**：记录于 `问题/`；解决后移入 `知识与经验/`，属性标注 `created`
  （问题出现日期，勿改）、`resolved`（解决日期）、`status: done`，正文追加
  "经验总结"；TODO.md 中对应待办同步勾选（`task path=TODO.md line=<n> done`）。
- **TODO.md**：问题 / 项目记录时自动追加
  `- [ ] [类型] 标题 → [[链接]]（YYYY-MM-DD 记录）`；人工待办也可直接写入；
  全库任务仍可用 `tasks` 与 Bases 视图聚合。

配置键见 `kb_config.py list` 输出的 `preferences`；修改用
`kb_config.py set preferences.<键> <值>`（用户知情后进行）。
