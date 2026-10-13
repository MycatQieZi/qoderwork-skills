---
name: edict-sanshen
version: 1.0.0
description: Orchestrates complex multi-step tasks using a Three Departments and Six Ministries (Sanshen Liubu) workflow with planning, mandatory audit, parallel execution, and real-time kanban dashboard. Use when the user presents a complex task requiring decomposition, quality review, multi-agent execution, or when the user mentions multi-agent collaboration, task orchestration, workflow automation, or explicitly asks to use the edict/sanshen system.
description_zh: 用「三省六部」工作流编排复杂的多步任务：规划 → 强制审计 → 并行执行 → 实时看板。当用户提出需要拆解的复杂任务、需要质量复核或多智能体执行，或提到多智能体协作、任务编排、工作流自动化、明确要求使用 edict/sanshen 体系时使用。
---

# 三省六部 · Edict Workflow

## When to Apply

Apply this skill when the user:
- Presents a **complex task** needing decomposition into subtasks
- Explicitly mentions "三省六部", "edict", "sanshen", "workflow", "multi-agent", or "task orchestration"
- Needs a task to go through **planning, review, and execution** stages
- Wants a **kanban dashboard** or audit trail for task tracking

Do NOT apply for simple queries, greetings, or single-step tasks (e.g., "what's the weather", "hello").

## Architecture Overview

```
User (Emperor) -> Taizi (Sort) -> Zhongshu (Plan) -> Menxia (Audit) -> Shangshu (Dispatch) -> Liubu (Execute) -> Memorial (Archive)
```

| Role | QoderWork Implementation |
|------|--------------------------|
| Emperor | User |
| Taizi (Sorter) | Main conversation (lightweight filtering) |
| Zhongshu (Planner) | Subagent spawned via Task tool |
| Menxia (Auditor) | Subagent spawned via Task tool |
| Shangshu (Dispatcher) | Main conversation (coordination) |
| Liubu (Six Ministries) | Parallel subagents spawned via Task tool |
| Kanban | Auto-generated HTML dashboard |
| Memorial | Auto-generated Markdown archive |

## Core Scripts

All scripts are in `scripts/` directory. Use absolute paths when invoking.

### Create an Edict (Task)
```bash
python scripts/edict_cli.py create "TITLE" "CONTENT"
```
Returns the edict ID (e.g., `ED-20260423-143052`).

### Transition State
```bash
python scripts/edict_cli.py transition ED-XXXXX STATUS DEPT --note "NOTE"
```
Statuses: `draft`, `taizi_sorted`, `zhongshu_planned`, `menxia_reviewing`, `menxia_rejected`, `menxia_approved`, `shangshu_dispatching`, `executing`, `reviewing`, `completed`, `cancelled`, `blocked`, `stopped`

Departments: `user`, `taizi`, `zhongshu`, `menxia`, `shangshu`, `hubu`, `libu`, `bingbu`, `xingbu`, `gongbu`, `libu_hr`

### Generate Kanban
```bash
python scripts/edict_cli.py kanban
```
Outputs path to `dashboard/kanban.html`.

### Export Memorial
```bash
python scripts/edict_cli.py memorial ED-XXXXX
```
Outputs path to `data/memorials/ED-XXXXX.md`.

### List/Show Edicts
```bash
python scripts/edict_cli.py list
python scripts/edict_cli.py show ED-XXXXX
```

## Workflow Steps

### Step 0: Taizi Sorting
Determine if the user's request is a **chat** (simple query) or an **edict** (complex task requiring multi-step orchestration).

- If chat: Respond directly. Do NOT create an edict.
- If edict: Extract a concise title and the full content, then proceed to Step 1.

### Step 1: Create Edict
Run `edict_cli.py create` to create the task record. Save the returned edict ID for all subsequent operations.

Then transition to `taizi_sorted`.

### Step 2: Zhongshu Planning
Spawn a subagent (Task tool) with the Zhongshu role. Pass the edict content and instruct it to output a JSON plan following the template in `reference.md#zhongshu-prompt`.

After receiving the plan:
1. Save it to the edict JSON using Python one-liner to update the `zhongshu_plan` field
2. Transition to `zhongshu_planned`

### Step 3: Menxia Audit
Spawn a subagent (Task tool) with the Menxia role. Pass both the original edict content and the Zhongshu plan. Instruct it to output a JSON audit result following `reference.md#menxia-prompt`.

Rules:
- Score >= 80 and no critical issues -> `menxia_approved`
- Score < 80 or any critical issue -> `menxia_rejected`

If rejected:
1. Transition to `menxia_rejected`
2. Return to Step 2 with the Menxia feedback for rework (max 3 rejection cycles)
3. After 3 rejections, escalate to user

If approved:
1. Transition to `menxia_approved`

### Step 4: Shangshu Dispatch
Analyze the approved plan's `subtasks` array. Group by dependencies to identify parallel execution groups.

Transition to `shangshu_dispatching`, then `executing`.

### Step 5: Liubu Parallel Execution
Spawn **parallel** subagents via Task tool — one per subtask. Each subagent receives:
- The Liubu role prompt (see `reference.md#liubu-prompt`)
- Its specific subtask details
- The original edict content for context

Wait for all parallel tasks to complete. Collect results.

Save results to the edict's `subtask_results` field.

### Step 6: Review and Complete
Review aggregated results. If any subtask failed or quality is insufficient, transition back to `executing` for rework.

If all good:
1. Transition to `reviewing`
2. Transition to `completed`
3. Run `edict_cli.py memorial` to generate the archive
4. Run `edict_cli.py kanban` to refresh the dashboard
5. **Automatically present the kanban dashboard to the user** — read the `dashboard/kanban.html` file and use the file presentation tool to display it as an interactive card. Do NOT just show the file path; the user should see the kanban directly.
6. Present a summary to the user

### Step 7: User Intervention (Anytime)
The user may intervene at any stage:
- "Cancel this task" -> transition to `cancelled`
- "Stop / Pause" -> transition to `stopped`
- "Resume" -> transition back to `executing`
- "Show dashboard" -> open `dashboard/kanban.html`
- "Show memorial" -> open `data/memorials/ED-XXXXX.md`

## State Machine Constraints

The Python state_manager enforces these rules. Never attempt illegal transitions:
- `draft` -> `taizi_sorted` -> `zhongshu_planned` -> `menxia_reviewing` -> `menxia_approved` -> `shangshu_dispatching` -> `executing` -> `reviewing` -> `completed`
- `menxia_reviewing` may go to `menxia_rejected`, which loops back to `zhongshu_planned`
- `executing` may go to `blocked` or `stopped`
- Any non-terminal state may go to `cancelled`

## Data Fields to Maintain

Always keep the edict JSON updated with these fields:
- `zhongshu_plan`: The planner's JSON output
- `menxia_review`: The auditor's JSON output
- `subtasks`: Array of subtask definitions
- `subtask_results`: Dict mapping dept_id to result string

## Kanban and Memorial

After every significant state change, consider refreshing the kanban. After completion, always generate the memorial.

- Kanban path: `dashboard/kanban.html` (single-file HTML, zero dependencies)
- Memorial path: `data/memorials/ED-XXXXX.md` (Markdown with full audit trail)

## Additional Resources

- For detailed role prompts, see [reference.md](reference.md)
- For usage examples, see [examples.md](examples.md)
