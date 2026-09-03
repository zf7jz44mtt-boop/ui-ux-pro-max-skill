/* ==========================================================================
   main.js — boots De la Isla
   ========================================================================== */

import { initIslaScene } from './isla-3d.js';
import { initStagger } from './stagger.js';

/* ---- header: stuck state + mobile nav ---------------------------------- */
function initHeader(){
  const header = document.querySelector('.site-header');
  const toggle = document.querySelector('.nav-toggle');
  const nav = document.getElementById('nav');

  const onScroll = () => header.classList.toggle('is-stuck', window.scrollY > 24);
  onScroll();
  window.addEventListener('scroll', onScroll, { passive: true });

  const setOpen = (open) => {
    nav.classList.toggle('is-open', open);
    toggle.setAttribute('aria-expanded', String(open));
    toggle.setAttribute('aria-label', open ? 'Cerrar menú' : 'Abrir menú');
    toggle.textContent = open ? '✕' : '☰';
    document.body.style.overflow = open ? 'hidden' : '';
  };

  toggle.addEventListener('click', () => setOpen(!nav.classList.contains('is-open')));
  nav.addEventListener('click', (e) => { if (e.target.closest('a')) setOpen(false); });
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && nav.classList.contains('is-open')){
      setOpen(false);
      toggle.focus();
    }
  });
  // Leaving the mobile breakpoint must not strand the overlay open.
  window.matchMedia('(min-width: 861px)').addEventListener('change', (e) => { if (e.matches) setOpen(false); });
}

/* ---- scroll spy --------------------------------------------------------- */
function initScrollSpy(){
  const links = Array.from(document.querySelectorAll('.nav a[href^="#"]'));
  const sections = links
    .map((link) => document.querySelector(link.getAttribute('href')))
    .filter(Boolean);
  if (!sections.length) return;

  const io = new IntersectionObserver((entries) => {
    for (const entry of entries){
      if (!entry.isIntersecting) continue;
      links.forEach((link) => link.setAttribute(
        'aria-current',
        link.getAttribute('href') === `#${entry.target.id}` ? 'true' : 'false'
      ));
    }
  }, { rootMargin: '-45% 0px -50% 0px' });

  sections.forEach((section) => io.observe(section));
}

/* ---- animate.css on scroll ---------------------------------------------- */
function initAnimateOnScroll(){
  const nodes = Array.from(document.querySelectorAll('[data-animate]'));
  if (!nodes.length) return;

  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  const io = new IntersectionObserver((entries) => {
    for (const entry of entries){
      if (!entry.isIntersecting) continue;
      const el = entry.target;
      el.style.animationDelay = `${el.dataset.animateDelay || 0}ms`;
      el.classList.add('animate__animated', `animate__${el.dataset.animate}`);
      io.unobserve(el);
    }
  }, { threshold: 0.2, rootMargin: '0px 0px -6% 0px' });

  nodes.forEach((el) => io.observe(el));
}

/* ---- contact form ------------------------------------------------------- */
function initForm(){
  const form = document.getElementById('contact-form');
  if (!form) return;
  const status = form.querySelector('.form-status');

  const rules = {
    nombre: (v) => (v.trim().length >= 2 ? '' : 'Dinos cómo te llamas.'),
    negocio: (v) => (v.trim().length >= 2 ? '' : 'Nombre del negocio, por favor.'),
    email: (v) => (/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v.trim()) ? '' : 'Revisa el correo: falta algo.'),
    mensaje: (v) => (v.trim().length >= 12 ? '' : 'Cuéntanos un poco más (12 caracteres mínimo).'),
  };

  function validateField(field){
    const rule = rules[field.name];
    if (!rule) return true;
    const message = rule(field.value);
    const wrap = field.closest('.field');
    wrap.classList.toggle('is-invalid', Boolean(message));
    wrap.querySelector('.error').textContent = message;
    field.setAttribute('aria-invalid', message ? 'true' : 'false');
    return !message;
  }

  form.querySelectorAll('input, textarea').forEach((field) => {
    field.addEventListener('blur', () => validateField(field));
    field.addEventListener('input', () => {
      if (field.closest('.field').classList.contains('is-invalid')) validateField(field);
    });
  });

  const consent = form.querySelector('#consentimiento');

  function validateConsent(){
    const wrap = consent.closest('.field');
    const ok = consent.checked;
    wrap.classList.toggle('is-invalid', !ok);
    wrap.querySelector('.error').textContent = ok ? '' : 'Necesitamos tu permiso para responderte.';
    return ok;
  }
  consent.addEventListener('change', () => {
    if (consent.closest('.field').classList.contains('is-invalid')) validateConsent();
  });

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const fields = Array.from(form.querySelectorAll('input[name], textarea[name]'))
      .filter((field) => rules[field.name]);
    const invalid = fields.filter((field) => !validateField(field));
    const consentOk = validateConsent();

    if (invalid.length || !consentOk){
      status.textContent = 'Faltan datos por revisar.';
      (invalid[0] || consent).focus();
      return;
    }

    const boton = form.querySelector('button[type="submit"]');
    boton.disabled = true;
    status.textContent = 'Enviando…';

    // Netlify recoge el formulario en la propia URL del sitio; enviarlo por
    // fetch evita el salto de página y deja el mensaje aquí mismo.
    try {
      const respuesta = await fetch('/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams(new FormData(form)).toString(),
      });
      if (!respuesta.ok) throw new Error(`El servidor respondió ${respuesta.status}`);
      status.innerHTML = 'Recibido. Te escribimos en menos de 24 h laborables.';
      form.reset();
    } catch (err){
      console.warn('[de-la-isla] el envío del formulario falló:', err);
      status.innerHTML = 'No hemos podido enviarlo. Escríbenos por ' +
        '<a href="https://wa.me/34622411144?text=Hola+quiero+el+diagnostico+gratis" target="_blank" rel="noopener">WhatsApp</a> ' +
        'y lo vemos igual.';
    } finally {
      boton.disabled = false;
    }
  });
}

/* ---- boot --------------------------------------------------------------- */
function boot(){
  document.documentElement.classList.add('js-motion');

  initHeader();
  initScrollSpy();
  initStagger();
  initAnimateOnScroll();
  initForm();

  const canvas = document.getElementById('isla-canvas');
  if (canvas) initIslaScene(canvas);

  const year = document.getElementById('year');
  if (year) year.textContent = String(new Date().getFullYear());
}

if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
else boot();
