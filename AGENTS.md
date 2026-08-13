# AGENTS.md — KnowOps 开发指南

> 本文件是**在本仓库工作的 agent 的唯一权威入口**。任何新对话/新 agent 从本文档
> 开始：读完即可独立完成本仓库的维护、测试与发布，不依赖历史对话或任何 agent
> 私有记忆（`.workbuddy/` 等仅为本地工作日志）。完整工作流与开发规范见
> `dev/DESIGN.md`。

## 项目概览

- **定位**：面向 AI agent 的 Obsidian 知识管理 skill 包，单仓库两 skill，统一版本号
  一起发布。
- `skills/knowops/`：桌面端统一入口（知识库怎么组织 + Obsidian 怎么操作）。
- `skills/everywhere-note/`：随身端捕获（手机 @ 即记，生成规范 md + 22:00 提醒）。
- **当前版本**：1.2.1（`dev/CHANGELOG.md` 有完整历史）。
- 同一设备不要同时安装两个 skill（触发竞争），README 已注明。

## 仓库布局与版本管理

git 跟踪：`AGENTS.md`、`README.md`、`README.en.md`、`LICENSE`、`.gitignore`、
`skills/`（两 skill 的全部运行时文件）。

本地维护、不进 git：`dev/`（开发期文档）、`dist/`（发布产物，可重建）、`test/`
（本地测试知识库）、`.test-env/`（测试脚本）、`.workbuddy/`（agent 工作日志）。
开发与测试都在本工作区进行；克隆到新机器只用于安装 skill。

改动惯例（用户已拍板）：**每次改动完成后自动执行发布**；版本号默认只升最后一位，
第一位/中间位仅用户要求时升。

## 架构要点（当前版本）

- **单 vault 配置**：`<vault>/.config/knowops.config.json`，由 agent 直接读写；
  schema 为 `version / vaultPath / exportRoot / exportEnabled / preferences`。
- **每次对话前置（bootstrap）**：定位 vault → 读配置 → 读 `.config/agent-rules.md`
  （若存在）→ 缺配置则按 `references/init-config.md` 初始化。任何新对话都能从零
  接手知识库。
- **约束收口**：agent 读的个性化约束统一存 `.config/agent-rules.md`；`08 系统管理/`
  只放 5 份用户可见文档，agent 不读。
- **HTML 镜像导出**：`html_export.py` 自包含（标准库），初始化复制到
  `.config/scripts/` 与 `html-export.json` 配对；导出默认启用。
- **两 skill 依赖方向**：knowops 解析 everywhere-note 的 capture 产物（字段契约
  `type/capture_kind/created/tags/文件名`）；everywhere-note 不依赖 knowops。
  **改契约必须两端同步**（desktop-ingest.md ↔ mobile-capture.md）。
- **通用红线 7 条**：删除进回收站、变更分级、不代为 git init、信息以用户为准、
  创建前相似检查、重要写入后回读、变更前读 agent-rules（见 knowops SKILL.md）。
- 工具型 skill（obsidian-cli / obsidian-markdown / obsidian-bases / json-canvas /
  defuddle）来自 [kepano/obsidian-skills](https://github.com/kepano/obsidian-skills)，
  不随本项目打包；knowops 只引用、不复制其内容。

## skill 内部结构约定

- knowops 的 SKILL.md 只承载触发、前置引导、加载规则与通用红线；references 按需
  加载（workflow / redlines / init-config / desktop-ingest / properties）。
- workflow.md 保持**工具无关的中立规范**视角，不写工具名/命令/委托链。
- `assets/system-manage/` 是 08 系统管理的 5 份**用户文档模板**（自洽自足：只引用
  08 系统管理 内部文档与知识库本身，不依赖 skill 侧给 agent 读的文档）；初始化复制、
  已存在不覆盖；**改动模板必须同步** workflow.md、properties.md、README（中英）。
- `everywhere-note` 独立自洽：SKILL.md + references/mobile-capture.md +
  assets/capture-template.md。

## 开发工作流（强制，详见 dev/DESIGN.md）

需求提出 → 讨论对齐并**复述需求** → 用户确认后开工 → 实施并**同步更新受影响文档**
（CHANGELOG / DESIGN / README / TEST-REPORT，改动完成即文档就绪）→ 验证（结构
校验 + 脚本级 + **test/ 测试知识库真实测试**）→ 展示成果 + 自动打包、提交、推送、
安装到各 agent → 汇报（附完成检查清单）。

## 测试（发布前必跑）

1. **结构校验**：skill-creator 的 quick_validate.py（须 `PYTHONUTF8=1`，且 Python
   需带 PyYAML；Codex 受管运行时自带）。
2. **脚本级**：`python .test-env/kb_test.py`（html_export，临时目录，不需 Obsidian）。
3. **真实测试（发布前必做）**：在 `test/Obsidian测试知识库` 执行实际场景测试
   （CLI 创建/回读、操作日志、HTML 导出、删除进回收站）；可运行
   `python .test-env/forward_test.py`（需 Obsidian 运行 + 测试库已注册；前置不满足
   时 exit 2，不自动拉起）。Obsidian 未运行则请用户打开后再测，**未通过不发布**。
4. 测试库基建：`test/Obsidian测试知识库/.config/` 按当前版本初始化（knowops.config.json
   + scripts 副本 + agent-rules.md）。

## 发布流程（每次改动完成后执行，md 驱动、agent 执行，无脚本）

1. 版本默认只升最后一位；更新 `dev/CHANGELOG.md` 顶部条目。
2. 打包：`dist/<version>/` 下为两 skill 各生成 `<skill>-v<version>-<timestamp>.zip`，
   zip 内以 `<skill名>/` 为根，**只含运行时文件**（SKILL.md、references/、scripts/、
   assets/），排除 `__pycache__`、`*.pyc`、`.git`。
3. `git add -A -- .` + `git commit -m "feat:/fix:/docs: v<version> - 描述"`
   （永不 git init）。
4. `git push`（origin = git@github.com:The-Daybreaker/KnowOps.git，分支 master）。
5. 安装：复制 `skills/knowops`、`skills/everywhere-note` 到各平台用户级 skill 目录
   （Codex `~/.codex/skills/`、WorkBuddy `~/.workbuddy/skills/`、QoderWork
   `~/.qoderwork/skills/`，可调整），确认各目标 `SKILL.md` 存在。

## 文档职责划分

| 文档 | 职责 |
|---|---|
| `AGENTS.md` | 开发入口与当前状态（本文件，唯一常青记忆） |
| `dev/DESIGN.md` | 当前设计 + 开发工作流 + 开发规范 |
| `dev/CHANGELOG.md` | 完整版本历史（每次发布必更新） |
| `dev/TEST-REPORT.md` | 当前测试记录与运行方式 |
| `README.md` / `README.en.md` | 面向使用者/安装者，双语同步 |
| skill 内 references/assets | 运行时给 agent/用户读的规范与模板 |

## 环境与已知坑

- Obsidian CLI：`D:\AppGallery\Software\Obsidian\Obsidian.com`（1.13.4），**需
  Obsidian 正在运行**；写操作参数形态：create 用 `path=`、search 用 `query=`、
  move 用 `to=`、`vault=<名>` 放子命令前；点开头目录（`.config/`）CLI 不可达 →
  隐藏目录内文件直写（例外清单第 6 条）；`append` 只能追加末尾，中间插入用
  read → 重组 → create overwrite；**沙箱内命名管道被拦截时 CLI 报"unable to find
  Obsidian"，需在非沙箱环境运行**。
- Python：中文读写/输出一律显式 UTF-8 或 `PYTHONUTF8=1`（本机 Python 默认 GBK）。
- 删除纪律：只走工具删除接口（进回收站）；本地文件操作用 apply_patch，删除用
  确认路径后的 `Remove-Item -LiteralPath`。
- 不代为 `git init`；保留用户未提交的改动，不擅自回滚。
