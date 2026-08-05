# Obsidian CLI 实测经验与例外清单（仅供参考）

> **本文件仅保留 1.13.4 实测的操作经验与坑**，以及本 skill 的直接文件访问例外清单。
> 命令的完整用法、参数与当前版本行为以 `@skill:obsidian-cli` 为准；
> 本文件内容可能过时，**使用时需自行验证**。

## 已实测的 CLI 行为（1.13.4，Windows，仅供参考）

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
6. **长参数截断风险**：CLI content 参数超长时可能被截断导致内容缺失/语法破坏
   （命令行参数长度受限）。超长内容（>4000 字符）**两步写入**：CLI `create` 先建
   占位文件（创建动作仍走 CLI）→ 文件系统直写完整内容 → 回读校验（例外第 5 条）。
7. 怪癖（均为 1.13.4 实测，**不同版本需自行验证**）：
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
4. HTML 导出读取源文件（`html_export.py` 的固有工作方式，不依赖 Obsidian 运行）；
5. 超长内容（>4000 字符）CLI 参数可能被截断：CLI 创建占位文件后直写完整内容
   （v1.3.0 起，见 SKILL.md「创建笔记」通用步骤 3）。
