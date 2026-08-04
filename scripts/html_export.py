#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""html_export.py - obsidian-kb HTML 镜像导出（Python 标准库，跨平台）

职责：
  - 将 vault 内 Markdown 笔记按相对路径镜像导出为独立 HTML 到 vault 外目录：
        <exportRoot>/<vault名>/<相对路径>.html
  - 增量导出（按 mtime）与全量导出（--full）；删除的笔记同步移除对应 HTML；
    附件按相对路径一并复制；生成 vault 级详细索引 index.html
    （v1.3.0 起不再生成导出根级索引，历史残留自动清理）。
  - 不依赖 Obsidian 处于打开状态；转换目标为"跨设备可读"，不追求与 Obsidian 完全一致。

自写轻量 Markdown 转换器覆盖（Obsidian Flavored Markdown 子集）：
  frontmatter（剥离并渲染属性表）、标题（带锚点）、段落、粗斜体/删除线/高亮、
  行内代码与代码块（语言标注）、任务列表、嵌套列表、表格、引用块、Callout、
  分隔线、外链、图片、wikilink 双链（含 #标题锚点与 |别名）、嵌入 ![[...]]、
  行内标签、脚注标记、数学式降级为等宽文本、Mermaid（CDN 渲染，离线降级为代码块）、
  Obsidian 注释 %%...%% 剔除。

例外说明（§10.2-4）：本脚本直接读取 vault 源文件——CLI 无法在无 Obsidian 时提供
等价批量读取，且导出本身不要求 Obsidian 运行，属于需求允许的例外场景。
"""

from __future__ import annotations

import argparse
import html
import json
import os
import posixpath
import re
import shutil
import sys
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

import kb_config  # noqa: E402

SKIP_DIR_PREFIX = "."          # 跳过 .obsidian / .git / .trash 等隐藏目录
NOTE_EXT = ".md"
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".bmp", ".avif"}
MERMAID_CDN = "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs"


# ---------------------------------------------------------------------------
# Markdown → HTML 轻量转换器
# ---------------------------------------------------------------------------

class LinkResolver:
    """wikilink 解析：basename（小写）→ vault 相对路径（posix，无扩展名）。"""

    def __init__(self, note_paths: list[str]):
        self.by_basename: dict[str, str] = {}
        self.by_path: dict[str, str] = {}
        for rel in note_paths:
            stem = rel[: -len(NOTE_EXT)] if rel.lower().endswith(NOTE_EXT) else rel
            self.by_path[stem.lower()] = stem
            base = posixpath.basename(stem).lower()
            self.by_basename.setdefault(base, stem)

    def resolve(self, target: str) -> str | None:
        t = target.strip().replace("\\", "/")
        if t.lower().endswith(NOTE_EXT):
            t = t[: -len(NOTE_EXT)]
        if t.lower() in self.by_path:
            return self.by_path[t.lower()]
        return self.by_basename.get(posixpath.basename(t).lower())


def slugify(heading: str, used: set[str]) -> str:
    s = re.sub(r"[^\w一-鿿\- ]", "", heading).strip().lower().replace(" ", "-")
    base, i = s or "section", 2
    while s in used:
        s = f"{base}-{i}"
        i += 1
    used.add(s)
    return s


class MdConverter:
    def __init__(self, resolver: LinkResolver, current_rel: str):
        self.resolver = resolver
        self.current_rel = current_rel          # 当前笔记 vault 相对路径（posix）
        self.current_dir = posixpath.dirname(current_rel)
        self.has_mermaid = False
        self._used_slugs: set[str] = set()
        self._code_blocks: list[str] = []

    # ---- 链接工具 ----

    def _href_to(self, target_stem: str, anchor: str = "") -> str:
        target_html = target_stem + ".html"
        rel = posixpath.relpath(target_html, self.current_dir or ".")
        return rel + (f"#{anchor}" if anchor else "")

    def _file_href(self, rel_path: str) -> str:
        return posixpath.relpath(rel_path, self.current_dir or ".")

    # ---- 行内处理 ----

    def render_inline(self, text: str) -> str:
        codes: list[str] = []

        def stash_code(m):
            codes.append(m.group(1))
            return f"\x00IC{len(codes) - 1}\x00"

        text = re.sub(r"`([^`\n]+)`", stash_code, text)
        text = html.escape(text, quote=False)

        # 嵌入 ![[...]]（先于普通 wikilink）
        def repl_embed(m):
            inner = m.group(1)
            parts = inner.split("|")
            target = parts[0].strip()
            size = parts[1].strip() if len(parts) > 1 else ""
            ext = posixpath.splitext(target)[1].lower()
            rel = self._resolve_any(target)
            if ext in IMAGE_EXTS:
                href = self._file_href(rel) if rel else html.escape(target)
                w = f' width="{html.escape(size)}"' if size.isdigit() else ""
                alt = html.escape(posixpath.basename(target))
                return f'<img class="embed" src="{href}" alt="{alt}"{w}>'
            if rel:
                label = html.escape(posixpath.basename(target))
                return f'<a class="wikilink embed-file" href="{self._href_to(rel[: -len(NOTE_EXT)] if rel.lower().endswith(NOTE_EXT) else rel)}">{label}</a>'
            return f'<span class="unresolved">![[{html.escape(inner)}]]</span>'

        text = re.sub(r"!\[\[([^\]]+)\]\]", repl_embed, text)

        # wikilink [[target#anchor|display]]
        def repl_wikilink(m):
            target, anchor, display = m.group(1), m.group(2) or "", m.group(3)
            label = display or (anchor.lstrip("#") if anchor else "") or posixpath.basename(target)
            stem = self.resolver.resolve(target)
            if stem:
                anchor_slug = ""
                if anchor:
                    anchor_slug = re.sub(r"[^\w一-鿿\- ]", "", anchor.lstrip("#")).strip().lower().replace(" ", "-")
                return f'<a class="wikilink" href="{self._href_to(stem, anchor_slug)}">{html.escape(label)}</a>'
            return f'<span class="unresolved">{html.escape(label)}</span>'

        text = re.sub(r"\[\[([^\]|#]+)(#[^\]|]*)?(?:\|([^\]]+))?\]\]", repl_wikilink, text)

        # 图片与外链（相对路径按 vault 内文件解析并转为相对镜像路径）
        def repl_img(m):
            alt, url = m.group(1), m.group(2)
            resolved = self._resolve_resource(url)
            return f'<img src="{html.escape(resolved)}" alt="{alt}">'

        def repl_link(m):
            label, url = m.group(1), m.group(2)
            resolved = self._resolve_resource(url)
            if resolved.lower().endswith(NOTE_EXT):
                resolved = resolved[: -len(NOTE_EXT)] + ".html"
            return f'<a href="{html.escape(resolved)}">{label}</a>'

        text = re.sub(r"!\[([^\]]*)\]\(([^)\s]+)\)", repl_img, text)
        text = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", repl_link, text)

        # 强调
        text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
        text = re.sub(r"(?<!\w)\*([^*\n]+)\*(?!\w)", r"<em>\1</em>", text)
        text = re.sub(r"(?<!\w)_([^_\n]+)_(?!\w)", r"<em>\1</em>", text)
        text = re.sub(r"~~([^~]+)~~", r"<del>\1</del>", text)
        text = re.sub(r"==([^=]+)==", r"<mark>\1</mark>", text)

        # 数学式降级为等宽文本
        text = re.sub(r"\$([^$\n]+)\$", r'<code class="math">\1</code>', text)

        # 行内标签
        text = re.sub(
            r"(?<![\w/&#])#([A-Za-z0-9_\-/一-鿿]+)",
            r'<span class="tag">#\1</span>',
            text,
        )

        # 脚注引用
        text = re.sub(r"\[\^([^\]]+)\]", r'<sup class="footnote-ref">[\1]</sup>', text)

        def restore_code(m):
            return f"<code>{html.escape(codes[int(m.group(1))], quote=False)}</code>"

        text = re.sub(r"\x00IC(\d+)\x00", restore_code, text)
        return text

    def _resolve_resource(self, url: str) -> str:
        """Markdown 链接/图片路径解析：绝对 URL 原样返回；相对路径依次按
        笔记相对 → vault 相对 → basename 匹配解析，命中则返回镜像相对路径。"""
        if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", url) or url.startswith(("#", "//")):
            return url
        parts = url.split("#", 1)
        clean = parts[0].replace("\\", "/")
        anchor = ("#" + parts[1]) if len(parts) > 1 else ""
        for cand in (posixpath.normpath(posixpath.join(self.current_dir, clean)),
                     posixpath.normpath(clean)):
            if cand in self._all_files:
                return self._file_href(cand) + anchor
        base = posixpath.basename(clean).lower()
        for f in self._all_files:
            if posixpath.basename(f).lower() == base:
                return self._file_href(f) + anchor
        return url

    def _resolve_any(self, target: str) -> str | None:
        """按 vault 相对路径或 basename 解析任意文件（附件或笔记）。"""
        t = target.strip().replace("\\", "/")
        cand = posixpath.normpath(posixpath.join(self.current_dir, t)) if not t.startswith("/") else t.lstrip("/")
        if cand.lower() in self.resolver.by_path or cand in self._all_files:
            return cand
        base = posixpath.basename(t).lower()
        if base in self.resolver.by_basename:
            stem = self.resolver.by_basename[base]
            return stem + NOTE_EXT
        for f in self._all_files:
            if posixpath.basename(f).lower() == base:
                return f
        return None

    _all_files: set[str] = set()

    # ---- 块级处理 ----

    def render(self, md_text: str) -> tuple[str, dict[str, str]]:
        md_text = md_text.replace("\r\n", "\n").replace("\r", "\n")
        frontmatter, body = self._split_frontmatter(md_text)

        # 保护代码块
        def stash_block(m):
            lang = (m.group(1) or "").strip().lower()
            code = m.group(2)
            if lang == "mermaid":
                self.has_mermaid = True
                block = f'<pre class="mermaid">{html.escape(code, quote=False)}</pre>'
            else:
                cls = f' class="language-{html.escape(lang)}"' if lang else ""
                block = f"<pre><code{cls}>{html.escape(code, quote=False)}</code></pre>"
            self._code_blocks.append(block)
            return f"\n\x00CB{len(self._code_blocks) - 1}\x00\n"

        body = re.sub(r"```(\w*)\n(.*?)```", stash_block, body, flags=re.DOTALL)
        # 剔除 Obsidian 注释
        body = re.sub(r"%%.*?%%", "", body, flags=re.DOTALL)

        html_body = self._render_blocks(body.split("\n"))
        return html_body, frontmatter

    def _split_frontmatter(self, text: str) -> tuple[dict[str, str], str]:
        if not text.startswith("---\n"):
            return {}, text
        end = text.find("\n---", 4)
        if end == -1:
            return {}, text
        raw = text[4:end]
        rest = text[end + 4:].lstrip("\n")
        fm: dict[str, str] = {}
        key = None
        for line in raw.split("\n"):
            m = re.match(r"^([A-Za-z0-9_\-]+):\s*(.*)$", line)
            if m:
                key = m.group(1)
                fm[key] = m.group(2).strip()
            elif key and re.match(r"^\s+-\s+", line):
                item = re.sub(r"^\s+-\s+", "", line).strip()
                fm[key] = (fm[key] + ", " + item) if fm[key] else item
        return fm, rest

    def _render_blocks(self, lines: list[str]) -> str:
        out: list[str] = []
        i = 0
        n = len(lines)
        para: list[str] = []

        def flush_para():
            if para:
                joined = " ".join(x.strip() for x in para).strip()
                if joined:
                    out.append(f"<p>{self.render_inline(joined)}</p>")
                para.clear()

        while i < n:
            line = lines[i]

            m = re.match(r"^\x00CB(\d+)\x00\s*$", line)
            if m:
                flush_para()
                out.append(self._code_blocks[int(m.group(1))])
                i += 1
                continue

            if not line.strip():
                flush_para()
                i += 1
                continue

            m = re.match(r"^(#{1,6})\s+(.*)$", line)
            if m:
                flush_para()
                level = len(m.group(1))
                text = m.group(2).strip()
                anchor = slugify(re.sub(r"[*_~=`]", "", text), self._used_slugs)
                out.append(f'<h{level} id="{anchor}">{self.render_inline(text)}</h{level}>')
                i += 1
                continue

            if re.match(r"^\s*(-{3,}|\*{3,}|_{3,})\s*$", line):
                flush_para()
                out.append("<hr>")
                i += 1
                continue

            if line.lstrip().startswith(">"):
                flush_para()
                quote_lines = []
                while i < n and lines[i].lstrip().startswith(">"):
                    quote_lines.append(re.sub(r"^\s*> ?", "", lines[i]))
                    i += 1
                out.append(self._render_quote(quote_lines))
                continue

            if self._is_table_start(lines, i):
                flush_para()
                table_html, consumed = self._render_table(lines[i:])
                out.append(table_html)
                i += consumed
                continue

            if re.match(r"^\s*(?:[-*+] |\d+\. )", line):
                flush_para()
                list_lines = []
                while i < n and (re.match(r"^\s*(?:[-*+] |\d+\. )", lines[i]) or
                                 (lines[i].startswith(("  ", "\t")) and lines[i].strip())):
                    list_lines.append(lines[i])
                    i += 1
                out.append(self._render_list(list_lines))
                continue

            para.append(line)
            i += 1

        flush_para()
        return "\n".join(out)

    def _render_quote(self, qlines: list[str]) -> str:
        first = qlines[0] if qlines else ""
        m = re.match(r"^\[!(\w+)\][+-]?\s*(.*)$", first)
        if m:
            ctype, title = m.group(1).lower(), m.group(2).strip()
            content_lines = qlines[1:]
            body = "<br>\n".join(self.render_inline(x) for x in content_lines if x.strip())
            title_html = self.render_inline(title) if title else ctype.capitalize()
            return (f'<div class="callout callout-{ctype}">'
                    f'<div class="callout-title">{title_html}</div>'
                    f'<div class="callout-body">{body}</div></div>')
        body = "<br>\n".join(self.render_inline(x) for x in qlines if x.strip())
        return f"<blockquote><p>{body}</p></blockquote>"

    @staticmethod
    def _is_table_start(lines: list[str], i: int) -> bool:
        if i + 1 >= len(lines):
            return False
        head, sep = lines[i], lines[i + 1]
        return ("|" in head and re.match(r"^\s*\|?[\s:|-]+\|?\s*$", sep) is not None
                and "-" in sep)

    def _render_table(self, lines: list[str]) -> tuple[str, int]:
        def split_row(row: str) -> list[str]:
            row = row.strip()
            if row.startswith("|"):
                row = row[1:]
            if row.endswith("|"):
                row = row[:-1]
            return [c.strip() for c in row.split("|")]

        header = split_row(lines[0])
        consumed = 2
        rows = []
        while consumed < len(lines) and "|" in lines[consumed] and lines[consumed].strip():
            rows.append(split_row(lines[consumed]))
            consumed += 1
        parts = ["<table><thead><tr>"]
        parts += [f"<th>{self.render_inline(c)}</th>" for c in header]
        parts.append("</tr></thead><tbody>")
        for r in rows:
            parts.append("<tr>" + "".join(f"<td>{self.render_inline(c)}</td>" for c in r) + "</tr>")
        parts.append("</tbody></table>")
        return "".join(parts), consumed

    def _render_list(self, lines: list[str]) -> str:
        # 1) 解析为扁平项 [indent, ltype, content]
        flat: list[list] = []
        for raw in lines:
            m = re.match(r"^(\s*)([-*+]|\d+\.)\s+(.*)$", raw)
            if m:
                indent = len(m.group(1).replace("\t", "    "))
                ltype = "ol" if m.group(2)[0].isdigit() else "ul"
                flat.append([indent, ltype, m.group(3)])
            elif flat:
                flat[-1][2] += " " + raw.strip()
        # 2) 按缩进建树：(ltype, content, children)
        root: list = []
        stack: list[tuple[int, list]] = [(-1, root)]
        for indent, ltype, content in flat:
            while len(stack) > 1 and indent <= stack[-1][0]:
                stack.pop()
            node = (ltype, content, [])
            stack[-1][1].append(node)
            stack.append((indent, node[2]))

        # 3) 渲染
        def build(children: list) -> str:
            if not children:
                return ""
            ltype = children[0][0]
            parts = [f"<{ltype}>"]
            for _, content, kids in children:
                task = re.match(r"^\[([ xX])\]\s+(.*)$", content)
                if task:
                    checked = " checked" if task.group(1).lower() == "x" else ""
                    inner = (f'<input type="checkbox" disabled{checked}> '
                             f'{self.render_inline(task.group(2))}')
                    parts.append(f'<li class="task">{inner}{build(kids)}</li>')
                else:
                    parts.append(f"<li>{self.render_inline(content)}{build(kids)}</li>")
            parts.append(f"</{ltype}>")
            return "".join(parts)

        return build(root)


# ---------------------------------------------------------------------------
# HTML 页面模板
# ---------------------------------------------------------------------------

PAGE_CSS = """
:root { --fg:#1f2328; --muted:#6a737d; --bg:#ffffff; --panel:#f6f8fa; --border:#d0d7de;
        --accent:#0969da; --code-bg:#eff1f3; }
* { box-sizing: border-box; }
body { margin:0; padding:24px 16px; background:var(--bg); color:var(--fg);
       font:16px/1.7 -apple-system,"Segoe UI","Microsoft YaHei",sans-serif; }
main { max-width:820px; margin:0 auto; }
a { color:var(--accent); text-decoration:none; } a:hover { text-decoration:underline; }
h1,h2,h3,h4,h5,h6 { line-height:1.35; margin:1.4em 0 .5em; }
h1 { padding-bottom:.3em; border-bottom:1px solid var(--border); }
h2 { padding-bottom:.2em; border-bottom:1px solid var(--border); }
code { background:var(--code-bg); border-radius:6px; padding:.15em .4em; font-size:.9em;
       font-family:ui-monospace,Consolas,"Courier New",monospace; }
pre { background:var(--panel); border:1px solid var(--border); border-radius:8px;
      padding:12px 14px; overflow-x:auto; }
pre code { background:none; padding:0; }
blockquote { margin:1em 0; padding:.2em 1em; color:var(--muted);
             border-left:4px solid var(--border); background:var(--panel); }
table { border-collapse:collapse; margin:1em 0; width:100%; }
th,td { border:1px solid var(--border); padding:6px 12px; text-align:left; }
th { background:var(--panel); }
img { max-width:100%; }
mark { background:#fff8c5; padding:0 .2em; border-radius:3px; }
hr { border:none; border-top:1px solid var(--border); margin:1.6em 0; }
.tag { display:inline-block; background:#ddf4ff; color:#0550ae; border-radius:12px;
       padding:0 .6em; font-size:.85em; }
.wikilink { border-bottom:1px dashed var(--accent); }
.unresolved { color:var(--muted); border-bottom:1px dashed var(--muted); }
li.task { list-style:none; margin-left:-1.4em; }
li.task input { margin-right:.4em; }
.props { width:100%; margin:0 0 1.2em; font-size:.9em; }
.props th { width:8em; color:var(--muted); }
.callout { border:1px solid var(--border); border-left-width:4px; border-radius:8px;
           padding:10px 14px; margin:1em 0; background:var(--panel); }
.callout-title { font-weight:600; margin-bottom:4px; }
.callout-note,.callout-info,.callout-tip { border-left-color:#0969da; }
.callout-warning,.callout-caution { border-left-color:#bf8700; }
.callout-danger,.callout-bug,.callout-failure { border-left-color:#d1242f; }
.callout-success { border-left-color:#1a7f37; }
.callout-question,.callout-example { border-left-color:#8250df; }
.meta-bar { color:var(--muted); font-size:.85em; margin-bottom:1em;
            padding-bottom:.6em; border-bottom:1px solid var(--border); }
footer { margin-top:3em; color:var(--muted); font-size:.8em; text-align:center; }
pre.mermaid { background:var(--panel); }
.idx-folder { margin-top:1.2em; font-weight:600; }
.idx-list { list-style:none; padding-left:1em; }
.idx-list li { margin:.25em 0; }
.idx-time { color:var(--muted); font-size:.8em; margin-left:.6em; }
#filter { width:100%; padding:8px 12px; border:1px solid var(--border); border-radius:8px;
          font-size:1em; margin-bottom:1em; }
"""

MERMAID_SCRIPT = f"""
<script type="module">
try {{
  const m = (await import("{MERMAID_CDN}")).default;
  m.initialize({{ startOnLoad: true, theme: "default" }});
}} catch (e) {{ /* 离线时降级：保留为可读代码块 */ }}
</script>
"""


def render_page(title: str, body_html: str, frontmatter: dict[str, str],
                source_rel: str, has_mermaid: bool, depth: int) -> str:
    parts = ["<!DOCTYPE html>", '<html lang="zh-CN"><head>',
             '<meta charset="utf-8">',
             '<meta name="viewport" content="width=device-width, initial-scale=1">',
             f"<title>{html.escape(title)}</title>",
             f"<style>{PAGE_CSS}</style></head><body><main>"]
    home_href = posixpath.join(*([".."] * depth), "index.html") if depth else "index.html"
    parts.append(f'<div class="meta-bar"><a href="{home_href}">⌂ 索引</a> · 源文件：'
                 f'{html.escape(source_rel)}</div>')
    if frontmatter:
        parts.append('<table class="props"><tbody>')
        for k, v in frontmatter.items():
            parts.append(f"<tr><th>{html.escape(k)}</th><td>{html.escape(v)}</td></tr>")
        parts.append("</tbody></table>")
    parts.append(body_html or "<p>（空笔记）</p>")
    parts.append("<footer>由 obsidian-kb html_export 生成</footer>")
    parts.append("</main>")
    if has_mermaid:
        parts.append(MERMAID_SCRIPT)
    parts.append("</body></html>")
    return "\n".join(parts)


def render_index(vault_name: str, entries: list[tuple[str, float]]) -> str:
    items = []
    for rel, mtime in sorted(entries):
        href = rel[: -len(NOTE_EXT)] + ".html"
        folder = posixpath.dirname(rel) or "（根目录）"
        t = time.strftime("%Y-%m-%d %H:%M", time.localtime(mtime))
        items.append((folder, href, posixpath.basename(rel), t))
    parts = ["<!DOCTYPE html>", '<html lang="zh-CN"><head><meta charset="utf-8">',
             '<meta name="viewport" content="width=device-width, initial-scale=1">',
             f"<title>{html.escape(vault_name)} · 笔记索引</title>",
             f"<style>{PAGE_CSS}</style></head><body><main>",
             f"<h1>{html.escape(vault_name)} · 笔记索引</h1>",
             '<input id="filter" placeholder="输入关键词过滤…" '
             'oninput="document.querySelectorAll(\'.idx-list li\').forEach(li=>'
             'li.style.display=li.textContent.toLowerCase().includes('
             'this.value.toLowerCase())?\'\':\'none\')">']
    current = None
    for folder, href, name, t in items:
        if folder != current:
            if current is not None:
                parts.append("</ul>")
            parts.append(f'<div class="idx-folder">📁 {html.escape(folder)}</div><ul class="idx-list">')
            current = folder
        parts.append(f'<li><a href="{html.escape(href)}">{html.escape(name)}</a>'
                     f'<span class="idx-time">{t}</span></li>')
    if current is not None:
        parts.append("</ul>")
    parts.append(f"<footer>共 {len(items)} 篇 · 由 obsidian-kb html_export 生成 · "
                 f"{time.strftime('%Y-%m-%d %H:%M')}</footer>")
    parts.append("</main></body></html>")
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# 导出逻辑
# ---------------------------------------------------------------------------

def scan_vault(vault_path: str) -> tuple[list[str], list[str]]:
    """返回 (笔记相对路径列表, 附件相对路径列表)，均为 posix 相对路径。"""
    notes, others = [], []
    for dirpath, dirnames, filenames in os.walk(vault_path):
        dirnames[:] = [d for d in dirnames if not d.startswith(SKIP_DIR_PREFIX)]
        for fn in filenames:
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, vault_path).replace(os.sep, "/")
            if fn.lower().endswith(NOTE_EXT):
                notes.append(rel)
            else:
                others.append(rel)
    return sorted(notes), sorted(others)


def mirror_root_for(export_root: str, vault_name: str) -> str:
    return os.path.join(export_root, vault_name)


def convert_one(vault_path: str, mirror_root: str, rel: str,
                resolver: LinkResolver, force: bool = False) -> str:
    """转换单篇笔记。返回状态：written / skipped。"""
    src = os.path.join(vault_path, rel.replace("/", os.sep))
    html_rel = rel[: -len(NOTE_EXT)] + ".html" if rel.lower().endswith(NOTE_EXT) else rel + ".html"
    dst = os.path.join(mirror_root, html_rel.replace("/", os.sep))
    if not force and os.path.exists(dst) and os.path.getmtime(dst) >= os.path.getmtime(src):
        return "skipped"
    with open(src, "r", encoding="utf-8") as f:
        text = f.read()
    conv = MdConverter(resolver, rel)
    body, fm = conv.render(text)
    title = fm.get("title") or posixpath.basename(rel[: -len(NOTE_EXT)])
    depth = rel.count("/")
    page = render_page(title, body, fm, rel, conv.has_mermaid, depth)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    with open(dst, "w", encoding="utf-8", newline="\n") as f:
        f.write(page)
    return "written"


def copy_attachment(vault_path: str, mirror_root: str, rel: str) -> str:
    src = os.path.join(vault_path, rel.replace("/", os.sep))
    dst = os.path.join(mirror_root, rel.replace("/", os.sep))
    if os.path.exists(dst) and os.path.getmtime(dst) >= os.path.getmtime(src):
        return "skipped"
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)
    return "copied"


def prune_mirror(mirror_root: str, notes: list[str], attachments: list[str]) -> list[str]:
    """移除镜像中源已不存在的文件，返回被移除的相对路径列表。"""
    expected = set()
    for rel in notes:
        expected.add((rel[: -len(NOTE_EXT)] + ".html").lower())
    expected.update(a.lower() for a in attachments)
    removed = []
    for dirpath, dirnames, filenames in os.walk(mirror_root):
        for fn in filenames:
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, mirror_root).replace(os.sep, "/")
            if rel.lower() == "index.html":
                continue
            if rel.lower() not in expected:
                os.unlink(full)
                removed.append(rel)
    # 清理空目录
    for dirpath, dirnames, filenames in os.walk(mirror_root, topdown=False):
        if dirpath != mirror_root and not os.listdir(dirpath):
            os.rmdir(dirpath)
    return removed


def cmd_export(args) -> dict:
    vault_name, vault_path, export_root = _resolve_paths(args)
    mirror_root = mirror_root_for(export_root, vault_name)
    os.makedirs(mirror_root, exist_ok=True)

    notes, attachments = scan_vault(vault_path)
    resolver = LinkResolver(notes)
    MdConverter._all_files = set(notes) | set(attachments)

    stats = {"written": 0, "skipped": 0, "copied": 0, "pruned": []}
    for rel in notes:
        status = convert_one(vault_path, mirror_root, rel, resolver, force=args.full)
        stats["written" if status == "written" else "skipped"] += 1
    for rel in attachments:
        if copy_attachment(vault_path, mirror_root, rel) == "copied":
            stats["copied"] += 1
    stats["pruned"] = prune_mirror(mirror_root, notes, attachments)

    index_entries = [(rel, os.path.getmtime(os.path.join(vault_path, rel.replace("/", os.sep))))
                     for rel in notes]
    with open(os.path.join(mirror_root, "index.html"), "w", encoding="utf-8", newline="\n") as f:
        f.write(render_index(vault_name, index_entries))
    _clean_root_index(export_root)

    return {
        "vault": vault_name, "mirrorRoot": mirror_root,
        "notes": len(notes), "attachments": len(attachments),
        **stats,
    }


def cmd_export_one(args) -> dict:
    vault_name, vault_path, export_root = _resolve_paths(args)
    mirror_root = mirror_root_for(export_root, vault_name)
    rel = args.file.replace("\\", "/").lstrip("/")
    if os.path.isabs(args.file):
        rel = os.path.relpath(args.file, vault_path).replace(os.sep, "/")
    if not rel.lower().endswith(NOTE_EXT):
        rel += NOTE_EXT
    src = os.path.join(vault_path, rel.replace("/", os.sep))
    if not os.path.isfile(src):
        raise ExportError(f"笔记不存在：{rel}")
    notes, attachments = scan_vault(vault_path)
    resolver = LinkResolver(notes)
    MdConverter._all_files = set(notes) | set(attachments)
    status = convert_one(vault_path, mirror_root, rel, resolver, force=True)
    index_entries = [(r, os.path.getmtime(os.path.join(vault_path, r.replace("/", os.sep))))
                     for r in notes]
    os.makedirs(mirror_root, exist_ok=True)
    with open(os.path.join(mirror_root, "index.html"), "w", encoding="utf-8", newline="\n") as f:
        f.write(render_index(vault_name, index_entries))
    _clean_root_index(export_root)
    return {"vault": vault_name, "file": rel, "status": status,
            "html": (rel[: -len(NOTE_EXT)] + ".html")}


def _clean_root_index(export_root: str) -> None:
    """v1.3.0 起不再生成导出根级 index.html（只保留 vault 级详细索引）；
    若历史导出残留了根级 index.html，在此尽力移除（失败不阻断导出）。"""
    root_index = os.path.join(export_root, "index.html")
    if os.path.isfile(root_index):
        try:
            os.unlink(root_index)
        except OSError:
            pass


class ExportError(Exception):
    pass


def _resolve_paths(args) -> tuple[str, str, str]:
    """返回 (vault_name, vault_path, export_root)。优先命令行覆盖，其次配置文件。"""
    vault_path = getattr(args, "vault_path", None)
    export_root = getattr(args, "export_root", None)
    vault_name = getattr(args, "vault", None)
    if vault_path and export_root:
        return vault_name or os.path.basename(os.path.normpath(vault_path)), \
            kb_config.validate_vault_path(vault_path), kb_config._norm_path(export_root)
    config, _ = kb_config.load_config(getattr(args, "config", None))
    v = kb_config.resolve_vault(config, vault_name)
    vault_path = kb_config.validate_vault_path(v["path"])
    export_root = export_root or config.get("exportRoot")
    if not export_root:
        raise ExportError("配置缺少 exportRoot，请先用 kb_config.py set exportRoot <路径>")
    return v["name"], vault_path, kb_config._norm_path(export_root)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="html_export.py",
                                description="HTML 镜像导出（vault 外目录，增量同步）")
    p.add_argument("--json", action="store_true", help="以 JSON 输出结果")
    sub = p.add_subparsers(dest="command", required=True)

    sp = sub.add_parser("export", help="增量导出整个 vault（--full 全量重建），并同步移除已删除笔记的镜像")
    sp.add_argument("--config", help="显式指定配置文件路径")
    sp.add_argument("--vault", help="vault 名称（缺省用默认 vault）")
    sp.add_argument("--full", action="store_true", help="全量重建")
    sp.add_argument("--vault-path", help="覆盖 vault 路径（免配置模式，需同时给 --export-root）")
    sp.add_argument("--export-root", help="覆盖导出根目录")
    sp.set_defaults(func=cmd_export)

    sp = sub.add_parser("export-one", help="导出单篇笔记（写入/修改后的快速增量）")
    sp.add_argument("--config", help="显式指定配置文件路径")
    sp.add_argument("--vault", help="vault 名称（缺省用默认 vault）")
    sp.add_argument("--file", required=True, help="vault 相对路径或绝对路径")
    sp.add_argument("--vault-path", help="覆盖 vault 路径")
    sp.add_argument("--export-root", help="覆盖导出根目录")
    sp.set_defaults(func=cmd_export_one)

    return p


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = args.func(args)
    except (ExportError, kb_config.ConfigError) as e:
        if args.json:
            print(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False))
        else:
            print(f"错误：{e}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps({"ok": True, **result}, ensure_ascii=False))
    else:
        for k, v in result.items():
            print(f"{k}: {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
