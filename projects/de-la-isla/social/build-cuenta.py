#!/usr/bin/env python3
"""Monta dist/cuenta.html: todo lo que hay que pegar para abrir la cuenta de
Instagram (foto, nombre, usuario, bio, destacados, primeras publicaciones).

    node export.mjs --brand && node export.mjs --feed && python3 build-cuenta.py

Las imágenes van incrustadas en base64 y el HTML se escribe en ASCII puro con
entidades numéricas, para que la página se lea igual aunque se sirva sin
charset declarado.
"""
import base64, io, os
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
PERFIL = os.path.join(HERE, 'dist', 'perfil')
FEED = os.path.join(HERE, 'dist', 'feed')
OUT = os.path.join(HERE, 'dist', 'cuenta.html')


def data_uri(im: Image.Image, quality: int = 86) -> str:
    buf = io.BytesIO()
    im.convert('RGB').save(buf, format='JPEG', quality=quality, optimize=True, progressive=True)
    return 'data:image/jpeg;base64,' + base64.b64encode(buf.getvalue()).decode()


def square(path: str, size: int) -> str:
    return data_uri(Image.open(path).resize((size, size), Image.LANCZOS))


def story_center(path: str, size: int) -> str:
    """El trozo de la story que Instagram recorta como portada del destacado."""
    im = Image.open(path)
    top = (im.height - im.width) // 2
    return data_uri(im.crop((0, top, im.width, top + im.width)).resize((size, size), Image.LANCZOS))


AVATAR_DARK = square(os.path.join(PERFIL, 'avatar-oscuro.png'), 420)
AVATAR_PAPER = square(os.path.join(PERFIL, 'avatar-papel.png'), 420)
AVATAR_SMALL = square(os.path.join(PERFIL, 'avatar-oscuro.png'), 120)

COVERS = [
    ('Casos', 'destacado-casos',
     'Los cinco casos: un vídeo corto o unas capturas por cliente, con la cifra que consiguió.'),
    ('Antes/después', 'destacado-antes-despues',
     'Capturas de la web vieja y la nueva, una detrás de otra. Es el destacado que más se mira.'),
    ('Precios', 'destacado-precios',
     'Los tres planes con lo que incluye cada uno y la frase de «sin permanencia».'),
    ('La isla', 'destacado-la-isla',
     'Quién está detrás, el estudio, los pueblos donde trabajáis. Da confianza antes de escribir.'),
]
COVER_URIS = {slug: story_center(os.path.join(PERFIL, slug + '.png'), 360) for _, slug, _ in COVERS}

PRIMEROS = [
    ('01-web-que-trae-clientes', 'Una web que trae clientes', 'Carrusel de 5. El post fijado.'),
    ('02-ficha-google', 'Tu ficha de Google es tu escaparate', 'Consejo, sin venta.'),
    ('03-bon-dia', 'Bon dia des de Mallorca', 'Marca y sitio. Da aire.'),
    ('05-tres-errores', 'Tres errores en tu ficha de Google', 'El que trae seguidores.'),
    ('06-caso-soller', '+64 % reservas directas', 'La primera prueba.'),
    ('07-desde-390', 'Desde 390 € al mes', 'Precio a la vista.'),
    ('08-antes-despues', 'La misma cocina, dos webs', 'La prueba visual.'),
    ('09-fotos-reales', 'Una foto de tu cocina', 'Consejo que vende contenido.'),
    ('11-diagnostico', 'Diagnóstico gratuito en 24 h', 'La oferta, la novena.'),
]
PRIMEROS_URIS = {slug: square(os.path.join(FEED, slug + '-1080x1080.png'), 200) for slug, *_ in PRIMEROS}

SOL = '\U0001F305'    # 🌅
MANO = '\U0001F447'   # 👇

BIOS = [
    ('Recomendada', f"""Webs y Google para negocios pequeños de Mallorca {SOL}
Sin permanencia · Respuesta en 24 h
Català · ES · EN · DE
{MANO} Diagnóstico gratis"""),
    ('Más corta', f"""Marketing para negocios pequeños de Mallorca {SOL}
Webs que reservan · Google · Redes
Sin permanencia · 24 h
{MANO} Diagnóstico gratis"""),
    ('Más directa', f"""Hacemos que te encuentren y te llamen {SOL}
Webs y Google para negocios de la isla
Sin permanencia · Respuesta en 24 h
{MANO} Diagnóstico gratis"""),
]

CAMPOS = [
    ('Nombre', 'De la Isla · Marketing Palma',
     'Es el campo que indexa el buscador de Instagram, así que lleva la palabra clave y la ciudad. Máximo 30 caracteres (este ocupa 28).'),
    ('Usuario', '@delaisla.mallorca',
     'Alternativas si está cogido: @somosdelaisla, @delaisla.studio, @delaisla.mkt. Comprueba de paso que el mismo nombre esté libre en el dominio y en LinkedIn.'),
    ('Categoría', 'Agencia de publicidad / Marketing',
     'Solo aparece en cuentas profesionales. Elige la que más se parezca; se cambia cuando quieras.'),
    ('Enlace de la bio', 'delaisla.example/?utm_source=instagram',
     'Un solo enlace, directo a la web. La UTM te dice en Analytics cuánta gente llega desde aquí.'),
    ('Botones de contacto', 'WhatsApp, correo y dirección',
     'Se activan al pasar a cuenta profesional. El de WhatsApp es el que más se usa en negocio local.'),
    ('Zona', 'Palma de Mallorca',
     'Pon la ubicación en el perfil y etiqueta un pueblo distinto en cada publicación: Sóller, Manacor, Alcúdia.'),
]

AJUSTES = [
    ('a1', 'Crear la cuenta y pasarla a profesional', 'Ajustes &rarr; Tipo de cuenta &rarr; Cuenta de empresa.'),
    ('a2', 'Subir la foto de perfil (versi&oacute;n oscura)', 'El archivo est&aacute; en social/dist/perfil/avatar-oscuro.png.'),
    ('a3', 'Rellenar nombre, usuario, categor&iacute;a y bio', 'Copia los textos de esta p&aacute;gina.'),
    ('a4', 'Activar los botones de contacto', 'WhatsApp, correo y direcci&oacute;n del estudio.'),
    ('a5', 'Poner el enlace de la bio con UTM', 'Y comprobar que la web abre bien en m&oacute;vil.'),
    ('a6', 'Publicar las nueve primeras piezas antes de dar difusi&oacute;n', 'Un perfil con tres posts no convierte; con nueve, s&iacute;.'),
    ('a7', 'Fijar arriba el carrusel &ldquo;Una web que trae clientes&rdquo;', 'Instagram deja fijar hasta tres.'),
    ('a8', 'Crear los cuatro destacados con sus portadas', 'Sube la portada como story, gu&aacute;rdala en el destacado y luego a&ntilde;ade el contenido.'),
    ('a9', 'Vincular la p&aacute;gina de Facebook si vas a hacer anuncios', 'Sin p&aacute;gina vinculada no se puede promocionar desde Meta.'),
    ('a10', 'Escribir los tres primeros mensajes guardados', 'Respuestas r&aacute;pidas para &ldquo;&iquest;cu&aacute;nto cuesta?&rdquo;, &ldquo;&iquest;hac&eacute;is webs?&rdquo; y &ldquo;pedir diagn&oacute;stico&rdquo;.'),
]


def bio_block(i, titulo, texto):
    return f'''      <article class="bio">
        <div class="bio__head">
          <span class="tag">{titulo}</span>
          <span class="count" data-count="{i}"></span>
        </div>
        <pre id="bio-{i}">{texto}</pre>
        <button class="copy" data-copy="bio-{i}">Copiar</button>
      </article>'''


def campo_row(nombre, valor, nota, i):
    return f'''        <tr>
          <td><b>{nombre}</b></td>
          <td><code id="campo-{i}">{valor}</code><button class="copy copy--sm" data-copy="campo-{i}">Copiar</button></td>
          <td class="muted">{nota}</td>
        </tr>'''


def cover_card(nombre, slug, nota):
    return f'''      <article class="cover">
        <span class="cover__img"><img src="{COVER_URIS[slug]}" alt="Portada del destacado {nombre}"></span>
        <div>
          <h3>{nombre}</h3>
          <p>{nota}</p>
        </div>
      </article>'''


def primero_card(i, slug, titulo, nota):
    return f'''      <article class="first">
        <span class="first__n">{i:02d}</span>
        <img src="{PRIMEROS_URIS[slug]}" alt="">
        <div><b>{titulo}</b><small>{nota}</small></div>
      </article>'''


def ajuste_row(key, texto, nota):
    return f'''      <label class="check"><input type="checkbox" data-k="{key}"><span>{texto}<small>{nota}</small></span></label>'''


html = f'''<title>Abrir @delaisla</title>
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
  h3{{ font-size:20px; }}
  p{{ margin:0; }}
  .eyebrow{{
    font-family:var(--mono); font-size:11.5px; letter-spacing:.2em; text-transform:uppercase;
    color:var(--gold); display:flex; align-items:center; gap:14px; margin-bottom:20px;
  }}
  .eyebrow::before{{ content:""; width:32px; height:2px; background:var(--gold); flex:none; }}
  .lead{{ color:var(--sand-dim); max-width:66ch; margin-top:20px; font-size:17.5px; }}
  section{{ margin-top:64px; }}
  .sec-head{{ display:grid; gap:12px; margin-bottom:26px; }}
  .sec-head p{{ color:var(--sand-dim); max-width:70ch; }}
  .num{{ font-family:var(--mono); font-size:11.5px; letter-spacing:.18em; color:var(--gold); }}
  .muted{{ color:var(--sand-faint); }}
  :focus-visible{{ outline:2px solid var(--gold); outline-offset:3px; border-radius:4px; }}

  .note{{
    border-left:3px solid var(--terracotta); background:rgba(196,100,60,.09);
    padding:18px 22px; border-radius:0 12px 12px 0; color:var(--sand-dim); font-size:15.5px;
  }}
  .note b{{ color:var(--sand); font-weight:500; }}

  /* ---- foto de perfil ---- */
  .avatars{{ display:grid; grid-template-columns:repeat(auto-fit,minmax(300px,1fr)); gap:22px; }}
  .av{{
    border:1px solid var(--line); border-radius:16px; padding:26px;
    background:linear-gradient(180deg, rgba(243,234,218,.045), rgba(243,234,218,.012));
    display:grid; gap:16px; justify-items:center; text-align:center;
  }}
  .av--pick{{ border-color:rgba(216,166,87,.5); background:linear-gradient(180deg, rgba(216,166,87,.10), rgba(216,166,87,.02)); }}
  .av img{{ border-radius:50%; display:block; }}
  .av .tag{{ font-family:var(--mono); font-size:10.5px; letter-spacing:.16em; text-transform:uppercase; color:var(--gold); }}
  .av p{{ color:var(--sand-dim); font-size:15px; }}
  .sizes{{ display:flex; align-items:flex-end; gap:16px; justify-content:center; margin-top:4px; }}
  .sizes figure{{ margin:0; display:grid; gap:8px; justify-items:center; }}
  .sizes img{{ border-radius:50%; display:block; }}
  .sizes figcaption{{ font-family:var(--mono); font-size:10px; letter-spacing:.1em; color:var(--sand-faint); }}
  .path{{
    font-family:var(--mono); font-size:12px; color:var(--sand-faint);
    border:1px dashed var(--line-strong); border-radius:8px; padding:8px 12px;
  }}

  /* ---- tabla de campos ---- */
  .tablewrap{{ overflow-x:auto; border:1px solid var(--line); border-radius:14px; }}
  table{{ border-collapse:collapse; width:100%; min-width:640px; font-size:15px; }}
  th,td{{ text-align:left; padding:15px 18px; border-bottom:1px solid var(--line); vertical-align:top; }}
  thead th{{
    font-family:var(--mono); font-size:10.5px; letter-spacing:.16em; text-transform:uppercase;
    color:var(--gold); font-weight:400; background:rgba(243,234,218,.04);
  }}
  tbody tr:last-child td{{ border-bottom:0; }}
  code{{ font-family:var(--mono); font-size:13.5px; color:var(--gold-soft); }}

  /* ---- copiar ---- */
  .copy{{
    background:none; border:1px solid var(--line-strong); color:var(--sand-dim); cursor:pointer;
    font-family:var(--mono); font-size:10.5px; letter-spacing:.14em; text-transform:uppercase;
    padding:8px 14px; border-radius:999px; transition:border-color .18s, color .18s;
  }}
  .copy:hover{{ border-color:var(--gold); color:var(--gold); }}
  .copy--sm{{ margin-left:10px; padding:5px 11px; font-size:9.5px; vertical-align:middle; }}
  .copy.done{{ border-color:var(--teal); color:var(--teal); }}

  /* ---- bios ---- */
  .bios{{ display:grid; grid-template-columns:repeat(auto-fit,minmax(290px,1fr)); gap:18px; }}
  .bio{{
    border:1px solid var(--line); border-radius:14px; padding:22px;
    background:rgba(243,234,218,.03); display:grid; gap:14px; align-content:start;
  }}
  .bio__head{{ display:flex; justify-content:space-between; align-items:center; gap:12px; }}
  .bio .tag{{ font-family:var(--mono); font-size:10.5px; letter-spacing:.16em; text-transform:uppercase; color:var(--gold); }}
  .bio .count{{ font-family:var(--mono); font-size:11px; color:var(--sand-faint); }}
  .bio pre{{
    margin:0; white-space:pre-wrap; font-family:var(--body); font-size:15.5px;
    line-height:1.55; color:var(--sand);
  }}
  .bio button{{ justify-self:start; }}

  /* ---- destacados ---- */
  .covers{{ display:grid; grid-template-columns:repeat(auto-fit,minmax(300px,1fr)); gap:22px; }}
  .cover{{ display:grid; grid-template-columns:120px 1fr; gap:18px; align-items:start; }}
  .cover__img{{ width:120px; height:120px; border-radius:50%; overflow:hidden; display:block; border:1px solid var(--line); }}
  .cover__img img{{ width:100%; height:100%; display:block; }}
  .cover p{{ color:var(--sand-dim); font-size:14.5px; margin-top:6px; }}

  /* ---- primeras publicaciones ---- */
  .firsts{{ display:grid; grid-template-columns:repeat(auto-fit,minmax(280px,1fr)); gap:16px; }}
  .first{{ display:grid; grid-template-columns:auto 76px 1fr; gap:14px; align-items:center; }}
  .first__n{{ font-family:var(--mono); font-size:11px; color:var(--gold); }}
  .first img{{ width:76px; height:76px; border-radius:9px; border:1px solid var(--line); display:block; }}
  .first b{{ font-weight:500; font-size:15px; display:block; }}
  .first small{{ color:var(--sand-faint); font-size:13px; }}

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
    margin-top:76px; border-top:1px solid var(--line); padding-top:24px;
    font-family:var(--mono); font-size:11px; letter-spacing:.12em; text-transform:uppercase;
    color:var(--sand-faint); display:flex; flex-wrap:wrap; gap:12px 26px; justify-content:space-between;
  }}
  @media (max-width:620px){{
    body{{ padding:44px 18px 72px; }}
    .first{{ grid-template-columns:auto 60px 1fr; }}
    .first img{{ width:60px; height:60px; }}
  }}
  @media (prefers-reduced-motion:reduce){{ *{{ transition-duration:.001ms !important; }} }}
</style>

<div class="shell">
  <p class="eyebrow">De la Isla &middot; Instagram</p>
  <h1>Todo lo que hace falta<br>para <em>abrir la cuenta</em></h1>
  <p class="lead">
    La foto de perfil, los textos exactos que van en cada campo, las portadas de los
    destacados y el orden de las nueve primeras publicaciones. Los botones de copiar dejan
    el texto listo para pegar en la app.
  </p>

  <!-- 01 foto de perfil -->
  <section>
    <div class="sec-head">
      <span class="num">01 &middot; Foto de perfil</span>
      <h2>El sol y las <em>dos olas</em>, sin texto</h2>
      <p>
        A 32 p&iacute;xeles no se lee ninguna palabra, as&iacute; que la foto es solo la marca. Las dos
        versiones est&aacute;n en 1080 &times; 1080; Instagram las recorta en c&iacute;rculo.
      </p>
    </div>

    <div class="avatars">
      <article class="av av--pick">
        <span class="tag">Recomendada</span>
        <img src="{AVATAR_DARK}" width="200" height="200" alt="Foto de perfil sobre fondo oscuro">
        <p>Sobre tinta de mar. Destaca en el feed claro de Instagram y es la que combina con la cuadr&iacute;cula.</p>
        <div class="sizes">
          <figure><img src="{AVATAR_SMALL}" width="88" height="88" alt=""><figcaption>88 px</figcaption></figure>
          <figure><img src="{AVATAR_SMALL}" width="56" height="56" alt=""><figcaption>56 px</figcaption></figure>
          <figure><img src="{AVATAR_SMALL}" width="32" height="32" alt=""><figcaption>32 px</figcaption></figure>
        </div>
        <span class="path">social/dist/perfil/avatar-oscuro.png</span>
      </article>

      <article class="av">
        <span class="tag">Alternativa</span>
        <img src="{AVATAR_PAPER}" width="200" height="200" alt="Foto de perfil sobre fondo claro">
        <p>Sobre papel. &Uacute;sala si alg&uacute;n d&iacute;a el feed se vuelve mayoritariamente oscuro, o para el perfil de WhatsApp Business.</p>
        <span class="path">social/dist/perfil/avatar-papel.png</span>
      </article>
    </div>
  </section>

  <!-- 02 campos -->
  <section>
    <div class="sec-head">
      <span class="num">02 &middot; Los campos</span>
      <h2>Qu&eacute; va en cada <em>casilla</em></h2>
      <p>El campo &ldquo;Nombre&rdquo; es el que busca la gente; el usuario, el que se comparte. No son lo mismo.</p>
    </div>

    <div class="tablewrap">
      <table>
        <thead><tr><th>Campo</th><th>Qu&eacute; poner</th><th>Por qu&eacute;</th></tr></thead>
        <tbody>
{chr(10).join(campo_row(n, v, nota, i) for i, (n, v, nota) in enumerate(CAMPOS))}
        </tbody>
      </table>
    </div>
  </section>

  <!-- 03 bio -->
  <section>
    <div class="sec-head">
      <span class="num">03 &middot; Biograf&iacute;a</span>
      <h2>Tres bios, <em>150 caracteres</em> como techo</h2>
      <p>
        Las tres dicen lo mismo en distinto orden: qu&eacute; haces, para qui&eacute;n, la pega que quitas
        (permanencia) y la acci&oacute;n. El contador incluye los saltos de l&iacute;nea.
      </p>
    </div>
    <div class="bios">
{chr(10).join(bio_block(i, t, b) for i, (t, b) in enumerate(BIOS))}
    </div>
    <p class="note" style="margin-top:22px">
      <b>El emoji cuenta.</b> Instagram no siempre cuenta los emojis como un solo car&aacute;cter, as&iacute;
      que si te avisa de que te pasas, quita el \U0001F305 y listo. Y las may&uacute;sculas de m&aacute;s
      (&ldquo;WEBS QUE VENDEN&rdquo;) no ayudan: en una bio corta restan.
    </p>
  </section>

  <!-- 04 destacados -->
  <section>
    <div class="sec-head">
      <span class="num">04 &middot; Destacados</span>
      <h2>Cuatro portadas que hacen de <em>men&uacute;</em></h2>
      <p>
        Son lo primero que mira quien llega desde un anuncio. Se suben como story (1080 &times; 1920),
        se guardan en el destacado y despu&eacute;s se a&ntilde;ade el contenido de verdad.
      </p>
    </div>
    <div class="covers">
{chr(10).join(cover_card(n, s, nota) for n, s, nota in COVERS)}
    </div>
  </section>

  <!-- 05 primeras publicaciones -->
  <section>
    <div class="sec-head">
      <span class="num">05 &middot; Primera pantalla</span>
      <h2>Las nueve primeras, <em>en este orden</em></h2>
      <p>
        Publ&iacute;calas antes de dar difusi&oacute;n a la cuenta: un perfil con tres publicaciones no
        convierte. Despu&eacute;s, tres por semana &mdash; martes, jueves y s&aacute;bado.
      </p>
    </div>
    <div class="firsts">
{chr(10).join(primero_card(i + 1, s, t, n) for i, (s, t, n) in enumerate(PRIMEROS))}
    </div>
  </section>

  <!-- 06 ajustes -->
  <section>
    <div class="sec-head">
      <span class="num">06 &middot; Para ir tachando</span>
      <h2>Montaje de la cuenta</h2>
      <p>Se guarda en este navegador: puedes cerrar la p&aacute;gina y seguir donde lo dejaste.</p>
    </div>
    <div class="checks" id="checks">
{chr(10).join(ajuste_row(k, t, n) for k, t, n in AJUSTES)}
    </div>
    <p class="checks-foot" id="progreso">0 de {len(AJUSTES)} hechos</p>

    <p class="note" style="margin-top:26px">
      <b>Dos avisos.</b> El tel&eacute;fono, el correo, el dominio y el usuario que aparecen aqu&iacute; son
      marcadores: c&aacute;mbialos por los de verdad antes de publicar nada. Y hasta que la marca est&eacute;
      concedida, en el perfil y en la web se usa <b>&trade;</b>, nunca &reg;.
    </p>
  </section>

  <footer>
    <span>De la Isla &middot; kit de apertura de cuenta</span>
    <span>Im&aacute;genes en social/dist/perfil/ y social/dist/feed/</span>
  </footer>
</div>

<script>
  // ---------- contador de caracteres de las bios ----------
  document.querySelectorAll('[data-count]').forEach((el) => {{
    const texto = document.getElementById('bio-' + el.dataset.count).textContent;
    const n = [...texto].length;
    el.textContent = n + ' / 150';
    if (n > 150) el.style.color = '#E08A6A';
  }});

  // ---------- copiar al portapapeles ----------
  document.querySelectorAll('.copy').forEach((btn) => {{
    btn.addEventListener('click', async () => {{
      const nodo = document.getElementById(btn.dataset.copy);
      const texto = nodo.textContent;
      const ok = () => {{
        const previo = btn.textContent;
        btn.textContent = 'Copiado';
        btn.classList.add('done');
        setTimeout(() => {{ btn.textContent = previo; btn.classList.remove('done'); }}, 1600);
      }};
      try {{
        await navigator.clipboard.writeText(texto);
        ok();
      }} catch {{
        // Sin permiso de portapapeles: dejamos el texto seleccionado para copiar a mano.
        const rango = document.createRange();
        rango.selectNodeContents(nodo);
        const sel = window.getSelection();
        sel.removeAllRanges();
        sel.addRange(rango);
        btn.textContent = 'Selecciona y copia';
        setTimeout(() => {{ btn.textContent = 'Copiar'; }}, 2400);
      }}
    }});
  }});

  // ---------- checklist con memoria local ----------
  const KEY = 'delaisla-cuenta-checklist';
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
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, 'w') as fh:
    fh.write(ascii_html)
print('dist/cuenta.html', os.path.getsize(OUT) // 1024, 'KB')
