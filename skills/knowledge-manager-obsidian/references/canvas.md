# Obsidian Canvas（.canvas）语法要点

> Canvas 基于 JSON Canvas 规范（jsoncanvas.org/spec/1.0/）。完整语法以官方规范
> 与 Obsidian 官方文档为准，本文只收要点与写入注意。

## 文件结构（JSON Canvas 1.0）

```json
{
  "nodes": [
    {
      "id": "16位小写十六进制",
      "type": "text",
      "text": "笔记内容",
      "x": 100, "y": 100,
      "width": 400, "height": 300
    },
    {
      "id": "...",
      "type": "file",
      "file": "笔记路径.md",
      "x": 600, "y": 100,
      "width": 400, "height": 300
    }
  ],
  "edges": [
    {
      "id": "...",
      "fromNode": "源节点id",
      "fromSide": "right",
      "toNode": "目标节点id",
      "toSide": "left",
      "label": "连线文字（可选）"
    }
  ],
  "groups": [
    {
      "id": "...",
      "label": "分组名",
      "nodes": ["节点id1", "节点id2"]
    }
  ]
}
```

要点：
- `nodes`：`text`（文字）、`file`（指向库内文件）、`group`（分组）等类型；
- `edges`：`fromNode` / `toNode` 引用节点 id，`fromSide` / `toSide` 取
  `top` / `right` / `bottom` / `left`；
- `groups`：把多个节点框进一个分组（可选背景色 / 标签）；
- 节点与边 id 全局唯一，用 16 位小写十六进制（64 位随机）。

## 写入注意（实测，需自行验证）

- **CLI 写不出合法 Canvas**：JSON 字符串内的字面 `\n` 会被命令行工具转成真实
  换行，破坏 JSON 结构——**.canvas 一律直接写文件**（直接文件访问例外清单
  第 1/2 条：工具对该内容类型不可用 + 需格式校验，回复中说明原因）。

## 写入后校验

1. `json.load` 可解析（合法 JSON）；
2. 所有 `fromNode` / `toNode` 引用存在的节点 id（边不悬空）；
3. 必填字段齐全（id / type / 坐标与尺寸）；
4. 失败则修正后重写并重新校验。
