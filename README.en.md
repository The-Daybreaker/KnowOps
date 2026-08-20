# KnowOps: Obsidian Knowledge Management Skills

KnowOps is a set of **Obsidian knowledge-management skills** for AI agents: two skills
that keep your knowledge base well organized — **a desktop entry point + portable
capture**, installed by device type and designed to work together.

## What is this

When managing a personal knowledge base in Obsidian (inbox capture, question
tracking, knowledge distillation, projects, schedule, todos, dashboard, archive...),
an agent needs two things: *how the content should be organized* (what modules the
knowledge base has, how an inbox item is reviewed and distilled, how a question
moves from "unresolved" to "distilled", how knowledge differs from projects), and
*how to operate Obsidian* (read/write notes via the official CLI, respect delete
red lines). This repo puts both into one desktop skill (`knowops`) that loads its
references on demand, plus a portable skill (`everywhere-note`) for quick capture
on phones/tablets.

| Skill | Role | One-liner |
|---|---|---|
| **knowops** | Desktop entry point | "How the KB should be organized + how to operate Obsidian", loaded progressively via references; works alone |
| **everywhere-note** | Portable capture | Capture with @ on the phone, get standard md + a 22:00 reminder |

## Features

- **Inbox capture & review**: short, fragmented thoughts, inspirations and unclear
  items go to `00 收件箱` (随手记 / 灵感 / 待整理内容 / 摘录) by default; during
  review, each item is distilled, deleted or archived based on how it will be used;
- **Excerpt system**: long excerpts (poetry, classical prose) get one note per work
  (named by work title, with author / dynasty / source properties); short quotes
  (famous sayings, aphorisms, personal reflections) are aggregated by category
  (split into numbered files past 100 entries); desktop "excerpt: ..." goes
  straight in, portable excerpts settle via inbox review;
- **Progressive loading**: knowops' SKILL.md only carries the trigger, loading rules
  and common red lines; workflow.md, redlines.md and desktop-ingest.md are read on
  demand;
- **Portable capture & unified ingest**: @ everywhere-note on a phone/portable device and dictate directly; it generates KB-compliant markdown (a file when supported) and sets a 22:00 reminder; back at the desktop, knowops parses the captures and writes them into `00 收件箱`; the phone only needs this one skill and no transfer channel;
- **GitHub staging repo sync (optional)**: you designate a GitHub staging repo; on the phone, when GitHub capability is available (gh CLI / git / GitHub MCP etc.), entries are uploaded into this KB's folder in the staging repo; on the desktop, "ingest" pulls new entries into `00 收件箱` and archives the source files into `<KB-name>/归档/<date>/` in the staging repo (split by ingest date); multiple KBs can share one staging repo without conflicts;
- **Full question lifecycle**: unresolved → in progress → resolved → distilled;
  the original question moves to `已沉淀` and keeps **bidirectional links** to the
  knowledge note;
- **Knowledge distillation**: grouped by type (概念原理 / 经验方法 / 方案 / 案例),
  domain subfolders created **only when used**, growth-triggered splitting
  (<50 keep flat / near 50 add a domain level after confirmation / >150 evaluate third level);
- **Assets & standards**: templates / workflows for reuse; principles / standards /
  checklists for compliance;
- **Project system**: active / completed / retrospective, with a six-file project
  template;
- **Schedule + automated reminders**: enter with one sentence ("project review at
  3pm Friday"), reminders auto-created when explicit time signals are present;
- **Two-way task sync**: task notes are the dashboard data source; TODO.md is the
  human quick checklist; both mirror each other and stay in sync;
- **Dashboard created by default**: Bases-driven real-time aggregation; views are
  extensible on request;
- **Archive & system management**: `08 归档` uses zero-padded Chinese date folders;
  `09 系统管理` holds architecture, classification, naming, frontmatter, agent
  change log and user manual; dashboard, archive and system management are fixed
  as the last three modules;
- **Plugin integration rules**: at onboarding, plugins are scanned and the user
  confirms how they integrate; rules are written to hidden config `.config/agent-rules.md`,
  read before every mutating operation and executed afterwards (e.g., version
  commit first, then cloud sync);
- **Config-driven, version-following**: directories and preferences live in `.config/knowops.config.json` (single vault);
  schema version follows the skill version;
- **Data-safety red lines**: delete always goes to the system trash and stays
  recoverable; high-risk changes (mass file impact, permanent deletes) ask for
  consent first, while low-risk ones run first and are logged afterwards; never run
  `git init` for the user; similarity check before creating; user-provided info is
  authoritative; read back and verify after important writes.

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
   - Ingesting captured content/files → read `references/desktop-ingest.md`.
2. The onboarding wizard confirms step by step: vault path & name, the 00–09
   ten-module structure, optional GitHub staging repo sync, plugin integration
   rules (written to `.config/agent-rules.md`), the `09 系统管理` template set,
   the `07 看板` dashboard, and the HTML mirror export (enabled by default).
3. Load the tool skills (CLI / Markdown / Bases / Canvas / web extraction) on
   demand when their capability is needed.

Usage examples:

| You say | The agent does |
|---|---|
| Phone: "log: XXX" | everywhere-note generates a KB-compliant md entry and sets a 22:00 reminder; uploads to the staging repo when configured and GitHub capability is available |
| "Ingest today's phone captures" | knowops loads desktop-ingest.md: user-provided content first; with a staging repo configured, pulls new entries from GitHub into `00 收件箱` and archives the sources to the staging repo |
| "Log an idea: ..." | Writes it to `00 收件箱/灵感/` with properties & tags |
| "Excerpt: 将进酒..." | Long works get a dedicated note under `06 摘录系统/长篇/诗词/` (named by work title); short quotes are appended to the matching category file under `06 摘录系统/短篇/` |
| "Log a question: how to handle FPGA clock domain crossing" | Creates a question note (`01 生活系统/问题/未解决/`), links task and log |
| "Project review at 3pm Friday" | Creates a schedule note + auto-creates a reminder |
| "This question is resolved" | Moves it to `已解决`, updates properties, checks the task |
| "Distill this question" | Confirms the knowledge type with you, creates a knowledge note with bidirectional links |
| "Review the inbox" | Judges each item: distill / delete / archive |
| "Create a project: xxx" | Creates the six-file project folder under `05 项目系统/进行中/xxx/` |

## Layout

```
KnowOps/
├── README.md / README.en.md / LICENSE / .gitignore / AGENTS.md
└── skills/
    ├── knowops/                     # Desktop entry point
    │   ├── SKILL.md                 # trigger + loading rules + common red lines
    │   ├── references/
    │   │   ├── workflow.md          # workflow spec (model/classification/module flows/log/post-op)
    │   │   ├── init-config.md       # onboarding/GitHub staging/plugin integration/config & HTML export/scripts
    │   │   ├── properties.md        # properties/naming/layout/lifecycle design
    │   │   ├── redlines.md          # execution red lines + direct-write exceptions
    │   │   └── desktop-ingest.md    # captured content / GitHub staging pull → 00 收件箱
    │   ├── scripts/                 # html_export
    │   └── assets/
    │       ├── system-manage/       # 09 系统管理 onboarding templates (5 files)
    │       ├── agent-rules.md       # .config/agent-rules.md template
    │       └── html-export.json     # HTML export range config template
    ├── everywhere-note/             # Portable capture (optional GitHub staging sync)
    │   ├── SKILL.md
    │   ├── references/mobile-capture.md
    │   └── assets/capture-template.md
    └── automation-prompt-template.md  # automation prompt template for scheduled ingest
```

## Roadmap (future directions)

- Other file-sync channels such as Nutstore (GitHub staging-repo sync is
  implemented, see above);
- The phone sends a reminder to the desktop to trigger an automated ingest
  (scheduled ingest can be set up via `skills/automation-prompt-template.md`).

Not implemented yet; recorded for future work.

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
