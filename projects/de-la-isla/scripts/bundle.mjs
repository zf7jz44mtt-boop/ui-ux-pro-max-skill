#!/usr/bin/env node
/* ==========================================================================
   bundle.mjs — flattens the site into dist/de-la-isla.html

   One file, no build tooling, no network at runtime (only the Google Fonts
   stylesheet stays remote). Handy for sending the page to a client, dropping
   it on any static host, or publishing it where external scripts are blocked.

     node scripts/bundle.mjs

   The ES-module graph is flattened by hand — no rollup/esbuild in the loop.
   three.js ships as three.module.js + three.core.js, plain ESM with a single
   import edge between them; each becomes an IIFE that returns its exports
   (they mint colliding internals like _m1$1, so they cannot share a scope),
   and our own modules are concatenated after them.
   ========================================================================== */

import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const read = (rel) => readFile(resolve(root, rel), 'utf8');

/** `A, B as C` -> ['A: A', 'C: B'] so we can rebuild a namespace object. */
function exportedPairs(list){
  return list
    .split(',')
    .map((entry) => entry.trim())
    .filter(Boolean)
    .map((entry) => {
      const [local, exported = local] = entry.split(/\s+as\s+/).map((s) => s.trim());
      return [exported, local];
    });
}

function stripThreeCore(src){
  const match = src.match(/^export \{([\s\S]*?)\};?\s*$/m);
  if (!match) throw new Error('three.core.js: no se encontró la lista de exports');
  return { code: src.replace(match[0], ''), pairs: exportedPairs(match[1]) };
}

function stripThreeModule(src){
  let code = src;

  // 1. the import edge into three.core.js — we keep the list to re-inject the
  //    same bindings inside the module's scope.
  const importEdge = code.match(/^import \{([\s\S]*?)\} from '\.\/three\.core\.js';$/m);
  if (!importEdge) throw new Error('three.module.js: no se encontró el import de three.core.js');
  const imported = exportedPairs(importEdge[1]);
  code = code.replace(importEdge[0], '');

  // 2. the re-export of core symbols (covered by spreading the core namespace)
  const reExport = code.match(/^export \{[\s\S]*?\} from '\.\/three\.core\.js';$/m);
  if (reExport) code = code.replace(reExport[0], '');

  // 3. its own export list
  const ownExport = code.match(/^export \{([\s\S]*?)\};?\s*$/m);
  if (!ownExport) throw new Error('three.module.js: no se encontró la lista de exports');
  const pairs = exportedPairs(ownExport[1]);
  code = code.replace(ownExport[0], '');

  return { code, pairs, imported };
}

/** Our own modules: drop the import lines and the `export` keyword. */
function stripLocalModule(src){
  return src
    .replace(/^import [\s\S]*?from '[^']+';$/gm, '')
    .replace(/^export (function|const|let|class|async function) /gm, '$1 ')
    .replace(/^export \{[\s\S]*?\};$/gm, '');
}

/** `{ exported: local, … }` for a namespace object literal. */
const nsObject = (pairs) => `{\n${pairs.map(([e, l]) => `  ${e}: ${l},`).join('\n')}\n}`;
/** `const { local: alias, … } = ns;` to bring imports back into scope. */
const nsDestructure = (pairs, from) =>
  `const {\n${pairs.map(([e, l]) => (e === l ? `  ${e},` : `  ${e}: ${l},`)).join('\n')}\n} = ${from};`;

const [html, animateCss, islaCss, coreSrc, moduleSrc, stagger, sliders, scene, main] = await Promise.all([
  read('index.html'),
  read('assets/css/vendor/animate.min.css'),
  read('assets/css/isla.css'),
  read('assets/js/vendor/three.core.js'),
  read('assets/js/vendor/three.module.js'),
  read('assets/js/stagger.js'),
  read('assets/js/sliders.js'),
  read('assets/js/isla-3d.js'),
  read('assets/js/main.js'),
]);

const core = stripThreeCore(coreSrc);
const mod = stripThreeModule(moduleSrc);

// three.core.js and three.module.js each mint their own suffixed internals
// (_m1$1 and friends), so they cannot share a scope: each becomes an IIFE that
// hands back only its exports.
const threeBundle = `const __THREE_CORE__ = (function(){
${core.code}
return ${nsObject(core.pairs)};
})();

const __THREE_MODULE__ = (function(){
${nsDestructure(mod.imported, '__THREE_CORE__')}
${mod.code}
return ${nsObject(mod.pairs)};
})();

const THREE = Object.freeze({ ...__THREE_CORE__, ...__THREE_MODULE__ });`;

const bundle = [
  '/* three.js r186dev — MIT — https://github.com/mrdoob/three.js */',
  threeBundle,
  '/* de-la-isla modules */',
  stripLocalModule(stagger),
  stripLocalModule(sliders),
  stripLocalModule(scene),
  stripLocalModule(main),
].join('\n');

if (bundle.includes('</script')) throw new Error('El bundle contiene "</script"; hay que escaparlo.');

// Replacer *functions*: the payloads contain `$'` and `$&` sequences (three.js
// builds regexes out of them), which a string replacement would expand.
let out = html
  .replace(/^\s*<link rel="stylesheet" href="assets\/css\/vendor\/animate\.min\.css">\s*$/m,
    () => `<style>\n/* animate.css 4.1.1 — MIT — https://animate.style */\n${animateCss}\n</style>`)
  .replace(/^\s*<link rel="stylesheet" href="assets\/css\/isla\.css">\s*$/m,
    () => `<style>\n${islaCss}\n</style>`)
  .replace(/^\s*<script type="module" src="assets\/js\/main\.js"><\/script>\s*$/m,
    () => `<script type="module">\n${bundle}\n</script>`);

for (const marker of ['animate.css 4.1.1', 'de-la-isla modules']){
  if (!out.includes(marker)) throw new Error(`La sustitución falló: falta "${marker}"`);
}

await mkdir(resolve(root, 'dist'), { recursive: true });
await writeFile(resolve(root, 'dist/de-la-isla.html'), out, 'utf8');

console.log(`dist/de-la-isla.html — ${(Buffer.byteLength(out) / 1024 / 1024).toFixed(2)} MB`);
