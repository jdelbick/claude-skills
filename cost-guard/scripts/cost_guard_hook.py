#!/usr/bin/env python3
"""Claude Code hook entry point for cost-guard.

Wire this into PreToolUse (matcher "*") and, optionally, UserPromptSubmit in
settings.json. On each firing it estimates the current session's spend from
the transcript and either lets the turn continue, attaches a warning, or
blocks (PreToolUse: denies the tool call; UserPromptSubmit: blocks the prompt).

Reads the standard Claude Code hook JSON from stdin: session_id,
transcript_path, cwd, hook_event_name, (tool_name for PreToolUse).
Never fails closed on an internal error -- a bug here should not brick an
unrelated tool call, so any exception falls back to allowing the turn.
"""

import json
import os
import sys

from cost_lib import estimate_session_cost

DEFAULT_WARN_USD = 2.0
DEFAULT_STOP_USD = 5.0


def load_config(cwd):
    config = {"warn_usd": DEFAULT_WARN_USD, "stop_usd": DEFAULT_STOP_USD}
    cfg_path = os.path.join(cwd, ".claude", "cost-guard.json")
    if os.path.exists(cfg_path):
        try:
            with open(cfg_path) as f:
                user_cfg = json.load(f)
            for key in ("warn_usd", "stop_usd"):
                if key in user_cfg:
                    config[key] = float(user_cfg[key])
        except (OSError, ValueError, json.JSONDecodeError):
            pass
    for env_key, cfg_key in (("COST_GUARD_WARN_USD", "warn_usd"), ("COST_GUARD_STOP_USD", "stop_usd")):
        if os.environ.get(env_key):
            try:
                config[cfg_key] = float(os.environ[env_key])
            except ValueError:
                pass
    return config


def build_output(hook_event, total, config):
    if total >= config["stop_usd"]:
        reason = (
            f"Cost guard: estimated session spend ${total:.2f} has reached the "
            f"${config['stop_usd']:.2f} stop threshold. Stop working, tell the user "
            f"the cap was hit, and wait for them to raise the limit or say how to proceed."
        )
        if hook_event == "PreToolUse":
            return {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
                }
            }
        return {"decision": "block", "reason": reason}

    if total >= config["warn_usd"]:
        msg = (
            f"Cost guard warning: estimated session spend is ${total:.2f} "
            f"(warn ${config['warn_usd']:.2f}, stop ${config['stop_usd']:.2f})."
        )
        output = {"systemMessage": msg, "additionalContext": msg}
        if hook_event == "PreToolUse":
            output["hookSpecificOutput"] = {"hookEventName": "PreToolUse", "permissionDecision": "allow"}
        return output

    return {}


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        print(json.dumps({}))
        return

    hook_event = data.get("hook_event_name")
    cwd = data.get("cwd") or os.getcwd()
    transcript_path = data.get("transcript_path")

    if not transcript_path or not os.path.exists(transcript_path):
        print(json.dumps({}))
        return

    try:
        config = load_config(cwd)
        result = estimate_session_cost(transcript_path)
        output = build_output(hook_event, result["total_usd"], config)
    except Exception as exc:  # fail open -- never brick an unrelated tool call
        print(f"cost-guard hook error (allowing): {exc}", file=sys.stderr)
        output = {}

    print(json.dumps(output))


if __name__ == "__main__":
    main()
