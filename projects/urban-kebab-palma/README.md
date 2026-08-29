# Urban Kebab Palma — landing page

Landing page for [Urban Kebab](https://www.instagram.com/urbankebabpalma/), a gourmet
kebab restaurant in Palma de Mallorca. The centrepiece is a scroll-scrubbed product
build: an Urban Kebab assembles itself layer by layer, pinned to the scrollbar, with
the ingredient story changing in step.

`index.html` is a single self-contained file — every product image is embedded as a
WebP data URI, so it can be opened straight from disk or dropped on any static host.
The only external requests are Google Fonts and GSAP from cdnjs.

## Design system

| | |
|---|---|
| Ground | `#12150E` deep olive-black (dark-first; a full light palette ships too) |
| Accent | `#E8511F` ember — the only loud colour on the page |
| Support | `#E9B949` saffron, `#8B9A64` olive, used only as small marks |
| Display | Anton, set very large with tight tracking |
| Text / labels | Barlow and Barlow Condensed |

Both themes are token-driven and cover all three viewer states (explicit dark,
explicit light, and the un-stamped system default).

## Building

The page is generated from one template plus the product photography, so the markup
and the compositing geometry can never drift apart.

```
src/
  layers/                 the product layers, bottom of the stack to top
  layout.json             the stack: geometry and scroll-step copy per layer
  urban-kebab.tpl.html    the page itself, with {{IMG:*}} and <!--LAYERS--> slots
  dechecker.mjs           keys out a transparency checkerboard baked into pixels
  cutout.mjs              crops each layer to its alpha bounding box
  prep.mjs                encodes the layers; composites the hero from them
  build.mjs               injects everything -> ../index.html
```

```bash
cd src
npm install
npm run all       # prep + build
```

`prep.mjs` trims each layer to its alpha bounding box, so the offsets in
`layout.json` address the ingredient itself rather than whatever transparent margin
the source file happened to carry. It then stacks the layers with that same geometry
to composite the hero shot, which means the hero is a true render of the finished
product rather than a separate image that can fall out of sync.

`layout.json` is the single source for the whole sequence. Each entry carries its
geometry — `w` (width, % of stack) and `t` (top offset, % of stack height) — and
the copy for its scroll step. The layer markup, the step list the animation walks
through, and the hero composite are all generated from it, so a layer is added or
reordered in one place and everything follows.

**Still to come:** lettuce and tomato. Their photography had not arrived, and two
flat vector stand-ins beside six photographic layers cheapened the whole stack,
so the build ships as six real layers rather than a mixed eight. To add them,
drop the cutouts into `src/layers/` and insert their entries into `layout.json`
between the bun base and the onion, then re-run `npm run all`. Nothing else
needs touching. The offsets below the insertion point will want nudging so the
stack closes up.

## Replacing the product photography

Drop new files into `src/layers/` under the same names and re-run `npm run all`.
They should be:

- shot straight-on from the side, same camera distance and lighting for all eight,
  so the layers stack into one coherent product
- comfortably larger than 900px wide

Real alpha is preferred, but a file that arrives with the transparency
checkerboard flattened into its pixels — what an image host's preview download
usually gives you — is handled automatically. `dechecker.mjs` keys it out by
finding the background as the near-neutral, bright pixels *reachable from the
border*; that connectivity test is what stops it punching holes through pale
food like the garlic sauce or the crumb of the bun. Anything already carrying an
alpha channel skips the step untouched.

## Content sources

Menu, prices, addresses and hours were compiled from the restaurant's public
listings and are marked on the page as indicative. Confirm them against the
restaurant before this goes live.
