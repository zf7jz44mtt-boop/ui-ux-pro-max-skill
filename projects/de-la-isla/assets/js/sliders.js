/* ==========================================================================
   sliders.js — the three interactive pieces of De la Isla

     initCoverflow()  3D cover-flow of case studies (drag, swipe, keys, dots)
     initCompare()    before / after wipe with a keyboard-operable handle
     initBudget()     budget range -> recommended plan
     initCounters()   count-up figures

   All of them are keyboard-operable and stop animating under
   prefers-reduced-motion.
   ========================================================================== */

const prefersReduced = () => window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const clamp = (n, min, max) => Math.min(max, Math.max(min, n));

/* --------------------------------------------------------------------------
   1. Cover-flow
   -------------------------------------------------------------------------- */
export function initCoverflow(root){
  if (!root) return null;
  const stage = root.querySelector('.coverflow__stage');
  const slides = Array.from(stage.querySelectorAll('.slide'));
  if (slides.length < 2) return null;

  const scope = root.closest('[data-coverflow-scope]') || root.parentElement;
  const prevBtn = scope.querySelector('[data-coverflow-prev]');
  const nextBtn = scope.querySelector('[data-coverflow-next]');
  const dotsWrap = scope.querySelector('[data-coverflow-dots]');
  const counter = scope.querySelector('[data-coverflow-counter]');
  const live = scope.querySelector('[data-coverflow-live]');

  const n = slides.length;
  let index = 0;
  let dragging = false;
  let startX = 0;
  let deltaX = 0;
  let autoplayId = 0;

  const dots = slides.map((slide, i) => {
    if (!dotsWrap) return null;
    const li = document.createElement('li');
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.setAttribute('aria-label', `Ir al caso ${i + 1}: ${slide.dataset.title || ''}`.trim());
    btn.addEventListener('click', () => { go(i); restartAutoplay(); });
    li.appendChild(btn);
    dotsWrap.appendChild(li);
    return btn;
  });

  /** Shortest signed distance from the active slide, so the ring wraps. */
  function offsetOf(i){
    let off = i - index;
    if (off > n / 2) off -= n;
    if (off < -n / 2) off += n;
    return off;
  }

  function layout(drag = 0){
    const width = root.clientWidth || 1;
    const nudge = (drag / width) * 1.15;
    // On phones this becomes a one-card slider: the neighbours are pushed
    // almost off-screen and dimmed, leaving an edge that invites the swipe.
    const narrow = width < 760;
    const spread = narrow ? 94 : 56;
    const cutoff = narrow ? 1.15 : 2.2;
    const tilt = narrow ? 12 : 26;

    slides.forEach((slide, i) => {
      const off = offsetOf(i) - nudge;
      const abs = Math.abs(off);
      const depth = -Math.min(abs, 3) * (narrow ? 120 : 190);
      const rotate = clamp(-off * tilt, -52, 52);
      const scale = Math.max(1 - abs * 0.09, 0.62);
      const opacity = abs > cutoff ? 0 : 1 - Math.min(abs, cutoff) * (narrow ? 0.8 : 0.3);

      slide.style.transform =
        `translateX(${off * spread}%) translateZ(${depth}px) rotateY(${rotate}deg) scale(${scale})`;
      slide.style.opacity = String(opacity);
      slide.style.zIndex = String(100 - Math.round(abs * 10));
      slide.style.pointerEvents = abs < 0.5 ? 'auto' : 'none';
      slide.classList.toggle('is-active', abs < 0.5);
      slide.setAttribute('aria-hidden', abs < 0.5 ? 'false' : 'true');
      slide.querySelectorAll('a, button').forEach((el) => {
        if (abs < 0.5) el.removeAttribute('tabindex');
        else el.setAttribute('tabindex', '-1');
      });
    });

    dots.forEach((dot, i) => dot && dot.setAttribute('aria-current', i === index ? 'true' : 'false'));
    if (counter) counter.textContent = `${String(index + 1).padStart(2, '0')} / ${String(n).padStart(2, '0')}`;
  }

  function go(next, announce = true){
    index = ((next % n) + n) % n;
    layout();
    if (announce && live) live.textContent = `Caso ${index + 1} de ${n}: ${slides[index].dataset.title || ''}`;
  }

  /* drag / swipe */
  function onPointerDown(e){
    if (e.button != null && e.button !== 0) return;
    dragging = true;
    startX = e.clientX;
    deltaX = 0;
    root.classList.add('is-dragging');
    root.setPointerCapture?.(e.pointerId);
    slides.forEach((s) => { s.style.transition = 'none'; });
    stopAutoplay();
  }
  function onPointerMove(e){
    if (!dragging) return;
    deltaX = e.clientX - startX;
    layout(deltaX);
  }
  function onPointerUp(){
    if (!dragging) return;
    dragging = false;
    root.classList.remove('is-dragging');
    slides.forEach((s) => { s.style.transition = ''; });
    const threshold = Math.min(120, root.clientWidth * 0.12);
    if (deltaX > threshold) go(index - 1);
    else if (deltaX < -threshold) go(index + 1);
    else layout();
    deltaX = 0;
    restartAutoplay();
  }

  root.addEventListener('pointerdown', onPointerDown);
  root.addEventListener('pointermove', onPointerMove);
  root.addEventListener('pointerup', onPointerUp);
  root.addEventListener('pointercancel', onPointerUp);
  root.addEventListener('pointerleave', onPointerUp);
  root.addEventListener('dragstart', (e) => e.preventDefault());

  root.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowLeft'){ e.preventDefault(); go(index - 1); restartAutoplay(); }
    if (e.key === 'ArrowRight'){ e.preventDefault(); go(index + 1); restartAutoplay(); }
    if (e.key === 'Home'){ e.preventDefault(); go(0); restartAutoplay(); }
    if (e.key === 'End'){ e.preventDefault(); go(n - 1); restartAutoplay(); }
  });

  prevBtn?.addEventListener('click', () => { go(index - 1); restartAutoplay(); });
  nextBtn?.addEventListener('click', () => { go(index + 1); restartAutoplay(); });

  /* autoplay — never for reduced-motion users, never off-screen */
  function startAutoplay(){
    if (prefersReduced() || autoplayId) return;
    autoplayId = window.setInterval(() => go(index + 1, false), 6500);
  }
  function stopAutoplay(){
    window.clearInterval(autoplayId);
    autoplayId = 0;
  }
  function restartAutoplay(){ stopAutoplay(); startAutoplay(); }

  root.addEventListener('mouseenter', stopAutoplay);
  root.addEventListener('mouseleave', startAutoplay);
  root.addEventListener('focusin', stopAutoplay);
  root.addEventListener('focusout', startAutoplay);
  document.addEventListener('visibilitychange', () => (document.hidden ? stopAutoplay() : startAutoplay()));

  const io = new IntersectionObserver(([entry]) => (entry.isIntersecting ? startAutoplay() : stopAutoplay()), { threshold: 0.25 });
  io.observe(root);

  window.addEventListener('resize', () => layout(), { passive: true });
  go(0, false);

  return { go, next: () => go(index + 1), prev: () => go(index - 1) };
}

/* --------------------------------------------------------------------------
   2. Before / after
   -------------------------------------------------------------------------- */
export function initCompare(root){
  if (!root) return null;
  const handle = root.querySelector('.compare__handle');
  let split = Number(root.dataset.start || 50);

  function paint(){
    root.style.setProperty('--split', `${split}%`);
    handle.setAttribute('aria-valuenow', String(Math.round(split)));
    handle.setAttribute('aria-valuetext', `${Math.round(split)}% del diseño nuevo visible`);
  }

  function setFromClientX(clientX){
    const r = root.getBoundingClientRect();
    split = clamp(((clientX - r.left) / r.width) * 100, 0, 100);
    paint();
  }

  let dragging = false;
  const down = (e) => {
    dragging = true;
    root.setPointerCapture?.(e.pointerId);
    setFromClientX(e.clientX);
  };
  const move = (e) => { if (dragging){ e.preventDefault(); setFromClientX(e.clientX); } };
  const up = () => { dragging = false; };

  root.addEventListener('pointerdown', down);
  root.addEventListener('pointermove', move);
  root.addEventListener('pointerup', up);
  root.addEventListener('pointercancel', up);
  root.addEventListener('pointerleave', up);

  handle.addEventListener('keydown', (e) => {
    const step = e.shiftKey ? 10 : 2;
    if (e.key === 'ArrowLeft'){ e.preventDefault(); split = clamp(split - step, 0, 100); paint(); }
    if (e.key === 'ArrowRight'){ e.preventDefault(); split = clamp(split + step, 0, 100); paint(); }
    if (e.key === 'Home'){ e.preventDefault(); split = 0; paint(); }
    if (e.key === 'End'){ e.preventDefault(); split = 100; paint(); }
  });

  paint();
  return { set: (v) => { split = clamp(v, 0, 100); paint(); } };
}

/* --------------------------------------------------------------------------
   3. Budget slider
   -------------------------------------------------------------------------- */
const PLANS = [
  {
    max: 449,
    name: 'Cala',
    summary: 'Presencia local cuidada: fichas, reseñas y una web que carga rápido.',
    includes: ['Google Business', 'SEO local', 'Web 1 página', 'Reseñas'],
    card: 'cala',
  },
  {
    max: 899,
    name: 'Tramuntana',
    summary: 'Crecimiento sostenido: contenido cada semana y campañas siempre activas.',
    includes: ['Todo Cala', 'Meta + Google Ads', 'Contenido 8/mes', 'Email', 'Informe mensual'],
    card: 'tramuntana',
  },
  {
    max: Infinity,
    name: 'Mediterráneo',
    summary: 'Marca y demanda a la vez, con producción propia en la isla y CRO continuo.',
    includes: ['Todo Tramuntana', 'Vídeo y foto', 'Landing + CRO', 'CRM', 'Sesión quincenal'],
    card: 'mediterraneo',
  },
];

export function initBudget(root){
  if (!root) return null;
  const input = root.querySelector('input[type="range"]');
  const amount = root.querySelector('[data-budget-amount]');
  const planName = root.querySelector('[data-budget-plan]');
  const planText = root.querySelector('[data-budget-summary]');
  const chips = root.querySelector('[data-budget-includes]');
  const hours = root.querySelector('[data-budget-hours]');
  const euro = new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 });

  function update(){
    const value = Number(input.value);
    const pct = ((value - input.min) / (input.max - input.min)) * 100;
    input.style.setProperty('--pct', `${pct}%`);

    const plan = PLANS.find((p) => value <= p.max);
    if (amount) amount.textContent = euro.format(value);
    if (planName) planName.textContent = plan.name;
    if (planText) planText.textContent = plan.summary;
    if (hours) hours.textContent = `${Math.round(value / 45)} h/mes de equipo`;
    if (chips){
      chips.replaceChildren(...plan.includes.map((label) => {
        const li = document.createElement('li');
        li.textContent = label;
        return li;
      }));
    }
    document.querySelectorAll('[data-plan]').forEach((card) => {
      card.classList.toggle('is-recommended', card.dataset.plan === plan.card);
      const badge = card.querySelector('.plan__badge');
      if (badge) badge.hidden = card.dataset.plan !== plan.card;
    });
  }

  input.addEventListener('input', update);
  update();
  return { update };
}

/* --------------------------------------------------------------------------
   4. Count-up figures
   -------------------------------------------------------------------------- */
export function initCounters(root = document){
  const nodes = Array.from(root.querySelectorAll('[data-count-to]'));
  if (!nodes.length) return;

  const format = new Intl.NumberFormat('es-ES');
  const run = (el) => {
    const to = Number(el.dataset.countTo);
    const decimals = Number(el.dataset.countDecimals || 0);
    if (prefersReduced()){
      el.textContent = format.format(to);
      return;
    }
    const duration = 1100;
    const start = performance.now();
    const step = (now) => {
      const t = clamp((now - start) / duration, 0, 1);
      const eased = 1 - Math.pow(1 - t, 3);
      const value = to * eased;
      el.textContent = decimals
        ? value.toFixed(decimals).replace('.', ',')
        : format.format(Math.round(value));
      if (t < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  };

  const io = new IntersectionObserver((entries) => {
    for (const entry of entries){
      if (!entry.isIntersecting) continue;
      run(entry.target);
      io.unobserve(entry.target);
    }
  }, { threshold: 0.6 });

  nodes.forEach((el) => { el.textContent = '0'; io.observe(el); });
}
