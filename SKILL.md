---
name: obsidian-kb
description: 基于 Obsidian CLI 的通用知识库管理。当用户要求记录笔记或问题、搜索/读取/整理 Obsidian vault、写原生日记、管理任务、设置属性标签、创建 Bases 视图或 Canvas 画布、网页剪藏、HTML 镜像导出、多 vault 切换、首次接入知识库时使用。写入/修改/删除只走 Obsidian CLI，Vault 是唯一数据源，删除进系统回收站。内置五份参考技能（references/skills/）：Obsidian Markdown 语法、Obsidian CLI 用法、Obsidian Bases、JSON Canvas、defuddle 网页剪藏。
agent_created: true
---

# obsidian-kb 知识库管理

以 Obsidian 本体 + Obsidian CLI 管理知识库。Vault 是唯一数据源；本 skill 不构建任何
索引、同步、数据库或守护进程。

## 安全红线（每次操作前默念）

1. 写入 / 修改 / 移动 / 重命名 / 删除：**只走 Obsidian CLI**。直接读写文件仅限
   `references/cli-commands.md` 末尾的例外清单，且必须在回复中说明原因。
2. 修改 / 移动 / 重命名已有内容前：**先展示变更方案并征得用户同意**。
3. 删除：只用 CLI `delete`（默认进系统回收站，可恢复）；**严禁 `permanent` 参数**；
   删除前征得用户同意并告知"进回收站可恢复"。
4. 创建新内容无需同意，但写入前**必须用 CLI `search` 做相似检查**；高相似时展示给
   用户由其决策（合并 / 跳过 / 仍写入），不强制阻断、不强制标题规范。
5. 永不执行 `git init`；HTML 导出**绝不写入 vault 内部**；配置与用户手册只写入
   大知识库文件夹（vault 上级目录），绝不写入 vault 内部。
6. 不假设 vault 名称或任何固定目录名：一切以用户确认与配置文件为准。

## 运行环境准备

### Python 解释器发现（脚本运行前置）

按顺序探测，用第一个可用的：
1. `python` 或 `python3`；
2. Windows：`py -3`；
3. WorkBuddy 受管运行时：`~/.workbuddy/binaries/python/versions/<版本>/python.exe`
   （Windows 为 `%USERPROFILE%\.workbuddy\...`，取最高版本）；
4. 均不可用 → 提示用户安装 Python 3.10+，停止脚本类操作（CLI 操作不受影响）。

### CLI 发现与连接

- CLI 路径：读配置 `cliPath` → `kb_env.py cli-path` 自动发现（PATH / 平台常见位置）。
- 首次使用或关键操作前执行 `kb_env.py check`：CLI 不可用或 Obsidian 未运行时，
  脚本会尝试拉起并轮询等待；失败则明确提示用户手动打开 Obsidian。
- 所有 CLI 命令用绝对路径调用（如 `"<cliPath>" create ...`），不依赖 PATH。
- 多 vault：命令首参加 `vault="<名称>"`（名称为 Obsidian 注册名，与配置一致）；
  单 vault 可省略。

### 配置发现

按顺序：用户在会话中显式指定的路径 → `kb_config.py find`（从当前目录向上查找
`obsidian-kb.config.json`）→ 找不到则进入首次初始化。脚本统一加 `--json` 消费输出。

## 首次初始化向导（仅配置不存在时执行）

按以下顺序与用户确认，**逐项来，不一次性抛所有问题**：

1. 告知：vault 在 agent 项目建立前已存在、名称不统一，skill 只读取实际路径与名称，
   不假设固定名称（如 MyVault）。
2. 确认 vault 实际路径与名称：可先用 CLI `vaults` 列出已注册 vault 供用户点选；
   若目标文件夹尚未注册，请用户在 Obsidian 中「打开文件夹作为仓库」。
3. 发现 CLI 路径（`kb_env.py cli-path`），确认后随初始化写入配置。
4. 确认配置文件位置：**默认大知识库文件夹（vault 上级目录）**，可改（但不得在 vault 内）。
5. 确认 HTML 导出目录：默认 `<大知识库文件夹>/HTML-Export/`，可改（不得在 vault 内）。
6. 询问是否还有其他 vault（逐个注册）。
7. 展示默认目录结构（见 `references/properties.md` 的目录模板，含 问题 / 项目 /
   日志 / 知识与经验 / TODO.md 模块约定）供确认或修改，结果写入偏好。
8. 执行初始化：
   ```bash
   python scripts/kb_config.py --json init \
     --vault-name "<名称>" --vault-path "<路径>" \
     [--config "<配置位置>"] [--export-root "<导出根>"] [--cli-path "<CLI路径>"]
   ```
   其余 vault 用 `add-vault --name <名> --path <路径>` 注册。
9. 复制用户手册：把 `assets/user-manual.md` 复制为 `<大知识库文件夹>/用户手册.md`；
   **已存在则不覆盖**，只提示用户。（此为写文件例外，手册在 vault 外。）
10. 检查 vault 是否已是 Git 仓库（存在 `.git`）：是 → 告知将自动提交；否 → 提示用户
    可自行建仓，**绝不代为 init**。
11. 日记按月切分：用 CLI 依次执行（1.13.4 实测有效）：
    ```bash
    # ① 持久化到 .obsidian/app.json（重启后仍有效）
    "<cliPath>" eval code="app.vault.setConfig('daily-notes',{folder:'<dailyFolder>',format:'<dailyFormat>'})"
    # ② 同步运行中实例的内存设置（立即生效）
    "<cliPath>" eval code="const p=app.internalPlugins.plugins['daily-notes'].instance;p.options.folder='<dailyFolder>';p.options.format='<dailyFormat>'"
    # ③ 若 daily:path 报 Folder not found，先建目录（eval 走 CLI，合规）
    "<cliPath>" eval code="app.vault.createFolder('<dailyFolder>')"
    ```
    最后用 `daily:path` 验证路径形态（应形如 `日志/2026-08/2026-08-03.md`）。
    eval 全部不可用时给用户一次性人工指引：设置 → 日记 → 日期格式
    `YYYY-MM/YYYY-MM-DD`、新笔记位置 `<dailyFolder>`。
12. 首次全量导出：`python scripts/html_export.py --json export --full`。
13. 向用户反馈：配置路径、vault 列表、导出目录、手册位置、日记格式验证结果。

## 日常工作流

### 创建笔记：先分类，再路由（核心规则）

收到任何记录请求（再笼统也要分类），**先判定模块类型，再按规则路由**；
禁止一律写入收件箱。目录名全部来自配置偏好（`kb_config.py list` 查看）。

| 类型 | 判定线索 | 目标位置（配置键 → 默认） | 联动 |
|---|---|---|---|
| 问题 | "问题 / 没搞懂 / 不懂 / 为什么 / 待复盘 / bug" | `questionDir` → `问题/` | 日志 + TODO |
| 项目 | "项目 / 工程 / 学习项目 / 课题" | `projectsDir` → `项目/<项目名>/` | 日志 + TODO |
| 剪藏 | 给出 URL | `clipDir` → `40-Resources/Clips/` | 日志 |
| 日记 | "日记 / 今天" | 原生日记 `daily:*`（`dailyFolder` → `日志/`） | — |
| 普通 | 其余 | `inboxDir` → `00-Inbox/` | — |

通用步骤（全部类型）：
1. CLI 相似检查：`search query="<关键词>" limit=5`；高相似 → 展示给用户决策。
2. 组装结构化内容：frontmatter（`type` / `status` / `source` / `created` 等，见
   `references/properties.md`）+ 正文；**代码块原样保留**。
3. CLI 创建：多行 content 优先 shell 单引号内**真实换行**；frontmatter 列表用
   行内数组 `tags: [a, b]`（`\n` 转义会触发盘符误判，见
   `references/cli-commands.md`）；单引号用 `'"'"'`；写后回读校验。
4. 联动（见下）；5. 写后三件套；6. 反馈路径。

**问题类**：
- 含图片/附件等资源 → 建文件夹 `问题/<标题>/`，md 与资源同目录存放
  （资源复制属附件例外，回复中说明）；纯文字 → `问题/<标题>.md`。
- frontmatter 至少含 `type: question`、`status: pending`、`created`（= 问题出现日期）。
- 用户让记录问题时不回答技术问题；反馈时提示"解决后可随时发起沉淀"。

**项目类**：`项目/<项目名>/<标题>.md`；项目主页不存在时可一并创建。

**联动动作**（问题 / 项目 / 剪藏记录后执行）：
1. **写日志**：`daily:append content="- [<类型>] 记录：<标题> → [[<标题>]]"`；
   当日日记或日志目录不存在时，先
   `eval code="app.vault.createFolder('<dailyFolder>')"` 再重试。
2. **追加 TODO**（仅问题 / 项目）：`todoFile`（默认 `TODO.md`）不存在则先创建：
   `create path="TODO.md" content='# 待办\n\n各模块记录自动追踪的待办。'`；
   然后 `append path="TODO.md" content="- [ ] [<类型>] <标题> → [[<标题>]]（<YYYY-MM-DD> 记录）"`。

### 问题沉淀（解决后移入知识与经验）

触发：用户表示某问题已解决 / 已复盘 / 已学会。

1. **展示方案征得同意**：源（`问题/...`）→ 目标（`knowledgeDir` → `知识与经验/`），
   说明链接由 CLI 自动更新；含资源的问题整个文件夹移动。
2. **更新属性**：`property:set name=status value=done`、
   `property:set name=resolved value=<YYYY-MM-DD>`（created 即问题出现日期，勿改）。
3. **追加经验总结**：`append` 写入 `## 经验总结` 小节（内容向用户索要或按其复盘整理）。
4. **移动**：目标目录不存在先 `eval code="app.vault.createFolder('知识与经验')"`，再
   `move path="<源>" to="知识与经验"`。
5. **勾选 TODO**：`read path="TODO.md"` 定位对应条目行号 →
   `task path="TODO.md" line=<n> done`。
6. **写日志**：`daily:append content="- [经验] 解决：<标题> → [[<标题>]]"`。
7. 执行"写后三件套"。

### 写后三件套（每次新增 / 修改 / 删除后固定执行）

1. **HTML 镜像增量更新**：单篇变更用
   `python scripts/html_export.py --json export-one --file "<相对路径>"`；
   涉及删除 / 移动 / 重命名用 `python scripts/html_export.py --json export`
   （自动同步移除多余镜像）。
2. **Git 提交**：vault 是 Git 仓库时（`test -d <vault>/.git`）执行
   `git -C <vault> add -A -- . && git -C <vault> commit -m "docs: <简述>"`；
   不是仓库则跳过并提示一次（可在配置 `preferences.gitCommit=false` 关闭提醒）。
3. **反馈**：笔记路径 / 变更摘要。

### 读取与搜索

- 读取：`"<cliPath>" read file="<名称>"`（或 `path=` 精确路径）。
- 搜索：`"<cliPath>" search query="<词>" limit=<n>`；要上下文用 `search:context`。
- 不封装搜索工具，直接调 CLI。列表类：`files` / `folders` / `tags` / `backlinks`。

### 修改与整理（移动 / 重命名 / 归档）

1. 先展示方案（源 → 目标、影响的链接）并征得用户同意。
2. 简单变更优先 CLI 原生命令：`property:set name="<k>" value="<v>" file="<f>"`、
   `append` / `prepend`；移动 / 重命名用
   `"<cliPath>" move file="<f>" to="<目标目录或新路径>"`（CLI 会自动更新链接）。
3. 执行"写后三件套"。

### 删除

1. 征得用户同意，并说明"删除后进入系统回收站，可恢复"。
2. `"<cliPath>" delete file="<名称>"`（或 `path=`）。**永不加 `permanent`**。
3. `python scripts/html_export.py --json export`（同步移除镜像）+ Git 提交。

### 日记（原生日记，按月切分）

- 写今天的日记：`"<cliPath>" daily:append content="<内容>"`；读：`daily:read`；
  查路径：`daily:path`（验证按月目录形态 `YYYY-MM/YYYY-MM-DD`）。
- 日记目录与格式来自配置 `preferences.dailyFolder`（默认 `日志/`）/
  `preferences.dailyFormat`。
- 分类路由的记录动作会自动写一行日志（见"创建笔记"联动动作），无需重复写。
- 复盘场景：按"问题沉淀"工作流处理，不要只改属性。

### 任务

- 统一 `- [ ]` 语法；汇总用 `"<cliPath>" tasks`（`todo` / `daily` 等过滤见
  `references/cli-commands.md`）；看板用 Bases 视图（`references/bases.md`）。

### 属性与标签

- frontmatter 属性：`property:set` / `property:read` / `property:remove`；
  默认核心属性集与层级标签约定见 `references/properties.md`（约定非强制）。

### Bases 视图

- 创建 `.base`：用 CLI 写入，content 用 **shell 单引号内的真实换行**（不要用 `\n`
  转义——`key:\n` 会触发 CLI 的盘符误判，见 `references/cli-commands.md` 怪癖节）：
  ```bash
  "<cliPath>" create path="<目录>/<名>.base" silent content='filters:
    and:
      - file.hasTag("task")
  views:
    - type: table
      name: "进行中"'
  ```
- 校验：`base:query path="<同路径>"` 能返回结果（空数组也算 YAML 合法）；
  语法要点与任务看板 / 阅读清单 / 日记索引示例见 `references/bases.md`。

### Canvas 画布

- `.canvas` 是 JSON，其字符串内的 `\n` 必须保持两个字面字符；而 CLI 会把各种
  形式的 `\n` 都转成真实换行 → **CLI 写不出合法 Canvas，一律直接写文件**
  （例外清单第 1/2 条：CLI 对该内容类型不可用 + 需格式校验，回复中说明原因）。
- 节点/边 ID 用 16 位十六进制且唯一，边引用必须有效；写后用 Python `json.load`
  校验（合法、ID 唯一、边不悬空）；规范要点见 `references/canvas.md`。

### 网页剪藏

1. `defuddle parse <url> --md` 提取正文（defuddle 未安装则提示用户
   `npm install -g defuddle`，或用 WebFetch 兜底并说明降级）。
2. 组装笔记：`type: clip`、`source_url`、`source_domain`、`clipped_at`（ISO 时间）+
   正文；标题取页面标题。
3. 相似检查 → CLI 创建到 `preferences.clipDir` → 写后三件套 → 反馈链接。

### 附件

- CLI 无二进制导入能力：直接复制到 vault 的 `preferences.attachmentDir`
  （例外清单第 3 条，**回复中必须说明原因**），随后在笔记中用 `![[<文件名>]]` 引用。

### 模板

- 列出：`"<cliPath>" templates`；用模板创建：
  `"<cliPath>" create name="<名>" template="<模板名>" silent`；
  模板目录见配置 `preferences.templateDir`，skill 不内置个人模板。

### Git 提交（仅提交）

- 仅当 vault 已是 Git 仓库时提交；**永不 `git init`**；提交信息用简短中文
  `docs: <简述>`；非仓库跳过并提示。

### HTML 镜像导出

- 见"写后三件套"。全量重建：`html_export.py export --full`。
- 导出位置 / 名称来自配置 `exportRoot`；镜像结构 `<exportRoot>/<vault名>/<相对路径>.html`，
  索引页 `index.html`，不依赖 Obsidian 打开。

### 多 vault

- 列出 / 切换默认：`kb_config.py list` / `set-default --name <名>`；
  指定 vault 操作：CLI 命令首参 `vault="<名>"`，脚本加 `--vault <名>`。

## 脚本一览（均 `--json` 输出，`-h` 查看完整参数）

| 脚本 | 用途 |
|---|---|
| `scripts/kb_config.py` | 配置与多 vault：init / find / add-vault / remove-vault / list / set-default / path / get / set / validate / migrate |
| `scripts/kb_env.py` | 环境自检：check（CLI/Obsidian/配置/vault，自动拉起）/ launch / cli-path |
| `scripts/html_export.py` | HTML 镜像：export（增量+清理，--full 全量）/ export-one（单篇） |
| `scripts/update_skill.py` | 发布辅助（仅用户明确要求时用）：check / package / commit / release |

## references 索引（按需加载）

| 文件 | 何时读 |
|---|---|
| `references/cli-commands.md` | 需要命令细节、参数、例外清单、CLI 行为备注时 |
| `references/properties.md` | 需要属性集、标签约定、目录模板细节时 |
| `references/bases.md` | 创建 / 编辑 .base 视图时 |
| `references/canvas.md` | 创建 / 编辑 .canvas 画布时 |
| `references/trash-verification.md` | 需要引用删除安全性实测结论时 |

## 内置参考技能（references/skills/，按需加载）

五份独立参考技能随包分发，编写对应内容时优先查阅其 `SKILL.md`
（大型细节文档位于各自的 `references/` 子目录）：

| 目录 | 何时读 |
|---|---|
| `references/skills/obsidian-markdown/` | 撰写 Obsidian Markdown：wikilink、嵌入、callout、属性、标签（细节见其子 references：CALLOUTS / EMBEDS / PROPERTIES） |
| `references/skills/obsidian-cli/` | 需要 CLI 调用约定、插件开发命令时 |
| `references/skills/obsidian-bases/` | 编写 .base 的复杂过滤 / 公式 / 视图（函数全集见其子 references：FUNCTIONS_REFERENCE） |
| `references/skills/json-canvas/` | 编写 .canvas：节点/边属性、布局、完整示例（见其子 references：EXAMPLES） |
| `references/skills/defuddle/` | 网页剪藏提取正文的参数细节 |

## 项目文档

- `CHANGELOG.md`：版本历史（v1.0.0 起，每次发布同步更新）。
- `DESIGN.md`：架构决策、模块职责、数据流、兼容性策略。
- 发布流程见 DESIGN.md「发布约定」；**不主动打包 / 提交 / 发布**。
