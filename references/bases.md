# Obsidian Bases（.base）要点

`.base` 文件 = 合法 YAML。结构：`filters`（全局过滤）→ `formulas`（公式属性）→
`properties`（显示名）→ `views`（table / cards / list / map 视图）。

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

## 嵌入笔记

```markdown
![[任务看板.base]]
![[任务看板.base#进行中]]
```

完整函数参考见 Obsidian 官方文档 https://help.obsidian.md/bases/functions 。
