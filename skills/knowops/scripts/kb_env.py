#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""kb_env.py - knowops 环境自检（Python 标准库，跨平台）

检查项：
  1. obsidian CLI 是否可用（配置 cliPath → PATH → 平台常见位置）
  2. Obsidian 是否运行 / CLI 是否可连接；未运行时尝试拉起并轮询等待
  3. 配置文件是否有效、vault 路径是否存在
  4. （可选）目标 vault 是否已在 Obsidian 注册

设计要点：
  - CLI 非 headless：它连接的是"已运行的 Obsidian"。官方称首条命令可拉起 app，
    实测在自定义安装目录 / PATH 不全时不可靠，因此本脚本实现显式拉起 + 轮询。
  - 拉起方式：Windows 用 cliPath 同目录的 Obsidian.exe；macOS 用 `open -a Obsidian`。
  - 检查失败时给出可执行的修复提示，不静默失败。
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

import kb_config  # noqa: E402

POLL_INTERVAL = 2.0
POLL_TIMEOUT = 40.0
CMD_TIMEOUT = 20.0


class EnvError(Exception):
    pass


# ---------------------------------------------------------------------------
# CLI 发现
# ---------------------------------------------------------------------------

def platform_cli_candidates() -> list[str]:
    candidates = []
    if sys.platform.startswith("win"):
        local = os.environ.get("LOCALAPPDATA", "")
        if local:
            candidates.append(os.path.join(local, "Obsidian", "Obsidian.com"))
            candidates.append(os.path.join(local, "Obsidian", "Obsidian.exe"))
        for pf in (os.environ.get("ProgramFiles"), os.environ.get("ProgramFiles(x86)")):
            if pf:
                candidates.append(os.path.join(pf, "Obsidian", "Obsidian.com"))
    elif sys.platform == "darwin":
        candidates.append("/Applications/Obsidian.app/Contents/MacOS/Obsidian")
    return candidates


def resolve_cli(config: dict | None = None) -> tuple[str | None, str]:
    """返回 (cli_path 或 None, 发现来源说明)。"""
    if config and config.get("cliPath"):
        p = config["cliPath"]
        if os.path.isfile(p):
            return p, "配置 cliPath"
    on_path = shutil.which("obsidian")
    if on_path:
        return on_path, "PATH"
    for c in platform_cli_candidates():
        if os.path.isfile(c):
            return c, "平台常见位置"
    return None, "未找到"


# ---------------------------------------------------------------------------
# CLI 调用与拉起
# ---------------------------------------------------------------------------

def run_cli(cli: str, *args: str, timeout: float = CMD_TIMEOUT) -> subprocess.CompletedProcess:
    return subprocess.run(
        [cli, *args],
        capture_output=True, text=True, timeout=timeout, encoding="utf-8", errors="replace",
    )


def cli_alive(cli: str) -> tuple[bool, str]:
    """用 version 探测 CLI 是否可连接到运行中的 Obsidian。"""
    try:
        r = run_cli(cli, "version", timeout=15)
    except subprocess.TimeoutExpired:
        return False, "CLI 调用超时"
    except OSError as e:
        return False, f"CLI 无法执行：{e}"
    out = (r.stdout or "") + (r.stderr or "")
    if r.returncode == 0 and r.stdout.strip() and not out.lstrip().startswith("Error:"):
        return True, r.stdout.strip()
    return False, out.strip() or "CLI 无响应"


def _obsidian_app_path(cli: str) -> str | None:
    """由 CLI 路径推导 app 路径：Obsidian.com 同目录的 Obsidian.exe。"""
    directory = os.path.dirname(os.path.abspath(cli))
    if sys.platform.startswith("win"):
        for name in ("Obsidian.exe",):
            p = os.path.join(directory, name)
            if os.path.isfile(p):
                return p
    elif sys.platform == "darwin":
        # cli 即 .app/Contents/MacOS/Obsidian
        if cli.endswith("/Contents/MacOS/Obsidian"):
            return cli
    return None


# 无 GPU/远程/沙箱环境下拉起失败时使用的 Electron 兜底参数（实测有效）
_GPU_FALLBACK_FLAGS = ["--in-process-gpu", "--disable-gpu", "--disable-software-rasterizer"]
_RETRY_AFTER = 12.0  # 普通方式拉起后等待多久未见效则换 GPU 兜底重拉


def _spawn_win(app: str, flags: list[str]) -> None:
    subprocess.Popen(
        [app, *flags],
        creationflags=getattr(subprocess, "DETACHED_PROCESS", 0)
        | getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0),
        close_fds=True,
    )


def launch_obsidian(cli: str) -> tuple[bool, str]:
    """尝试拉起 Obsidian 并轮询等待 CLI 可用。

    Windows：先普通拉起；若 12 秒内未见效，换 GPU 兜底参数（--in-process-gpu 等，
    解决无 GPU 桌面/远程/沙箱环境 Obsidian 因 "GPU process isn't usable" 退出
    的问题）再拉，直到超时。
    """
    app = _obsidian_app_path(cli)
    try:
        if sys.platform.startswith("win"):
            if not app:
                return False, "无法由 CLI 路径推导 Obsidian.exe，请手动打开 Obsidian"
            _spawn_win(app, [])
            retried = False
            retry_at = time.time() + _RETRY_AFTER
        elif sys.platform == "darwin":
            subprocess.Popen(["open", "-a", "Obsidian"], close_fds=True)
            retried, retry_at = True, time.time()  # macOS 无 GPU 兜底，直接等到超时
        else:
            if not app:
                return False, "无法定位 Obsidian 可执行文件，请手动打开"
            subprocess.Popen([app], start_new_session=True, close_fds=True)
            retried, retry_at = True, time.time()
    except OSError as e:
        return False, f"拉起 Obsidian 失败：{e}。请手动打开 Obsidian"

    deadline = time.time() + POLL_TIMEOUT
    while time.time() < deadline:
        alive, detail = cli_alive(cli)
        if alive:
            return True, f"Obsidian 已拉起并就绪（{detail}）"
        if sys.platform.startswith("win") and not retried and time.time() >= retry_at:
            _spawn_win(app, _GPU_FALLBACK_FLAGS)
            retried = True
        time.sleep(POLL_INTERVAL)
    return False, f"已尝试拉起 Obsidian（含 GPU 兜底参数），但 {int(POLL_TIMEOUT)} 秒内 CLI 仍不可用。请手动打开 Obsidian 后重试"


# ---------------------------------------------------------------------------
# 子命令
# ---------------------------------------------------------------------------

def cmd_cli_path(args) -> dict:
    config = _try_load_config(args.config)
    cli, source = resolve_cli(config)
    return {"cliPath": cli, "source": source, "found": cli is not None}


def cmd_launch(args) -> dict:
    config = _try_load_config(args.config)
    cli = _require_cli(config)
    alive, detail = cli_alive(cli)
    if alive:
        return {"cliPath": cli, "launched": False, "message": f"Obsidian 已在运行（{detail}）"}
    ok, msg = launch_obsidian(cli)
    if not ok:
        raise EnvError(msg)
    return {"cliPath": cli, "launched": True, "message": msg}


def cmd_check(args) -> dict:
    report: dict = {"checks": {}, "ok": True}

    def fail(key, msg):
        report["checks"][key] = {"ok": False, "message": msg}
        report["ok"] = False

    def pass_(key, msg, **extra):
        report["checks"][key] = {"ok": True, "message": msg, **extra}

    # 1. 配置文件（可选，缺失不致命，只提示）
    config = None
    config_path = None
    try:
        config, config_path = kb_config.load_config(args.config)
        pass_("config", f"配置有效：{config_path}")
    except kb_config.ConfigError as e:
        report["checks"]["config"] = {"ok": None, "message": str(e)}

    # 2. CLI 发现
    cli, source = resolve_cli(config)
    if not cli:
        fail("cli", "未找到 obsidian CLI。请在 Obsidian 设置 → 通用 → 命令行界面 中启用并注册 CLI，"
                     "或在初始化时用 --cli-path 指定其路径")
        return report
    pass_("cli", f"CLI 可用（来源：{source}）", cliPath=cli)

    # 3. CLI 连接（必要时拉起）
    alive, detail = cli_alive(cli)
    launched = False
    if not alive:
        ok, msg = launch_obsidian(cli)
        if not ok:
            fail("obsidian", msg)
            return report
        launched = True
        detail = msg
    pass_("obsidian", detail, launched=launched)

    # 4. vault 路径（配置存在时）
    if config:
        problems = []
        for name, v in config.get("vaults", {}).items():
            if not os.path.isdir(v.get("path", "")):
                problems.append(f"vault「{name}」路径不存在：{v.get('path')}")
        if problems:
            fail("vaultPaths", "；".join(problems))
        else:
            pass_("vaultPaths", "全部 vault 路径有效")

    # 5. 目标 vault 是否已在 Obsidian 注册（可选检查）
    target = args.vault
    if not target and config:
        target = config.get("defaultVault")
    if target:
        try:
            r = run_cli(cli, "vaults")
            names = [ln.strip() for ln in (r.stdout or "").splitlines() if ln.strip()]
            if target in names:
                pass_("vaultRegistered", f"vault「{target}」已在 Obsidian 注册")
            else:
                fail("vaultRegistered",
                     f"vault「{target}」未在 Obsidian 注册（已注册：{'、'.join(names) or '无'}）。"
                     f"请在 Obsidian 中打开该文件夹作为仓库")
        except (subprocess.TimeoutExpired, OSError) as e:
            fail("vaultRegistered", f"无法查询 vault 列表：{e}")

    return report


# ---------------------------------------------------------------------------
# 工具
# ---------------------------------------------------------------------------

def _try_load_config(explicit: str | None) -> dict | None:
    try:
        data, _ = kb_config.load_config(explicit)
        return data
    except kb_config.ConfigError:
        return None


def _require_cli(config: dict | None) -> str:
    cli, source = resolve_cli(config)
    if not cli:
        raise EnvError("未找到 obsidian CLI（PATH、配置 cliPath、平台常见位置均无）")
    return cli


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="kb_env.py", description="knowops 环境自检")
    p.add_argument("--json", action="store_true", help="以 JSON 输出结果")
    sub = p.add_subparsers(dest="command", required=True)

    sp = sub.add_parser("check", help="全面自检（CLI / Obsidian / 配置 / vault）")
    sp.add_argument("--config", help="显式指定配置文件路径")
    sp.add_argument("--vault", help="检查指定 vault 是否已注册（缺省用默认 vault）")
    sp.set_defaults(func=cmd_check)

    sp = sub.add_parser("launch", help="尝试拉起 Obsidian 并等待就绪")
    sp.add_argument("--config", help="显式指定配置文件路径")
    sp.set_defaults(func=cmd_launch)

    sp = sub.add_parser("cli-path", help="打印解析到的 CLI 路径与来源")
    sp.add_argument("--config", help="显式指定配置文件路径")
    sp.set_defaults(func=cmd_cli_path)

    return p


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = args.func(args)
    except EnvError as e:
        if args.json:
            print(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False))
        else:
            print(f"错误：{e}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(result, ensure_ascii=False))
    else:
        _print_human(args.command, result)
    return 0 if result.get("ok", True) else 2


def _print_human(command: str, result: dict) -> None:
    if command == "check":
        for name, chk in result["checks"].items():
            mark = {True: "[OK]", False: "[FAIL]", None: "[--]"}[chk["ok"]]
            print(f"{mark} {name}: {chk['message']}")
        print("总体：" + ("通过" if result["ok"] else "存在问题，见上"))
    else:
        for k, v in result.items():
            print(f"{k}: {v}")


if __name__ == "__main__":
    sys.exit(main())
