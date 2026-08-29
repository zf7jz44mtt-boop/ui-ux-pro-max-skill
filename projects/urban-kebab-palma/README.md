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
  layers/                 8 product layers, bottom of the stack to top
  layout.json             each layer's width and vertical offset in the stack
  urban-kebab.tpl.html    the page itself, with {{IMG:*}} and <!--LAYERS--> slots
  prep.mjs                trims, resizes and encodes the layers; composites the hero
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

To restyle the stack, edit `w` (width, % of stack) and `t` (top offset, % of stack
height) in `layout.json` and re-run — the CSS and the hero composite both follow.

## Replacing the product photography

Drop new files into `src/layers/` under the same names and re-run `npm run all`.
They should be:

- PNG with a real alpha channel (no baked-in background, plate or shadow)
- shot straight-on from the side, same camera distance and lighting for all eight,
  so the layers stack into one coherent product
- horizontally centred, comfortably larger than 900px wide

## Content sources

Menu, prices, addresses and hours were compiled from the restaurant's public
listings and are marked on the page as indicative. Confirm them against the
restaurant before this goes live.
