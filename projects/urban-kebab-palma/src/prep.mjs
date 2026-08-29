/* Turns the 8 layer PNGs in ./layers into embeddable WebP data URIs, and
   composites them into a single hero shot of the finished product.
   Drop the real files in ./layers (named per layout.json) and re-run. */
import sharp from "sharp";
import { readFileSync, writeFileSync, readdirSync } from "node:fs";
import { loadLayer } from "./cutout.mjs";

const layout = JSON.parse(readFileSync("layout.json", "utf8"));
const STACK_W = 1000;
const STACK_H = Math.round(STACK_W * layout.stackAspect);

function find(base) {
  const hit = readdirSync("layers").find(f => f.replace(/\.[^.]+$/, "") === base);
  if (!hit) throw new Error(`missing layers/${base}.(png|webp|jpg)`);
  return "layers/" + hit;
}

const assets = {};
const composites = [];

for (const L of layout.layers) {
  const file = find(L.file);
  // cropped to the ingredient itself, so --t/--w address the food and not the canvas
  const { buf: trimmed, width: tw, height: th, keyed } = await loadLayer(file);
  const tm = { width: tw, height: th };

  const web = await sharp(trimmed)
    .resize({ width: 900, withoutEnlargement: true })
    .webp({ quality: 82, alphaQuality: 92, effort: 6 })
    .toBuffer();
  const wm = await sharp(web).metadata();
  assets[L.id] = { uri: "data:image/webp;base64," + web.toString("base64"), kb: web.length / 1024 };

  // same geometry the CSS uses, so the hero is a true render of the finished stack
  const w = Math.round(STACK_W * L.w / 100);
  const scaled = await sharp(trimmed).resize({ width: w }).png().toBuffer();
  const sm = await sharp(scaled).metadata();
  composites.push({
    input: scaled,
    left: Math.round((STACK_W - w) / 2),
    top: Math.round(STACK_H * L.t / 100),
    _h: sm.height
  });
  console.log(String(L.id).padEnd(4), file.replace("layers/", "").padEnd(26),
    keyed ? "keyed  " : "alpha  ", `${tm.width}x${tm.height}`.padEnd(10),
    "ar " + (tm.width / tm.height).toFixed(2), "→", Math.round(web.length / 1024) + "KB");
}

// the canvas has to clear the lowest layer's full height, not just its top edge
const canvasH = Math.max(STACK_H, ...composites.map(c => c.top + c._h)) + 8;
// sharp applies trim before composite within one pipeline, so flatten the stack first
const stacked = await sharp({ create: { width: STACK_W, height: canvasH, channels: 4, background: { r: 0, g: 0, b: 0, alpha: 0 } } })
  .composite(composites.map(({ _h, ...c }) => c))
  .png()
  .toBuffer();
const hero = await sharp(stacked)
  .trim({ threshold: 2 })
  .resize({ width: 920, withoutEnlargement: true })
  .webp({ quality: 84, alphaQuality: 92, effort: 6 })
  .toBuffer();
assets.hero = { uri: "data:image/webp;base64," + hero.toString("base64"), kb: hero.length / 1024 };
assets._stackAspect = +(STACK_W / canvasH).toFixed(4);
await sharp(hero).toFile("hero-preview.webp");
console.log("hero  composited from all 8 layers →", Math.round(hero.length / 1024) + "KB");

writeFileSync("assets.json", JSON.stringify(assets));
console.log("stack aspect", assets._stackAspect);
console.log("TOTAL embedded:", Math.round(Object.values(assets).filter(a => a.kb).reduce((a, b) => a + b.kb, 0)) + "KB");
