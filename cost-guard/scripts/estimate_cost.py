#!/usr/bin/env python3
"""Print an estimated USD cost for the current (or a specified) Claude Code session.

Usage:
    estimate_cost.py                              # auto-detect: cwd -> most recent transcript
    estimate_cost.py --transcript /path/to.jsonl
    estimate_cost.py --cwd /path/to/project [--session-id <id>]
    estimate_cost.py --json                        # machine-readable output
"""

import argparse
import json
import os
import sys

from cost_lib import estimate_session_cost, transcript_path_for_cwd


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--transcript", help="Path to a transcript JSONL file")
    parser.add_argument("--cwd", default=os.getcwd(), help="Project directory (used to auto-locate the transcript)")
    parser.add_argument("--session-id", help="Specific session ID to look up under --cwd")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON instead of text")
    args = parser.parse_args()

    transcript_path = args.transcript or transcript_path_for_cwd(args.cwd, args.session_id)
    if not transcript_path or not os.path.exists(transcript_path):
        print("Could not find a transcript for this session. Pass --transcript explicitly.", file=sys.stderr)
        sys.exit(1)

    result = estimate_session_cost(transcript_path)

    if args.json:
        print(json.dumps(result))
        return

    print(f"Transcript: {transcript_path}")
    for model, cost in sorted(result["by_model_usd"].items(), key=lambda kv: -kv[1]):
        print(f"  {model}: ${cost:.4f}")
    if result["unpriced_models"]:
        print(f"  (no pricing entry, not counted: {', '.join(result['unpriced_models'])} -- update scripts/pricing.json)", file=sys.stderr)
    print(f"Estimated total: ${result['total_usd']:.4f}")


if __name__ == "__main__":
    main()
