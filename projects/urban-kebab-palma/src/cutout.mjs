import sharp from "sharp";
import { dechecker } from "./dechecker.mjs";

/* Crop to the alpha bounding box. sharp's trim() compares RGB, and a keyed pixel
   keeps whatever colour sat under it, so trim() reads the leftover checkerboard as
   content and crops to nonsense. The alpha channel is the only reliable bound. */
export async function alphaCrop(buf, { threshold = 8 } = {}) {
  const { data, info } = await sharp(buf).ensureAlpha().raw().toBuffer({ resolveWithObject: true });
  const { width: W, height: H } = info;
  let x0 = W, y0 = H, x1 = -1, y1 = -1;
  for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
    if (data[(y * W + x) * 4 + 3] > threshold) {
      if (x < x0) x0 = x;
      if (x > x1) x1 = x;
      if (y < y0) y0 = y;
      if (y > y1) y1 = y;
    }
  }
  if (x1 < 0) throw new Error("layer is fully transparent");
  // clear the colour under transparent pixels so the fringe cannot bleed on resize
  for (let i = 0; i < data.length; i += 4) if (data[i + 3] === 0) { data[i] = data[i + 1] = data[i + 2] = 0; }
  return sharp(data, { raw: { width: W, height: H, channels: 4 } })
    .extract({ left: x0, top: y0, width: x1 - x0 + 1, height: y1 - y0 + 1 })
    .png().toBuffer();
}

/* Returns each layer as a PNG cropped to its content, keying out a baked-in
   transparency checkerboard first when the source has no real alpha. */
export async function loadLayer(file) {
  const meta = await sharp(file).metadata();
  let buf = await sharp(file).png().toBuffer();
  let keyed = false;
  if (!meta.hasAlpha) {
    const r = await dechecker(file);
    if (!r) throw new Error(`${file} has no alpha channel and no checkerboard to key out`);
    buf = r.buf;
    keyed = true;
  }
  const cropped = await alphaCrop(buf);
  const cm = await sharp(cropped).metadata();
  return { buf: cropped, width: cm.width, height: cm.height, keyed };
}
