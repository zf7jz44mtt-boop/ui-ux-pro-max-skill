# De la Isla — agencia de marketing en Mallorca

Landing page de una agencia de marketing ficticia con sede en Palma que trabaja
con negocios pequeños de la isla: restaurantes, hoteles rurales, tiendas,
clínicas y alquiler náutico.

Es una página estática, sin framework y sin dependencias de red en tiempo de
ejecución (salvo la hoja de Google Fonts). Todo lo demás —el motor 3D, las
animaciones y los sliders— va servido desde el propio proyecto.

```
python3 -m http.server 8000       # ver la web en local
node scripts/build-site.mjs       # preparar dist/site/ para el hosting
node scripts/bundle.mjs           # archivo único dist/de-la-isla.html
```

> Hace falta un servidor: `index.html` carga módulos ES y el navegador los
> bloquea sobre `file://`. Si necesitas abrirlo con doble clic, usa el archivo
> único de `dist/` (ver más abajo).

## Qué hay dentro

| Pieza | Dónde | Qué hace |
| --- | --- | --- |
| Escena 3D del hero | `assets/js/isla-3d.js` | Amanecer mediterráneo con three.js: mar con shader propio, isla low-poly con pinos y faro, cúpula de cielo con degradado y motas de luz. |
| Slider 3D de casos | `assets/js/sliders.js` → `initCoverflow` | Cover-flow con arrastre, swipe, teclado, puntos, autoplay y anuncio por `aria-live`. |
| Antes / después | `assets/js/sliders.js` → `initCompare` | Comparador con tirador arrastrable y operable con ← → (rol `slider` con `aria-valuenow`). |
| Calculadora de presupuesto | `assets/js/sliders.js` → `initBudget` | El rango recomienda plan, horas y servicios, y resalta la tarjeta de precio correspondiente. |
| Revelado escalonado | `assets/js/stagger.js` | Port a web de `flutter_staggered_animations`. |
| Empaquetado a un solo archivo | `scripts/bundle.mjs` | Genera `dist/de-la-isla.html`. |

## Cómo se usan los repositorios

- **three.js** (`build/three.module.js` + `build/three.core.js`, r186dev) —
  copiados tal cual a `assets/js/vendor/`. La escena sigue las pautas del
  stack `threejs` de ui-ux-pro-max: presupuesto de segmentos por rol, nada de
  shadow maps donde no aportan, entrada de ratón **y** táctil, `devicePixelRatio`
  limitado a 2 y bucle de render parado fuera de pantalla o con la pestaña oculta.
  El agua calcula su normal de forma analítica en el vertex shader (derivada de
  la suma de senos): con la normal por derivadas de pantalla, el brillo del sol
  se rompía en triángulos visibles.
- **animate.css** (4.1.1) — `animate.min.css` en `assets/css/vendor/`. Se aplica
  con `data-animate="fadeInUp"` y un `IntersectionObserver` (`main.js`), nunca
  para usuarios con `prefers-reduced-motion`.
- **flutter_staggered_animations** (1.1.1) — portado, no copiado. `stagger.js`
  reproduce la semántica del paquete Dart: duración 225 ms, retardo
  `duración ÷ 6`, fórmula de rejilla
  `(posición ÷ columnas + posición % columnas) × retardo`, curva `Curves.ease`
  (`cubic-bezier(.25,.1,.25,1)`) y desplazamiento de 50 px de `SlideAnimation`.
  Se declara en el HTML con `data-stagger="grid" data-columns="3"`.
- **ui-ux-pro-max** — usado como fuente de decisiones de diseño:
  `search.py "marketing agency landing page local small business" --domain product`,
  `--domain typography` (de ahí Playfair Display + Inter, con JetBrains Mono para
  etiquetas) y `--stack threejs`. La paleta rosa que la base de datos asocia a
  “Marketing Agency” se sustituyó por una mediterránea (tinta de mar, arena,
  latón y terracota), que encaja mejor con la marca; el resto de recomendaciones
  se respetó.
- **everything-claude-code** — su skill `frontend-patterns` es de React, así que
  aquí sólo se aplicó su criterio (composición, estado mínimo, sin capas
  innecesarias) sobre JavaScript plano.

## Archivo único

```
node scripts/bundle.mjs        # -> dist/de-la-isla.html (~2,2 MB)
```

`dist/` está en el `.gitignore` del repositorio, así que el archivo se genera
cuando hace falta; el script sí está versionado.

Aplana el grafo de módulos sin bundler: three.core.js y three.module.js pasan a
ser sendas IIFE que devuelven sus exports (comparten nombres internos como
`_m1$1`, así que no pueden compartir ámbito), y encima se concatenan los módulos
del proyecto. El resultado se abre con doble clic y se puede enviar por correo o
publicar en cualquier sitio que bloquee scripts externos.

## Publicar

`node scripts/build-site.mjs` deja en `dist/site/` exactamente lo que se sube y
nada más: las cuatro páginas, `assets/`, `robots.txt`, `sitemap.xml` y
`netlify.toml`. Por el camino empaqueta y minifica el JavaScript con esbuild
(2,1 MB de módulos sueltos → 550 kB, unos 140 kB por la red), así que la carpeta
pesa **~1 MB**. Se arrastra a [app.netlify.com/drop](https://app.netlify.com/drop)
o se conecta por Git.

El formulario usa **Netlify Forms**: se detecta solo al desplegar porque el HTML
lleva `data-netlify="true"` y el campo oculto `form-name`. Los envíos aparecen en
el panel de Netlify, en Forms → *contacto*. Se envía por `fetch`, así que si algo
falla el visitante ve un aviso con el enlace de WhatsApp en vez de perder el
mensaje.

Las tipografías se sirven desde `assets/fonts/` (subconjunto latino de Google
Fonts). Sin peticiones a Google: una carga menos y ningún dato del visitante
viaja a un tercero, que es lo que permite no poner banner de cookies.

### Antes de publicar

1. **Dominio**: `delaisla.es` aparece en `canonical`, `og:url`, `sitemap.xml` y
   `robots.txt`. Si el dominio es otro, cámbialo en esos cuatro sitios.
2. **Aviso legal y privacidad**: llevan `[NOMBRE Y APELLIDOS]`, `[NIF]`,
   `[DIRECCIÓN FISCAL]` y `[CORREO DE CONTACTO]` sin rellenar. La LSSI obliga a
   identificar al titular, así que no se publica sin eso.
3. **Analítica**: si añades una, que sea sin cookies (Plausible, Umami o la de
   Cloudflare). Con Google Analytics harían falta banner y política de cookies.

## Accesibilidad

- `prefers-reduced-motion` desactiva transiciones, animaciones, autoplay del
  slider, el bucle 3D (queda un fotograma fijo) y el conteo de cifras.
- Todos los sliders funcionan con teclado: ← → Inicio Fin en el cover-flow y en
  el comparador; el estado se anuncia con `aria-live`.
- Menú móvil con `aria-expanded`, cierre con `Escape` y foco devuelto al botón.
- Enfoque visible (`:focus-visible`), enlace de salto al contenido, formulario
  con validación en línea y mensajes de error asociados.
- Si WebGL falla, el `<canvas>` conserva el degradado CSS de respaldo y el resto
  de la página funciona igual.

## Qué se quitó al preparar el lanzamiento

La primera versión llevaba contenido de demostración que no podía publicarse:
cinco casos de clientes inventados, tres testimonios firmados con nombre y
apellido, un antes/después atribuido a un restaurante concreto y un contador de
«38 negocios · 4,9 de valoración». Todo eso salió de la web — publicar
resultados y reseñas que no existen es publicidad engañosa. Cuando haya casos
reales, se vuelven a montar con el mismo diseño (está en el historial de Git).
