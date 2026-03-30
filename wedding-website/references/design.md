# Design Reference

## Color Palette

```css
:root {
  /* Backgrounds */
  --bg-primary:    #faf9f5;   /* warm cream — main page background */
  --bg-secondary:  #f5f0e8;   /* slightly warmer — alternating sections */
  --bg-accent:     #ede8dc;   /* visible warmth — highlight sections */

  /* Text */
  --text-primary:   #2f2f2a;  /* near-black warm */
  --text-secondary: #6b6459;  /* warm medium gray */
  --text-accent:    #3d3a30;  /* deep warm brown — headings */

  /* Brand */
  --color-sage:       #7a9467;   /* sage green — primary accent */
  --color-sage-light: #b7c4ad;   /* soft sage — borders, dividers */
  --color-olive:      #5a7048;   /* deeper green — hover states */
  --color-stone:      #8a7f72;   /* warm stone — secondary text */

  /* Borders */
  --border-color: #e5dfd4;    /* warm light border */
}
```

**Never use** pure black (`#000`), pure white (`#fff`), or any saturated/bright colors. Everything should feel warm, aged, and elegant — like a letterpress invitation.

## Typography

```css
:root {
  --font-display: 'Cormorant Garamond', Georgia, serif;  /* headings, titles */
  --font-body:    'Cormorant Garamond', Georgia, serif;  /* body text */
  --font-sans:    'Inter', system-ui, sans-serif;        /* labels, UI, caps */
}
```

Load from Google Fonts:
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;1,300;1,400&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
```

### Type Scale
- Hero title: `clamp(3.5rem, 10vw, 6rem)` weight 300
- Section titles: `clamp(2rem, 4vw, 2.75rem)` weight 300
- Card titles: `1.1875rem` weight 400
- Body: `0.9375rem` line-height 1.75–1.85
- Labels/caps: `0.625–0.75rem` weight 500–600, `text-transform: uppercase`, `letter-spacing: 0.12–0.2em`

## Spacing System

```css
:root {
  --space-xs:  0.5rem;
  --space-sm:  1rem;
  --space-md:  1.5rem;
  --space-lg:  2.5rem;
  --space-xl:  4rem;
  --space-2xl: 6rem;
}

.section         { padding: var(--space-2xl) 0; }
.section--compact { padding: var(--space-xl) 0; }
```

## Key Component Patterns

### Page Hero (interior pages)
```html
<section class="page-hero">
  <div class="container text-center">
    <h1 class="page-hero__title animate-fade-in">Page Title</h1>
    <p class="page-hero__subtitle animate-fade-in delay-1">Subtitle</p>
  </div>
</section>
```

```css
.page-hero {
  background: var(--bg-secondary);
  padding: var(--space-2xl) 0 var(--space-xl);
  border-bottom: 1px solid var(--border-color);
}
.page-hero__title {
  font-size: clamp(2.5rem, 6vw, 4rem);
  font-weight: 300;
  letter-spacing: 0.06em;
  margin-bottom: 1rem;
}
.page-hero__subtitle {
  font-family: var(--font-display);
  font-style: italic;
  font-size: clamp(1.125rem, 2.5vw, 1.5rem);
  color: var(--text-secondary);
}
```

### Section Divider
```html
<div class="divider"><span class="divider-icon">·</span></div>
```

```css
.divider {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  margin: 1.5rem 0;
}
.divider::before, .divider::after {
  content: "";
  flex: 1;
  max-width: 60px;
  height: 1px;
  background: var(--color-sage-light);
}
.divider-icon { color: var(--color-sage-light); }
```

### Buttons
```html
<a href="/rsvp" class="btn btn--primary">RSVP Now</a>
<a href="/logistics" class="btn btn--secondary">Learn More</a>
```

```css
.btn {
  display: inline-block;
  font-family: var(--font-sans);
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.16em;
  padding: 1rem 2.25rem;
  transition: all 0.2s ease;
  border-radius: 0;  /* sharp corners — no border-radius */
}
.btn--primary {
  background: var(--color-sage);
  color: #fff;
  border: 1.5px solid var(--color-sage);
}
.btn--primary:hover { background: var(--color-olive); border-color: var(--color-olive); }

.btn--secondary {
  background: transparent;
  color: var(--text-accent);
  border: 1.5px solid var(--text-accent);
}
.btn--secondary:hover { background: var(--text-accent); color: var(--bg-primary); }
```

### Cards (info cards, tip cards)
```css
.card {
  background: var(--bg-secondary);
  padding: 2.5rem 2rem;
  border: 1px solid var(--border-color);
  box-shadow: 0 10px 24px rgba(47, 47, 42, 0.06);
  transition: transform 0.25s ease, box-shadow 0.25s ease;
}
.card:hover {
  transform: translateY(-2px);
  box-shadow: 0 16px 36px rgba(47, 47, 42, 0.1);
}
```

### Scroll Reveal Animation Classes
```css
.animate-fade-in {
  animation: fadeInUp 0.7s ease both;
}
.delay-1 { animation-delay: 0.1s; }
.delay-2 { animation-delay: 0.2s; }
.delay-3 { animation-delay: 0.3s; }
.delay-4 { animation-delay: 0.4s; }
.delay-5 { animation-delay: 0.5s; }

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to   { opacity: 1; transform: none; }
}

/* Scroll reveal (IntersectionObserver in Layout.astro) */
.will-reveal {
  opacity: 0;
  transform: translateY(22px);
  transition: opacity 0.55s ease, transform 0.55s ease;
}
.will-reveal.revealed { opacity: 1; transform: none; }
```

## Mobile Breakpoints

```css
/* Tablet and below */
@media (max-width: 900px) {
  /* 3-column layouts collapse to 1 */
}

/* Mobile */
@media (max-width: 768px) {
  /* 2-column layouts collapse, navigation becomes hamburger */
}

/* Small mobile */
@media (max-width: 480px) {
  /* Fine-tune spacing, font sizes */
}
```

Always use `min-height: 100dvh` (not `100vh`) for full-screen elements on mobile — iOS Safari's URL bar causes `100vh` to not fill the actual visible area.

## Navigation

Desktop: horizontal links. Mobile: hamburger button → full-screen overlay sliding in from right.

Mobile nav overlay must use `height: calc(100dvh - var(--nav-height))` not `bottom: 0` — the latter doesn't always fill correctly in iOS Safari.

```css
/* Nav height CSS variable */
--nav-height: 76px;
```
