# Obsidian Bases（.base）语法要点

> Bases 是 Obsidian 原生的数据库式实时聚合视图（.base 文件 = 数据源）。
> 完整语法（filters / formulas / views / functions）以官方文档
> （help.obsidian.md/bases）为准，本文只收要点与常见坑。

## 文件结构

`.base` 文件是合法 YAML，包含：

```yaml
# 全局过滤（作用于所有视图）；可以是单个字符串，或 and/or/not 递归对象
filters:
  and:
    - 'status == "active"'
    - not:
        - 'file.hasTag("archived")'

# 计算属性（可在视图与公式中引用 formula.<名>）
formulas:
  days_until_due: 'if(due, (date(due) - today()).days, "")'

# 属性显示名等
properties:
  status:
    displayName: 状态

# 视图（一个 .base 可有多个视图）
views:
  - type: table        # table | cards | list（calendar 不支持，见下）
    name: "进行中"
    filters:
      and:
        - 'status != "done"'
    order:              # 展示的列
      - file.name
      - status
      - formula.days_until_due
```

## 过滤语法

- 单条件：`filters: 'status == "done"'`
- 组合：`and:` / `or:` / `not:` 递归嵌套
- 运算符：`==` `!=` `>` `<` `>=` `<=` `&&` `||` `!`
- 常用文件属性：`file.name` / `file.basename` / `file.path` / `file.folder` /
  `file.ext` / `file.size` / `file.ctime` / `file.mtime` / `file.tags` /
  `file.links` / `file.backlinks` / `file.embeds` / `file.properties`
- 常用函数：`file.hasTag("x")` / `file.inFolder("路径")` / `file.hasLink("笔记")`

## 公式要点

- `now()` / `today()` / `date(字符串)` / `if(条件, 真, 假)` / `duration(...)`；
- **日期相减得到 Duration 类型，不是数字**：先取字段再运算，如
  `(now() - file.ctime).days`；Duration 不支持直接 `.round()`；
- 属性可能缺失：用 `if()` 兜底，如 `'if(due, (date(due) - today()).days, "")'`；
- 引号规则：公式含双引号时整体用单引号包裹；
  `formula.X` 必须在 `formulas` 中定义，否则静默失效。

## 视图类型

- `table`（表格）/ `cards`（卡片）/ `list`（列表）/ `map`（地图，需 Maps 插件）；
- **⚠️ `calendar` 视图类型不受支持**（报"未知视图类型"）：日程类一律用
  `table`，按日期属性排序 +「即将到来」过滤（如 `date >= today()`）。

## 嵌入

```markdown
![[我的.base]]                 嵌入全部视图
![[我的.base#视图名]]          嵌入指定视图
```

## 常见坑

1. 未加引号的特殊字符（`: { } [ ] , & * # ? | < > = !` 等）破坏 YAML——字符串
   一律加引号；
2. 公式引号不匹配（双引号嵌套）——外层用单引号；
3. 日期属性须为 ISO 格式（如 `2026-08-07T15:00`）才能被识别为日期类型；
4. `.base` 创建后用查询校验（空结果也算 YAML 合法）。
