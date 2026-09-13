# KnowOps: Obsidian Knowledge-Management Skills for AI Agents

**English**: this file · **中文**: [README.md](README.md)

KnowOps is a set of Obsidian knowledge-management skills you install into an AI agent. Once installed, the agent knows how to take care of your knowledge base: capture a thought the moment it arrives, with no need to decide where it belongs; when you have a moment, say the word and it files those notes away under rules you define; and genuinely validated experience gradually settles into topic documents you can return to again and again — in your own original words, never rewritten on your behalf.

It consists of two skills, installed by device and designed to work together:

| Skill | Installed on | Role |
|---|---|---|
| **knowops** | A computer (a device that can operate the base) | The base's steward: how content is organized and how Obsidian is operated; installing it alone runs the whole base |
| **everywhere-note** | Phones / tablets and other portable devices | The portable note-taker: @ it and dictate; it shapes a clean note and reminds you that evening to collect it on the computer |

> Do not install both skills on the same device — they would compete for the same triggers.

Here is the journey of a record, from an offhand remark to settled experience:

```text
[Phone / Tablet]
  @everywhere-note and dictate directly
        │  shaped into a clean note, with a 22:00 reminder to process it
        ▼
[Your Computer] collect: paste / hand over a file, or auto-pull from a GitHub staging repo
        │
        ▼
  00 收件箱 (Inbox) — drop freely, zero fuss
        │  you say "review the inbox"; the agent routes each item
        ├─▶ merge into 01 知识 & other modules (validated experience)
        ├─▶ move to 04 归档 (inactive, stored by date)
        ├─▶ delete (system trash, recoverable)
        └─▶ still unclear — stays in the inbox
```

## How it takes care of your knowledge base

This section follows the order of everyday use: what you actually experience, and why things are arranged this way.

### When capturing, you don't have to think about anything

Knowledge bases usually fail not for lack of things to record, but because the act of recording is too much trouble: pick a category first, follow a format, come up with a naming rule — hesitate once and the thought is gone. KnowOps moves all of that off your shoulders. Say "log this" to the agent on the computer, or just create a file in `00 收件箱` yourself — no format to fill, no title to settle first, just drop it in. Agent-written entries automatically carry a sequence number and properties so they're easy to browse later; your own hand-written files have no requirements at all, and the inbox runs no format checks.

Classification is deliberately postponed to organizing time. Information is often incomplete at the moment of capture, and classifying in a hurry tends to go wrong — an agent holding only fragments gets it wrong just as often; judging where something belongs is far more reliable once the whole item lies in front of you. So at the capture end, the only thing you need to do is keep it.

It's just as easy on the phone. @ everywhere-note and dictate; it shapes the content into a clean note for you to check, and if anything was captured that day it sets a 22:00 reminder so you don't forget to process it back at the computer. How the content reaches the computer is up to you — paste it yourself, or designate a GitHub repo as a relay and let the desktop pull automatically, as covered later.

"Don't think when capturing" doesn't mean "store everything". Todos are better off in a todo app, project materials belong in their project folders, and runnable templates belong to their code repositories — keeping another copy in the knowledge base only leaves you with a stale replica that costs effort to sync. This base is reserved for something else: excerpts you read, experience that has been validated, and thoughts not yet worked out. Deciding whether something belongs here comes down to two questions: does it have a more suitable home elsewhere? Can it be conveyed in a single note?

### When organizing, the rules are yours

When you have a moment, say "review the inbox", and the agent goes through it item by item, routing each by its content: experience belonging to a topic is merged into the matching topic document; inactive items move into date-based archive folders; things confirmed useless are deleted to the system trash (recoverable); anything still unclear stays in the inbox. Missing information such as dates and tags is filled in at this point.

How does it know where each item belongs? From a **User Manual that lives in your own base**. What every module holds, how content enters, how it's classified and named — the rules all live in `03 系统/用户手册.md`, which you can open and edit at any time; the agent reads it before every piece of work and follows your rules. The rules have exactly this one home, and the config stores only a machine-oriented directory index, so two disagreeing copies of the rules can never happen.

Opening a new module doesn't require waiting for anyone to update the skill. Create a folder in the base (say, 读书 / "reading"), tell the agent what it's for, what counts as belonging, and how it's organized internally; once it has asked and understood, it writes the rules into the manual, adds an entry on the dashboard, and follows them from then on. If you later delete that folder, it asks whether to remove the manual section too or mark it retired with history kept. You decide what shape the knowledge base grows into; the skill supplies only a general way of working.

### Experience settles into topics, in your original words

Genuinely valuable experience lives in `01 知识`, organized by topic — one document per topic, rather than forced into abstract drawers like "principles / methods / cases", because topics are the real thread along which you recall knowledge. Inside a document, sections and numbered paragraphs ("一、二、三") organize the content; each paragraph carries one piece of experience, stating the conclusion together with its full context.

One rule here doesn't budge: your words are recorded exactly as you say them. The agent doesn't polish, rewrite or compress on your behalf, because your original wording holds the shape and nuance of your thinking at that moment — once "tidied up", it can't be recovered. If it believes some background is worth adding, it asks you first and appends it as a new paragraph, rather than mixing it into your own words.

Structurally, it insists on "grow in one place first; split only when it's full". A topic starts in a single document; only when a section reaches roughly 30 paragraphs and genuinely becomes awkward to navigate does the agent propose splitting it into a standalone document, with the original becoming a folder that holds them — never designing layers in advance, before the content exists. Whether a module deserves to exist follows the same logic: look at whether real content actually flows through it, not at whether it "might be useful someday".

`02 摘录` (excerpts) is the one preset example module, for collected poetry, quotes and sentences; initialization asks whether to enable it. On, long works each get their own note while short quotes aggregate by category, and a category past 100 entries splits automatically; leaving it off doesn't affect anything, and the manual keeps that section as a model of "how module rules are written".

### Every step is on record, and a mistaken deletion is recoverable

When you hand a knowledge base to an agent, the fear is that it changes things without your knowing. KnowOps makes every write accountable. Under `03 系统/日记` there is one diary file per day, split into "user" and "agent" chapters: agent actions are logged in detail across seven categories (ingest, settle, organize, archive, delete, back-fill, system); changes you made by hand without noting are back-filled as far as possible from file records and git history, marked as inference. After each batch, a "review" checklist also appears in the inbox, stating what changed and where to look — delete it once you've checked; the root dashboard shows in real time what's waiting and what was recently updated.

Behind this sits the agent's defined role: a steward, not an author. It handles formatting, system upkeep and writes on your explicit instruction; it never decides on its own what "should be recorded", and never proactively adds to your documents. The content stays yours, which is also why you always have a clear picture of what's in the base.

Safety isn't left to "it'll be careful" either — it's written into fixed rules: deletion always goes through the system trash and stays recoverable; changes affecting many files, or irreversible ones, show you a plan and wait for your go-ahead; every important write is read back for verification. Notes are also incrementally exported, by default, to standalone HTML that opens without Obsidian, for reading on other devices; the canvases you draw yourself are entirely free space — never managed, checked or exported.

> The division of labor in one sentence: **you** define the structure and the trade-offs, the **skill** provides responsibilities, contracts and safety boundaries, the **agent** organizes and maintains accordingly, and **Obsidian** keeps the result as notes that are readable, linkable and recoverable.

## What the base looks like after initialization

```text
My Knowledge Base/
├── 看板.md            # the front door: a one-screen overview (embedded live views)
├── 00 收件箱/          # the entry for every quick note; flat, no subfolders
├── 01 知识/            # validated experience, converged into topic documents
├── 03 系统/            # facilities: user manual, diary, templates, dashboard data
├── 04 归档/            # inactive content worth keeping, stored by date
└── .config/           # hidden: config, change history, scripts, HTML mirror
```

Each of the four base modules is memorable in one line: the inbox holds "not yet thought through", knowledge holds "validated", system holds "the base's own traces and manual", and archive holds "no longer active". `03 系统` and `04 归档` are fixed as the last two positions; every future module is inserted before them and renumbered in order. The root `看板.md` is the overview entry, not a module.

Initialization doesn't create a pile of empty folders: it places only `03 系统` (user manual, templates) and the root dashboard first, while the inbox, knowledge and archive appear the first time something is written to them. `.config/` is the hidden facilities layer for the config, change history, scripts and exported HTML mirror, so it never occupies your visible space in Obsidian.

## Installation

Choose by device — **never install both on the same device**:

| Device | Install |
|---|---|
| Desktop computer (operates the knowledge base) | `skills/knowops/` |
| Phone / tablet / portable device | `skills/everywhere-note/` |

Installation always means "copy the skill folder into your agent's user-level skill directory" (the location varies by platform, typically `~/.<platform>/skills/`; follow your platform's instructions). Obtain it either way:

- Download `<skill>-vX.Y.Z.zip` from [GitHub Releases](https://github.com/The-Daybreaker/KnowOps/releases) (generated on every release; the skill folder is the zip root, ready to unpack);
- Or clone the repo and copy manually:

```sh
git clone https://github.com/The-Daybreaker/KnowOps.git
# then copy the matching skill folder under skills/ into the user-level skill directory
```

**Where concrete Obsidian operations come from**: knowops doesn't reimplement a set of operating commands. Concrete capabilities — reading and writing notes, Markdown, Bases, Canvas, web extraction — are delegated to the officially maintained tool skills: obsidian-cli, obsidian-markdown, obsidian-bases, json-canvas and defuddle, from [kepano/obsidian-skills](https://github.com/kepano/obsidian-skills); installing them as well is recommended (see "Related projects" below). The system works without them: knowops checks with you first and falls back to the official Obsidian help docs rather than guessing commands from memory.

## Getting Started

### First run: the initialization wizard

A desktop knowledge-base task triggers knowops; when it finds an uninitialized base, it confirms things with you in order, one question at a time, rather than dumping everything at once:

1. The vault's actual path and name;
2. The four base modules and the root dashboard (along with an explanation of the extension mechanism: you create folders, it asks for the rules);
3. Whether to enable the preset "excerpts" extension module;
4. Whether to configure GitHub staging-repo sync (skippable);
5. Scan existing plugins and confirm integration rules one by one (for example, "commit first, then cloud sync"), written into the "agent constraints" chapter of the User Manual;
6. Place the user manual and note templates under `03 系统/`, and guide you to enable Obsidian's core Templates and Daily notes plugins;
7. Create the root dashboard and enable the HTML mirror export as needed.

All configuration lives in the hidden in-base file `.config/knowops.config.json`, one per vault. For a pre-existing base with content, the agent never migrates or changes anything automatically — it discusses how to proceed with you on the spot.

### Daily use: just ask in natural language

| You say | The agent does |
|---|---|
| On the phone: "log: ..." | everywhere-note shapes a clean note and sets a 22:00 reminder; uploads to the staging repo when configured and GitHub-capable |
| "Ingest today's phone captures" | Takes content you provide first; with none provided and a staging repo configured, pulls new entries, writes them into `00 收件箱` with numbered names, and archives the staging sources |
| "Log this: ..." | Writes to `00 收件箱/` with a numbered name, complete properties and tags |
| "Excerpt: 将进酒, ..." | Ingests per the manual's excerpt rules: long works stand alone, short quotes append to their category |
| "File this experience under the topic 架构设计" | Merges it into the matching section of the topic document under `01 知识/`, keeping your words verbatim |
| "Review the inbox" | Routes each item: destination module / archive / delete / keep |
| "I made a folder called 读书 for book notes" | Asks for the module's rules → writes them into the User Manual → follows them thereafter |
| "Archive this note" | Moves it to `04 归档/<today's date>/` |
| "What did I change recently?" | Reads the diary and review receipts and gives you a timeline |

### Scheduled automatic ingest

To have the desktop collect new staging-repo entries on a schedule, use `skills/automation-prompt-template.md`: copy the template onto an agent platform that supports scheduled or event-triggered tasks, and replace the vault path, skill location and staging-repo placeholders. It does only one thing — "check the staging repo → ingest → archive sources" — and stops to report whenever it is unsure, deciding nothing on its own. The template ships with every Release.

## Repository Layout

```text
KnowOps/
├── README.md / README.en.md / LICENSE / .gitignore / AGENTS.md
├── tools/                          # dev-time validation (check.py, also used by CI)
├── .github/workflows/              # core checks on push / PR
└── skills/
    ├── knowops/                    # the single desktop entry point
    │   ├── SKILL.md                # triggers, loading rules, common red lines (kept thin)
    │   ├── references/             # business details, loaded on demand to avoid rule clashes
    │   │   ├── workflow.md         # workflow: two gates, module flows, diary, post-op
    │   │   ├── init-config.md      # wizard, plugin integration, config & HTML export
    │   │   ├── properties.md       # properties, naming, layout and lifecycle
    │   │   ├── redlines.md         # execution red lines and direct-write exceptions
    │   │   └── desktop-ingest.md   # captured content / staging pull → inbox
    │   ├── scripts/                # lightweight scripts shipped with the skill: html_export, vault_check
    │   └── assets/
    │       ├── system-manage/      # the base's own document templates (user manual, change log)
    │       ├── templates/          # note templates (topic document, for the Templates plugin)
    │       └── html-export.json    # HTML export scope config
    ├── everywhere-note/            # portable capture, self-contained in one file
    │   └── SKILL.md
    └── automation-prompt-template.md  # prompt template for scheduled automatic ingest
```

## Related Projects

- [kepano/obsidian-skills](https://github.com/kepano/obsidian-skills) — the officially maintained agent skill set for Obsidian (obsidian-cli / obsidian-markdown / obsidian-bases / json-canvas / defuddle), to which KnowOps delegates concrete Obsidian operations;
- [kepano/defuddle](https://github.com/kepano/defuddle) — web page content extraction library.

## License

MIT License, see [LICENSE](LICENSE).
