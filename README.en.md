# Obsidian Knowledge Base Management Skills

A set of **Obsidian knowledge-base management skills** for AI agents: three skills
that keep your knowledge base well organized — **workflow specification + tool
operation specification + dispatch entry**, with clear boundaries, designed to be
used together.

## What is this

When managing a personal knowledge base in Obsidian (question tracking, knowledge
distillation, schedule, todos, dashboard...), an agent needs two things: *how the
content should be organized* (what modules the knowledge base has, how a question
moves from "unresolved" to "resolved" and then "distilled into knowledge"), and
*how to operate Obsidian* (read/write notes via the official CLI, respect delete
red lines, handle quirks). This repo splits those into two complementary skills,
plus a dispatch entry that tells the agent in which order to load them:

| Skill | Role | One-liner |
|---|---|---|
| **knowledge-workflow** | Workflow specification | "How the knowledge base should look and flow" — a neutral spec shared by user & agent |
| **kb-obsidian** | Tool operation specification | "How to operate Obsidian" — CLI usage, red lines, syntax essentials |
| **obsidian-suite** | Dispatch entry | "In what order to load them" — flow first, operations next, tools on demand |

## Features

- **Full question lifecycle**: unresolved → resolved → distillation; resolved
  questions become knowledge notes with **bidirectional links back to the original
  question** (the original is kept);
- **Knowledge distillation**: archived by type (experience / principle / tool /
  design / convention / case / template), **created only when used**, extensible;
- **Schedule + automated reminders**: enter with one sentence ("project review at
  3pm Friday"), reminders auto-created when explicit time signals are present;
- **Unified TODO management**: single todo file; checking an item moves it into the
  collapsed "Completed" section, newest first;
- **Real-time dashboard**: Bases views read note properties — change a status or
  tag and the dashboard updates, no manual refresh;
- **Web clipping / daily notes / operation log**: every action (including reads &
  searches) is logged;
- **Config-driven & migratable**: no hardcoded vault names or paths; everything
  from config, old configs migrate in one command;
- **Data-safety red lines**: ask consent before modify/delete, delete always goes
  to the system trash, **never permanent delete**, never initialize a repo on
  behalf of the user.

## Installation

Copy the three skills under `skills/` (`knowledge-workflow`, `kb-obsidian`,
`obsidian-suite`) into your agent's **user-level skill directory** (location
varies by platform; see your platform's skill installation docs; typically
`~/.<platform>/skills/`), or clone this repo:

```sh
git clone https://github.com/The-Daybreaker/knowledge-base.git
# then copy the three directories under skills/ into the user-level skill directory
```

> **Dependencies**: the tool skills referenced by `kb-obsidian` (obsidian-cli /
> obsidian-markdown / obsidian-bases / json-canvas / defuddle) come from the
> official Obsidian skills repository
> [kepano/obsidian-skills](https://github.com/kepano/obsidian-skills) and must be
> installed separately (see "Related projects").

## Quick start

1. Load `obsidian-suite` (dispatch entry), then load `knowledge-workflow` and run
   the **onboarding wizard**:
   - Confirm the vault's actual path & name;
   - Config defaults to the hidden `.config/` directory inside the vault (changeable);
   - Optionally enable HTML mirror export and create a dashboard.
2. When operating Obsidian, follow `kb-obsidian` for the red lines and operation
   rules (CLI usage, delete discipline, read-back verification, etc.).
3. Load the tool skills (CLI / Markdown / Bases / Canvas / web extraction) on
   demand when their capability is needed.

Usage examples:

| You say | The agent does |
|---|---|
| "Log a question: how to handle FPGA clock domain crossing" | Creates a question note (`问题/未解决/`), adds properties & tags, links TODO and log |
| "Project review at 3pm Friday" | Creates a schedule note + auto-creates a reminder |
| "This question is resolved" | Moves it to `问题/已解决/`, updates properties, checks the TODO |
| "Distill this question" | Determines knowledge type, creates a knowledge note with bidirectional link back to the question |

## Layout

```
knowledge-base/
├── README.md / README.en.md / LICENSE / .gitignore
└── skills/
    ├── knowledge-workflow/          # Skill A: workflow specification
    │   ├── SKILL.md
    │   ├── references/properties.md   # properties/dirs/lifecycle design
    │   ├── scripts/                  # kb_config / kb_env / html_export
    │   └── assets/user-manual.md     # user manual template
    ├── kb-obsidian/                  # Skill B: Obsidian operation rules & red lines
    │   ├── SKILL.md
    │   └── references/              # redlines / cli / markdown / bases / canvas
    └── obsidian-suite/               # Skill C: dispatch entry (loading-order guide)
        └── SKILL.md
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
