# Canvas 实测经验（仅供参考）

> JSON Canvas 规范的完整语法（节点类型 / 边 / 布局 / 示例）以
> `@skill:json-canvas` 与官方规范 https://jsoncanvas.org/spec/1.0/ 为准。
> 本文件只保留 obsidian-kb 实测的写入经验，**可能随版本变化，需自行验证**。

## 实测经验（1.13.4，仅供参考）

1. **CLI 写不出合法 Canvas**：JSON 字符串内的字面 `\n` 会被 CLI 转成真实换行，
   破坏 JSON 结构 → **.canvas 一律直接写文件**（例外清单第 1/2 条：CLI 对该内容
   类型不可用 + 需格式校验，回复中说明原因）。
2. **写入后校验**（例外第 2 条，说明原因）：Python `json.load` 可解析；所有
   `fromNode` / `toNode` 引用存在的节点 ID；必填字段齐全。
3. **ID 约定**：节点 `id` 用 16 位小写十六进制（64 位随机），节点与边 ID 全局唯一。

## 校验要点（obsidian-kb 要求）

- JSON 合法、ID 唯一、边不悬空（fromNode/toNode 必须存在）；
- 失败则修正后重写并重新校验。
