# Obsidian Bases（.base）要点

`.base` 文件 = 合法 YAML。结构：`filters`（全局过滤）→ `formulas`（公式属性）→
`properties`（显示名）→ `views`（table / cards / list / map / calendar 视图）。

## 创建与校验流程

1. `"<cliPath>" create path="<目录>/<名>.base" content="<YAML>" silent`
2. 回读校验：`"<cliPath>" read path="<同路径>"`；YAML 合法性可用 Python
   `import yaml` 或 CLI `base:query file="<名>"` 实测查询验证
3. 常见坑：公式含双引号时整体用单引号包裹；`formula.X` 必须在 `formulas` 中定义；
   日期相减得到 Duration，须先取 `.days` 等字段再运算

## 过滤语法

```yaml
filters:
  and:
    - 'status != "done"'
    - file.hasTag("task")
  # or: / not: 可嵌套
```

操作符：`==` `!=` `>` `<` `>=` `<=` `&&` `||` `!`；
常用函数：`file.hasTag()`、`file.inFolder()`、`date()`、`now()`、`today()`、`if()`。

## 示例 1：任务看板

```yaml
filters:
  and:
    - file.hasTag("task")
formulas:
  days_until_due: 'if(due, (date(due) - today()).days, "")'
  is_overdue: 'if(due, date(due) < today() && status != "done", false)'
properties:
  formula.days_until_due:
    displayName: "剩余天数"
views:
  - type: table
    name: "进行中"
    filters:
      and:
        - 'status != "done"'
    order:
      - file.name
      - status
      - due
      - formula.days_until_due
    groupBy:
      property: status
      direction: ASC
  - type: table
    name: "已完成"
    filters:
      and:
        - 'status == "done"'
    order:
      - file.name
      - finished_date
```

## 示例 2：阅读清单

```yaml
filters:
  or:
    - file.hasTag("book")
    - file.hasTag("article")
formulas:
  status_icon: 'if(status == "reading", "📖", if(status == "done", "✅", "📚"))'
views:
  - type: cards
    name: "书库"
    order:
      - file.name
      - author
      - formula.status_icon
  - type: table
    name: "待读"
    filters:
      and:
        - 'status == "to-read"'
    order:
      - file.name
      - author
```

## 示例 3：日记索引（按月目录 `日志/YYYY-MM/`）

```yaml
filters:
  and:
    - file.inFolder("日志")
    - '/^\d{4}-\d{2}-\d{2}$/.matches(file.basename)'
formulas:
  day_of_week: 'date(file.basename).format("dddd")'
views:
  - type: table
    name: "最近日记"
    limit: 30
    order:
      - file.name
      - formula.day_of_week
      - file.mtime
```

## 示例 4：日程日历（calendar 月历 + table 列表，v2.2.0）

```yaml
filters:
  and:
    - file.hasTag("日程")
views:
  - type: calendar
    name: "日程月历"
    dateField: date
  - type: table
    name: "即将到来"
    filters:
      and:
        - 'date >= today()'
    order:
      - date
      - file.name
```

> calendar 视图依赖 Obsidian 版本支持；不支持时回退纯 table（按 date 排序），
> 功能不受影响。`date` 属性须为 ISO 格式（如 `2026-08-07T15:00`）才能被识别为日期。

## 看板板块过滤要点（v2.2.0 可选组件，用户要求创建看板时参考）

| 板块 | 全局过滤 | 视图与列 |
|---|---|---|
| 问题看板 | `file.inFolder("<questionDir>")` | 视图：未解决（`status != "done"`）/ 已解决（`status == "done"`）；列：file.name / status / created / resolved / tags |
| 任务看板 | `file.hasTag("task")` | 视图：进行中 / 已完成；公式：`days_until_due`、`is_overdue`（逾期高亮）；列：file.name / due / status / tags |
| 日程日历 | `file.hasTag("日程")` | calendar（dateField=date）+ table「即将到来」（`date >= today()`） |
| 知识索引 | `type == "knowledge"` | table 按 `knowledge_type` 分组；列：file.name / knowledge_type / created / resolved / tags |
| 项目进展 | `file.inFolder("<projectsDir>")` | table 按项目名分组；列：file.name / status / created / tags |
| 剪藏列表 | `type == "clip"` | table 按 `clipped_at` 倒序；列：file.name / source_domain / clipped_at |
| 日记索引 | `file.inFolder("<dailyFolder>")` | table 按日期倒序；列：file.name / file.mtime |

> 看板是**用户指令指定的可选组件**（初始化询问或按需创建），不是 agent 日常
> 按需创建 Bases 的固化模板；上述过滤要点供生成看板时参考，agent 可按需调整。

## 嵌入笔记

```markdown
![[任务看板.base]]
![[任务看板.base#进行中]]
```

完整函数参考见 Obsidian 官方文档 https://help.obsidian.md/bases/functions 。
