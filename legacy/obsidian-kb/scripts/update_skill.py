#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""update_skill.py - obsidian-kb 发布辅助工具（Python 标准库，跨平台）

实现 §12 发布约定的工具化（仅在用户明确要求发布时由 agent 调用，绝不自动运行）：
  1. check   — 发布前检查：CHANGELOG/DESIGN 已同步版本、兼容性（配置可迁移、
               用户手册模板存在）、quick_validate 校验
  2. package — 打包 zip 到 dist/，命名 obsidian-kb-vX.Y.Z-<timestamp>.zip
               （仅含运行时文件，开发期文档 CHANGELOG/DESIGN/REQUIREMENTS/
               TEST-REPORT 不随包分发）
  3. commit  — git add -A + git commit（feat:/fix:/docs: vX.Y.Z - 描述）；永不 git init
  4. release — 顺序执行 check → package → commit
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
import zipfile

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, SCRIPT_DIR)

import kb_config  # noqa: E402

SKILL_NAME = "obsidian-kb"
# 打包排除项（相对 skill 根目录）：分发包仅含运行时文件，
# 开发期文档由 git 管理，不随包分发（v1.4.0 起）
EXCLUDE_DIRS = {".git", ".test-env", "dist", "__pycache__", ".workbuddy"}
EXCLUDE_FILES = {"REQUIREMENTS.md", "PROMPT.md", "TEST-REPORT.md",
                 "CHANGELOG.md", "DESIGN.md"}
EXCLUDE_SUFFIXES = {".pyc"}


class ReleaseError(Exception):
    pass


def find_validator() -> str | None:
    """定位 skill-creator 的 quick_validate.py。可用 --validator 覆盖。"""
    candidates = [
        os.path.join(os.path.dirname(SKILL_ROOT), "skill-creator", "scripts", "quick_validate.py"),
    ]
    appdata = os.environ.get("LOCALAPPDATA", "")
    # WorkBuddy 内置 skill-creator 常见位置（仅作候选，存在才使用）
    for root in filter(None, [os.environ.get("WORKBUDDY_HOME"), appdata]):
        candidates.append(os.path.join(
            root, "..", "Develop", "WorkBuddy", "resources", "app.asar.unpacked",
            "resources", "builtin-skills", "skill-creator", "scripts", "quick_validate.py"))
    for c in candidates:
        c = os.path.normpath(c)
        if os.path.isfile(c):
            return c
    return None


# ---------------------------------------------------------------------------
# check
# ---------------------------------------------------------------------------

def cmd_check(args) -> dict:
    problems, warnings, passed = [], [], []

    changelog = os.path.join(SKILL_ROOT, "CHANGELOG.md")
    if not os.path.isfile(changelog):
        problems.append("缺少 CHANGELOG.md")
    else:
        text = _read(changelog)
        if re.search(rf"^#+\s*\[?v?{re.escape(args.version)}\]?", text, re.M):
            passed.append(f"CHANGELOG.md 已包含 v{args.version} 条目")
        else:
            problems.append(f"CHANGELOG.md 缺少 v{args.version} 条目")
        if "兼容" in text:
            passed.append("CHANGELOG.md 含兼容性说明")

    design = os.path.join(SKILL_ROOT, "DESIGN.md")
    if not os.path.isfile(design):
        problems.append("缺少 DESIGN.md")
    elif args.version in _read(design):
        passed.append(f"DESIGN.md 已提及 v{args.version}")
    else:
        warnings.append(f"DESIGN.md 未提及 v{args.version}（如架构有变化请同步更新）")

    # 兼容性：配置可加载 / 迁移路径存在
    try:
        if kb_config.SCHEMA_VERSION > 1 and 0 not in kb_config.MIGRATIONS and \
                len(kb_config.MIGRATIONS) < kb_config.SCHEMA_VERSION - 1:
            problems.append("配置 schema 升级但缺少完整迁移路径（MIGRATIONS）")
        else:
            passed.append(f"配置 schema v{kb_config.SCHEMA_VERSION} 迁移路径检查通过")
    except Exception as e:  # noqa: BLE001
        problems.append(f"配置模块自检异常：{e}")

    # 用户手册模板存在（保护已生成手册的逻辑在初始化流程中，不覆盖）
    if os.path.isfile(os.path.join(SKILL_ROOT, "assets", "user-manual.md")):
        passed.append("assets/user-manual.md 存在")
    else:
        problems.append("缺少 assets/user-manual.md")

    # quick_validate
    validator = args.validator or find_validator()
    if not validator:
        warnings.append("未找到 quick_validate.py（可用 --validator 指定），跳过结构校验")
    else:
        r = subprocess.run(
            [sys.executable, validator, SKILL_ROOT],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        out = ((r.stdout or "") + (r.stderr or "")).strip()
        if r.returncode == 0:
            passed.append("quick_validate 通过")
        else:
            problems.append(f"quick_validate 未通过：{out[:500]}")

    return {"version": args.version, "ok": not problems,
            "passed": passed, "warnings": warnings, "problems": problems}


# ---------------------------------------------------------------------------
# package
# ---------------------------------------------------------------------------

def cmd_package(args) -> dict:
    dist = os.path.join(SKILL_ROOT, "dist")
    os.makedirs(dist, exist_ok=True)
    timestamp = time.strftime("%Y%m%d-%H%M")
    zip_name = f"{SKILL_NAME}-v{args.version}-{timestamp}.zip"
    zip_path = os.path.join(dist, zip_name)

    included = []
    for dirpath, dirnames, filenames in os.walk(SKILL_ROOT):
        rel_dir = os.path.relpath(dirpath, SKILL_ROOT)
        parts = set(rel_dir.split(os.sep))
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        if parts & EXCLUDE_DIRS:
            continue
        for fn in filenames:
            if fn in EXCLUDE_FILES or os.path.splitext(fn)[1] in EXCLUDE_SUFFIXES:
                continue
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, SKILL_ROOT)
            included.append(rel)

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for rel in sorted(included):
            zf.write(os.path.join(SKILL_ROOT, rel),
                     arcname=os.path.join(SKILL_NAME, rel))

    return {"zip": zip_path, "files": len(included)}


# ---------------------------------------------------------------------------
# commit
# ---------------------------------------------------------------------------

def _git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=SKILL_ROOT,
                          capture_output=True, text=True, encoding="utf-8", errors="replace")


def cmd_commit(args) -> dict:
    r = _git("rev-parse", "--is-inside-work-tree")
    if r.returncode != 0 or "true" not in (r.stdout or ""):
        raise ReleaseError(
            "skill 目录不是 Git 仓库。本工具永不执行 git init；"
            "如需版本管理请手动初始化仓库后再运行"
        )
    top = _git("rev-parse", "--show-toplevel").stdout.strip()
    if os.path.normpath(top) != os.path.normpath(SKILL_ROOT):
        raise ReleaseError(
            f"skill 目录位于上层仓库（{top}）内，而非独立仓库根。\n"
            f"为避免污染上层仓库历史，发布提交被拒绝。请将 skill 目录作为独立仓库（手动 git init）后再运行。"
        )
    msg = f"{args.type}: v{args.version} - {args.msg}"
    _git("add", "-A", "--", ".")
    r = _git("commit", "-m", msg)
    if r.returncode != 0:
        out = (r.stdout or "") + (r.stderr or "")
        if "nothing to commit" in out:
            return {"committed": False, "message": "没有需要提交的变更"}
        raise ReleaseError(f"git commit 失败：{out.strip()[:500]}")
    h = _git("rev-parse", "--short", "HEAD").stdout.strip()
    return {"committed": True, "message": msg, "commit": h}


# ---------------------------------------------------------------------------
# release
# ---------------------------------------------------------------------------

def cmd_release(args) -> dict:
    check = cmd_check(args)
    if not check["ok"]:
        raise ReleaseError("发布前检查未通过：\n- " + "\n- ".join(check["problems"]))
    pkg = cmd_package(args)
    result = {"check": check, "package": pkg}
    if not args.skip_commit:
        result["commit"] = cmd_commit(args)
    return result


def _read(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="update_skill.py",
                                description="obsidian-kb 发布辅助（仅显式调用，不自动发布）")
    p.add_argument("--json", action="store_true")
    sub = p.add_subparsers(dest="command", required=True)

    def common(sp):
        sp.add_argument("--version", required=True, help="目标版本号，如 1.0.0")
        sp.add_argument("--validator", help="quick_validate.py 路径（可选）")

    sp = sub.add_parser("check", help="发布前检查（CHANGELOG/DESIGN/兼容性/quick_validate）")
    common(sp)
    sp.set_defaults(func=cmd_check)

    sp = sub.add_parser("package", help="打包到 dist/")
    common(sp)
    sp.set_defaults(func=cmd_package)

    sp = sub.add_parser("commit", help="git 提交（永不 git init）")
    common(sp)
    sp.add_argument("--type", choices=["feat", "fix", "docs"], default="feat")
    sp.add_argument("--msg", required=True, help="变更描述")
    sp.set_defaults(func=cmd_commit)

    sp = sub.add_parser("release", help="check → package → commit 完整流程")
    common(sp)
    sp.add_argument("--type", choices=["feat", "fix", "docs"], default="feat")
    sp.add_argument("--msg", required=True)
    sp.add_argument("--skip-commit", action="store_true", help="只检查与打包，不提交")
    sp.set_defaults(func=cmd_release)

    return p


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = args.func(args)
    except ReleaseError as e:
        if args.json:
            print(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False))
        else:
            print(f"错误：{e}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps({"ok": True, **result}, ensure_ascii=False))
    else:
        _print_human(result)
    return 0 if result.get("ok", True) else 2


def _print_human(result: dict) -> None:
    if "passed" in result:
        for s in result["passed"]:
            print(f"[OK] {s}")
        for s in result.get("warnings", []):
            print(f"[WARN] {s}")
        for s in result.get("problems", []):
            print(f"[FAIL] {s}")
        print("检查：" + ("通过" if result["ok"] else "未通过"))
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    sys.exit(main())
