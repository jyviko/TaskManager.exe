Spawn an agent to work on a specific task, optionally in an isolated worktree for true parallelism.

Usage: `/delegate <task-slug> [--worktree] [--background]`

## Workflow

1. **Load task** — Read `.agent-files/tasks/TASK_<slug>.md`
   - Verify status is `planned` or `in_progress`
   - Check dependencies are met (dependent tasks are `complete`)
   - If dependencies unmet, report which and stop

2. **Update task status** — Set Status: `in_progress`

3. **Spawn agent** via the Agent tool:
   - `--worktree` → set `isolation: "worktree"` for parallel-safe isolation
   - `--background` → set `run_in_background: true`
   - Without flags: runs in foreground, shared working directory

4. **On agent completion:**
   - Read handoff at `.agent-files/handoffs/HANDOFF_<task-slug>.md`
   - Update task status → `complete` or `blocked`
   - Update STATUS.md
   - If worktree: merge results back (see `/merge`)
   - Check if this unblocks downstream tasks — report them

## Agent Prompt

The delegated agent receives:

```
DELEGATED TASK: <task-slug>

## Spec
<full contents of TASK_<slug>.md>

## Context
<relevant STATUS.md sections, dependency outputs>

## Instructions
1. Read the task spec
2. Implement the work
3. Run /simplify to review code quality
4. Write results to: .agent-files/handoffs/HANDOFF_<task-slug>.md
5. Run: taskman describe "<task-slug> done"

## Handoff Format
Write to .agent-files/handoffs/HANDOFF_<task-slug>.md:

# HANDOFF: <task-slug>
updated: <timestamp>
commit: <sha>
status: complete | blocked

## files
- <path> (created|modified|deleted)

## approach
<what you did and why>

## output
<anything downstream tasks need: API shapes, file paths, schemas>

## concerns
<blockers, risks, open questions>
```

## Parallel Delegation

Delegate multiple independent tasks in one message for true parallelism:

```python
# Both run simultaneously in isolated worktrees
Agent(prompt="DELEGATED TASK: auth-api ...", isolation="worktree", run_in_background=True)
Agent(prompt="DELEGATED TASK: auth-ui ...", isolation="worktree", run_in_background=True)
```

Monitor progress via STATUS.md. Each agent updates its task file and writes a handoff.

## Persistence

- Handoff files are the durable record of what each agent did
- Task files track status across all agents
- STATUS.md is the shared coordination board
- All of this survives worktree cleanup because .agent-files/ is synced via `taskman sync`
- Run `taskman sync` after merging results to checkpoint the state
