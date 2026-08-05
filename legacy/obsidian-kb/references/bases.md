# Bases 看板板块过滤要点（obsidian-kb 领域约定，仅供参考）

> Bases 的完整语法（filters / formulas / properties / views）、视图类型与函数
> 以 `@skill:obsidian-bases` 及官方文档为准；本文件只保留 obsidian-kb 生成
> 看板时使用的板块过滤设计，**可能随 Obsidian 版本变化，需自行验证**。

## 看板结构（v2.3.2 定稿，动态生成：只加载已有模块）

- **`看板.md` + `看板.base` 两个文件，命名统一为「看板」**：`看板.base` 是数据源
  （`views` 数组承载各板块视图，每个视图各自过滤条件），看板.md 嵌入
  `![[看板.base#视图名]]`；**Bases 是 Obsidian 原生唯一实时聚合方案，必须有 .base
  数据源**（看板.md 只是嵌入容器）；
- **动态板块**：生成时只为**有内容的模块**创建视图（问题 / 任务 / 日程 / 知识 /
  项目 / 剪藏 / 日记）；板块首次出现内容时操作后流程自动增补视图；
- **⚠️ Bases 不支持 `calendar` 视图类型**（实测 Obsidian 1.13.4 报"未知视图类型"）——
  日程一律用 `table` 视图（按 `date` 排序 +「即将到来」过滤 `date >= today()`）。

## 看板板块（每个板块 = 看板.base 中的一个或多个视图）

| 板块 | 全局过滤 | 视图与列 |
|---|---|---|
| 问题 | `file.inFolder("<questionDir>")` | 视图：未解决（`status != "done"`）/ 已解决（`status == "done"`）；列：file.name / status / created / resolved / tags |
| 任务 | `file.hasTag("task")` | 视图：进行中 / 已完成；公式：`days_until_due`、`is_overdue`（逾期高亮）；列：file.name / due / status / tags |
| 日程 | `file.hasTag("日程")` | 视图：日程列表（按 date 排序）/ 即将到来（`date >= today()`）；**不用 calendar** |
| 知识 | `type == "knowledge"` | table 按 `knowledge_type` 分组；列：file.name / knowledge_type / created / resolved / tags |
| 项目 | `file.inFolder("<projectsDir>")` | table 按项目名分组；列：file.name / status / created / tags |
| 剪藏 | `type == "clip"` | table 按 `clipped_at` 倒序；列：file.name / source_domain / clipped_at |
| 日记 | `file.inFolder("<dailyFolder>")` | table 按日期倒序；列：file.name / file.mtime |

> 看板是**用户指令指定的可选组件**（初始化询问或按需创建），生成时只为**已有内容**
> 的模块创建视图（见 SKILL.md「看板」小节）；板块过滤为参考设计，agent 可按需调整。

## 经验备注（仅供参考）

- 公式含双引号时整体用单引号包裹；`formula.X` 必须在 `formulas` 中定义；
- 日期相减得到 Duration，须先取 `.days` 等字段再运算；
- `date` 属性须为 ISO 格式（如 `2026-08-07T15:00`）才能被 Bases 识别为日期类型；
- `.base` 创建后用 CLI 查询校验（空结果也算 YAML 合法）。
