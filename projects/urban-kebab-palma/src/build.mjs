/* One source (urban-kebab.tpl.html) -> the artifact fragment and the standalone page. */
import { readFileSync, writeFileSync } from "node:fs";
const tpl = readFileSync("urban-kebab.tpl.html", "utf8");
const layout = JSON.parse(readFileSync("layout.json", "utf8"));
const assets = JSON.parse(readFileSync("assets.json", "utf8"));

const steps = JSON.stringify(
  layout.layers.map(L => ({ id: "#" + L.id, word: L.word, title: L.title, text: L.text }))
    .concat([{ id: null, ...layout.final }]));

const imgs = layout.layers.map(L =>
  `          <img class="ly" id="${L.id}" src="${assets[L.id].uri}" alt="" aria-hidden="true"\n` +
  `               style="--w:${L.w}%;--t:${L.t}%" decoding="async">`
).join("\n");

let body = tpl.replace("<!--LAYERS-->", imgs)
              .replace("/*STEPS*/", steps)
              .replace("--stack-ar-value", String(assets._stackAspect))
              .replace(/\{\{IMG:(\w+)\}\}/g, (_, k) => assets[k].uri);
writeFileSync("urban-kebab.html", body);

const head = body.slice(0, body.indexOf("<style>"));
const rest = body.slice(body.indexOf("<style>"));
writeFileSync("standalone.html", `<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="Urban Kebab Palma — kebab gourmet en Palma de Mallorca. Carne fresca de la Carnicería Rocha cada mañana, patata cortada a diario. Dos locales, abiertos de 13:00 a 23:30.">
<meta name="color-scheme" content="dark light">
${head.trim()}
<style>html,body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style>
${rest}
</body>
</html>
`);
console.log("built urban-kebab.html + standalone.html —", Math.round(body.length / 1024) + "KB fragment");
