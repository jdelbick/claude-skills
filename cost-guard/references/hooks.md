# Hook mechanics this skill relies on

Source: Claude Code hooks docs (`https://code.claude.com/docs/en/hooks.md`). Re-verify against the live docs if Claude Code's hook schema has changed since this was written.

## What every hook receives on stdin (JSON)

`session_id`, `transcript_path`, `cwd`, `permission_mode`, `hook_event_name`, plus event-specific fields (`tool_name` / `tool_input` on `PreToolUse`).

`transcript_path` points at the session's JSONL transcript, normally under `~/.claude/projects/<escaped-cwd>/<session_id>.jsonl`, where `<escaped-cwd>` is the absolute cwd with every `/` replaced by `-`.

## Blocking semantics

- **Exit code 2** is the older blocking mechanism: stderr is fed back to Claude, tool call blocked. Still works, but the JSON form below is more precise and is what this skill uses.
- **PreToolUse deny (used for the hard stop):** exit 0, stdout is:
  ```json
  {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": "..."}}
  ```
- **UserPromptSubmit / Stop block:** exit 0, stdout is:
  ```json
  {"decision": "block", "reason": "..."}
  ```
- **Warn without blocking:** exit 0, stdout carries `systemMessage` (shown to the user) and/or `additionalContext` (injected into Claude's context). No `decision`/`permissionDecision` needed -- omitting them (or setting `permissionDecision: "allow"`) lets the turn proceed normally.

## Why PreToolUse, not UserPromptSubmit, is the primary gate

`UserPromptSubmit` only fires once per user-submitted message. Within a single turn, Claude Code's agentic loop can call many tools back-to-back with no new user prompt in between -- so a long autonomous task could blow past a spend cap entirely between `UserPromptSubmit` firings. `PreToolUse` (matcher `"*"`) fires before every tool call, including inside that loop, so it's the point that actually catches runaway spend mid-turn. This skill wires the same hook script to both events: `PreToolUse` for the real-time stop, `UserPromptSubmit` as a belt-and-suspenders check before the next turn even starts.

## Caveats

- Config changes to `hooks` in `settings.json` take effect on the **next session start** -- an already-running session won't pick up a newly added hook.
- A `PreToolUse` deny stops further tool calls, but it can't retroactively stop the plain-text generation that already happened in that same turn (the model has already produced output by the time the hook fires). It's a cap on further *action*, not a hard ceiling on every last token.
- The hook fails open (allows the call) on any internal error, by design -- a bug in the cost-estimation script should not brick unrelated tool calls. This means a broken hook silently stops enforcing the cap rather than blocking everything; check stderr / hook logs if spend seems uncapped.
