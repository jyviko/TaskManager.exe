Decompose a goal into visible, manageable tasks. Replaces built-in opaque planning.

Usage: `/plan <goal-description>`

## Workflow

1. **Analyze the goal** — Understand scope, components, constraints

2. **Decompose into tasks** — Each task = one TASK file in `.agent-files/tasks/`:
   - Right-sized: completable by one agent session
   - Clear "done" definition
   - Dependencies explicit

3. **Identify parallel streams** — Tasks with no dependencies between them can run simultaneously via `/delegate --worktree`

4. **Create TASK files** — For each task, write `.agent-files/tasks/TASK_<slug>.md`:
   ```markdown
   # TASK: <title>

   ## Meta
   Status: planned
   Priority: P0|P1|P2
   Created: YYYY-MM-DD

   ## Dependencies
   depends: TASK_<slug>.md
   blocks: TASK_<slug>.md
   parallel_group: <group-name>

   ## Problem
   <what, why, acceptance criteria>

   ## Design
   <approach, constraints>

   ## Checklist
   - [ ] item
   ```

5. **Update STATUS.md** — Add plan overview with execution order and parallel streams

6. **Present plan to user** — Show task list, dependency graph, parallel opportunities. **Wait for user approval/edits before any execution.**

7. **Run:** `taskman sync "plan: <goal summary>"`

## Decomposition Principles

**Dependency analysis:**
| Pattern | Parallel? |
|---------|-----------|
| Different layers (FE + BE) | Yes |
| Independent features | Yes |
| Shared data model | Coordinate — may conflict |
| Producer -> consumer | No — sequential |
| Same files modified | No — will conflict |

**Right-sizing:** Too big = hard to delegate. Too small = overhead exceeds value. Each task should map to a meaningful deliverable.

## Example

Goal: "Add user authentication with OAuth + email/password"

```
TASK_auth-data-model.md     [P0, no deps]
TASK_oauth-provider.md      [P1, depends: data-model]  } parallel
TASK_email-auth.md          [P1, depends: data-model]  }
TASK_auth-ui.md             [P1, depends: oauth, email]
TASK_auth-tests.md          [P2, depends: all above]
```

STATUS.md:
```markdown
## Active Plan: User Authentication

### Execution Order
1. TASK_auth-data-model (P0) — start immediately
2. TASK_oauth-provider + TASK_email-auth (P1) — parallel after data model
3. TASK_auth-ui (P1) — after both auth backends
4. TASK_auth-tests (P2) — after all implementation
```

## After Planning

User reviews and edits TASK files directly, then:
- `/delegate <task>` — spawn agent for a task (parallel with `--worktree`)
- `/implement <task>` — implement hands-on in current session
