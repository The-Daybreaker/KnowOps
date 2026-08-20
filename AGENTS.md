# AGENTS.md — KnowOps

> 本文件随仓库发布到 GitHub，只承载可公开、面向使用者的内容；项目开发与维护的
> 完整规范位于开发工作区的私有指引（由平台自动加载）。仓库内的 `private/`
> 文件夹存放开发期文档（不进 git、不对外发布）；**承担开发、测试、发布等维护
> 任务时必须先完整阅读该文件夹**，其规范与本文件冲突时以 `private/` 为准。

## 项目概览

- **定位**：面向 AI agent 的 Obsidian 知识管理 skill 包，单仓库两 skill，统一版本号
  一起发布。
- `skills/knowops/`：桌面端统一入口（知识库怎么组织 + Obsidian 怎么操作）。
- `skills/everywhere-note/`：随身端捕获（手机 @ 即记，生成规范 md + 22:00 提醒；
  可选 GitHub 暂存库同步）。
- `skills/automation-prompt-template.md`：自动化入库提示词模板（设置定时自动化时
  使用）。
- **版本**：两 skill 统一版本号，以各 SKILL.md frontmatter 的 `metadata.version`
  为准。
- 同一设备不要同时安装两个 skill（触发竞争），README 已注明。

## 仓库布局

git 跟踪：`README.md`、`README.en.md`、`LICENSE`、`.gitignore`、`AGENTS.md`
（本文件）、`skills/`（两 skill 的全部运行时文件 + automation-prompt-template.md）、
`tools/`（开发期校验脚本 check.py）、`.github/workflows/`（CI）。

克隆本仓库后，把 `skills/` 下对应 skill 目录复制到 agent 的用户级 skill 目录即可
安装（详见 README）。

## 架构要点

- **单 vault 配置**：`<vault>/.config/knowops.config.json`，由 agent 直接读写；
  schema 为 `version / vaultPath / exportRoot / exportEnabled / preferences`，
  可选顶层键 `githubSync`（GitHub 暂存库同步：`enabled/repo/branch/folder`）。
- **每次对话前置（bootstrap）**：定位 vault → 读配置 → 读 `.config/agent-rules.md`
  （若存在）→ 缺配置则按 `references/init-config.md` 初始化。任何新对话都能从零
  接手知识库。
- **约束收口**：agent 读的个性化约束统一存 `.config/agent-rules.md`；`09 系统管理/`
  只放 5 份用户可见文档，agent 不读。
- **库内脚本**：`html_export.py`（HTML 镜像导出，与 `html-export.json` 配对，
  导出默认启用）与 `vault_check.py`（结构面校验：frontmatter 可解析/必填属性/
  type 枚举），均自包含（标准库），初始化复制到 `.config/scripts/`。
- **模块结构**：00 收件箱 → 05 项目系统 + 06 摘录系统（长篇/短篇摘录，含
  超量拆分）+ 07 看板 → 08 归档 → 09 系统管理；看板、归档与系统管理固定
  最后三位，新模块插入其前顺延编号。
- **两 skill 依赖方向**：knowops 解析 everywhere-note 的 capture 产物（字段契约
  `type/capture_kind/created/tags/文件名`，capture_kind 含 `摘录`）；everywhere-note
  不依赖 knowops。**改契约必须两端同步**（desktop-ingest.md ↔ mobile-capture.md）。
- **GitHub 暂存库同步（可选）**：手机端在用户指定暂存库且具备 GitHub 能力时上传
  条目到暂存库 `<folder>/`；knowops 入库时拉取新条目、并把源文件归档到暂存库
  `<folder>/归档/<入库日期>/`。暂存库目录约定两端同步。
- **操作后核验**：每次写入/修改/移动/删除/归档后核验，缺失即补正——结构面
  （frontmatter 可解析/必填属性/type 枚举/命名）由库内脚本 `vault_check.py`
  输出键值摘要、agent 扫读（批量 ≥3 篇时抽 1 篇全文回读）；语义面（双链/
  操作日志与日记同步/任务双轨/插件与导出）由 agent 回读核验。
- 工具型 skill（obsidian-cli / obsidian-markdown / obsidian-bases / json-canvas /
  defuddle）来自 [kepano/obsidian-skills](https://github.com/kepano/obsidian-skills)，
  不随本项目打包；knowops 只引用、不复制其内容。

## skill 内部结构约定

- knowops 的 SKILL.md 只承载触发、前置引导、加载规则与通用红线；references 按需
  加载（workflow / redlines / init-config / desktop-ingest / properties）。
- workflow.md 保持**工具无关的中立规范**视角，不写工具名/命令/委托链。
- `assets/system-manage/` 是 08 系统管理的 5 份**用户文档模板**（自洽自足：只引用
  08 系统管理 内部文档与知识库本身）；初始化复制、已存在不覆盖。
- `everywhere-note` 独立自洽：SKILL.md + references/mobile-capture.md +
  assets/capture-template.md。
- 两 skill 的 SKILL.md frontmatter 均含 `metadata.version`，跟随当前版本。

## 通用红线（对知识库操作）

1. **删除永远进系统回收站且可恢复**。
2. **变更分级**：高风险操作先展示方案、征得同意后执行；低风险先执行、随后记录。
3. **不代为 `git init`**。
4. **信息以用户给出为准**。
5. **创建前相似检查**。
6. **重要写入后回读校验**。
7. **变更操作前读取 `.config/agent-rules.md`**。
