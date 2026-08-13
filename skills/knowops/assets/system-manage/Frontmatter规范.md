# Frontmatter 规范（本库定制）

> 本文件记录当前知识库 frontmatter 属性与标签约定，供你了解。

## 核心属性

| 属性 | 说明 |
|---|---|
| `type` | capture / question / knowledge / principle / standard / checklist / template / workflow / project / daily / event / task / review / archive / system |
| `capture_kind` | 收件箱子类：随手记 / 灵感 / 待整理内容 |
| `knowledge_type` | 知识类型：概念原理 / 经验方法 / 方案 / 案例 |
| `domain` | 领域（知识系统重点使用） |
| `status` | pending / in-progress / done / scheduled / cancelled / active / completed |
| `precipitated` | 问题已沉淀标记（true 或日期） |
| `created` / `updated` | 创建/更新时间；**updated 每次修改必须更新，精确到分钟** |
| `resolved` | 解决/沉淀日期 |
| `due` / `finished_date` | 任务截止/完成时间 |
| `date` / `end` / `location` | 日程时间与地点 |
| `source` / `source_url` | 来源 |
| `project` | 项目归属 |
| `tags` | 层级标签 |

## 标签约定

- 积极打层级标签：`#领域/ai`、`#知识/概念原理`、`#项目/xxx`、`#日程`；
- 状态类信息优先用 `status` 属性，不依赖状态标签；
- 列表类标签用行内数组 `tags: [a, b]`。

## 硬性要求

1. 修改任何笔记后 `updated` 必须更新（精确到分钟）；
2. 沉淀/归档/相关知识之间建立双向链接；
3. 本库额外属性约定（如有）：
