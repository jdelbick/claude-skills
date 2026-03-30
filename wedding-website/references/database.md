# Database Reference

## D1 Schema

### guests table
Pre-loaded with the guest list before invitations go out.

```sql
CREATE TABLE IF NOT EXISTS guests (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  first_name TEXT NOT NULL,
  last_name TEXT NOT NULL,
  email TEXT,
  party_size INTEGER DEFAULT 1,
  notes TEXT
);
```

### rsvp_responses table
One row per guest who RSVPs.

```sql
CREATE TABLE IF NOT EXISTS rsvp_responses (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  guest_id INTEGER NOT NULL REFERENCES guests(id),
  attending INTEGER NOT NULL,  -- 1 = yes, 0 = no
  guest_count INTEGER DEFAULT 1,
  dietary TEXT,
  song TEXT,
  message TEXT,
  submitted_at TEXT DEFAULT (datetime('now')),
  UNIQUE(guest_id)
);
```

### flappy_scores table
For the Flappy Jake leaderboard easter egg.

```sql
CREATE TABLE IF NOT EXISTS flappy_scores (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  score INTEGER NOT NULL,
  created_at TEXT DEFAULT (datetime('now'))
);
```

## Loading the Guest List

Create a migration script `scripts/seed_guests.sql` (gitignored since it contains real names):
```sql
INSERT INTO guests (first_name, last_name, email, party_size) VALUES
  ('John', 'Smith', 'john@example.com', 2),
  ('Jane', 'Doe', 'jane@example.com', 1);
  -- ... etc
```

Run locally:
```bash
wrangler d1 execute wedding-rsvp --local --file=./scripts/seed_guests.sql
```

Run in production:
```bash
wrangler d1 execute wedding-rsvp --remote --file=./scripts/seed_guests.sql
```

## RSVP Lookup API Pattern

`src/pages/api/rsvp/lookup.ts` — fuzzy name search:

```ts
import type { APIRoute } from "astro";

export const GET: APIRoute = async ({ url, locals }) => {
  const query = url.searchParams.get("q")?.trim() ?? "";
  if (!query || query.length < 2) {
    return new Response(JSON.stringify({ guests: [] }), {
      headers: { "Content-Type": "application/json" },
    });
  }

  const db = locals.runtime?.env?.DB;
  if (!db) {
    return new Response(JSON.stringify({ guests: [], dev: true }), {
      headers: { "Content-Type": "application/json" },
    });
  }

  const term = `%${query.toLowerCase()}%`;
  const result = await db
    .prepare(`
      SELECT g.id, g.first_name, g.last_name, g.party_size,
             r.attending, r.guest_count, r.dietary, r.song
      FROM guests g
      LEFT JOIN rsvp_responses r ON g.id = r.guest_id
      WHERE LOWER(g.first_name || ' ' || g.last_name) LIKE ?
         OR LOWER(g.last_name) LIKE ?
      LIMIT 8
    `)
    .bind(term, term)
    .all();

  return new Response(JSON.stringify({ guests: result.results }), {
    headers: { "Content-Type": "application/json" },
  });
};
```

## RSVP Submit API Pattern

`src/pages/api/rsvp/submit.ts`:

```ts
import type { APIRoute } from "astro";

export const POST: APIRoute = async ({ request, locals }) => {
  const { guestId, attending, guestCount, dietary, song, message } =
    await request.json();

  if (!guestId) {
    return new Response(JSON.stringify({ error: "Guest ID required" }), { status: 400 });
  }

  const db = locals.runtime?.env?.DB;
  if (!db) {
    return new Response(JSON.stringify({ success: true, dev: true }), {
      headers: { "Content-Type": "application/json" },
    });
  }

  await db.prepare(`
    INSERT INTO rsvp_responses (guest_id, attending, guest_count, dietary, song, message)
    VALUES (?, ?, ?, ?, ?, ?)
    ON CONFLICT(guest_id) DO UPDATE SET
      attending = excluded.attending,
      guest_count = excluded.guest_count,
      dietary = excluded.dietary,
      song = excluded.song,
      message = excluded.message,
      submitted_at = datetime('now')
  `)
  .bind(guestId, attending ? 1 : 0, guestCount ?? 1, dietary ?? null, song ?? null, message ?? null)
  .run();

  return new Response(JSON.stringify({ success: true }), {
    headers: { "Content-Type": "application/json" },
  });
};
```

## Flappy Scores API Pattern

`src/pages/api/scores/leaderboard.ts`:
```ts
export const GET: APIRoute = async ({ locals }) => {
  const db = locals.runtime?.env?.DB;
  if (!db) return new Response(JSON.stringify({ scores: [] }), { headers: { "Content-Type": "application/json" } });

  await db.exec(`CREATE TABLE IF NOT EXISTS flappy_scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL, score INTEGER NOT NULL,
    created_at TEXT DEFAULT (datetime('now'))
  )`);

  const result = await db.prepare(
    "SELECT name, score FROM flappy_scores ORDER BY score DESC LIMIT 10"
  ).all();

  return new Response(JSON.stringify({ scores: result.results }), {
    headers: { "Content-Type": "application/json" },
  });
};
```

`src/pages/api/scores/submit.ts`:
```ts
export const POST: APIRoute = async ({ request, locals }) => {
  const { name, score } = await request.json();
  const safeName = String(name ?? "").slice(0, 20).trim() || "Anonymous";
  const safeScore = Math.max(0, Math.min(9999, Math.floor(Number(score))));

  const db = locals.runtime?.env?.DB;
  if (!db) return new Response(JSON.stringify({ success: true, scores: [] }), { headers: { "Content-Type": "application/json" } });

  await db.prepare("INSERT INTO flappy_scores (name, score) VALUES (?, ?)")
    .bind(safeName, safeScore).run();

  const result = await db.prepare(
    "SELECT name, score FROM flappy_scores ORDER BY score DESC LIMIT 10"
  ).all();

  return new Response(JSON.stringify({ success: true, scores: result.results }), {
    headers: { "Content-Type": "application/json" },
  });
};
```
