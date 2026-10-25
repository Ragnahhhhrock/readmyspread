# readmyspread design system and style guide

Live reference: https://readmyspread.com/style-guide/ (built from the same tokens as the site).
Contact: contact@readmyspread.com

readmyspread reads tarot card spreads from a photo. The look is a tarot theme on a deep night sky: gold linework, soft violet, and tarot card art (card backs, arcana faces, the four suits). The zodiac wheel stays only as a faded backdrop. Calm and legible rather than mystical.

## 1. Principles

1. **Plain over mystical.** Clear reading, no act, no fog.
2. **Legible first.** Every text pairing meets WCAG AA. Touch targets are at least 48px.
3. **Tarot is always named and always shown.** Public copy, titles and share images say "tarot" or "tarot spread", and the art uses cards, suits and card backs rather than star signs, so nobody has to guess what the site does.
4. **One source of truth.** Tokens live in `public/css/tokens.css`. Change them there and nowhere else.
5. **Bump the asset version.** CSS and JS links carry `?v=YYYYMMDD`. Change it on every page and in `scripts/build-learn.py` whenever a stylesheet or script changes, so phones fetch the new file. A second change on the same day adds a letter (`?v=20261010e`). `js/audio.js` and `js/music.js` are imported by `js/app.js` with the same version.
6. **Mobile first.** Design and check at 390px wide before anything wider. Every control is a tap target of at least 48px and reads without zooming.

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

- **Logo and wordmark:** the card mark, then "readmyspread" in Cormorant 600, always lower case, one word. The mark is a gold 7:12 tarot card with a crescent and a four-point star cut out (one evenodd path, so the background shows through), drawn once in `scripts/mark.py`. It is portrait (viewBox 36 x 64): 1.07rem x 1.9rem in the header, 1.97rem x 3.5rem in the closing call. Gold only, never outlined, never on a gold surface.
- **Buttons:** `.btn--primary` (gold fill, night text), `.btn--secondary` (outlined with `--line`), disabled uses nebula. One primary per screen.
- **Header menu:** `.site-nav` with `.menu-btn` on mobile (panel opens under the header), items inline from 52rem. Every item, the `.menu-link` links and the "Read my cards" action, uses the same outlined `.btn--secondary` look: `--line` border, 8px radius, Hanken 600, 48px tall and full width in the mobile panel, 40px inline on wide screens. The current page uses a nebula fill.
- **Fields:** `.field`, `.input` on dusk with a `--line` border, hint text in mist.
- **Upload zone:** `.upload`, dusk panel, gold border, the card back (`assets/tarot/card-back.svg`) at 10rem tall.
- **Tarot card thumbnail:** `.tcard`, 7:12 face, gold border, 8px radius. Reversed cards rotate 180 degrees and are also labelled in text.
- **Steps:** `.step` with a 3rem tarot icon (`.step__icon`): photograph, eye, card fan. No moon phases. Above each icon sits a 16:10 illustration (`.step__art`, 20px radius, full width) from `assets/tarot/steps/`: `step-photograph.svg` (cards beside a phone), `step-identify.svg` (cards marked found, one reversed), `step-read.svg` (card, reading lines, speaker). Dusk panel, gold 2px linework, no text inside the art, so it needs no translation or font loading. Alt text describes the picture.
- **Suits band:** `.suits` on the home page, four items (Wands, Cups, Swords, Pentacles), each a 2.25rem suit icon and a Cormorant italic label in mist. Two columns on mobile, four from 40rem. It replaces the old star-sign strip.
- **Reading:** `.reading` in Cormorant at reading size, verdict in italic, one section per card position with a quiet divider.
- **Status:** `.status` panel with a left rule; errors use gold, never red.
- **Focus:** 3px violet outline, 3px offset, on every interactive element.
- **Reader and audio offer:** `.reader`, see section 14.
- **Share bar:** `.sharebar`, see section 12.
- **Social proof strip:** `.stats`, see section 17.
- **Tip panel:** `.tip`, dusk panel with 20px radius, Cormorant heading (step-2), mist copy, one full-width `.btn--primary` (the only gold action on the result screen) linking to the Stripe payment link in a new tab, with a mist step--1 note. No embedded third-party widgets: they cannot follow the design system.

## 6. Motifs

Tarot first, astrology as backdrop. All art is original gold linework, never a published deck. Files live in `public/assets/tarot/` and are drawn by `scripts/build-tarot-proposal.py` (output in `docs/tarot-identity/assets/`; copy the ones in use).

- **Card back** (`assets/tarot/card-back.svg`, 7:12): double gold frame, diamond lattice, a gold eye inside a four-point star in a dotted ring, corner stars. Used in the explainer video, the upload zone and the loading ring.
- **Arcana faces** (`card-star.svg`, `card-moon.svg`, `card-sun.svg`): The Star XVII, The Moon XVIII, The Sun XIX. Each has a Roman numeral, a name in outlined Cormorant 600 caps, a double frame and corner stars. Numerals and names are decorative; the position labels carry the meaning.
- **Suit icons** (`assets/tarot/icons/`): wands, cups, swords, pentacles on a 48px grid with a 1.5px gold stroke and round caps. Step icons use the same style: `photograph`, `third-eye`, `card-fan`.
- **Zodiac wheel** (`assets/zodiac-wheel.svg`): twelve sign glyphs outlined from DejaVu Sans. Kept as the share-image backdrop and, faded to 40%, behind the explainer video's intro and outro, so the cards lead. It no longer appears in the loading screen or upload zone.
- **The mark:** a gold tarot card with a crescent and four-point star cut out (section 5). Moon phases are no longer used for the steps.
- Star-field tiles (`assets/stars-a.svg`, `stars-b.svg`) with a slow twinkle.
- Tarot card outlines (7:12, gold edge) for anything that stands in for a card.
- **Hero:** text on the left (stacked first on mobile), the explainer video (section 16) on the right with a soft violet halo. The old three-card deal (`.deal`) was replaced by the video on 10 Oct 2026 and its CSS removed; the card trio still appears in the share images and the video's outro.
- **Not adopted** (kept in `docs/tarot-identity/` for later): the card fan hero, the reader's table scene, the spread diagram with position badges.

## 7. Voice and copy

Plain, warm, even-handed. No persona (the reader avatar in section 14 is a picture, not a character: no name, no backstory, no first-person voice), no jokes at the reader's expense. Australian spelling (recognises, colour). Sentence case headings. No exclamation marks.

- **Tagline:** "Your tarot spread, read plainly."
- **Eyebrow / category label:** "Tarot spread readings" (also the home hero eyebrow)
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
| `assets/linkedin-card.png` | 1200 x 627 (1.91:1) | LinkedIn post image (attach to a post; not referenced by the site) |

Layout (same on both): night sky with soft indigo and violet glows and the star field. The zodiac wheel is faded to 40% and bleeds off the right edge, with three arcana cards laid over it (The Star, The Moon, The Sun, 125px wide, turned -6, 0 and 6 degrees, face up, each labelled Past, Present or Future on a night pill in Hanken 600, mist, 19px, caps). The left column holds the card mark (72px tall) beside the eyebrow "Tarot spread readings" (Hanken 600, mist, tracked caps), then the wordmark (Cormorant 600, starlight), the tagline (Cormorant italic, gold), one sentence of support (Hanken, mist), and the URL (Hanken 600, gold) bottom left. All text stays inside a 76px left margin and clear of the cards (they start at x = 755), so it survives cropping. Keep alt text in the page head in step with the image copy.

## 9. Icons

The card mark in `scripts/mark.py` is the source. `build-assets.py` writes `favicon.svg` from it (the card on a night tile, 14px corners), then renders `favicon-32.png`, `favicon.ico`, `assets/apple-touch-icon.png`, `assets/icon-192.png` and `assets/icon-512.png`.

## 10. Checklist for a new page

1. Link `tokens.css` then `components.css`; use tokens, never raw hex.
2. Title and meta description mention tarot spread readings.
3. Canonical URL, `og:` and `twitter:` tags with the shared images and matching alt text.
4. `lang="en-AU"`, one `h1`, visible focus, 48px targets.
5. Footer with the disclaimer, privacy link and contact link.
6. A share bar (section 12) before the footer, with `js/share.js` loaded.

## 11. Learn tarot section (`public/css/learn.css`)

Generated, not hand-written: `python3 scripts/build-learn.py` builds `/learn-tarot/`, category pages, articles and `/about-tarot/` from `content/learn-tarot/`. It links `tokens.css`, `components.css`, `landing.css` (sky, `.wide`, `.nav`, `.eyebrow`, footer) then `learn.css`.

- **URLs:** `/learn-tarot/` hub, `/learn-tarot/<title-as-stub>/` articles, `/learn-tarot/category/<category-stub>/` categories, `/about-tarot/` fixed page.
- **Components:** `.chip` (category link, 48px, gold fill when current), `.post` (article card on dusk, 20px radius), `.prose` (article body, Cormorant reading size, 36rem measure), `.figure` with `figcaption` (Hanken, mist, step--1), `.note` (status-style aside), `.cta` (one `.btn--primary` per article).
- **Article images:** built by `scripts/learn_images.py` at 1600 x 900: night sky, gold linework, 7:12 gold-edged card outlines with the four-point star, lining numerals, Cormorant headings, Hanken labels. Every image has alt text and a caption in `content/learn-tarot/articles/<slug>.json`.
- **Article share images:** `assets/learn/og-<slug>.png` (1200 x 630) and `twitter-<slug>.png` (1200 x 600). Same layout as section 8 with the eyebrow "Learn tarot" and the article title in place of the wordmark. Category and hub pages use the site-wide share images.
- **Every article has:** title and meta description naming tarot, canonical URL, `og:` and `twitter:` tags with alt text, Article and BreadcrumbList JSON-LD, one `h1`, category chips, the standard footer.
- **Publishing:** `content/learn-tarot/schedule.json` holds one article per day at a randomised time. Articles not yet due are not written to `public/`. Links to articles that are not live are rendered as plain text.

## 12. Share bar (`.sharebar`, `public/js/share.js`, `scripts/sharebar.py`)

On every page, including the reading result screen. Threads, Facebook and Instagram only. No Telegram, and no other networks, unless this section changes first.

- **Layout:** heading in Cormorant (step-2, "Share this page" or "Share readmyspread"), then three `.btn--secondary` buttons: stacked and full width on mobile, three across from 40rem. Each is 48px tall minimum. Never gold, because the page's one primary action keeps that.
- **Labels:** "Share on Threads", "Share on Facebook", "Share on Instagram".
- **Threads:** a plain link that opens Threads' share page with the page address. It works without JavaScript.
- **Facebook and Instagram on phones and tablets:** their web links only open the app and drop the page address, so on a device that supports the device share sheet, a tap opens that sheet with the page title, one line of copy and the page address. The person picks Facebook or Instagram there and the link goes with it. Cancelling the sheet does nothing.
- **Facebook and Instagram without a share sheet (computers):** plain new-tab links, as before. Facebook opens `facebook.com/sharer/sharer.php` with the page address. Instagram has no web share link, so it opens `instagram.com/direct/inbox/` and `share.js` copies the page address on tap and says so in the status line under the buttons, ready to paste. The same copy-and-open path is the fallback if the sheet fails to open.
- **What is shared:** the page address and one line of copy that says tarot. Never a photo, question or reading, so a shared reading link opens `/read/`, not the reading.
- **Analytics:** GA4 `share` event with `method` (`threads`, `facebook`, `instagram`).
- **Markup:** generated by `scripts/sharebar.py` so every page matches. `build-learn.py` adds it to all Learn tarot pages; hand-written pages carry the same markup. Each bar needs a unique heading `id`.

## 13. Facebook page

Images are built by `python3 scripts/build-facebook.py` into `public/assets/facebook/` (do not edit by hand). Page copy, post drafts and the setup checklist are in `docs/facebook-page-setup.md`.

| File | Size | Notes |
| --- | --- | --- |
| `profile-720.png` | 720 x 720 | Mark only, inside the central 60% so the circular crop never clips it. |
| `cover-1640x924.png` | 1640 x 924 (16:9) | Phones show the full image; computers crop to the middle 2.63:1. Copy stays in the middle 624px band and clear of the bottom-left profile overlap. Eyebrow, wordmark, tagline and URL only: anything smaller is unreadable at 640px wide. |
| `post-launch-1080x1350.png` | 1080 x 1350 (4:5) | Same layout rules as section 8, wheel bleeding off the right edge, copy clear of it. |
| `post-how-it-works-1080x1350.png` | 1080 x 1350 (4:5) | `.row` panels on dusk, 20px radius, moon phases for the three steps. |

Same tokens, fonts and voice as the site: eyebrow "Tarot spread readings", lower-case wordmark, no exclamation marks. The profile picture and posts use the card mark; the posts still show the wheel at full strength and have not moved to the card trio layout in section 8.

## 14. Reader avatar and audio version (`public/assets/reader.svg`, `.reader` in `components.css`, `public/js/audio.js`)

**The avatar.** A calm head-and-shoulders figure in the site's gold linework: dusk sky with a nebula glow and a dotted ring, hair in night, shoulders in nebula, every outline in gold at 2px, the card mark as a brooch. Closed eyes, a quiet mouth, no hood, crystal ball or props. No skin tone is used, so the figure is not tied to any one person. It is a picture, not a persona: no name, no backstory, no first-person lines. The reading text keeps the plain voice in section 7. `reader.svg` is hand-authored from tokens (hex values match `tokens.css`); alt text is empty where it sits beside text that says the same thing.

**Where it appears**
- **Loading screen:** 5rem avatar inside a 10.5rem ring of three card backs (2rem wide), which turns slowly. Decorative, so `aria-hidden`.
- **Reading screen:** `.reader` panel above the reading: 4.5rem avatar, "Prefer to listen?", one line of support, then the audio button.

**Audio version.** Offered on every finished reading except the care screen. The voice is a female ElevenLabs voice (Lily, warm and calm, British English; ElevenLabs has no stock Australian female voice). The browser sends each part of the reading to `/api/speak` (`functions/api/speak.js`), which holds the ElevenLabs key and returns the audio. Nothing is recorded or stored by readmyspread, and the privacy page says the reading text goes to ElevenLabs. If the voice service can't be reached or isn't set up, the device's own voice (`speechSynthesis`) reads it instead. The panel is shown wherever either can play. A silent utterance is spoken inside the tap to unlock the device voice on phones, and once the voice service has failed the page goes straight to the device voice for the rest of the visit.
- **Button:** one `.btn--secondary`, full width, 48px, speaker icon. Label "Listen to this reading", then "Stop listening" while playing. Never gold, because the page's one primary action keeps that.
- **Voice:** ElevenLabs Lily, model `eleven_flash_v2_5`, stability 0.6, speed 0.95, set in `speak.js` and overridable with `ELEVENLABS_VOICE_ID` and `ELEVENLABS_MODEL`. Fallback device voice: Australian English first, then other English, preferring on-device voices, rate 0.95. Spoken text is the spread name and verdict, each card and position with its text, then the closing line. Each part is fetched as its own clip, and the next one loads while the current one plays. The audio element is unlocked inside the tap so iPhone allows it.
- **Note under the button:** "Voiced by ElevenLabs. Only the reading text is sent, and readmyspread doesn't save audio." With the device voice: "Read aloud by your device. readmyspread doesn't record or save audio." While playing: "Reading aloud."
- **While playing:** the avatar ring pulses (`.reader--speaking`), the card being read gets a gold left rule (`.is-speaking`), and the status line is `aria-live="polite"`.
- **Stops:** on Stop, on "Read another spread", on leaving the page.
- **Failure:** only when neither voice can play: "Audio isn't working on this device. You can still read it here."
- **Limits:** one request is at most 1,200 characters. With the `RATE` KV binding, 40 requests per visitor and 1,500 in total per day (`DAILY_AUDIO_PER_VISITOR`, `DAILY_AUDIO_GLOBAL`).
- **Analytics:** GA4 `audio_started` with `spread`. Never the reading text.

## 15. Instagram profile

Images are built by `python3 scripts/build-instagram.py` into `public/assets/instagram/` (do not edit by hand). Page copy, post captions and the setup checklist are in `docs/instagram-setup.md`. The homepage footer links to https://www.instagram.com/readmyspread with a `.btn--secondary` beside the Facebook link.

| File | Size | Notes |
| --- | --- | --- |
| `profile-1080.png` | 1080 x 1080 | Mark only, inside the central 55% so the circular crop never clips it. |
| `highlight-*.png` (read, how-it-works, learn-tarot, privacy) | 1080 x 1920 (9:16) | No text: Instagram prints the highlight name. One gold motif inside the central 600px so the circular crop keeps it: tarot card outline, three moon phases, three-card fan, crescent and star inside a dotted ring. |
| `post-launch-1080x1350.png`, `post-how-it-works-1080x1350.png`, `post-photo-tips-1080x1350.png` | 1080 x 1350 (4:5) | Same layout rules as sections 8 and 13. Copy keeps a 90px margin so the 3:4 profile-grid crop never cuts it. |

Same tokens, fonts and voice as the site: eyebrow "Tarot spread readings", lower-case wordmark, no exclamation marks. The profile picture, posts and highlight use the card mark; posts still show the wheel at full strength and have not moved to the card trio layout in section 8.

## 16. Explainer video (`public/assets/video/`, `.explainer` in `landing.css`, `public/js/video.js`)

Built by `python3 scripts/build-video.py` (Playwright, ffmpeg, NumPy and SciPy). Do not edit the outputs by hand. The scene is `scripts/explainer/scene.html`, which links `public/css/tokens.css` and uses the site's fonts and tarot art, so the video changes with the design system. The score is `scripts/explainer/music.py`: original, synthesised from scratch, no samples or licensed audio.

| File | Size | Notes |
| --- | --- | --- |
| `explainer-1080x1350.mp4` | 1080 x 1350 (4:5), 30 fps, 56s | H.264 high + AAC 160k, faststart. 4:5 so it fills a phone screen width without being taller than the viewport. |
| `explainer-poster.jpg` | 1080 x 1350 | Frame at 4.6s: mark, eyebrow, wordmark, tagline. |

**Running order (56s, never over 60s):** intro (card mark draws on in gold, eyebrow "Tarot spread readings", the wordmark letter by letter, tagline); title "Get your tarot spread read in three steps" with the three step tiles; a step bar (Photograph, Identify, Read) stays at the top for the steps; step one: cards dealt, a phone frames the spread, shutter, "Is that your tarot spread?" with the set question pills ("Ask a question"), one tapped and selected, then "Read my cards" tapped; step two: the loading avatar and card-back ring, a gold scan line, cards flip to The Star, The Moon and The Sun (reversed), each ticked and named, then Past, Present, Future and "A three-card spread"; step three: the cards shrink to a header, the verdict and a section per position write in (lines, not words), then the reader panel, "Listen to this reading" tapped, the avatar ring pulses and the gold rule moves card to card; outro: the hero card trio on the faded wheel, wordmark, tagline, the one gold "Read my cards", the URL, "Free. No account. Your photo isn't saved." and "For entertainment only."

**Rules:** one gold-filled action per frame (the "Read my cards" button); a selected question pill is gold as it is in the app. The phone screens mirror the real app: questions are set pills, never a free-text field. Captions are the site's voice (sentence case, Australian spelling, no exclamation marks) and carry the meaning, so it works with the sound off; there is no voiceover. Smallest text is 13px on a 540px-wide stage (about 9px on a 390px phone), used only for labels the captions repeat. Motion uses the site curve `cubic-bezier(0.2, 0.7, 0.2, 1)`. A night scrim sits behind intro and outro text so wheel lines never cross words. Music sits at about -17 LUFS, fades in over 1.2s and out over 2.6s, with chimes on the mark, shutter, card flips and taps.

**On the homepage:** in the hero, in place of the old card deal: below the hero text on mobile (full width, max 26rem), the right-hand column from 52rem (`.hero__video`, with a soft violet halo behind the frame). A short visible caption ("Watch how it works. 56 seconds, with music.", step--1, mist, centred) and a fuller visually hidden description linked by `aria-describedby`. The video is never autoplayed (it has music). `preload="none"` so it costs nothing until tapped. With JavaScript, the whole poster is one tap target with a 5rem round play button below the wordmark (night fill, gold 2px edge, gold triangle, never a gold fill, so the hero's "Read my cards" keeps that); the first tap plays with sound and switches to native controls. Without JavaScript, native controls show. `playsinline` keeps it in the page on iPhone.

**Analytics:** GA4 `video_start` and `video_complete` with `video_title` = `explainer`.

## 17. Social proof strip (`.stats` in `landing.css`, `public/js/stats.js`, `functions/api/stats.js`)

Running totals on the homepage, directly under the hero: **Tarot readings given**, **Questions answered**, **Cards identified**.

- **Layout:** full-width band like the suits band (night at 60%, quiet border above and below). Three across at every width, so it stays one short band on a 390px phone. Number first in Cormorant 600, gold, lining tabular numerals (step-2 on mobile, step-3 from 40rem); label below in Hanken, mist (step--1, step-0 from 40rem). One mist step--1 note: "Running totals, updated as readings happen." Marked up as a `dl` with a visually hidden `h2`. Not interactive, so no tap targets.
- **Numbers:** en-AU grouping (12,483); compact from a million (1.2M).
- **What counts:** a reading counts when it is shown (status ok, not the care screen, not no-cards or unreadable). Questions answered counts those with a set question. Cards identified adds the cards named in each. Only the three totals are kept, in the `STATS` KV namespace (falls back to `RATE`), never the photo, question, reading or anything about the visitor.
- **Updates:** `/api/read` adds to the totals after each reading. The page fetches `/api/stats` on load, then every 60 seconds while visible and again when the tab comes back; changed numbers count up over 900ms (instant under `prefers-reduced-motion`). **On page load** the stats wait until the band is 40% on screen, then each rises 0.75rem and fades in (480ms reveal, site curve) while its number counts up from zero over 1400ms, ease-out, staggered 150ms left to right; no motion under `prefers-reduced-motion`. KV is eventually consistent, so a new reading can take about a minute to appear.
- **Hidden** without JavaScript, when the binding is missing, or until there is at least one reading, so it never shows a zero.

## 18. Progress bar and calming music (`.progress` and `.btn--music` in `components.css`, `public/js/music.js`)

**Progress bar.** On the loading screen, under the reading line, so a reading that takes a while never looks stuck.
- **Look:** a 0.75rem track in nebula with a 1px `--line` border (so the edge meets 3:1 on night), 8px radius, max 20rem wide and centred. The fill is gold: the loading screen has no primary action, so gold is free here. A mist step--1 caption under it reads "Step 1 of 4" to "Step 4 of 4", matching the four loading lines.
- **Behaviour:** the reading has no real progress signal, so the fill eases toward 94% (about two thirds of the way after 15 seconds), never runs backwards, and jumps to 100% when the reading arrives. The result shows 450ms later so the finish is seen. The fill moves with `transform: scaleX()` over 400ms on the site curve.
- **Accessibility:** `role="progressbar"` with `aria-valuenow` and an `aria-valuetext` of "Step 2 of 4: Identifying each card." The existing polite live line announces each stage; the bar itself is not live, so it doesn't chatter.
- **Reduced motion:** the fill still updates but without the transition.

**Calming music.** Plays while a reading is made and while it is on screen, and stops on "Read another spread", on an error, on the care screen and when the page is left.
- **Source:** original and synthesised in the browser with the Web Audio API (`music.js`). A slow, breathing pad of five sine and triangle voices through a gently moving low-pass filter and a soft echo, drifting through four chords in D major (Dmaj9, Bm7/D, Gmaj9, A add4) every 22 seconds. No samples, no licensed audio, no network request, nothing stored.
- **Level:** master 0.2, fades in over 2.5s and out over 1.2s. While the audio version reads the reading aloud, the music drops to 35% so the voice stays clear.
- **Start:** inside the "Read my cards" tap, because phones only allow sound after a tap. It is on by default for the visit; the choice is kept in memory only, never stored.
- **Toggle:** one `.btn--secondary.btn--music` with a music note icon, 48px tall and full width (max 20rem on the loading screen). Label "Pause calming music" or "Play calming music". Never gold. It appears on the loading screen and above the reading, with the note "Calm ambient music, made on your device while you read." It is hidden where the device has no Web Audio.
- **Background:** the music pauses when the tab is hidden and resumes when it returns.

## 19. Learn tarot article videos (`public/assets/video/learn/`, `.explainer` and `.article__video`, `scripts/build-article-video.py`)

Every published Learn tarot article gets a short video, made automatically from the article itself and never by hand. Run `python3 scripts/build-article-video.py --live --missing` (the GitHub workflow `learn-videos.yml` does it hourly). Outputs are rebuilt, not edited.

| File | Size | Notes |
| --- | --- | --- |
| `assets/video/learn/<slug>.mp4` | 720 x 900 (4:5), 24 fps | The article page. H.264 + AAC, faststart, about 1.5 MB. |
| `assets/video/learn/<slug>.jpg` | 720 x 900 | Poster, taken once the hook is fully on screen (3.2s in). |
| `assets/video/learn/<slug>.vtt` | captions | `<track kind="captions">`, off by default because the video also carries on-screen text. |
| `assets/video/social/<slug>.mp4` | 1080 x 1920 (9:16), 24 fps | Instagram Reels, TikTok, YouTube Shorts, queued through Buffer (`scripts/post-social.py`). |
| `content/learn-tarot/videos/<slug>.json` | script and timings | Set `"locked": true` to stop it being regenerated and hand-edit the script. |

**One render, two shapes.** The scene (`scripts/explainer/article-scene.html`) is drawn 9:16, and everything that matters sits in the central 4:5 band (540 x 675 of 540 x 960). The article video is that band cropped out, and the vertical version keeps the same band clear of the app overlays social apps draw at the top and bottom. Do not put copy outside the band.

**Running order (never over 60 seconds, usually 40 to 50):** hook (card mark draws on, eyebrow "Learn tarot" and the category, the article title, the article's own lede); up to four key points (an "n of N" tag, then a 16:10 visual, the section heading and one or two sentences from that section); call to action (the three arcana cards, "Have a tarot spread in front of you?", the one gold "Read my cards", the URL, "Free. No account. Your photo isn't saved.", "For entertainment only."). The key-point visual is the article's own figure for the first point, then arcana faces flipping, card backs, or the suit icon for suit articles. Wheel faded to 32% behind the hook and call to action and 9% behind the points. No gold fills except the call to action's button.

**Script.** Built by `scripts/video_story.py` from the article text only: sentences are taken from the article, never invented. Sections such as "Where to go next" are skipped, card sections read "The Lovers stands for choice, values and union", and a line that points to another article is dropped. Spoken forms: "readmyspread.com" is read "read my spread dot com", "Step 1" as "Step one", bracketed asides are removed. Captions and the VTT show the site name as written.

**Voice.** Free offline text-to-speech (Piper, en_GB Jenny medium, length scale 1.08), run by the builder with no account or API key. The model is fetched once into `.scratch/piper`. This differs from the on-site audio reader (section 14), because a browser voice cannot be recorded into a video file. Each scene is voiced as its own clip, and the scene lasts as long as its clip plus a short lead and tail, so picture and voice never drift. The voice is described as AI in every post caption, and TikTok posts are flagged as AI-generated.

**Sound.** Voice at about -16 LUFS over a quiet original bed (`scripts/explainer/bed.py`: the homepage score's D major pad and bells, synthesised, ducked under the voice). No samples or licensed audio.

**On the article page.** A `.explainer.article__video` figure between the article header and the text, using the homepage component (section 16): 4:5 frame, poster as one tap target with the 5rem round play button, native controls after the first tap, `preload="none"`, `playsinline`. Caption "Watch the summary. N seconds, with voiceover.", with the full transcript visually hidden and linked by `aria-describedby`. `VideoObject` JSON-LD is added to the article. GA4 `video_start` and `video_complete` carry `video_title` = the article slug (`data-video-title`). An article only shows a video once its file exists, so nothing breaks while a backlog is being built.

**Only published articles.** A video is built only after its article's publish time, so scheduled articles never reach `public/`.

**Social posting.** `scripts/post-social.py` queues each new vertical video on every connected channel with Buffer's next-slot queue: Instagram as a Reel, TikTok, YouTube as a Short (title `<article title> | Learn tarot #Shorts`, category Education, public). Captions follow the voice rules in section 7: the article title and description, the article link, "Narrated with an AI voice. For entertainment only.", and `#tarot #tarotspread #tarotreading #learntarot`. At most two articles a day, oldest first, tracked in `content/learn-tarot/videos/posted.json`. Setup is in `docs/social-automation.md`.

## 20. YouTube channel

Channel: Read my Spread - Tarot readings (https://www.youtube.com/@readmyspread; the handle is `@readmyspread` as created). Images are built by `python3 scripts/build-youtube.py` into `public/assets/youtube/` (do not edit by hand). Copy and the setup checklist are in `docs/youtube-setup.md`. The homepage footer links to the channel beside Facebook and Instagram.

| File | Size | Notes |
| --- | --- | --- |
| `profile-800.png` | 800 x 800 | Mark only, inside the central 60% so the circular crop never clips it. |
| `banner-2560x1440.png` | 2560 x 1440 | All copy inside the central 1546 x 423 band that phones and computers show: eyebrow, wordmark, tagline, URL. |

Same tokens, fonts and voice as the site: eyebrow "Tarot spread readings", lower-case wordmark, no exclamation marks.
