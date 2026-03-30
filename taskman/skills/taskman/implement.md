Implement a single task with code quality review.

Usage: `/implement <task-slug>`

For multi-task orchestration, use `/plan` to decompose and `/delegate` to parallelize.

## Workflow

1. **Load task**
   - From `.agent-files/tasks/TASK_<slug>.md` if slug provided
   - From file path if full path provided
   - If no argument, list available tasks and prompt for selection

2. **Update task status**
   - Set Status: `in_progress`
   - Record attempt start in Attempts section

3. **Implement** — Execute per task spec. Use existing codebase patterns.

4. **Checkpoint** — Run: `taskman describe "impl: <task-slug> checkpoint"`

5. **Review** — Run `/simplify` to review changed code for quality, reuse, and efficiency. It finds and fixes issues automatically.

6. **Validate** — Run tests, linters, type checks as appropriate for the codebase.

7. **Iterate** — If `/simplify` or validation found issues:
   - Fix them
   - Re-run validation
   - Max 3 iterations, then flag remaining issues in task Notes and ask user for direction

8. **Finalize**
   - Update task file: Attempts section with outcome
   - If complete: `/complete <slug>`
   - If blocked: `/handoff <slug>`

## Persona Reviews (optional)

For tasks needing specialized review beyond `/simplify` (security audits, UX review, etc.), persona guides are available in `personas/`:

| Persona | When to use |
|---------|-------------|
| system-architect | Major structural changes, scalability concerns |
| backend-engineer | Data integrity, API design, security |
| frontend-dev | Component arch, state management, performance |
| ux-ui-expert | Usability, accessibility |
| qa-engineer | Test coverage, edge cases |
| genai-expert | LLM integration, token efficiency |
| prompt-engineer | Prompt design, robustness |
| fullstack-dev | Cross-layer integration |

To use: read the persona file, adopt that perspective, review the changes. This is manual and optional — `/simplify` handles the common case.
