# ECLYPSE Club — landing page

Landing page de una sola pantalla (`index.html`) para **ECLYPSE Club**, discoteca
del Port d'Alcúdia (Mallorca). Archivo único, sin dependencias ni build: se abre
directamente en el navegador o se sube a cualquier hosting estático.

## Qué incluye

- Hero con eclipse animado en CSS puro y datos clave (día, horario, edad, dirección)
- Marquesina de géneros musicales
- Experiencia (sonido, luz, terraza, reservados)
- Agenda de próximos sábados con etiquetas y CTA de entradas
- Ambiente: cuatro paneles pensados para sustituirse por fotos reales
- Reservados: tres formatos de mesa con CTA de consulta
- Cómo llegar: dirección, horario, edad, dress code y enlace a Google Maps
- FAQ (`<details>` nativo, sin JS)
- CTA final a WhatsApp e Instagram, footer y datos estructurados `NightClub` (JSON-LD)
- Selector ES / EN (detecta el idioma del navegador y recuerda la elección)
- Menú móvil accesible, `prefers-reduced-motion`, focus visible y skip link

## Datos reales vs. datos de ejemplo

Verificado en fuentes públicas: nombre e Instagram (`@eclypse_club`), dirección
(Av. del Tucán 1, 07400 Port d'Alcúdia, Zona Magic) y que abre cada sábado.

**Pendiente de confirmar antes de publicar** (marcado con `TODO` en el HTML):
horario exacto, edad mínima y dress code; fechas, nombres de fiesta y line-up de
la agenda; enlaces de ticketing; número de WhatsApp de reservas; páginas legales;
y las fotos de la sección Ambiente.

## Personalización rápida

Los colores y el espaciado viven en las variables CSS de `:root`
(`--corona`, `--violet`, `--void`, `--maxw`…). Las tipografías son Anton y
Space Grotesk, cargadas desde Google Fonts.
