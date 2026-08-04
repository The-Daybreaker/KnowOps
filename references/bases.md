# Bases 看板板块过滤要点（obsidian-kb 领域约定，仅供参考）

> Bases 的完整语法（filters / formulas / properties / views）、视图类型与函数
> 以 `@skill:obsidian-bases` 及官方文档为准；本文件只保留 obsidian-kb 生成
> 「总看板.base」时使用的板块过滤设计，**可能随 Obsidian 版本变化，需自行验证**。

## 看板板块（v2.2.0，动态生成：只加载已有模块）

| 板块 | 全局过滤 | 视图与列 |
|---|---|---|
| 问题看板 | `file.inFolder("<questionDir>")` | 视图：未解决（`status != "done"`）/ 已解决（`status == "done"`）；列：file.name / status / created / resolved / tags |
| 任务看板 | `file.hasTag("task")` | 视图：进行中 / 已完成；公式：`days_until_due`、`is_overdue`（逾期高亮）；列：file.name / due / status / tags |
| 日程日历 | `file.hasTag("日程")` | calendar（dateField=date，版本不支持则回退 table）+ table「即将到来」（`date >= today()`） |
| 知识索引 | `type == "knowledge"` | table 按 `knowledge_type` 分组；列：file.name / knowledge_type / created / resolved / tags |
| 项目进展 | `file.inFolder("<projectsDir>")` | table 按项目名分组；列：file.name / status / created / tags |
| 剪藏列表 | `type == "clip"` | table 按 `clipped_at` 倒序；列：file.name / source_domain / clipped_at |
| 日记索引 | `file.inFolder("<dailyFolder>")` | table 按日期倒序；列：file.name / file.mtime |

> 看板是**用户指令指定的可选组件**（初始化询问或按需创建），生成时只为**已有内容**
> 的模块创建视图（见 SKILL.md「看板」小节）；板块过滤为参考设计，agent 可按需调整。

## 经验备注（仅供参考）

- 公式含双引号时整体用单引号包裹；`formula.X` 必须在 `formulas` 中定义；
- 日期相减得到 Duration，须先取 `.days` 等字段再运算；
- `date` 属性须为 ISO 格式（如 `2026-08-07T15:00`）才能被 Bases 识别为日期类型；
- `.base` 创建后用 CLI 查询校验（空结果也算 YAML 合法）。
