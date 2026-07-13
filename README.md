# Claude Skills

A collection of [Claude Code skills](https://code.claude.com/docs/en/skills) — packaged instructions, scripts, and references that extend Claude with specialized workflows.

## Skills

| Skill | Description |
|---|---|
| [`cost-guard`](cost-guard/) | Estimate and cap the $ cost of Claude Code sessions by parsing the session transcript's token usage. Warns as spend approaches a threshold and can hard-stop tool use via a hook once a cap is hit. |
| [`wedding-website`](wedding-website/) | Build, improve, or deploy a wedding website: full-stack setup with Astro + Cloudflare Pages, design system, RSVP/logistics/FAQ pages, password protection, a Cloudflare D1 database, and optional fun features like easter eggs and game leaderboards. |

## Installing a skill

Claude Code loads skills from `~/.claude/skills/<name>/` (personal, available in every project) or `<project>/.claude/skills/<name>/` (scoped to one project). This repo is just the source — cloning it doesn't make the skills available on its own; each one needs to be linked or copied into one of those locations.

**Symlink (recommended)** — keeps the installed skill in sync with any edits you make in this repo:

```bash
ln -s "$(pwd)/cost-guard" ~/.claude/skills/cost-guard
```

Symlink every skill in this repo at once:

```bash
for d in */; do
  name="${d%/}"
  [ -f "$name/SKILL.md" ] && ln -sf "$(pwd)/$name" ~/.claude/skills/"$name"
done
```

**Copy** — if you'd rather have an independent snapshot that won't change when this repo does:

```bash
cp -r cost-guard ~/.claude/skills/cost-guard
```

For a project-scoped install (only available inside one project, e.g. to share with a team via that project's own repo), target `<project>/.claude/skills/<name>/` instead of `~/.claude/skills/<name>/`.

After installing, start a new Claude Code session (or `/skills` reload, if your version supports it) for newly added skills to be picked up.

## Adding a new skill

Use the `skill-creator` skill (`init_skill.py`) to scaffold a new skill directory here with the right `SKILL.md` structure, then add a row to the table above.
