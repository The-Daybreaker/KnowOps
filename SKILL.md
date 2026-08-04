---
name: obsidian-kb
description: 基于 Obsidian CLI 的通用知识库管理。当用户要求记录笔记或问题（按未解决/已解决管理）、搜索/读取/整理 Obsidian vault、知识沉淀（按类型归档）、写原生日记、管理任务、设置属性标签与双向链接、创建 Bases 视图或 Canvas 画布、网页剪藏、HTML 镜像导出、多 vault 切换、首次接入知识库时使用。写入/修改/删除只走 Obsidian CLI，Vault 是唯一数据源，删除进系统回收站。
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
7. 展示默认目录结构（见 `references/properties.md` 的目录模板，含 问题/未解决、
   问题/已解决、项目、日志、知识（按类型）、TODO.md 模块约定）供确认或修改，
   结果写入偏好；**不询问**剪藏/模板/附件/Bases/Canvas 的存放位置
   （v2.0 起为文件类型分类，使用时以用户指令为准）。
8. 执行初始化：
   ```bash
   python scripts/kb_config.py --json init \
     --vault-name "<名称>" --vault-path "<路径>" \
     [--config "<配置位置>"] [--export-root "<导出根>"] [--cli-path "<CLI路径>"]
   ```
   其余 vault 用 `add-vault --name <名> --path <路径>` 注册。
9. **复制用户手册（必做，流程规范）**：把 `assets/user-manual.md` 复制到
   **大知识库文件夹根目录**（vault 的上级目录，与配置文件同层），默认文件名
   `用户手册.md`；目标文件**已存在则绝不覆盖**，只提示用户。（此为写文件例外，
   手册在 vault 外。）
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
无收件箱兜底。目录名全部来自配置偏好（`kb_config.py list` 查看）。

| 类型 | 判定线索 | 目标位置（配置键 → 默认） | 联动 |
|---|---|---|---|
| 问题 | "问题 / 没搞懂 / 不懂 / 为什么 / 待复盘 / bug" | `<questionDir>/未解决/` → `问题/未解决/` | 日志 + TODO + log |
| 项目 | "项目 / 工程 / 学习项目 / 课题" | `<projectsDir>` → `项目/<项目名>/` | 日志 + TODO + log |
| 剪藏 | 给出 URL | **用户指令指定位置**（不预设目录） | 日志 + log |
| 日记 | "日记 / 今天" | 原生日记 `daily:*`（`dailyFolder` → `日志/`） | log |
| 知识 | "沉淀 / 总结 / 整理成知识" | `<knowledgeDir>/<类型>/` → `知识/<类型>/`（类型交用户审核） | 链接 + log |
| 无法判定 | 不属于上述任何一类 | **询问用户归属**，由用户决定写入哪一模块（无收件箱） | 按用户决定 |

> v2.0 起**无收件箱**：判断不出类型时，向用户说明内容要点并列出可选模块请其
> 决策，确认后再写入；不再有任何静默兜底目录。

通用步骤（全部类型）：
1. CLI 相似检查：`search query="<关键词>" limit=5`；高相似 → 展示给用户决策。
2. 组装结构化内容：frontmatter（`type` / `status` / `source` / `created` / `tags` 等，
   见 `references/properties.md`）+ 正文；**代码块原样保留**；
   **积极打层级标签**（领域 / 类型 / 来源，如 `#领域/fpga`、`#知识/经验`）。
3. CLI 创建：多行 content 优先 shell 单引号内**真实换行**；frontmatter 列表用
   行内数组 `tags: [a, b]`（`\n` 转义会触发盘符误判，见
   `references/cli-commands.md`）；单引号用 `'"'"'`；写后回读校验。
   **超长内容（>4000 字符）改用两步写入**：先用 CLI 创建占位文件
   `create path="<路径>.md" silent content="占位"`（**创建动作必须走 CLI**，
   保证 Obsidian 索引注册），再用文件系统直接写入完整内容（CLI 参数长度受限，
   属例外清单第 5 条，回复中说明原因），最后仍执行回读校验与操作后流程。
4. 联动（见下）；5. 操作后流程；6. 反馈路径。

**问题类**：
- 文件名统一 `YYYY-MM-DD 文件名.md`（**日期为问题出现日期**；"文件名"用简短
  描述如 `2026-08-04 FPGA同步异步复位问题.md`，**不要用长句描述做文件名**）。
- 纯文字 → `<questionDir>/未解决/<文件名>.md`；含图片/附件等资源 → 建文件夹
  `<questionDir>/未解决/<文件名>/`，md 与资源同目录存放（资源复制属附件例外，回复中说明）。
- frontmatter 至少含 `type: question`、`status: pending`、`created`（= 问题出现日期）、
  领域标签。
- 用户让记录问题时不回答技术问题；反馈时提示"解决后可标记完成，之后可随时发起沉淀"。

**项目类**：`项目/<项目名>/<标题>.md`；项目主页不存在时可一并创建。

**联动动作**（问题 / 项目 / 剪藏 / 知识记录后执行）：
1. **写日志**：`daily:append content="- [<类型>] 记录：<标题> → [[<标题>]]"`；
   当日日记或日志目录不存在时，先
   `eval code="app.vault.createFolder('<dailyFolder>')"` 再重试。
2. **追加 TODO**（仅问题 / 项目）：`todoFile`（默认 `TODO.md`）不存在则先创建：
   `create path="TODO.md" content='# 待办\n\n各模块记录自动追踪的待办。'`；
   然后 `append path="TODO.md" content="- [ ] [<类型>] <标题> → [[<标题>]]（<YYYY-MM-DD> 记录）"`。
3. **建立双向链接**（知识 / 剪藏 / 沉淀时）：链接原问题、相关笔记（见"知识沉淀"）。

### 问题解决（移入已解决文件夹，标记完成）

触发：用户表示某问题已解决 / 已复盘 / 已学会（与"沉淀"分离，**解决不自动沉淀**）。

1. **展示方案征得同意**：源（`<questionDir>/未解决/...`）→ 目标（`<questionDir>/已解决/`），
   说明链接由 CLI 自动更新；含资源的问题整个文件夹移动；**文件名保持
   `YYYY-MM-DD 文件名.md` 不变**。
2. **更新属性**：`property:set name=status value=done`、
   `property:set name=resolved value=<YYYY-MM-DD>`（解决日期）、
   `property:set name=updated value=<YYYY-MM-DDTHH:MM>`（精确到分钟）；
   `created`（记录日期）保持问题出现日期勿改。
3. **移动**：目标目录不存在先 `eval code="app.vault.createFolder('<questionDir>/已解决')"`，
   再 `move path="<源>" to="<questionDir>/已解决"`。
4. **勾选 TODO**：按下方「TODO 勾选与折叠归档」工作流执行。
5. **写日志**：`daily:append content="- [解决] <标题> → [[<标题>]]"`。
6. 执行"操作后流程"。

### TODO 勾选与折叠归档（v2.1.0）

勾选完成（`- [ ]` → `- [x]`）后，把已完成条目移到 TODO.md 底部「已完成」折叠块，
最新完成排最上、完成越久越靠下。全程 CLI：

1. **读全文记录进行中行**：`read path="<todoFile>"`，记下所有 `- [ ]` 行内容
   （用于勾选后对比定位）。
2. **勾选**：`task path="<todoFile>" line=<n> done`。
3. **重读全文**：`read path="<todoFile>"`，找出"上次是 `- [ ]`、现在是 `- [x]`"
   的行 = 刚完成的条目。
4. **重组全文**：
   - 进行中条目（`- [ ]`）保持原序在上；
   - 底部接「已完成」折叠块：
     ```markdown
     > [!success]- 已完成
     > - [x] <条目>（保持行内容）
     > - [x] <条目>
     ```
     刚完成的条目放**块内最上方**，其余已完成条目保持相对顺序；
     折叠块不存在则新建，已存在则合并（把所有 `- [x]` 收进块内）。
5. **写回**：`create path="<todoFile>" overwrite content="<重组后全文>"`
   （CLI create 支持 `overwrite`，覆盖写合规，不绕红线）。

> 说明：折叠用 Obsidian callout `[!success]-`（`-` 后缀即默认折叠）；行号以
> 勾选前 `read` 输出的行为准。历史遗留的块外 `- [x]` 行在下次重组时一并收进块内。

### 知识沉淀（创建知识笔记，链接回原问题）

触发：用户另行发起"沉淀这个问题 / 总结成知识"（已解决问题才沉淀）。

1. **判定知识类型**：根据问题内容与经验总结，从初始 7 类（经验 / 原理 / 工具 /
   设计 / 规范 / 案例 / 模板）中选择；**内容不适合现有类型时，提出新类型并交
   用户确认**（确认后即为新子目录，知识类型可动态扩展）。
2. **展示方案征得同意**：目标 `<knowledgeDir>/<类型>/<YYYY-MM-DD 标题>.md`
   （日期为沉淀日期，标题用简短描述）；向用户展示拟创建位置与类型，确认后执行。
3. **创建知识笔记**：CLI 创建，frontmatter 含 `type: knowledge`、
   `knowledge_type: <类型>`、`created`、`resolved`（沉淀日期）、`source`、领域标签；
   正文含**经验总结**小节，并**双向链接回原问题**：`[[<原问题文件名>]]`（原问题
   保留在 `<questionDir>/已解决/`，不删除、不移动）。
4. **回写原问题**：在原问题笔记正文追加"已沉淀"链接（`[[<知识笔记>]]`），
   形成双向链接。
5. **写日志**：`daily:append content="- [知识] 沉淀：<标题> → [[<标题>]]"`。
6. 执行"操作后流程"。

> 知识类型子目录**用到才建**（首次沉淀到某类型时创建），不预建空目录。

### 操作后流程（每次对知识库的操作后固定执行）

1. **更新 `updated` 属性**（仅修改已有笔记时）：`property:set name=updated
   value=<YYYY-MM-DDTHH:MM>`（精确到分钟，v2.0 硬性要求）。
2. **HTML 镜像增量更新**（仅写操作）：单篇变更用
   `python scripts/html_export.py --json export-one --file "<相对路径>"`；
   涉及删除 / 移动 / 重命名用 `python scripts/html_export.py --json export`
   （自动同步移除多余镜像）。
3. **记录操作日志**（**所有操作**，含读取/搜索）：向大知识库文件夹（vault 外，
   与配置同层）`<logDir>/<YYYY-MM>/<YYYY-MM-DD>.md`（默认 `log/`）追加一行
   `- <HH:MM> [<操作类型>] <目标路径或简述>`；日志目录不存在先创建；
   日志在 vault 外，直接写文件（与配置/手册同理，非 CLI 操作）。
4. **Git 提交**（写操作）：vault 是 Git 仓库时（`test -d <vault>/.git`）执行
   `git -C <vault> add -A -- . && git -C <vault> commit -m "docs: <简述>"`；
   不是仓库则跳过并提示一次（可在配置 `preferences.gitCommit=false` 关闭提醒）。
5. **反馈**：笔记路径 / 变更摘要。

### 读取与搜索

- 读取：`"<cliPath>" read file="<名称>"`（或 `path=` 精确路径）。
- 搜索：`"<cliPath>" search query="<词>" limit=<n>`；要上下文用 `search:context`。
- 不封装搜索工具，直接调 CLI。列表类：`files` / `folders` / `tags` / `backlinks`。
- **读取 / 搜索也算操作**：结束后在操作日志记录一行（见"操作后流程"第 3 条）。

### 修改与整理（移动 / 重命名）

1. 先展示方案（源 → 目标、影响的链接）并征得用户同意。
2. 简单变更优先 CLI 原生命令：`property:set name="<k>" value="<v>" file="<f>"`、
   `append` / `prepend`；移动 / 重命名用
   `"<cliPath>" move file="<f>" to="<目标目录或新路径>"`（CLI 会自动更新链接）。
3. 修改内容后必须同步 `updated` 属性（精确到分钟）；执行"操作后流程"。

### 删除

1. 征得用户同意，并说明"删除后进入系统回收站，可恢复"。
2. `"<cliPath>" delete file="<名称>"`（或 `path=`）。**永不加 `permanent`**。
3. `python scripts/html_export.py --json export`（同步移除镜像）+ 记录日志 + Git 提交。

### 日记（原生日记，按月切分）

- 写今天的日记：`"<cliPath>" daily:append content="<内容>"`；读：`daily:read`；
  查路径：`daily:path`（验证按月目录形态 `YYYY-MM/YYYY-MM-DD`）。
- 日记目录与格式来自配置 `preferences.dailyFolder`（默认 `日志/`）/
  `preferences.dailyFormat`。
- 分类路由的记录动作会自动写一行日志（见"创建笔记"联动动作），无需重复写。
- 复盘场景：按"问题解决"→"知识沉淀"工作流处理，不要只改属性。

### 任务

- 统一 `- [ ]` 语法；汇总用 `"<cliPath>" tasks`（`todo` / `daily` 等过滤见
  `references/cli-commands.md`）；看板用 Bases 视图（`references/bases.md`）。
- **勾选完成**（`task ... done`）后，按「TODO 勾选与折叠归档」工作流把已完成条目
  移入 TODO.md 底部「已完成」折叠块（默认折叠，最新完成在最上）。

### 属性、标签与双向链接

- frontmatter 属性：`property:set` / `property:read` / `property:remove`；
  默认核心属性集见 `references/properties.md`。
- **积极打标签**（v2.0 硬性要求）：创建笔记时根据内容主动打层级标签
  （`#领域/fpga`、`#知识/经验`、`#课程/小梅哥` 等），为 Bases 聚合与检索建立索引。
- **建立双向链接**（v2.0 硬性要求）：知识沉淀链接原问题、剪藏链接相关笔记、
  相关知识互相链接；发现相关内容时主动补链。

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
  语法要点与任务看板 / 阅读清单 / 日记索引示例见 `references/bases.md`；
  `.base` 存放位置由用户指令决定（不预设目录）。

### Canvas 画布

- `.canvas` 是 JSON，其字符串内的 `\n` 必须保持两个字面字符；而 CLI 会把各种
  形式的 `\n` 都转成真实换行 → **CLI 写不出合法 Canvas，一律直接写文件**
  （例外清单第 1/2 条：CLI 对该内容类型不可用 + 需格式校验，回复中说明原因）。
- 节点/边 ID 用 16 位十六进制且唯一，边引用必须有效；写后用 Python `json.load`
  校验（合法、ID 唯一、边不悬空）；规范要点见 `references/canvas.md`；
  `.canvas` 存放位置由用户指令决定（不预设目录）。

### 网页剪藏

1. `defuddle parse <url> --md` 提取正文（defuddle 未安装则提示用户
   `npm install -g defuddle`，或用 WebFetch 兜底并说明降级）。
2. 组装笔记：`type: clip`、`source_url`、`source_domain`、`clipped_at`（ISO 时间）+
   正文；标题取页面标题；打来源/领域标签；如与现有笔记相关，建立双向链接。
3. **确认存放位置**：剪藏位置不预设，**询问用户存到哪个文件夹**（或按用户指令）；
   确认后相似检查 → CLI 创建 → 操作后流程 → 反馈链接。

### 附件

- CLI 无二进制导入能力：直接复制到**用户指定的 vault 内位置**（不预设目录，
  例外清单第 3 条，**回复中必须说明原因**），随后在笔记中用 `![[<文件名>]]` 引用。

### 模板

- 列出：`"<cliPath>" templates`；用模板创建：
  `"<cliPath>" create name="<名>" template="<模板名>" silent`；
  模板目录位置由用户指令决定，skill 不内置个人模板。

### Git 提交（仅提交）

- 仅当 vault 已是 Git 仓库时提交；**永不 `git init`**；提交信息用简短中文
  `docs: <简述>`；非仓库跳过并提示。

### HTML 镜像导出

- 见"操作后流程"。全量重建：`html_export.py export --full`。
- 导出位置 / 名称来自配置 `exportRoot`；镜像结构 `<exportRoot>/<vault名>/<相对路径>.html`，
  索引页 `index.html`，不依赖 Obsidian 打开。
- 操作日志在 vault 外，不纳入 HTML 镜像导出。

### 多 vault

- 列出 / 切换默认：`kb_config.py list` / `set-default --name <名>`；
  指定 vault 操作：CLI 命令首参 `vault="<名>"`，脚本加 `--vault <名>`。

## 脚本一览（均 `--json` 输出，`-h` 查看完整参数）

| 脚本 | 用途 |
|---|---|
| `scripts/kb_config.py` | 配置与多 vault：init / find / add-vault / remove-vault / list / set-default / path / get / set / validate / migrate |
| `scripts/kb_env.py` | 环境自检：check（CLI/Obsidian/配置/vault，自动拉起）/ launch / cli-path |
| `scripts/html_export.py` | HTML 镜像：export（增量+清理，--full 全量）/ export-one（单篇） |
| `scripts/update_skill.py` | 发布辅助（每次改动后自动执行）：check / package / commit / release |

## references 索引（按需加载）

| 文件 | 何时读 |
|---|---|
| `references/cli-commands.md` | 需要命令细节、参数、例外清单、CLI 行为备注时 |
| `references/properties.md` | 需要属性集、标签约定、目录模板细节时 |
| `references/bases.md` | 创建 / 编辑 .base 视图时 |
| `references/canvas.md` | 创建 / 编辑 .canvas 画布时 |
| `references/trash-verification.md` | 需要引用删除安全性实测结论时 |
