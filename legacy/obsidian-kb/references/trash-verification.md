# CLI 删除 → 系统回收站 实测记录

> **仅供参考**：2026-08-03 在 1.13.4 实测，命令行为可能随版本变化，需自行验证；
> 命令用法以 `@skill:obsidian-cli` 为准。

> 目的：验证红线"删除只走 CLI、进系统回收站可恢复"在真实环境成立。

## 环境

- OS：Windows 11（win32），Obsidian 1.13.4（installer 1.13.4）
- CLI：`Obsidian.com`（随应用安装目录）
- 测试 vault：`.test-env/KB-Home/测试学习库`（D 盘）

## 步骤与结果（2026-08-03）

1. CLI 创建两篇测试笔记（`00-Inbox/异步复位与同步复位问题.md`、`00-Inbox/转义测试.md`）；
2. 执行 `"<cliPath>" vault="测试学习库" delete path="<笔记>"`，
   CLI 返回 `Moved to trash: <笔记>`；
3. 检查系统回收站 `D:\$RECYCLE.BIN\<SID>\`：
   - 两篇笔记均以 `$R*.md` 形式存在（内容逐字节一致），对应 `$I*.md` 元数据齐全；
   - 即 Windows 回收站标准结构，**可从回收站还原**；
4. 结论：**CLI `delete`（不带 `permanent`）默认进入系统回收站，可恢复**。
   与官方说明一致：该行为忽略 Obsidian 的".trash"设置项。

## 操作纪律（skill 红线）

- 删除命令**永不附加 `permanent`**（该参数绕过回收站彻底删除）；
- 删除前征得用户同意，并告知"进系统回收站、可恢复"；
- 严禁 `rm` / `Remove-Item` / Python `os.remove` 等任何绕过 CLI 的删除方式。

## 附：CLI 已知怪癖（1.13.4，实测）

| 现象 | 结论 |
|---|---|
| `create content=` 中 `\x27` 等十六进制转义 | 不支持，原样保留；单引号用 bash `'"'"'` 拼接 |
| 个别 `\n` 被渲染为 `/n` | 已定位：**盘符陷阱**——`<字母>:\n`（如 `tags:\n`）被 CLI 误判为 Windows 盘符路径，`\` 变 `/`；frontmatter 列表改用行内数组 `tags: [a, b]` 规避 |
| `.` 开头文件名 | create 报 TypeError 但文件实际已创建、delete 解析不到；避免点开头文件名 |
| `daily:append` 在日记目录不存在时 | 报 `Folder "<dir>" not found`；先用 `eval app.vault.createFolder(...)` 建目录 |
