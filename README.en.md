# KnowOps: Obsidian Knowledge Management Skills

KnowOps is a set of **Obsidian knowledge-management skills** for AI agents: four skills
that keep your knowledge base well organized — **workflow specification + tool
operation specification + dispatch entry + portable capture**, with clear boundaries,
designed to be used together.

## What is this

When managing a personal knowledge base in Obsidian (inbox capture, question
tracking, knowledge distillation, projects, schedule, todos, dashboard, archive...),
an agent needs two things: *how the content should be organized* (what modules the
knowledge base has, how an inbox item is reviewed and distilled, how a question
moves from "unresolved" to "distilled", how knowledge differs from projects), and
*how to operate Obsidian* (read/write notes via the official CLI, respect delete
red lines, handle quirks). This repo splits those into two complementary skills,
plus a dispatch entry that tells the agent in which order to load them, and a companion
skill for portable-device capture:

| Skill | Role | One-liner |
|---|---|---|
| **knowops-workflow** | Workflow specification (standalone) | "How the knowledge base should look and flow" — a neutral spec shared by user & agent; works alone, execution via the agent's general capabilities |
| **knowops-obsidian** | Obsidian execution layer | "How to operate Obsidian" — CLI usage, red lines, syntax essentials; loaded via knowops-navigator routing |
| **knowops-navigator** | Dispatch entry | "In what order to load them" — flow first, operations next, tools on demand |
| **everywhere-note** | Portable capture & unified ingest | Capture with @ on the phone, get standard md + a 22:00 reminder; the desktop ingests in the evening |

## Features

- **Inbox capture & review**: short, fragmented thoughts, inspirations and unclear
  items go to `00 收件箱` (随手记 / 灵感 / 待整理内容) by default; during review,
  each item is distilled, deleted or archived based on how it will be used;
- **Standalone**: knowops-workflow alone can manage the knowledge base; the spec and red lines are tool-agnostic, and execution relies on the agent's general capabilities;
- **Portable capture & unified ingest**: @ everywhere-note on a phone/portable device and dictate directly; it generates KB-compliant markdown (a file when supported) and sets a 22:00 reminder; back at the desktop, knowops-navigator routes the batch ingest into `00 收件箱`; the phone only needs this one skill and no transfer channel;
- **Full question lifecycle**: unresolved → in progress → resolved → distilled;
  the original question moves to `已沉淀` and keeps **bidirectional links** to the
  knowledge note;
- **Knowledge distillation**: grouped by type (概念原理 / 经验方法 / 方案 / 案例),
  domain subfolders created **only when used**, growth-triggered splitting
  (<50 keep flat / 50–150 add domain level / >150 evaluate third level);
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
- **Archive & system management**: `07 归档` uses zero-padded Chinese date folders;
  `08 系统管理` holds architecture, classification, naming, frontmatter, agent
  rules, change log and user manual;
- **Plugin integration rules**: at onboarding, plugins are scanned and the user
  confirms how they integrate; rules are written to `08 系统管理/Agent规则.md`,
  read before every operation and executed afterwards (e.g., version commit first,
  then cloud sync);
- **Config-driven, version-following**: directories and preferences live in config;
  schema version follows the skill version;
- **Data-safety red lines (tool-agnostic)**: delete always goes to the system trash and
  stays recoverable; prefer git when creating/initializing a knowledge base; run a
  similarity check before creating anything; prefer existing modules. Execution-layer
  red lines (consent before modify/delete, user-provided info is authoritative, etc.)
  live in knowops-obsidian.

## Installation

Copy the four skills under `skills/` (`knowops-workflow`, `knowops-obsidian`,
`knowops-navigator`, `everywhere-note`) into your agent's **user-level skill directory** (location
varies by platform; see your platform's skill installation docs; typically
`~/.<platform>/skills/`), or clone this repo:

```sh
git clone https://github.com/The-Daybreaker/KnowOps.git
# then copy the four directories under skills/ into the user-level skill directory
```

> **Portable devices**: only `everywhere-note` needs to be installed on phones/portable devices (its mobile part is self-contained and does not depend on this suite).

> **Dependencies**: the tool skills referenced by `knowops-obsidian` (obsidian-cli /
> obsidian-markdown / obsidian-bases / json-canvas / defuddle) come from the
> official Obsidian skills repository
> [kepano/obsidian-skills](https://github.com/kepano/obsidian-skills) and must be
> installed separately (see "Related projects").

## Quick start

1. For most knowledge-base tasks, start with `knowops-navigator` (dispatch entry), then
   load `knowops-workflow` and run the **onboarding wizard**; directly @-ing
   `knowops-workflow` also works.
   - Confirm the vault's actual path & name;
   - Confirm the 8+1 module structure and config location (defaults to the hidden
     `.config/` directory inside the vault);
   - Scan installed plugins and confirm integration rules one by one (whether to
     include, when, and in what order); rules are written to
     `08 系统管理/Agent规则.md`;
   - Copy the full `08 系统管理` template set; create `06 看板` by default;
     optionally enable HTML mirror export.
2. By default `knowops-workflow` works standalone (execution via the agent's general
   capabilities); when Obsidian operations are needed, `knowops-navigator` routes to
   `knowops-obsidian` for red lines and operation rules (CLI usage, delete discipline,
   read-back verification, etc.).
3. Load the tool skills (CLI / Markdown / Bases / Canvas / web extraction) on
   demand when their capability is needed.

Usage examples:

| You say | The agent does |
|---|---|
| Phone: "log: XXX" | Generates a KB-compliant md entry and sets a 22:00 reminder |
| "Ingest today's phone captures" | knowops-navigator routes to everywhere-note's desktop part, parses and writes into `00 收件箱` |
| "Log an idea: ..." | Writes it to `00 收件箱/灵感/` with properties & tags |
| "Log a question: how to handle FPGA clock domain crossing" | Creates a question note (`01 生活系统/问题/未解决/`), links task and log |
| "Project review at 3pm Friday" | Creates a schedule note + auto-creates a reminder |
| "This question is resolved" | Moves it to `已解决`, updates properties, checks the task |
| "Distill this question" | Confirms the knowledge type with you, creates a knowledge note with bidirectional links |
| "Review the inbox" | Judges each item: distill / delete / archive |
| "Create a project: xxx" | Creates the six-file project folder under `05 项目系统/进行中/xxx/` |

## Layout

```
KnowOps/
├── README.md / README.en.md / LICENSE / .gitignore
└── skills/
    ├── knowops-workflow/          # Skill A: workflow specification
    │   ├── SKILL.md
    │   ├── references/properties.md   # properties/naming/layout/lifecycle design
    │   ├── scripts/                  # kb_config / kb_env / html_export
    │   └── assets/
    │       ├── system-manage/        # 08 系统管理 onboarding templates (7 files)
    │       └── html-export.json      # HTML export range config template
    ├── knowops-obsidian/                  # Skill B: Obsidian operation rules & red lines
    │   ├── SKILL.md
    │   └── references/              # redlines / cli / markdown / bases / canvas
    ├── knowops-navigator/               # Skill C: dispatch entry (loading-order guide)
    │   └── SKILL.md
    └── everywhere-note/              # Skill D: portable capture & desktop ingest
        ├── SKILL.md
        ├── references/              # mobile-capture / desktop-ingest
        └── assets/capture-template.md
```

## Roadmap (future directions)

- Once mobile agents gain GitHub / Nutstore-style file sync: the portable side auto-syncs captures to the platform, and the desktop runs a scheduled task to pull and ingest them;
- The phone sends a reminder to the desktop to trigger an automated ingest.

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