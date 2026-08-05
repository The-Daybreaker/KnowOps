#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""kb_config.py - knowledge-workflow 配置与多 vault 管理（Python 标准库，跨平台）

职责：
  - 配置发现：显式 --config → 从当前目录向上查找 knowledge-workflow.config.json
    → 兼容旧文件名 knowledge-base.config.json / obsidian-kb.config.json（需迁移）
    → 提示首次初始化
  - 首次初始化写入：默认写入 vault 内隐藏目录 .config/（可改选其他位置）；
    写入规则：允许 vault 内隐藏目录（点开头），不写入用户笔记内容区
  - 多 vault：注册 / 列出 / 移除 / 默认切换 / 按名解析路径 / 路径校验
  - 偏好读写：get / set（点号键，如 preferences.gitCommit）
  - schema version 检查与迁移（migrate；v1→v2→v3→v4→v5 链式迁移）

设计原则：零硬编码个人路径；配置文件是保存"位置与习惯"的唯一地方。
所有子命令支持 --json 输出机器可读结果，供 agent 消费。
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile

CONFIG_FILENAME = "knowledge-workflow.config.json"
# 历史文件名（find 时兼容、migrate 时迁移到新名）：v4（knowledge-base）与 v≤3（obsidian-kb）
LEGACY_FILENAMES = ("knowledge-base.config.json", "obsidian-kb.config.json")
SCHEMA_VERSION = 5

# 默认偏好（写入新配置；均为可配置默认值，非个人习惯硬编码）
# v2.0 起：剪藏/模板/附件/Bases/Canvas 为文件类型分类，位置不预设，
# 使用时以用户指令为准（配置中不设目录键）；收件箱已移除。
# v2.2.0 起：新增 scheduleDir（日程内容模块目录）与 dashboardFile（看板可选组件）。
# v4.0（0.6.0）起：新增 configDir（vault 内隐藏目录名，默认 config → 实际 .config/）。
DEFAULT_PREFERENCES = {
    "dailyFormat": "YYYY-MM/YYYY-MM-DD",
    "dailyFolder": "日志",
    "structure": "default",
    "questionDir": "问题",
    "projectsDir": "项目",
    "knowledgeDir": "知识",
    "scheduleDir": "日程",
    "dashboardFile": "看板.md",
    "todoFile": "TODO.md",
    "logDir": "log",
    "exportDirName": "HTML-Export",
    "configDir": "config",
    "gitCommit": True,
}


class ConfigError(Exception):
    """配置相关错误，message 面向用户（中文）。"""


# ---------------------------------------------------------------------------
# 基础 IO
# ---------------------------------------------------------------------------

def _read_json(path: str) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        raise ConfigError(f"配置文件不存在：{path}")
    except json.JSONDecodeError as e:
        raise ConfigError(f"配置文件不是合法 JSON：{path}（{e}）")
    if not isinstance(data, dict):
        raise ConfigError(f"配置文件根节点必须是对象：{path}")
    return data


def _write_json_atomic(path: str, data: dict) -> None:
    """原子写入：先写临时文件再替换，避免半成品状态。"""
    directory = os.path.dirname(os.path.abspath(path))
    os.makedirs(directory, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".kb-", suffix=".tmp", dir=directory)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def _norm_path(p: str) -> str:
    return os.path.normpath(os.path.abspath(os.path.expanduser(p)))


def hidden_dir_name(data: dict | None = None) -> str:
    """vault 内隐藏目录名：preferences.configDir 的值加点前缀（config → .config）。"""
    name = "config"
    if data:
        name = (data.get("preferences") or {}).get("configDir") or name
    return "." + name.lstrip(".")


def default_config_dir(vault_path: str) -> str:
    """配置文件默认目录：<vault>/.config/（vault 内隐藏目录，v4 起默认）。"""
    return os.path.join(vault_path, hidden_dir_name())


# ---------------------------------------------------------------------------
# 配置发现
# ---------------------------------------------------------------------------

def find_config(explicit: str | None = None, start: str | None = None) -> str | None:
    """按发现顺序定位配置文件，找不到返回 None。

    顺序：显式路径 → 新文件名（knowledge-workflow.config.json）向上查找 →
    旧文件名（knowledge-base.config.json / obsidian-kb.config.json）向上查找
    （兼容，返回旧路径，需迁移）。
    不查系统环境变量 / 全局用户目录（按项目隔离）。
    """
    if explicit:
        p = _norm_path(explicit)
        if os.path.isfile(p):
            return p
        raise ConfigError(f"显式指定的配置文件不存在：{p}")

    current = _norm_path(start or os.getcwd())
    while True:
        # 候选位置：目录本身 + 目录内隐藏目录（.config/，v4 默认配置位置）
        for fname in (CONFIG_FILENAME, *LEGACY_FILENAMES):
            for cand in (os.path.join(current, fname),
                         os.path.join(current, hidden_dir_name(), fname)):
                if os.path.isfile(cand):
                    return cand
        parent = os.path.dirname(current)
        if parent == current:
            return None
        current = parent


def is_legacy_path(path: str) -> bool:
    return os.path.basename(path) in LEGACY_FILENAMES


def load_config(explicit: str | None = None, start: str | None = None) -> tuple[dict, str]:
    """加载配置，返回 (data, path)。找不到或校验失败抛 ConfigError。"""
    path = find_config(explicit, start)
    if path is None:
        raise ConfigError(
            "未找到配置文件。请先执行首次初始化：\n"
            f"  kb_config.py init --vault-name <名称> --vault-path <vault路径>\n"
            f"（配置默认写入 vault 内隐藏目录 .config/）"
        )
    data = _read_json(path)
    check_schema(data, path)
    return data, path


def check_schema(data: dict, path: str = "") -> None:
    version = data.get("version")
    if version is None:
        raise ConfigError(f"配置缺少 version 字段：{path}")
    if not isinstance(version, int) or version < 1:
        raise ConfigError(f"配置 version 非法：{version!r}（{path}）")
    if version > SCHEMA_VERSION:
        raise ConfigError(
            f"配置 schema 版本（{version}）高于本工具支持的版本（{SCHEMA_VERSION}）。\n"
            f"请升级 knowledge-workflow skill 后再操作。"
        )
    if version < SCHEMA_VERSION:
        # 有迁移路径时由 migrate 处理；这里提示
        raise ConfigError(
            f"配置 schema 版本（{version}）过旧，当前为 {SCHEMA_VERSION}。\n"
            f"请先执行：kb_config.py migrate --config \"{path}\""
        )
    if "vaults" not in data or not isinstance(data["vaults"], dict):
        raise ConfigError(f"配置缺少 vaults 对象：{path}")


# ---------------------------------------------------------------------------
# 位置规则（v4：vault 内仅允许隐藏目录，不写入用户笔记区）
# ---------------------------------------------------------------------------

def _is_inside(path: str, base: str) -> bool:
    try:
        return os.path.commonpath([path, base]) == base
    except ValueError:
        return False


def assert_not_note_area(path: str, vault_path: str, label: str) -> None:
    """位置规则：配置/导出等知识库无关文件若位于 vault 内，必须处于隐藏目录
    （点开头，如 .config/）下；不得写入用户笔记内容区。"""
    norm_path = _norm_path(path)
    norm_vault = _norm_path(vault_path)
    if not _is_inside(norm_path, norm_vault):
        return
    rel = os.path.relpath(norm_path, norm_vault)
    first = rel.split(os.sep)[0]
    if not first.startswith("."):
        raise ConfigError(
            f"{label}不能写入 vault 用户笔记区：{path}\n"
            f"（vault 内仅允许隐藏目录，如 {os.path.join(norm_vault, hidden_dir_name())}）"
        )


# ---------------------------------------------------------------------------
# vault 操作
# ---------------------------------------------------------------------------

def validate_vault_path(path: str) -> str:
    """校验 vault 路径：必须存在且是目录。返回规范化绝对路径。"""
    p = _norm_path(path)
    if not os.path.isdir(p):
        raise ConfigError(f"vault 路径不存在或不是目录：{p}")
    return p


def vault_warnings(path: str) -> list[str]:
    """非致命提示：例如目录下没有 .obsidian（可能尚未被 Obsidian 打开过）。"""
    warns = []
    if not os.path.isdir(os.path.join(path, ".obsidian")):
        warns.append(
            "该目录下暂无 .obsidian 配置目录；若这是新文件夹，请先在 Obsidian 中"
            "「打开文件夹作为仓库」注册，否则无法操作它。"
        )
    return warns


def add_vault(data: dict, name: str, path: str) -> list[str]:
    if not name or not name.strip():
        raise ConfigError("vault 名称不能为空")
    name = name.strip()
    if name in data["vaults"]:
        raise ConfigError(f"vault 名称已存在：{name}（如需更换路径请先 remove-vault）")
    norm = validate_vault_path(path)
    for existing_name, v in data["vaults"].items():
        if _norm_path(v.get("path", "")) == norm:
            raise ConfigError(f"该路径已被注册为 vault「{existing_name}」：{norm}")
    data["vaults"][name] = {"name": name, "path": norm}
    return vault_warnings(norm)


def remove_vault(data: dict, name: str) -> None:
    if name not in data["vaults"]:
        raise ConfigError(f"vault 不存在：{name}")
    del data["vaults"][name]
    if data.get("defaultVault") == name:
        data["defaultVault"] = next(iter(data["vaults"]), None)


def set_default(data: dict, name: str) -> None:
    if name not in data["vaults"]:
        raise ConfigError(f"vault 不存在：{name}")
    data["defaultVault"] = name


def resolve_vault(data: dict, name: str | None = None) -> dict:
    """按名解析 vault；name 为空时用默认 vault。单 vault 时可省略名称。"""
    vaults = data["vaults"]
    if name is None:
        name = data.get("defaultVault")
        if name is None:
            if len(vaults) == 1:
                name = next(iter(vaults))
            else:
                raise ConfigError("未设置默认 vault，请用 vault=<名称> 显式指定或先 set-default")
    if name not in vaults:
        known = "、".join(vaults) or "（无）"
        raise ConfigError(f"vault 不存在：{name}（已注册：{known}）")
    return vaults[name]


# ---------------------------------------------------------------------------
# 点号键 get / set
# ---------------------------------------------------------------------------

def get_key(data: dict, dotted: str):
    node = data
    for part in dotted.split("."):
        if not isinstance(node, dict) or part not in node:
            raise ConfigError(f"配置项不存在：{dotted}")
        node = node[part]
    return node


def set_key(data: dict, dotted: str, raw_value: str):
    parts = dotted.split(".")
    node = data
    for part in parts[:-1]:
        nxt = node.get(part)
        if nxt is None:
            nxt = {}
            node[part] = nxt
        if not isinstance(nxt, dict):
            raise ConfigError(f"配置项 {part} 不是对象，无法设置子键：{dotted}")
        node = nxt
    leaf = parts[-1]
    old = node.get(leaf)
    node[leaf] = _coerce_value(raw_value, old)
    return old


def _coerce_value(raw: str, old):
    """按旧值类型做最小 coercion；无旧值时尝试解析 JSON 标量，失败按字符串。"""
    if isinstance(old, bool):
        low = raw.strip().lower()
        if low in ("true", "1", "yes", "on"):
            return True
        if low in ("false", "0", "no", "off"):
            return False
        raise ConfigError(f"布尔配置项只接受 true/false，收到：{raw}")
    if isinstance(old, int) and not isinstance(old, bool):
        try:
            return int(raw)
        except ValueError:
            raise ConfigError(f"整数配置项收到非法值：{raw}")
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        return raw


# ---------------------------------------------------------------------------
# 迁移
# ---------------------------------------------------------------------------

MIGRATIONS = {}  # version -> callable(data) -> data；未来 schema 变更在此注册


def _migrate_v1_to_v2(data: dict) -> dict:
    """v1 → v2（v2.0.0）：移除文件类型目录键与收件箱；knowledgeDir 改名。

    - 删除 inboxDir / clipDir / templateDir / attachmentDir
      （v2.0 起文件类型位置以用户指令为准，不预设目录）；
    - knowledgeDir 默认值由「知识与经验」改为「知识」：
      仅当旧值等于旧默认时改名，用户自定义值保持不变。
    """
    prefs = data.setdefault("preferences", {})
    for key in ("inboxDir", "clipDir", "templateDir", "attachmentDir"):
        prefs.pop(key, None)
    if prefs.get("knowledgeDir") == "知识与经验":
        prefs["knowledgeDir"] = "知识"
    return data


def _migrate_v2_to_v3(data: dict) -> dict:
    """v2 → v3（v2.2.0）：新增日程目录与看板可选组件配置键。

    - 补齐 scheduleDir（默认「日程」）与 dashboardFile（默认「看板.md」），
      缺省补齐、不覆盖用户自定义值。
    """
    prefs = data.setdefault("preferences", {})
    defaults = DEFAULT_PREFERENCES
    for key in ("scheduleDir", "dashboardFile"):
        if key not in prefs:
            prefs[key] = defaults[key]
    return data


def _migrate_v3_to_v4(data: dict) -> dict:
    """v3 → v4（0.6.0）：知识库无关文件位置改为 vault 内隐藏目录。

    - 补齐 preferences.configDir（默认 config → 实际目录 .config/），缺省补齐；
    - exportRoot：若等于旧默认（vault 上级目录/HTML-Export）则迁移到
      <vault>/.config/HTML-Export/；用户自定义值保留（仍受「不写入笔记区」规则约束）；
    - 配置文件改名（obsidian-kb.config.json / knowledge-base.config.json →
      knowledge-workflow.config.json）在 migrate 命令的文件层完成，本函数只处理数据。
    """
    prefs = data.setdefault("preferences", {})
    if "configDir" not in prefs:
        prefs["configDir"] = DEFAULT_PREFERENCES["configDir"]
    vaults = data.get("vaults", {})
    default = data.get("defaultVault")
    vault_path = None
    if default and default in vaults:
        vault_path = vaults[default].get("path")
    elif vaults:
        vault_path = next(iter(vaults.values())).get("path")
    if vault_path:
        er = data.get("exportRoot")
        if er:
            old_default = os.path.join(os.path.dirname(vault_path), "HTML-Export")
            new_default = os.path.join(vault_path, ".config", "HTML-Export")
            if _norm_path(er) == _norm_path(old_default):
                data["exportRoot"] = new_default
    return data


def _migrate_v4_to_v5(data: dict) -> dict:
    """v4 → v5（0.7.0）：skill 改名 knowledge-workflow，配置文件改名
    （knowledge-base.config.json → knowledge-workflow.config.json）。
    数据无结构变化；文件名迁移在 migrate 命令的文件层完成。
    """
    return data


MIGRATIONS[1] = _migrate_v1_to_v2
MIGRATIONS[2] = _migrate_v2_to_v3
MIGRATIONS[3] = _migrate_v3_to_v4
MIGRATIONS[4] = _migrate_v4_to_v5


def migrate(data: dict, path: str) -> tuple[dict, list[str]]:
    """把旧版本配置迁移到当前 SCHEMA_VERSION。返回 (新配置, 迁移说明列表)。"""
    notes = []
    version = data.get("version")
    if not isinstance(version, int):
        raise ConfigError(f"配置 version 非法：{version!r}")
    while version < SCHEMA_VERSION:
        step = MIGRATIONS.get(version)
        if step is None:
            raise ConfigError(f"缺少从 schema v{version} 到 v{version + 1} 的迁移路径")
        data = step(data)
        version += 1
        data["version"] = version
        notes.append(f"已迁移 schema v{version - 1} → v{version}")
    if version > SCHEMA_VERSION:
        raise ConfigError(f"配置 schema 版本（{version}）高于支持的版本（{SCHEMA_VERSION}）")
    # 兜底补全新增偏好键（缺什么补什么，不覆盖用户已有值）
    prefs = data.setdefault("preferences", {})
    for k, v in DEFAULT_PREFERENCES.items():
        prefs.setdefault(k, v)
    _write_json_atomic(path, data)
    return data, notes


# ---------------------------------------------------------------------------
# 子命令
# ---------------------------------------------------------------------------

def cmd_init(args) -> dict:
    """首次初始化：创建配置文件。默认写入 vault 内隐藏目录 .config/（可改选）。"""
    vault_path = validate_vault_path(args.vault_path)
    config_path = args.config
    if config_path:
        config_path = _norm_path(config_path)
    else:
        config_path = os.path.join(default_config_dir(vault_path), CONFIG_FILENAME)

    if os.path.exists(config_path) and not args.force:
        raise ConfigError(f"配置文件已存在：{config_path}（--force 可覆盖，或改用 add-vault）")

    # 位置规则：vault 内仅允许隐藏目录
    assert_not_note_area(config_path, vault_path, "配置文件")

    data = {
        "version": SCHEMA_VERSION,
        "defaultVault": args.vault_name,
        "vaults": {args.vault_name: {"name": args.vault_name, "path": vault_path}},
        "preferences": dict(DEFAULT_PREFERENCES),
    }
    if args.export_root:
        export_root = _norm_path(args.export_root)
        assert_not_note_area(export_root, vault_path, "HTML 导出目录")
        data["exportRoot"] = export_root
    if args.cli_path:
        cli = _norm_path(args.cli_path)
        if not os.path.isfile(cli):
            raise ConfigError(f"指定的 CLI 路径不存在：{cli}")
        data["cliPath"] = cli

    _write_json_atomic(config_path, data)
    warns = vault_warnings(vault_path)
    return {
        "config": config_path,
        "vault": data["vaults"][args.vault_name],
        "exportRoot": data.get("exportRoot"),
        "warnings": warns,
    }


def cmd_find(args) -> dict:
    path = find_config(args.config, args.start)
    return {
        "found": path is not None,
        "path": path,
        "legacy": is_legacy_path(path) if path else False,
    }


def cmd_add_vault(args) -> dict:
    data, path = load_config(args.config)
    warns = add_vault(data, args.name, args.path)
    if args.default or data.get("defaultVault") is None:
        data["defaultVault"] = args.name
    _write_json_atomic(path, data)
    return {"config": path, "added": args.name, "defaultVault": data["defaultVault"], "warnings": warns}


def cmd_remove_vault(args) -> dict:
    data, path = load_config(args.config)
    remove_vault(data, args.name)
    _write_json_atomic(path, data)
    return {"config": path, "removed": args.name, "defaultVault": data.get("defaultVault")}


def cmd_list(args) -> dict:
    data, path = load_config(args.config)
    return {
        "config": path,
        "defaultVault": data.get("defaultVault"),
        "exportRoot": data.get("exportRoot"),
        "cliPath": data.get("cliPath"),
        "vaults": list(data["vaults"].values()),
        "preferences": data.get("preferences", {}),
    }


def cmd_set_default(args) -> dict:
    data, path = load_config(args.config)
    set_default(data, args.name)
    _write_json_atomic(path, data)
    return {"config": path, "defaultVault": args.name}


def cmd_path(args) -> dict:
    data, _ = load_config(args.config)
    v = resolve_vault(data, args.name)
    return {"name": v["name"], "path": v["path"]}


def cmd_get(args) -> dict:
    data, path = load_config(args.config)
    return {"config": path, "key": args.key, "value": get_key(data, args.key)}


def cmd_set(args) -> dict:
    data, path = load_config(args.config)
    old = set_key(data, args.key, args.value)
    _write_json_atomic(path, data)
    return {"config": path, "key": args.key, "old": old, "value": get_key(data, args.key)}


def cmd_validate(args) -> dict:
    data, path = load_config(args.config)
    problems = []
    warnings = []
    for name, v in data["vaults"].items():
        p = v.get("path", "")
        if not os.path.isdir(p):
            problems.append(f"vault「{name}」路径不存在：{p}")
    export_root = data.get("exportRoot")
    if export_root and not os.path.isdir(export_root):
        warnings.append(f"exportRoot 目录不存在（将在首次导出时自动创建）：{export_root}")
    cli = data.get("cliPath")
    if cli and not os.path.isfile(cli):
        problems.append(f"cliPath 不存在：{cli}")
    return {"config": path, "ok": not problems, "problems": problems, "warnings": warnings}


def cmd_migrate(args) -> dict:
    """迁移旧配置到当前 schema；旧文件名（knowledge-base / obsidian-kb）迁移时
    同时写入新文件名（knowledge-workflow.config.json），旧文件保留不删除。"""
    path = find_config(args.config)
    if path is None:
        raise ConfigError("未找到配置文件，无法迁移")
    data = _read_json(path)
    data, notes = migrate(data, path)

    new_path = path
    if is_legacy_path(path):
        vault_path = None
        default = data.get("defaultVault")
        vaults = data.get("vaults", {})
        if default and default in vaults:
            vault_path = vaults[default].get("path")
        if vault_path:
            new_path = os.path.join(default_config_dir(vault_path), CONFIG_FILENAME)
            _write_json_atomic(new_path, data)
            notes.append(f"配置文件名已迁移：{path} → {new_path}（旧文件保留）")
    return {"config": new_path, "version": data["version"],
            "notes": notes or ["已是最新 schema，无需迁移"]}


# ---------------------------------------------------------------------------
# 入口
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="kb_config.py",
        description="knowledge-workflow 配置与多 vault 管理（配置默认写入 vault 内隐藏目录 .config/）",
    )
    p.add_argument("--json", action="store_true", help="以 JSON 输出结果（供 agent 消费）")
    sub = p.add_subparsers(dest="command", required=True)

    def add_config_arg(sp):
        sp.add_argument("--config", help="显式指定配置文件路径")

    sp = sub.add_parser("init", help="首次初始化：创建配置文件")
    sp.add_argument("--vault-name", required=True, help="vault 名称（用户确认的实际名称）")
    sp.add_argument("--vault-path", required=True, help="vault 实际路径")
    sp.add_argument("--config", help="配置文件写入位置（默认：<vault>/.config/）")
    sp.add_argument("--export-root", help="HTML 导出根目录（可选；默认 <vault>/.config/HTML-Export/，不提供则不启用导出）")
    sp.add_argument("--cli-path", help="Obsidian CLI 路径（可选，发现后写入）")
    sp.add_argument("--force", action="store_true", help="覆盖已存在的配置文件")
    sp.set_defaults(func=cmd_init)

    sp = sub.add_parser("find", help="定位配置文件")
    add_config_arg(sp)
    sp.add_argument("--start", help="向上查找的起始目录（默认当前目录）")
    sp.set_defaults(func=cmd_find)

    sp = sub.add_parser("add-vault", help="注册 vault")
    add_config_arg(sp)
    sp.add_argument("--name", required=True)
    sp.add_argument("--path", required=True)
    sp.add_argument("--default", action="store_true", help="同时设为默认 vault")
    sp.set_defaults(func=cmd_add_vault)

    sp = sub.add_parser("remove-vault", help="移除 vault（不删除任何文件）")
    add_config_arg(sp)
    sp.add_argument("--name", required=True)
    sp.set_defaults(func=cmd_remove_vault)

    sp = sub.add_parser("list", help="列出配置与全部 vault")
    add_config_arg(sp)
    sp.set_defaults(func=cmd_list)

    sp = sub.add_parser("set-default", help="切换默认 vault")
    add_config_arg(sp)
    sp.add_argument("--name", required=True)
    sp.set_defaults(func=cmd_set_default)

    sp = sub.add_parser("path", help="按名解析 vault 路径（缺省用默认 vault）")
    add_config_arg(sp)
    sp.add_argument("--name")
    sp.set_defaults(func=cmd_path)

    sp = sub.add_parser("get", help="读取配置项（点号键，如 preferences.gitCommit）")
    add_config_arg(sp)
    sp.add_argument("key")
    sp.set_defaults(func=cmd_get)

    sp = sub.add_parser("set", help="修改配置项（用户知情后使用）")
    add_config_arg(sp)
    sp.add_argument("key")
    sp.add_argument("value")
    sp.set_defaults(func=cmd_set)

    sp = sub.add_parser("validate", help="校验配置与 vault 路径有效性")
    add_config_arg(sp)
    sp.set_defaults(func=cmd_validate)

    sp = sub.add_parser("migrate", help="迁移旧 schema 配置到当前版本（旧文件名一并迁移）")
    add_config_arg(sp)
    sp.set_defaults(func=cmd_migrate)

    return p


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = args.func(args)
    except ConfigError as e:
        if args.json:
            print(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False))
        else:
            print(f"错误：{e}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps({"ok": True, **result}, ensure_ascii=False))
    else:
        _print_human(args.command, result)
    return 0


def _print_human(command: str, result: dict) -> None:
    if command == "find":
        print(result["path"] if result["found"] else "（未找到配置文件）")
        if result.get("legacy"):
            print("（旧文件名，请执行 kb_config.py migrate 迁移到新文件名）")
    elif command == "list":
        print(f"配置文件：{result['config']}")
        print(f"默认 vault：{result['defaultVault']}")
        print(f"HTML 导出根目录：{result.get('exportRoot') or '（未启用）'}")
        if result.get("cliPath"):
            print(f"CLI 路径：{result['cliPath']}")
        print("vaults：")
        for v in result["vaults"]:
            mark = "*" if v["name"] == result["defaultVault"] else " "
            print(f" {mark} {v['name']}  ->  {v['path']}")
        print("偏好：")
        for k, v in result["preferences"].items():
            print(f"  {k} = {v}")
    elif command == "get":
        print(json.dumps(result["value"], ensure_ascii=False))
    else:
        for k, v in result.items():
            if isinstance(v, (dict, list)):
                v = json.dumps(v, ensure_ascii=False)
            print(f"{k}: {v}")


if __name__ == "__main__":
    sys.exit(main())
