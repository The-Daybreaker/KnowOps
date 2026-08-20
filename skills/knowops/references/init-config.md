# 知识库初始化与配置（init-config.md）

> 本文件是 knowops 的初始化、插件集成、配置与 HTML 导出流程。仅在初始化、配置、
> HTML 导出、插件集成维护等任务时加载；日常记录/整理/搜索/审阅走
> `references/workflow.md`。通用红线见 SKILL.md；执行层红线见 `references/redlines.md`。

## 初始化向导（首次接入知识库，按序逐项确认，不一次性抛所有问题）

1. 确认 vault 实际路径与名称（已注册 vault 供点选；未注册时按应用流程注册）。
2. 展示并确认默认目录结构（00–09 十个模块）；配置与日志固定写入 vault 内隐藏
   目录 `.config/`（不提供仓库外选项）；**内容模块目录按需创建（懒加载）**：
   初始化只预置 09 系统管理 与 07 看板，其余模块在首次写入时自动出现。
3. 由 agent 直接写 `.config/knowops.config.json`（schema 见下，默认值见
   `references/properties.md`）。
4. **GitHub 暂存库同步配置（可选）**：确认是否启用、仓库（owner/repo）、分支、
   本库在暂存库中的目录名（默认 = vault 文件夹名）；启用则写入配置 `githubSync`，
   不启用则不写入。
5. 扫描当前知识库可用的插件/扩展能力。
6. 逐个确认插件集成规则（是否纳入、时机与顺序），按 `assets/agent-rules.md` 模板
   写入 `.config/agent-rules.md`。
7. 复制 `assets/system-manage/` 模板到 `09 系统管理/`（已存在不覆盖，询问
   保留/合并）。
8. 创建 `07 看板/看板.md` + `看板.base`（默认视图，含「摘录-最近添加」）。
9. 配置原生日记（文件夹与日期格式），验证路径形态。
10. 若启用 HTML 导出（默认 `exportEnabled=true`）：复制 `scripts/html_export.py` 与
    `assets/html-export.json` 到 `.config/scripts/`；同时复制
    `scripts/vault_check.py`（结构校验脚本，始终复制）。
11. 写首条操作日志，反馈汇总（配置路径、GitHub 暂存库、插件规则、系统管理文档、
    看板、日记格式、导出状态）。

> 旧库接入：检测到与默认结构不一致的已有内容时，**不自动迁移**，现场向用户
> 确认处理方式（保持 / 部分调整 / 全量重构），结论写入 `.config/agent-rules.md`。

## 插件集成（通用机制，不写死具体插件）

- 不写死任何插件名、流程或顺序；一切以**初始化时用户确认并写入
  `.config/agent-rules.md` 的规则**为准。
- 初始化时：扫描当前知识库可用的插件/扩展能力 → 逐个向用户确认是否纳入工作流、
  执行时机与顺序（如"修改后先版本提交、再同步"）→ 写入 `.config/agent-rules.md`。
- 插件信息默认只存于 `.config/agent-rules.md`（人读、可编辑）；自动化脚本确实需要
  机器可读数据时再补写配置，不提前落盘。
- 插件变动（安装/卸载/改规则）：更新 `.config/agent-rules.md`。

## 配置与 HTML 导出

- **配置文件**：`.config/knowops.config.json`（单 vault，由 agent 直接读写）。键包括：
  `version`（跟随 skill 版本）、`vaultPath`、`exportRoot`（默认 `.config/HTML-Export`，
  相对 vault）、`exportEnabled`（默认 true）、`preferences`（各模块目录与偏好，见
  `references/properties.md`）。**配置只覆盖「配置层」约定；「规范层」固定约定见
  `references/workflow.md`「规范与配置的边界」**。
- **GitHub 暂存库同步（可选顶层键 `githubSync`）**：`enabled`（bool）/ `repo`
  （owner/repo）/ `branch`（默认 main）/ `folder`（本库在暂存库中的目录名，默认 =
  vault 文件夹名）。缺失或 `enabled=false` 视为未启用，入库时跳过 GitHub 检查。
  暂存库约定：根目录下每个知识库一个目录；`<folder>/` 根目录放待入库条目
  （everywhere-note 上传位置），`<folder>/归档/<YYYY年MM月DD日>/` 放已入库源文件
  （按入库当天日期切分，中文补零）。
- **agent 读的个性化约束**：`.config/agent-rules.md`（插件规则、额外红线、额外操作、
  旧库约定）；每次变更操作前读取（见 SKILL.md 红线 7）。
- **HTML 镜像导出**（默认启用，`exportEnabled=true`）：把 vault 内笔记镜像导出为
  独立 HTML，增量同步、删除的笔记同步移除镜像；隐藏目录不导出；`09 系统管理` 属
  可见笔记，参与导出。启用时，每次操作后按 `references/workflow.md` 的「操作后流程」
  增量导出。
- **库内脚本副本（可改造）**：初始化时把 `html_export.py` + `html-export.json` +
  `vault_check.py` 复制到 `.config/scripts/`，此后导出与校验一律运行库内副本；
  skill 内脚本只是默认模板；升级时副本与模板不一致则询问用户（覆盖/保留/对比）。
- **导出范围**：`.config/scripts/html-export.json` 控制 include/exclude（glob），
  隐藏目录始终不导出。

## 脚本一览（`--json` 输出机器可读结果，`-h` 查看参数）

| 脚本 | 用途 |
|---|---|
| `scripts/html_export.py` | HTML 镜像导出：export / export-one |
| `scripts/vault_check.py` | 结构面校验：check（指定笔记，输出 frontmatter 键值摘要，用于操作后核验）/ check-vault（全库巡检：目录与配置匹配、frontmatter 扫描，用于巡检、迁移前、升级后） |

> 具体调用方式与参数以脚本 `-h` 输出为准；本文档不展开命令细节。
