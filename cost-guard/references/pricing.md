# Pricing table maintenance

`scripts/pricing.json` is a cached snapshot (dated in its `_snapshot_date` field), not a live feed. Claude Code has no API for current spend or live pricing, so this skill estimates cost purely from transcript token counts times this hardcoded table.

## Updating it

1. Check current pricing at https://platform.claude.com/docs/en/pricing (or ask the `claude-api` skill for a refreshed table).
2. Edit `scripts/pricing.json`: `models.<model-id>.input` / `.output` are USD per **million** tokens. The model ID must match the `model` field written into the transcript JSONL exactly (e.g. `claude-sonnet-5`, `claude-opus-4-8`) -- check a live transcript under `~/.claude/projects/<project>/<session>.jsonl` if unsure.
3. Cache write/read prices are not per-model entries -- they're the multipliers in `cache_multipliers` (write_5m, write_1h, read), applied against that model's input price. This has held true across all current models; if a future model breaks that pattern, add a per-model override rather than changing the global multipliers.
4. If `estimate_cost.py` or the hook logs "no pricing entry" for a model, that model's usage is silently excluded from the total -- the estimate is a **lower bound**, not wrong-but-close. Add the missing entry.

## Known limitations of the estimate

- Introductory/promotional pricing (e.g. Sonnet 5's discounted rate through 2026-08-31) is a snapshot value with an expiry noted in the `_comment` field -- it will silently become stale after that date until someone updates it.
- No visibility into batch API discounts (50% off), fast-mode premiums, or organization-level negotiated rates -- this table assumes standard synchronous Messages API pricing.
- The estimate is per-transcript (per session), not per-organization or per-billing-period. It cannot see spend from other sessions, other users, or the Console's actual invoiced total.
