# KnowOps: Obsidian Knowledge Management Skills

KnowOps is a set of **Obsidian knowledge-management skills** for AI agents: two skills
that keep your knowledge base well organized — **a desktop entry point + portable
capture**, installed by device type and designed to work together.

## What is this

When managing a personal knowledge base in Obsidian, an agent needs two things:
*how the content should be organized* (what modules the knowledge base has, how inbox
items are settled, along which axis knowledge accumulates), and *how to operate
Obsidian* (read/write notes via the official CLI, respect delete red lines). This repo
puts both into one desktop skill (`knowops`) that loads its references on demand, plus
a portable skill (`everywhere-note`) for quick capture on phones/tablets.

The base only keeps content that has **no better home**: todos belong in a todo app,
project files belong in project folders, executable scripts and templates belong in
their own repos — none of those enter the base. What lives here: excerpts, validated
experience, and half-formed thoughts.

| Skill | Role | One-liner |
|---|---|---|
| **knowops** | Desktop entry point | "How the KB should be organized + how to operate Obsidian", loaded progressively via references; works alone |
| **everywhere-note** | Portable capture | Capture with @ on the phone, get standard md + a 22:00 reminder |

## Features

- **Generic foundation + registered extension modules**: the skill only presets the
  base skeleton — `00 收件箱` (not yet thought through) / `01 知识` (validated) /
  `03 系统` (the base's own traces and docs) / `04 归档` (no longer active), plus a
  root-level `看板.md` as the one-screen overview; 系统 and 归档 stay fixed as the
  last two. **Adding a module = create a folder in your vault**: the agent asks you
  for the rules, writes them into the user manual, and follows them from then on —
  your base grows your way, no skill release required;
- **Single source of truth**: what each module keeps, how things get ingested,
  classified and named — all of it lives only in the "模块规则" (module rules)
  chapter of the in-vault `03 系统/用户手册.md` (user-visible and editable, a
  must-read for the agent); the config only keeps a machine-readable index — no
  rule copies, no drift;
- **Inbox: easy in, strict out**: flat layout, numbered filenames, no subfolders; you
  may drop in files with no formatting at all — rules bind the agent, which fills in
  everything at settlement time; the inbox is exempt from structural checks;
- **Knowledge by topic, verbatim quotes**: one document per topic, entries organized
  in sections; entry bodies **keep your original words intact** (the agent never
  rewrites or compresses them; extra explanations are added only with your consent);
  when a section passes about 30 entries a split is proposed — monolith first, split
  only when it bursts;
- **Excerpts = the preset extension module**: onboarding asks whether to enable it;
  long excerpts get one note per work, short quotes aggregate by category (split
  into numbered files past 100 entries); every rule is registered in the user manual
  and the whole module can be retired;
- **Write-audit loop**: after each batch of content written by the agent (ingest /
  settlement / archive / delete), a `待审阅-<date>.md` receipt is left in the inbox
  (visible on the dashboard, deleted after review) and the diary gets a detailed
  entry;
- **Diary split into "用户 / agent" chapters**: one file per day (following
  Obsidian's Daily notes rules, kept by year under `03 系统/日记/`); agent actions
  are logged by type in the agent chapter, and your manual edits are **back-filled**
  by the agent from file history and git (with the inference noted) — who did what
  is always answerable;
- **Obsidian templates**: `03 系统/模板/` ships the topic-document template for
  use with Obsidian's core Templates plugin;
- **Progressive loading**: knowops' SKILL.md only carries the trigger, loading rules
  and common red lines; workflow.md, redlines.md and desktop-ingest.md are read on
  demand;
- **Portable capture & unified ingest**: @ everywhere-note on a phone/portable device and dictate directly; it generates KB-compliant markdown (a file when supported) and sets a 22:00 reminder; back at the desktop, knowops parses the captures and writes them into `00 收件箱`; the phone only needs this one skill and no transfer channel; the portable skill embeds no desktop-base structure, so desktop restructuring never forces a reinstall;
- **GitHub staging repo sync (optional)**: you designate a GitHub staging repo; on the phone, when GitHub capability is available (gh CLI / git / GitHub MCP etc.), entries are uploaded into this KB's folder in the staging repo; on the desktop, "ingest" pulls new entries into `00 收件箱` (numbered filenames) and archives the source files into `<KB-name>/归档/<date>/` in the staging repo (split by ingest date); multiple KBs can share one staging repo without conflicts;
- **Dashboard**: root `看板.md` embeds the live views from `03 系统/看板.base`
  (inbox pending, knowledge recent); views follow module registration/retirement;
- **Archive**: `04 归档` uses zero-padded Chinese date folders;
- **Canvas is free space**: canvases you create are never managed, checked or exported;
- **Plugin integration rules**: at onboarding, plugins are scanned and the user
  confirms how they integrate; rules are written to the user manual's "agent
  约束" chapter (same book as the module rules, viewable and editable anytime),
  read before every mutating operation and executed afterwards (e.g., version
  commit first, then cloud sync);
- **Config-driven, version-following**: module index and preferences live in
  `.config/knowops.config.json` (single vault); schema version follows the skill version;
- **Data-safety red lines**: delete always goes to the system trash and stays
  recoverable; high-risk changes (mass file impact, permanent deletes) ask for
  consent first, while low-risk ones run first and are logged afterwards; never run
  `git init` for the user; similarity check before creating; user-provided info is
  authoritative (original words never rewritten or compressed); read back and verify
  after important writes.

## Installation

Install by device type — **do not install both skills on the same device** (they
would compete for the same triggers):

| Device | Install |
|---|---|
| Desktop (can operate the knowledge base) | `skills/knowops/` |
| Phone/tablet/portable device | `skills/everywhere-note/` |

Copy the matching directory into your agent's **user-level skill directory** (location
varies by platform; see your platform's skill installation docs; typically
`~/.<platform>/skills/`), or clone this repo:

```sh
git clone https://github.com/The-Daybreaker/KnowOps.git
# then copy the matching directory under skills/ into the user-level skill directory
```

> You can also download the `<skill>-vX.Y.Z.zip` package from GitHub Releases
> (generated on every release; the skill directory is the zip root).

> **Dependencies**: knowops delegates concrete syntax and commands to the official
> tool skills (obsidian-cli / obsidian-markdown / obsidian-bases / json-canvas /
> defuddle) from the official Obsidian skills repository
> [kepano/obsidian-skills](https://github.com/kepano/obsidian-skills); install them
> separately (see "Related projects"). If they are missing, knowops falls back to
> the official Obsidian docs.

## Quick start

1. When a desktop task triggers `knowops`, read the references per the loading rules
   in SKILL.md:
   - Recording/managing/organizing content → read `references/workflow.md` first,
     and run the **onboarding wizard** when needed;
   - Obsidian operations → read `references/redlines.md` first;
   - Ingesting captured content/files → read `references/desktop-ingest.md`,
     then load `references/workflow.md` and `references/redlines.md` per its
     header note.
2. The onboarding wizard confirms step by step: vault path & name, the four base
   modules (lazy loading: inbox/archive appear on first write), whether to enable
   the excerpt module (the preset extension; skippable), optional GitHub staging
   repo sync, plugin integration rules (written to the manual's "agent 约束"
   chapter), the `03 系统` user manual and templates (the manual's "模块规则"
   chapter is what the agent executes against), the root dashboard, and the
   Daily notes diary setup; config lives in the vault's hidden `.config/` directory,
   and the HTML mirror export is enabled by default
   (`<vault>/.config/HTML-Export/`).
3. Load the tool skills (CLI / Markdown / Bases / Canvas / web extraction) on
   demand when their capability is needed.

Usage examples:

| You say | The agent does |
|---|---|
| Phone: "log: XXX" | everywhere-note generates a KB-compliant md entry and sets a 22:00 reminder; uploads to the staging repo when configured and GitHub capability is available |
| "Ingest today's phone captures" | knowops loads desktop-ingest.md: user-provided content first; when no content is provided and a staging repo is configured, new entries are pulled from GitHub, written into `00 收件箱` with numbered filenames, and the sources are archived to the staging repo |
| "Log this: ..." | Writes it to `00 收件箱/` (numbered, with properties & tags) |
| "Excerpt: 将进酒..." | Ingested per the excerpt chapter of the user manual: long works get a dedicated note (named by work title), short quotes are appended to the matching category file |
| "File this experience under the topic 架构设计" | Merges it into the matching section of the topic document under `01 知识/` (your original words kept verbatim) |
| "Review the inbox" | Judges each item against the manual's module rules: destination module / archive / delete / keep |
| "I made a folder called 读书 for book notes" | The agent asks for the module's ingest & classification rules → writes them into the manual's "模块规则" chapter → follows them from then on |
| "Archive this note" | Moves it to `04 归档/<today>/` |

## Layout

```
KnowOps/
├── README.md / README.en.md / LICENSE / .gitignore / AGENTS.md
├── tools/                        # dev-time validation script (check.py)
├── .github/workflows/            # CI (core checks on push/PR)
└── skills/
    ├── knowops/                     # Desktop entry point
    │   ├── SKILL.md                 # trigger + loading rules + common red lines
    │   ├── references/
    │   │   ├── workflow.md          # workflow spec (two gates/module flows/diary/post-op)
    │   │   ├── init-config.md       # onboarding/GitHub staging/plugin integration/config & HTML export/scripts
    │   │   ├── properties.md        # properties/naming/layout/lifecycle design
    │   │   ├── redlines.md          # execution red lines + direct-write exceptions
    │   │   └── desktop-ingest.md    # captured content / GitHub staging pull → 00 收件箱
    │   ├── scripts/                 # html_export / vault_check
    │   └── assets/
    │       ├── system-manage/       # vault doc templates (user manual→03 系统; change log→.config)
    │       ├── templates/           # note template (topic document, for the Obsidian Templates plugin)
    │       └── html-export.json     # HTML export range config template
    ├── everywhere-note/             # Portable capture (optional GitHub staging sync; single-file)
    │   └── SKILL.md
    └── automation-prompt-template.md  # automation prompt template for scheduled ingest
```

## Related projects

The tool skills are installed copies from the **official Obsidian skills
repository**, updatable from upstream:

- [kepano/obsidian-skills](https://github.com/kepano/obsidian-skills) — Official
  Obsidian agent skills (obsidian-cli / obsidian-markdown / obsidian-bases /
  json-canvas / defuddle)
- [kepano/defuddle](https://github.com/kepano/defuddle) — web page content
  extraction library

## License

MIT License, see [LICENSE](LICENSE).
