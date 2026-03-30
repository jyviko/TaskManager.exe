Merge worktree code AND agent files back to base branch.

Usage: `/taskman merge`

No parameters needed - auto-detects context.

## Auto-Detection

The agent detects everything automatically:

```bash
# Detect if in a worktree
git worktree list --porcelain | grep -q "worktree $(pwd)" && echo "In worktree"
# or for jj
jj workspace list  # shows current workspace

# Find main repo (worktree source)
MAIN_REPO=$(git worktree list --porcelain | grep -m1 "worktree " | cut -d' ' -f2)
# or for jj
jj workspace root  # if available, else parse from .jj/

# Find base branch (where worktree branched from)
# git: check upstream or merge-base with main/develop
# jj: jj log -r 'roots(@)' to find branch point
```

## Problem

When working in a git/jj worktree:
- Code changes merge normally via git/jj
- `.agent-files/` is gitignored → stays isolated in worktree
- After code merge, agent context (tasks, memory, status) is lost

This command merges BOTH code and agent files.

## Workflow

### 1. Detect context (automatic)
```bash
# Confirm we're in a worktree
CURRENT=$(pwd)
MAIN_REPO=$(git worktree list --porcelain | grep -m1 "worktree " | cut -d' ' -f2)

if [ "$CURRENT" = "$MAIN_REPO" ]; then
  echo "Error: Not in a worktree. Run from worktree directory."
  exit 1
fi

# Detect base branch
BASE_BRANCH=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@')
# fallback: develop or main
BASE_BRANCH=${BASE_BRANCH:-develop}

echo "Worktree: $CURRENT"
echo "Main repo: $MAIN_REPO"
echo "Base branch: $BASE_BRANCH"
```

### 2. Pre-merge validation
```bash
# Check for uncommitted changes
jj st || git status

# Check agent files exist
ls .agent-files/ || echo "No agent files to merge"
ls "$MAIN_REPO/.agent-files/" || echo "No agent files in main repo"
```

### 3. Merge code (choose one)

**jj (preferred):**
```bash
# Get current change ID
CHANGE=$(jj log -r @ --no-graph -T 'change_id.short()')

# From main repo, rebase the worktree change onto base branch
jj rebase -r "$CHANGE" -d "$BASE_BRANCH" --repository "$MAIN_REPO"
```

**git:**
```bash
BRANCH=$(git branch --show-current)
git -C "$MAIN_REPO" merge "$BRANCH"
```

### 4. Fuse agent files

Agent files require intelligent merging, not overwriting.

#### STATUS.md
Merge task indexes - combine, dedupe, resolve conflicts:
```bash
# Read both (CURRENT = worktree, MAIN_REPO = main)
MAIN_STATUS="$MAIN_REPO/.agent-files/STATUS.md"
WT_STATUS=".agent-files/STATUS.md"

# Fuse: take worktree updates for tasks it worked on
# Keep main's entries for unrelated tasks
# Resolve conflicts (same task updated in both) → prefer most recent
```

#### *_MEM.md files
Append new entries, dedupe, merge indexes:
- LONGTERM_MEM.md - architectural knowledge (rarely conflicts)
- MEDIUMTERM_MEM.md - patterns, topic index (merge indexes)

#### tasks/
```bash
# Copy completed/updated tasks from worktree to main
# Archive if marked complete
# Update if same task exists with newer state
for task in .agent-files/tasks/TASK_*.md; do
  slug=$(basename "$task")
  if [ -f "$MAIN_REPO/.agent-files/tasks/$slug" ]; then
    # Compare timestamps/status, take newer
  else
    cp "$task" "$MAIN_REPO/.agent-files/tasks/"
  fi
done
```

#### topics/
```bash
# Merge new topics, append to existing
for topic in .agent-files/topics/*.md; do
  slug=$(basename "$topic")
  if [ -f "$MAIN_REPO/.agent-files/topics/$slug" ]; then
    # Append new entries (dedupe by problem: line)
  else
    cp "$topic" "$MAIN_REPO/.agent-files/topics/"
  fi
done
```

#### handoffs/
Worktree handoffs are session-specific. Options:
- **Discard** - handoff served its purpose
- **Archive** - move to handoffs/_archive/ for reference
- **Merge** - if continuing same work stream

### 5. Sync merged agent files (from main repo)
```bash
cd "$MAIN_REPO"
taskman sync "merge: incorporated worktree $(basename $CURRENT)"
```

### 6. Cleanup worktree (optional)
```bash
# If done with worktree
git worktree remove "$CURRENT"
# or for jj
jj workspace forget $(basename "$CURRENT")
```

## Fuse Strategy by File Type

| File | Strategy |
|------|----------|
| STATUS.md | Merge task entries, prefer recent for conflicts |
| LONGTERM_MEM.md | Append, dedupe |
| MEDIUMTERM_MEM.md | Merge topic index, append patterns |
| tasks/TASK_*.md | Copy new, update existing (prefer newer status) |
| topics/TOPIC_*.md | Copy new, append entries to existing |
| handoffs/ | Archive or discard |

## Conflict Resolution

When same content modified in both:

1. **Task status conflict** → prefer: complete > in_progress > planned
2. **Memory entries** → keep both, dedupe exact matches
3. **Topic entries** → append all, dedupe by `problem:` line
4. **STATUS.md priorities** → prefer worktree (it has fresher context)

## Example

```bash
# You're working in worktree ~/src/myproject-feature-x
pwd  # ~/src/myproject-feature-x

# Just run:
/taskman merge

# Agent auto-detects:
# - Current dir is worktree: ~/src/myproject-feature-x
# - Main repo: ~/src/myproject
# - Base branch: develop

# Then:
# 1. jj rebase worktree changes onto develop
# 2. Reads both .agent-files/ directories
# 3. Fuses STATUS.md, *_MEM.md, tasks/, topics/
# 4. Syncs in main repo: taskman sync "merge: feature-x"
# 5. Optionally cleans up worktree
```

## When NOT to Merge Agent Files

- Worktree was abandoned (no useful context)
- Worktree task unrelated to main work stream
- Experimental spike (discard memory)

In these cases, just merge code: `jj rebase` or `git merge`
