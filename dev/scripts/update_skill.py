#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""update_skill.py - knowledge-workflow / knowledge-manager-obsidian 双 skill 发布辅助
工具（标准库，跨平台）。开发期工具，存放于 dev/scripts/。

单仓库双 skill（skills/ 下两个目录）一起发布、一起升级（统一版本号）。
 1. check   — 发布前检查：CHANGELOG 已同步版本、两个 skill 的 SKILL.md 存在、
               quick_validate 逐个校验
 2. package — 为每个 skill 打包 zip 到 dist/，命名 <skill>-v<version>-<timestamp>.zip
               （仅含各自运行时文件；legacy/ 与 dev/ 开发期资产不进包）
 3. commit  — git add -A + git commit（feat:/fix:/docs: v<version> - 描述）；永不 git init
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

# dev/scripts/ → dev/ → 仓库根
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))

# 两个 skill：目录相对仓库根，zip 内 arcname 根用 skill 名
SKILLS = [
    {"name": "knowledge-workflow", "dir": "skills/knowledge-workflow"},
    {"name": "knowledge-manager-obsidian", "dir": "skills/knowledge-manager-obsidian"},
]
LEGACY_DIR = "legacy"  # 旧版存档，只进 git 不进包

# 打包排除项（相对各 skill 目录）
EXCLUDE_DIRS = {".git", "__pycache__"}
EXCLUDE_FILES = set()
EXCLUDE_SUFFIXES = {".pyc"}


class ReleaseError(Exception):
    pass


def find_validator() -> str | None:
    """定位 skill-creator 的 quick_validate.py。可用 --validator 覆盖。

    探测顺序：WORKBUDDY_HOME 环境变量 → 兄弟目录 skill-creator
    （skill-creator 与当前仓库同级的开发目录）→ 本机常见安装位置
    （D:\\AppGallery\\Develop\\WorkBuddy 内置 skill）。找不到返回 None（check 仅警告）。
    """
    candidates = []
    wb_home = os.environ.get("WORKBUDDY_HOME", "")
    if wb_home:
        candidates.append(os.path.join(
            wb_home, "resources", "app.asar.unpacked", "resources",
            "builtin-skills", "skill-creator", "scripts", "quick_validate.py"))
    candidates.append(os.path.join(
        os.path.dirname(SKILL_ROOT), "skill-creator", "scripts", "quick_validate.py"))
    candidates.append(r"D:\AppGallery\Develop\WorkBuddy\resources\app.asar.unpacked"
                      r"\resources\builtin-skills\skill-creator\scripts\quick_validate.py")
    for c in candidates:
        c = os.path.normpath(c)
        if os.path.isfile(c):
            return c
    return None


def skill_path(skill: dict) -> str:
    return os.path.join(SKILL_ROOT, skill["dir"])


# ---------------------------------------------------------------------------
# check
# ---------------------------------------------------------------------------

def cmd_check(args) -> dict:
    problems, warnings, passed = [], [], []

    # CHANGELOG 版本条目（dev/ 下，两个 skill 共用）
    changelog = os.path.join(SKILL_ROOT, "dev", "CHANGELOG.md")
    if not os.path.isfile(changelog):
        problems.append("缺少 CHANGELOG.md")
    else:
        text = _read(changelog)
        if re.search(rf"^#+\s*\[?v?{re.escape(args.version)}\]?", text, re.M):
            passed.append(f"CHANGELOG.md 已包含 v{args.version} 条目")
        else:
            problems.append(f"CHANGELOG.md 缺少 v{args.version} 条目")

    # 每个 skill：SKILL.md 存在 + quick_validate
    for skill in SKILLS:
        sp = skill_path(skill)
        if not os.path.isfile(os.path.join(sp, "SKILL.md")):
            problems.append(f"{skill['name']} 缺少 SKILL.md")
            continue
        passed.append(f"{skill['name']}/SKILL.md 存在")
        validator = args.validator or find_validator()
        if not validator:
            warnings.append("未找到 quick_validate.py（可用 --validator 指定），跳过结构校验")
            break
        r = subprocess.run(
            [sys.executable, validator, sp],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        out = ((r.stdout or "") + (r.stderr or "")).strip()
        if r.returncode == 0:
            passed.append(f"{skill['name']} quick_validate 通过")
        else:
            problems.append(f"{skill['name']} quick_validate 未通过：{out[:500]}")

    return {"version": args.version, "ok": not problems,
            "passed": passed, "warnings": warnings, "problems": problems}


# ---------------------------------------------------------------------------
# package
# ---------------------------------------------------------------------------

def _package_one(skill: dict, version: str, dist: str) -> dict:
    root = skill_path(skill)
    timestamp = time.strftime("%Y%m%d-%H%M")
    zip_name = f"{skill['name']}-v{version}-{timestamp}.zip"
    zip_path = os.path.join(dist, zip_name)

    included = []
    for dirpath, dirnames, filenames in os.walk(root):
        rel_dir = os.path.relpath(dirpath, root)
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        for fn in filenames:
            if fn in EXCLUDE_FILES or os.path.splitext(fn)[1] in EXCLUDE_SUFFIXES:
                continue
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, root)
            included.append(rel)

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for rel in sorted(included):
            zf.write(os.path.join(root, rel),
                     arcname=os.path.join(skill["name"], rel))
    return {"zip": zip_path, "files": len(included)}


def cmd_package(args) -> dict:
    dist = os.path.join(SKILL_ROOT, "dist")
    os.makedirs(dist, exist_ok=True)
    packages = [_package_one(skill, args.version, dist) for skill in SKILLS]
    return {"packages": packages, "total": len(packages)}


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
            "仓库根不是 Git 仓库。本工具永不执行 git init；"
            "如需版本管理请手动初始化仓库后再运行"
        )
    top = _git("rev-parse", "--show-toplevel").stdout.strip()
    if os.path.normpath(top) != os.path.normpath(SKILL_ROOT):
        raise ReleaseError(
            f"仓库根位于上层仓库（{top}）内，而非独立仓库根。\n"
            f"为避免污染上层仓库历史，发布提交被拒绝。请将仓库根作为独立仓库后再运行。"
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
                                description="knowledge-base / obsidian-kb 发布辅助（仅显式调用，不自动发布）")
    p.add_argument("--json", action="store_true")
    sub = p.add_subparsers(dest="command", required=True)

    def common(sp):
        sp.add_argument("--version", required=True, help="目标版本号，如 0.6.0")
        sp.add_argument("--validator", help="quick_validate.py 路径（可选）")

    sp = sub.add_parser("check", help="发布前检查（CHANGELOG/双 skill quick_validate）")
    common(sp)
    sp.set_defaults(func=cmd_check)

    sp = sub.add_parser("package", help="双 skill 打包到 dist/")
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
