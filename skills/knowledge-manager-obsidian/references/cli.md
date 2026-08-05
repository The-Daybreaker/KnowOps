# Obsidian CLI 操作与实测注意（通用化表述）

> 本文为 Obsidian 官方 CLI 的使用要点与跨平台实测注意；命令行为可能随版本
> 变化，**使用时需自行验证**。完整用法以 Obsidian 官方 CLI 文档为准。

## 命令速查

| 用途 | 命令形态 | 说明 |
|---|---|---|
| 版本/连通 | `version` | 探测 CLI 是否可连接运行中的 Obsidian |
| 列表 | `vaults` | 列出已注册 vault 名称 |
| 创建 | `create path=<路径>` | 路径参数用 `path=`（或 `name=`）；多行内容直接传 |
| 读取 | `read path=<路径>` | 按路径读取笔记内容 |
| 搜索 | `search <关键词>` | 全库搜索，用于相似检查与检索 |
| 追加 | `append file=<路径>` | 向已存在笔记追加内容 |
| 移动/重命名 | `move file=<源> path=<目标>` | 自动更新相关链接 |
| 删除 | `delete file=<路径>` | 默认进系统回收站；**严禁永久删除参数** |
| 日记 | `daily:append / daily:path` | 原生日记操作，依赖日记设置 |
| 配置 | `eval app.vault.setConfig(...)` 等 | 读取/修改应用配置（副作用可能报无害错误） |
| 插件 | 插件相关命令 | 管理插件（如启用状态） |

> 注意：`create` 用 `path=` / `name=` 指定路径；`append` / `read` / `delete` /
> `move` 用 `file=` 指定目标。

## 发现与连接

- 解析顺序：配置 `cliPath` → 系统 PATH → 平台常见安装位置（Windows 安装目录
  / macOS Applications）。
- 非 headless：连接已运行的 Obsidian；未运行时先自动拉起并轮询等待，失败则
  提示手动打开。
- 拉起兜底：Windows 可用 `--in-process-gpu` 等 GPU 兜底参数重试（解决无 GPU /
  远程 / 沙箱环境下启动即退出的问题）。

## 实测注意（跨平台通用表述，需自行验证）

1. **换行**：content 多行优先用真实换行；`\n` 转义序列可能被转成真实换行——
   JSON 类内容（.canvas）字符串内的字面 `\n` 会被破坏，无法经 CLI 写入，
   一律直接写文件（例外清单第 2 条）。
2. **盘符陷阱（Windows）**：转义换行下 `<字母>:\n`（如 `tags:\n`）可能被误判
   为盘符路径、`\` 变 `/`——frontmatter 列表改用行内数组 `tags: [a, b]`。
3. **含单引号内容**：`1'b0` 之类经 shell 拼接易错；用 Python subprocess 传参
   （参数列表直传，不经 shell）最稳。
4. **点开头文件名**：`.xxx.md` 可能解析异常（创建报错但文件已生成、删除找不到），
   避免点开头文件名。
5. **日记目录不存在**：`daily` 追加报目录不存在——先创建日记目录再操作。
6. **长参数截断**：命令行参数超长（约 4000 字符以上）可能截断——用两步写入
   （见 SKILL.md「长内容两步写入」）。
7. **`eval` 副作用**：`eval` 返回对象时报 "Converting circular structure to
   JSON" 属无害（副作用已生效，如 createFolder）。
8. **无创建 vault 命令**：新文件夹需在 Obsidian GUI「打开文件夹作为仓库」注册。

## 日记设置三步法（工具无专用命令时）

1. 持久化：`eval app.vault.setConfig('daily-notes', {folder, format})`
   （写入 `.obsidian/app.json`）；
2. 内存实例设置：`eval instance.options.folder/format = ...`（立即生效）；
3. 目录不存在时：`eval app.vault.createFolder(...)` 先建目录。
   三步缺一不可（仅 setConfig 运行中实例不刷新；仅改内存重启后丢失）。
