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

- **Five modules, each with an obvious job**: `00 收件箱` (not yet thought through) /
  `01 知识` (validated) / `02 摘录` (collected excerpts) / `03 系统` (the base's own
  traces and docs) / `04 归档` (no longer active); 系统 and 归档 are fixed as the last
  two, with a root-level `看板.md` as the one-screen overview;
- **Inbox: easy in, strict out**: flat layout, numbered filenames, no subfolders; you
  may drop in files with no formatting at all — rules bind the agent, which fills in
  everything at settlement time; the inbox is exempt from structural checks;
- **Knowledge by topic**: one document per topic, entries organized in sections; when a
  section passes about 30 entries a split is proposed and the document is upgraded to a
  folder of its name — monolith first, split only when it bursts; no hierarchy designed
  up front;
- **Excerpts**: long excerpts (poetry, classical prose) get one note per work
  (named by work title, with author / dynasty / source properties); short quotes
  (famous sayings, aphorisms, personal reflections) are aggregated by category
  (split into numbered files past 100 entries); desktop "excerpt: ..." goes
  straight in, portable excerpts settle via inbox review;
- **Diary = operation record**: every write/edit/move/delete/archive appends a line,
  kept by year under `03 系统/日记/` — written automatically, browsable anytime;
- **Obsidian templates**: `03 系统/模板/` ships two note templates (topic document,
  long excerpt) for use with Obsidian's core Templates plugin;
- **Progressive loading**: knowops' SKILL.md only carries the trigger, loading rules
  and common red lines; workflow.md, redlines.md and desktop-ingest.md are read on
  demand;
- **Portable capture & unified ingest**: @ everywhere-note on a phone/portable device and dictate directly; it generates KB-compliant markdown (a file when supported) and sets a 22:00 reminder; back at the desktop, knowops parses the captures and writes them into `00 收件箱`; the phone only needs this one skill and no transfer channel; the portable skill embeds no desktop-base structure, so desktop restructuring never forces a reinstall;
- **GitHub staging repo sync (optional)**: you designate a GitHub staging repo; on the phone, when GitHub capability is available (gh CLI / git / GitHub MCP etc.), entries are uploaded into this KB's folder in the staging repo; on the desktop, "ingest" pulls new entries into `00 收件箱` (numbered filenames) and archives the source files into `<KB-name>/归档/<date>/` in the staging repo (split by ingest date); multiple KBs can share one staging repo without conflicts;
- **Dashboard**: root `看板.md` embeds the views from `03 系统/看板.base` (inbox
  pending, knowledge recent, excerpts recent); extensible;
- **Archive**: `04 归档` uses zero-padded Chinese date folders;
- **Canvas is free space**: canvases you create are never managed, checked or exported;
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
   - Ingesting captured content/files → read `references/desktop-ingest.md`,
     then load `references/workflow.md` and `references/redlines.md` per its
     header note.
2. The onboarding wizard confirms step by step: vault path & name, the five-module
   default structure (lazy loading: inbox/excerpt/archive appear on first write),
   optional GitHub staging repo sync, plugin integration rules (written to
   `.config/agent-rules.md`), the `03 系统` user docs and templates, the example
   topic document, the root dashboard; config lives in the vault's hidden `.config/`
   directory, and the HTML mirror export is enabled by default
   (`<vault>/.config/HTML-Export/`).
3. Load the tool skills (CLI / Markdown / Bases / Canvas / web extraction) on
   demand when their capability is needed.

Usage examples:

| You say | The agent does |
|---|---|
| Phone: "log: XXX" | everywhere-note generates a KB-compliant md entry and sets a 22:00 reminder; uploads to the staging repo when configured and GitHub capability is available |
| "Ingest today's phone captures" | knowops loads desktop-ingest.md: user-provided content first; when no content is provided and a staging repo is configured, new entries are pulled from GitHub, written into `00 收件箱` with numbered filenames, and the sources are archived to the staging repo |
| "Log this: ..." | Writes it to `00 收件箱/` (numbered, with properties & tags) |
| "Excerpt: 将进酒..." | Long works get a dedicated note under `02 摘录/长篇/诗词/` (named by work title); short quotes are appended to the matching category file under `02 摘录/短篇/` |
| "File this experience under the topic 架构设计" | Merges it into the matching section of the topic document under `01 知识/` |
| "Review the inbox" | Judges each item, five destinations: knowledge / excerpt / archive / delete / keep |
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
    │       ├── system-manage/       # 03 系统 onboarding user docs (2 files: manual/change log)
    │       ├── templates/           # note templates (topic document/long excerpt, for the Obsidian Templates plugin)
    │       ├── knowledge-example/   # example topic document for the knowledge module
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
