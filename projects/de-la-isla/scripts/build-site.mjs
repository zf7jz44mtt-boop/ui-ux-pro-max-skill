#!/usr/bin/env node
/* ==========================================================================
   build-site.mjs — prepara dist/site/ con lo que se sube al hosting y nada más.

     node scripts/build-site.mjs

   Deja fuera lo que vive en el repositorio pero no en la web: las piezas de
   redes (social/), el archivo único de dist/ y los scripts de construcción.
   La carpeta resultante se arrastra tal cual a Netlify.
   ========================================================================== */

import { cp, mkdir, rm, readdir, stat, readFile, writeFile } from 'node:fs/promises';
import { spawnSync } from 'node:child_process';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const out = join(root, 'dist', 'site');

const ARCHIVOS = [
  'index.html',
  'aviso-legal.html',
  'privacidad.html',
  '404.html',
  'robots.txt',
  'sitemap.xml',
  'netlify.toml',
];
const CARPETAS = ['assets'];

async function tamano(dir){
  let total = 0;
  for (const entrada of await readdir(dir, { withFileTypes: true })){
    const ruta = join(dir, entrada.name);
    total += entrada.isDirectory() ? await tamano(ruta) : (await stat(ruta)).size;
  }
  return total;
}

await rm(out, { recursive: true, force: true });
await mkdir(out, { recursive: true });

for (const archivo of ARCHIVOS) await cp(join(root, archivo), join(out, archivo));
for (const carpeta of CARPETAS) await cp(join(root, carpeta), join(out, carpeta), { recursive: true });

// three.js sin minificar son 2,1 MB. esbuild lo empaqueta con nuestros módulos
// en un solo archivo de ~550 kB (unos 140 kB por la red, ya comprimido).
const salida = join(out, 'assets', 'js', 'app.min.js');
const esbuild = spawnSync('npx', [
  '--yes', 'esbuild@0.25.0', join(root, 'assets/js/main.js'),
  '--bundle', '--format=esm', '--minify', '--target=es2020', `--outfile=${salida}`,
], { encoding: 'utf8', timeout: 240000 });

if (esbuild.status === 0){
  // Fuera los módulos sueltos: en producción solo viaja el empaquetado.
  for (const sobra of ['vendor', 'main.js', 'isla-3d.js', 'sliders.js', 'stagger.js']){
    await rm(join(out, 'assets', 'js', sobra), { recursive: true, force: true });
  }
  const html = join(out, 'index.html');
  const marcado = await readFile(html, 'utf8');
  await writeFile(html, marcado.replace('src="assets/js/main.js"', 'src="assets/js/app.min.js"'), 'utf8');
  console.log('JavaScript empaquetado y minificado con esbuild.');
} else {
  console.warn('aviso: esbuild no se pudo ejecutar; se suben los módulos sin minificar.');
  console.warn(`  ${(esbuild.stderr || esbuild.error?.message || '').split('\n')[0]}`);
}

const bytes = await tamano(out);
console.log(`dist/site/ listo — ${(bytes / 1024 / 1024).toFixed(2)} MB`);
console.log(`  ${ARCHIVOS.length} archivos + ${CARPETAS.join(', ')}`);
console.log('  Arrástralo a app.netlify.com/drop o conéctalo por Git.');
