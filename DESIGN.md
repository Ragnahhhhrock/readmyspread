# readmyspread design notes

Generic astrological theme: a deep night sky, gold linework, soft violet. Calm and legible rather than mystical.

## Colour (tokens in `public/css/tokens.css`)

| Token | Value | Use |
| --- | --- | --- |
| night | #0b1024 | page background |
| dusk | #141a38 | panels, cards |
| nebula | #232b55 | dividers, raised surfaces |
| starlight | #f3efe4 | primary text |
| mist | #aeb4d3 | secondary text |
| gold | #e2c071 | primary buttons (night text), card edging, accents |
| violet | #b4a8ff | links, focus ring |

All text pairings meet WCAG AA; UI boundaries use `--line` (#6b74a8) for at least 3:1 against night.

## Type

- Display: Cormorant Garamond (400, 400 italic, 600), self-hosted woff2, SIL OFL.
- UI: Hanken Grotesk (variable), self-hosted woff2, SIL OFL.
- Cormorant runs small, so reading text is 1.3125rem.

## Motifs

- Zodiac wheel (`assets/zodiac-wheel.svg`): twelve sign glyphs outlined from DejaVu Sans, so it looks the same everywhere.
- Moon phases for the three steps; crescent and four-point star as the mark.
- Star-field tiles (`assets/stars-a.svg`, `stars-b.svg`) with a slow twinkle. Motion is switched off for `prefers-reduced-motion`.

## Voice

Plain, warm, even-handed. No persona, no jokes at the reader's expense. Australian spelling. Readings are for entertainment and never predict health, money or legal outcomes.
