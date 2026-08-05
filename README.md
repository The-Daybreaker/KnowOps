# knowledge-workflow / kb-obsidian / obsidian-suite

通用知识库管理的 **Obsidian skill 组合**：`knowledge-workflow` 管"知识库应该怎么
组织"（工作流程规范），`kb-obsidian` 管"怎么操作工具"（Obsidian 操作规范与红线），
`obsidian-suite` 是调度入口（告诉 agent 何时加载哪个 skill）。三者能力边界清晰、
配套使用。

## 三个 skill

| | knowledge-workflow | kb-obsidian | obsidian-suite |
|---|---|---|---|
| 定位 | **工作流程规范（workflow）** | **工具操作规范** | **调度入口** |
| 面向 | 用户与 agent 共同遵守的流程要求 | 对工具与执行者的统一要求 + Obsidian 专有操作 | agent（加载顺序指引） |
| 包含 | 模块路由（问题/项目/日程/知识/剪藏/日记/任务）、问题生命周期（未解决→已解决→沉淀分离）、知识分类沉淀、看板、日程、自动化提醒、操作日志、初始化向导、配置与 HTML 导出策略 | 统一红线（改删前征求同意、永不 git init、删除进回收站、记录归属询问用户、信息以用户给出为准、直接文件访问例外清单）；Obsidian 专有（CLI 使用与怪癖、笔记读写改删、日记设置、Markdown/Bases/Canvas 语法要点、剪藏、两步写入、回读校验） | 调度顺序：先 knowledge-workflow（业务流程）→ 再 kb-obsidian（操作规范）→ 工具型 skill 按需加载 |
| 不含 | 对 agent 的行为要求、对工具的操作要求、任何工具名 | 知识库业务规则（路由/生命周期/沉淀流程等） | 具体业务与操作内容 |

一句话：**knowledge-workflow 回答"知识库该长什么样、流程怎么走"，
kb-obsidian 回答"执行时对工具和操作者的约束、Obsidian 具体怎么操作"，
obsidian-suite 回答"该按什么顺序加载它们"。**

## 快速开始

1. 加载 `obsidian-suite`（调度入口）→ 按指引加载 `knowledge-workflow`，
   按初始化向导接入知识库：
   - 确认 vault 实际路径与名称；
   - 配置默认写入 vault 内隐藏目录 `.config/`（可改选其他位置）；
   - 按需启用 HTML 镜像导出、创建看板。
2. 操作知识库时，Obsidian 侧的具体执行遵循 `kb-obsidian` 的
   操作规范与红线。
3. 用到具体能力（CLI / Markdown / Bases / Canvas / 网页提取）时，
   按需加载对应工具型 skill。

> 工具层连接方式由使用者自行编排（例如让 agent 同时加载两个 skill，或配置
> 调度关系）；knowledge-workflow 本身不绑定任何工具。

## 目录结构

```
knowledge-base/
├── README.md                 # 中文说明
├── README.en.md              # English
├── LICENSE                   # MIT
├── .gitignore
└── skills/
    ├── knowledge-workflow/          # Skill A：知识库管理工作流程规范
    │   ├── SKILL.md
    │   ├── references/properties.md   # 属性/目录/生命周期领域设计
    │   ├── scripts/                  # kb_config / kb_env / html_export
    │   └── assets/user-manual.md     # 用户手册模板
    ├── kb-obsidian/                  # Skill B：Obsidian 操作规范与红线
    │   ├── SKILL.md
    │   └── references/              # redlines / cli / markdown / bases / canvas
    └── obsidian-suite/               # Skill C：调度入口（加载顺序指引）
        └── SKILL.md
```

## 核心约定

- **无收件箱**：记录请求先判定模块类型再路由；无法判定时询问用户归属；
- **创建前相似检查**；**改删前征求同意**；**删除进系统回收站、不做彻底删除**；
- **知识库无关文件默认收在 vault 内隐藏目录 `.config/`**（配置/日志/手册/导出），
  不写入用户笔记内容区、不影响笔记浏览；
- **配置驱动**：vault 名、目录、偏好全在 `knowledge-workflow.config.json`，不假设
  任何固定名称；旧配置可迁移（`kb_config.py migrate`）；
- **积极打标签 + 双向链接**；修改必更新 `updated`（精确到分钟）；
- **每次操作记日志**（`.config/log/`，含读取/搜索）。

## 相关项目

工具型 skill（obsidian-cli / obsidian-markdown / obsidian-bases / json-canvas /
defuddle）是 **Obsidian 官方技能仓库**的安装副本，可随官方更新：

- **https://github.com/kepano/obsidian-skills** —— Obsidian 官方 agent skills
  （obsidian-cli、obsidian-markdown、obsidian-bases、json-canvas、defuddle）
- defuddle 本体：https://github.com/kepano/defuddle

## 许可证

MIT License，见 [LICENSE](LICENSE)。
