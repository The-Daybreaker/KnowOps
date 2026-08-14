---
name: knowops
metadata:
  version: 1.2.7
description: 知识库管理与 Obsidian 操作。当用户要求记录、整理、搜索、审阅知识库内容，执行 Obsidian 操作（读写改删笔记、移动、日记、插件、Bases/Canvas/Markdown），或将暂存内容/文件写入知识库（含从 GitHub 暂存库拉取新条目入库）时使用。工作流规范与执行红线按 references 渐进式加载；具体语法与命令以 obsidian-cli、obsidian-markdown、obsidian-bases、json-canvas、defuddle 及官方文档为准。
---

# knowops 知识库管理

## 定位

桌面端知识库管理的统一入口。本 skill 的 SKILL.md 只承载触发、前置引导、加载规则与
通用红线；业务流程、执行层红线与桌面入库流程均按需加载自 references/。

具体语法与命令以已安装的官方工具 skill（obsidian-cli / obsidian-markdown /
obsidian-bases / json-canvas / defuddle）为准；未安装时询问用户是否安装，拒绝则
用 Obsidian 官方文档（help.obsidian.md）兜底。GitHub 相关操作（暂存库拉取/移动）
由 agent 自行判断平台具备的能力（gh CLI / git / GitHub MCP 等）执行。

## 每次对话前置（任何任务开始前必做）

1. 确定目标 vault（用户指定 / 通过 Obsidian CLI 查询已注册 vault 供点选 / 当前目录
   向上查找 `.config/knowops.config.json`；仍不确定就询问用户，不猜测）。
2. 读取该 vault 的 `.config/knowops.config.json`（目录名、路径、HTML 导出、GitHub
   暂存库同步等偏好）。
3. 读取该 vault 的 `.config/agent-rules.md`（若存在：插件规则、额外红线、额外操作、
   旧库约定）。
4. 找不到配置 → 该 vault 尚未初始化 → 按 `references/init-config.md` 走初始化向导。

## 加载规则（先读引用，再操作）

| 任务 | 必读 | 按需 |
|---|---|---|
| 记录/管理/整理/搜索内容 | `references/workflow.md` | `references/properties.md` |
| 初始化、配置、HTML 导出、GitHub 暂存库配置 | `references/init-config.md` | `references/properties.md` |
| 执行 Obsidian 操作（读写改删、移动、日记、插件、Bases/Canvas/Markdown） | `references/redlines.md` | 官方工具 skill |
| 暂存内容/文件入库（含 GitHub 暂存库拉取） | `references/desktop-ingest.md`、`references/workflow.md`、`references/redlines.md` | 官方工具 skill |

> 任何写入/修改/移动/删除/归档操作前，必须读完对应引用后再执行。

## 通用红线

1. **删除永远进系统回收站且可恢复**。
2. **变更分级**：大规模影响文件、永久删除等高风险操作，先展示变更方案（源 → 目标、
   受影响的内容与链接），征得用户同意后再执行；工作流程内规定的变更（如沉淀后删除
   原收件箱文件）按流程执行；其余变更由 agent 按风险判断，低风险先执行，随后记录、
   告知用户并给出回退方案。
3. **不代为 `git init`**：vault 非 Git 仓库时提示用户可自行建仓。
4. **信息以用户给出为准**：不自行臆造；信息不足时询问补齐。
5. **创建前相似检查**：创建新内容前先搜索相似内容，高相似时由用户决策
   （合并 / 跳过 / 仍写入）。
6. **重要写入后回读校验**：写入/修改/移动后读回核对内容与结构。
7. **变更操作前读取 `.config/agent-rules.md`**：agent 读的个性化约束（插件规则、
   额外红线、额外操作、旧库约定）；文件不存在视为无额外约束。
