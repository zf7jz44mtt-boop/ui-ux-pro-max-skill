/* ==========================================================================
   stagger.js — a web port of `flutter_staggered_animations` (v1.1.1)

   The Dart package composes AnimationConfiguration + SlideAnimation +
   FadeInAnimation to animate a list or grid of children in sequence. This
   module keeps its semantics on the web:

     duration          225ms                          (AnimationConfiguration)
     delay             duration ~/ 6  = 37ms          (AnimationConfigurator)
     list delay        position * delay
     grid delay        (position ~/ columnCount + position % columnCount) * delay
     curve             Curves.ease -> cubic-bezier(.25,.1,.25,1)
     slide offset      50px vertical when nothing else is given (SlideAnimation)

   Markup:
     <div data-stagger="grid" data-columns="3">…children…</div>
     Optional: data-duration, data-delay, data-offset-y, data-offset-x,
               data-scale, data-once="false"
   ========================================================================== */

export const STAGGER_DEFAULTS = Object.freeze({
  duration: 225,        // AnimationConfiguration.duration
  columnCount: 1,       // AnimationConfiguration.staggeredGrid
  verticalOffset: 50,   // SlideAnimation.verticalOffset
  horizontalOffset: 0,
  scale: 1,             // ScaleAnimation.scale (1 = disabled)
});

/**
 * Port of AnimationConfigurator.stagger().
 * @param {number} position  index of the child
 * @param {number} duration  ms
 * @param {number|null} delay  ms between two children, defaults to duration/6
 * @param {number} columnCount  1 for lists, >1 for grids
 * @returns {number} delay in ms for this child
 */
export function staggerDelay(position, duration, delay, columnCount = 1){
  const step = delay == null ? Math.floor(duration / 6) : delay;
  if (columnCount > 1){
    // Dart's `~/` is a truncating integer division.
    return (Math.trunc(position / columnCount) + (position % columnCount)) * step;
  }
  return position * step;
}

function readConfig(el){
  const num = (name, fallback) => {
    const raw = el.dataset[name];
    const parsed = raw == null ? NaN : Number(raw);
    return Number.isFinite(parsed) ? parsed : fallback;
  };
  const mode = (el.dataset.stagger || 'list').toLowerCase();
  return {
    duration: num('duration', STAGGER_DEFAULTS.duration),
    delay: el.dataset.delay == null ? null : num('delay', null),
    columnCount: mode === 'grid' ? num('columns', 3) : STAGGER_DEFAULTS.columnCount,
    verticalOffset: num('offsetY', STAGGER_DEFAULTS.verticalOffset),
    horizontalOffset: num('offsetX', STAGGER_DEFAULTS.horizontalOffset),
    scale: num('scale', STAGGER_DEFAULTS.scale),
    once: el.dataset.once !== 'false',
  };
}

/** Arms one container: children start hidden and carry their own delay. */
export function armStagger(container){
  const cfg = readConfig(container);
  const children = Array.from(container.children);

  children.forEach((child, position) => {
    child.classList.add('isla-reveal');
    child.style.setProperty('--isla-dur', `${cfg.duration}ms`);
    child.style.setProperty('--isla-delay', `${staggerDelay(position, cfg.duration, cfg.delay, cfg.columnCount)}ms`);
    child.style.setProperty('--isla-y', `${cfg.verticalOffset}px`);
    child.style.setProperty('--isla-x', `${cfg.horizontalOffset}px`);
    child.style.setProperty('--isla-scale', String(cfg.scale));
  });

  return { children, once: cfg.once };
}

/** Plays the sequence (AnimationExecutor.forward equivalent). */
export function playStagger(children){
  // Two frames: the first commits the armed state, the second starts the run.
  requestAnimationFrame(() => requestAnimationFrame(() => {
    children.forEach((child) => child.classList.add('is-in'));
  }));
}

/**
 * Wires every [data-stagger] container in `root` to the viewport.
 * Honours prefers-reduced-motion by revealing everything immediately.
 */
export function initStagger(root = document){
  const containers = Array.from(root.querySelectorAll('[data-stagger]'));
  if (!containers.length) return;

  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  if (reduced || !('IntersectionObserver' in window)){
    containers.forEach((c) => Array.from(c.children).forEach((child) => {
      child.classList.add('isla-reveal', 'is-in');
      child.style.setProperty('--isla-delay', '0ms');
    }));
    return;
  }

  const armed = new WeakMap();
  const observer = new IntersectionObserver((entries) => {
    for (const entry of entries){
      if (!entry.isIntersecting) continue;
      const state = armed.get(entry.target);
      if (!state) continue;
      playStagger(state.children);
      if (state.once) observer.unobserve(entry.target);
    }
  }, { threshold: 0.12, rootMargin: '0px 0px -8% 0px' });

  containers.forEach((container) => {
    armed.set(container, armStagger(container));
    observer.observe(container);
  });
}
