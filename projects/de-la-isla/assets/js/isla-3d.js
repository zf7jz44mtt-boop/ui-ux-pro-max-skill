/* ==========================================================================
   isla-3d.js — hero scene (three.js r186dev, vendored from the three.js repo)

   A slow Mediterranean dawn: a shader sea, a low-poly island with pines and a
   lighthouse, warm light motes and a sun sitting on the horizon.

   Follows the ui-ux-pro-max `threejs` stack guidelines:
   - segment budget per role (hero water 160², motes 6-sided points)
   - no shadow maps (nothing in frame gains from them) instead of blanket casts
   - mouse *and* touch parallax
   - render loop paused off-screen / on hidden tab, DPR clamped to 2
   ========================================================================== */

import * as THREE from './vendor/three.module.js';

const PALETTE = {
  deep:    0x06202B,
  shallow: 0x18606A,
  sun:     0xF0C173,
  sand:    0xC9B189,
  rock:    0x7A7259,
  pine:    0x3C5647,
  fog:     0x0B2731,
};

const WATER_VERT = /* glsl */`
  uniform float uTime;
  varying vec3 vWorld;
  varying vec3 vNormal;
  varying float vWave;

  // Sum of directional sines. The analytic derivative gives us a smooth normal,
  // which is what keeps the sun glitter from breaking into visible triangles.
  #define WAVE(DX, DY, FREQ, SPEED, AMP) { \
    vec2 d = normalize(vec2(DX, DY)); \
    float phase = dot(pos.xy, d) * FREQ + uTime * SPEED; \
    h += sin(phase) * AMP; \
    float c = cos(phase) * AMP * FREQ; \
    dhdx += c * d.x; \
    dhdy += c * d.y; \
  }

  void main(){
    vec3 pos = position;
    float h = 0.0;
    float dhdx = 0.0;
    float dhdy = 0.0;

    WAVE( 1.0,  0.35, 0.26, 0.85, 0.50)
    WAVE(-0.40, 1.00, 0.47, 1.20, 0.26)
    WAVE( 0.80,-0.60, 0.98, 1.70, 0.10)
    WAVE( 0.20, 0.90, 2.10, 2.35, 0.035)

    pos.z += h;
    vWave = h;

    vec3 localNormal = normalize(vec3(-dhdx, -dhdy, 1.0));
    vNormal = normalize(mat3(modelMatrix) * localNormal);

    vec4 world = modelMatrix * vec4(pos, 1.0);
    vWorld = world.xyz;
    gl_Position = projectionMatrix * viewMatrix * world;
  }
`;

const WATER_FRAG = /* glsl */`
  uniform vec3 uDeep;
  uniform vec3 uShallow;
  uniform vec3 uSunColor;
  uniform vec3 uSunDir;
  uniform vec3 uFog;
  varying vec3 vWorld;
  varying vec3 vNormal;
  varying float vWave;

  void main(){
    vec3 n = normalize(vNormal);
    vec3 viewDir = normalize(cameraPosition - vWorld);
    vec3 sunDir  = normalize(uSunDir);
    vec3 halfDir = normalize(sunDir + viewDir);

    float fresnel = pow(1.0 - clamp(dot(n, viewDir), 0.0, 1.0), 4.0);
    float spec    = pow(max(dot(n, halfDir), 0.0), 90.0);
    float sheen   = pow(max(dot(n, halfDir), 0.0), 18.0) * 0.10;
    float crest   = smoothstep(-0.55, 0.85, vWave);
    float haze    = smoothstep(34.0, 150.0, length(vWorld.xz));

    vec3 col = mix(uDeep, uShallow, crest * 0.45 + fresnel * 0.40);

    // Sun road: a glitter corridor under the sun, fading out with distance so
    // the far water does not alias into noise.
    float road = exp(-pow((vWorld.x - 5.5) * 0.045, 2.0));
    col += uSunColor * (spec * (0.35 + road * 1.15) + sheen * (0.4 + road)) * (1.0 - haze * 0.75);

    col = mix(col, uFog, haze);

    // Manual sRGB encode: this material opts out of three's colour-space chunk.
    gl_FragColor = vec4(pow(clamp(col, 0.0, 1.0), vec3(1.0 / 2.2)), 1.0);
  }
`;

/** Deterministic value noise — no dependency, stable island silhouette. */
function noise3(x, y, z){
  return (
    Math.sin(x * 1.7 + y * 0.9) * 0.5 +
    Math.sin(y * 2.3 - z * 1.1) * 0.3 +
    Math.sin(z * 3.1 + x * 1.3) * 0.2
  );
}

function buildIsland(){
  const group = new THREE.Group();

  // Landmass: hero silhouette, so it gets the higher detail level (icosa 3).
  const geo = new THREE.IcosahedronGeometry(3.1, 3);
  const pos = geo.attributes.position;
  const v = new THREE.Vector3();
  for (let i = 0; i < pos.count; i++){
    v.fromBufferAttribute(pos, i);
    const n = noise3(v.x * 0.55, v.y * 0.55, v.z * 0.55);
    v.multiplyScalar(1 + n * 0.12);
    // Flatten the underside into a shelf that sits just under the waterline.
    if (v.y < 0) v.y *= 0.28;
    v.y -= 0.5;
    pos.setXYZ(i, v.x, v.y, v.z);
  }
  geo.computeVertexNormals();

  const land = new THREE.Mesh(
    geo,
    new THREE.MeshStandardMaterial({
      color: PALETTE.rock, roughness: 0.95, metalness: 0.0, flatShading: true,
    })
  );
  group.add(land);

  // A sand collar where the rock meets the water.
  const collar = new THREE.Mesh(
    new THREE.CylinderGeometry(3.15, 3.45, 0.5, 26, 1, true),
    new THREE.MeshStandardMaterial({
      color: PALETTE.sand, roughness: 1, side: THREE.DoubleSide, flatShading: true,
    })
  );
  collar.position.y = -0.55;
  group.add(collar);

  // Pines — background detail, so 6-sided cones are plenty.
  const pineGeo = new THREE.ConeGeometry(0.34, 1.25, 6);
  const trunkGeo = new THREE.CylinderGeometry(0.06, 0.08, 0.4, 5);
  const pineMat = new THREE.MeshStandardMaterial({ color: PALETTE.pine, roughness: 0.9, flatShading: true });
  const trunkMat = new THREE.MeshStandardMaterial({ color: 0x4A3B2C, roughness: 1 });
  const spots = [
    [-1.5, 0.6], [-0.4, 1.4], [0.9, 0.9], [1.7, -0.3],
    [0.2, -1.3], [-1.2, -0.9], [1.1, 1.8],
  ];
  for (const [x, z] of spots){
    const r = Math.hypot(x, z);
    const y = 2.35 - r * 0.42 + noise3(x, 0, z) * 0.12;
    const scale = 0.85 + noise3(z, x, 1) * 0.18;

    const trunk = new THREE.Mesh(trunkGeo, trunkMat);
    trunk.position.set(x, y, z);
    trunk.scale.setScalar(scale);
    group.add(trunk);

    const pine = new THREE.Mesh(pineGeo, pineMat);
    pine.position.set(x, y + 0.72 * scale, z);
    pine.scale.setScalar(scale);
    group.add(pine);
  }

  // Lighthouse: the one warm focal point in the scene.
  const tower = new THREE.Mesh(
    new THREE.CylinderGeometry(0.16, 0.24, 1.5, 12),
    new THREE.MeshStandardMaterial({ color: 0xE7DDC7, roughness: 0.8 })
  );
  tower.position.set(-0.2, 3.05, -0.6);
  group.add(tower);

  const lamp = new THREE.Mesh(
    new THREE.SphereGeometry(0.14, 12, 12),
    new THREE.MeshBasicMaterial({ color: PALETTE.sun })
  );
  lamp.position.set(-0.2, 3.9, -0.6);
  group.add(lamp);

  const lampLight = new THREE.PointLight(PALETTE.sun, 6, 14, 2);
  lampLight.position.copy(lamp.position);
  group.add(lampLight);

  group.userData.lamp = lamp;
  group.userData.lampLight = lampLight;
  return group;
}

function buildMotes(){
  const count = 220;
  const positions = new Float32Array(count * 3);
  const speeds = new Float32Array(count);
  for (let i = 0; i < count; i++){
    positions[i * 3 + 0] = (Math.random() - 0.5) * 60;
    positions[i * 3 + 1] = Math.random() * 16 - 1;
    positions[i * 3 + 2] = (Math.random() - 0.5) * 46 - 6;
    speeds[i] = 0.12 + Math.random() * 0.3;
  }
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.BufferAttribute(positions, 3));

  // 6-sided radial sprite drawn once into a canvas — no network request.
  const c = document.createElement('canvas');
  c.width = c.height = 64;
  const ctx = c.getContext('2d');
  const grd = ctx.createRadialGradient(32, 32, 0, 32, 32, 32);
  grd.addColorStop(0, 'rgba(255,236,201,1)');
  grd.addColorStop(0.35, 'rgba(240,193,115,.55)');
  grd.addColorStop(1, 'rgba(240,193,115,0)');
  ctx.fillStyle = grd;
  ctx.fillRect(0, 0, 64, 64);
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;

  const points = new THREE.Points(geo, new THREE.PointsMaterial({
    size: 0.26, map: tex, transparent: true, depthWrite: false,
    blending: THREE.AdditiveBlending, opacity: 0.55, fog: false,
  }));
  points.userData.speeds = speeds;
  return points;
}

function buildSky(sunPos){
  // A gradient dome costs one draw call and reads far better than a flat
  // background colour behind a horizon line.
  const geo = new THREE.SphereGeometry(200, 32, 16);
  const mat = new THREE.ShaderMaterial({
    side: THREE.BackSide,
    depthWrite: false,
    fog: false,
    uniforms: {
      uTop:    { value: new THREE.Color(0x05141B) },
      uBottom: { value: new THREE.Color(0x14414E) },
      uGlow:   { value: new THREE.Color(0xE0A867) },
      uSunPos: { value: sunPos.clone().normalize() },
    },
    vertexShader: /* glsl */`
      varying vec3 vDir;
      void main(){
        vDir = normalize(position);
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      }
    `,
    fragmentShader: /* glsl */`
      uniform vec3 uTop;
      uniform vec3 uBottom;
      uniform vec3 uGlow;
      uniform vec3 uSunPos;
      varying vec3 vDir;
      void main(){
        vec3 dir = normalize(vDir);
        float height = smoothstep(-0.05, 0.55, dir.y);
        vec3 col = mix(uBottom, uTop, height);
        float glow = pow(max(dot(dir, normalize(uSunPos)), 0.0), 14.0);
        col += uGlow * glow * 0.65;
        gl_FragColor = vec4(pow(clamp(col, 0.0, 1.0), vec3(1.0 / 2.2)), 1.0);
      }
    `,
  });
  return new THREE.Mesh(geo, mat);
}

function buildSun(position){
  const sun = new THREE.Mesh(
    new THREE.CircleGeometry(5.4, 48),
    new THREE.MeshBasicMaterial({ color: PALETTE.sun, transparent: true, opacity: 0.95, fog: false })
  );
  sun.position.copy(position);
  return sun;
}

/**
 * Boots the hero scene.
 * @param {HTMLCanvasElement} canvas
 * @returns {{dispose: () => void} | null} null when WebGL is unavailable —
 *          the caller keeps the CSS gradient fallback painted on the canvas.
 */
export function initIslaScene(canvas){
  let renderer;
  try {
    renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: false, powerPreference: 'high-performance' });
  } catch (err){
    console.warn('[de-la-isla] WebGL no disponible, se usa el degradado de respaldo.', err);
    return null;
  }

  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  const scene = new THREE.Scene();
  scene.fog = new THREE.Fog(PALETTE.fog, 46, 165);

  const camera = new THREE.PerspectiveCamera(42, 1, 0.1, 400);
  const camHome = new THREE.Vector3(0, 4.6, 15.5);
  camera.position.copy(camHome);
  camera.lookAt(0, 1.6, 0);

  const water = new THREE.Mesh(
    new THREE.PlaneGeometry(280, 280, 220, 220),
    new THREE.ShaderMaterial({
      vertexShader: WATER_VERT,
      fragmentShader: WATER_FRAG,
      fog: false,
      uniforms: {
        uTime:     { value: 0 },
        uDeep:     { value: new THREE.Color(PALETTE.deep) },
        uShallow:  { value: new THREE.Color(PALETTE.shallow) },
        uSunColor: { value: new THREE.Color(PALETTE.sun) },
        uSunDir:   { value: new THREE.Vector3(0.34, 0.26, -1).normalize() },
        uFog:      { value: new THREE.Color(PALETTE.fog) },
      },
    })
  );
  water.rotation.x = -Math.PI / 2;
  water.position.y = -0.4;
  scene.add(water);

  const island = buildIsland();
  island.position.set(5.0, -0.25, -7);
  scene.add(island);

  const motes = buildMotes();
  scene.add(motes);

  const sunPos = new THREE.Vector3(11, 2.2, -82);
  scene.add(buildSky(sunPos));
  scene.add(buildSun(sunPos));

  scene.add(new THREE.HemisphereLight(0x9FD3DE, 0x3A3020, 1.45));
  const key = new THREE.DirectionalLight(0xFFD9A0, 2.4);
  key.position.set(9, 7, -8);          // rim light from the sun
  scene.add(key);
  const fill = new THREE.DirectionalLight(0xBFD9DE, 1.35);
  fill.position.set(-7, 5, 9);         // keeps the face of the island readable
  scene.add(fill);

  /* ---- sizing ---------------------------------------------------------- */
  let lookAtX = 1.8;
  function resize(){
    const w = canvas.clientWidth || window.innerWidth;
    const h = canvas.clientHeight || window.innerHeight;
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    renderer.setSize(w, h, false);
    camera.aspect = w / h;
    // Pull the camera back on narrow screens so the island still reads.
    const narrow = w < 760;
    camera.fov = narrow ? 58 : 42;
    island.position.x = narrow ? 2.2 : 5.0;
    island.position.z = narrow ? -8.5 : -7;
    lookAtX = narrow ? 0.8 : 1.8;
    camera.updateProjectionMatrix();
  }
  resize();
  window.addEventListener('resize', resize, { passive: true });

  /* ---- pointer parallax (mouse + touch) -------------------------------- */
  const pointer = { x: 0, y: 0 };
  const target = { x: 0, y: 0 };

  function setPointer(clientX, clientY){
    const r = canvas.getBoundingClientRect();
    target.x = ((clientX - r.left) / r.width) * 2 - 1;
    target.y = -(((clientY - r.top) / r.height) * 2 - 1);
  }
  const onMouse = (e) => setPointer(e.clientX, e.clientY);
  const onTouch = (e) => { const t = e.touches[0]; if (t) setPointer(t.clientX, t.clientY); };

  if (!reduced.matches){
    window.addEventListener('mousemove', onMouse, { passive: true });
    canvas.addEventListener('touchmove', onTouch, { passive: true });
  }

  /* ---- loop ------------------------------------------------------------ */
  const timer = new THREE.Timer();
  let frame = 0;
  let visible = true;
  let running = false;

  function renderFrame(){
    timer.update();
    const t = timer.getElapsed();
    water.material.uniforms.uTime.value = t;

    pointer.x += (target.x - pointer.x) * 0.045;
    pointer.y += (target.y - pointer.y) * 0.045;

    // Scroll parallax: the camera lifts and drifts back as the hero leaves.
    const scrolled = Math.min(window.scrollY / Math.max(window.innerHeight, 1), 1);

    camera.position.x = camHome.x + pointer.x * 1.5;
    camera.position.y = camHome.y + pointer.y * 0.7 + scrolled * 2.6;
    camera.position.z = camHome.z + scrolled * 3.2;
    camera.lookAt(lookAtX, 1.4 - scrolled * 0.6, 0);

    island.rotation.y = Math.sin(t * 0.06) * 0.14 + 0.25;
    island.position.y = Math.sin(t * 0.35) * 0.06;

    const lamp = island.userData.lampLight;
    const pulse = 0.55 + 0.45 * Math.pow(Math.abs(Math.sin(t * 0.55)), 3);
    lamp.intensity = 3 + pulse * 7;
    island.userData.lamp.material.opacity = pulse;

    const p = motes.geometry.attributes.position;
    const speeds = motes.userData.speeds;
    for (let i = 0; i < speeds.length; i++){
      let y = p.getY(i) + speeds[i] * 0.012;
      if (y > 15) y = -1;
      p.setY(i, y);
    }
    p.needsUpdate = true;
    motes.rotation.y = t * 0.008;

    renderer.render(scene, camera);
  }

  function tick(){
    if (!running) return;
    frame = requestAnimationFrame(tick);
    renderFrame();
  }

  function start(){
    if (running || reduced.matches) return;
    running = true;
    timer.update();
    tick();
  }
  function stop(){
    running = false;
    cancelAnimationFrame(frame);
  }

  // Only render while the hero is on screen and the tab is in front.
  const io = new IntersectionObserver(([entry]) => {
    visible = entry.isIntersecting;
    if (visible && !document.hidden) start(); else stop();
  }, { threshold: 0.01 });
  io.observe(canvas);

  const onVisibility = () => {
    if (document.hidden) stop();
    else if (visible) start();
  };
  document.addEventListener('visibilitychange', onVisibility);

  const onMotionChange = () => { stop(); renderFrame(); if (!reduced.matches) start(); };
  reduced.addEventListener('change', onMotionChange);

  renderFrame();          // first paint, reduced-motion users stop here
  if (visible) start();

  return {
    dispose(){
      stop();
      io.disconnect();
      document.removeEventListener('visibilitychange', onVisibility);
      reduced.removeEventListener('change', onMotionChange);
      window.removeEventListener('resize', resize);
      window.removeEventListener('mousemove', onMouse);
      canvas.removeEventListener('touchmove', onTouch);
      scene.traverse((obj) => {
        if (obj.geometry) obj.geometry.dispose();
        const mat = obj.material;
        if (Array.isArray(mat)) mat.forEach((m) => m.dispose());
        else if (mat){ if (mat.map) mat.map.dispose(); mat.dispose(); }
      });
      renderer.dispose();
    },
  };
}
