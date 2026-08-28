#!/usr/bin/env python3
"""Monta dist/profile.html: la maqueta del perfil de Instagram con las piezas
de dist/feed/ incrustadas (base64), para poder enseñarla sin servidor.

    node export.mjs --feed && python3 build-profile.py
"""
import base64, io, json, os, re
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
FEED = os.path.join(HERE, 'dist', 'feed')
OUT = os.path.join(HERE, 'dist', 'profile.html')

# slug -> (tipo, título, pie para el visor)
POSTS = [
    ('01-web-que-trae-clientes', 'Carrusel', 'Una web que trae clientes',
     'Portada del carrusel de cinco piezas. El post ancla del perfil: explica el servicio de un vistazo.'),
    ('02-ficha-google', 'Consejo', 'Tu ficha de Google es tu escaparate',
     'Consejo suelto, sin venta. Da valor y educa al cliente antes de pedirle nada.'),
    ('03-bon-dia', 'Marca', 'Bon dia des de Mallorca',
     'Respiro visual: la escena 3D de la web, sin argumentario. Da aire a la cuadrícula.'),
    ('04-cliente-que-vuelve', 'Frase', 'El cliente que ya vino es el más barato',
     'Pieza en oro. Una cada seis publicaciones: rompe el ritmo y se comparte sola.'),
    ('05-tres-errores', 'Lista', 'Tres errores en tu ficha de Google',
     'Formato guardable. Este es el que suele traer seguidores nuevos.'),
    ('06-caso-soller', 'Caso', '+64 % reservas directas',
     'Prueba con número grande. Siempre con el contexto debajo, nunca el dato solo.'),
    ('07-desde-390', 'Precio', 'Desde 390 € al mes, sin permanencia',
     'Precio a la vista: filtra a quien no encaja y evita la conversación incómoda.'),
    ('08-antes-despues', 'Antes/después', 'La misma cocina, dos webs',
     'Captura real del comparador de la web. La prueba más directa que tenemos.'),
    ('09-fotos-reales', 'Consejo', 'Una foto de tu cocina vale más que diez de banco',
     'Consejo que además vende el servicio de contenido, sin decirlo.'),
    ('10-reel-carta', 'Reel', 'Cómo escribir la carta de tu web',
     'Portada de reel. Se diseña igual que el resto para que la cuadrícula no se rompa.'),
    ('11-diagnostico', 'Llamada', 'Diagnóstico gratuito en 24 h',
     'La oferta. Una cada nueve o diez publicaciones, no más.'),
    ('12-zona', 'Zona', 'De Palma a Alcúdia',
     'Señal local: dice a Google y al vecino de Manacor que trabajamos en su pueblo.'),
]


REEL_BADGE = ('<span class="cell__badge" aria-hidden="true">'
               '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg></span>')
CAROUSEL_BADGE = ('<span class="cell__badge" aria-hidden="true">'
                  '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">'
                  '<rect x="8" y="3" width="13" height="13" rx="2"/><path d="M16 20H5a1 1 0 0 1-1-1V8"/></svg></span>')


def uri(slug: str, width: int, quality: int = 82) -> str:
    im = Image.open(os.path.join(FEED, f'{slug}-1080x1080.png')).convert('RGB')
    im = im.resize((width, width), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, format='JPEG', quality=quality, optimize=True, progressive=True)
    return 'data:image/jpeg;base64,' + base64.b64encode(buf.getvalue()).decode()


def inline_fonts() -> str:
    css = open(os.path.join(HERE, 'assets', 'fonts.css')).read()

    def sub(m):
        path = os.path.join(HERE, 'assets', m.group(1))
        return "url('data:font/woff2;base64,%s')" % base64.b64encode(open(path, 'rb').read()).decode()

    return re.sub(r"url\('([^']+)'\)", sub, css)


thumbs = {slug: uri(slug, 330, 78) for slug, *_ in POSTS}
larges = {slug: uri(slug, 760, 84) for slug, *_ in POSTS}

grid_cells = '\n'.join(
    f'''        <button class="cell" data-post="{i}" aria-label="Ver publicación: {title}">
          <img src="{thumbs[slug]}" alt="{title}">
          {REEL_BADGE if kind == 'Reel' else ''}
          {CAROUSEL_BADGE if kind == 'Carrusel' else ''}
        </button>'''
    for i, (slug, kind, title, _) in enumerate(POSTS)
)

plan_rows = '\n'.join(
    f'''        <article class="plan">
          <img src="{thumbs[slug]}" alt="">
          <div>
            <span class="plan__kind">{kind}</span>
            <h3>{title}</h3>
            <p>{note}</p>
          </div>
        </article>'''
    for slug, kind, title, note in POSTS
)

posts_json = json.dumps([
    {'src': larges[slug], 'kind': kind, 'title': title, 'note': note}
    for slug, kind, title, note in POSTS
], ensure_ascii=True)   # \uXXXX: el bloque <script> no decodifica entidades HTML

MARK = ('<svg viewBox="0 0 40 40" aria-hidden="true">'
        '<circle cx="20" cy="16" r="7" fill="#D8A657"/>'
        '<path d="M6 26q7-5 14 0t14 0" fill="none" stroke="#2F8A87" stroke-width="2.4" stroke-linecap="round"/>'
        '<path d="M6 31q7-5 14 0t14 0" fill="none" stroke="rgba(47,138,135,.5)" stroke-width="1.8" stroke-linecap="round"/>'
        '</svg>')

ICON = {
    'star': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M12 3.6 14.4 9l5.9.8-4.3 4.1 1 5.9-5-2.8-5 2.8 1-5.9L3.7 9.8 9.6 9z"/></svg>',
    'swap': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M4 9h13l-3.4-3.4M20 15H7l3.4 3.4"/></svg>',
    'tag': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M16.5 8.5H9.8a3.2 3.2 0 0 0 0 6.4h5.9M7.5 10.6h8M7.5 13.4h8"/></svg>',
    'sun': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="11" r="4"/><path d="M3 19h18M12 3v2M5 7 6.4 8.4M19 7l-1.4 1.4"/></svg>',
    'grid': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><rect x="3" y="3" width="18" height="18" rx="1.5"/><path d="M9 3v18M15 3v18M3 9h18M3 15h18"/></svg>',
    'reels': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><rect x="3" y="3" width="18" height="18" rx="4"/><path d="m10 9 5 3-5 3z"/><path d="m7.5 3 3.2 5M14 3l3.2 5M3 8h18"/></svg>',
    'tagged': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><rect x="3" y="3" width="18" height="18" rx="3"/><circle cx="12" cy="10" r="2.8"/><path d="M7 18.5a5.2 5.2 0 0 1 10 0"/></svg>',
    'home': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M4 10.5 12 4l8 6.5V20a1 1 0 0 1-1 1h-4v-6H9v6H5a1 1 0 0 1-1-1z"/></svg>',
    'search': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="11" cy="11" r="7"/><path d="m16.5 16.5 4 4"/></svg>',
    'plus': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><rect x="3" y="3" width="18" height="18" rx="4"/><path d="M12 8v8M8 12h8"/></svg>',
    'heart': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M12 20s-7-4.6-7-9.4A3.9 3.9 0 0 1 12 8a3.9 3.9 0 0 1 7 2.6C19 15.4 12 20 12 20z"/></svg>',
    'menu': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M4 6h16M4 12h16M4 18h16"/></svg>',
    'add': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M12 5v14M5 12h14"/></svg>',
}

HIGHLIGHTS = [('Casos', ICON['star']), ('Antes/después', ICON['swap']),
              ('Precios', ICON['tag']), ('La isla', ICON['sun'])]
highlights = '\n'.join(
    f'''          <div class="hl"><span class="hl__ring">{icon}</span><small>{name}</small></div>'''
    for name, icon in HIGHLIGHTS
)

html = f'''<title>El perfil de De la Isla</title>
<style>
{inline_fonts()}
:root{{
  --sea-900:#07191F; --sea-850:#09202A; --sea-800:#0B242D; --sea-700:#10333E;
  --gold:#D8A657; --gold-soft:#E8C68B; --terracotta:#C4643C; --teal:#2F8A87;
  --sand:#F3EADA; --sand-dim:rgba(243,234,218,.72); --sand-faint:rgba(243,234,218,.46);
  --line:rgba(243,234,218,.14);
  --display:'Playfair Display',Georgia,serif;
  --body:'Inter',system-ui,-apple-system,sans-serif;
  --mono:'JetBrains Mono',ui-monospace,monospace;
}}
*,*::before,*::after{{ box-sizing:border-box; }}
body{{
  margin:0; background:var(--sea-900); color:var(--sand);
  font-family:var(--body); font-size:16px; line-height:1.6;
  padding:60px 22px 90px;
}}
.wrap{{ width:min(100%, 1240px); margin-inline:auto; }}
.eyebrow{{
  font-family:var(--mono); font-size:12px; letter-spacing:.2em; text-transform:uppercase;
  color:var(--gold); display:flex; align-items:center; gap:14px; margin:0 0 20px;
}}
.eyebrow::before{{ content:""; width:32px; height:2px; background:var(--gold); }}
h1{{
  font-family:var(--display); font-weight:500; margin:0;
  font-size:clamp(36px,5.4vw,62px); line-height:1.04; letter-spacing:-.02em;
}}
h1 em{{ font-style:italic; color:var(--gold); }}
.lead{{ color:var(--sand-dim); max-width:64ch; margin:20px 0 0; font-size:17px; }}

.split{{ display:grid; grid-template-columns:minmax(0,420px) minmax(0,1fr); gap:56px; margin-top:64px; align-items:start; }}
@media (max-width:940px){{ .split{{ grid-template-columns:1fr; gap:44px; }} }}

/* ---------- teléfono ---------- */
.phone{{
  border:12px solid #16303B; border-radius:46px; overflow:hidden;
  background:#000; box-shadow:0 60px 120px -50px rgba(0,0,0,.95), 0 0 0 2px rgba(216,166,87,.22);
  position:sticky; top:36px;
}}
@media (max-width:940px){{ .phone{{ position:static; max-width:420px; margin-inline:auto; }} }}
.ig{{ background:#000; color:#fff; font-size:13px; }}
.ig__status{{
  display:flex; justify-content:space-between; padding:12px 22px 6px;
  font-family:var(--mono); font-size:11px; color:#fff;
}}
.ig__top{{ display:flex; align-items:center; gap:10px; padding:8px 16px 14px; }}
.ig__handle{{ font-weight:600; font-size:16px; }}
.ig__top .sp{{ flex:1; }}
.ig__top svg{{ width:20px; height:20px; stroke:#fff; }}
.ig__head{{ display:flex; align-items:center; gap:22px; padding:0 16px; }}
.avatar{{
  width:84px; height:84px; border-radius:50%; flex:none; display:grid; place-items:center;
  background:var(--sea-800); border:2px solid rgba(216,166,87,.5);
}}
.avatar svg{{ width:52px; height:52px; }}
.stats{{ display:flex; flex:1; justify-content:space-around; text-align:center; }}
.stats b{{ display:block; font-size:16px; }}
.stats span{{ font-size:12px; color:#bdbdbd; }}
.ig__bio{{ padding:14px 16px 0; }}
.ig__bio b{{ font-size:14px; }}
.ig__bio .cat{{ color:#bdbdbd; font-size:12.5px; }}
.ig__bio p{{ margin:6px 0 0; font-size:13px; line-height:1.5; color:#e8e8e8; }}
.ig__bio a{{ color:var(--gold-soft); text-decoration:none; font-size:13px; }}
.ig__buttons{{ display:flex; gap:8px; padding:14px 16px 0; }}
.ig__buttons span{{
  flex:1; text-align:center; padding:8px; border-radius:9px; font-size:13px; font-weight:600;
  background:#262626;
}}
.ig__buttons span.primary{{ background:var(--gold); color:#20160A; }}
.hls{{ display:flex; gap:16px; padding:18px 16px 6px; overflow:hidden; }}
.hl{{ text-align:center; width:66px; }}
.hl__ring{{
  width:60px; height:60px; border-radius:50%; display:grid; place-items:center;
  border:1.5px solid rgba(243,234,218,.35); background:var(--sea-800); color:var(--gold);
}}
.hl__ring svg{{ width:26px; height:26px; }}
.hl small{{ display:block; margin-top:6px; font-size:10.5px; color:#d6d6d6; }}
.ig__tabs{{ display:flex; border-top:1px solid #262626; margin-top:14px; }}
.ig__tabs span{{ flex:1; display:grid; place-items:center; padding:11px 0; color:#7a7a7a; }}
.ig__tabs svg{{ width:19px; height:19px; }}
.ig__tabs span.on{{ color:#fff; box-shadow:inset 0 2px 0 #fff; }}
.ig__grid{{ display:grid; grid-template-columns:repeat(3,1fr); gap:2px; }}
.cell{{ position:relative; padding:0; border:0; background:none; cursor:pointer; display:block; }}
.cell img{{ width:100%; display:block; aspect-ratio:1; object-fit:cover; }}
.cell__badge{{ position:absolute; top:6px; right:7px; color:#fff; filter:drop-shadow(0 1px 3px rgba(0,0,0,.7)); }}
.cell__badge svg{{ width:15px; height:15px; display:block; }}
.cell:focus-visible{{ outline:2px solid var(--gold); outline-offset:-2px; }}
.ig__nav{{ display:flex; justify-content:space-around; align-items:center; padding:12px 0 16px; border-top:1px solid #262626; color:#fff; }}
.ig__nav svg{{ width:22px; height:22px; }}
.ig__nav .me{{ width:24px; height:24px; border-radius:50%; border:1.5px solid var(--gold); display:grid; place-items:center; }}
.ig__nav .me svg{{ width:16px; height:16px; }}

/* ---------- notas ---------- */
.notes h2{{ font-family:var(--display); font-weight:500; font-size:30px; margin:0 0 14px; letter-spacing:-.01em; }}
.notes h2 + p{{ color:var(--sand-dim); margin:0 0 26px; }}
.block{{ border-top:1px solid var(--line); padding:26px 0; }}
.block:first-of-type{{ border-top:0; padding-top:0; }}
.block h3{{
  font-family:var(--mono); font-size:11.5px; letter-spacing:.18em; text-transform:uppercase;
  color:var(--gold); margin:0 0 14px; font-weight:400;
}}
.block p{{ margin:0 0 12px; color:var(--sand-dim); font-size:15.5px; }}
.swatches{{ display:flex; flex-wrap:wrap; gap:12px; margin-top:6px; }}
.sw{{ display:flex; align-items:center; gap:10px; font-family:var(--mono); font-size:11.5px; color:var(--sand-faint); }}
.sw i{{ width:30px; height:30px; border-radius:8px; display:block; border:1px solid rgba(243,234,218,.3); }}
.rhythm{{ display:grid; grid-template-columns:repeat(3,44px); gap:6px; margin-top:6px; }}
.rhythm i{{ height:44px; border-radius:6px; display:block; border:1px solid rgba(243,234,218,.22); }}
.rule{{ display:grid; grid-template-columns:auto 1fr; gap:12px 16px; align-items:baseline; }}
.rule b{{ font-family:var(--display); font-size:26px; color:var(--gold); font-weight:500; }}
.rule span{{ color:var(--sand-dim); font-size:15px; }}

/* ---------- plan de contenidos ---------- */
.plangrid{{ margin-top:80px; }}
.plangrid > h2{{ font-family:var(--display); font-weight:500; font-size:34px; margin:0 0 8px; }}
.plangrid > p{{ color:var(--sand-dim); margin:0 0 34px; max-width:60ch; }}
.plans{{ display:grid; grid-template-columns:repeat(auto-fit,minmax(300px,1fr)); gap:26px; }}
.plan{{ display:grid; grid-template-columns:104px 1fr; gap:18px; align-items:start; }}
.plan img{{ width:104px; height:104px; border-radius:10px; border:1px solid var(--line); display:block; }}
.plan__kind{{
  font-family:var(--mono); font-size:10.5px; letter-spacing:.16em; text-transform:uppercase; color:var(--gold);
}}
.plan h3{{ font-family:var(--display); font-weight:500; font-size:20px; margin:4px 0 6px; line-height:1.2; }}
.plan p{{ margin:0; font-size:14.5px; color:var(--sand-dim); }}

/* ---------- visor ---------- */
dialog{{
  border:0; padding:0; background:none; max-width:min(94vw,760px); width:100%;
  color:var(--sand);
}}
dialog::backdrop{{ background:rgba(4,12,16,.88); }}
.viewer{{ background:var(--sea-850); border:1px solid var(--line); border-radius:16px; overflow:hidden; }}
.viewer img{{ width:100%; display:block; }}
.viewer__body{{ padding:22px 24px 26px; }}
.viewer__kind{{ font-family:var(--mono); font-size:11px; letter-spacing:.16em; text-transform:uppercase; color:var(--gold); }}
.viewer h3{{ font-family:var(--display); font-weight:500; font-size:24px; margin:6px 0 8px; }}
.viewer p{{ margin:0; color:var(--sand-dim); font-size:15px; }}
.viewer__close{{
  margin-top:20px; background:var(--gold); color:#20160A; border:0; cursor:pointer;
  font-family:var(--mono); font-size:12px; letter-spacing:.14em; text-transform:uppercase;
  padding:12px 22px; border-radius:8px; font-weight:700;
}}
.foot{{
  margin-top:76px; border-top:1px solid var(--line); padding-top:22px;
  font-family:var(--mono); font-size:11.5px; letter-spacing:.12em; text-transform:uppercase;
  color:var(--sand-faint); display:flex; flex-wrap:wrap; gap:14px 28px; justify-content:space-between;
}}
@media (prefers-reduced-motion:reduce){{ *{{ animation:none !important; transition:none !important; }} }}
</style>

<div class="wrap">
  <p class="eyebrow">De la Isla · Instagram</p>
  <h1>Así se vería la cuenta<br>con la <em>estética de la web</em></h1>
  <p class="lead">
    Doce publicaciones reales generadas con los mismos tokens que el sitio: tinta de mar,
    latón y arena, Playfair Display para los titulares y JetBrains Mono para las etiquetas.
    Toca cualquier pieza de la cuadrícula para verla entera.
  </p>

  <div class="split">
    <div class="phone">
      <div class="ig">
        <div class="ig__status"><span>10:50</span><span>5G ▮▮▮</span></div>

        <div class="ig__top">
          <span class="ig__handle">delaisla.mallorca</span>
          <span class="sp"></span>
          {ICON['add']}
          {ICON['menu']}
        </div>

        <div class="ig__head">
          <span class="avatar">{MARK}</span>
          <div class="stats">
            <div><b>{len(POSTS)}</b><span>publicaciones</span></div>
            <div><b>1.284</b><span>seguidores</span></div>
            <div><b>312</b><span>seguidos</span></div>
          </div>
        </div>

        <div class="ig__bio">
          <b>De la Isla</b>
          <div class="cat">Agencia de marketing · Palma de Mallorca</div>
          <p>Webs y Google para negocios pequeños de la isla 🌅<br>
          Sin permanencia · Respuesta en 24 h<br>
          Català · Español · English · Deutsch</p>
          <a href="#">delaisla.example</a>
        </div>

        <div class="ig__buttons">
          <span class="primary">Seguir</span>
          <span>Mensaje</span>
          <span>Contacto</span>
        </div>

        <div class="hls">
{highlights}
        </div>

        <div class="ig__tabs">
          <span class="on">{ICON['grid']}</span><span>{ICON['reels']}</span><span>{ICON['tagged']}</span>
        </div>

        <div class="ig__grid">
{grid_cells}
        </div>

        <div class="ig__nav">
          <span>{ICON['home']}</span><span>{ICON['search']}</span><span>{ICON['plus']}</span>
          <span>{ICON['heart']}</span><span class="me">{MARK}</span>
        </div>
      </div>
    </div>

    <div class="notes">
      <h2>Por qué la cuadrícula se lee como una sola pieza</h2>
      <p>No es que todas las piezas sean iguales, sino que se turnan siguiendo tres reglas.</p>

      <div class="block">
        <h3>1 · Tres fondos que se alternan</h3>
        <p>
          Tinta de mar para lo que vende, papel para lo que enseña y latón para las frases
          y la oferta. Al alternarlos, ninguna fila queda plana y la marca se reconoce
          desde la miniatura, sin leer una palabra.
        </p>
        <div class="rhythm">
          <i style="background:#07191F"></i><i style="background:#FBF7EF"></i><i style="background:#07191F"></i>
          <i style="background:linear-gradient(150deg,#E0AF61,#C88A3F)"></i><i style="background:#FBF7EF"></i><i style="background:#07191F"></i>
          <i style="background:#FBF7EF"></i><i style="background:#07191F"></i><i style="background:#FBF7EF"></i>
        </div>
      </div>

      <div class="block">
        <h3>2 · La misma tipografía que la web</h3>
        <p>
          Titular en Playfair Display con una palabra en cursiva dorada, cuerpo en Inter y
          etiquetas en JetBrains Mono con letra espaciada. Es la firma: cualquiera que llegue
          del perfil a la web reconoce el mismo sitio.
        </p>
        <div class="swatches">
          <span class="sw"><i style="background:#07191F"></i>#07191F</span>
          <span class="sw"><i style="background:#0B242D"></i>#0B242D</span>
          <span class="sw"><i style="background:#D8A657"></i>#D8A657</span>
          <span class="sw"><i style="background:#C4643C"></i>#C4643C</span>
          <span class="sw"><i style="background:#2F8A87"></i>#2F8A87</span>
          <span class="sw"><i style="background:#FBF7EF"></i>#FBF7EF</span>
        </div>
      </div>

      <div class="block">
        <h3>3 · Cinco tipos de publicación, en proporción</h3>
        <div class="rule">
          <b>4</b><span><b style="font-family:inherit;font-size:inherit;color:var(--sand)">Consejo o lista.</b> Enseñan algo aunque nadie contrate nada. Son los que se guardan.</span>
          <b>3</b><span><b style="font-family:inherit;font-size:inherit;color:var(--sand)">Prueba.</b> Casos, números y antes/después. Nunca un dato sin su contexto.</span>
          <b>2</b><span><b style="font-family:inherit;font-size:inherit;color:var(--sand)">Marca.</b> La isla, el sitio, el equipo. Dan aire entre pieza y pieza de venta.</span>
          <b>2</b><span><b style="font-family:inherit;font-size:inherit;color:var(--sand)">Servicio.</b> Qué hacemos y cuánto cuesta, con el precio a la vista.</span>
          <b>1</b><span><b style="font-family:inherit;font-size:inherit;color:var(--sand)">Oferta.</b> El diagnóstico gratuito. Una cada nueve o diez, no más.</span>
        </div>
      </div>

      <div class="block">
        <h3>Ritmo y destacados</h3>
        <p>
          Tres publicaciones por semana (martes, jueves y sábado) llenan la primera pantalla
          en un mes. Los cuatro destacados —Casos, Antes/después, Precios y La isla— hacen de
          menú: es lo primero que mira quien llega desde un anuncio.
        </p>
      </div>

      <div class="block">
        <h3>Qué hay que cambiar</h3>
        <p>
          El usuario <b>@delaisla.mallorca</b>, el enlace de la bio y las cifras de seguidores
          son de ejemplo, igual que los números de los casos. Todo lo demás está listo para
          publicar.
        </p>
      </div>
    </div>
  </div>

  <section class="plangrid">
    <h2>Las doce piezas, una a una</h2>
    <p>Cada una tiene un trabajo distinto. Este es el orden en el que llenarían el perfil.</p>
    <div class="plans">
{plan_rows}
    </div>
  </section>

  <div class="foot">
    <span>De la Isla · Agencia de marketing en Mallorca</span>
    <span>Piezas 1080 × 1080 · generadas desde social/feed.html</span>
  </div>
</div>

<dialog id="viewer">
  <div class="viewer">
    <img id="viewer-img" alt="">
    <div class="viewer__body">
      <span class="viewer__kind" id="viewer-kind"></span>
      <h3 id="viewer-title"></h3>
      <p id="viewer-note"></p>
      <button class="viewer__close" id="viewer-close">Cerrar</button>
    </div>
  </div>
</dialog>

<script>
  const POSTS = {posts_json};
  const dialog = document.getElementById('viewer');
  const img = document.getElementById('viewer-img');
  document.querySelectorAll('.cell').forEach((cell) => {{
    cell.addEventListener('click', () => {{
      const post = POSTS[Number(cell.dataset.post)];
      img.src = post.src;
      img.alt = post.title;
      document.getElementById('viewer-kind').textContent = post.kind;
      document.getElementById('viewer-title').textContent = post.title;
      document.getElementById('viewer-note').textContent = post.note;
      dialog.showModal();
    }});
  }});
  document.getElementById('viewer-close').addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', (e) => {{ if (e.target === dialog) dialog.close(); }});
</script>
'''

# Los acentos salen como entidades numericas para que la pagina se lea igual
# aunque se sirva sin charset declarado (CSS y JS ya son ASCII).
ascii_html = html.encode('ascii', 'xmlcharrefreplace').decode('ascii')

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, 'w') as fh:
    fh.write(ascii_html)
print('dist/profile.html', os.path.getsize(OUT) // 1024, 'KB')
