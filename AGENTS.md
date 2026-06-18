# AGENTS.md — HV_Harness

Entry point for AI coding agents (Codex and others that look for an
`AGENTS.md`). The **canonical** project instruction file is `CLAUDE.md`
in this same directory; this short stub exists only so that agents which
do not read `CLAUDE.md` automatically are pointed to it and start
correctly. It is deliberately not a duplicate — when this file and
`CLAUDE.md` disagree, `CLAUDE.md` wins.

## Do these first, in order

1. **Read `CLAUDE.md` in full**, then read `docs/quick_start.md`, the
   session entry script it points you to. Together they set the
   terminology rules, the governing principles, and how a session
   begins.

2. **Check the environment before running anything:**

   ```bash
   python scripts/check_env.py
   ```

   It is read-only and needs no config or network. Resolve anything it
   reports as `MISSING` (it prints the exact command) before going
   further. This avoids the usual start-up fumbling over Python version
   and packages.

3. **Do not run any pipeline script, open any config, or propose search
   terms until the `docs/quick_start.md` conversation has been
   completed.** The scripts are fast; the structured conversation is the
   work.

Everything else — methodology, the five checkpoints, repository layout —
lives in `CLAUDE.md` and the `docs/` it references.
