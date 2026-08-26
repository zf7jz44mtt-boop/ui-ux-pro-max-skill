// ── Modal de consulta gratis → Discord webhook ──────────────────────
// 1. En Discord: Ajustes del canal → Integraciones → Webhooks → Nuevo webhook → Copiar URL
// 2. Pega esa URL abajo, reemplazando el texto entre comillas.
// ⚠️ No publiques la URL real del webhook en un repositorio público: cualquiera que
// vea el código fuente podría usarla para enviar mensajes falsos a tu canal de Discord.
// Sustitúyela por tu propia URL en el servidor de despliegue o pásala a través de una
// función serverless (Cloudflare Worker / Netlify Function) en lugar de dejarla en el cliente.
const DISCORD_WEBHOOK_URL = "PEGA_AQUI_TU_URL_DE_WEBHOOK_DE_DISCORD";

function openConsultModal(){
  document.getElementById('consultModal').classList.add('active');
}
function closeConsultModal(){
  document.getElementById('consultModal').classList.remove('active');
}

document.addEventListener('DOMContentLoaded', () => {
  const consultForm = document.getElementById('consultForm');
  const cfStatus = document.getElementById('cf-status');
  const cfSubmit = document.getElementById('cf-submit');
  const modal = document.getElementById('consultModal');

  if (!consultForm) return;

  consultForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    if (DISCORD_WEBHOOK_URL.includes("PEGA_AQUI")) {
      cfStatus.textContent = "Falta configurar la URL del webhook de Discord.";
      cfStatus.className = "modal-status err";
      return;
    }

    const name = document.getElementById('cf-name').value;
    const business = document.getElementById('cf-business').value;
    const email = document.getElementById('cf-email').value;
    const phone = document.getElementById('cf-phone').value || "No indicado";
    const message = document.getElementById('cf-message').value;
    const service = consultForm.dataset.service || "General";

    cfSubmit.disabled = true;
    cfSubmit.textContent = "Enviando...";
    cfStatus.textContent = "";
    cfStatus.className = "modal-status";

    const payload = {
      embeds: [{
        title: "🧾 Nueva consulta gratis — De La Isla",
        color: 11834458,
        fields: [
          { name: "Servicio de interés", value: service, inline: false },
          { name: "Nombre", value: name, inline: true },
          { name: "Negocio", value: business, inline: true },
          { name: "Email", value: email, inline: false },
          { name: "Teléfono", value: phone, inline: false },
          { name: "Qué necesita", value: message, inline: false }
        ],
        timestamp: new Date().toISOString()
      }]
    };

    try {
      const res = await fetch(DISCORD_WEBHOOK_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      if (res.ok) {
        cfStatus.textContent = "¡Listo! Te contactamos muy pronto.";
        cfStatus.className = "modal-status ok";
        consultForm.reset();
        setTimeout(() => {
          closeConsultModal();
          cfStatus.textContent = "";
        }, 2000);
      } else {
        throw new Error("Respuesta no válida de Discord");
      }
    } catch (err) {
      cfStatus.textContent = "No se pudo enviar. Intenta de nuevo.";
      cfStatus.className = "modal-status err";
    } finally {
      cfSubmit.disabled = false;
      cfSubmit.textContent = "Enviar";
    }
  });

  if (modal) {
    modal.addEventListener('click', (e) => {
      if (e.target.id === 'consultModal') closeConsultModal();
    });
  }
});

// ── Menú móvil (hamburguesa) ──────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  const navToggle = document.getElementById('navToggle');
  const navLinks = document.getElementById('navLinks');
  if (!navToggle || !navLinks) return;

  const closeNav = () => {
    navLinks.classList.remove('open');
    navToggle.setAttribute('aria-expanded', 'false');
    document.body.style.overflow = '';
  };

  navToggle.addEventListener('click', () => {
    const isOpen = navLinks.classList.toggle('open');
    navToggle.setAttribute('aria-expanded', String(isOpen));
    document.body.style.overflow = isOpen ? 'hidden' : '';
  });

  navLinks.querySelectorAll('a').forEach(a => a.addEventListener('click', closeNav));

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && navLinks.classList.contains('open')) closeNav();
  });
});

// ── Tilt 3D de la etiqueta del héroe (desactivado si el usuario prefiere menos movimiento) ──
document.addEventListener('DOMContentLoaded', () => {
  const heroLabel = document.querySelector('#heroLabel .label');
  const serviceHero = document.querySelector('.service-hero');
  if (!heroLabel || !serviceHero) return;
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  serviceHero.addEventListener('mousemove', (e) => {
    const rect = heroLabel.getBoundingClientRect();
    const cx = rect.left + rect.width / 2;
    const cy = rect.top + rect.height / 2;
    const dx = (e.clientX - cx) / rect.width;
    const dy = (e.clientY - cy) / rect.height;
    heroLabel.style.transform = `rotateY(${dx * 14}deg) rotateX(${-dy * 14}deg)`;
  });
  serviceHero.addEventListener('mouseleave', () => {
    heroLabel.style.transform = 'rotateY(0deg) rotateX(0deg)';
  });
});
