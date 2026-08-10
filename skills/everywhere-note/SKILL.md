---
name: everywhere-note
description: 随身记录与电脑端统一入库的配套 skill。在手机/随身设备上调用本 skill 后直接口述要记录的内容（灵感、随手记、待整理内容等），生成符合知识库格式的 markdown 条目，并设置当晚 22:00 提醒；回到电脑端后，由 obsidian-suite 路由加载本 skill 的桌面部分，将暂存内容解析写入 00 收件箱。不依赖特定 agent 或传输通道。
---

# everywhere-note 随身记录与统一入库

## 定位

一个 skill、两个能力部分，按运行环境渐进式按需加载：

| 部分 | 运行环境 | 加载文件 |
|---|---|---|
| 随身端捕获 | 手机/平板等移动或随身设备 | `references/mobile-capture.md` |
| 桌面端入库 | 桌面设备（可操作知识库的电脑） | `references/desktop-ingest.md` |

- 由 **agent 根据自身运行环境**判断是移动/随身设备还是桌面设备，不要用“能否操作
  Obsidian vault”判断。
- 随身端部分**独立自洽**：手机端只安装本 skill 即可完成“记录 → 规范 md →
  22:00 提醒”闭环，不依赖 knowledge-workflow / obsidian-suite。
- 桌面端部分由 **obsidian-suite 路由进入**：依赖方向为 obsidian-suite →
  everywhere-note（桌面部分），本 skill 不反向路由到 obsidian-suite。

## 路由

1. 收到记录/入库请求后，先按当前运行环境选择：
   - **移动/随身设备**：加载 `references/mobile-capture.md`，按其中流程执行；
   - **桌面设备**：仅当 obsidian-suite 路由而来（用户提供暂存内容/文件要求入库）
     时，加载 `references/desktop-ingest.md`；桌面端直接说“记一下……”仍由
     knowledge-workflow 处理，本 skill 不介入。
2. 环境不明确时，按用户所处场景判断，仍拿不准则问一句。

## 通用红线（两部分均遵守）

1. **信息以用户给出为准**：内容、时间、归属不自行臆造；缺关键信息时问一句。
2. **不越权分类**：随身端只标 `capture_kind` 与建议归属，不决定内容最终进入哪个
   知识模块。
3. **不改动已有内容**：本 skill 不修改/删除知识库已有笔记；涉及此类操作时交由
   知识库套件规则处理。
4. **提醒不撒谎**：设置成功才说已设置；平台做不到时如实说明并给出手动替代。

## references 索引（按需读取）

| 文件 | 何时读 |
|---|---|
| `references/mobile-capture.md` | 运行在移动/随身设备上，用户口述要记录的内容 |
| `references/desktop-ingest.md` | 桌面设备上由 obsidian-suite 路由，用户提供暂存内容/文件要求入库 |
| `assets/capture-template.md` | 生成暂存条目时对照模板与示例 |
