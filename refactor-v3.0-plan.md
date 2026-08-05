# knowledge-base / obsidian-kb 拆分重构方案（v0.6.0，本地沉淀，防对话丢失）

> 状态：**需求已确认（2026-08-05 三轮确认），未开始实施，等待用户指示「开始」**。
> 本文件为唯一完整方案源，实施时以本文件为准；同时同步维护 MEMORY.md 要点。创建：2026-08-05。
>
> 需求确认记录（2026-08-05 三轮 AskUserQuestion）：
> - 配置目录定 **`.config/`**（vault 内隐藏，带点前缀=文件树隐藏；`config` 为业界
>   通用名词用法，如 `~/.config/`、`config.json`；`configer` 不通用，已解释排除）。
> - display_name 定稿 **KB Manager**（Skill A）/ **Obsidian Guide**（Skill B）。
> - **发布版本统一 0.6.0**（替换原 v3.0.0；两 skill 同版本，一起发布一起升级）。
> - **发布范围=仅本地**（双 zip + git 提交，不推 GitHub；GitHub 仓库结构仍就位备用）。
> - **Skill B 改名 = `obsidian-kb`**（沿用原 skill 名，用户拍板）：定位为
>   **Obsidian 管理知识库全流程操作指南**（CLI/语法/操作红线/实测经验），
>   **不含知识库自身业务规则**。
> - **Skill A = workflow 规范**（第四轮细化）：knowledge-base 定位为**给用户和 agent
>   都能看的工作流程规范**——描述知识库工作流**应该怎么走**（对流程的要求），**不是
>   对 agent 的行为要求，也不是对工具的要求**；**不提及任何工具名，不写委托链**，
>   工具层连接由用户另行实现；**agent 行为纪律（改删前征求同意、永不 git init、
>   不假设 vault 名等）不放 A**，仅保留「创建前相似检查」这一流程环节。
> - **Skill B 分两大部分**（第四轮细化）：obsidian-kb = **① 对所有工具的统一规范与
>   红线**（跨工具通用纪律）+ **② Obsidian 专有规范**（vault/CLI 等）；**所有对工具
>   的要求都放进 B**。
> - **旧文件全保留**：现有 obsidian-kb 全部文件原样归档 `legacy/obsidian-kb/`
>   （内容一字不改，git 历史保留）；**两个新 skill 从零开始建**（不复用旧文件）。
>
> 原项目路径：`D:\Peojects\MyProject\Skills\obsidian-kb`（工作区目录现已为
> knowledge-base，git 历史完整保留，无需再改目录名）。

---

## 1. 背景与动机

- 现 obsidian-kb 单 skill 混了两类知识：**知识库管理逻辑**（领域规则）与
  **Obsidian 操作知识**（CLI/语法/实测经验），职责边界模糊。
- skill 将发布到 GitHub：现 references 大量为**本机实测表述**
  （1.13.4 / Windows / bash / 回收站路径 / WorkBuddy 受管 Python 路径），
  通用性差，设备经验不得写入 skill。
- 用户要求：**拆两个 skill，能力边界分清**——Skill A 只管知识库业务规则
  （纯规范、不绑定任何工具），Skill B 管 Obsidian 操作全流程（含操作红线）；
  Skill B 沿用原名 `obsidian-kb`；方案沉淀本地以防换对话丢失。

## 2. 已确认的决策（2026-08-05 三轮 AskUserQuestion）

| 决策点 | 用户选择 | 说明 |
|---|---|---|
| Skill A 定位 | **workflow 规范**（给用户与 agent 看） | knowledge-base 是对**整个工作流程规范**的要求（路由、问题生命周期、沉淀、看板、日程、提醒、日志、初始化、配置策略、创建前相似检查）；**不是对 agent/工具的要求**；不提及任何工具名、不写委托链，工具层连接用户另行实现 |
| Skill B 定位 | **对工具的要求**，分两大部分 | ① **对所有工具的统一规范与红线**（跨工具通用纪律）；② **Obsidian 专有规范**（vault/CLI 等）；所有对工具的要求都放进 B |
| 能力边界 | 见 §2.1 | A 管"工作流程怎么走"，B 管"工具怎么用/行为红线"，互不越界 |
| 仓库组织 | **单仓库双 skill** | skills/ 下两目录，一起发布、一起升级 |
| Skill B 命名 | **obsidian-kb**（沿用原名） | 2026-08-05 用户拍板改回原名（原候选 obsidian-guide 作废） |
| 新名字（Skill A） | **knowledge-base**（定稿） | 标准拼写，见 §4 同名注意 |
| GitHub 发布件 | **中英双语 README** | README.md（中文）+ README.en.md（英文）+ LICENSE(MIT) + .gitignore |
| 知识库无关文件位置 | **vault 内隐藏目录 `.config/`**（已确认） | 带点前缀=文件树隐藏；配置/log/手册默认 `<vault>/.config/`；HTML 导出默认 `<vault>/.config/HTML-Export/` |
| display_name | **KB Manager** / **Obsidian Guide** | Skill A=KB Manager，Skill B=Obsidian Guide（2026-08-05 定稿） |
| 旧文件处置 | **原样归档 `legacy/obsidian-kb/`** | 内容一字不改；新两个 skill 从零建，不复用旧文件 |
| 发布版本 | **0.6.0**（统一） | 替换原 v3.0.0；两 skill 同版本一起发布一起升级；发布范围=仅本地（不推 GitHub） |

### 2.1 能力边界（用户强调，实施时必须严守）

- **Skill A（knowledge-base）= workflow 规范**：给**用户和 agent 都能看**的
  工作流程规范——描述知识库工作流**应该怎么走**（对流程的要求），**不是对
  agent 的行为要求，也不是对工具的要求**。
- **Skill B（obsidian-kb）= 工具操作规范**：**所有对工具的要求都放进 B**，分两大部分：
  - **Part 1 对所有工具的统一规范与红线**（跨工具通用纪律）：修改/删除前征求同意、
    永不 git init、不假设路径/名称（一切配置驱动）、删除只走工具接口并进回收站、
    禁止永久删除、直接文件访问例外清单等；
  - **Part 2 Obsidian 专有规范**：vault 与 CLI 相关——CLI 发现/连接/怪癖（盘符陷阱、
    换行、单引号、点开头文件）、笔记读写改删具体操作、Markdown/属性/链接/Bases/
    Canvas 语法、剪藏、日记设置、长内容两步写入、回读校验、实测经验（通用化表述）。

| 层面 | Skill A = knowledge-base | Skill B = obsidian-kb |
|---|---|---|
| 定位 | workflow 规范（给用户+agent 看，对流程的要求） | 对工具的要求（统一红线 + Obsidian 专有） |
| 包括 | 模块路由、问题生命周期（未解决→已解决→沉淀分离）、知识分类沉淀、看板、日程、任务、自动化提醒、操作日志、初始化向导、配置策略、HTML 导出策略、**创建前相似检查**（流程环节）、updated 精确到分钟/打 tag/双向链接等内容规范 | Part 1：修改/删除前征求同意、永不 git init、不假设路径（配置驱动）、删除进回收站、禁永久删除、直写例外清单等通用红线；Part 2：CLI 发现/连接/怪癖、vault 操作、日记设置、语法（Markdown/Bases/Canvas）、剪藏、两步写入、回读校验 |
| 不含 | 对 agent 的行为要求（改删前征求同意等）、对工具的要求、任何工具名/命令 | 知识库业务规则与流程（路由/生命周期/沉淀流程等） |

## 3. 新增需求（2026-08-05 用户补充，纳入 v0.6.0）

1. **知识库无关文件位置可配置**（配置 / log / 用户手册 / HTML 导出产物）：
   - 已定默认：**vault 内隐藏目录 `.config/`**（与 `.obsidian/` 同级惯例，
     vault 一定可写、最通用）；`config` 为通用名词用法（`~/.config/`、`config.json`）；
     初始化时仍可让用户改选其他位置（如上级目录）；
   - **红线修订（原：配置/手册/HTML 导出绝不写入 vault 内）**：
     允许写入 vault 内隐藏目录 `.config/`，但**不得写入用户笔记内容区、
     不得影响笔记浏览**；`.config/` 整体不进 HTML 导出、不参与看板聚合。
2. **HTML 镜像导出改为初始化可选**：不是所有人都需要；初始化向导新增询问
   "是否需要 HTML 镜像导出"，不需要则 `exportRoot` 不配置、html_export 流程整体跳过；
   需要时默认导出到 `<vault>/.config/HTML-Export/`（可改）。
3. **⚠️ HTML 导出在 vault 内带来的连带问题（实施时处理）**：
   - vault 是 git 仓库时 `git add -A -- .` 会包含 `.config/HTML-Export/` →
     vault 的 `.gitignore` 需排除（或提交逻辑排除），避免把导出产物提交进库；
   - Obsidian 不索引 html 文件，不影响笔记检索。

## 4. 命名（已定稿）

- **Skill A：`knowledge-base`**（标准拼写，用户 2026-08-05 拍板）。
  - ⚠️ **同名注意**：本机上层目录 `D:\Peojects\MyProject\knowledge-base` 是另一个
    git 仓库（无关，勿向其提交）；两者仅名称相同、路径不同，互不影响。
- **Skill B：`obsidian-kb`**（沿用原 skill 名，用户 2026-08-05 拍板改回；
  原候选 `obsidian-guide` 作废）。
- display_name（2026-08-05 定稿）：Skill A = "KB Manager"，Skill B = "Obsidian Guide"。
- 配置文件：`obsidian-kb.config.json` → `knowledge-base.config.json`
  （schema v3→v4 major，提供迁移）。
- 改名影响范围（Skill A 内部）：SKILL.md frontmatter `name`；agents/openai.yaml
  `display_name`；脚本内部 SKILL_NAME / 常量；REQUIREMENTS / DESIGN / CHANGELOG 描述。

## 5. 目标结构（GitHub 仓库形态）

```
knowledge-base/（GitHub 仓库根）
├── README.md / README.en.md      ← 中英双语项目说明
├── LICENSE                       ← MIT
├── .gitignore
├── skills/
│   ├── knowledge-base/           ← Skill A：知识库管理（从零建，纯规范）
│   │   ├── SKILL.md
│   │   ├── references/properties.md
│   │   ├── scripts/{kb_config,kb_env,html_export}.py
│   │   ├── assets/user-manual.md
│   │   └── agents/openai.yaml
│   └── obsidian-kb/              ← Skill B：工具操作规范（从零建）
│       ├── SKILL.md              ← Part 1 统一规范红线 + Part 2 Obsidian 专有
│       └── references/{redlines,cli,canvas,markdown,bases}.md（按需）
├── legacy/obsidian-kb/           ← 旧版 obsidian-kb 原样存档（内容一字不改，不进包）
├── scripts/update_skill.py       ← 开发期发布工具（双 skill 打包，不进包）
├── REQUIREMENTS.md / DESIGN.md / CHANGELOG.md / TEST-REPORT.md  ← 开发期文档（不进包）
└── dist/                         ← knowledge-base.zip + obsidian-kb.zip
```

## 6. 通用化处理清单（设备经验不写入 skill）

| 内容 | 处理 |
|---|---|
| trash-verification.md（含回收站路径、测试库名） | legacy 原样保留；「CLI delete 默认进系统回收站」结论在 Skill B 以通用化表述重写 |
| cli-commands.md 实测表述（1.13.4/Windows/bash `'"'"'`） | Skill B 通用化重写（跨平台一致行为保留，bash/Git Bash 特定删除） |
| canvas.md（CLI 写不出合法 Canvas） | Skill B 通用化重写（CLI 行为跨平台一致） |
| SKILL.md Python 解释器发现（WorkBuddy 受管路径） | Skill A 脚本改为通用探测链（python → py -3 → 提示安装 3.10+） |
| 例外清单（5 条） | 直接文件访问例外属工具层纪律 → 归 Skill B Part 1（对所有工具的统一红线） |
| 测试库路径 / Python 版本路径 | 只存开发文档与记忆，不进 skill 包 |
| kb_env.py Obsidian.com 候选路径 | Windows 平台常见安装位置（通用逻辑），保留，表述确认"平台常见位置" |

## 7. 实施步骤（需求确认后按序执行）

1. **归档旧版**：新建 `legacy/obsidian-kb/`，把现有 SKILL.md、scripts/、references/、
   agents/、assets/ 原样 `git mv` 进去（**内容一字不改**，git 历史保留）；
2. **Skill A 从零建**（`skills/knowledge-base/`）：全新 SKILL.md（**workflow 规范，
   给用户+agent 看；只写流程要求，不放 agent 行为纪律、不写任何工具名/命令**）；
   scripts 重写（kb_config/kb_env/html_export 支持 `knowledge-base.config.json`、
   `.config/` 默认位置、HTML 导出可选）；references（properties 等领域设计）；
   agents/openai.yaml；assets/user-manual.md；
3. **Skill B 从零建**（`skills/obsidian-kb/`）：全新 SKILL.md，**分两大部分——
   Part 1 对所有工具的统一规范与红线（改删前征求同意、永不 git init、删除进回收站、
   禁 permanent、直写例外清单等）；Part 2 Obsidian 专有规范（vault/CLI 操作、语法、
   剪藏、两步写入、回读校验，通用化表述）** + references（统一红线/cli/canvas/
   markdown/bases 按需）；
4. 配置迁移：kb_config.py 实现 `obsidian-kb.config.json`（v3）→
   `knowledge-base.config.json`（v4）迁移，缺省补齐不覆盖自定义值；
5. 发布工具：update_skill.py（仓库根 scripts/）按 skill 子目录双打包
   （各自 zip、各自 check）；
6. 仓库根件：README.md（中文）+ README.en.md（英文）+ LICENSE(MIT) + .gitignore；
7. 开发文档：REQUIREMENTS.md 更新拆分模型与能力边界；DESIGN.md/CHANGELOG.md v0.6.0 条目；
8. 测试：quick_validate 两个 skill + 脚本级测试 + 测试库 forward-test（自测约定保留）；
9. 发布：**0.6.0**（用户拍板，替换原 v3.0.0），产物两个 zip
   （knowledge-base + obsidian-kb）；git 提交；**仅本地发布，不推 GitHub**。

## 8. 影响与注意

- git 历史：`git mv` 归档旧文件，历史可追溯；工作区目录已为 knowledge-base
  （无需再改目录名）；发布 GitHub 时用新仓库名；
- 本机自用：工具层连接由用户另行实现（本机既有 obsidian-suite 可继续使用）；
  测试库自测约定存开发文档与记忆，不进包；
- 配置迁移：旧 `obsidian-kb.config.json`（schema v3）需迁移到新文件名/新 schema，
  迁移在 kb_config.py 实现，缺省补齐不覆盖自定义值；
- 红线修订：§3.1 允许 vault 内隐藏目录 `.config/`（配置/log/手册/HTML 导出），
  但不得写入用户笔记内容区；HTML 导出在 vault 内需 git 排除（§3.3）。
