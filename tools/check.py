#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check.py — KnowOps 开发期确定性校验脚本（开发维护用，不随 skill 分发）

位置：发布层 `workspace/tools/`（随公开仓走 CI）；协作层私有件（测试库、
archive 等）在本仓之外，经父目录可达。

用法：
  python tools/check.py                  自动模式：协作层 test/ 测试库可达时含全量检查
  python tools/check.py --core           仅核心检查（CI 模式；协作层不在发布仓内）
  python tools/check.py --dist <version> 附加 dist 打包完整性检查（发布后运行）

退出码：0 = 无 error（warning 不影响）；1 = 存在 error；2 = 环境缺依赖
（argparse 参数错误同为 2）。
依赖：Python 3.10+、PyYAML。文件读写内部强制 UTF-8（规避本机 GBK 默认编码）。

检查项：
  核心（CI 可跑，不依赖协作层）：
    C1  两 skill SKILL.md frontmatter 可解析且 metadata.version 相等
    C2  workflow.md 基础骨架表：编号自 00 连续、末两位固定为 系统/归档
    C3  skill 文档引用的 references/assets/scripts 路径真实存在
    C4  仓库内 JSON 配置可解析
    C5  README 双语与 automation-prompt-template 中模块编号→名称与基础骨架一致
    C6  vault_check.py 内嵌 type 基础枚举与必填表（REQUIRED）
        同 properties.md 声明一致（防双源漂移）
    C7  隐私门禁：跟踪内容禁密钥样式/邮箱/本机绝对路径/手机号；
        .gitignore 必备条目齐全（防测试产物再入库）
  全量（本地，协作层 test/ 测试库可达时启用）：
    P1  版本一致性链 + 开发期文档 frontmatter 分档 + 审计归档护栏
        （CHANGELOG 声明的 AUDIT.md [版本] 章节必须存在）
    P2  测试库 config preferences.modules 登记清单与一级目录匹配
        （基础四模块必须在列、末两位固定、编号不重）
    P3  测试库笔记 frontmatter 可解析且 type 在基础枚举∪登记类型内
        （收件箱豁免；未登记编号目录为警告）
    P4  模板联动：用户手册（03 系统，章节锚点）、变更记录（.config）、
        笔记模板、已移除资产防复现、脚本副本一致
    P5  dist 完整性（--dist）：zip 清单与源目录一致 + 自动化模板附件与源一致
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    print("[FATAL] 缺少 PyYAML：请先 `python -m pip install pyyaml`", file=sys.stderr)
    sys.exit(2)

ROOT = Path(__file__).resolve().parent.parent          # 发布层（workspace/，公开仓）
COLLAB = ROOT.parent                                    # 协作层（私有仓根）
SKILL_KNOWOPS = ROOT / "skills" / "knowops"
SKILL_NOTE = ROOT / "skills" / "everywhere-note"
AUTOMATION_TEMPLATE = ROOT / "skills" / "automation-prompt-template.md"
TEST_VAULT = COLLAB / "test" / "Obsidian测试知识库"

# 模块表末两位固定名称（编号规则：系统倒数第二、归档殿后）
FIXED_TAIL = ["系统", "归档"]

# P5：源目录 junk 文件（与 release.py ZIP_EXCLUDE_NAMES 口径一致，
# 打包排除它们 → src_set 同样排除，避免 --dist 误报）
ZIP_JUNK_NAMES = {".DS_Store", "Thumbs.db", "desktop.ini"}

# P3：允许无 frontmatter 的文件（相对测试库根）
NO_FM_ALLOW = {
    "看板.md",          # 根目录看板嵌入容器（位置固定）
}

# P4：笔记模板清单（v3.0.1 起仅主题文档模板 1 份；摘录长篇模板与示例主题已随
# 模块登记制移除。增删模板改这里——P4 循环与通过文案共用，避免文案漂移）
P4_NOTE_TEMPLATES = ("主题文档模板.md",)

# C7 隐私门禁：敏感模式（仅扫 git 跟踪内容——精确等于将公开的部分）
C7_SECRET_PATTERNS = [
    (r"ghp_[A-Za-z0-9]{20,}", "GitHub personal access token（ghp_）"),
    (r"gho_[A-Za-z0-9]{20,}", "GitHub OAuth token（gho_）"),
    (r"ghu_[A-Za-z0-9]{20,}", "GitHub user-to-server token（ghu_）"),
    (r"ghs_[A-Za-z0-9]{20,}", "GitHub server-to-server token（ghs_）"),
    (r"ghr_[A-Za-z0-9]{20,}", "GitHub refresh token（ghr_）"),
    (r"github_pat_[A-Za-z0-9_]{20,}", "GitHub fine-grained PAT"),
    (r"xox[baprs]-[A-Za-z0-9-]{10,}", "Slack token"),
    (r"(?<![A-Za-z0-9])sk-[A-Za-z0-9\-_]{16,}", "sk- 样式 API key"),
    (r"AKIA[0-9A-Z]{12,}", "AWS Access Key ID"),
    (r"AIza[0-9A-Za-z_\-]{20,}", "Google API key"),
    (r"-----BEGIN [A-Z ]*PRIVATE KEY-----", "私钥内容"),
]
C7_EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
# 邮箱豁免：GitHub 匿名邮箱与示例域
C7_EMAIL_ALLOW_SUFFIX = ("@users.noreply.github.com", "@example.com", "@example.org")
# 本机绝对路径：盘符形态（lookbehind 排除 URL scheme 与 URL 内的盘符片段）
# + UNC 形态（双反斜杠开头的网络路径；lookbehind 排除盘符转义与多反斜杠源码
# 字面量，避免把转义写法误报为 UNC）
C7_ABSPATH_RES = [
    re.compile(r"(?<![A-Za-z0-9/])[A-Za-z]:[\\/]\S*"),
    re.compile(r"(?<![A-Za-z0-9:\\])\\\\[\w.\-]+[\\/][^\s]+"),
]
# 豁免：已文档化的占位示例路径（新增占位符须在此显式登记，可审查）
C7_ABSPATH_ALLOW_PREFIX = ("D:\\MyVault", "C:\\Users\\me\\")
C7_PHONE_RE = re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)")
# .gitignore 必备条目：本地目录绝不入库（缺一条即 error）
C7_REQUIRED_IGNORE = [".workbuddy/", "dist/", "_trash/"]


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
    """解析 workflow.md「基础骨架」表格 → {编号: 名称}。同时执行 C2。"""
    wf_path = SKILL_KNOWOPS / "references" / "workflow.md"
    text = safe_read(rep, wf_path, "C2 workflow.md")
    if text is None:
        return None
    m = re.search(r"## 基础骨架.*?(?=\n## |\Z)", text, re.S)
    if not m:
        rep.error("C2 workflow.md 未找到「## 基础骨架」章节")
        return None
    rows = re.findall(r"^\|\s*(\d{2})\s+([^\|]+?)\s*\|", m.group(0), re.M)
    if not rows:
        rep.error("C2 workflow.md 基础骨架表未解析到任何行")
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
    # C2b：末两位固定（系统倒数第二、归档殿后）
    tail = [table[n] for n in sorted(table, key=int)[-len(FIXED_TAIL):]]
    if tail != FIXED_TAIL:
        rep.error(f"C2 模块表末 {len(FIXED_TAIL)} 位应为 {FIXED_TAIL}，实际 {tail}")
        return None
    # C2c：基础四模块必须在骨架中（收件箱/知识/系统/归档）
    for want in ("收件箱", "知识", "系统", "归档"):
        if want not in table.values():
            rep.error(f"C2 基础骨架缺基础模块「{want}」")
            return None
    rep.ok(f"C2 基础骨架编号连续（{len(table)} 行）、末位固定 {FIXED_TAIL}、"
           "基础四模块在列")
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


def load_vc_defs(rep: Report) -> tuple[frozenset | None, dict[str, list[str]] | None]:
    """从 vault_check.py 提取 TYPE_ENUM / REQUIRED（C6/P3 共用，单一定义点）。
    任一提取失败记 error 并返回 None 分量（绝不静默退化为空集）。"""
    vc_path = SKILL_KNOWOPS / "scripts" / "vault_check.py"
    if not vc_path.is_file():
        rep.error("vault_check.py 不存在：skills/knowops/scripts/vault_check.py")
        return None, None
    vc = safe_read(rep, vc_path, "vault_check.py")
    if vc is None:
        return None, None
    m = re.search(r"TYPE_ENUM\s*=\s*frozenset\(\s*\{([^}]*)\}", vc, re.S)
    if not m:
        rep.error("vault_check.py 未找到 TYPE_ENUM 定义（正则失配，"
                  "枚举相关检查全部失效，请先修复）")
        return None, None
    enum = frozenset(re.findall(r"[\"'](\w+)[\"']", m.group(1)))

    m2 = re.search(r"REQUIRED\s*=\s*\{(.*?)\n\}", vc, re.S)
    if not m2:
        rep.error("vault_check.py 未找到 REQUIRED 定义（正则失配，"
                  "必填表检查失效，请先修复）")
        return enum, None
    required: dict[str, list[str]] = {}
    for t, attrs in re.findall(r'"(\w+)":\s*\[([^\]]*)\]', m2.group(1)):
        required[t] = re.findall(r'"(\w+)"', attrs)
    return enum, required


def check_c6_required_sync(rep: Report, required: dict[str, list[str]] | None) -> None:
    """C6b：vault_check.py REQUIRED 与 properties.md「必填与自由」表一致
    （表格为文档侧权威定义；扩展模块必填归用户手册，脚本不内嵌）。"""
    if required is None:
        return  # 提取失败已在 load_vc_defs 记 error
    props_path = SKILL_KNOWOPS / "references" / "properties.md"
    if not props_path.is_file():
        rep.error("C6 properties.md 不存在")
        return
    props = safe_read(rep, props_path, "C6 properties.md")
    if props is None:
        return

    # 行扫描定位「| type | 必填属性…」表头，收集后续表格行（遇非表格行停止）
    rows: list[tuple[str, str]] = []
    in_table = False
    for ln in props.splitlines():
        if re.match(r"^\|\s*type\s*\|\s*必填属性", ln):
            in_table = True
            continue
        if in_table:
            if not ln.strip().startswith("|"):
                break
            cells = [c.strip() for c in ln.strip().strip("|").split("|")]
            if len(cells) < 2 or set(cells[0]) <= set("-: "):
                continue  # 分隔行
            rows.append((cells[0], cells[1]))
    if not rows:
        rep.error("C6 properties.md 未找到「必填与自由」必填表（| type | 必填属性 |）")
        return

    parsed: dict[str, tuple[set, set]] = {}
    for t, cell in rows:
        base = cell.split("；")[0].split("（")[0]
        toks = set(re.findall(r"`(\w+)`", base))
        extra_toks: set = set()
        m = re.search(r"另加\s*(.+)$", cell)
        if m:
            extra_toks = set(re.findall(r"`(\w+)`", m.group(1)))
        parsed[t] = (toks, extra_toks)

    problems = []
    unknown = set(required) - set(parsed)
    if unknown:
        problems.append(f"vault_check REQUIRED 中的类型在必填表缺失：{sorted(unknown)}")
    for t in sorted(set(required) | set(parsed)):
        if t in unknown:
            continue
        toks, extra_toks = parsed[t]
        if t not in required:
            if toks != {"type"}:
                problems.append(f"type {t} 必填表应仅含 type（vault_check 无此必填），"
                                f"实际 {sorted(toks)}")
            continue
        if set(required[t]) != toks:
            problems.append(f"type {t} 必填属性漂移：vault_check {sorted(required[t])}"
                            f" vs properties {sorted(toks)}")
    if problems:
        for it in problems:
            rep.error(f"C6 必填表双源漂移：{it}")
    else:
        rep.ok(f"C6 必填表与 vault_check REQUIRED 一致（{len(required)} 类）")


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


def _c7_tracked_files(rep: Report) -> list[Path]:
    """git 跟踪文件清单（= 将被公开的精确集合）。git 不可用时退化为全盘扫描
    （排除 .git/、dist/、_trash/、.workbuddy/ 目录），保证门禁不因环境缺失而
    失效。"""
    try:
        out = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT,
                             capture_output=True, check=True).stdout.decode("utf-8")
        return [ROOT / name for name in out.split("\0") if name]
    except (OSError, subprocess.CalledProcessError, UnicodeDecodeError) as e:
        rep.warn(f"C7 git 跟踪清单获取失败（{e}），退化为全盘扫描")
        skip_dirs = {".git", "dist", "_trash", ".workbuddy"}
        return [p for p in ROOT.rglob("*")
                if p.is_file()
                and not (set(p.parts[:-1]) & skip_dirs)]


def check_c7_privacy(rep: Report) -> None:
    """隐私门禁：跟踪内容禁密钥样式/邮箱/本机绝对路径/手机号；
    .gitignore 必备条目齐全（2026-08-03 .test-env 误入库事故的机制封堵）。"""
    hits: list[str] = []
    scanned = skipped = 0
    for p in _c7_tracked_files(rep):
        try:
            text = read_text(p)
        except (OSError, ValueError):
            skipped += 1
            continue  # 二进制/不可解码文件不参与文本模式检查
        scanned += 1
        rel = p.relative_to(ROOT).as_posix()
        for i, line in enumerate(text.splitlines(), 1):
            for pat, label in C7_SECRET_PATTERNS:
                if re.search(pat, line):
                    hits.append(f"{rel}:{i} 含{label}")
            for m in C7_EMAIL_RE.finditer(line):
                if not m.group(0).lower().endswith(C7_EMAIL_ALLOW_SUFFIX):
                    hits.append(f"{rel}:{i} 含邮箱 {m.group(0)}")
            for rex in C7_ABSPATH_RES:
                for m in rex.finditer(line):
                    # 归一化转义写法（源码/JSON 中的双反斜杠）与正斜杠分隔符，
                    # 再比对豁免前缀
                    norm = m.group(0).replace("\\\\", "\\").replace("/", "\\")
                    if not norm.startswith(C7_ABSPATH_ALLOW_PREFIX):
                        hits.append(f"{rel}:{i} 含本机绝对路径 {norm[:60]!r}")
            if C7_PHONE_RE.search(line):
                hits.append(f"{rel}:{i} 疑似国内手机号")
    gi = safe_read(rep, ROOT / ".gitignore", "C7 .gitignore")
    if gi is not None:
        entries = {ln.strip() for ln in gi.splitlines()}
        for req in C7_REQUIRED_IGNORE:
            if req not in entries:
                hits.append(f".gitignore 缺必备条目 {req}")
    if hits:
        for h in hits:
            rep.error(f"C7 {h}")
    else:
        rep.ok(f"C7 隐私门禁通过（扫描 {scanned} 份跟踪文本，跳过二进制 {skipped} 份）")


# ---------------------------------------------------------------------------
# 全量检查（协作层 test/ 测试库可达时）
# ---------------------------------------------------------------------------

def load_test_config(rep: Report) -> dict | None:
    cfg_path = TEST_VAULT / ".config" / "knowops.config.json"
    try:
        return json.loads(read_text(cfg_path))
    except (OSError, json.JSONDecodeError) as e:
        rep.error(f"P1 测试库配置读取失败：{e}")
        return None


def check_p1_versions(rep: Report, skill_ver: str, cfg: dict | None) -> None:
    # CHANGELOG 顶部条目与历史版本集合（发布仓根，公开）
    cl = safe_read(rep, ROOT / "CHANGELOG.md", "P1 CHANGELOG.md")
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

    # 审计归档护栏：CHANGELOG 条目声明「归档 dev/AUDIT.md [版本]」的，AUDIT.md
    # 必须存在对应章节（v3.0.3 起，防「声明归档但实际漏写」复发）。分隔符放宽
    # 到空白与常用全半角标点（如「AUDIT.md（[3.0.2] 补记…）」），中间含其他
    # 字符的散文形态不匹配、不误报。
    aud_path = COLLAB / "archive" / "audit" / "AUDIT.md"
    declared = sorted(set(re.findall(
        r"AUDIT\.md[\s（(：:、，,]*\[(\d+\.\d+\.\d+)\]", cl)))
    aud_ok = True
    if declared:
        if not aud_path.is_file():
            rep.error(f"P1 CHANGELOG 声明审计归档 archive/audit/AUDIT.md，但该文件不存在"
                      f"（声明版本：{declared}）")
            aud_ok = False
        else:
            aud_text = safe_read(rep, aud_path, "P1 AUDIT.md")
            if aud_text is None:
                aud_ok = False  # 读取失败已记 error，不级联重复比对
            else:
                aud_sections = set(re.findall(
                    r"^## \[(\d+\.\d+\.\d+)\]", aud_text, re.M))
                for aud_ver in [v for v in declared if v not in aud_sections]:
                    rep.error(f"P1 CHANGELOG 声明审计归档 archive/audit/AUDIT.md "
                              f"[{aud_ver}]，但 AUDIT.md 无对应章节")
                    aud_ok = False
    if aud_ok:
        rep.ok(f"P1 审计归档护栏通过（{len(declared)} 处声明）")

    # 严格分档（每版必更）：协作层总纲 AGENTS.md
    for label, path in (("AGENTS.md（总纲）", COLLAB / "AGENTS.md"),):
        fm = read_fm(rep, path, f"P1 {label}")
        if fm is None:
            continue  # 读取/解析失败已记 error
        v = str(fm.get("version", ""))
        if v != skill_ver:
            rep.error(f"P1 {label} version={v or '缺失'} ≠ {skill_ver}")
        else:
            rep.ok(f"P1 {label} version = {v}")

    # 滞后分档（须为 CHANGELOG 历史版本；本次无相关改动的版本允许滞后）：
    # design.md、AUDIT.md（审计档案，首次审计建立前允许不存在）
    for label, path in (("design.md", COLLAB / "context" / "design" / "design.md"),
                        ("AUDIT.md", COLLAB / "archive" / "audit" / "AUDIT.md")):
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
    mods = prefs.get("modules")
    if not isinstance(mods, list) or not mods:
        rep.error("P2 preferences 缺 modules 模块清单（应为非空数组）")
        mods = []
    expected: dict[int, str] = {}
    for m in mods:
        if not isinstance(m, dict):
            rep.error("P2 preferences.modules 存在非对象元素")
            continue
        d = str(m.get("dir", ""))
        mm = re.match(r"^(\d{2})\s+(.+)$", d)
        if not mm:
            rep.error(f"P2 modules dir={d!r} 不符合「NN 名称」格式")
            continue
        num = int(mm.group(1))
        if num in expected:
            rep.error(f"P2 modules 编号 {num:02d} 重复"
                      f"（{expected[num]} 与 {mm.group(2)}）")
            continue
        expected[num] = mm.group(2)
        if not str(m.get("type", "")):
            rep.error(f"P2 modules dir={d!r} 缺 type")

    # 重复 type（如两个 type=capture 会让收件箱豁免判定歧义）
    types = [str(m.get("type")) for m in mods
             if isinstance(m, dict) and m.get("type")]
    dup_types = sorted({t for t in types if types.count(t) > 1})
    if dup_types:
        rep.error(f"P2 modules 重复 type：{dup_types}")

    # 基础四模块必须在登记清单中
    for want in ("收件箱", "知识", "系统", "归档"):
        if want not in expected.values():
            rep.error(f"P2 modules 缺基础模块「{want}」")

    # 末两位固定：编号为最大两个连续值，且名称与 FIXED_TAIL 逐位对应
    if len(expected) >= len(FIXED_TAIL):
        mx = max(expected)
        for off, want in zip(range(len(FIXED_TAIL) - 1, -1, -1), FIXED_TAIL):
            got = expected.get(mx - off)
            if got != want:
                rep.error(f"P2 倒数第 {off + 1} 位（编号 {mx - off:02d}）"
                          f"应为「{want}」，实际「{got}」")

    # 实际编号目录 ⊆ expected（未登记目录允许存在——运行期只警告，此处同样警告）
    actual: dict[int, str] = {}
    for d in TEST_VAULT.iterdir():
        if d.name.startswith(".") or not d.is_dir():
            continue
        mm = re.match(r"^(\d{2})\s+(.+)$", d.name)
        if mm:
            actual[int(mm.group(1))] = mm.group(2)
    problems = []
    for num, name in sorted(actual.items()):
        if num not in expected:
            rep.warn(f"P2 目录「{num:02d} {name}」未登记（不在 config "
                     "preferences.modules 中）")
        elif expected[num] != name:
            problems.append(f"目录「{num:02d} {name}」与 config 值「{expected[num]}」不一致")
    if problems:
        for it in problems:
            rep.error(f"P2 {it}")
    else:
        rep.ok(f"P2 测试库 modules 登记清单与一级目录匹配"
               f"（登记 {len(expected)} 个、在场 {len(actual)} 个编号目录）")


def check_p3_test_frontmatter(rep: Report, cfg: dict,
                              type_enum: frozenset | None) -> None:
    if type_enum is None:
        rep.warn("P3 跳过：TYPE_ENUM 提取失败（见前述 error）")
        return

    prefs = cfg.get("preferences", {}) if isinstance(cfg.get("preferences"), dict) else {}
    mods = prefs.get("modules", []) if isinstance(prefs.get("modules"), list) else []

    def dir_of(t: str) -> str:
        for m in mods:
            if isinstance(m, dict) and m.get("type") == t:
                return str(m.get("dir", ""))
        return {"capture": "00 收件箱", "system": "03 系统"}.get(t, "")

    inbox_dir = dir_of("capture")
    system_dir = dir_of("system")
    # 允许的 type = 基础枚举 ∪ 登记模块类型（扩展模块如 excerpt 随登记放行）
    allowed = set(type_enum) | {str(m.get("type")) for m in mods
                                if isinstance(m, dict) and m.get("type")}

    no_fm, bad_fm, bad_type = [], [], []
    count = 0
    for p in TEST_VAULT.rglob("*.md"):
        rel = p.relative_to(TEST_VAULT).as_posix()
        if any(part.startswith(".") for part in p.relative_to(TEST_VAULT).parts):
            continue  # 隐藏目录（.config/.obsidian 等）不扫
        if rel == inbox_dir or rel.startswith(inbox_dir + "/"):
            continue  # 收件箱校验豁免区（零门槛捕获区）
        count += 1
        try:
            fm, _ = parse_frontmatter(read_text(p))
        except (OSError, ValueError) as e:
            bad_fm.append(f"{rel}：{e}")
            continue
        if fm is None:
            # 豁免：根目录看板容器、系统模块内文件（用户文档/模板/日记）
            if p.name in NO_FM_ALLOW or rel.startswith(system_dir + "/"):
                continue
            no_fm.append(rel)
            continue
        t = fm.get("type")
        if t is None:
            no_fm.append(f"{rel}（有 frontmatter 但无 type）")
        elif str(t) not in allowed:
            bad_type.append(f"{rel}：type={t}")
    for it in bad_fm:
        rep.error(f"P3 frontmatter 解析失败：{it}")
    for it in bad_type:
        rep.error(f"P3 type 越界（不在基础枚举∪登记类型内）：{it}")
    if no_fm:
        for it in no_fm:
            rep.warn(f"P3 无 frontmatter：{it}")
    rep.ok(f"P3 测试库笔记扫描完成（{count} 篇；error {len(bad_fm) + len(bad_type)}，"
           f"无 frontmatter 警告 {len(no_fm)}）")


def check_p4_template_sync(rep: Report, cfg: dict) -> None:
    prefs = cfg.get("preferences")
    if not isinstance(prefs, dict):
        prefs = {}
    mods = prefs.get("modules", []) if isinstance(prefs.get("modules"), list) else []

    def dir_of(t: str, fallback: str) -> str:
        for m in mods:
            if isinstance(m, dict) and m.get("type") == t:
                return str(m.get("dir", ""))
        return fallback

    system_dir = dir_of("system", "03 系统")
    knowledge_dir = dir_of("knowledge", "01 知识")
    tpl_dir = SKILL_KNOWOPS / "assets" / "system-manage"
    tgt_dir = TEST_VAULT / system_dir
    problems = []
    # 用户手册：v3.0.2 起初始化会把实际目录名/插件规则填入副本，不再逐字比对；
    # 改为章节锚点校验——模板的全部「## 」章节标题必须在副本中逐一存在
    # （副本是"已初始化"形态，章节集合不得缺失或改名）
    manual = "用户手册.md"
    tpl, tgt = tpl_dir / manual, tgt_dir / manual
    if not tpl.is_file():
        problems.append(f"模板缺失：assets/system-manage/{manual}")
    if not tgt.is_file():
        problems.append(f"测试库副本缺失：{system_dir}/{manual}")
    if tpl.is_file() and tgt.is_file():
        try:
            tpl_lines = read_text(tpl).splitlines()
            tgt_lines = read_text(tgt).splitlines()
        except (OSError, ValueError) as e:
            problems.append(f"模板/副本读取失败（{e}）：{manual}")
        else:
            tpl_heads = [ln.strip() for ln in tpl_lines
                         if ln.startswith("## ")]
            tgt_set = {ln.strip() for ln in tgt_lines if ln.startswith("## ")}
            for h in tpl_heads:
                if h not in tgt_set:
                    problems.append(f"手册副本缺章节「{h}」"
                                    f"（模板章节须逐一存在）")
    vc = "变更记录.md"
    tpl, tgt = tpl_dir / vc, TEST_VAULT / ".config" / vc
    if not tpl.is_file():
        problems.append(f"变更记录模板缺失：assets/system-manage/{vc}")
    if not tgt.is_file():
        problems.append(f"测试库副本缺失：.config/{vc}")
    if (tgt_dir / vc).is_file():
        problems.append(f"变更记录仍残留在 {system_dir}/{vc}"
                        f"（v2.0.3 起应为 .config/{vc}）")
    if tpl.is_file() and tgt.is_file():
        # 变更记录是活文档：副本初始化自模板后持续追加历史条目，且模板的初始
        # 示例条目会随版本更新——历史条目不回溯改写。只校验标题一致性。
        try:
            tpl_title = read_text(tpl).splitlines()[0].strip()
        except (OSError, ValueError, IndexError) as e:
            problems.append(f"assets/system-manage/{vc} 读取失败（{e}）")
        else:
            try:
                tgt_title = read_text(tgt).splitlines()[0].strip()
            except (OSError, ValueError, IndexError) as e:
                problems.append(f".config/{vc} 读取失败（{e}）")
            else:
                if tpl_title != tgt_title:
                    problems.append(f".config/{vc} 副本标题与模板不一致"
                                    f"（{tgt_title!r} ≠ {tpl_title!r}）")

    # 笔记模板：源文件存在 + 测试库 系统/模板/ 副本逐字一致（v3.0.1 起仅
    # 主题文档模板 1 份；摘录长篇模板与示例主题已随模块登记制移除）
    note_tpl_src = SKILL_KNOWOPS / "assets" / "templates"
    note_tpl_tgt = tgt_dir / "模板"
    for name in P4_NOTE_TEMPLATES:
        src, dst = note_tpl_src / name, note_tpl_tgt / name
        if not src.is_file():
            problems.append(f"笔记模板缺失：assets/templates/{name}")
            continue
        if not dst.is_file():
            problems.append(f"测试库模板副本缺失：{system_dir}/模板/{name}")
            continue
        try:
            if read_text(src) != read_text(dst):
                problems.append(f"模板副本与源不一致：{system_dir}/模板/{name}")
        except (OSError, ValueError) as e:
            problems.append(f"模板副本读取失败（{e}）：{name}")
    for legacy_rel in ("assets/knowledge-example",
                       "assets/templates/摘录长篇模板.md",
                       "assets/agent-rules.md"):
        if (SKILL_KNOWOPS / legacy_rel).exists():
            problems.append(f"已移除的资产仍存在（v3.0.1/v3.0.2）：{legacy_rel}")

    # 测试库知识模块至少有一份主题文档（示例主题已移除，其余为真实测试数据）
    kdir = TEST_VAULT / knowledge_dir
    if not kdir.is_dir():
        problems.append(f"测试库知识模块缺失：{knowledge_dir}/")
    elif not any(kdir.rglob("*.md")):
        problems.append(f"测试库知识模块无主题文档：{knowledge_dir}/")

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
        rep.ok(f"P4 模板联动一致（用户手册锚点 + 变更记录（.config）+ "
               f"笔记模板 {len(P4_NOTE_TEMPLATES)} 份 + 已移除资产防复现"
               " + 脚本副本）")


def check_p5_dist(rep: Report, version: str) -> None:
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        rep.error(f"P5 --dist 版本号格式非法：{version!r}（应为 X.Y.Z）")
        return
    dist_dir = ROOT / "dist" / version
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
                               and p.suffix != ".pyc"
                               and p.name not in ZIP_JUNK_NAMES}
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

    # 自动化模板附件：存在且与源一致（v3.0.1 起随 Release 分发；旧版本 dist
    # 无此附件，按版本门控避免追溯性误报）
    if tuple(int(x) for x in version.split(".")) >= (3, 0, 1):
        automation = dist_dir / f"automation-prompt-template-v{version}.md"
        if not automation.is_file():
            rep.error(f"P5 缺少自动化模板附件：{automation.name}")
        else:
            a_text = safe_read(rep, automation, f"P5 {automation.name}")
            s_text = safe_read(rep, AUTOMATION_TEMPLATE,
                               "P5 skills/automation-prompt-template.md")
            if a_text is not None and s_text is not None:
                if a_text != s_text:
                    rep.error("P5 自动化模板附件与源文件不一致")
                else:
                    rep.ok(f"P5 {automation.name} 完整（与源一致）")


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
    vc_enum, vc_required = load_vc_defs(rep)  # C6/P3 共用，单次提取
    check_c6_enum_sync(rep, vc_enum)
    check_c6_required_sync(rep, vc_required)
    check_c7_privacy(rep)

    # 全量检查（协作层 test/ 测试库可达时）
    full_on = not args.core and TEST_VAULT.is_dir()
    if full_on:
        cfg = load_test_config(rep)
        if skill_ver:
            check_p1_versions(rep, skill_ver, cfg)
        else:
            rep.warn("P1 跳过：C1 未取得 skill 版本（先修复 C1）")
        if cfg is not None:
            check_p2_test_structure(rep, cfg)
            check_p3_test_frontmatter(rep, cfg, vc_enum)
            check_p4_template_sync(rep, cfg)
        if args.dist:
            check_p5_dist(rep, args.dist)
    else:
        print("[跳过] 全量检查（协作层 test/ 测试库不可达，或 --core 模式）")
        if args.dist:
            rep.error("P5 --dist 需要在本地（协作层 test/ 测试库可达）运行")

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
    print(f"\n结论：校验通过（全量检查：{'已启用' if full_on else '已跳过'}）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
