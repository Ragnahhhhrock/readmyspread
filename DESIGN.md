# readmyspread design system and style guide

Live reference: https://readmyspread.com/style-guide/ (built from the same tokens as the site).
Contact: contact@readmyspread.com

readmyspread reads tarot card spreads from a photo. The look is a generic astrological theme: a deep night sky, gold linework, soft violet. Calm and legible rather than mystical.

## 1. Principles

1. **Plain over mystical.** Clear reading, no act, no fog.
2. **Legible first.** Every text pairing meets WCAG AA. Touch targets are at least 48px.
3. **Tarot is always named.** Public copy, titles and share images say "tarot" or "tarot spread" so nobody has to guess what the site does.
4. **One source of truth.** Tokens live in `public/css/tokens.css`. Change them there and nowhere else.

## 2. Colour (tokens in `public/css/tokens.css`)

| Token | Value | Use | Contrast |
| --- | --- | --- | --- |
| night | #0b1024 | page background | base |
| dusk | #141a38 | panels, cards | |
| nebula | #232b55 | raised or selected surfaces, quiet dividers | |
| starlight | #f3efe4 | primary text | 16.2:1 on night |
| mist | #aeb4d3 | secondary text | 9.0:1 on night |
| gold | #e2c071 | primary fills (night text), card edging, accents | 10.3:1 with night text |
| gold-deep | #cfa94f | hover for gold fills | |
| violet | #b4a8ff | links, focus ring | 8.7:1 on night |
| line | #6b74a8 | UI boundaries (inputs, outlined buttons) | 3:1+ on night |

Rules: gold is for the one primary action per screen and for card edging. Violet is for links and focus only. Never put mist text on nebula. Dark theme only (`color-scheme: dark`).

## 3. Type

- **Display:** Cormorant Garamond (400, 400 italic, 600), self-hosted woff2, SIL OFL. Headings, the wordmark, readings.
- **UI:** Hanken Grotesk (variable), self-hosted woff2, SIL OFL. Buttons, labels, captions, body UI.
- Cormorant runs small, so reading text is 1.3125rem.

| Step | Size | Use |
| --- | --- | --- |
| step--1 | 0.875rem | captions, fine print |
| step-0 | 1rem | UI text (16px minimum on inputs stops iOS zoom) |
| step-1 | 1.3125rem | reading text |
| step-2 | 1.75rem | card names, section titles |
| step-3 | 2.25rem | screen titles |
| step-4 | 3rem (4.25rem from 40rem) | hero |
| step-5 | 4rem (5.5rem from 40rem) | large wordmark |

Line heights: tight 1.05 (headings), UI 1.45, reading 1.55. Reading column is 36rem wide.

## 4. Space, shape, motion

- Space: 4px base. `--s-1` 0.25rem, `--s-2` 0.5, `--s-3` 0.75, `--s-4` 1, `--s-5` 1.5, `--s-6` 2, `--s-7` 3, `--s-8` 4.5, `--s-9` 6.5.
- Radius: 8px for buttons, inputs and tarot card thumbnails; 20px for panels and the upload zone.
- Touch target: 3rem (48px) minimum.
- Motion: 160ms for hover and press, 480ms for reading reveal, `cubic-bezier(0.2, 0.7, 0.2, 1)`. All motion is switched off under `prefers-reduced-motion`.

## 5. Components (`public/css/components.css`)

- **Wordmark:** crescent plus four-point star, then "readmyspread" in Cormorant 600, always lower case, one word.
- **Buttons:** `.btn--primary` (gold fill, night text), `.btn--secondary` (outlined with `--line`), disabled uses nebula. One primary per screen.
- **Fields:** `.field`, `.input` on dusk with a `--line` border, hint text in mist.
- **Upload zone:** `.upload`, dusk panel, gold border, faint zodiac wheel.
- **Tarot card thumbnail:** `.tcard`, 7:12 face, gold border, 8px radius. Reversed cards rotate 180 degrees and are also labelled in text.
- **Reading:** `.reading` in Cormorant at reading size, verdict in italic, one section per card position with a quiet divider.
- **Status:** `.status` panel with a left rule; errors use gold, never red.
- **Focus:** 3px violet outline, 3px offset, on every interactive element.

## 6. Motifs

- Zodiac wheel (`assets/zodiac-wheel.svg`): twelve sign glyphs outlined from DejaVu Sans, so it looks the same everywhere.
- Moon phases for the three steps; crescent and four-point star as the mark.
- Star-field tiles (`assets/stars-a.svg`, `stars-b.svg`) with a slow twinkle.
- Tarot card outlines (7:12, gold edge) for anything that stands in for a card.

## 7. Voice and copy

Plain, warm, even-handed. No persona, no jokes at the reader's expense. Australian spelling (recognises, colour). Sentence case headings. No exclamation marks.

- **Tagline:** "Your tarot spread, read plainly."
- **Eyebrow / category label:** "Tarot spread readings"
- **Primary action:** "Read my cards"
- **Always say "tarot spread" (or "tarot card spread") in:** page titles, meta descriptions, share titles, the hero, the app tagline, and the first mention in any new page. On a screen already inside the reader, "your spread" is fine after the tarot context is set.
- **Disclaimer (footer, every page):** "For entertainment only. Not medical, legal or financial advice." Readings never predict health, money or legal outcomes.
- **Contact:** contact@readmyspread.com, linked as `mailto:` in the footer and on the privacy page.

## 8. Social share images

Built by `python3 scripts/build-assets.py` (Playwright and Pillow). Do not edit the PNGs by hand.

| File | Size | Used by |
| --- | --- | --- |
| `assets/og-image.png` | 1200 x 630 (1.91:1) | `og:image` |
| `assets/twitter-card.png` | 1200 x 600 (2:1) | `twitter:image`, `twitter:card` = `summary_large_image` |

Layout (same on both): night sky with soft indigo and violet glows and the star field; zodiac wheel bleeding off the right edge; left column holds the eyebrow "Tarot spread readings" (Hanken 600, mist, tracked caps), the wordmark (Cormorant 600, starlight), the tagline (Cormorant italic, gold), one sentence of support (Hanken, mist), and the URL (Hanken 600, gold) bottom left. All text stays inside a 76px left margin and clear of the wheel, so it survives cropping. Keep alt text in the page head in step with the image copy.

## 9. Icons

`favicon.svg` is the source. `build-assets.py` renders `favicon-32.png`, `favicon.ico`, `assets/apple-touch-icon.png`, `assets/icon-192.png` and `assets/icon-512.png`.

## 10. Checklist for a new page

1. Link `tokens.css` then `components.css`; use tokens, never raw hex.
2. Title and meta description mention tarot spread readings.
3. Canonical URL, `og:` and `twitter:` tags with the shared images and matching alt text.
4. `lang="en-AU"`, one `h1`, visible focus, 48px targets.
5. Footer with the disclaimer, privacy link and contact link.
