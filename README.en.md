# knowledge-workflow / kb-obsidian

A **two-skill combo** for general knowledge management: one defines *how the
knowledge base should be organized* (workflow specification), the other defines
*how to operate the tools* (Obsidian operation rules & red lines). Clear
boundaries, designed to be used together.

## The two skills

| | knowledge-workflow | kb-obsidian |
|---|---|---|
| Role | **Workflow specification** | **Tool operation specification** |
| Audience | Process rules shared by user & agent | Unified requirements on tools/operators + Obsidian-specific operations |
| Includes | Module routing (questions/projects/schedule/clips/daily/knowledge/tasks), question lifecycle (unresolved → resolved → distillation), knowledge archiving by type, dashboard, schedule, automation reminders, operation log, onboarding wizard, config & HTML export policy | Unified red lines (ask consent before modify/delete, never `git init`, delete to system trash, direct file access exceptions); Obsidian-specific (CLI usage & quirks, note CRUD, daily notes setup, Markdown/Bases/Canvas syntax essentials, web clipping, two-step write, read-back verification) |
| Excludes | Requirements on agent behavior, tool operation requirements, any tool names | Knowledge-base business rules (routing/lifecycle/distillation flows, etc.) |

In one sentence: **knowledge-workflow answers "how the knowledge base should look
and flow"; kb-obsidian answers "what constraints apply to tools &
operators, and how to operate Obsidian concretely".**

## Quick start

1. Load `knowledge-workflow` and follow the onboarding wizard:
   - Confirm the vault's actual path & name;
   - Config defaults to the hidden `.config/` directory inside the vault (changeable);
   - Optionally enable HTML mirror export and create a dashboard.
2. When operating the knowledge base, follow `kb-obsidian` for the
   Obsidian-side execution rules and red lines.

> The tool-layer connection is left to the user to arrange (e.g. loading both
> skills in the agent, or configuring the dispatch relationship); knowledge-workflow
> itself does not bind to any specific tool.

## Layout

```
├── skills/
│   ├── knowledge-workflow/          # Skill A: knowledge workflow specification
│   │   ├── SKILL.md
│   │   ├── references/properties.md   # properties/dirs/lifecycle design
│   │   ├── scripts/                  # kb_config / kb_env / html_export
│   │   └── assets/user-manual.md     # user manual template
│   └── kb-obsidian/                  # Skill B: Obsidian operation rules & red lines
│       ├── SKILL.md
│       └── references/              # redlines / cli / markdown / bases / canvas
├── legacy/
│   ├── obsidian-kb/                 # archived old obsidian-kb (historical reference only)
│   └── dist-archive/                # archived old release zips (v1.0.0~v2.3.3)
├── dev/                             # dev-time assets (not shipped)
│   ├── CHANGELOG.md / DESIGN.md / REQUIREMENTS.md / TEST-REPORT.md
│   └── scripts/update_skill.py      # dev-time release tool (packages both skills)
└── dist/                            # releases: zips for both skills
```

## Core conventions

- **No inbox**: classify every record request before routing; ask the user when
  the type is unclear;
- **Similarity check before create**; **consent before modify/delete**;
  **delete goes to system trash, never permanent**;
- **Knowledge-base-irrelevant files default to the hidden `.config/` directory**
  inside the vault (config/log/manual/export) — never touch the user's note area;
- **Config-driven**: vault name, directories and preferences all live in
  `knowledge-workflow.config.json`; no hardcoded names; old configs migratable
  (`kb_config.py migrate`);
- **Active tags & bidirectional links**; `updated` (to the minute) on every edit;
- **Operation log on every action** (`.config/log/`, including reads & searches).

## License

MIT License, see [LICENSE](LICENSE).
