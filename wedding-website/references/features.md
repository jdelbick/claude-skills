# Features Reference

## Add-to-Calendar

### ICS File (`public/wedding.ics`)
```
BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Wedding//Wedding//EN
BEGIN:VEVENT
DTSTART:20250528T160000
DTEND:20250801T220000
SUMMARY:My Wedding
DESCRIPTION:Ceremony at 4:00 PM · Cocktail Hour at 4:45 PM · Reception at 6:00 PM
LOCATION:Napa
END:VEVENT
END:VCALENDAR
```

Dates are in `YYYYMMDDTHHmmss` local time format, or append `Z` for UTC.

### Google Calendar URL
```
https://calendar.google.com/calendar/render?action=TEMPLATE
  &text=NAME+%26+NAME%27s+Wedding
  &dates=20270731T230000Z%2F20270801T060000Z   ← UTC times
  &details=Ceremony+at+4%3A00+PM...
  &location=VENUE+ADDRESS
```

### Popup Component Pattern
```astro
<button class="cal-trigger" id="cal-trigger" aria-expanded="false" aria-haspopup="true">
  <svg><!-- calendar icon --></svg>
  Save the date
</button>
<div class="cal-popup" id="cal-popup" role="menu" hidden>
  <a href={googleUrl} target="_blank" role="menuitem">Google Calendar</a>
  <a href="/wedding.ics" download="wedding.ics" role="menuitem">Apple / Outlook</a>
</div>
```

## Countdown Timer

```astro
---
// CountdownTimer.astro
const { targetDate } = Astro.props;
---
<div class="countdown-timer" id="countdown-timer"
  data-target={targetDate.toISOString()}>
  <div class="countdown-unit">
    <span class="countdown-value" id="days">--</span>
    <span class="countdown-label">Days</span>
  </div>
  <!-- hours, minutes, seconds units -->
</div>
<script>
  const target = new Date(document.getElementById('countdown-timer').dataset.target);
  function update() {
    const diff = target - Date.now();
    // calculate days/hours/minutes/seconds from diff
    // update DOM
    requestAnimationFrame(update);
  }
  update();
</script>
```

## Logistics Page Structure

Recommended sections in order:
1. **Day-Of Schedule** — timeline with ceremony, cocktail hour, dinner, dancing, end time
2. **The Venue** — address, map link, brief description
3. **Getting There** — driving directions, ride share recommendation, parking situation
4. **Shuttle Service** — if provided, hotel pickup times
5. **Parking** — how many spots, any restrictions
6. **Dress Code** — label + description for guests + gentlemen separately
7. **Accommodations** — room block (if booked), Airbnb suggestions, nearby hotels

### Dress Code Copy Examples
```
Formal
Think elevated elegance — floor-length or midi gowns or cocktail dresses are all
welcome. Given that July in Saratoga can be warm, lighter fabrics are encouraged.
Wear whatever makes you feel your best — no restrictions on colors or patterns.

For gentlemen: dark suits or dress shirts with slacks all fit the occasion.
The ceremony is outdoors on lawn, so we recommend dress shoes over stilettos,
and a light layer for the evening.
```

## Things To Do — Swimming Lanes Layout

Use a 3-column CSS grid (one column per geographic area). Each "lane" has:
- Distance tag pill
- Area title + italic subtitle
- Curated spot list (3–5 spots max per lane)
- Transit note at bottom

Recommended areas: Local (venue neighborhood), Nearest City, Day Trip destination.

Keep it curated and personal — 3–5 spots per lane beats an exhaustive list. Include personal favorites with specific details ("order the espresso martini").

```css
.lanes-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  border: 1px solid var(--border-color);
}
.lane { border-right: 1px solid var(--border-color); padding: 2.75rem 2.25rem; }
.lane:last-child { border-right: none; }

@media (max-width: 900px) {
  .lanes-grid { grid-template-columns: 1fr; }
  .lane { border-right: none; border-bottom: 1px solid var(--border-color); }
}
```

## FAQ Page

Use an accordion pattern — question visible, answer expands on click.

Recommended questions to include:
- Is there parking at the venue?
- How do I get there? (ride share, shuttle)
- What's the dress code?
- Can I bring a plus one?
- Are kids welcome?
- Do you have dietary accommodation?
- Is there a hotel room block?
- What time should I arrive?
- Can I take photos during the ceremony?

```astro
<div class="faq-item" id={`faq-${i}`}>
  <button class="faq-question" aria-expanded="false" aria-controls={`answer-${i}`}>
    {question}
    <svg class="faq-chevron"><!-- chevron icon --></svg>
  </button>
  <div class="faq-answer" id={`answer-${i}`} hidden>
    <p>{answer}</p>
  </div>
</div>
```

## RSVP Page UX Flow

1. **Search** — Guest types their name, results appear as they type (debounced 300ms)
2. **Select** — Guest clicks their name from results
3. **Form** — Pre-filled with any existing RSVP; fields: attending Y/N, guest count, dietary restrictions (textarea), song request (text), message to couple (textarea)
4. **Submit** — Shows confirmation screen with their response summary

If guest is not found: "Don't see your name? Reach out to us directly."

## Our Story Page

Suggested structure:
- Hero quote or opening line
- Timeline of key moments: how they met, first date, major milestones, proposal
- Each milestone: date + location + 2–3 sentences + optional photo
- Engagement story in more detail (guests love this)
- Photo gallery

## Home Page Quick Info Cards

Three cards in a grid: The Venue, The Date, Registry.
Each card has: icon, title, 3–4 lines of detail, one link.

```html
<div class="info-grid">
  <div class="info-card">
    <svg class="info-card__icon"><!-- pin icon --></svg>
    <h3>The Venue</h3>
    <p>Villa Montalvo<br>15400 Montalvo Road<br>Saratoga, CA 95070</p>
    <a href="/logistics">Get Directions →</a>
  </div>
  <!-- Date card, Registry card -->
</div>
```

## Flappy Jake Easter Egg

A Flappy Bird clone hidden behind a "Games" link in the footer. Uses:
- HTML5 Canvas for the game
- Site color palette (cream sky, sage pipes, warm bird)
- Cloudflare D1 for persistent leaderboard across all guests
- HTML overlays (not canvas drawing) for leaderboard and name entry UI

Game state machine: `idle` (leaderboard shown) → `playing` → `dead` → `entering name` → `submitting` → back to `idle` (leaderboard refreshed).

Score of 0 skips name entry and goes straight back to leaderboard.
