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
    ├── 00-Inbox/                  # 收件箱（preferences.inboxDir）
    ├── 10-Daily/                  # 原生日记（preferences.dailyFolder）
    │   └── YYYY-MM/YYYY-MM-DD.md  # 年月/日 两层（preferences.dailyFormat）
    ├── 20-Projects/               # 项目
    ├── 30-Areas/                  # 领域/主题
    ├── 40-Resources/              # 资源（剪藏在 Clips/，preferences.clipDir）
    ├── 50-Archive/                # 归档
    ├── 99-Meta/
    │   ├── Templates/             # 模板（preferences.templateDir）
    │   ├── Bases/                 # .base 视图
    │   └── Canvas/                # .canvas 画布
    └── Attachments/               # 附件（preferences.attachmentDir）
```

配置键见 `kb_config.py list` 输出的 `preferences`；修改用
`kb_config.py set preferences.<键> <值>`（用户知情后进行）。
