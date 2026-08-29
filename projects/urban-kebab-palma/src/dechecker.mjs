import sharp from "sharp";

/* Some sources hand back the transparency checkerboard baked into the pixels
   instead of a real alpha channel. The checkerboard is two bright neutral greys;
   every ingredient is either coloured (meat, cheese, onion, bun) or a warm
   off-white (garlic sauce, crumb) that is not neutral. So a pixel is background
   when it is neutral AND bright — and, crucially, when it is reachable from the
   border through other background pixels. That connectivity test is what keeps
   an enclosed pale highlight inside the food from being punched out. */
export async function dechecker(file, { minLevel = 224, neutral = 10 } = {}) {
  const { data, info } = await sharp(file).ensureAlpha().raw().toBuffer({ resolveWithObject: true });
  const { width: W, height: H } = info;
  const at = (x, y) => (y * W + x) * 4;

  const isBg = (x, y) => {
    const i = at(x, y), r = data[i], g = data[i + 1], b = data[i + 2];
    return r >= minLevel && Math.max(r, g, b) - Math.min(r, g, b) <= neutral;
  };

  // only treat this as a keyable backdrop if the border really is one
  let frameBg = 0, frameN = 0;
  for (let x = 0; x < W; x++) for (const y of [0, 1, H - 2, H - 1]) { frameBg += isBg(x, y) ? 1 : 0; frameN++; }
  for (let y = 0; y < H; y++) for (const x of [0, 1, W - 2, W - 1]) { frameBg += isBg(x, y) ? 1 : 0; frameN++; }
  if (frameBg / frameN < 0.9) return null;

  const bg = new Uint8Array(W * H);
  const stack = new Int32Array(W * H);
  let sp = 0;
  const push = (x, y) => { const p = y * W + x; if (!bg[p] && isBg(x, y)) { bg[p] = 1; stack[sp++] = p; } };
  for (let x = 0; x < W; x++) { push(x, 0); push(x, H - 1); }
  for (let y = 0; y < H; y++) { push(0, y); push(W - 1, y); }
  while (sp > 0) {
    const p = stack[--sp], x = p % W, y = (p / W) | 0;
    if (x > 0) push(x - 1, y);
    if (x < W - 1) push(x + 1, y);
    if (y > 0) push(x, y - 1);
    if (y < H - 1) push(x, y + 1);
  }

  // grow the background by one pixel: the ring where food blends into the backdrop
  // is neither, and left behind it reads as a pale halo once composited on dark
  const alpha = Buffer.alloc(W * H, 255);
  for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
    const p = y * W + x;
    if (bg[p] || (x > 0 && bg[p - 1]) || (x < W - 1 && bg[p + 1]) || (y > 0 && bg[p - W]) || (y < H - 1 && bg[p + W])) alpha[p] = 0;
  }

  // Write the mask straight into the RGBA we already decoded. Handing sharp a
  // separate mask via joinChannel silently misaligned it against the colour data.
  // blur() on a single-channel raw input comes back as 3 interleaved channels,
  // so read it back with its reported stride rather than assuming one byte per pixel
  const soft = await sharp(alpha, { raw: { width: W, height: H, channels: 1 } })
    .blur(0.6).raw().toBuffer({ resolveWithObject: true });
  const stride = soft.info.channels;
  if (soft.data.length !== W * H * stride) throw new Error(`unexpected mask size ${soft.data.length}`);
  let kept = 0;
  for (let p = 0; p < W * H; p++) {
    const a = soft.data[p * stride];
    data[p * 4 + 3] = a;
    if (a) kept++; else data[p * 4] = data[p * 4 + 1] = data[p * 4 + 2] = 0;
  }
  return {
    buf: await sharp(data, { raw: { width: W, height: H, channels: 4 } }).png().toBuffer(),
    keptPct: (100 * kept / (W * H)).toFixed(1)
  };
}
