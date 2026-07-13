---
name: cost-guard
description: Estimate and cap the $ cost of Claude Code sessions by parsing the session transcript's token usage. Use this skill when the user wants to set a spending threshold or budget for Claude Code, wants to be warned as cost approaches a limit, wants Claude to stop working once a $ cap is hit, or asks how much the current session has cost so far.
---

# Cost Guard

## Overview

Estimate a Claude Code session's cost in USD from its transcript (token usage x cached model pricing), then optionally enforce a warn threshold and a hard stop threshold via Claude Code hooks. There is no live billing API available to a session -- every number this skill produces is an estimate derived from `usage` fields in the transcript JSONL, not the Console's invoiced total. Say so plainly whenever reporting a figure.

## One-off: "how much has this session cost?"

Run the estimator directly -- no setup required:

```bash
python3 <skill-dir>/scripts/estimate_cost.py
```

It auto-locates the current project's most recently modified transcript under `~/.claude/projects/<escaped-cwd>/`. Report the per-model breakdown and the total, and note it's an estimate (see Limitations below).

## Ongoing enforcement: warn + stop thresholds

This is a two-part setup: a small config file with the thresholds, and a hook wired into `settings.json` that actually enforces them. A skill's own instructions can only ask Claude to self-regulate -- real enforcement (blocking a tool call) requires a Claude Code hook, because only hooks can technically deny an action. Read `references/hooks.md` before wiring hooks if anything here is unclear on the mechanics.

1. **Ask for the two numbers** if the user hasn't given them: a warn threshold (e.g. $2) and a stop threshold (e.g. $5). Don't assume defaults for a real enforcement setup -- get explicit numbers from the user.

2. **Write the config file** at `.claude/cost-guard.json` in the project root (create the `.claude/` directory if it doesn't exist):
   ```json
   { "warn_usd": 2.0, "stop_usd": 5.0 }
   ```

3. **Wire the hook into `settings.json`.** This edits shared Claude Code configuration -- confirm with the user before writing, and prefer `.claude/settings.json` (project-scoped) over the user's global `~/.claude/settings.json` unless they ask for the cap to apply everywhere. Add both `PreToolUse` (the real enforcement point -- fires on every tool call, including inside a long autonomous loop) and `UserPromptSubmit` (a secondary check before the next turn even starts):
   ```json
   {
     "hooks": {
       "PreToolUse": [
         {
           "matcher": "*",
           "hooks": [
             { "type": "command", "command": "python3 <absolute-path-to-skill>/scripts/cost_guard_hook.py", "timeout": 5 }
           ]
         }
       ],
       "UserPromptSubmit": [
         {
           "hooks": [
             { "type": "command", "command": "python3 <absolute-path-to-skill>/scripts/cost_guard_hook.py", "timeout": 5 }
           ]
         }
       ]
     }
   }
   ```
   Use an absolute path to `cost_guard_hook.py` (it needs `cost_lib.py` and `pricing.json` alongside it, and the hook runs with an unpredictable cwd). If `hooks` already has entries for these events, merge in rather than overwrite the existing array.

4. **Tell the user hooks take effect on the next session start**, not the current one -- if the setup happens mid-session, tell them to start a new session (or otherwise reload) before relying on the cap.

5. **Verify it fires** before considering the task done: simulate the hook the way `references/hooks.md` describes, or just watch for the warning `systemMessage` once real usage crosses the warn threshold.

To change thresholds later, just edit `.claude/cost-guard.json` -- no hook re-wiring needed. To remove enforcement, delete the hook entries from `settings.json` (or the config file, which reverts the hook to its built-in $2 / $5 defaults rather than disabling it).

## Limitations (state these when reporting numbers or setting expectations)

- **Estimate, not ground truth.** Built from `scripts/pricing.json`, a cached price snapshot -- see `references/pricing.md` for how to update it and what it doesn't account for (batch discounts, negotiated rates, promotional pricing expiry).
- **Per-session, not per-org.** Each transcript is one session. This cannot see spend from other sessions, other users, or the Console's actual billing.
- **PreToolUse blocks tool calls, not token generation.** By the time the hook fires, that turn's model call has already happened and been billed -- the stop threshold prevents *further* tool use and turns, it doesn't retroactively cap a turn already in flight.
- **Fails open.** If the hook script errors, it allows the call rather than blocking (a bug in cost-guard shouldn't brick unrelated tool use). Check stderr if spend seems to be exceeding the cap unchecked.
