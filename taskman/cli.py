import argparse

from taskman import core


def _get_version() -> str:
    try:
        from importlib.metadata import version
        return version("taskmanager-exe")
    except Exception:
        return "dev"


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="taskman",
        description="Version-controlled task management for AI agents.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
quick start:
  taskman init                    Create .agent-files/ in current project
  taskman install-skills claude   Install skill files for Claude Code
  taskman install-mcp claude      Install MCP server for Claude Code

workflow:
  taskman tasks                   See all tasks across worktrees
  taskman sync "checkpoint" --all Sync state across all worktrees
  taskman describe "milestone"    Create named checkpoint

worktrees:
  taskman wt feature-x --new     Create worktree with .agent-files workspace
  taskman wt-list                 Show worktree health
  taskman wt-rm feature-x        Merge and cleanup worktree
""",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {_get_version()}")
    subparsers = parser.add_subparsers(dest="command", metavar="command")

    # --- Setup ---
    subparsers.add_parser("init", help="create .agent-files/ jj repo in current project")
    subparsers.add_parser("migrate", help="migrate from old clone/push model to jj workspaces")

    install_mcp = subparsers.add_parser("install-mcp", help="install MCP server config")
    install_mcp.add_argument("agent", choices=["claude", "cursor", "codex"],
                             help="target agent/editor")

    install_skills = subparsers.add_parser("install-skills", help="install skill files")
    install_skills.add_argument("agent", choices=["claude", "codex", "pi"],
                                help="target agent/editor")

    uninstall_mcp = subparsers.add_parser("uninstall-mcp", help="remove MCP server config")
    uninstall_mcp.add_argument("agent", choices=["claude", "cursor", "codex"],
                               help="target agent/editor")

    uninstall_skills = subparsers.add_parser("uninstall-skills", help="remove skill files")
    uninstall_skills.add_argument("agent", choices=["claude", "codex", "pi"],
                                  help="target agent/editor")

    subparsers.add_parser("stdio", help="run MCP server on stdio (used by agents)")

    # --- Worktrees ---
    wt_parser = subparsers.add_parser("wt", help="create git worktree with jj workspace")
    wt_parser.add_argument("name", nargs="?", default=None,
                           help="worktree name (omit to add workspace in current dir)")
    wt_parser.add_argument("--new", dest="new_branch", action="store_true",
                           help="create new branch instead of using existing one")

    subparsers.add_parser("wt-list", help="list worktrees with health status")

    wt_rm_parser = subparsers.add_parser("wt-rm", help="remove worktree and merge changes")
    wt_rm_parser.add_argument("name", help="worktree name to remove")
    wt_rm_parser.add_argument("--force", "-f", action="store_true",
                              help="force removal even with uncommitted changes")

    subparsers.add_parser("wt-prune", help="cleanup orphaned worktree/workspace state")

    # --- Operations ---
    subparsers.add_parser("tasks", help="list tasks across all worktrees")

    desc = subparsers.add_parser("describe", help="create named checkpoint")
    desc.add_argument("reason", help="checkpoint description")

    sy = subparsers.add_parser("sync", help="checkpoint and advance workspace bookmark")
    sy.add_argument("reason", help="sync description")
    sy.add_argument("--all", dest="sync_all", action="store_true",
                    help="merge other workspace bookmarks into current")

    # --- History ---
    hd = subparsers.add_parser("history-diffs", help="show diffs for a file across revisions")
    hd.add_argument("file", help="file path within .agent-files/")
    hd.add_argument("start_rev", help="start revision")
    hd.add_argument("end_rev", nargs="?", default="@", help="end revision (default: @)")

    hb = subparsers.add_parser("history-batch", help="show file content at each revision")
    hb.add_argument("file", help="file path within .agent-files/")
    hb.add_argument("start_rev", help="start revision")
    hb.add_argument("end_rev", nargs="?", default="@", help="end revision (default: @)")

    hs = subparsers.add_parser("history-search", help="search history for pattern in diffs")
    hs.add_argument("pattern", help="search pattern (glob, regex:, exact:, substring:)")
    hs.add_argument("--file", default=None, help="restrict search to file")
    hs.add_argument("--limit", type=int, default=20, help="max results (default: 20)")

    args = parser.parse_args()

    if args.command == "init":
        print(core.init())
    elif args.command == "migrate":
        print(core.migrate())
    elif args.command == "wt":
        print(core.wt(args.name, new_branch=args.new_branch))
    elif args.command == "wt-list":
        print(core.wt_list())
    elif args.command == "wt-rm":
        print(core.wt_rm(args.name, force=args.force))
    elif args.command == "wt-prune":
        print(core.wt_prune())
    elif args.command == "install-mcp":
        print(core.install_mcp(args.agent))
    elif args.command == "install-skills":
        print(core.install_skills(args.agent))
    elif args.command == "uninstall-mcp":
        print(core.uninstall_mcp(args.agent))
    elif args.command == "uninstall-skills":
        print(core.uninstall_skills(args.agent))
    elif args.command == "stdio":
        from taskman.server import main as server_main

        server_main()
    elif args.command == "tasks":
        print(core.tasks())
    elif args.command == "describe":
        print(core.describe(args.reason))
    elif args.command == "sync":
        print(core.sync(args.reason, sync_all=args.sync_all))
    elif args.command == "history-diffs":
        print(core.history_diffs(args.file, args.start_rev, args.end_rev))
    elif args.command == "history-batch":
        print(core.history_batch(args.file, args.start_rev, args.end_rev))
    elif args.command == "history-search":
        print(core.history_search(args.pattern, args.file, args.limit))
    else:
        parser.print_help()
        raise SystemExit(1)


if __name__ == "__main__":
    main()
