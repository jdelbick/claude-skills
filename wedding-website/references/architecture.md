# Architecture Reference

## Project Structure

```
wedding-website/
├── public/
│   ├── images/           # engagement photos, venue illustration
│   ├── favicon.svg
│   └── wedding.ics       # Add-to-calendar file for Apple/Outlook
├── scripts/              # gitignored — real guest data CSVs
├── src/
│   ├── components/
│   │   ├── Navigation.astro
│   │   ├── Footer.astro          # includes hidden Flappy Jake game
│   │   ├── AddToCalendar.astro   # popup: Google + Apple/Outlook
│   │   ├── CountdownTimer.astro
│   │   └── HeroImage.astro
│   ├── layouts/
│   │   └── Layout.astro          # global shell: nav, footer, scroll button,
│   │                             # vibe toggle, pot mode canvas, scroll reveal
│   ├── pages/
│   │   ├── index.astro
│   │   ├── our-story.astro
│   │   ├── logistics.astro
│   │   ├── rsvp.astro
│   │   ├── faq.astro
│   │   ├── things-to-do.astro
│   │   ├── login.astro
│   │   └── api/
│   │       ├── login.ts
│   │       ├── rsvp/
│   │       │   ├── lookup.ts     # GET — fuzzy name search in guests table
│   │       │   └── submit.ts     # POST — write rsvp_responses row
│   │       └── scores/
│   │           ├── leaderboard.ts  # GET — top 10 flappy scores
│   │           └── submit.ts       # POST — insert score, return updated top 10
│   ├── styles/
│   │   └── global.css
│   └── middleware.ts             # auth guard — checks wedding_auth cookie
├── .dev.vars                     # local secrets — NEVER commit
├── .gitignore                    # includes .dev.vars, scripts/
├── astro.config.mjs
├── wrangler.toml
└── tsconfig.json
```

## Key Patterns

### Accessing D1 in API Routes
```ts
export const GET: APIRoute = async ({ locals }) => {
  const db = locals.runtime?.env?.DB;
  if (!db) {
    // Dev fallback — DB not available locally without wrangler dev
    return new Response(JSON.stringify({ data: [] }), {
      headers: { "Content-Type": "application/json" },
    });
  }
  const result = await db.prepare("SELECT * FROM table").all();
  return new Response(JSON.stringify({ data: result.results }), {
    headers: { "Content-Type": "application/json" },
  });
};
```

### Cookies in Middleware
```ts
// Set cookie on login
cookies.set("wedding_auth", password, {
  httpOnly: true,
  secure: true,
  sameSite: "lax",
  path: "/",
  maxAge: 60 * 60 * 24 * 30, // 30 days
});

// Read cookie in middleware
const authCookie = context.cookies.get("wedding_auth");
```

### Pot Mode (easter egg) Pattern
Two cookies:
- `wedding_auth` — httpOnly, holds the raw password (server-readable only)
- `wedding_pot_mode` — NOT httpOnly (JS-readable), set to `"1"` when alternate password used

In Layout.astro, JS reads `wedding_pot_mode` cookie to activate client-side effects.

### Scroll Reveal Animations
In `global.css`:
```css
.will-reveal {
  opacity: 0;
  transform: translateY(22px);
  transition: opacity 0.55s ease, transform 0.55s ease;
}
.will-reveal.revealed {
  opacity: 1;
  transform: none;
}
```

In Layout.astro, an IntersectionObserver adds `will-reveal` class to named selectors (`.tip-card`, `.faq-item`, `.timeline-item`, etc.) and adds `revealed` when they enter the viewport. Elements inside `.hero` and `.page-hero` are skipped (they use CSS `animate-fade-in` instead).

### Scroll/Top Button
Single button at bottom-right, dual-state:
- Below `window.innerHeight * 0.6` → shows "↑ TOP"
- Above threshold → shows "↓ SCROLL" and uses `window.scrollBy({ top: window.innerHeight * 0.88 })`

### wrangler.toml (production)
```toml
name = "jamie-jake-wedding"
compatibility_date = "2024-12-01"
pages_build_output_dir = "dist"

[[d1_databases]]
binding = "DB"
database_name = "wedding-rsvp"
database_id = "YOUR-DATABASE-ID"

[vars]
# Do NOT put passwords here — set them in Cloudflare dashboard
```

### .gitignore essentials
```
.dev.vars
scripts/
node_modules/
dist/
.astro/
```
