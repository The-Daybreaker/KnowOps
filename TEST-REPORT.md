# obsidian-kb 测试记录与 forward-test 结果（v1.0.0，2026-08-03）

> 开发期交付物，不随 skill 打包。环境：Windows 11、Obsidian 1.13.4（CLI 随应用，
> `Obsidian.com`）、受管 Python 3.13.12、受管 Node 22.22.2（defuddle 隔离安装）。

## v0.6.0 拆分重构测试（2026-08-05）

- **quick_validate**：`skills/knowledge-base/` 与 `skills/obsidian-kb/` 双 skill
  均通过结构校验 ✅
- **脚本级测试 18/18**（.test-env/v0_6_test.py，临时目录）：
  - kb_config v4 init：默认写入 `<vault>/.config/knowledge-base.config.json`；
    find（含 .config/ 子目录查找）/ list / validate ✅
  - 位置规则：`--config` 指向 vault 用户笔记区 → 拒绝（提示"不能写入 vault 用户
    笔记区"）✅
  - migrate v3→v4：旧文件名 `obsidian-kb.config.json` 迁移到新文件名；旧默认
    exportRoot（vault 上级 HTML-Export）自动改为 `<vault>/.config/HTML-Export/`；
    补齐 configDir；旧文件保留 ✅
  - set/get 点号键；html_export export（--full）与 export-one ✅
- **真实 forward-test 6/6**（.test-env/forward_v06.py，测试库「Obsidian测试知识库」）：
  CLI 创建问题笔记（Python subprocess 传参，多行中文）→ 回读校验 → html_export
  export-one（v4 配置）→ CLI delete 进系统回收站（"Moved to trash"）→ 删除后
  读取失败 → 操作日志写入 `.config/log/` ✅
- 测试配置：`.test-env/obsidian-kb.config.json`（v3）已迁移到测试库
  `.config/knowledge-base.config.json`（v4），exportRoot 修正为
  `knowledge-base/.test-env/HTML-Export`（旧目录名路径已失效，一并修正）✅

## 〇〇、v1.3.0 变更 forward-test（2026-08-03，vault「知识库skill测试」）

- **HTML 只留 vault 级索引**：fake vault 导出验证——根级 `index.html` 不再生成，
  历史残留的根级索引被尽力清理；`<exportRoot>/<vault名>/index.html` 即详细索引 ✅
- **超长文本两步写入**：CLI create 占位（创建走 CLI）→ 直写 10152 字符 →
  回读长度一致（无截断）→ search 命中（Obsidian 索引识别直写内容）✅
- **kb_env 拉起（GPU 兜底）**：Obsidian 未运行环境下实测——普通拉起 12 秒无效果
  后自动以 `--in-process-gpu --disable-gpu --disable-software-rasterizer` 重拉，
  最终 "Obsidian 已拉起并就绪（1.13.4）" ✅（解决无 GPU 桌面/远程/沙箱环境
  "GPU process isn't usable. Goodbye." 导致拉起失败的问题；`cli_alive` 同时加固
  为忽略应用半就绪时的 "Error:" 假成功输出）
- 取消"普通→收件箱"兜底：SKILL.md 路由表更新为"无法判定 → 询问用户"（规则级
  变更，配置兼容）✅

## 〇、v1.2.0 分类路由 forward-test（2026-08-03，vault「知识库skill测试」）

- 相似检查命中既有笔记（00-Inbox/FPGA…疑问.md）→ 高相似提示成立 ✅
- 问题（纯文字）→ `问题/异步复位与同步复位问题.md`；问题（含资源）→
  `问题/引脚电平异常问题/`（md + png 同目录，附件复制例外已说明）✅
- 项目 → `项目/FPGA学习/第12讲课程笔记.md` ✅
- 联动：日志写入 `日志/2026-08/2026-08-03.md`（4 行分类日志）；
  TODO.md 自动创建并追加 3 条 `- [ ]` ✅
- 问题沉淀：property:set status=done/resolved → append 经验总结 →
  move 到 `知识与经验/` → `task path=TODO.md line=4 done` 勾选 `[x]` → 经验日志 ✅
- 镜像 export：6 笔记 + 1 附件，结构对应 ✅
- 兼容性：旧配置 migrate 补齐新偏好键且旧值（dailyFolder/gitCommit）不动 ✅

## 一、脚本自测

### kb_config.py（22 项，全部通过）

- init 默认写入 vault 上级目录、中文 vault 名、cliPath 写入、警告提示（无 .obsidian）✅
- find 从子目录向上发现 ✅；list / path（默认与按名）✅
- add-vault（重名拒绝、路径重复拒绝、不存在路径拒绝）✅；set-default ✅；
  remove-vault（默认回退）✅
- get/set：布尔 coercion（true/false）、字符串 ✅
- 拒绝项：配置写入 vault 内 ❌→拦截 ✅；exportRoot 写入 vault 内 ❌→拦截 ✅
- validate（问题/警告分级）✅；migrate（当前版本 no-op）✅
- 两个大知识库文件夹（KB-Home / KB-Home2）各自配置、互不冲突 ✅

### kb_env.py（通过）

- cli-path 三来源（配置 cliPath / PATH / 平台候选）✅
- check 全绿：配置有效、CLI 可用、Obsidian 运行（1.13.4）、vault 路径有效、
  目标 vault 已注册 ✅
- 拉起逻辑：`_obsidian_app_path` 由 Obsidian.com 正确推导同目录 Obsidian.exe ✅
  （真实拉起未测：需关闭用户 Obsidian，按约定不打扰；失败路径会明确提示手动打开）

### html_export.py（通过）

- 假 vault 全量：3 笔记 + 2 附件镜像、相对路径结构、index 双级 ✅
- 增量：mtime 未变全 skipped ✅；export-one 单篇 ✅
- 删除同步：源删除后 export 自动 prune 对应 HTML 并清理空目录 ✅
- 转换保真：frontmatter 属性表、标题锚点、wikilink（含 #标题锚点与 |别名）、
  未解析链接降级、callout、GFM 表格、任务列表（嵌套）、行内标签、
  代码块（verilog 原样）、Mermaid（CDN + 离线降级代码块）、
  注释 %% %% 剔除、数学降级等宽 ✅
- 修复记录：Markdown 相对图片路径按 笔记相对→vault 相对→basename 解析 ✅

### update_skill.py（通过）

- check：缺 CHANGELOG/DESIGN/手册时正确报缺 ✅
- package：zip 到 dist/，排除 REQUIREMENTS.md/.test-env/dist ✅
- commit 守卫：**曾误提交到上层仓库（knowledge-base），已用 `git reset --mixed HEAD~1`
  完整回滚（全部为新文件，工作区无损）**；修复为"要求 skill 目录本身是仓库根 +
  `git add -A -- .` 限定路径"后复测拒绝 ✅

## 二、forward-test（测试 vault：`.test-env/KB-Home/测试学习库`，用户 GUI 注册）

### 首次初始化（§4.9 / §14）

- 配置写入大知识库文件夹（vault 上级）、vault 内零 skill 残留 ✅
- 用户手册复制到根目录；追加一行后重跑不覆盖 ✅
- 日记按月切分（1.13.4 实测三步法）：
  `eval app.vault.setConfig('daily-notes',{folder,format})`（持久化 app.json）→
  `eval instance.options.folder/format=...`（立即生效）→
  目录缺失时 `eval app.vault.createFolder(...)`；
  `daily:append` 生成 `10-Daily/2026-08/2026-08-03.md` ✅

### 场景 A：FPGA 问题记录（§4.1 原样）

- 未回答技术问题 ✅；相似检查（search 无命中）✅
- 结构化笔记：`type: question`、`status: pending`、`source`、`created`、
  `tags: [fpga, 课程/小梅哥]` ✅；两段 Verilog 代码块逐字符保真 ✅
- Git 自动提交（`docs:` 前缀中文信息）✅；反馈路径并提示可发起复盘 ✅
- 复盘流：append 学习进展 → 再提交 ✅

### 场景 B：网页剪藏

- defuddle `--md` 提取 + `-p title` ✅（`-p domain` 为空 → 域名为 URL 解析）
- 笔记含 `type: clip`、`source_url`、`source_domain`、`clipped_at`（ISO）✅；
  存入 `40-Resources/Clips/` ✅

### 场景 C/D：日记与任务

- 日记按月生成（见初始化）✅；`daily:append` 加 `- [ ]` 任务 ✅；
  `tasks` 全库汇总（日记 + 笔记两处任务均列出）✅

### 场景 F：Bases / Canvas

- `.base`：真实换行 content 经 CLI 创建，`base:query` 正常返回（YAML 合法）✅
- `.canvas`：直写（CLI 无法保留 JSON 内字面 `\n`，例外已说明）→
  `json.load` 校验：合法、ID 唯一、边引用有效 ✅

### 场景 G：HTML 镜像

- 创建/修改 → export-one 增量 ✅；移动/删除 → export prune ✅；
  目录结构对应、index 可打开 ✅

### 场景 H：多 vault

- `vaults verbose` 列出 3 个已注册 vault ✅；
  `vault=<名>` 切换（测试学习库 / Obsidian知识库 只读 / Obsidian Vault 只读）✅；
  生产库全程只读（search/vault/files），零写入 ✅

### 安全与红线

- 删除回收站：2 篇测试笔记 CLI delete → `D:\$RECYCLE.BIN\<SID>` 内容逐字节一致、
  可还原 ✅（详见 `references/trash-verification.md`）
- 同意流程：移动前展示方案（源→目标、链接影响）后执行 ✅
- move 链接自动更新：Canvas 中 file 引用被 Obsidian 同步改写 ✅
- 高相似提示：再次检索"异步复位 同步复位"命中既有笔记，交由用户决策 ✅
- 非 Git 仓库跳过提交并提示；建仓后自动提交 ✅
- move 目标目录不存在时报 ENOENT → 先 `eval createFolder`（已写入 references）✅

### 发现的 CLI 怪癖（已写入 references/cli-commands.md）

1. 盘符陷阱：`\n` 转义形式下 `<字母>:\n`（如 `tags:\n`）被误判盘符，`\`→`/`
   → frontmatter 列表用行内数组；
2. `\n` 与 `\\n` 都会转成真实换行 → .canvas（JSON）无法经 CLI 写入，须直写；
3. `.` 开头文件名 create/delete 解析异常；
4. 单引号用 `'"'"'` 拼接；重要写入回读校验。

## 三、验收标准（§14）核对

| 条目 | 结果 |
|---|---|
| 从零初始化：配置与手册在 vault 上级、vault 无残留 | ✅ |
| 任意自定义 vault 名接入（测试学习库/第二个库） | ✅ |
| 手册与模板一致、重复初始化不覆盖 | ✅ |
| 两项目目录配置隔离 | ✅ |
| HTML 导出默认在大知识库文件夹内、名称位置经确认 | ✅ |
| CHANGELOG 与 DESIGN 随仓库维护、与版本一致（开发期文档，v1.4.0 起不进包） | ✅ |
| 版本升级模拟：配置可读取/迁移（migrate no-op + 缺省补齐逻辑） | ✅ |
| FPGA 示例全链路 | ✅ |
| 日记按月分目录 | ✅ |
| 剪藏带 source_url/source_domain | ✅ |
| 镜像结构对应、index 可打开、增删改同步 | ✅ |
| 删除进回收站可恢复 | ✅ |
| 修改/删除前同意环节 | ✅（流程演示） |
| 多 vault 切换 | ✅ |
| 高相似提示不阻断 | ✅ |
| Windows 可用、无 Windows 专属依赖（脚本纯 stdlib） | ✅ |
| quick_validate 通过、SKILL.md <500 行（243 行） | ✅ |

## 四、遗留说明

- `kb_env.py` 的真实拉起路径（Obsidian 关闭时）未实测——不打扰用户运行中的
  Obsidian；逻辑已实现（推导同级 Obsidian.exe → 拉起 → 轮询 40s → 明确提示）；
- Mermaid 渲染依赖 CDN（jsdelivr），手机端离线时降级为代码块（设计决策）；
- defuddle 安装于受管 Node 隔离环境，未污染系统；用户侧使用见其 defuddle skill。
