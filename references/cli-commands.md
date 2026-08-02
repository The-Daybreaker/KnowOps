# Obsidian CLI 命令速查（基于 1.13.4 实测）

> CLI 随版本演进，一切以 `"<cliPath>" help` 输出为准；单命令详情用
> `"<cliPath>" help <命令>`。本文件为 1.13.4 的实测摘要。

## 调用约定

- 参数带值用 `=`，值含空格加引号：`create name="My Note" content="Hello"`
- 布尔开关直接写：`silent`、`overwrite`、`total`
- 多行内容用 `\n`，制表用 `\t`
- `file=<名>` 按 wikilink 解析（可省路径与扩展名）；`path=<路径>` 从 vault 根算精确路径
- 省略 file/path 时作用于当前活动文件
- 多 vault：`vault="<名>"` 作**首参**
- 全量命令清单：`"<cliPath>" help`（约 90 个命令）

## 高频命令

| 需求 | 命令 |
|---|---|
| 创建 | `create name="<名>" content="<文本>" [template="<模板>"] [silent] [overwrite]`，或用 `path="<路径>.md"` |
| 追加 / 前插 | `append file="<f>" content="<t>"` / `prepend ...`（`inline` 不换行） |
| 读取 | `read file="<f>"` |
| 搜索 | `search query="<词>" limit=<n>`；带行上下文 `search:context` |
| 任务 | `tasks [todo\|daily]`、`task`（查看/更新单个任务） |
| 标签 | `tags sort=count counts`、`tag` |
| 属性 | `property:set name="<k>" value="<v>" file="<f>"`、`property:read`、`property:remove`、`properties` |
| 日记 | `daily`（打开）、`daily:append content="<t>"`、`daily:read`、`daily:path`、`daily:prepend` |
| 反链/出链 | `backlinks file="<f>"`、`links` |
| 移动/重命名 | `move file="<f>" to="<目标目录或新路径>"`（自动更新链接）、`rename` |
| 删除 | `delete file="<f>"`（**默认进系统回收站**；`permanent`= 彻底删除，本 skill 禁用） |
| 模板 | `templates`、`template:read`、`template:insert` |
| Bases | `bases`、`base:query file="<b>" [view="<v>"] format=json`、`base:create`、`base:views` |
| 文件/目录 | `files`、`folders`、`file`、`folder` |
| vault | `vault`（当前信息）、`vaults`（已注册列表，`verbose` 带路径） |
| 应用 | `version`、`open file="<f>"`、`reload`、`restart` |
| 插件命令 | `commands`（列命令 ID）、`command id=<id>`（执行） |
| 执行 JS | `eval code="<js>"`（在应用上下文运行，可改设置，如 Daily Notes 格式） |

## 已实测的 CLI 行为（1.13.4，Windows）

1. **非 headless**：CLI 通过本地 socket/命名管道连接已运行的 Obsidian。
   官方称"未运行时首条命令会拉起 app"，但自定义安装目录 / PATH 不全时不可靠
   （报 `The CLI is unable to find Obsidian...`）。`kb_env.py` 已实现显式拉起 + 轮询。
2. **delete 默认进系统回收站**，忽略 Obsidian 的 .trash 设置；`permanent` 才彻底删除
   （回收站实测记录见 `trash-verification.md`）。
3. **没有创建 vault 的 CLI 命令**；新文件夹需在 Obsidian GUI「打开文件夹作为仓库」注册。
4. **没有修改 Daily Notes 设置的专用命令**；实测可行序列（1.13.4）：
   `eval app.vault.setConfig('daily-notes',{folder,format})` 持久化（写入
   `.obsidian/app.json`）→ `eval instance.options.folder/format=...` 立即生效 →
   目录不存在时 `eval app.vault.createFolder(...)`。三步缺一不可（仅 setConfig
   运行中实例不刷新；仅改内存重启后丢失）。
5. CLI 无附件二进制导入能力 → 直接复制文件（例外第 3 条）。
6. 怪癖（均为 1.13.4 实测）：
   - **换行策略**：content 多行优先用 shell 单引号内的**真实换行**（最可靠）；
     `\n` 与 `\\n` 转义都会被 CLI 转成真实换行——因此 **JSON（.canvas）无法经
     CLI 写入**（JSON 字符串内的字面 `\n` 会被破坏），一律直接写文件（例外）；
   - **盘符陷阱**：`\n` 转义形式下，`<字母>:\n`（如 `tags:\n`）会被误判为
     Windows 盘符路径，`\` 变 `/` → frontmatter 列表用行内数组 `tags: [a, b]`；
   - 单引号字符：bash 中用 `'"'"'` 拼接（如 `1'"'"'d1` → `1'd1`）；
   - `.` 开头文件名 CLI 解析异常（create 报 TypeError 但文件已生成、delete 找不到）；
   - 日记目录不存在时 `daily:append` 报错，先 `eval app.vault.createFolder(...)`；
   - 重要写入后回读校验（`read path=...`）。

## 直接文件访问例外清单（§10.2，使用时必须在回复中说明原因）

1. CLI 不可用 / Obsidian 未运行，且用户明确同意继续；
2. 需对原始文件做格式校验（JSON / YAML / Canvas）；
3. 二进制附件导入（CLI 不支持时）；
4. HTML 导出读取源文件（`html_export.py` 的固有工作方式，不依赖 Obsidian 运行）。
