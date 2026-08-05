# knowledge-workflow / knowledge-manager-obsidian

通用知识库管理的**双 skill 组合**：一个管"知识库应该怎么组织"（工作流程规范），
一个管"怎么操作工具"（Obsidian 操作规范与红线）。二者能力边界清晰、配套使用。

## 两个 skill

| | knowledge-workflow | knowledge-manager-obsidian |
|---|---|---|
| 定位 | **工作流程规范（workflow）** | **工具操作规范** |
| 面向 | 用户与 agent 共同遵守的流程要求 | 对工具与执行者的统一要求 + Obsidian 专有操作 |
| 包含 | 模块路由（问题/项目/日程/知识/剪藏/日记/任务）、问题生命周期（未解决→已解决→沉淀分离）、知识分类沉淀、看板、日程、自动化提醒、操作日志、初始化向导、配置与 HTML 导出策略 | 统一红线（改删前征求同意、永不 git init、删除进回收站、直接文件访问例外清单）；Obsidian 专有（CLI 使用与怪癖、笔记读写改删、日记设置、Markdown/Bases/Canvas 语法要点、剪藏、两步写入、回读校验） |
| 不含 | 对 agent 的行为要求、对工具的操作要求、任何工具名 | 知识库业务规则（路由/生命周期/沉淀流程等） |

一句话：**knowledge-workflow 回答"知识库该长什么样、流程怎么走"，
knowledge-manager-obsidian 回答"执行时对工具和操作者的约束、Obsidian 具体
怎么操作"。**

## 快速开始

1. 加载 `knowledge-workflow`，按初始化向导接入知识库：
   - 确认 vault 实际路径与名称；
   - 配置默认写入 vault 内隐藏目录 `.config/`（可改选其他位置）；
   - 按需启用 HTML 镜像导出、创建看板。
2. 操作知识库时，Obsidian 侧的具体执行遵循 `knowledge-manager-obsidian` 的
   操作规范与红线。

> 工具层连接方式由使用者自行编排（例如让 agent 同时加载两个 skill，或配置
> 调度关系）；knowledge-workflow 本身不绑定任何工具。

## 目录结构

```
├── skills/
│   ├── knowledge-workflow/          # Skill A：知识库管理工作流程规范
│   │   ├── SKILL.md
│   │   ├── references/properties.md   # 属性/目录/生命周期领域设计
│   │   ├── scripts/                  # kb_config / kb_env / html_export
│   │   ├── assets/user-manual.md     # 用户手册模板
│   │   └── agents/openai.yaml
│   └── knowledge-manager-obsidian/  # Skill B：Obsidian 操作规范与红线
│       ├── SKILL.md
│       └── references/              # redlines / cli / markdown / bases / canvas
├── legacy/
│   ├── obsidian-kb/                 # 旧版 obsidian-kb 存档（仅历史参考，不含新功能）
│   └── dist-archive/                # 旧版本发布包归档（v1.0.0~v2.3.3）
├── dev/                             # 开发期资产（不进包）
│   ├── CHANGELOG.md / DESIGN.md / REQUIREMENTS.md / TEST-REPORT.md
│   └── scripts/update_skill.py      # 开发期发布工具（双 skill 打包）
└── dist/                            # 发布产物：两个 skill 的 zip
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

## 许可证

MIT License，见 [LICENSE](LICENSE)。
