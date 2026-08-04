# Canvas（.canvas）要点 — JSON Canvas 规范 1.0

顶层结构：`{"nodes": [], "edges": []}`。

## 创建与校验流程

1. 按规范组装 JSON；节点 `id` 用 16 位小写十六进制（64 位随机），节点与边 ID 全局唯一
2. 写入：`"<cliPath>" create path="<目录>/<名>.canvas" content="<JSON>" silent`
   （CLI 不支持该扩展名时直接写文件，属例外并在回复中说明原因）
3. 校验（例外清单第 2 条，说明原因）：Python `json.load` 可解析；所有
   `fromNode` / `toNode` 引用存在的节点 ID；必填字段齐全
4. 换行陷阱：JSON 字符串中用 `\n`，不要用字面 `\\n`（会被渲染成两个字符）

## 节点类型

| type | 额外必填 | 说明 |
|---|---|---|
| `text` | `text` | Markdown 文本 |
| `file` | `file`（vault 内路径） | 文件卡片，`subpath` 可指 `#标题` |
| `link` | `url` | 外部链接 |
| `group` | — | 分组容器（`label`），子节点放在其坐标范围内 |

通用必填：`id` `type` `x` `y` `width` `height`；可选 `color`（预设 `"1"`红 `"2"`橙
`"3"`黄 `"4"`绿 `"5"`青 `"6"`紫，或 hex `"#FF0000"`）。

## 边

```json
{"id": "0123456789abcdef", "fromNode": "<id>", "toNode": "<id>",
 "fromSide": "right", "toSide": "left", "toEnd": "arrow", "label": "下一步"}
```

`fromSide`/`toSide` ∈ `top|right|bottom|left`；`fromEnd`/`toEnd` ∈ `none|arrow`。

## 布局约定

- 坐标可负，x 向右、y 向下，定位点为左上角；数组顺序 = 层级（后者在上）
- 节点间距 50–100px，组内边距 20–50px，对齐 10/20 网格更整洁
- 参考尺寸：小文本 250×120，中文本 400×200，文件卡片 400×300

## 最小示例

```json
{
  "nodes": [
    {"id": "6f0ad84f44ce9c17", "type": "text", "x": 0, "y": 0,
     "width": 300, "height": 120, "text": "# 学习路线\nFPGA 基础"},
    {"id": "a1b2c3d4e5f67890", "type": "file", "x": 400, "y": 0,
     "width": 400, "height": 300, "file": "项目/FPGA学习/课程笔记.md"}
  ],
  "edges": [
    {"id": "0123456789abcdef", "fromNode": "6f0ad84f44ce9c17",
     "toNode": "a1b2c3d4e5f67890", "fromSide": "right", "toSide": "left"}
  ]
}
```

规范全文：https://jsoncanvas.org/spec/1.0/ 。
