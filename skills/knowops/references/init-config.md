# 知识库初始化与配置（init-config.md）

> 本文件是 knowops 的初始化、插件集成、配置与 HTML 导出流程。仅在初始化、配置、
> HTML 导出、插件集成维护等任务时加载；日常记录/整理/搜索/审阅走
> `references/workflow.md`。通用红线见 SKILL.md；执行层红线见 `references/redlines.md`。

## 初始化向导（首次接入知识库，按序逐项确认，不一次性抛所有问题）

1. 确认 vault 实际路径与名称（已注册 vault 供点选；未注册时按应用流程注册）。
2. 展示并确认默认目录结构（00–08 九个模块）；配置与日志固定写入 vault 内隐藏
   目录 `.config/`（不提供仓库外选项）；**内容模块目录按需创建（懒加载）**：
   初始化只预置 08 系统管理 与 06 看板，其余模块在首次写入时自动出现。
3. 写入配置文件（schema 版本跟随 skill 版本）。
4. 扫描当前知识库可用的插件/扩展能力。
5. 逐个确认插件集成规则（是否纳入、时机与顺序）。
6. 复制 `assets/system-manage/` 模板到 `08 系统管理/`（已存在不覆盖，询问
   保留/合并）。
7. 将插件集成规则写入 `Agent规则.md`（默认不写入机器配置）。
8. 创建 `06 看板/看板.md` + `看板.base`（默认视图）。
9. 配置原生日记（文件夹与日期格式），验证路径形态。
10. 默认启用 HTML 镜像导出（位置固定 `<vault>/.config/HTML-Export/`；复制脚本
    副本与 `html-export.json` 到 `.config/scripts/`）。
11. 写首条操作日志，反馈汇总（配置路径、插件规则、系统管理文档、看板、
    日记格式、导出状态）。

> 旧库接入：检测到与默认结构不一致的已有内容时，**不自动迁移**，现场向用户
> 确认处理方式（保持 / 部分调整 / 全量重构），结论写入 `Agent规则.md`。

## 插件集成（通用机制，不写死具体插件）

- 不写死任何插件名、流程或顺序；一切以**初始化时用户确认并写入
  `08 系统管理/Agent规则.md` 的规则**为准。
- 初始化时：扫描当前知识库可用的插件/扩展能力 → 逐个向用户确认是否纳入工作流、
  执行时机与顺序（如"修改后先版本提交、再同步"）→ 写入 `Agent规则.md`。
- 插件信息默认只存于 `Agent规则.md`（人读、可编辑）；自动化脚本确实需要
  机器可读数据时再补写配置，不提前落盘。
- 插件变动（安装/卸载/改规则）：更新 `Agent规则.md` 并记入 `变更记录.md`。

## 配置与 HTML 导出

- **配置文件**：`knowops.config.json`（固定 `<vault>/.config/`，初始化不提供
  位置选择）。键包括：`version`（跟随 skill 版本）、`defaultVault`、`vaults`、
  `exportRoot`（默认 `<vault>/.config/HTML-Export/`，可后续修改）、`cliPath`
  （工具路径，初始化时确认）、`preferences`（各模块目录与偏好，见
  `references/properties.md`）。
- **HTML 镜像导出**（默认启用）：把 vault 内笔记镜像导出为独立 HTML，增量同步、
  删除的笔记同步移除镜像；隐藏目录不导出；`08 系统管理` 属可见笔记，参与导出。
- **库内脚本副本（可改造）**：初始化时把导出/配置脚本复制到 `.config/scripts/`，
  此后导出一律运行库内副本；本 skill 内脚本只是默认模板；升级时副本与模板
  不一致则询问用户（覆盖/保留/对比）。
- **导出范围**：`.config/scripts/html-export.json` 控制 include/exclude（glob），
  隐藏目录始终不导出。

## 脚本一览（`--json` 输出机器可读结果，`-h` 查看参数）

| 脚本 | 用途 |
|---|---|
| `scripts/kb_config.py` | 配置与多 vault：init / find / add-vault / remove-vault / list / set-default / path / get / set / validate |
| `scripts/kb_env.py` | 环境自检：check / launch / cli-path |
| `scripts/html_export.py` | HTML 镜像导出（可选）：export / export-one |

> 具体调用方式与参数以各脚本 `-h` 输出为准；本文档不展开命令细节。
> 库内副本机制见「配置与 HTML 导出」。
