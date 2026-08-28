#!/usr/bin/env python3
"""Monta dist/post-01.html: la primera publicación lista para subir — las cinco
diapositivas en orden, el pie de foto, los textos alternativos, el primer
comentario y la biografía del perfil, todo con botón de copiar.

    node export.mjs && python3 build-post1.py
"""
import base64, io, os
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(HERE, 'dist')
OUT = os.path.join(DIST, 'post-01.html')

SOL = '\U0001F305'      # 🌅
MANO = '\U0001F447'     # 👇
PIN = '\U0001F4CD'      # 📍

SLIDES = [
    ('01-portada', 'Portada',
     'Portada del carrusel: «Una web que trae clientes a tu puerta», con un móvil que muestra la web de De la Isla.'),
    ('02-que-incluye', 'Qué incluye',
     'Lista de lo que lleva la página: el servicio explicado en claro, ficha de Google y SEO local, WhatsApp y llamada visibles, reservas que llegan al móvil, cuatro idiomas y mapa de zona.'),
    ('03-antes-despues', 'Antes y después',
     'Comparación de la web de un restaurante de Port de Sóller antes y después del rediseño, con las cifras de carga y reservas.'),
    ('04-planes', 'Planes',
     'Los tres planes mensuales: Cala 390 €, Tramuntana 790 € y Mediterráneo 1.450 €, todos sin permanencia.'),
    ('05-contacto', 'Contacto',
     'Cierre del carrusel: diagnóstico gratuito en 24 horas, con teléfono, correo y los pueblos donde trabajamos.'),
]

PIE = f"""No todos los negocios necesitan una web enorme. La mayoría necesita una que haga bien una sola cosa: que te llamen.

Trabajamos con restaurantes, hoteles rurales, tiendas y clínicas de Mallorca, y casi siempre el problema es el mismo: se les encuentra mal en Google, la web tarda ocho segundos en abrir y el teléfono está escondido en la tercera pantalla.

Lo que ponemos en una sola página:
· Tu servicio explicado en claro, sin palabras raras
· Ficha de Google y SEO local, para que aparezcas al buscar «cerca de mí»
· WhatsApp y llamada siempre a la vista
· Reservas que llegan a tu móvil, sin comisiones de portales
· Español, català, English y Deutsch

Sin permanencia, y con un informe al mes que se entiende: cuánto costó, cuánto entró y qué cambiamos.

¿Te miramos tu Google y tu web? Diagnóstico gratuito en 24 h — escríbenos por DM o entra por el enlace de la bio. {SOL}

{PIN} Palma · Calvià · Sóller · Manacor · Alcúdia

#Mallorca #Palma #MarketingLocal #NegociosDeMallorca #SEOLocal"""

COMENTARIO = """Y si te queda alguna duda, pregúntala aquí abajo: contestamos a todo, aunque no acabes contratando nada.

#DiseñoWeb #GoogleBusiness #ComercioLocal #Sóller #Manacor #Alcúdia #Calvià #RestaurantesMallorca #HotelRural #PequeñoComercio"""

BIO = f"""Webs y Google para negocios pequeños de Mallorca {SOL}
Sin permanencia · Respuesta en 24 h
Català · ES · EN · DE
{MANO} Diagnóstico gratis"""

PASOS = [
    ('p1', 'Revisar los datos de las diapositivas 3 y 4',
     'Las cifras del caso y los precios vienen de la demo. Si no son reales todavía, cámbialos o quita esa diapositiva antes de publicar.'),
    ('p2', 'Poner el teléfono, el correo y el enlace de verdad',
     'La diapositiva 5 lleva marcadores. Se regenera con <code>node export.mjs</code> después de editarlos.'),
    ('p3', 'Subir las cinco imágenes en orden, de la 01 a la 05',
     'Instagram respeta el orden en el que las seleccionas. Formato 4:5, sin recortar.'),
    ('p4', 'Pegar el pie de foto',
     'Los saltos de línea se conservan si lo pegas de una vez.'),
    ('p5', 'Escribir el texto alternativo de cada diapositiva',
     'Ajustes avanzados &rarr; Escribir texto alternativo. Ayuda a quien usa lector de pantalla y también al buscador.'),
    ('p6', 'Etiquetar la ubicación: Palma de Mallorca',
     'En los siguientes posts, ve rotando pueblo: Sóller, Manacor, Alcúdia.'),
    ('p7', 'Publicar y fijar el post arriba del perfil',
     'Tres puntos &rarr; Fijar en tu perfil. Es el post ancla mientras la cuenta es nueva.'),
    ('p8', 'Dejar el primer comentario con el resto de etiquetas',
     'Así el pie queda limpio y no pierdes alcance por hashtags.'),
    ('p9', 'Actualizar la biografía del perfil',
     'Es la de aquí abajo. Si ya la tenías puesta, comprueba que el enlace funciona.'),
    ('p10', 'Contestar los mensajes el mismo día',
     'La promesa del perfil es responder en 24 h: el primer post es justo cuando se comprueba.'),
]


def data_uri(path: str, width: int, quality: int = 84) -> str:
    im = Image.open(path).convert('RGB')
    im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, format='JPEG', quality=quality, optimize=True, progressive=True)
    return 'data:image/jpeg;base64,' + base64.b64encode(buf.getvalue()).decode()


SLIDE_URIS = {slug: data_uri(os.path.join(DIST, f'{slug}-1080x1350.png'), 420) for slug, *_ in SLIDES}


def slide_card(i, slug, titulo, alt):
    return f'''      <article class="slide">
        <span class="slide__n">{i:02d}</span>
        <img src="{SLIDE_URIS[slug]}" alt="Diapositiva {i}: {titulo}">
        <div class="slide__alt">
          <span class="tag">Texto alternativo</span>
          <p id="alt-{i}">{alt}</p>
          <button class="copy" data-copy="alt-{i}">Copiar</button>
        </div>
      </article>'''


def paso_row(key, texto, nota):
    return f'''      <label class="check"><input type="checkbox" data-k="{key}"><span>{texto}<small>{nota}</small></span></label>'''


html = f'''<title>Primer post de la Isla</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&family=Playfair+Display:ital,wght@0,500;1,500&display=swap">

<style>
  :root{{
    --sea-900:#07191F; --sea-850:#09202A; --sea-800:#0B242D;
    --gold:#D8A657; --gold-soft:#E8C68B; --terracotta:#C4643C; --teal:#2F8A87;
    --sand:#F3EADA; --sand-dim:rgba(243,234,218,.74); --sand-faint:rgba(243,234,218,.48);
    --line:rgba(243,234,218,.14); --line-strong:rgba(243,234,218,.28);
    --display:'Playfair Display',Georgia,serif;
    --body:'Inter',system-ui,-apple-system,sans-serif;
    --mono:'JetBrains Mono',ui-monospace,monospace;
  }}
  *,*::before,*::after{{ box-sizing:border-box; }}
  body{{
    margin:0; background:var(--sea-900); color:var(--sand);
    font-family:var(--body); font-size:16.5px; line-height:1.65;
    -webkit-font-smoothing:antialiased; padding:58px 22px 96px;
  }}
  .shell{{ width:min(100%, 1080px); margin-inline:auto; }}
  h1,h2,h3{{ font-family:var(--display); font-weight:500; margin:0; letter-spacing:-.02em; line-height:1.08; text-wrap:balance; }}
  h1{{ font-size:clamp(34px,5.4vw,58px); }}
  h1 em, h2 em{{ font-style:italic; color:var(--gold); }}
  h2{{ font-size:clamp(26px,3.4vw,36px); }}
  h3{{ font-size:19px; }}
  p{{ margin:0; }}
  .eyebrow{{
    font-family:var(--mono); font-size:11.5px; letter-spacing:.2em; text-transform:uppercase;
    color:var(--gold); display:flex; align-items:center; gap:14px; margin-bottom:20px;
  }}
  .eyebrow::before{{ content:""; width:32px; height:2px; background:var(--gold); flex:none; }}
  .lead{{ color:var(--sand-dim); max-width:66ch; margin-top:20px; font-size:17.5px; }}
  section{{ margin-top:62px; }}
  .sec-head{{ display:grid; gap:12px; margin-bottom:26px; }}
  .sec-head p{{ color:var(--sand-dim); max-width:70ch; }}
  .num{{ font-family:var(--mono); font-size:11.5px; letter-spacing:.18em; color:var(--gold); }}
  .tag{{ font-family:var(--mono); font-size:10.5px; letter-spacing:.16em; text-transform:uppercase; color:var(--gold); }}
  :focus-visible{{ outline:2px solid var(--gold); outline-offset:3px; border-radius:4px; }}
  code{{ font-family:var(--mono); font-size:13px; color:var(--gold-soft); }}

  .note{{
    border-left:3px solid var(--terracotta); background:rgba(196,100,60,.09);
    padding:18px 22px; border-radius:0 12px 12px 0; color:var(--sand-dim); font-size:15.5px;
  }}
  .note b{{ color:var(--sand); font-weight:500; }}
  .note + .note{{ margin-top:14px; }}

  /* ---- bloques de texto copiable ---- */
  .copyblock{{
    border:1px solid var(--line); border-radius:14px; padding:24px;
    background:rgba(243,234,218,.03); display:grid; gap:16px;
  }}
  .copyblock--pick{{ border-color:rgba(216,166,87,.45); background:linear-gradient(180deg, rgba(216,166,87,.09), rgba(216,166,87,.02)); }}
  .copyblock__head{{ display:flex; justify-content:space-between; align-items:center; gap:14px; flex-wrap:wrap; }}
  .copyblock pre{{
    margin:0; white-space:pre-wrap; font-family:var(--body); font-size:16px;
    line-height:1.6; color:var(--sand);
  }}
  .count{{ font-family:var(--mono); font-size:11px; color:var(--sand-faint); }}
  .copy{{
    background:none; border:1px solid var(--line-strong); color:var(--sand-dim); cursor:pointer;
    font-family:var(--mono); font-size:10.5px; letter-spacing:.14em; text-transform:uppercase;
    padding:9px 16px; border-radius:999px; transition:border-color .18s, color .18s;
    justify-self:start;
  }}
  .copy:hover{{ border-color:var(--gold); color:var(--gold); }}
  .copy.done{{ border-color:var(--teal); color:var(--teal); }}

  /* ---- diapositivas ---- */
  .slides{{ display:grid; gap:20px; }}
  .slide{{
    display:grid; grid-template-columns:auto 200px 1fr; gap:20px; align-items:start;
    border-top:1px solid var(--line); padding-top:20px;
  }}
  .slide__n{{ font-family:var(--mono); font-size:12px; color:var(--gold); padding-top:4px; }}
  .slide img{{ width:200px; border-radius:10px; border:1px solid var(--line); display:block; }}
  .slide__alt{{ display:grid; gap:10px; align-content:start; }}
  .slide__alt p{{ color:var(--sand-dim); font-size:15px; }}

  /* ---- checklist ---- */
  .checks{{ display:grid; gap:2px; border:1px solid var(--line); border-radius:14px; overflow:hidden; }}
  .check{{
    display:flex; gap:15px; align-items:flex-start; padding:15px 20px;
    background:rgba(243,234,218,.03); cursor:pointer; transition:background-color .18s;
  }}
  .check:hover{{ background:rgba(243,234,218,.06); }}
  .check input{{ width:20px; height:20px; margin-top:2px; accent-color:var(--gold); flex:none; }}
  .check span{{ font-size:15.5px; }}
  .check small{{ display:block; color:var(--sand-faint); font-size:13.5px; margin-top:3px; }}
  .check:has(input:checked) span{{ color:var(--sand-faint); text-decoration:line-through; text-decoration-color:rgba(216,166,87,.6); }}
  .checks-foot{{
    font-family:var(--mono); font-size:11px; letter-spacing:.14em; text-transform:uppercase;
    color:var(--sand-faint); margin-top:14px;
  }}

  footer{{
    margin-top:74px; border-top:1px solid var(--line); padding-top:24px;
    font-family:var(--mono); font-size:11px; letter-spacing:.12em; text-transform:uppercase;
    color:var(--sand-faint); display:flex; flex-wrap:wrap; gap:12px 26px; justify-content:space-between;
  }}
  @media (max-width:680px){{
    body{{ padding:44px 18px 72px; }}
    .slide{{ grid-template-columns:auto 110px 1fr; gap:14px; }}
    .slide img{{ width:110px; }}
  }}
  @media (prefers-reduced-motion:reduce){{ *{{ transition-duration:.001ms !important; }} }}
</style>

<div class="shell">
  <p class="eyebrow">De la Isla &middot; publicaci&oacute;n 01</p>
  <h1>El primer post,<br><em>listo para subir</em></h1>
  <p class="lead">
    El carrusel de cinco diapositivas, su pie de foto, el texto alternativo de cada imagen,
    el primer comentario y la biograf&iacute;a del perfil. Todo con bot&oacute;n de copiar, para hacerlo
    desde el m&oacute;vil.
  </p>

  <p class="note" style="margin-top:28px">
    <b>Yo no puedo publicarlo por ti:</b> no tengo conexi&oacute;n con tu Instagram, as&iacute; que el
    &uacute;ltimo paso &mdash; subir las im&aacute;genes y darle a compartir &mdash; lo haces t&uacute;. Aqu&iacute; est&aacute; todo
    preparado para que sea copiar y pegar.
  </p>

  <p class="note">
    <b>Antes de darle a publicar:</b> las cifras de la diapositiva 3 (&laquo;+64 % de reservas&raquo;) y
    los precios de la 4 vienen de la demo que montamos. Si todav&iacute;a no tienes ese caso real,
    c&aacute;mbialos por datos tuyos o quita esa diapositiva &mdash; publicar resultados de un cliente que
    no existe es publicidad enga&ntilde;osa, y en un sector local se nota r&aacute;pido.
  </p>

  <!-- 01 · el pie de foto -->
  <section>
    <div class="sec-head">
      <span class="num">01 &middot; Pie de foto</span>
      <h2>El texto que va <em>debajo</em></h2>
      <p>
        Empieza por el problema, no por nosotros. Las dos primeras l&iacute;neas son las &uacute;nicas que se
        ven sin pulsar &laquo;m&aacute;s&raquo;, as&iacute; que ah&iacute; va el gancho.
      </p>
    </div>
    <div class="copyblock copyblock--pick">
      <div class="copyblock__head">
        <span class="tag">Pie de foto</span>
        <span class="count" data-count="pie"></span>
      </div>
      <pre id="pie">{PIE}</pre>
      <button class="copy" data-copy="pie">Copiar pie de foto</button>
    </div>
  </section>

  <!-- 02 · las cinco imágenes -->
  <section>
    <div class="sec-head">
      <span class="num">02 &middot; Las im&aacute;genes</span>
      <h2>Cinco diapositivas, <em>en este orden</em></h2>
      <p>
        Est&aacute;n en <code>social/dist/</code> en 1080 &times; 1350. Instagram respeta el orden en el que
        las seleccionas al subirlas.
      </p>
    </div>
    <div class="slides">
{chr(10).join(slide_card(i + 1, slug, titulo, alt) for i, (slug, titulo, alt) in enumerate(SLIDES))}
    </div>
  </section>

  <!-- 03 · primer comentario -->
  <section>
    <div class="sec-head">
      <span class="num">03 &middot; Primer comentario</span>
      <h2>El resto de <em>etiquetas</em></h2>
      <p>
        Cinco hashtags en el pie y el resto aqu&iacute;: el texto queda limpio y no pierdes alcance.
        P&uacute;blicalo t&uacute; mismo justo despu&eacute;s de publicar el post.
      </p>
    </div>
    <div class="copyblock">
      <div class="copyblock__head">
        <span class="tag">Primer comentario</span>
        <span class="count" data-count="comentario"></span>
      </div>
      <pre id="comentario">{COMENTARIO}</pre>
      <button class="copy" data-copy="comentario">Copiar comentario</button>
    </div>
  </section>

  <!-- 04 · biografía -->
  <section>
    <div class="sec-head">
      <span class="num">04 &middot; Biograf&iacute;a</span>
      <h2>La bio del <em>perfil</em></h2>
      <p>
        Que est&eacute; puesta antes de que llegue la primera visita desde el post: mucha gente entra al
        perfil desde el carrusel y decide ah&iacute; si escribe o no.
      </p>
    </div>
    <div class="copyblock">
      <div class="copyblock__head">
        <span class="tag">Biograf&iacute;a &middot; m&aacute;ximo 150</span>
        <span class="count" data-count="bio"></span>
      </div>
      <pre id="bio">{BIO}</pre>
      <button class="copy" data-copy="bio">Copiar biograf&iacute;a</button>
    </div>
  </section>

  <!-- 05 · pasos -->
  <section>
    <div class="sec-head">
      <span class="num">05 &middot; Al publicar</span>
      <h2>Los diez pasos</h2>
      <p>Se guardan en este navegador, as&iacute; que puedes ir tachando desde el m&oacute;vil.</p>
    </div>
    <div class="checks" id="checks">
{chr(10).join(paso_row(k, t, n) for k, t, n in PASOS)}
    </div>
    <p class="checks-foot" id="progreso">0 de {len(PASOS)} hechos</p>
  </section>

  <footer>
    <span>De la Isla &middot; publicaci&oacute;n 01</span>
    <span>Im&aacute;genes en social/dist/*-1080x1350.png</span>
  </footer>
</div>

<script>
  // ---------- contadores ----------
  const LIMITES = {{ pie: 2200, comentario: 2200, bio: 150 }};
  Object.entries(LIMITES).forEach(([id, limite]) => {{
    const texto = document.getElementById(id).textContent;
    const n = [...texto].length;
    const el = document.querySelector(`[data-count="${{id}}"]`);
    el.textContent = n + ' / ' + limite;
    if (n > limite) el.style.color = '#E08A6A';
  }});

  // ---------- copiar ----------
  document.querySelectorAll('.copy').forEach((btn) => {{
    btn.addEventListener('click', async () => {{
      const nodo = document.getElementById(btn.dataset.copy);
      const previo = btn.textContent;
      try {{
        await navigator.clipboard.writeText(nodo.textContent);
        btn.textContent = 'Copiado';
        btn.classList.add('done');
        setTimeout(() => {{ btn.textContent = previo; btn.classList.remove('done'); }}, 1600);
      }} catch {{
        const rango = document.createRange();
        rango.selectNodeContents(nodo);
        const sel = window.getSelection();
        sel.removeAllRanges();
        sel.addRange(rango);
        btn.textContent = 'Selecciona y copia';
        setTimeout(() => {{ btn.textContent = previo; }}, 2400);
      }}
    }});
  }});

  // ---------- checklist ----------
  const KEY = 'delaisla-post01';
  const casillas = Array.from(document.querySelectorAll('#checks input'));
  const leer = () => {{ try {{ return JSON.parse(localStorage.getItem(KEY) || '{{}}'); }} catch {{ return {{}}; }} }};
  const guardar = (e) => {{ try {{ localStorage.setItem(KEY, JSON.stringify(e)); }} catch {{}} }};
  const pintar = () => {{
    const hechos = casillas.filter((c) => c.checked).length;
    document.getElementById('progreso').textContent = hechos + ' de ' + casillas.length + ' hechos';
  }};
  const estado = leer();
  casillas.forEach((c) => {{
    if (estado[c.dataset.k]) c.checked = true;
    c.addEventListener('change', () => {{
      const actual = leer();
      actual[c.dataset.k] = c.checked;
      guardar(actual);
      pintar();
    }});
  }});
  pintar();
</script>
'''

ascii_html = html.encode('ascii', 'xmlcharrefreplace').decode('ascii')
os.makedirs(DIST, exist_ok=True)
with open(OUT, 'w') as fh:
    fh.write(ascii_html)
print('dist/post-01.html', os.path.getsize(OUT) // 1024, 'KB')
print('pie de foto:', len(PIE), 'caracteres')
print('comentario:', len(COMENTARIO), 'caracteres')
print('bio:', len(BIO), 'caracteres')
