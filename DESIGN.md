# DESIGN — obsidian-kb 设计文档（v1.4.0）

## 1. 架构决策

### 1.1 Vault 是唯一数据源

不构建任何自研引擎：无 SQLite 索引、无同步映射表、无冲突副本、无守护进程、
无数据库。所有知识状态以 vault 内文件为准，Obsidian 本体负责索引与渲染。

### 1.2 操作通道：Obsidian CLI 唯一写入口

- 写入 / 修改 / 移动 / 重命名 / 删除：只走 Obsidian CLI；
- 读取：优先 CLI（`read` / `search` / `tasks` / `tags` / `backlinks` 等）；
- 直接文件访问仅限例外清单（见 `references/cli-commands.md` 末尾）：
  CLI 不可用且用户同意、格式校验、二进制附件、HTML 导出读源文件；
  每次例外使用必须在回复中说明原因。

理由：CLI 会维护 Obsidian 的索引、链接更新、模板展开与回收站语义；绕过 CLI
写文件会造成索引滞后与链接断裂。

### 1.3 配置驱动，零硬编码

- 配置文件 `obsidian-kb.config.json` 保存：vault 名→路径映射、默认 vault、
  HTML 导出根目录、CLI 路径、偏好（日记格式、目录、Git 开关等），带 `version` 字段；
- 发现顺序：会话显式指定 → 从当前目录向上查找 → 首次初始化向导；
- 默认写入**大知识库文件夹（vault 上级目录）**，绝不写入 vault 内部，
  不写入系统环境变量 / 全局用户目录 → 多个 agent / 项目并行管理不同知识库时
  配置互相隔离；
- vault 在 agent 项目之前已由用户创建、名称不统一，skill 不假设任何固定名称，
  初始化必须读取用户确认的实际路径与名称。

### 1.4 搜索不封装

CLI `search` 已完备，由 agent 直接调用；skill 不提供搜索工具。

### 1.4.1 知识模型：模块路由而非单一收件箱（v1.2.0 起，v1.3.0 修订）

创建动作先判定模块类型再路由：问题（`questionDir`，纯文字单文件 / 含资源建
同名文件夹）、项目（`projectsDir/<项目名>/`）、剪藏、日记；
**v1.3.0 起取消收件箱兜底**——判断不出类型时 agent 必须询问用户决策归属。
记录问题 / 项目联动写当日日志并追加根目录唯一待办文件（`todoFile`）。
问题具有生命周期：解决后从 `questionDir` 沉淀到 `knowledgeDir`，标注
`created`（出现日期）/ `resolved`（解决日期）与经验总结，TODO 同步勾选
（`task` 命令按行号操作）。目录约定默认纯中文，全部配置驱动可改。

### 1.4.2 写入通道分层（v1.3.0）

- 常规长度内容：全量走 CLI（保持索引一致）；
- 超长内容（>4000 字符）：**创建动作仍走 CLI**（`create` 占位文件，注册索引），
  内容本体直接写文件（CLI 参数长度受限，例外清单第 5 条），随后回读校验；
- 二进制附件：直接复制（例外第 3 条）；JSON（.canvas）：直接写（例外第 1/2 条）。

### 1.5 HTML 镜像导出

- 每次写操作后的固定流程（新增 / 修改 → `export-one`；删除 / 移动 → `export` 含清理）；
- 镜像位置：`<exportRoot>/<vault名>/<相对路径>.html`，默认导出根在大知识库文件夹内；
- **仅生成 vault 级索引 `index.html`**（v1.3.0 起不再生成导出根级索引，历史残留
  自动清理）；
- 自写轻量 Markdown 转换器（Python 标准库）：覆盖 Obsidian Flavored Markdown
  常用子集；Mermaid 用 CDN 渲染、离线降级为可读代码块；目标"跨设备可读"，
  不追求与 Obsidian 渲染一致；
- 不依赖 Obsidian 运行（例外清单第 4 条）。

### 1.6 安全模型

| 动作 | 规则 |
|---|---|
| 创建 | 无需同意；写前 CLI search 相似检查，高相似交用户决策 |
| 修改 / 移动 / 重命名 | 先展示方案，用户同意后执行；优先 CLI 原生命令（链接自动更新） |
| 删除 | 仅 CLI `delete`（系统回收站）；禁用 `permanent`；前同意、后同步镜像 |
| Git | 仅提交（`git add -A -- .` + 中文简述）；永不 `git init`；非仓库跳过并提示 |

## 2. 模块职责

| 模块 | 职责 | 关键设计 |
|---|---|---|
| `scripts/kb_config.py` | 配置发现与读写、多 vault 管理、schema 迁移 | 原子写（临时文件 + replace）；init 拒绝写入 vault 内；validate 区分问题与警告 |
| `scripts/kb_env.py` | CLI 发现、Obsidian 运行检查与拉起、配置 / vault 校验 | CLI 发现顺序：配置 cliPath → PATH → 平台常见位置；拉起用 cliPath 同级 `Obsidian.exe`（macOS 用 `open -a`），轮询等待就绪 |
| `scripts/html_export.py` | MD→HTML 转换、镜像导出、索引生成、附件复制、孤儿清理 | 增量按 mtime；wikilink 以 basename→路径映射解析；Markdown 相对资源按 笔记相对→vault 相对→basename 解析 |
| `scripts/update_skill.py` | 发布辅助：检查 / 打包 / 提交 | 提交要求 skill 目录本身是仓库根（防止污染上层仓库）；永不 `git init`；打包仅含运行时文件，排除开发期文档（REQUIREMENTS.md / TEST-REPORT.md / CHANGELOG.md / DESIGN.md / .test-env / dist） |
| `assets/user-manual.md` | 最终用户手册模板 | 初始化复制到大知识库文件夹，已存在不覆盖 |
| `references/` | 渐进披露的细节文档 | CLI 速查、属性约定、Bases / Canvas 要点、回收站实测 |

数据流：用户意图 → agent 按 SKILL.md 工作流 → CLI（写）/ 脚本（配置、导出）→
vault → 写后三件套（HTML 镜像 → Git 提交 → 反馈）。

## 3. 兼容性策略

- 语义化版本；配置 schema 带 `version`，变更在 `kb_config.MIGRATIONS` 注册迁移函数；
- 每次发布前置条件：`CHANGELOG.md` 与 `DESIGN.md` 同步更新、兼容性检查通过
  （旧配置可读取或可迁移、vault 内容不受影响、已生成的用户手册不被覆盖）；
- 破坏性变更必须升主版本，并在 CHANGELOG / DESIGN 中说明迁移方案；
- 配置新增偏好键时，迁移逻辑做"缺省补齐、不覆盖用户已有值"。

## 4. 发布约定（§12）

1. 更新 `CHANGELOG.md` 与 `DESIGN.md`（`vX.Y.Z - 描述`，含兼容性说明）；
2. 兼容性检查（见上节）；
3. 测试：`quick_validate.py` + 脚本自测 + 真实场景 forward-test；
4. 打包：`update_skill.py package` 生成 `dist/obsidian-kb-vX.Y.Z-<timestamp>.zip`
   （仅运行时文件，开发期文档 CHANGELOG / DESIGN / REQUIREMENTS / TEST-REPORT 不随包分发）；
5. Git 提交：`feat:/fix:/docs: vX.Y.Z - 描述`（`update_skill.py commit`）；
6. **仅在用户明确要求时执行发布**；日常开发不打包、不提交。

## 5. 已知限制与决策备忘（v1.0.0）

- **打包纯净（v1.4.0 决策）**：分发包仅含运行时文件（SKILL.md、agents/、
  scripts/、references/、assets/）；CHANGELOG / DESIGN / REQUIREMENTS /
  TEST-REPORT 为开发期文档，由 git 管理，不随包分发（打包排除项见
  `update_skill.py` EXCLUDE_*）。内置参考技能 `references/skills/`
  （obsidian-markdown / obsidian-cli / obsidian-bases / json-canvas / defuddle）
  自 v1.4.0 起移除，能力说明收敛于 SKILL.md 与顶层 references/ 文档。
- CLI 非 headless：写操作需要 Obsidian 运行；`kb_env.py` 显式拉起兜底，
  失败时提示用户手动打开；
- Daily Notes 格式无专用 CLI 设置项：初始化用 `eval` 写插件设置并验证，
  失败给一次性人工指引；
- `.base` / `.canvas` 创建优先走 CLI `create path=...`；CLI 不支持时直接写文件
  （例外并说明），再用 `base:query` / `json.load` 校验；
- Markdown 转换器为子集实现：脚注定义为纯文本降级、数学式等宽降级；
- 本机系统 `python` 可能不存在：SKILL.md 规定解释器发现顺序
  （PATH → `py -3` → WorkBuddy 受管运行时）。
