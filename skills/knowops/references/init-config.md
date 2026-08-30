# 知识库初始化与配置（init-config.md）

> 本文件是 knowops 的初始化、插件集成、配置与 HTML 导出流程。仅在初始化、配置、
> HTML 导出、插件集成维护等任务时加载；日常记录/整理/搜索/审阅走
> `references/workflow.md`。通用红线见 SKILL.md；执行层红线见 `references/redlines.md`。

## 初始化向导（首次接入知识库，按序逐项确认，不一次性抛所有问题）

1. 确认 vault 实际路径与名称（已注册 vault 供点选；未注册时按应用流程注册）。
2. 展示并确认**基础骨架**：`00 收件箱` / `01 知识` / `03 系统` / `04 归档`
   四个基础模块＋根目录看板（见 `references/properties.md` 目录骨架）；说明
   扩展模块机制——**你在库里新建文件夹、agent 来问规则并写进用户手册**，
   模块规则以用户手册为准。配置固定写入 vault 内隐藏目录 `.config/`（不提供
   仓库外选项）。**懒加载**：初始化预置 03 系统（用户手册、模板），并创建
   根目录看板；01 知识、收件箱、归档首次写入时自动出现（01 知识起步为空，
   首次写入时按 `03 系统/模板/主题文档模板.md` 的形状创建）。
3. **询问是否启用摘录模块**（预置扩展模块，示例）：展示用户手册摘录节摘要；
   **启用** → 执行登记（config `preferences.modules` 追加、建 `02 摘录/`
   文件夹、看板补视图）；**不启用** → 不建目录、不登记（手册摘录节保留，
   作为「模块规则怎么写」的第一个示例扩展模块）。
4. 由 agent 直接写 `.config/knowops.config.json`（`preferences.modules` 收录
   基础四模块与启用的扩展模块，schema 见 `references/properties.md`）。
5. **GitHub 暂存库同步配置（可选）**：确认是否启用、仓库（owner/repo）、分支、
   本库在暂存库中的目录名（默认 = vault 文件夹名）；启用则写入配置 `githubSync`，
   不启用则不写入。
6. 扫描当前知识库可用的插件/扩展能力。
7. 逐个确认插件集成规则（是否纳入、时机与顺序）与额外红线/操作/旧库约定
   （结论暂记，第 8 步复制手册后填入；v3.0.2 起约束并入手册「agent 约束」章，
   `.config/agent-rules.md` 不再使用；旧库遗留的该文件现场询问是否并入手册）。
8. 复制 `assets/system-manage/用户手册.md` 到 `03 系统/`（**已存在绝不覆盖**，
   询问保留/合并）；按确认结果把基础模块与已登记扩展模块的**实际目录名**填入
   手册「模块规则」章节（未启用的扩展模块保持示例标注），并把第 7 步确认的
   插件规则与额外红线/操作/旧库约定填入手册「agent 约束」章节；复制
   `assets/system-manage/变更记录.md` 到 `.config/变更记录.md`（库的结构与
   规则变更史，agent 维护；已存在不覆盖）。
9. 复制 `assets/templates/主题文档模板.md` 到 `03 系统/模板/`（共 1 份；
   已存在不覆盖），并引导用户启用 Obsidian 核心插件 **Templates**、把
   模板文件夹指向 `03 系统/模板`（设置路径：设置 → 核心插件 → Templates →
   模板文件夹位置）。模板里的时间用模板变量自动填写，无需手改。
10. **引导配置核心插件 Daily notes**（日记规则遵循 Obsidian 本身）：设置 →
    核心插件 → Daily notes → 新建文件位置填 `03 系统/日记`、日期格式填
    `YYYY/YYYY-MM-DD`（年份做子文件夹，实现按年切分）。
11. 创建根目录 `看板.md` ＋ `03 系统/看板.base`（基础视图：收件箱-待沉淀、
    知识-最近更新；摘录-最近添加仅启用摘录时创建；已登记扩展模块各对应
    一个视图，视图可扩展）。
12. 若启用 HTML 导出（默认 `exportEnabled=true`）：复制 `scripts/html_export.py`
    与 `assets/html-export.json` 到 `.config/scripts/`（json 的 exclude 目录路径
    按本库确认的 `dailyFolder`/`templatesDir` 改写；glob 分隔符必须用 `/`）；
    同时复制 `scripts/vault_check.py`（结构校验脚本，始终复制）。
13. 写首条日记（当日日记，agent 章「系统」小节追加初始化记录；日记为两章节
    结构，见 `references/workflow.md`「日记」），反馈汇总（配置路径、模块清单
    与登记状态、GitHub 暂存库、插件规则、用户手册（模块规则与 agent 约束
    位置）、变更记录位置、模板、看板、日记格式、导出状态）。

> **旧库接入安全底线**：检测到与基础骨架不一致的已有内容时，**不自动迁移**，
> 现场向用户确认处理方式（保持 / 部分调整 / 全量重构）；其中用户手建的模块
> 文件夹逐个走「模块发现与登记」流程（见 `references/workflow.md`），结论写入
> 用户手册「agent 约束」章节。动机：不背着用户拆数据——动用户的东西之前，
> 先问人。

## 插件集成（通用机制，不写死具体插件）

- 不写死任何插件名、流程或顺序；一切以**初始化时用户确认并写入用户手册
  「agent 约束」章节的规则**为准。
- 初始化时：扫描当前知识库可用的插件/扩展能力 → 逐个向用户确认是否纳入工作流、
  执行时机与顺序（如"修改后先版本提交、再同步"）→ 写入手册「agent 约束」章。
- 插件信息默认只存于手册「agent 约束」章（人读、可编辑）；自动化脚本确实需要
  机器可读数据时再补写配置，不提前落盘。
- 插件变动（安装/卸载/改规则）：更新手册「agent 约束」章。

## 配置与 HTML 导出

- **配置文件**：`.config/knowops.config.json`（单 vault，由 agent 直接读写）。键包括
  `version`（跟随 skill 版本）、`vaultPath`、`exportRoot`（默认 `.config/HTML-Export`，
  相对 vault）、`exportEnabled`（默认 true）、`preferences`（`modules` 模块清单、
  `dailyFolder`、`dailyFormat`、`templatesDir`，见 `references/properties.md`）。
  **配置只覆盖「配置层」约定；「规范层」固定约定见 `references/workflow.md`
  「规范与配置的边界」；模块规则正文在用户手册，config 只存机器索引。**
- **GitHub 暂存库同步（可选顶层键 `githubSync`）**：`enabled`（bool）/ `repo`
  （owner/repo）/ `branch`（默认 main）/ `folder`（本库在暂存库中的目录名，默认 =
  vault 文件夹名）。缺失或 `enabled=false` 视为未启用，入库时跳过 GitHub 检查。
  暂存库约定：根目录下每个知识库一个目录；`<folder>/` 根目录放待入库条目
  （everywhere-note 上传位置），`<folder>/归档/<YYYY年MM月DD日>/` 放已入库源文件
  （按入库当天日期切分，中文补零）。
- **agent 读的个性化约束**：用户手册「agent 约束」章节（插件规则、额外红线、
  额外操作、旧库约定；v3.0.2 起并入手册）；每次变更操作前读取（见 SKILL.md
  红线 7）。**内容规则**（模块归属、分类、命名）读手册「模块规则」章节。
- **HTML 镜像导出**（默认启用，`exportEnabled=true`）：把 vault 内笔记镜像导出为
  独立 HTML，增量同步、删除的笔记同步移除镜像；隐藏目录不导出。导出范围默认
  **排除**：`03 系统/日记/**`、`03 系统/模板/**`、`待审阅-*.md`（agent 写入审计
  用的运营件）、`.canvas` 等非笔记文件（日记是痕迹、模板是工具件、待审阅是
  运营件，都不是要读的内容）；`03 系统` 的其余可见笔记（用户手册）参与导出；
  `.config/`（含变更记录）属隐藏目录，始终不导出。启用时，每次操作后按
  `references/workflow.md` 的「操作后流程」增量导出。
- **库内脚本副本（可改造）**：初始化时把 `html_export.py` + `html-export.json` +
  `vault_check.py` 复制到 `.config/scripts/`，此后导出与校验一律运行库内副本；
  skill 内脚本只是默认模板；升级时副本与模板不一致则询问用户（覆盖/保留/对比）。
- **导出范围**：`.config/scripts/html-export.json` 控制 include/exclude（glob），
  隐藏目录始终不导出。

## 脚本一览（`--json` 输出机器可读结果，`-h` 查看参数）

| 脚本 | 用途 |
|---|---|
| `scripts/html_export.py` | HTML 镜像导出：export / export-one |
| `scripts/vault_check.py` | 结构面校验：check（指定笔记，输出 frontmatter 键值摘要，用于操作后核验）/ check-vault（全库巡检：目录与配置 modules 匹配、frontmatter 扫描，用于巡检、升级后核对）。**收件箱路径豁免、非 md 文件跳过、未登记目录只警告** |

> 具体调用方式与参数以脚本 `-h` 输出为准；本文档不展开命令细节。
