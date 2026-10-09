# readmyspread Facebook page: setup and copy

Voice follows DESIGN.md section 7: plain, warm, Australian spelling, sentence case, no exclamation marks, "tarot spread" named in every public line. Images are built by `python3 scripts/build-facebook.py` into `public/assets/facebook/`.

## Images

| File | Size | Where it goes |
| --- | --- | --- |
| `profile-720.png` | 720 x 720 | Profile picture. Facebook shows it as a circle; the mark sits inside the safe centre. |
| `cover-1640x924.png` | 1640 x 924 | Cover photo. Phones show the full 16:9; computers crop to the middle 2.63:1. All copy sits in the middle band, clear of the profile picture. |
| `post-launch-1080x1350.png` | 1080 x 1350 (4:5) | Launch post. Fills a phone screen. |
| `post-how-it-works-1080x1350.png` | 1080 x 1350 (4:5) | Second post. |
| `../og-image.png` | 1200 x 630 | Already used for link previews; no upload needed. |

## Page details

| Field | Value |
| --- | --- |
| Page name | readmyspread |
| Username | @readmyspread |
| Category | Website |
| Intro (101 characters max) | Photograph your tarot spread and get a clear, balanced reading. Free, no account. |
| Description (255 characters max) | readmyspread reads tarot card spreads from a photo. It names the spread, identifies every card and gives a plain, balanced reading for each position. Free, no account. For entertainment only. Not medical, legal or financial advice. |
| Website | https://readmyspread.com |
| Email | contact@readmyspread.com |
| Button | Learn more, linked to https://readmyspread.com/read/ |
| Location, phone, hours | Leave blank |

## Posts

Post these in order, a day or two apart. Pin the first one.

### 1. Launch (attach `post-launch-1080x1350.png`; pin this post)

readmyspread is a free way to get your tarot spread read plainly. Photograph your tarot card spread and you get the spread named, every card identified, and a short reading for each position.

No account. Your photo isn't saved.

Try it: https://readmyspread.com/read/

For entertainment only. Not medical, legal or financial advice.

### 2. How it works (attach `post-how-it-works-1080x1350.png`)

Three steps, no sign-up.

1. Photograph. Lay your tarot cards flat, get the whole spread in frame and take a photo.
2. Identify. readmyspread recognises the tarot spread and every card, including which are reversed, and shows you what it found so you can check it.
3. Read. You get a summary of the spread, then a reading for each card in its position. Add a question if you want the reading to keep it in view.

Read my cards: https://readmyspread.com/read/

### 3. Learn tarot (link post, no image needed)

New to tarot spreads? Our Learn tarot section explains what a tarot spread is, how positions work and what common spreads are for. Start with: What is a tarot spread?

https://readmyspread.com/learn-tarot/what-is-a-tarot-spread/

### 4. Privacy (link post)

A question we get: does readmyspread keep your tarot spread photos? No. Your photo is shrunk in your browser and sent to Claude, an AI model from Anthropic, to read the cards. readmyspread doesn't store photos, questions or readings.

The full detail is on our privacy page: https://readmyspread.com/privacy/

### 5. Tips for a good photo

Getting a clear reading from your tarot spread photo comes down to three things: good light, cards laid flat and the whole spread in frame. If a card is hard to make out, readmyspread marks it rather than guessing, and you can retake the photo at any time.

https://readmyspread.com/read/

## Setup checklist

1. Create the page from your personal Facebook account (Pages, Create new page). Facebook requires a person to create it.
2. Upload `profile-720.png` and `cover-1640x924.png`, then check the cover on both phone and computer.
3. Fill in the details above and add the Learn more button.
4. Publish post 1 and pin it.
5. Share posts 2 to 5 over the following week.
6. Add the page URL to the site footer once it exists (DESIGN.md section 10 footer), and link it from `contact@readmyspread.com` signatures if wanted.
