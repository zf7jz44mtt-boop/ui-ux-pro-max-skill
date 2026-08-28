#!/usr/bin/env node
/* ==========================================================================
   export.mjs — renders carousel.html to PNGs ready to upload to Instagram.

     node export.mjs            # 1080 x 1350 (4:5, el formato de feed)
     node export.mjs --square   # 1080 x 1080

   Sale en dist/. Sirve la carpeta por HTTP (no file://) para que las fuentes
   .woff2 y las imágenes carguen igual que en un navegador normal.
   ========================================================================== */

import { createServer } from 'node:http';
import { readFile, mkdir, readdir, unlink } from 'node:fs/promises';
import { extname, resolve, dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const { chromium } = require('/opt/node22/lib/node_modules/playwright/index.js');

const root = dirname(fileURLToPath(import.meta.url));
const square = process.argv.includes('--square');
const feed = process.argv.includes('--feed');   // 12 piezas cuadradas del perfil
const outDir = resolve(root, 'dist');

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript',
  '.woff2': 'font/woff2',
  '.jpg': 'image/jpeg',
  '.png': 'image/png',
  '.svg': 'image/svg+xml',
};

const server = createServer(async (req, res) => {
  try {
    const path = decodeURIComponent(req.url.split('?')[0]);
    const file = resolve(root, '.' + (path === '/' ? '/carousel.html' : path));
    if (!file.startsWith(root)) { res.writeHead(403).end(); return; }
    const body = await readFile(file);
    res.writeHead(200, { 'content-type': MIME[extname(file)] || 'application/octet-stream' });
    res.end(body);
  } catch {
    res.writeHead(404).end('not found');
  }
});
await new Promise((r) => server.listen(0, '127.0.0.1', r));
const { port } = server.address();

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1240, height: 1500 }, deviceScaleFactor: 1 });
await page.goto(`http://127.0.0.1:${port}/${feed ? 'feed.html' : 'carousel.html'}`, { waitUntil: 'load' });

await page.evaluate((isSquare) => {
  document.body.classList.remove('preview');
  if (isSquare) document.querySelectorAll('.slide').forEach((s) => s.classList.add('is-square'));
}, square);

await page.evaluate(() => document.fonts.ready);
await page.evaluate(() => Promise.all(
  Array.from(document.images).filter((i) => !i.complete).map((i) => i.decode().catch(() => {}))
));
await page.waitForTimeout(400);

await mkdir(join(outDir, 'feed'), { recursive: true });
const suffix = square ? '-1080x1080' : '-1080x1350';
for (const stale of await readdir(outDir).catch(() => [])){
  if (stale.endsWith(`${suffix}.png`)) await unlink(join(outDir, stale));
}

// Guard: a slide whose content is taller than the frame silently loses its
// footer in the export, so report it instead of shipping a cropped post.
// Mockups are absolutely positioned and may bleed past the frame on purpose,
// so only in-flow content counts towards the overflow check.
const overflow = await page.evaluate((sel) => Array.from(document.querySelectorAll(sel)).map((s, i) => {
  const box = s.getBoundingClientRect();
  const padBottom = parseFloat(getComputedStyle(s).paddingBottom);
  const inFlow = Array.from(s.children).filter((c) => getComputedStyle(c).position === 'static'
    || getComputedStyle(c).position === 'relative');
  const last = inFlow[inFlow.length - 1];
  const bottom = last ? last.getBoundingClientRect().bottom : box.bottom;
  return { slide: i + 1, overflowPx: Math.round(Math.max(0, bottom - (box.bottom - padBottom))) };
}), feed ? '.tile' : '.slide');
for (const o of overflow){
  if (o.overflowPx > 0) console.warn(`  aviso: slide ${o.slide} se sale ${o.overflowPx}px del marco`);
}

if (feed){
  const tiles = await page.locator('.tile').all();
  for (const tile of tiles){
    const name = `${await tile.getAttribute('data-name')}-1080x1080.png`;
    await tile.screenshot({ path: join(outDir, 'feed', name) });
    console.log(`dist/feed/${name}`);
  }
} else {
  const slides = await page.locator('.slide').all();
  const names = ['portada', 'que-incluye', 'antes-despues', 'planes', 'contacto'];
  for (const [i, slide] of slides.entries()){
    const name = `${String(i + 1).padStart(2, '0')}-${names[i] || 'slide'}${suffix}.png`;
    await slide.screenshot({ path: join(outDir, name) });
    console.log(`dist/${name}`);
  }
}

await browser.close();
server.close();
