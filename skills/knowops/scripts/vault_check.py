#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""vault_check.py — knowops 知识库结构校验（Python 标准库，跨平台）

职责：
  - check 模式：对指定笔记做**结构面**校验（frontmatter 可解析、必填属性齐全、
    type 合法），输出每篇的 frontmatter 键值摘要供 agent 快速扫读；
    **语义面核验**（内容正确性、原话完整、双向链接语义、插件规则、HTML 导出
    执行等）仍由 agent 按 workflow.md「操作后流程」执行。
    **收件箱豁免**：收件箱（type=capture 的基础模块）下的文件不判必填/枚举/
    命名（零门槛捕获区），输出 [EXEMPT]；**非 md 文件**（含 `.canvas`）同样
    输出 [EXEMPT]（summary: skipped: non-md），不判定。
  - check-vault 模式：全库结构巡检（一级目录与配置 modules 匹配、frontmatter
    扫描），适用于日常巡检、升级后核对。收件箱路径整体跳过，模板目录跳过
    （占位符），非 md 文件不参与扫描。
    **fail-closed**：check 模式传入目录或不存在的路径判 FAIL（不静默豁免）。

type 校验口径（v3）：
  - 基础枚举（capture/knowledge/daily/archive/system）硬校验；
  - 已登记模块按 config `preferences.modules[].type` 校验（规则正文在用户
    手册，脚本只查 type 值本身）；
  - 未登记目录 / 未登记 type 只出 **warning**，不影响退出码（用户自建模块
    在登记前不应被判死）。

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

# type 基础枚举（与 references/properties.md 的 type 行保持一致，两处定义
# 须同步、改动两端同步）。扩展模块的 type 随登记追加（config
# preferences.modules），不在本枚举内。
TYPE_ENUM = frozenset({
    "capture", "knowledge", "daily", "archive", "system",
})

# 各 type 的必填属性（只约束 agent 写入；用户手写文件在收件箱内豁免）
# 扩展模块的必填属性由用户手册「模块规则」定义，脚本对已登记模块只做
# type 存在性校验，不内嵌其必填表。
REQUIRED = {
    "capture": ["type", "created", "tags"],
    "knowledge": ["type", "created", "updated", "tags"],
}

# 基础模块默认登记（config 缺失时的兜底值，与 properties.md 默认值一致）。
# 扩展模块（如摘录）由初始化/登记流程追加，不在默认值内。
DEFAULT_MODULES = [
    {"dir": "00 收件箱", "name": "收件箱", "type": "capture", "base": True},
    {"dir": "01 知识", "name": "知识", "type": "knowledge", "base": True},
    {"dir": "03 系统", "name": "系统", "type": "system", "base": True},
    {"dir": "04 归档", "name": "归档", "type": "archive", "base": True},
]

# 其余默认偏好（config 缺失时的兜底值）
DEFAULT_PREFS = {
    "dailyFolder": "03 系统/日记",
    "dailyFormat": "YYYY/YYYY-MM-DD",
    "templatesDir": "03 系统/模板",
}
DASHBOARD_FILE = "看板.md"  # 根目录看板容器，位置固定，无 frontmatter 豁免


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
    标量、行内数组、块式列表、一层嵌套如 metadata.version；键名支持
    Unicode（中文属性键，Obsidian 属性面板允许）。键名仅 ASCII 时行为不变。
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
        m = re.match(r"^(\s*)(\w[\w-]*):\s*(.*)$", ln)
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
    missing = [k for k in keys if k not in fm]
    empty = [k for k in keys if k in fm and is_empty(fm[k])]
    out = []
    if missing:
        out.append(f"缺必填属性：{'、'.join(missing)}")
    if empty:
        out.append(f"必填属性值为空：{'、'.join(empty)}")
    return out


def normalize_modules(raw) -> list[dict]:
    """清洗 config preferences.modules：只保留 dir/type 至少可用的条目。"""
    mods: list[dict] = []
    if isinstance(raw, list):
        for it in raw:
            if not isinstance(it, dict):
                continue
            d = str(it.get("dir", "")).strip()
            if not d:
                continue
            mods.append({
                "dir": d,
                "name": str(it.get("name", "")).strip(),
                "type": str(it.get("type", "")).strip(),
                "base": bool(it.get("base", False)),
            })
    return mods


def load_prefs(vault: Path) -> dict:
    """读取 vault 配置：基础偏好 + modules 模块清单。config 缺失/异常/清单
    无效时用默认值兜底，并在 prefs["_config_ok"] 记 False（check-vault 据此
    单独报告配置问题）。"""
    cfg_path = vault / ".config" / "knowops.config.json"
    prefs = dict(DEFAULT_PREFS)
    modules = list(DEFAULT_MODULES)
    config_ok = False
    if cfg_path.is_file():
        try:
            cfg = json.loads(read_text(cfg_path))
            prefs_cfg = cfg.get("preferences")
            if not isinstance(prefs_cfg, dict):
                prefs_cfg = {}
            prefs.update(prefs_cfg)
            modules = normalize_modules(prefs_cfg.get("modules"))
            if not modules:
                modules = list(DEFAULT_MODULES)
            config_ok = True
        except (OSError, ValueError):  # ValueError 含 JSON/解码错误
            pass  # 配置异常时用默认值兜底（check-vault 会单独报告配置问题）
    prefs["modules"] = modules
    prefs["_config_ok"] = config_ok
    return prefs


def module_of(rel: str, prefs: dict) -> dict | None:
    """按相对路径（posix）匹配所属模块：取 dir 前缀最长者；无匹配返回 None
    （未登记区域）。"""
    best: dict | None = None
    best_len = -1
    for m in prefs.get("modules", []):
        d = str(m.get("dir", "")).rstrip("/")
        if d and (rel == d or rel.startswith(d + "/")) and len(d) > best_len:
            best, best_len = m, len(d)
    return best


def inbox_dir(prefs: dict) -> str:
    """收件箱目录 = type 为 capture 的登记模块；无则退回默认。"""
    for m in prefs.get("modules", []):
        if m.get("type") == "capture":
            return str(m["dir"])
    return "00 收件箱"


def system_dir(prefs: dict) -> str:
    """系统模块目录 = type 为 system 的登记模块；无则退回默认。"""
    for m in prefs.get("modules", []):
        if m.get("type") == "system":
            return str(m["dir"])
    return "03 系统"


def rel_posix(path: Path, vault: Path) -> str:
    # resolve() 归一短路径/junction/符号链接，避免绝对路径拼写失配导致
    # 豁免与模块归属静默失效
    try:
        p = path.resolve()
    except OSError:
        p = path
    if p.is_absolute() and vault in p.parents:
        return p.relative_to(vault).as_posix()
    return str(path)


def check_note(path: Path, vault: Path, prefs: dict) -> dict:
    """校验单篇笔记，返回结果对象：
    {path, ok, exempt, problems[], warnings[], summary}。"""
    rel = rel_posix(path, vault)
    result = {"path": rel, "ok": True, "exempt": False, "problems": [],
              "warnings": [], "summary": ""}
    if not path.is_file():
        # 目录 / 不存在的路径：fail-closed（与「非 md 文件跳过」区分开）
        result["ok"] = False
        result["problems"].append("路径不存在或不是文件")
        return result
    if path.is_absolute():
        # vault 之外的路径 fail-closed（resolve 后比较，归一短路径/junction）
        try:
            rp = path.resolve()
        except OSError:
            rp = path
        if vault not in rp.parents:
            result["ok"] = False
            result["problems"].append("路径不在 vault 内")
            return result
    if path.suffix.lower() != ".md":
        # 非 md（含 .canvas）：用户自由空间/非笔记内容，不判定
        result["exempt"] = True
        result["summary"] = "skipped: non-md"
        return result
    if rel == inbox_dir(prefs) or rel.startswith(inbox_dir(prefs) + "/"):
        # 收件箱豁免：零门槛捕获区，结构必填项不判
        result["exempt"] = True
        try:
            fm, _err = parse_frontmatter(read_text(path))
        except (OSError, ValueError):
            fm = None
        items = []
        if fm:
            t = fm.get("type")
            if t is not None:
                items.append(f"type={fmt_val(str(t))}")
            for k, v in fm.items():
                if k == "type":
                    continue
                items.append(f"{k}={fmt_val(v)}")
        result["summary"] = ("exempt: inbox"
                             + (f" | {' | '.join(items)}" if items else ""))
        return result
    if rel == DASHBOARD_FILE or rel.startswith(
            str(prefs.get("templatesDir", "")) + "/"):
        # 看板容器（位置固定）与模板（占位符）：与 check-vault 同口径豁免
        result["exempt"] = True
        result["summary"] = "exempt: dashboard/template"
        return result
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

    mod = module_of(rel, prefs)
    registered_types = {str(m.get("type")) for m in prefs.get("modules", [])
                        if m.get("type")}
    t = fm.get("type")
    t = str(t).strip() if t is not None else None
    if t == "":
        t = None  # 空字符串按缺 type 处理
    if mod is None:
        # 未登记目录：整体只警告，不判失败（登记后转为正常校验）
        result["warnings"].append("所在目录未登记（按 workflow「模块发现与登记」处理）")
    if t is None:
        if mod is not None:
            result["problems"].append("缺 type")
        else:
            result["warnings"].append("缺 type")
    elif t not in TYPE_ENUM and t not in registered_types:
        # 未登记 type 只警告（用户确认登记后转为正常校验）
        result["warnings"].append(
            f"type={t} 不在基础枚举与已登记模块类型内（未登记）")
    elif mod is not None:
        # 必填属性（仅基础类型 REQUIRED 覆盖；未登记目录不判，只警告）
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
    if r["exempt"]:
        print(f"[EXEMPT] {r['path']}")
        if r["summary"]:
            print(f"     {r['summary']}")
    elif r.get("warnings") and r["ok"]:
        print(f"[WARN] {r['path']}")
        for w in r["warnings"]:
            print(f"     {w}")
        if r["summary"]:
            print(f"     （已解析字段：{r['summary']}）")
    elif r["ok"]:
        print(f"[OK] {r['path']}")
        if r["summary"]:
            print(f"     {r['summary']}")
    else:
        print(f"[FAIL] {r['path']}")
        for p in r["problems"]:
            print(f"     {p}")
        for w in r.get("warnings", []):
            print(f"     [WARN] {w}")
        if r["summary"]:
            print(f"     （已解析字段：{r['summary']}）")


def cmd_check(vault: Path, files: list[str], as_json: bool) -> int:
    prefs = load_prefs(vault)
    results = []
    for f in files:
        p = Path(f)
        if not p.is_absolute():
            p = vault / f
        # 无扩展名的路径按笔记处理：存在同名 .md 时补上（与导出脚本行为一致）
        if p.suffix == "" and not p.exists() and p.with_suffix(".md").exists():
            p = p.with_suffix(".md")
        results.append(check_note(p, vault, prefs))
    ok = all(r["ok"] for r in results)
    if as_json:
        print(json.dumps({"mode": "check", "ok": ok, "results": results},
                         ensure_ascii=False, indent=2))
    else:
        for r in results:
            print_result(r)
        n_fail = sum(1 for r in results if not r["ok"])
        n_exempt = sum(1 for r in results if r["exempt"])
        n_warn = sum(1 for r in results if r["ok"] and r.get("warnings"))
        print(f"-- 汇总：{len(results)} 篇，{n_fail} 篇 FAIL，{n_warn} 篇警告，"
              f"{n_exempt} 篇豁免 --")
    return 0 if ok else 1


def cmd_check_vault(vault: Path, as_json: bool) -> int:
    problems = []
    warnings: list[str] = []
    prefs = load_prefs(vault)
    modules = prefs.get("modules", [])
    if not prefs.get("_config_ok", False):
        warnings.append("配置缺失或异常（.config/knowops.config.json），"
                        "已回退默认模块清单")
    # 登记清单自检：重复目录/重复 type/缺 type 只警告（登记流程问题，
    # 由 agent 现场对齐），不影响退出码
    dirs = [str(m.get("dir")) for m in modules]
    dup_dirs = sorted({d for d in dirs if dirs.count(d) > 1})
    if dup_dirs:
        warnings.append(f"modules 重复登记目录：{dup_dirs}")
    empty_type = [str(m.get("dir")) for m in modules if not m.get("type")]
    if empty_type:
        warnings.append(f"modules 缺 type：{empty_type}")
    types = [str(m.get("type")) for m in modules if m.get("type")]
    dup_types = sorted({t for t in types if types.count(t) > 1})
    if dup_types:
        warnings.append(f"modules 重复 type：{dup_types}")

    # 1) 一级目录与 preferences.modules 匹配（懒加载允许目录缺失）
    expected: dict[int, str] = {}
    for m in modules:
        d = str(m.get("dir", ""))
        mm = re.match(r"^(\d{2})\s+(.+)$", d)
        if mm:
            expected[int(mm.group(1))] = mm.group(2)
    actual: dict[int, str] = {}
    if vault.is_dir():
        for d in vault.iterdir():
            if d.name.startswith(".") or not d.is_dir():
                continue
            mm = re.match(r"^(\d{2})\s+(.+)$", d.name)
            if mm:
                actual[int(mm.group(1))] = mm.group(2)
    for num, name in sorted(actual.items()):
        if num not in expected:
            # 用户自建的未登记目录：只警告（登记流程处理），不判失败
            warnings.append(f"目录「{num:02d} {name}」未登记（不在 config "
                            "preferences.modules 中，按 workflow「模块发现与"
                            "登记」处理）")
        elif expected[num] != name:
            problems.append(f"目录「{num:02d} {name}」与配置值「{expected[num]}」不一致")
    # 末两位固定：系统（倒数第二）、归档（殿后）——约束登记清单本身。
    # 运行期对用户 vault 宽容：异常只警告（用户坚持自己的编号时以用户为准，
    # agent 登记时应给出保持末两位的方案；开发期 check.py P2 对测试库仍为 error）。
    if expected:
        sys_dir = system_dir(prefs)
        arc = next((str(m["dir"]) for m in modules if m.get("type") == "archive"),
                   "")
        sys_m = re.match(r"^(\d{2})\s", sys_dir)
        arc_m = re.match(r"^(\d{2})\s", arc)
        if sys_m and arc_m:
            tail = [int(sys_m.group(1)), int(arc_m.group(1))]
            if tail != [max(expected) - 1, max(expected)]:
                warnings.append(
                    f"末两位编号与规范不一致：系统/归档 = {tail}"
                    f"（规范期望 [{max(expected) - 1}, {max(expected)}]，"
                    "登记时应建议保持末两位的编号方案）")

    # 2) 全库 frontmatter 扫描（跳过隐藏目录；收件箱整体豁免；仅扫描 md）
    templates_dir = str(prefs.get("templatesDir", ""))
    sys_dir = system_dir(prefs)
    bad, warn_notes = [], []
    count = 0
    if vault.is_dir():
        for p in vault.rglob("*.md"):
            rel = p.relative_to(vault)
            if any(part.startswith(".") for part in rel.parts):
                continue
            rel_pos = rel.as_posix()
            if rel_pos == inbox_dir(prefs) or rel_pos.startswith(inbox_dir(prefs) + "/"):
                continue  # 收件箱校验豁免区
            if templates_dir and rel_pos.startswith(templates_dir + "/"):
                continue  # 模板是占位符不是内容，不校验
            count += 1
            mod = module_of(rel_pos, prefs)
            try:
                fm, err = parse_frontmatter(read_text(p))
            except (OSError, ValueError) as e:  # ValueError 含 UnicodeDecodeError
                bad.append(f"{rel_pos}：读取失败：{e}")
                continue
            if err:
                bad.append(f"{rel_pos}：{err}")
                continue
            if fm is None:
                # 豁免：根目录看板容器 / 系统模块内的用户文档、模板、日记
                if ((rel.parent == Path(".") and p.name == DASHBOARD_FILE)
                        or rel_pos.startswith(sys_dir + "/")):
                    continue
                if mod is None:
                    warn_notes.append(f"{rel_pos}：未登记目录且无 frontmatter")
                else:
                    # 已登记目录内的内容笔记无 frontmatter：硬失败
                    # （与 check 模式「无 frontmatter」FAIL 同口径）
                    bad.append(f"{rel_pos}：无 frontmatter")
                continue
            t = fm.get("type")
            if isinstance(t, str):
                t = t.strip()
            if not t:
                if mod is None:
                    warn_notes.append(f"{rel_pos}（有 frontmatter 但无 type，"
                                      "所在目录未登记）")
                else:
                    # 已登记目录内缺 type：硬失败（与 check 模式同口径）
                    bad.append(f"{rel_pos}：缺 type")
                continue
            registered_types = {str(m.get("type")) for m in modules if m.get("type")}
            if str(t) not in TYPE_ENUM and str(t) not in registered_types:
                # 未登记 type 只警告
                warn_notes.append(f"{rel_pos}：type={t} 未登记（不在基础枚举与"
                                  "已登记模块类型内）")
            elif mod is None:
                warn_notes.append(f"{rel_pos}：所在目录未登记")
            else:
                # 必填属性（与 check 模式同一套规则）
                for prob in required_problems(fm, str(t)):
                    bad.append(f"{rel_pos}：{prob}")

    ok = not problems and not bad
    all_warnings = warnings + warn_notes
    if as_json:
        print(json.dumps({
            "mode": "check-vault", "ok": ok,
            "problems": problems + [f"type/解析问题：{b}" for b in bad],
            "warnings": all_warnings,
            "summary": {"notes_scanned": count,
                        "modules_registered": len(modules),
                        "dirs_present": len(actual)},
        }, ensure_ascii=False, indent=2))
    else:
        print(f"== vault_check 全库巡检：{vault} ==")
        print(f"登记模块：{len(modules)} 个，在场目录：{len(actual)} 个")
        for it in problems:
            print(f"[FAIL] {it}")
        for it in bad:
            print(f"[FAIL] {it}")
        for it in all_warnings:
            print(f"[WARN] {it}")
        print(f"-- 汇总：扫描 {count} 篇笔记（收件箱豁免、非 md 跳过）；"
              f"error {len(problems) + len(bad)}，警告 {len(all_warnings)} --")
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

    vault = Path(args.vault).resolve()
    if not vault.is_dir():
        msg = f"vault 目录不存在：{args.vault}"
        if getattr(args, "json", False):
            print(json.dumps({"ok": False, "error": msg}, ensure_ascii=False))
        else:
            print(f"[FATAL] {msg}", file=sys.stderr)
        return 2
    if args.cmd == "check":
        return cmd_check(vault, args.files, args.json)
    return cmd_check_vault(vault, args.json)


if __name__ == "__main__":
    sys.exit(main())
