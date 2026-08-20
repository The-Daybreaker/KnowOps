#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check.py — KnowOps 开发期确定性校验脚本（开发维护用，不随 skill 分发）

用法：
  python tools/check.py                  自动模式：检测到 private/ 时含私有检查
  python tools/check.py --core           仅核心检查（CI 模式；private/ 不在仓库内）
  python tools/check.py --dist <version> 附加 dist 打包完整性检查（发布后运行）

退出码：0 = 无 error（warning 不影响）；1 = 存在 error；2 = 环境缺依赖
（argparse 参数错误同为 2）。
依赖：Python 3.10+、PyYAML。文件读写内部强制 UTF-8（规避本机 GBK 默认编码）。

检查项：
  核心（CI 可跑，不依赖 private/）：
    C1  两 skill SKILL.md frontmatter 可解析且 metadata.version 相等
    C2  workflow.md 模块表：编号自 00 连续、后三位固定为 看板/归档/系统管理
    C3  skill 文档引用的 references/assets/scripts 路径真实存在
    C4  仓库内 JSON 配置可解析
    C5  README 双语与 automation-prompt-template 中模块编号→名称与模块表一致
    C6  vault_check.py 内嵌 type 枚举与 properties.md 声明一致（防双源漂移）
  私有（本地全量，private/ 存在时启用）：
    P1  版本一致性链 + 开发期文档 frontmatter 分档检查
    P2  测试库一级目录与 config preferences 匹配
    P3  测试库笔记 frontmatter 可解析且 type 在枚举内
    P4  模板联动：system-manage 与 html_export 副本一致
    P5  dist 完整性（--dist）：zip 清单与源目录一致
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    print("[FATAL] 缺少 PyYAML：请先 `python -m pip install pyyaml`", file=sys.stderr)
    sys.exit(2)

ROOT = Path(__file__).resolve().parent.parent
SKILL_KNOWOPS = ROOT / "skills" / "knowops"
SKILL_NOTE = ROOT / "skills" / "everywhere-note"
AUTOMATION_TEMPLATE = ROOT / "skills" / "automation-prompt-template.md"
PRIVATE = ROOT / "private"
TEST_VAULT = PRIVATE / "test" / "Obsidian测试知识库"

# 模块表后三位固定名称（编号规则）
FIXED_TAIL = ["看板", "归档", "系统管理"]

# P3：允许无 frontmatter 的文件（相对测试库根，posix 风格）
NO_FM_ALLOW = {
    "看板.md",          # 07 看板嵌入容器（由 dashboardFile 配置）
    "TODO.md",          # 人工快捷清单
}
# P3：项目六文件中除项目说明.md 外的五份固定结构文档（项目说明.md 为项目主
# 笔记，需 frontmatter；其余五份为项目内结构文档，无 frontmatter 属预期）
PROJECT_FIXED_FILES = {"目标.md", "决策记录.md", "研究记录.md", "问题.md", "复盘.md"}


def read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8-sig")


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.passes: list[str] = []

    def ok(self, msg: str) -> None:
        self.passes.append(msg)

    def error(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)


def parse_frontmatter(text: str) -> tuple[dict | None, str]:
    """解析顶部 frontmatter；返回 (dict|None, 正文)。解析失败抛 ValueError。"""
    if not text.startswith("---"):
        return None, text
    lines = text.splitlines()
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            fm_text = "\n".join(lines[1:i])
            data = yaml.safe_load(fm_text)
            return (data if isinstance(data, dict) else {}), "\n".join(lines[i + 1:])
    raise ValueError("frontmatter 未闭合（缺少第二个 ---）")


def safe_read(rep: Report, p: Path, label: str) -> str | None:
    """统一文件读取：失败记 error 并返回 None（调用方据此跳过，校验不中断）。
    UnicodeDecodeError 属 ValueError 子类，坏编码文件同样被捕获。"""
    try:
        return read_text(p)
    except (OSError, ValueError) as e:
        rep.error(f"{label} 读取失败：{e}")
        return None


def read_fm(rep: Report, p: Path, label: str) -> dict | None:
    """读取并解析 frontmatter。返回 None 表示读取/解析失败（已记 error）；
    无 frontmatter 视为空 dict（后续 version 检查报缺失）。"""
    text = safe_read(rep, p, label)
    if text is None:
        return None
    try:
        fm, _ = parse_frontmatter(text)
    except ValueError as e:
        rep.error(f"{label} frontmatter 解析失败：{e}")
        return None
    return fm if isinstance(fm, dict) else {}


# ---------------------------------------------------------------------------
# 核心检查
# ---------------------------------------------------------------------------

def check_c1_skill_versions(rep: Report) -> str | None:
    versions = {}
    for skill, path in (("knowops", SKILL_KNOWOPS / "SKILL.md"),
                        ("everywhere-note", SKILL_NOTE / "SKILL.md")):
        try:
            fm, _ = parse_frontmatter(read_text(path))
        except (OSError, ValueError) as e:
            rep.error(f"C1 {skill}/SKILL.md frontmatter 解析失败：{e}")
            return None
        if not fm or "metadata" not in fm or "version" not in fm["metadata"]:
            rep.error(f"C1 {skill}/SKILL.md 缺 metadata.version")
            return None
        versions[skill] = str(fm["metadata"]["version"])
    if versions["knowops"] != versions["everywhere-note"]:
        rep.error(f"C1 两 skill 版本不一致：knowops={versions['knowops']} "
                  f"everywhere-note={versions['everywhere-note']}")
        return None
    rep.ok(f"C1 两 skill 版本一致：{versions['knowops']}")
    return versions["knowops"]


def parse_module_table(rep: Report) -> dict[str, str] | None:
    """解析 workflow.md「模块总览」表格 → {编号: 名称}。同时执行 C2。"""
    wf_path = SKILL_KNOWOPS / "references" / "workflow.md"
    text = safe_read(rep, wf_path, "C2 workflow.md")
    if text is None:
        return None
    m = re.search(r"## 模块总览.*?(?=\n## |\Z)", text, re.S)
    if not m:
        rep.error("C2 workflow.md 未找到「## 模块总览」章节")
        return None
    rows = re.findall(r"^\|\s*(\d{2})\s+([^\|]+?)\s*\|", m.group(0), re.M)
    if not rows:
        rep.error("C2 workflow.md 模块表未解析到任何行")
        return None
    # 先按原始行序查重（直接构造 dict 会静默去重，重号漏检）
    nums_raw = [int(n) for n, _ in rows]
    dup = sorted({n for n in nums_raw if nums_raw.count(n) > 1})
    if dup:
        rep.error(f"C2 模块编号重复：{dup}")
        return None
    table = {num: name.strip() for num, name in rows}

    # C2a：编号自 00 起连续（按原始行序，兼顾乱序与缺号）
    if nums_raw != list(range(len(nums_raw))):
        rep.error(f"C2 模块编号不连续（原始行序 {nums_raw}）")
        return None
    # C2b：后三位固定
    tail = [table[n] for n in sorted(table, key=int)[-3:]]
    if tail != FIXED_TAIL:
        rep.error(f"C2 模块表后三位应为 {FIXED_TAIL}，实际 {tail}")
        return None
    rep.ok(f"C2 模块表编号连续（{len(table)} 个模块）、后三位固定 {FIXED_TAIL}")
    return table


def check_c3_references(rep: Report) -> None:
    ref_re = re.compile(
        r"(?:references|assets|scripts)/[\w\-\.\u4e00-\u9fff]+(?:/[\w\-\.\u4e00-\u9fff]+)*")
    targets: list[tuple[Path, Path, Path, str]] = [
        # (文档路径, 主解析根, 跨skill回退根, 显示名)
        (SKILL_KNOWOPS / "SKILL.md", SKILL_KNOWOPS, SKILL_NOTE, "knowops/SKILL.md"),
        (SKILL_NOTE / "SKILL.md", SKILL_NOTE, SKILL_KNOWOPS, "everywhere-note/SKILL.md"),
        (AUTOMATION_TEMPLATE, SKILL_KNOWOPS, SKILL_NOTE, "automation-prompt-template.md"),
    ]
    for skill_root in (SKILL_KNOWOPS, SKILL_NOTE):
        refs_dir = skill_root / "references"
        if refs_dir.is_dir():
            for f in sorted(refs_dir.glob("*.md")):
                targets.append((f, skill_root,
                                SKILL_NOTE if skill_root == SKILL_KNOWOPS else SKILL_KNOWOPS,
                                f.relative_to(ROOT).as_posix()))

    missing: list[str] = []
    for doc, primary, fallback, label in targets:
        text = safe_read(rep, doc, f"C3 {label}")
        if text is None:
            continue
        for m in ref_re.finditer(text):
            # 排除更大路径的子串（如 .config/scripts/xxx 中的 scripts/xxx）
            start = m.start()
            if start > 0:
                prev = text[start - 1]
                if prev.isalnum() or prev in "./-_":
                    continue
            ref = m.group(0).rstrip(".,:;，。：；）)")
            if (primary / ref).exists() or (fallback / ref).exists():
                continue
            missing.append(f"{label} → {ref}")
    if missing:
        for it in missing:
            rep.error(f"C3 引用路径不存在：{it}")
    else:
        rep.ok(f"C3 引用完整性通过（扫描 {len(targets)} 份文档）")


def check_c4_json(rep: Report) -> None:
    json_files = [SKILL_KNOWOPS / "assets" / "html-export.json"]
    bad = []
    for p in json_files:
        try:
            json.loads(read_text(p))
        except (OSError, ValueError) as e:  # ValueError 含 JSON/解码错误
            bad.append(f"{p.relative_to(ROOT).as_posix()}：{e}")
    if bad:
        for it in bad:
            rep.error(f"C4 JSON 解析失败：{it}")
    else:
        rep.ok(f"C4 仓库内 JSON 可解析（{len(json_files)} 份）")


def check_c5_module_refs(rep: Report, table: dict[str, str]) -> None:
    """README 双语 + automation-prompt-template 中出现的 `NN 名称` 必须与模块表一致。"""
    files = [ROOT / "README.md", ROOT / "README.en.md", AUTOMATION_TEMPLATE]
    problems = []
    for f in files:
        label = f.relative_to(ROOT).as_posix()
        if not f.is_file():
            problems.append(f"文件不存在：{label}")
            continue
        text = safe_read(rep, f, f"C5 {label}")
        if text is None:
            continue
        seen: dict[str, list[str]] = {}
        for num, name in re.findall(r"`(\d{2})\s+([^`]+)`", text):
            name = name.strip().split("/")[0].strip()
            seen.setdefault(num, [])
            if name not in seen[num]:
                seen[num].append(name)
        for num, names in sorted(seen.items()):
            if len(names) > 1:
                problems.append(f"{label}：编号 {num} 出现多个名称 {names}")
                continue
            name = names[0]
            expect = table.get(num)
            if expect is None:
                problems.append(f"{label}：编号 {num}（{name}）不在模块表中")
            elif name != expect:
                problems.append(f"{label}：编号 {num} 名称应为「{expect}」，实际「{name}」")
    if problems:
        for it in problems:
            rep.error(f"C5 模块引用不一致：{it}")
    else:
        rep.ok("C5 README 双语与提示词模板的模块编号→名称与模块表一致")


def load_type_enum(rep: Report) -> frozenset | None:
    """从 vault_check.py 提取 TYPE_ENUM（C6/P3 共用，单一定义点）。
    提取失败记 error 并返回 None（绝不静默退化为空集）。"""
    vc_path = SKILL_KNOWOPS / "scripts" / "vault_check.py"
    if not vc_path.is_file():
        rep.error("vault_check.py 不存在：skills/knowops/scripts/vault_check.py")
        return None
    vc = safe_read(rep, vc_path, "vault_check.py")
    if vc is None:
        return None
    m = re.search(r"TYPE_ENUM\s*=\s*frozenset\(\s*\{([^}]*)\}", vc, re.S)
    if not m:
        rep.error("vault_check.py 未找到 TYPE_ENUM 定义（正则失配，"
                  "枚举相关检查全部失效，请先修复）")
        return None
    return frozenset(re.findall(r"[\"'](\w+)[\"']", m.group(1)))


def check_c6_enum_sync(rep: Report, vc_enum: frozenset | None) -> None:
    """vault_check.py 内嵌 TYPE_ENUM 与 properties.md 的 type 枚举一致。"""
    if vc_enum is None:
        return  # 提取失败已在 load_type_enum 记 error
    props_path = SKILL_KNOWOPS / "references" / "properties.md"
    if not props_path.is_file():
        rep.error("C6 properties.md 不存在")
        return

    props = safe_read(rep, props_path, "C6 properties.md")
    if props is None:
        return
    row = re.search(r"^\|\s*`type`\s*\|[^\n]*$", props, re.M)
    if not row:
        rep.error("C6 properties.md 未找到 type 属性行")
        return
    # 只取值列（第三列；split 首元素为行首空前缀），避免把说明列或
    # 交叉引用的反引词计入枚举
    cells = row.group(0).split("|")
    if len(cells) < 4:
        rep.error("C6 properties.md type 行格式异常（缺少值列）")
        return
    props_enum = set(re.findall(r"`(\w+)`", cells[3]))

    if vc_enum != props_enum:
        only_vc = sorted(vc_enum - props_enum)
        only_props = sorted(props_enum - vc_enum)
        rep.error(f"C6 type 枚举双源漂移：vault_check 独有 {only_vc}，"
                  f"properties 独有 {only_props}")
    else:
        rep.ok(f"C6 vault_check.py 与 properties.md 的 type 枚举一致（{len(vc_enum)} 个）")


# ---------------------------------------------------------------------------
# 私有检查（private/ 存在时）
# ---------------------------------------------------------------------------

def load_test_config(rep: Report) -> dict | None:
    cfg_path = TEST_VAULT / ".config" / "knowops.config.json"
    try:
        return json.loads(read_text(cfg_path))
    except (OSError, json.JSONDecodeError) as e:
        rep.error(f"P1 测试库配置读取失败：{e}")
        return None


def check_p1_versions(rep: Report, skill_ver: str, cfg: dict | None) -> None:
    # CHANGELOG 顶部条目与历史版本集合
    cl = safe_read(rep, PRIVATE / "dev" / "CHANGELOG.md", "P1 CHANGELOG.md")
    if cl is None:
        return
    entries = re.findall(r"^## \[(\d+\.\d+\.\d+)\]", cl, re.M)
    if not entries:
        rep.error("P1 CHANGELOG.md 未找到任何版本条目")
        return
    if entries[0] != skill_ver:
        rep.error(f"P1 CHANGELOG 顶部条目 {entries[0]} ≠ skill 版本 {skill_ver}")
    else:
        rep.ok(f"P1 CHANGELOG 顶部条目 = {skill_ver}")

    # 严格分档（每版必更）：private/AGENTS.md、TEST-REPORT.md
    for label, path in (("private/AGENTS.md", PRIVATE / "AGENTS.md"),
                        ("TEST-REPORT.md", PRIVATE / "dev" / "TEST-REPORT.md")):
        fm = read_fm(rep, path, f"P1 {label}")
        if fm is None:
            continue  # 读取/解析失败已记 error
        v = str(fm.get("version", ""))
        if v != skill_ver:
            rep.error(f"P1 {label} version={v or '缺失'} ≠ {skill_ver}")
        else:
            rep.ok(f"P1 {label} version = {v}")

    # 滞后分档（须为 CHANGELOG 历史版本；本次无相关改动的版本允许滞后）：
    # DESIGN.md、AUDIT.md（审计档案，首次审计建立前允许不存在）
    for label, path in (("DESIGN.md", PRIVATE / "dev" / "DESIGN.md"),
                        ("AUDIT.md", PRIVATE / "dev" / "AUDIT.md")):
        if label == "AUDIT.md" and not path.is_file():
            continue
        fm = read_fm(rep, path, f"P1 {label}")
        if fm is None:
            continue
        v = str(fm.get("version", ""))
        if not v:
            rep.error(f"P1 {label} frontmatter 缺 version")
        elif v not in entries:
            rep.error(f"P1 {label} version={v} 不是 CHANGELOG 中的历史版本")
        elif v != skill_ver:
            rep.warn(f"P1 {label} version={v} 滞后于当前 {skill_ver}（本次无相关"
                     "改动属预期，否则需更新）")
        else:
            rep.ok(f"P1 {label} version = {v}")

    # 测试库 config 版本
    if cfg is not None:
        cv = str(cfg.get("version", ""))
        if cv != skill_ver:
            rep.error(f"P1 测试库 knowops.config.json version={cv or '缺失'} ≠ {skill_ver}")
        else:
            rep.ok(f"P1 测试库 config version = {cv}")


def check_p2_test_structure(rep: Report, cfg: dict) -> None:
    prefs = cfg.get("preferences")
    if not isinstance(prefs, dict):
        rep.error("P2 knowops.config.json 的 preferences 应为对象")
        prefs = {}
    dir_keys = ["inboxDir", "lifeDir", "knowledgeDir", "assetsDir", "standardsDir",
                "projectsDir", "excerptDir", "dashboardDir", "archiveDir", "systemDir"]
    expected: dict[int, str] = {}
    for k in dir_keys:
        val = prefs.get(k)
        if not val:
            rep.error(f"P2 preferences 缺 {k}")
            continue
        m = re.match(r"^(\d{2})\s+(.+)$", str(val))
        if not m:
            rep.error(f"P2 preferences.{k}={val} 不符合「NN 名称」格式")
            continue
        num = int(m.group(1))
        if num in expected:
            rep.error(f"P2 preferences 编号 {num:02d} 重复"
                      f"（{expected[num]} 与 {m.group(2)}）")
            continue
        expected[num] = m.group(2)

    # 后三位固定：编号为最大三个连续值，且名称与 FIXED_TAIL 逐位对应
    # （防 dashboardDir/archiveDir 名称与键错位）
    if len(expected) >= 3:
        mx = max(expected)
        for off, want in zip((2, 1, 0), FIXED_TAIL):
            got = expected.get(mx - off)
            if got != want:
                rep.error(f"P2 后三位第 {3 - off} 位（编号 {mx - off:02d}）"
                          f"应为「{want}」，实际「{got}」")

    # 实际目录 ⊆ expected（懒加载允许缺失）
    actual: dict[int, str] = {}
    for d in TEST_VAULT.iterdir():
        if d.name.startswith(".") or not d.is_dir():
            continue
        m = re.match(r"^(\d{2})\s+(.+)$", d.name)
        if m:
            actual[int(m.group(1))] = m.group(2)
    problems = []
    for num, name in sorted(actual.items()):
        if num not in expected:
            problems.append(f"目录「{num:02d} {name}」不在 config preferences 中")
        elif expected[num] != name:
            problems.append(f"目录「{num:02d} {name}」与 config 值「{expected[num]}」不一致")
    if problems:
        for it in problems:
            rep.error(f"P2 {it}")
    else:
        rep.ok(f"P2 测试库一级目录与 config 匹配（存在 {len(actual)} 个模块目录）")


def check_p3_test_frontmatter(rep: Report, cfg: dict,
                              type_enum: frozenset | None) -> None:
    if type_enum is None:
        rep.warn("P3 跳过：TYPE_ENUM 提取失败（见前述 error）")
        return

    system_dir = str(cfg.get("preferences", {}).get("systemDir", "09 系统管理"))
    dashboard_file = str(cfg.get("preferences", {}).get("dashboardFile", "看板.md"))
    projects_dir = str(cfg.get("preferences", {}).get("projectsDir", "05 项目系统"))

    no_fm, bad_fm, bad_type = [], [], []
    count = 0
    for p in TEST_VAULT.rglob("*.md"):
        rel = p.relative_to(TEST_VAULT).as_posix()
        if any(part.startswith(".") for part in p.relative_to(TEST_VAULT).parts):
            continue  # 隐藏目录（.config/.obsidian 等）不扫
        count += 1
        try:
            fm, _ = parse_frontmatter(read_text(p))
        except (OSError, ValueError) as e:
            bad_fm.append(f"{rel}：{e}")
            continue
        if fm is None:
            # 豁免：TODO/看板容器、系统管理用户文档、项目固定结构文档
            if (p.name in NO_FM_ALLOW or p.name == dashboard_file
                    or rel.startswith(system_dir + "/")
                    or (rel.startswith(projects_dir + "/")
                        and p.name in PROJECT_FIXED_FILES)):
                continue
            no_fm.append(rel)
            continue
        t = fm.get("type")
        if t is None:
            no_fm.append(f"{rel}（有 frontmatter 但无 type）")
        elif str(t) not in type_enum:
            bad_type.append(f"{rel}：type={t}")
    for it in bad_fm:
        rep.error(f"P3 frontmatter 解析失败：{it}")
    for it in bad_type:
        rep.error(f"P3 type 越界：{it}")
    if no_fm:
        for it in no_fm:
            rep.warn(f"P3 无 frontmatter：{it}")
    rep.ok(f"P3 测试库笔记扫描完成（{count} 篇；error {len(bad_fm) + len(bad_type)}，"
           f"无 frontmatter 警告 {len(no_fm)}）")


def check_p4_template_sync(rep: Report, cfg: dict) -> None:
    prefs = cfg.get("preferences")
    if not isinstance(prefs, dict):
        prefs = {}
    system_dir = str(prefs.get("systemDir", "09 系统管理"))
    tpl_dir = SKILL_KNOWOPS / "assets" / "system-manage"
    tgt_dir = TEST_VAULT / system_dir
    problems = []
    # 4 份逐字一致 + 变更记录前缀一致（副本允许追加变更历史）
    exact = ["用户手册.md", "知识库架构.md", "分类规则.md", "记录规范.md"]
    for name in exact:
        tpl, tgt = tpl_dir / name, tgt_dir / name
        if not tpl.is_file():
            problems.append(f"模板缺失：assets/system-manage/{name}")
            continue
        if not tgt.is_file():
            problems.append(f"测试库副本缺失：{system_dir}/{name}")
            continue
        try:
            differs = read_text(tpl) != read_text(tgt)
        except (OSError, ValueError) as e:
            problems.append(f"模板/副本读取失败（{e}）：{name}")
            continue
        if differs:
            problems.append(f"副本与模板不一致：{system_dir}/{name}")
    vc = "变更记录.md"
    tpl, tgt = tpl_dir / vc, tgt_dir / vc
    if not (tpl.is_file() and tgt.is_file()):
        problems.append(f"变更记录模板或副本缺失：{system_dir}/{vc}")
    else:
        # 变更记录是活文档：副本初始化自模板后持续追加历史条目，且模板的初始
        # 示例条目会随版本更新——历史条目不回溯改写。只校验标题一致性。
        try:
            tpl_title = read_text(tpl).splitlines()[0].strip()
            tgt_title = read_text(tgt).splitlines()[0].strip()
        except (OSError, ValueError, IndexError) as e:
            problems.append(f"{system_dir}/{vc} 读取失败（{e}）")
        else:
            if tpl_title != tgt_title:
                problems.append(f"{system_dir}/{vc} 副本标题与模板不一致"
                                f"（{tgt_title!r} ≠ {tpl_title!r}）")

    # 脚本与配置副本逐字一致
    pairs = [
        (SKILL_KNOWOPS / "scripts" / "html_export.py",
         TEST_VAULT / ".config" / "scripts" / "html_export.py"),
        (SKILL_KNOWOPS / "assets" / "html-export.json",
         TEST_VAULT / ".config" / "scripts" / "html-export.json"),
    ]
    if (SKILL_KNOWOPS / "scripts" / "vault_check.py").is_file():
        pairs.append((SKILL_KNOWOPS / "scripts" / "vault_check.py",
                      TEST_VAULT / ".config" / "scripts" / "vault_check.py"))
    for src, dst in pairs:
        if not dst.is_file():
            problems.append(f"库内副本缺失：{dst.relative_to(TEST_VAULT).as_posix()}")
            continue
        try:
            same = read_text(src) == read_text(dst)
        except (OSError, ValueError) as e:
            problems.append(f"库内副本读取失败（{e}）："
                            f"{dst.relative_to(TEST_VAULT).as_posix()}")
            continue
        if not same:
            problems.append(f"库内副本与模板不一致：{dst.relative_to(TEST_VAULT).as_posix()}")
    if problems:
        for it in problems:
            rep.error(f"P4 {it}")
    else:
        rep.ok("P4 模板联动一致（system-manage 5 份 + 脚本副本）")


def check_p5_dist(rep: Report, version: str) -> None:
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        rep.error(f"P5 --dist 版本号格式非法：{version!r}（应为 X.Y.Z）")
        return
    dist_dir = PRIVATE / "dist" / version
    if not dist_dir.is_dir():
        rep.error(f"P5 dist 目录不存在：{dist_dir.relative_to(ROOT).as_posix()}")
        return
    import zipfile
    for skill, src_root in (("knowops", SKILL_KNOWOPS), ("everywhere-note", SKILL_NOTE)):
        zips = sorted(dist_dir.glob(f"{skill}-v{version}-*.zip"))
        if not zips:
            rep.error(f"P5 缺少 zip：{skill}-v{version}-*.zip")
            continue
        for zp in zips:  # 该版本可能存在多份（重跑打包），逐份校验
            try:
                with zipfile.ZipFile(zp) as zf:
                    names = [n for n in zf.namelist() if not n.endswith("/")]
                    roots = {n.split("/", 1)[0] for n in names}
                    if roots != {skill}:
                        rep.error(f"P5 {zp.name} 根目录应为 {skill}/，实际 {sorted(roots)}")
                        continue
                    zip_set = {n.split("/", 1)[1] for n in names}
                    src_set = {p.relative_to(src_root).as_posix()
                               for p in src_root.rglob("*")
                               if p.is_file() and "__pycache__" not in p.parts
                               and p.suffix != ".pyc"}
                    if zip_set != src_set:
                        rep.error(f"P5 {zp.name} 清单不一致：仅 zip 有 "
                                  f"{sorted(zip_set - src_set)}；仅源目录有 "
                                  f"{sorted(src_set - zip_set)}")
                        continue
                    fm_text = zf.read(f"{skill}/SKILL.md").decode("utf-8-sig")
                    fm, _ = parse_frontmatter(fm_text)
            except (OSError, ValueError, KeyError, zipfile.BadZipFile) as e:
                rep.error(f"P5 {zp.name} 读取/校验失败：{e}")
                continue
            v = str((fm or {}).get("metadata", {}).get("version", ""))
            if v != version:
                rep.error(f"P5 {zp.name} 内 SKILL.md version={v} ≠ {version}")
                continue
            rep.ok(f"P5 {zp.name} 完整（{len(zip_set)} 个文件，版本正确）")


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="KnowOps 开发期确定性校验")
    parser.add_argument("--core", action="store_true", help="仅核心检查（CI 模式）")
    parser.add_argument("--dist", metavar="VERSION", help="附加 dist 完整性检查")
    args = parser.parse_args()

    rep = Report()
    print("== KnowOps 开发期校验 ==")

    # 核心检查
    skill_ver = check_c1_skill_versions(rep)
    table = parse_module_table(rep)
    check_c3_references(rep)
    check_c4_json(rep)
    if table:
        check_c5_module_refs(rep, table)
    type_enum = load_type_enum(rep)  # C6/P3 共用，单次提取（失败即记 error）
    check_c6_enum_sync(rep, type_enum)

    # 私有检查
    private_on = not args.core and PRIVATE.is_dir()
    if private_on:
        cfg = load_test_config(rep)
        if skill_ver:
            check_p1_versions(rep, skill_ver, cfg)
        else:
            rep.warn("P1 跳过：C1 未取得 skill 版本（先修复 C1）")
        if cfg is not None:
            check_p2_test_structure(rep, cfg)
            check_p3_test_frontmatter(rep, cfg, type_enum)
            check_p4_template_sync(rep, cfg)
        if args.dist:
            check_p5_dist(rep, args.dist)
    else:
        print("[跳过] 私有检查（private/ 不存在或 --core 模式）")
        if args.dist:
            rep.error("P5 --dist 需要在本地（private/ 存在）运行")

    # 汇总输出
    print(f"\n-- 通过 {len(rep.passes)} 项 --")
    for it in rep.passes:
        print(f"  [PASS] {it}")
    if rep.warnings:
        print(f"\n-- 警告 {len(rep.warnings)} 项（不影响退出码）--")
        for it in rep.warnings:
            print(f"  [WARN] {it}")
    if rep.errors:
        print(f"\n-- 失败 {len(rep.errors)} 项 --")
        for it in rep.errors:
            print(f"  [FAIL] {it}")
        print(f"\n结论：校验未通过（{len(rep.errors)} 个 error）")
        return 1
    print(f"\n结论：校验通过（私有检查：{'已启用' if private_on else '已跳过'}）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
