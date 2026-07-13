#!/usr/bin/env python3
"""Shared helpers for estimating Claude Code session cost from a transcript JSONL file."""

import glob
import json
import os
import re
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PRICING_PATH = os.path.join(SCRIPT_DIR, "pricing.json")


def load_pricing(pricing_path=PRICING_PATH):
    with open(pricing_path) as f:
        return json.load(f)


def _resolve_model_pricing(model, pricing):
    models = pricing["models"]
    if model in models:
        return models[model]
    # Strip a trailing dated-snapshot suffix, e.g. claude-haiku-4-5-20251001
    stripped = re.sub(r"-\d{8}$", "", model)
    if stripped in models:
        return models[stripped]
    return None


def transcript_path_for_cwd(cwd, session_id=None):
    """Find the transcript JSONL for a given project cwd, mirroring Claude Code's
    ~/.claude/projects/<escaped-cwd>/<session_id>.jsonl layout."""
    escaped = re.sub(r"[/\\]", "-", os.path.abspath(cwd))
    if not escaped.startswith("-"):
        escaped = "-" + escaped
    project_dir = os.path.join(os.path.expanduser("~/.claude/projects"), escaped)
    if session_id:
        candidate = os.path.join(project_dir, f"{session_id}.jsonl")
        return candidate if os.path.exists(candidate) else None
    files = glob.glob(os.path.join(project_dir, "*.jsonl"))
    if not files:
        return None
    return max(files, key=os.path.getmtime)


def parse_transcript_usage(transcript_path):
    """Sum usage fields per model across every assistant message in the transcript.

    Returns: {model: {"input_tokens": int, "output_tokens": int,
                       "cache_read_input_tokens": int,
                       "cache_creation_5m": int, "cache_creation_1h": int}}
    """
    totals = {}
    with open(transcript_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            message = entry.get("message")
            if not isinstance(message, dict) or message.get("role") != "assistant":
                continue
            usage = message.get("usage")
            model = message.get("model")
            if not usage or not model:
                continue
            bucket = totals.setdefault(
                model,
                {
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "cache_read_input_tokens": 0,
                    "cache_creation_5m": 0,
                    "cache_creation_1h": 0,
                },
            )
            bucket["input_tokens"] += usage.get("input_tokens", 0) or 0
            bucket["output_tokens"] += usage.get("output_tokens", 0) or 0
            bucket["cache_read_input_tokens"] += usage.get("cache_read_input_tokens", 0) or 0
            creation = usage.get("cache_creation") or {}
            if creation:
                bucket["cache_creation_5m"] += creation.get("ephemeral_5m_input_tokens", 0) or 0
                bucket["cache_creation_1h"] += creation.get("ephemeral_1h_input_tokens", 0) or 0
            else:
                # Older transcripts without the ephemeral breakdown: assume 5m (the default TTL).
                bucket["cache_creation_5m"] += usage.get("cache_creation_input_tokens", 0) or 0
    return totals


def compute_cost(usage_by_model, pricing):
    """Returns (total_usd, per_model breakdown, list of model names with no pricing entry)."""
    mult = pricing["cache_multipliers"]
    total = 0.0
    breakdown = {}
    unpriced = []
    for model, u in usage_by_model.items():
        rates = _resolve_model_pricing(model, pricing)
        if rates is None:
            unpriced.append(model)
            continue
        in_price = rates["input"] / 1_000_000
        out_price = rates["output"] / 1_000_000
        cost = (
            u["input_tokens"] * in_price
            + u["output_tokens"] * out_price
            + u["cache_read_input_tokens"] * in_price * mult["read"]
            + u["cache_creation_5m"] * in_price * mult["write_5m"]
            + u["cache_creation_1h"] * in_price * mult["write_1h"]
        )
        breakdown[model] = cost
        total += cost
    return total, breakdown, unpriced


def estimate_session_cost(transcript_path, pricing_path=PRICING_PATH):
    pricing = load_pricing(pricing_path)
    usage_by_model = parse_transcript_usage(transcript_path)
    total, breakdown, unpriced = compute_cost(usage_by_model, pricing)
    return {
        "total_usd": total,
        "by_model_usd": breakdown,
        "unpriced_models": unpriced,
    }


if __name__ == "__main__":
    print("This is a library module -- run estimate_cost.py or cost_guard_hook.py instead.", file=sys.stderr)
    sys.exit(1)
