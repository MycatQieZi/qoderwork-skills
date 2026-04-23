# Examples: Edict Sanshen Workflow

## Example 1: Designing a User Registration System

**User edict:**
> "Design a user registration system with RESTful API (FastAPI), PostgreSQL database, JWT authentication, complete test cases, and deployment documentation."

**Step 0 - Taizi sorting:**
This is a complex multi-step task. Create an edict.

**Step 1 - Create edict:**
```bash
python scripts/edict_cli.py create "Design User Registration System" "Design a user registration system with RESTful API (FastAPI), PostgreSQL database, JWT authentication, complete test cases, and deployment documentation."
# Returns: ED-20260423-155359
```

```bash
python scripts/edict_cli.py transition ED-20260423-155359 taizi_sorted taizi --note "Confirmed as formal edict"
```

**Step 2 - Zhongshu planning:**
Spawn subagent with Zhongshu prompt + edict content.

Zhongshu returns:
```json
{
  "analysis": "Need a complete user registration system with API, DB, auth, tests, and deployment.",
  "task_type": "code",
  "subtasks": [
    {"id": "sub-1", "title": "API Design", "assignee": "bingbu", "deliverable": "FastAPI endpoints for register/login/verify"},
    {"id": "sub-2", "title": "Database Modeling", "assignee": "bingbu", "deliverable": "SQLAlchemy models with migrations"},
    {"id": "sub-3", "title": "JWT Authentication", "assignee": "bingbu", "deliverable": "JWT token generation and verification"},
    {"id": "sub-4", "title": "Test Cases", "assignee": "libu", "deliverable": "pytest unit and integration tests"},
    {"id": "sub-5", "title": "Deployment Config", "assignee": "gongbu", "deliverable": "Dockerfile + docker-compose + CI/CD"},
    {"id": "sub-6", "title": "Security Audit", "assignee": "xingbu", "deliverable": "Security review report"}
  ]
}
```

Save plan and transition:
```bash
python scripts/edict_cli.py transition ED-20260423-155359 zhongshu_planned zhongshu --note "Decomposed into 6 subtasks"
```

**Step 3 - Menxia audit:**
Spawn subagent with Menxia prompt + edict + plan.

Menxia returns:
```json
{
  "verdict": "approved",
  "score": 88,
  "dimensions": {
    "completeness": {"score": 95, "comment": "All requirements covered"},
    "feasibility": {"score": 90, "comment": "All subtasks are achievable"}
  },
  "issues": [],
  "rationale": "Plan is comprehensive and well-structured. Approved."
}
```

```bash
python scripts/edict_cli.py transition ED-20260423-155359 menxia_reviewing menxia --note "Review started"
python scripts/edict_cli.py transition ED-20260423-155359 menxia_approved menxia --note "Plan approved"
```

**Step 4 - Shangshu dispatch:**
```bash
python scripts/edict_cli.py transition ED-20260423-155359 shangshu_dispatching shangshu --note "Dispatch to bingbu, libu, gongbu, xingbu"
python scripts/edict_cli.py transition ED-20260423-155359 executing shangshu --note "Execution started"
```

**Step 5 - Liubu parallel execution:**
Spawn 4 parallel subagents:
- Task A: bingbu executes sub-1, sub-2, sub-3
- Task B: libu executes sub-4
- Task C: gongbu executes sub-5
- Task D: xingbu executes sub-6

Collect results and save to `subtask_results`.

**Step 6 - Complete:**
```bash
python scripts/edict_cli.py transition ED-20260423-155359 reviewing shangshu --note "Aggregating results"
python scripts/edict_cli.py transition ED-20260423-155359 completed shangshu --note "All subtasks passed"
python scripts/edict_cli.py memorial ED-20260423-155359
python scripts/edict_cli.py kanban
```

Present summary to user.

---

## Example 2: Rejected Plan (Menxia Rejection)

**User edict:**
> "Build an internal chatbot that connects to Feishu."

**Zhongshu plan:**
Decomposes into 3 simple subtasks without error handling or concurrency planning.

**Menxia audit:**
```json
{
  "verdict": "rejected",
  "score": 65,
  "issues": [
    {"severity": "critical", "category": "risk", "description": "No error handling or retry mechanism", "suggestion": "Add try/catch and exponential backoff"},
    {"severity": "major", "category": "completeness", "description": "No LLM provider specified", "suggestion": "Specify provider and API cost estimate"}
  ],
  "rework_focus": "Add error handling, retry logic, concurrency safety, and LLM provider selection"
}
```

**Action:**
Transition to `menxia_rejected`. Return to Step 2 with rework feedback. Zhongshu revises plan. Menxia re-reviews.

---

## Example 3: Simple Query (Taizi Direct Response)

**User:**
> "What's the weather today?"

**Taizi sorting:**
Simple factual query. No edict needed. Respond directly.

---

## Example 4: User Intervention

**User during execution:**
> "Cancel the registration system task."

**Action:**
```bash
python scripts/edict_cli.py transition ED-20260423-155359 cancelled user --note "User cancelled"
python scripts/edict_cli.py kanban
```

**User:**
> "Show me the dashboard."

**Action:**
```bash
python scripts/edict_cli.py kanban
# Open the generated kanban.html path
```

---

## Example 5: Data Analysis Task

**User edict:**
> "Generate a Q1 quarterly data report with sales, user growth, and retention metrics. Include interactive charts."

**Zhongshu plan assigns:**
- hubu: Data cleaning, statistical calculations, chart generation
- libu: Report document writing, PowerPoint creation

**Parallel execution:**
- Task A: hubu processes data and generates charts
- Task B: libu writes narrative report (can start after hubu delivers key metrics)

**Result:** Combined data report with charts and documentation.
