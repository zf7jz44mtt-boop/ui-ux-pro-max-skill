# PULSO — Landing de agencia de marketing

Landing page de una página (`index.html`, sin build) generada con las bases de datos de
**ui-ux-pro-max**. PULSO es una marca ficticia; las cifras y testimonios son ilustrativos.

## Decisiones de diseño y su origen en la base de datos

| Decisión | Consulta | Resultado aplicado |
|---|---|---|
| Estilo | `--domain product "marketing agency landing page"` | `Marketing Agency` → Brutalism + Motion-Driven (secundario: Vibrant & Block-based) |
| Estructura | `--domain landing "storytelling-driven feature-rich"` | `scroll-triggered-storytelling`: gancho → cap. 01 problema → cap. 02 recorrido → cap. 03 solución → CTA clímax, con mini-CTA al final de cada capítulo e indicador de progreso |
| Color | `--domain color "marketing agency"` | `#EC4899` primario / `#0891B2` acento / `#FDF2F8` fondo / `#831843` texto |
| Tipografía | `--domain typography "bold display marketing agency"` | `Bold Statement`: Bebas Neue (solo titulares grandes) + Source Sans 3 |
| Movimiento | `--domain gsap "scroll reveal stagger hero"` | Scroll Reveal *Subtle*: opacidad + 12 px de desplazamiento, 350 ms, stagger de 30 ms |
| Layout | `--stack html-tailwind "responsive layout accessibility"` | Padding responsivo `px-4 sm:px-6 lg:px-8`, anchos móvil primero, `motion-reduce:` |

## Accesibilidad

Las guías (`--domain ux`) marcan el contraste como severidad alta, y los tokens puros de la
paleta no la superan como **texto** sobre fondo claro. Se añadieron dos variantes verificadas:

| Uso | Color | Ratio |
|---|---|---|
| ~~`#EC4899` como texto sobre blanco~~ | descartado | 3.53:1 ❌ |
| ~~`#0891B2` como texto sobre blanco~~ | descartado | 3.68:1 ❌ |
| ~~Texto blanco sobre bloque `#0891B2`~~ | descartado | 3.68:1 ❌ |
| `primary-ink` `#BE185D` sobre blanco | ✅ | 6.04:1 |
| `accent-ink` `#0E7490` sobre blanco | ✅ | 5.36:1 |
| Texto `#0F172A` sobre bloque `#0891B2` | ✅ | 4.85:1 |
| `#000000` sobre `#EC4899` (botones) | ✅ | 5.95:1 |
| `#475569` sobre `#FDF2F8` (cuerpo) | ✅ | 6.94:1 |

Los colores puros `primary`/`accent` se conservan solo como fondos de bloque y para iconos
decorativos sobre `#0F172A`.

Además: enlace de salto al contenido, foco visible de 3 px con `outline-offset`, menú móvil con
`aria-expanded`, formulario con `<label>` por campo y estado en `aria-live`, botón de pausa para
la marquesina (WCAG 2.2.2) y `prefers-reduced-motion` que renderiza cada capítulo en su estado
final legible. Los testimonios son una rejilla estática, sin rotación automática.

## Verificación

Render real en Chromium (1440×900 y 390×844): sin errores de JS, sin desbordamiento horizontal,
las 38 animaciones de entrada se completan, la barra de progreso va de 0% a 100%, el formulario
valida y devuelve el foco al primer campo inválido, y con `prefers-reduced-motion` ningún
elemento queda invisible.

## Uso

Abre `index.html` en el navegador. Tailwind se carga por CDN y las fuentes desde Google Fonts.
El formulario es una demo: no envía datos, hay que conectar un endpoint en el manejador `submit`.
