# Carrusel de Instagram — De la Isla

Cinco diapositivas para un carrusel de Instagram, con la misma identidad que la
web (`projects/de-la-isla`): tinta de mar, latón y arena, Playfair Display +
Inter + JetBrains Mono. Los mockups de móvil y el antes/después son capturas
reales del sitio, no imágenes de stock.

```
node export.mjs            # carrusel: dist/*-1080x1350.png  (4:5, formato de feed)
node export.mjs --square   # carrusel: dist/*-1080x1080.png  (cuadrado)
node export.mjs --feed     # 12 piezas del perfil: dist/feed/*-1080x1080.png
python3 build-profile.py   # maqueta del perfil: dist/profile.html
```

`carousel.html` también se puede abrir en el navegador: se ve la maqueta a
escala. El exportador quita esa escala antes de capturar.

## Qué hay aquí

- `carousel.html` — las cinco diapositivas del carrusel.
- `feed.html` — doce piezas sueltas (consejos, casos, precios, reel, marca) que
  llenan la primera pantalla del perfil.
- `build-profile.py` — monta `dist/profile.html`: la maqueta del perfil de
  Instagram con las doce piezas incrustadas, para enseñar cómo quedaría la
  cuenta antes de publicar nada.

## Las cinco diapositivas

| # | Diapositiva | Para qué sirve |
| --- | --- | --- |
| 01 | Portada | El gancho: qué hacemos y para quién. Móvil con la web real. |
| 02 | Qué incluye | Seis cosas concretas, sin jerga. |
| 03 | Antes y después | Prueba: la misma web antes y ahora, con tres números. |
| 04 | Planes | Precios claros, sin permanencia. |
| 05 | Contacto | La llamada a la acción y por dónde escribir. |

## Las doce piezas del perfil

Se alternan tres fondos —tinta de mar, papel y latón— para que ninguna fila de
la cuadrícula quede plana, y se reparten en cinco tipos: consejo o lista (4),
prueba (3), marca (2), servicio (2) y oferta (1). La maqueta del perfil explica
el sistema pieza a pieza.

## Antes de publicar

1. **Teléfono y correo son marcadores** (`+34 971 00 00 00`,
   `hola@delaisla.example`). Cámbialos en `carousel.html`, diapositivas 05.
2. Las **cifras del caso** (1,4 s · +64 % · −31 %) y los nombres de negocios son
   de ejemplo, igual que en la web. Sustitúyelos por datos reales antes de
   usarlos como prueba social.
3. El usuario `@delaisla` del pie es un marcador.

## Cómo se cambian las cosas

- **Textos**: directamente en `carousel.html`.
- **Colores y tipos**: `carousel.css`, bloque `:root` (los mismos tokens que la web).
- **Mockups**: son capturas del sitio en `assets/`. Para regenerarlas, sirve la
  web (`python3 -m http.server` desde `projects/de-la-isla`) y vuelve a
  capturarlas con Playwright, o sustituye los `.jpg` por los tuyos.
- **Fuentes**: `assets/fonts/` (subconjunto latino de Google Fonts, con
  `assets/fonts.css`). Van locales para que la exportación no dependa de la red.

El exportador avisa por consola si el contenido de una diapositiva se sale del
marco, que es la forma silenciosa de perder el pie de página en un PNG.

## Texto sugerido para la publicación

> Una web que trae clientes a tu puerta 🌅
>
> En Mallorca hay negocios buenísimos que casi nadie encuentra en Google. No
> porque trabajen mal, sino porque su web no está hecha para eso.
>
> Nosotros hacemos páginas con un solo objetivo: que te llamen.
> · Tu servicio explicado en claro
> · Ficha de Google y SEO local
> · WhatsApp y llamada siempre a la vista
> · Reservas que llegan a tu móvil
> · Español, català, English y Deutsch
>
> Trabajamos con restaurantes, hoteles rurales, tiendas y clínicas de Palma,
> Calvià, Sóller, Manacor y Alcúdia. Sin permanencia.
>
> ¿Te miramos tu Google y tu web? Diagnóstico gratuito en 24 h: escríbenos por
> DM o en el enlace de la bio.
>
> #Mallorca #Palma #MarketingLocal #NegociosDeMallorca #SEOLocal #Sóller
> #Manacor #Alcúdia #ComercioLocal #GoogleBusiness
