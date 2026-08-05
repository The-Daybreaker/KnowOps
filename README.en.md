# knowledge-workflow / kb-obsidian / obsidian-suite

An **Obsidian skill combo** for general knowledge management: `knowledge-workflow`
defines *how the knowledge base should be organized* (workflow specification),
`kb-obsidian` defines *how to operate the tools* (Obsidian operation rules &
red lines), and `obsidian-suite` is the dispatch entry (tells the agent which
skill to load and in what order). Clear boundaries, designed to be used together.

## The three skills

| | knowledge-workflow | kb-obsidian | obsidian-suite |
|---|---|---|---|
| Role | **Workflow specification** | **Tool operation specification** | **Dispatch entry** |
| Audience | Process rules shared by user & agent | Unified requirements on tools/operators + Obsidian-specific operations | Agent (loading-order guidance) |
| Includes | Module routing (questions/projects/schedule/clips/daily/knowledge/tasks), question lifecycle (unresolved → resolved → distillation), knowledge archiving by type, dashboard, schedule, automation reminders, operation log, onboarding wizard, config & HTML export policy | Unified red lines (ask consent before modify/delete, never `git init`, delete to system trash, ask the user for record ownership, info comes from the user, direct file access exceptions); Obsidian-specific (CLI usage & quirks, note CRUD, daily notes setup, Markdown/Bases/Canvas syntax essentials, web clipping, two-step write, read-back verification) | Loading order: knowledge-workflow (business flow) first → kb-obsidian (operation rules) → tool skills on demand |
| Excludes | Requirements on agent behavior, tool operation requirements, any tool names | Knowledge-base business rules (routing/lifecycle/distillation flows, etc.) | Concrete business & operation content |

In one sentence: **knowledge-workflow answers "how the knowledge base should look
and flow"; kb-obsidian answers "what constraints apply to tools & operators, and
how to operate Obsidian concretely"; obsidian-suite answers "in what order to
load them".**

## Quick start

1. Load `obsidian-suite` (dispatch entry) → follow its guidance, load
   `knowledge-workflow` and run the onboarding wizard:
   - Confirm the vault's actual path & name;
   - Config defaults to the hidden `.config/` directory inside the vault (changeable);
   - Optionally enable HTML mirror export and create a dashboard.
2. When operating the knowledge base, follow `kb-obsidian` for the
   Obsidian-side execution rules and red lines.
3. Load the tool skills (CLI / Markdown / Bases / Canvas / web extraction)
   on demand when their capability is needed.

> The tool-layer connection is left to the user to arrange (e.g. loading both
> skills in the agent, or configuring the dispatch relationship); knowledge-workflow
> itself does not bind to any specific tool.

## Layout

```
knowledge-base/
├── README.md                 # Chinese docs
├── README.en.md              # English
├── LICENSE                   # MIT
├── .gitignore
└── skills/
    ├── knowledge-workflow/          # Skill A: knowledge workflow specification
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

## Related projects

The tool skills (obsidian-cli / obsidian-markdown / obsidian-bases / json-canvas /
defuddle) are installed copies from the **official Obsidian skills repository**,
and can be updated from upstream:

- **https://github.com/kepano/obsidian-skills** — Official Obsidian agent skills
  (obsidian-cli, obsidian-markdown, obsidian-bases, json-canvas, defuddle)
- defuddle itself: https://github.com/kepano/defuddle

## License

MIT License, see [LICENSE](LICENSE).
