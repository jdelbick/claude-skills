---
name: wedding-website
description: This skill should be used when helping someone build, improve, or deploy a wedding website. Covers full-stack setup with Astro + Cloudflare Pages, design system, all essential pages (RSVP, logistics, FAQ, things-to-do, our story), password protection, Cloudflare D1 database, and optional fun features like easter eggs and game leaderboards. Handles clients with no coding experience through expert developers.
---

# Wedding Website Skill

A complete guide for building and deploying a beautiful, functional wedding website. The reference stack is **Astro** (static site framework) + **Cloudflare Pages** (free hosting) + **Cloudflare D1** (SQLite database). Detailed patterns live in the `references/` files — load them as needed.

## Critical Working Rules

1. **Never commit or push without asking the client first.** Wedding websites are deeply personal. Always show what changed and explicitly ask "Want me to push this?" before running any git command that affects the remote.
2. **Ask before making design decisions.** Colors, copy, photos — confirm before choosing.
3. **Assume non-technical clients.** Explain every terminal command. Never skip setup steps.

## Gathering Requirements

Before writing any code, ask the couple:

1. Both full names
2. Wedding date + ceremony start time
3. Venue name + full address
4. Day-of schedule (ceremony, cocktail hour, reception start, end time)
5. Dress code
6. Transportation plan (shuttle from hotel? parking? Uber recommended?)
7. Hotel / accommodation situation (room block booked? coming soon? Airbnb only?)
8. Registry link (Zola, The Knot, etc.)
9. Photos — at minimum a hero/home photo + engagement photos
10. Site password(s) — main password for all guests, optionally a fun alternate
11. Custom domain (if any)
12. **Inspiration** — any wedding websites they love, Pinterest boards, or aesthetic references (colors, vibes, photos). This is one of the most important inputs for the design. If they have a Pinterest board, ask them to share the link or describe the overall feel: romantic/rustic/modern/minimalist/garden party/etc.

## Tech Stack

- **Astro** — `.astro` files with HTML + frontmatter + scoped `<style>` + `<script>`. SSR mode for API routes.
- **Cloudflare Pages** — free hosting, edge deployment, CI/CD from GitHub
- **Cloudflare D1** — SQLite DB bound as `DB` in `locals.runtime.env.DB`
- **TypeScript** — API routes in `src/pages/api/` exported as `GET`/`POST` functions
- **Vanilla JS** — no React/Vue needed; all interactivity in `<script>` blocks

See `references/architecture.md` for full project structure, key files, and code patterns.

## Cloudflare Setup (Step-by-Step for Non-Developers)

Walk through each step. Many clients have never used a terminal.

### Prerequisites
```bash
# 1. Install Node.js — go to https://nodejs.org, download the LTS version, run the installer
node --version   # confirm: should print v18 or higher

# 2. Install Wrangler (Cloudflare's command-line tool)
npm install -g wrangler

# 3. Log in to Cloudflare (creates free account if needed at cloudflare.com first)
wrangler login   # opens a browser tab — click "Allow"
```

### Create the Astro Project
```bash
npm create astro@latest wedding-website
# When prompted: Empty project → Yes TypeScript → Strict → Yes install deps
cd wedding-website
npm install @astrojs/cloudflare
```

### Configure Astro for Cloudflare
`astro.config.mjs`:
```js
import { defineConfig } from 'astro/config';
import cloudflare from '@astrojs/cloudflare';

export default defineConfig({
  output: 'server',
  adapter: cloudflare(),
});
```

`wrangler.toml`:
```toml
name = "their-wedding-name"
compatibility_date = "2024-12-01"
pages_build_output_dir = "dist"
```

### Create the D1 Database
```bash
wrangler d1 create wedding-rsvp
# Copy the database_id it prints — paste it below
```

Add to `wrangler.toml`:
```toml
[[d1_databases]]
binding = "DB"
database_name = "wedding-rsvp"
database_id = "PASTE-YOUR-ID-HERE"
```

### Local Development
```bash
# Create .dev.vars for local secrets — NEVER commit this file
# Add to .gitignore: .dev.vars
echo "SITE_PASSWORD=yourpassword" > .dev.vars

npm run dev   # site runs at http://localhost:4321
```

### Deploy to Cloudflare Pages
```bash
npm run build
wrangler pages deploy dist
# First deploy creates the project; future deploys update it
```

Set production passwords in Cloudflare Dashboard → Pages → your project → Settings → Environment Variables → Add `SITE_PASSWORD`.

### Connect GitHub for Automatic Deploys (recommended)
Cloudflare Dashboard → Pages → your project → Settings → Git integration → Connect GitHub → select repo → Build command: `npm run build` → Output dir: `dist`.

### Custom Domain
Cloudflare Dashboard → Pages → your project → Custom Domains → add domain. If domain is registered elsewhere, point nameservers to Cloudflare first.

## Essential Pages

See `references/features.md` for content guidance, copy examples, and component patterns for each page.

| Page | Path | Purpose |
|------|------|---------|
| Home | `/` | Names, date, venue, countdown timer, add-to-calendar button, photo gallery preview, quick info cards |
| Our Story | `/our-story` | How they met, proposal story, photos with captions |
| Logistics | `/logistics` | Full day schedule, venue info, transportation, parking, dress code, accommodations |
| RSVP | `/rsvp` | Guest lookup by name, attendance confirmation, meal prefs, song request |
| FAQ | `/faq` | Parking, plus-ones, kids, dietary, dress code — accordion style |
| Things To Do | `/things-to-do` | Local area, nearby city, day trips — 3-column "swimming lanes" layout |

## Password Protection

Gate the entire site so only invited guests can access it. Use Astro middleware:

`src/middleware.ts`:
```ts
import type { MiddlewareHandler } from "astro";

const PUBLIC_PATHS = ["/login", "/api/login"];

export const onRequest: MiddlewareHandler = async (context, next) => {
  const { pathname } = context.url;
  if (PUBLIC_PATHS.some(p => pathname.startsWith(p))) return next();
  if (pathname.match(/\.(js|css|png|jpg|webp|svg|ico|woff2?)$/)) return next();

  const authCookie = context.cookies.get("wedding_auth");
  const password = context.locals.runtime?.env?.SITE_PASSWORD;
  if (!authCookie || authCookie.value !== password) {
    return context.redirect("/login");
  }
  return next();
};
```

An alternate password (e.g. for an easter egg mode) can be checked alongside the main one.

## RSVP System

Guests look themselves up by first+last name (fuzzy match), then confirm attendance and fill in preferences. Guest list is pre-loaded into D1.

See `references/database.md` for the full D1 schema (guests, rsvp_responses, flappy_scores tables) and the lookup + submit API patterns.

## Design System

See `references/design.md` for the full color palette, typography scale, CSS custom properties, spacing system, and component patterns.

**Key principles:**
- Warm, muted palette: cream (`#faf9f5`), sage green (`#7a9467`), stone (`#8a7f72`)
- Never use bright or saturated colors — think old California, garden wedding
- Serif display font (e.g. Cormorant Garamond) + sans-serif body (e.g. Inter)
- Generous whitespace — let content breathe
- Mobile-first — many guests open on phones the day of the wedding

## Easter Eggs

Optional hidden features that make the site memorable:

- **Alternate password mode** — a second password triggers a different experience (e.g. falling cannabis leaves, color shift). Check both passwords in middleware and set a separate JS-readable cookie to indicate the mode.
- **Hidden game** — add a "Games" link in the footer that opens a Flappy Bird clone with a D1 leaderboard. Guests compete and scores persist across all visitors.
- **Konami code** — ↑↑↓↓←→←→BA triggers confetti or plays a song

Keep easter eggs tasteful and couple-appropriate. They should feel like a fun discovery, not a distraction.

## Add-to-Calendar

Support both Google Calendar and Apple/Outlook. Use a popup button (not two separate visible buttons):

- Google Calendar: deep link with URL params (`action=TEMPLATE`, `dates=`, `location=`, etc.)
- Apple/Outlook: serve a `.ics` file from `public/wedding.ics`

See `references/features.md` for the ICS file format and Google Calendar URL construction.

## Common Mistakes to Avoid

- Don't put passwords in `wrangler.toml` — use `.dev.vars` locally and the Cloudflare dashboard for production
- Don't commit `.dev.vars` — add it to `.gitignore`
- Don't use bright colors or busy patterns — keep it elegant and warm
- Don't put everything on one long scrolling page — use separate routes per section
- Don't forget mobile — test at 375px width before every deploy
- Don't push changes without the client's explicit approval
