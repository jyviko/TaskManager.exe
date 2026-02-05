Implement a task with multi-persona code review.

Usage: `/taskman implement <task-slug> [--max-iter=N]`

Parameters:
- `<task-slug>` - Task slug (loads from `.agent-files/tasks/TASK_<slug>.md`) or full file path
- `--max-iter=N` - Maximum review-fix iterations (default: 3)

## Workflow

1. **Load task**
   - From `.agent-files/tasks/TASK_<slug>.md` if slug provided
   - From file path if full path provided
   - If no argument, list available tasks and prompt for selection

2. **Analyze task type** - Determine which reviewers are relevant:
   | Task signals | Reviewers |
   |--------------|-----------|
   | UI, styling, user flows, components | UX/UI Expert, Frontend Developer |
   | API, data models, services, DB | Backend Engineer, System Architect |
   | Tests, validation, edge cases | QA Engineer |
   | LLM prompts, AI features | GenAI Expert, Prompt Engineer |
   | Infrastructure, scaling, security | System Architect, Backend Engineer |

3. **Update task status**
   - Set Status: in_progress
   - Record attempt start in Attempts section

4. **Implement** - Execute the implementation per task spec

5. **Run: taskman describe "impl: <task-slug> checkpoint"**

6. **Review** - For each relevant persona (see `personas/` for detailed prompts):
   - Adopt persona perspective
   - Evaluate implementation against persona's concerns
   - Record findings with severity: `[critical]` `[important]` `[minor]`

7. **Iterate** - If critical issues found (max `--max-iter` iterations, default 3):
   - Fix critical issues
   - Re-run affected persona reviews
   - Repeat until no critical issues OR max iterations reached
   - If max iterations reached with unresolved criticals → flag in task Notes, handoff

8. **Finalize**
   - Update task file: Attempts section with outcome
   - If complete: use `/taskman complete <slug>`
   - If blocked/needs more work: use `/taskman handoff <slug>`

## Review Output Format

```markdown
## <Persona> Review

### Assessment: PASS | CONCERNS | BLOCKERS

### Findings
- [severity] description
  - recommendation

### Summary
<1-2 sentences>
```

## Persona Selection Logic

Do NOT apply all personas. Select based on task characteristics:

**Frontend task** (components, UI, forms, styling):
→ Frontend Developer, UX/UI Expert, QA Engineer

**Backend task** (API, services, data, auth):
→ Backend Engineer, System Architect, QA Engineer

**Full-stack task** (crosses boundaries):
→ Full-stack Developer, System Architect, QA Engineer

**AI/LLM task** (prompts, model integration, AI features):
→ GenAI Expert, Prompt Engineer, QA Engineer

**Infra/DevOps task** (deployment, scaling, config):
→ System Architect, Backend Engineer

**Pure refactor** (no behavior change):
→ System Architect only (unless scope warrants more)

## Quick Reference

Read persona details: `personas/<persona>.md`

| Persona | Focus |
|---------|-------|
| qa-engineer | Test coverage, edge cases, error handling |
| ux-ui-expert | Usability, accessibility, design consistency |
| frontend-dev | Component arch, state, perf, patterns |
| fullstack-dev | End-to-end integration, data flow, API contracts |
| system-architect | Design patterns, scalability, coupling |
| backend-engineer | Data integrity, API design, security |
| genai-expert | LLM integration, tokens, fallbacks |
| prompt-engineer | Prompt structure, clarity, edge cases |
