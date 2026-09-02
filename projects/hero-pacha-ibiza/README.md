# PACHA IBIZA — Drop 01 landing page

A waitlist landing page for a limited drop, built around a single product
photograph. Cream studio palette sampled from the shot, oxblood as the one
accent, and a countdown to the drop moment.

> Concept / art-direction exercise. Unofficial — not affiliated with Pacha.

```
hero-pacha-ibiza/
├── index.html                    # the whole page: CSS + ~120 lines of JS
└── assets/
    ├── polo-pacha.webp           # the product, cut out of its studio background
    └── detail-{collar,crest,print,weave}.webp
```

Open `index.html` directly in a browser — there is no build step.

## Structure

| Section | Job |
|---|---|
| Hero | Product, wordmark, the promise, countdown, primary CTA |
| The drop | 400 pieces / 1 per person / 24h early access |
| Details | Four close-ups of the garment |
| Waitlist | Email + size capture, on an oxblood block so it cannot be missed |
| FAQ | Five questions, native `<details>` — no JS needed |
| Footer | Navigation, the unofficial-concept note |

A sticky bar appears once the hero scrolls away and hides again inside the
waitlist section, so the CTA is always one tap away without nagging.

## ⚠ Placeholder content

Every figure on this page is invented for the comp. Replace before it goes
anywhere real:

- **Drop date** — `const DROP` at the foot of `index.html`. ISO 8601 with an
  explicit offset. If the date has passed, the counter stops at zero and the
  label flips to "The drop is live" rather than counting up.
- **400 pieces, 1 per person, 24h early access** — the `#drop` section.
- **Sizes, shipping, returns, price policy** — the `#faq` section.

There is deliberately **no fake signup counter**. Manufactured social proof
("1,247 already joined") is the one placeholder that misleads rather than just
being wrong, so the scarcity claim leans on the run size instead.

## ⚠ The form does not send anything

`#wl-form` is front-end only. It validates the address, shows a success panel
and stores nothing. **Wire it to a real endpoint before telling anyone they are
on a list.** The handler is at the bottom of `index.html`, marked in a comment.

## The product asset

`assets/polo-pacha.webp` is the supplied photograph with its beige studio
background and drop shadow removed (900×989, transparent, 146 KB).

The cutout was done programmatically, because the polo's lightest cream squares
sit within ~15 RGB of the studio beige. A plain flood-fill loose enough to catch
the background leaks through the shadow under the left collar wing and eats the
garment — 82 lost px at tolerance 14, 3 525 at 16. So the matte:

1. **Floods at tolerance 14**, measured as the ceiling before the collar goes.
2. **Removes the shadow chromatically** — it is beige scaled down, caught by
   `|rgb − k·bg| < 12` with `k` in 0.22–1.04, not by brightness.
3. **Derives alpha from two criteria at once** — geometric interiority *and*
   colour difference. Either alone leaves a halo or punches holes in the cream.
4. **Decontaminates the rim**, un-mixing the beige so the edge does not glow.

The four detail images are square crops of the same photograph.

### Swapping the product

Drop your file into `assets/` and change one `src`:

```html
<img class="product__img" src="assets/polo-pacha.webp" alt="" …>
```

Portrait, transparent background, roughly **0.85–1.0 aspect**. Sizing, the
float, the parallax and the shadow all key off `.product__img` (marked
`SWAP POINT`). Keep `alt=""` — it is decorative, and the page has a real `<h1>`.
Update the `width`/`height` attributes to the file's true pixel size.

**If the garment carries its own chest print** — this one does — check nothing
lands on top of it.

## Design notes

- **Palette sampled from the photograph**: studio beige `#e2d3c2`, logo oxblood
  `#6f2b24` as the single accent, the polo's pink in the hairlines.
- **Type** — Baloo 2 800 for display, chosen because its rounded bowls echo the
  polo's own logotype; Inter for everything else.
- **The wordmark sits over the garment** on `mix-blend-mode: multiply`, so the
  checkerboard and the crest read *through* the letterforms.
- **Entrance is choreographed** so the garment leads: polo at 0.34s, wordmark
  at 1.25s, kicker at 1.65s.
- **Reveals are opt-in** — `.rv` only hides once JS adds `.js` to `<html>`. With
  JS off the page renders complete instead of blank.
- **Reduced motion** kills every animation, the parallax listeners and smooth
  scrolling.

## Verified

Chromium, 13 widths from 320px to 1600px:

- No horizontal overflow at any width.
- **Every visible text node passes WCAG AA** — checked by walking the DOM and
  compositing translucent backgrounds, not by spot-checking tokens.
- Every focusable element shows a focus ring. (The form fields needed an
  explicit `:focus-visible` rule — `.field input:focus{outline:none}`
  out-specifies the global one and was silently killing their ring.)
- No tap target under 32px on a coarse pointer.
- `prefers-reduced-motion`: 13/13 blocks visible, zero running animations.
- The page renders fully with JavaScript disabled, minus the live counter.
