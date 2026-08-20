#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""vault_check.py — knowops 知识库结构校验（Python 标准库，跨平台）

职责：
  - check 模式：对指定笔记做**结构面**校验（frontmatter 可解析、必填属性齐全、
    type 在枚举内），输出每篇的 frontmatter 键值摘要供 agent 快速扫读；
    **语义面核验**（内容正确性、双向链接语义、任务双轨、日记同步、插件规则、
    HTML 导出执行等）仍由 agent 按 workflow.md「操作后流程」执行。
  - check-vault 模式：全库结构巡检（一级目录与配置匹配、frontmatter 扫描），
    适用于日常巡检、结构迁移前、升级后核对。

用法：
  python vault_check.py check <vault> <文件...> [--json]
      <文件...> 支持绝对路径或相对 vault 的路径
  python vault_check.py check-vault <vault> [--json]

必填属性规则与 references/properties.md 对齐（改动须两端同步）。

例外说明：本脚本直接读取 vault 源文件——属于 redlines.md 直接文件访问
例外清单第 2 条（格式校验：需对原始文件做 JSON/YAML 结构校验）。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# type 枚举（与 references/properties.md 的 type 行保持一致，双源由开发期
# tools/check.py 的 C6 检查兜底）
TYPE_ENUM = frozenset({
    "capture", "question", "knowledge", "excerpt", "principle", "standard",
    "checklist", "template", "workflow", "project", "daily", "event", "task",
    "review", "archive", "system",
})

# 各 type 的必填属性（excerpt 长篇另加 source，见 EXCERPT_LONG_EXTRA）
REQUIRED = {
    "capture": ["type", "capture_kind", "created", "tags"],
    "knowledge": ["type", "knowledge_type", "domain", "created", "source"],
    "excerpt": ["type", "excerpt_kind", "category", "created", "tags"],
}
EXCERPT_LONG_EXTRA = ["source"]

# 默认目录约定（config 缺失时的兜底值，与 properties.md 默认值一致）
DEFAULT_PREFS = {
    "inboxDir": "00 收件箱", "lifeDir": "01 生活系统", "knowledgeDir": "02 知识系统",
    "assetsDir": "03 资产系统", "standardsDir": "04 规范系统",
    "projectsDir": "05 项目系统", "excerptDir": "06 摘录系统",
    "dashboardDir": "07 看板", "archiveDir": "08 归档", "systemDir": "09 系统管理",
    "dashboardFile": "看板.md",
}
DIR_KEYS = ["inboxDir", "lifeDir", "knowledgeDir", "assetsDir", "standardsDir",
            "projectsDir", "excerptDir", "dashboardDir", "archiveDir", "systemDir"]
FIXED_TAIL = ["看板", "归档", "系统管理"]


def read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8-sig")


def clean_val(v: str):
    """行内值清洗：行内数组 → list，其余去引号转字符串。"""
    if v.startswith("[") and v.endswith("]"):
        inner = v[1:-1].strip()
        if not inner:
            return []
        return [x.strip().strip("'\"") for x in inner.split(",") if x.strip()]
    return v.strip("'\"")


def parse_frontmatter(text: str) -> tuple[dict | None, str | None]:
    """轻量 YAML frontmatter 解析（覆盖 knowops 用到的子集：
    标量、行内数组、块式列表、一层嵌套如 metadata.version）。
    返回 (dict|None, 错误信息|None)。"""
    if not text.startswith("---"):
        return None, None
    lines = text.splitlines()
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return None, "frontmatter 未闭合（缺少第二个 ---）"
    data: dict = {}
    parent: str | None = None
    for idx, ln in enumerate(lines[1:end], start=2):
        if not ln.strip() or ln.lstrip().startswith("#"):
            continue
        # 块式列表项：挂在最近的父键下（如 tags:\n  - a\n  - b）
        mi = re.match(r"^\s+-\s+(.*)$", ln)
        if mi and parent is not None:
            if not isinstance(data.get(parent), list):
                data[parent] = []
            data[parent].append(clean_val(mi.group(1)))
            continue
        m = re.match(r"^(\s*)([A-Za-z_][\w-]*):\s*(.*)$", ln)
        if not m:
            return None, f"第 {idx} 行无法解析：{ln.strip()[:40]}"
        indent, key, val = len(m.group(1)), m.group(2), m.group(3).strip()
        if indent == 0:
            if val == "":
                parent = key
                data[key] = {}
            else:
                parent = None
                data[key] = clean_val(val)
        elif parent:
            if isinstance(data.get(parent), dict):
                data[parent][key] = clean_val(val)
            else:
                return None, f"第 {idx} 行结构冲突：{parent} 混用列表与映射"
    return data, None


def fmt_val(v) -> str:
    s = json.dumps(v, ensure_ascii=False) if isinstance(v, list) else str(v)
    return s if len(s) <= 60 else s[:57] + "..."


def is_empty(v) -> bool:
    """属性值为空：None / 空串 / 空列表 / 空字典。"""
    return v is None or v == "" or v == [] or v == {}


def required_problems(fm: dict, t: str | None) -> list[str]:
    """必填属性检查（check 与 check-vault 共用）：缺失与空值都算问题。"""
    if t not in REQUIRED:
        return []
    keys = list(REQUIRED[t])
    if t == "excerpt" and str(fm.get("excerpt_kind")) == "长篇":
        keys += EXCERPT_LONG_EXTRA
    missing = [k for k in keys if k not in fm]
    empty = [k for k in keys if k in fm and is_empty(fm[k])]
    out = []
    if missing:
        out.append(f"缺必填属性：{'、'.join(missing)}")
    if empty:
        out.append(f"必填属性值为空：{'、'.join(empty)}")
    return out


def load_prefs(vault: Path) -> dict:
    cfg_path = vault / ".config" / "knowops.config.json"
    prefs = dict(DEFAULT_PREFS)
    if cfg_path.is_file():
        try:
            cfg = json.loads(read_text(cfg_path))
            prefs.update(cfg.get("preferences", {}))
        except (OSError, ValueError):  # ValueError 含 JSON/解码错误
            pass  # 配置异常时用默认值兜底（check-vault 会单独报告配置问题）
    return prefs


def check_note(path: Path, vault: Path) -> dict:
    """校验单篇笔记，返回结果对象：{path, ok, problems[], summary}。"""
    result = {"path": path.relative_to(vault).as_posix()
              if path.is_absolute() and vault in path.parents else str(path),
              "ok": True, "problems": [], "summary": ""}
    try:
        text = read_text(path)
    except (OSError, ValueError) as e:  # ValueError 含 UnicodeDecodeError
        result["ok"] = False
        result["problems"].append(f"读取失败：{e}")
        return result
    fm, err = parse_frontmatter(text)
    if err:
        result["ok"] = False
        result["problems"].append(err)
        return result
    if fm is None:
        result["ok"] = False
        result["problems"].append("无 frontmatter")
        return result
    t = fm.get("type")
    t = str(t) if t is not None else None
    if t is None:
        result["problems"].append("缺 type")
    elif t not in TYPE_ENUM:
        result["problems"].append(f"type={t} 不在枚举内")
    # 必填属性（仅 REQUIRED 覆盖的类型；缺失与空值都算问题）
    result["problems"].extend(required_problems(fm, t))
    if result["problems"]:
        result["ok"] = False
    # 键值摘要（type 置前，其余按解析顺序）
    items = []
    if t:
        items.append(f"type={fmt_val(t)}")
    for k, v in fm.items():
        if k == "type":
            continue
        items.append(f"{k}={fmt_val(v)}")
    result["summary"] = " | ".join(items)
    return result


def print_result(r: dict) -> None:
    if r["ok"]:
        print(f"[OK] {r['path']}")
        if r["summary"]:
            print(f"     {r['summary']}")
    else:
        print(f"[FAIL] {r['path']}")
        for p in r["problems"]:
            print(f"     {p}")
        if r["summary"]:
            print(f"     （已解析字段：{r['summary']}）")


def cmd_check(vault: Path, files: list[str], as_json: bool) -> int:
    results = []
    for f in files:
        p = Path(f)
        if not p.is_absolute():
            p = vault / f
        results.append(check_note(p, vault))
    ok = all(r["ok"] for r in results)
    if as_json:
        print(json.dumps({"mode": "check", "ok": ok, "results": results},
                         ensure_ascii=False, indent=2))
    else:
        for r in results:
            print_result(r)
        n_fail = sum(1 for r in results if not r["ok"])
        print(f"-- 汇总：{len(results)} 篇，{n_fail} 篇 FAIL --")
    return 0 if ok else 1


def cmd_check_vault(vault: Path, as_json: bool) -> int:
    problems = []
    prefs = load_prefs(vault)

    # 1) 一级目录与 preferences 匹配（懒加载允许目录缺失）
    expected: dict[int, str] = {}
    for k in DIR_KEYS:
        m = re.match(r"^(\d{2})\s+(.+)$", str(prefs.get(k, "")))
        if m:
            expected[int(m.group(1))] = m.group(2)
    actual: dict[int, str] = {}
    if vault.is_dir():
        for d in vault.iterdir():
            if d.name.startswith(".") or not d.is_dir():
                continue
            m = re.match(r"^(\d{2})\s+(.+)$", d.name)
            if m:
                actual[int(m.group(1))] = m.group(2)
    for num, name in sorted(actual.items()):
        if num not in expected:
            problems.append(f"目录「{num:02d} {name}」不在配置 preferences 中")
        elif expected[num] != name:
            problems.append(f"目录「{num:02d} {name}」与配置值「{expected[num]}」不一致")
    # 后三位固定
    tail_nums = [int(str(prefs[k])[:2]) for k in ("dashboardDir", "archiveDir", "systemDir")
                 if re.match(r"^\d{2}\s", str(prefs.get(k, "")))]
    if expected and sorted(tail_nums) and sorted(tail_nums) != [max(expected) - 2,
                                                                max(expected) - 1,
                                                                max(expected)]:
        problems.append(f"后三位编号异常：{sorted(tail_nums)}（模块最大编号 {max(expected)}）")

    # 2) 全库 frontmatter 扫描（跳过隐藏目录）
    system_dir = str(prefs.get("systemDir"))
    dashboard_file = str(prefs.get("dashboardFile"))
    projects_dir = str(prefs.get("projectsDir"))
    project_fixed = {"目标.md", "决策记录.md", "研究记录.md", "问题.md", "复盘.md"}
    no_fm, bad = [], []
    count = 0
    if vault.is_dir():
        for p in vault.rglob("*.md"):
            rel = p.relative_to(vault)
            if any(part.startswith(".") for part in rel.parts):
                continue
            count += 1
            try:
                fm, err = parse_frontmatter(read_text(p))
            except (OSError, ValueError) as e:  # ValueError 含 UnicodeDecodeError
                bad.append(f"{rel.as_posix()}：读取失败：{e}")
                continue
            if err:
                bad.append(f"{rel.as_posix()}：{err}")
            elif fm is None:
                # 豁免：人工清单/看板容器/系统管理用户文档/项目固定结构文档
                if (p.name in ("TODO.md", dashboard_file)
                        or rel.as_posix().startswith(system_dir + "/")
                        or (rel.as_posix().startswith(projects_dir + "/")
                            and p.name in project_fixed)):
                    continue
                no_fm.append(rel.as_posix())
            elif fm.get("type") is None:
                no_fm.append(f"{rel.as_posix()}（有 frontmatter 但无 type）")
            elif str(fm.get("type")) not in TYPE_ENUM:
                bad.append(f"{rel.as_posix()}：type={fm.get('type')} 不在枚举内")
            else:
                # 必填属性（与 check 模式同一套规则）
                for prob in required_problems(fm, str(fm.get("type"))):
                    bad.append(f"{rel.as_posix()}：{prob}")

    ok = not problems and not bad
    if as_json:
        print(json.dumps({
            "mode": "check-vault", "ok": ok,
            "problems": problems + [f"type/解析问题：{b}" for b in bad],
            "no_frontmatter": no_fm,
            "summary": {"notes": count, "modules_present": len(actual)},
        }, ensure_ascii=False, indent=2))
    else:
        print(f"== vault_check 全库巡检：{vault} ==")
        print(f"模块目录：{len(actual)} 个（配置 {len(expected)} 个）")
        for it in problems:
            print(f"[FAIL] {it}")
        for it in bad:
            print(f"[FAIL] {it}")
        for it in no_fm:
            print(f"[WARN] 无 frontmatter：{it}")
        print(f"-- 汇总：{count} 篇笔记；error {len(problems) + len(bad)}，"
              f"警告 {len(no_fm)} --")
    return 0 if ok else 1


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="knowops 知识库结构校验（结构面）")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p1 = sub.add_parser("check", help="校验指定笔记（结构面 + frontmatter 摘要）")
    p1.add_argument("vault", help="vault 根目录路径")
    p1.add_argument("files", nargs="+", help="笔记路径（绝对或相对 vault）")
    p1.add_argument("--json", action="store_true", help="输出机器可读 JSON")
    p2 = sub.add_parser("check-vault", help="全库结构巡检")
    p2.add_argument("vault", help="vault 根目录路径")
    p2.add_argument("--json", action="store_true", help="输出机器可读 JSON")
    args = parser.parse_args()

    vault = Path(args.vault)
    if not vault.is_dir():
        print(f"[FATAL] vault 目录不存在：{vault}", file=sys.stderr)
        return 2
    if args.cmd == "check":
        return cmd_check(vault, args.files, args.json)
    return cmd_check_vault(vault, args.json)


if __name__ == "__main__":
    sys.exit(main())
