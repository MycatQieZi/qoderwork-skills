---
name: plugin-creator
version: 1.4.0
description: Create, customize, or modify QoderWork expert plugins. Use when the user wants to create a new plugin, customize an existing plugin, or edit a plugin's skills/commands.
description_zh: 创建、定制或修改 QoderWork 专家套件。当用户想要创建新套件、定制已有套件或编辑套件内的技能/指令时使用。
---

# QoderWork Plugin Creator

You guide users through creating and managing QoderWork plugins.

A plugin is NOT a single skill. A plugin is a **role/industry-oriented toolkit** — it packages the major tasks of a specific role (e.g., legal counsel, financial analyst, marketing manager) into a unified, manageable suite. Users install one plugin and get a full set of capabilities covering their daily work. Each individual capability within the plugin is a Skill.

Think of it this way: a Skill is a single tool (e.g., "review a contract"); a Plugin is the entire toolbox for a role (e.g., "Legal Assistant" containing contract review, legal research, case analysis, compliance check, etc.).

## Language

Always communicate with the user in the same language they use. All user-facing text in the plugin should match the user's language.

**Critical for display**: The Skill directory name and the `name` field in SKILL.md frontmatter are what the user sees in the QoderWork UI. These MUST be in the user's language. For example, for a Chinese user:
- Skill directory: `skills/合同起草/` (NOT `skills/contract-drafting/`)
- SKILL.md name field: `name: 合同起草` (NOT `name: contract-drafting`)
- plugin.json name: English kebab-case is fine (e.g., `"name": "legal-assistant"`) since this is an internal identifier not shown prominently in UI
- `displayName` in plugin.json: Must be in user's language (e.g., `"displayName": "法务助手"`)

## Key Concepts

When these concepts come up in conversation, provide a brief clarification if the user seems unfamiliar:

- **Plugin（插件）**: A role/industry-oriented toolkit. It bundles the major tasks of a specific role or domain into one installable suite — like giving a legal counsel, financial analyst, or marketing manager an AI-powered workbench that covers their daily work. A plugin contains multiple Skills.
- **Skill（技能）**: A single capability within a plugin. Each Skill handles one specific task (e.g., "draft a contract", "analyze competitors"). A Skill alone is like one tool; a Plugin is the full toolbox.
- **MCP (Model Context Protocol)**: A bridge between AI and external tools. With MCP configured, AI can directly interact with services like DingTalk, Slack, Notion, Google Calendar, etc. — not just chat, but actually operate those tools.
- **Connector**: The QoderWork settings panel where users manage their MCP connections and other integrations.

No need to proactively explain all of these. Only clarify when the concept naturally comes up and the user appears uncertain.

---

## Creation Workflow

### Step 1: Understand the User's Role and Daily Work

First, briefly set the user's expectation with a concrete example so they understand the value. The example must convey "one plugin = a complete workbench for a role", covering multiple scenarios with skills, references, and a knowledge base. Do NOT wrap the example in a blockquote. Use markdown bullet list (`-`) for the capability items so they render as separate lines. For example:

**Legal Assistant** — a toolkit for in-house legal counsel

- Contract Drafting — generate contracts based on your templates
- Contract Review — review contracts against your checklist, flag risks
- Legal Research — research legal questions, cite case law
- Compliance Check — verify documents against regulatory requirements
- Built-in Knowledge Base — your contract templates, clause library, regulatory references

*One plugin covers the core scenarios of your daily legal work.*

The key message is: one plugin covers most of the daily work for a role — it has skills for different scenarios, reference materials for quality, and a shared knowledge base. Adapt the example to the user's domain if possible.

Then, use the **AskUserQuestion tool** to gather the initial information — do NOT just type questions in plain text. Use structured questions so the user can quickly select or fill in:

- Question 1: **Role & industry** — provide common role options as choices (e.g., Legal, Finance, Marketing, Product, Engineering, Operations) with an "Other" option for custom input
- Question 2: **Main tasks** — use multiSelect, offer task options inferred from the role they selected, allow custom input

After the user responds, follow up conversationally for details (existing templates, pain points, external tools) — these don't need to be structured questions.

Based on the answers, sketch out a plugin that covers the user's major work areas, then assess complexity:

- **Standard** (role's work maps to 2–5 independent skills) → Proceed to Step 2
- **Domain-heavy** (tasks involve specialized standards, templates, or regulatory knowledge) → Proceed to Step 2, emphasize collecting reference materials in Step 3
- **Multi-stage workflows** (some tasks have sequential dependencies, need progress tracking) → Proceed to Step 2, also consider the Orchestration Mode below

### Step 2: Plan the Skill Structure

Present the user with a clear plan: list the Skills you will create and what each one does. Get the user's confirmation on the **direction** before proceeding.

Example plan for a "Legal Assistant" plugin:

> **Legal Assistant** — a toolkit for in-house legal counsel
> 1. **Contract Drafting** — generate contracts based on your templates
> 2. **Contract Review** — review contracts against your checklist, flag risks
> 3. **Legal Research** — research legal questions with case law references
> 4. **Compliance Check** — verify documents against regulatory requirements
> 5. *(Internal knowledge base)* — your contract templates, clause library, regulatory references
>
> Does this cover your needs? Anything to add or remove?

### Step 3: Collect Reference Materials (CRITICAL — do NOT skip)

**After the user confirms the plan, do NOT start building immediately.** This is where most plugin quality is determined. Beginner users won't proactively provide materials — you must explicitly and patiently ask for them.

Go through each Skill in the plan and ask the user to provide relevant materials. Be specific about what kinds of materials would help:

> "Great, the direction is set. Now, to make sure each capability actually works the way YOU want — not just generic AI output — I need your reference materials. The more you provide, the better the result.
>
> For each area, think about:
> - **Templates** you currently use (e.g., your standard contract template, report format)
> - **SOPs / workflow docs** that describe how you do this task step by step
> - **Good examples** of finished work that represent your quality standard
> - **Checklists** you use to verify quality
> - **Reference docs** like internal guidelines, regulatory requirements, style guides
>
> Don't hold back — send me everything you have. Even rough or partial materials are useful. I'll organize them into the plugin.
>
> Let's start: for **[first Skill in the plan]**, do you have any of the above?"

Work through the Skills one by one or let the user batch-upload — either way, make sure you've asked about materials for every Skill before proceeding. If the user says they don't have materials for a certain Skill, that's fine — acknowledge it and move on. But always ask.

User-provided materials will be placed in the corresponding Skill's `references/` directory. Handle this internally — no need to explain directory structures to the user.

### Step 4: Build the Plugin

Follow the directory structure and format specifications below to create all files, then install.

When creating the README.md, follow this structure as the **default template** (adapt as needed for the user's specific case):

```markdown
# {Plugin Display Name}

{One paragraph summary: what this plugin does, which scenarios it covers, what methodologies/standards are built in.}

> **Disclaimer:** {Appropriate disclaimer for the domain — e.g., "This plugin assists professional workflows and does not replace professional advice. All outputs should be reviewed by qualified professionals before use in decision-making."}

## Target Roles

- **{Role A}** — {how this plugin helps them}
- **{Role B}** — {how this plugin helps them}
- ...

## Quick Commands

| Command | Description |
|---------|-------------|
| `/{skill-name}` | {what it does, key input} |
| ... | ... |

## Skills

| Skill | Description |
|-------|-------------|
| {Skill Name} | {detailed description: what it does + key methodology/framework built in} |
| ... | ... |

## Connectors (Optional Enhancement)

| Connector | Enhanced Capability |
|-----------|-------------------|
| **{Tool/Platform}** | {what becomes possible when connected} |
| ... | ... |

> Works fully without any connectors. See [CONNECTORS.md](CONNECTORS.md) for details.
```

Key principles for the README:
- The summary paragraph should be dense and specific — mention the exact number of scenarios, key methodologies, and built-in standards
- "Target Roles" shows who benefits and how, reinforcing the "role-oriented toolkit" positioning
- "Quick Commands" gives users an instant-use reference — include typical input examples where helpful
- "Skills" table should describe not just WHAT but HOW (the methodology/framework inside)
- "Connectors" section is optional — only include if the user mentioned external tools. Always note that the plugin works without connectors

This is the default template. If the user has specific preferences for README format, adapt accordingly.

### Step 5: Post-Creation Guidance

After installation, inform the user of two things:

**How to use it**: The plugin is available in QoderWork's plugin page. Invoke skills via `@` or `/` in the chat.

**It can evolve**: This is important — many users assume a plugin is a one-time creation. Make it clear that the plugin can be continuously maintained and improved:

- Adjustments based on usage feedback
- Adding new templates or reference materials over time
- Expanding with new Skills as needs grow
- Integrating with external tools later — when they connect new MCP services in QoderWork, the plugin can be updated to leverage them

---

## External Tool Integration (MCP Guidance)

This extends from the "external tools" question in Step 1. Since a plugin covers a role's daily work, the user likely interacts with various platforms. Bring this up naturally during the requirements conversation.

### Approach

Do NOT provide MCP configurations. Your role is to **help the user think about what tools they could benefit from connecting**. Based on their workflow, ask:

> "It sounds like this workflow may involve other tools. What platforms do you typically use? For example:
> - Communication: DingTalk, Feishu/Lark, Slack, WeChat Work…
> - Docs & knowledge: Notion, Yuque, Confluence…
> - Project management: Jira, Asana, Linear…
> - Email & calendar: Gmail, Outlook…
> - Data & spreadsheets: Google Sheets, Feishu Bitable…
> - Design: Figma…
>
> No need to decide everything now — tools can always be added later."

### How to Record

If the user mentions tools they use:
1. In the relevant SKILL.md, add conditional logic like: "If the user has connected XX's MCP, automatically send results to XX"
2. Do NOT pre-configure `.mcp.json` in the plugin — MCP setup is done by the user in QoderWork's Connector settings

If the user doesn't mention tools or isn't interested right now, skip this entirely. It does not block plugin creation.

---

## Plugin Directory Structure

```
{plugin-name}/
├── .qoder-plugin/
│   └── plugin.json          # Plugin metadata (required)
├── skills/                   # Skills directory
│   ├── skill-a/
│   │   ├── SKILL.md          # Core instruction file
│   │   └── references/       # Reference materials (templates, examples, docs)
│   │       ├── template.md
│   │       └── examples.md
│   └── skill-b/
│       └── SKILL.md
└── README.md                 # Usage documentation (optional but recommended)
```

Compatibility: Always use `.qoder-plugin/` for new plugins. The system also reads `.claude-plugin/plugin.json` for third-party plugin imports, but prefer `.qoder-plugin/` when creating.

---

## plugin.json Schema

```json
{
  "name": "my-plugin",
  "displayName": "My Plugin",
  "version": "1.0.0",
  "description": "English description of the plugin",
  "descriptionZh": "插件的中文描述",
  "author": {
    "name": "Author Name",
    "url": "https://example.com"
  },
  "category": "marketing",
  "tags": ["social-media", "content"],
  "skills": [
    "skills/skill-a",
    "skills/skill-b"
  ]
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Technical identifier, kebab-case (e.g., `marketing-toolkit`) |
| `displayName` | Yes | Display name shown in UI, supports localized text |
| `version` | Yes | Semantic version (e.g., `1.0.0`) |
| `description` | Yes | English description |
| `descriptionZh` | No | Chinese description |
| `author` | No | Author info with `name` and optional `url` |
| `category` | No | Category: marketing, finance, legal, engineering, etc. |
| `customizedFrom` | No | Only set when customized from a built-in plugin — use the original plugin's `displayName`. Do NOT set for brand-new plugins |
| `tags` | No | Array of tags for search/filter |
| `skills` | No | Array of relative paths to skill directories |
| `commands` | No | Array of relative paths to command files |

---

## SKILL.md Format

Each skill is a directory under `skills/` containing a `SKILL.md` with frontmatter:

```markdown
---
name: my-skill-name
version: 1.0.0
description: What this skill does in English
description_zh: 这个技能做什么的中文描述
user-invocable: true
argument-hint: Brief hint of expected input
---

# Skill Title

Detailed instructions for the AI agent...
```

| Field | Required | Default | Description |
|-------|----------|---------|-------------|
| `name` | Yes | - | Skill identifier |
| `version` | No | - | Version number for tracking iterations |
| `description` | Yes | - | English description |
| `description_zh` | No | - | Chinese description |
| `user-invocable` | No | `true` | Set to `false` for internal knowledge-base skills that are only referenced by other skills, hidden from the user menu |
| `argument-hint` | No | - | Hint shown in the mention menu (e.g., "Upload a contract file or paste contract text") |

---

## Skill Content Guidelines

The body of SKILL.md is the core — it determines how well AI performs with this Skill.

### Write What AI Doesn't Already Know

AI has broad general knowledge. A Skill's value is the **incremental, domain-specific information** it injects: your industry standards, your template formats, your workflow rules, your quality criteria.

Avoid vague instructions like "analyze carefully" or "ensure high quality" — these add nothing. Be specific: which framework to use, which dimensions to evaluate, what output format to follow, what constitutes pass/fail.

### Progressive Loading with references/

Keep SKILL.md under 500 lines. For extensive reference materials (templates, examples, knowledge bases, regulatory docs), use the `references/` directory. AI loads only SKILL.md at startup and reads reference files on demand via markdown links.

Example structure:

```
skills/write-prd/
├── SKILL.md                     # Main instructions: workflow, rules, format
└── references/
    ├── prd-template.md          # PRD template
    ├── good-example.md          # Example of a good PRD
    └── review-checklist.md      # Quality checklist
```

Reference in SKILL.md via links:
```markdown
Follow the structure in [PRD Template](references/prd-template.md).
After drafting, verify against the [Quality Checklist](references/review-checklist.md).
```

Rule of thumb:
- **SKILL.md**: Execution flow, decision rules, output format definitions, conditional branches
- **references/**: Full templates, detailed examples, domain knowledge docs, regulatory text, checklists

### Flexibility Over Rigidity

Good skills handle varied inputs and scenarios:

- Use conditional branches for different cases: if input is X → path A; if input is Y → path B
- Define clearly but don't over-constrain: specify "output must contain these 5 sections" but don't dictate sentence counts
- Provide fallback logic: what AI should do when information is incomplete or the scenario is unexpected

### Internal Knowledge-Base Skills

For knowledge-intensive domains (legal, medical, finance), create internal skills with `user-invocable: false` to hold domain knowledge. Other skills reference them at runtime, but users don't see them in the menu:

```
skills/legal-knowledge/          # user-invocable: false — hidden from users
├── SKILL.md                     # Index and usage notes
└── references/
    ├── contract-law-essentials.md
    └── common-clauses.md

skills/draft-contract/           # user-invocable: true — references legal-knowledge
skills/review-contract/          # user-invocable: true — references legal-knowledge
```

---

## Plugin Modes

Two typical patterns based on task complexity. **Default to Simple Tool Mode** — only suggest Orchestration Mode when the project-mode signals are clearly met. When in doubt, choose simple.

### Mode 1: Simple Tool Mode (default)

Skills are independent; users invoke whichever they need. Suitable for most scenarios.

```
marketing-plugin/
├── skills/
│   ├── write-copy/SKILL.md        # Write marketing copy
│   ├── analyze-data/SKILL.md      # Analyze campaign data
│   └── plan-campaign/SKILL.md     # Plan marketing campaign
```

Use when: Skills have no strong dependencies, no fixed execution order, no shared state across skills.

### Mode 2: Project Orchestration Mode

When the task involves multiple dependent stages and requires progress tracking, add an **orchestrator skill** to manage the workflow. Suitable for legal cases, investment projects, product launch processes, etc.

```
legal-case-plugin/
├── skills/
│   ├── case-orchestrator/          # Orchestrator: manages the full workflow
│   │   ├── SKILL.md
│   │   └── references/
│   │       └── workflow-stages.md  # Stage definitions and dependencies
│   ├── case-analysis/SKILL.md      # Stage: case analysis
│   ├── evidence-organizer/SKILL.md # Stage: evidence organization
│   ├── defense-brief/SKILL.md      # Stage: defense brief
│   └── legal-knowledge/            # Internal knowledge base (user-invocable: false)
│       ├── SKILL.md
│       └── references/
```

The orchestrator skill is responsible for:
- Maintaining project state (a progress file in the working directory tracking each stage's status, outputs, and timestamps)
- Guiding the user to the next step, specifying what prerequisite outputs are needed
- Ensuring downstream stages can locate and reference upstream outputs
- Optionally syncing status to external tools if the user has connected relevant MCP services (e.g., DingTalk tasks, Feishu projects)

Use when: Stages have sequential dependencies (B requires A to complete), overall progress needs tracking, outputs need to be passed between stages. Note: multiple stages that are independent of each other (e.g., 5 parallel analysis tasks) should still use Simple Tool Mode.

When you determine Orchestration Mode is appropriate, explain it to the user:

> "Your scenario involves multiple work stages with dependencies between them. I recommend adding a project management Skill to coordinate the workflow — it will automatically track progress after each stage, and you can check the overall status at any time. Would you like this design?"

---

## Installation

User-created plugins are installed to `~/.qoderwork/plugins-custom/`. Process:

1. Create the directory at `~/.qoderwork/plugins-custom/{plugin-name}/`
2. Create `.qoder-plugin/plugin.json` with metadata
3. Create `skills/` and/or `commands/` directories with content
4. Optionally add `README.md`
5. Call `qoderwork.settings.plugins.install_from_path` with the plugin directory path to register and activate
6. Inform the user that the plugin is installed and available

Important:
- `~/.qoderwork/plugins/` is reserved for built-in plugin copies — do not write to it
- Do NOT manually split plugin content into separate `~/.qoderwork/skills/` files or `~/.qoderwork/mcp.json` — always install as a complete plugin directory via `install_from_path`

---

## Customizing an Existing Plugin

1. Read the existing plugin's `plugin.json` to understand its structure
2. Ask the user what they want to change or add
3. Set `customizedFrom` to the original plugin's `displayName` (e.g., `"customizedFrom": "投研分析"`)
4. Give the customized plugin its own `displayName` and `name`
5. Modify the relevant files
6. Preserve existing functionality unless explicitly asked to remove it

Note: Only set `customizedFrom` when derived from a built-in plugin. For brand-new plugins, do NOT set this field — the UI shows "Custom" automatically.

## Editing a Specific Skill or Command

1. Read the current file content
2. Ask the user what changes they want
3. Edit while preserving frontmatter format
4. Validate that changes don't break the structure

---

## Command .md Format (Legacy)

New plugins should prefer `skills/` with `user-invocable` and `argument-hint`. The `commands/` directory is still supported for backward compatibility.

```markdown
---
description: What this command does in English
description_zh: 这个指令做什么的中文描述
---

# Command Content

Content injected when the user invokes this command via /command-name...
```

---

## Best Practices

1. **Clear naming**: Use descriptive kebab-case for plugins, skills, and commands
2. **Bilingual descriptions**: Provide both `description` and `descriptionZh`/`description_zh`
3. **Focused scope**: Each plugin targets a specific industry scenario or workflow
4. **Single responsibility**: Each skill handles one specific capability
5. **Leverage references/**: Put templates, examples, and knowledge docs in `references/` to keep SKILL.md concise
6. **Document your plugin**: Include a README.md explaining use cases and examples
