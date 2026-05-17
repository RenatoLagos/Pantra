# Pantra — Landing Page Spec

- **Status**: spec en revisión, pendiente implementación
- **Fecha**: 2026-05-08
- **Owner**: Renato Lagos
- **Idioma del spec**: español (referencia para founder)
- **Idioma del copy final a publicar**: alemán (default) + inglés (toggle)

---

## 0. Estrategia y Objetivos

### 0.1 Dos landings, dos propósitos

| Landing | Audiencia | Tiers mostrados | Goal primario |
|---------|-----------|----------------|---------------|
| **/einzelpraxis** | Outbound destination (Lead Scout campaigns) | Solo Plus únicamente (single-tier) | Trial signup OR llamada agendada con founder |
| **/pricing** (pública) | Tráfico orgánico, SEO, referrals | Solo + Solo Plus + add-ons | Comparativa + trial signup |

Este spec cubre PRIMERO `/einzelpraxis` (más urgente para outbound), después `/pricing`.

### 0.2 Conversion goals (/einzelpraxis)

1. **Primary CTA**: "14 Tage kostenlos testen" (trial 14 días sin tarjeta)
2. **Secondary CTA**: "30 Min mit dem Gründer sprechen" (llamada con founder)
3. **Tertiary CTA**: descargar AVV + 1-pager para revisar offline

### 0.3 Principios de diseño

- **Single tier visible**: cero tabla comparativa, cero confusión
- **DSGVO/AVV trust signals visibles desde el hero** — esto desbloquea más ventas que cualquier feature
- **Social proof slot reservado** desde día 1 (placeholder hasta tener testimonios alemanes)
- **Mobile-first**: muchos dentistas verán esto desde su WhatsApp en el celular
- **Página de 1 sola scroll vertical** — no multi-página, no menú
- **SEPA Lastschrift mencionado explícitamente** como método de pago

---

## 1. Wireframe ASCII (/einzelpraxis)

```
┌─────────────────────────────────────────────────────────────┐
│  [Pantra Logo]                          [DE | EN]   [Login] │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   HERO SECTION                                              │
│   ┌────────────────────────────────┐  ┌──────────────────┐ │
│   │                                │  │                  │ │
│   │  H1: Der KI-Assistent für      │  │  [WhatsApp UI    │ │
│   │  Ihre Zahnarztpraxis. 24/7.    │  │   Mockup mit     │ │
│   │  Mehrsprachig. DSGVO-konform.  │  │   conversación   │ │
│   │                                │  │   real animada]  │ │
│   │  Subhead: Pantra antwortet     │  │                  │ │
│   │  auf WhatsApp, bucht Termine   │  │  Pantra → "Hi,   │ │
│   │  und reduziert No-Shows um     │  │  wir haben am    │ │
│   │  30%. In Deutsch, Englisch +   │  │  Mittwoch um     │ │
│   │  2 Sprachen Ihrer Wahl.        │  │  14:30 Zeit. ✅" │ │
│   │                                │  │                  │ │
│   │  [CTA: 14 Tage kostenlos      │  │                  │ │
│   │   testen] [secondary: Demo]   │  │                  │ │
│   │                                │  │                  │ │
│   │  ✓ DSGVO-konform               │  │                  │ │
│   │  ✓ AVV inklusive               │  │                  │ │
│   │  ✓ Hosted in Frankfurt         │  │                  │ │
│   │  ✓ SEPA-Lastschrift            │  │                  │ │
│   └────────────────────────────────┘  └──────────────────┘ │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   PROBLEM FRAMING                                           │
│   "Verlieren Sie Patienten am Wochenende?"                  │
│                                                             │
│   ┌──────────┐ ┌──────────┐ ┌──────────┐                   │
│   │ Icon     │ │ Icon     │ │ Icon     │                   │
│   │ 73%      │ │ 24%      │ │ 30%      │                   │
│   │ schreiben│ │ Berliner │ │ kommen   │                   │
│   │ außerhalb│ │ haben    │ │ nicht zum│                   │
│   │ der      │ │ Migr.    │ │ Termin   │                   │
│   │ Sprech-  │ │ hinter-  │ │ ohne     │                   │
│   │ zeiten   │ │ grund    │ │ Erinnerg.│                   │
│   └──────────┘ └──────────┘ └──────────┘                   │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   HOW IT WORKS (3 pasos)                                    │
│                                                             │
│   1. Setup in 30 Minuten                                    │
│      WhatsApp Business verbinden, Kalender syncen, fertig.  │
│                                                             │
│   2. Pantra antwortet ab Tag 1                              │
│      24/7 in DE, EN + 2 Sprachen Ihrer Wahl.               │
│                                                             │
│   3. Sie sehen die Ergebnisse                               │
│      Wochenreport mit Buchungen, Anfragen, gerettete        │
│      No-Shows.                                              │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   FEATURES (4 cards)                                        │
│                                                             │
│   ┌──────────────────┐ ┌──────────────────┐                │
│   │ Mehrsprachig     │ │ Sprachnachrichten│                │
│   │ DE+EN inkl.      │ │ Patient sendet   │                │
│   │ +2 Sprachen      │ │ Audio, Pantra    │                │
│   │ wählbar (TR, AR, │ │ versteht und     │                │
│   │ ES, FR, RU, IT,  │ │ antwortet auf    │                │
│   │ PT)              │ │ Wunsch per Audio │                │
│   └──────────────────┘ └──────────────────┘                │
│                                                             │
│   ┌──────────────────┐ ┌──────────────────┐                │
│   │ Termin-buchung   │ │ No-Show Recovery │                │
│   │ Direkt in Google │ │ Automatische     │                │
│   │ Calendar oder    │ │ Erinnerungen +   │                │
│   │ Ihrem PVS        │ │ Re-booking bei   │                │
│   │ (Dampsoft, CHARLY,│ │ Absage           │                │
│   │ Z1)              │ │                  │                │
│   └──────────────────┘ └──────────────────┘                │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   SOCIAL PROOF (placeholder hasta tener testimonios)        │
│                                                             │
│   "[Testimonial slot — bis September 2026: Beta-Praxen      │
│   verwenden Pantra im Pilotprogramm. Erste                  │
│   Erfahrungsberichte in Kürze.]"                            │
│                                                             │
│   [Logos slot: 3 clínica logos cuando estén firmadas]       │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   PRICING (single-tier visible)                             │
│                                                             │
│   ┌────────────────────────────────────────┐               │
│   │  Solo Plus                             │               │
│   │  Für Ihre Einzelpraxis                 │               │
│   │                                        │               │
│   │  €349 / Monat                          │               │
│   │  + €399 einmalige Einrichtung          │               │
│   │                                        │               │
│   │  Inklusive:                            │               │
│   │  ✓ DE + EN + 2 Sprachen Ihrer Wahl    │               │
│   │  ✓ Sprachnachrichten (Audio)          │               │
│   │  ✓ Bis zu 2.000 Konversationen/Monat  │               │
│   │  ✓ Terminbuchung + PVS-Integration    │               │
│   │  ✓ No-Show Recovery                   │               │
│   │  ✓ Telegram + Email Eskalation        │               │
│   │  ✓ AVV inklusive (DSGVO)              │               │
│   │  ✓ Hosted in Frankfurt                │               │
│   │  ✓ Premium Support (24h)              │               │
│   │                                        │               │
│   │  Jährlich zahlen → 2 Monate gratis     │               │
│   │                                        │               │
│   │  [CTA: 14 Tage kostenlos testen]      │               │
│   │  [secondary: Live-Demo buchen]        │               │
│   │                                        │               │
│   │  Bezahlung: SEPA-Lastschrift          │               │
│   │  oder Kreditkarte                     │               │
│   └────────────────────────────────────────┘               │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   TRUST / DSGVO BLOCK                                       │
│                                                             │
│   ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐     │
│   │ DSGVO    │ │ AVV      │ │ Server   │ │ SEPA     │     │
│   │ konform  │ │ inkl.    │ │ in DE    │ │ Last-    │     │
│   │          │ │ (PDF)    │ │ (Frank-  │ │ schrift  │     │
│   │          │ │          │ │ furt)    │ │          │     │
│   └──────────┘ └──────────┘ └──────────┘ └──────────┘     │
│                                                             │
│   [Link: AVV als PDF herunterladen]                         │
│   [Link: Datenschutzerklärung]                              │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   FAQ (5-7 preguntas en alemán)                             │
│                                                             │
│   ▸ Ist Pantra DSGVO-konform?                               │
│   ▸ Wo werden Patientendaten gespeichert?                   │
│   ▸ Welche Praxisverwaltungssysteme werden unterstützt?     │
│   ▸ Wie lange dauert die Einrichtung?                       │
│   ▸ Was passiert, wenn Pantra eine Frage nicht versteht?    │
│   ▸ Kann ich Pantra abbestellen?                            │
│   ▸ Welche WhatsApp-Nummer wird verwendet?                  │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   FINAL CTA                                                 │
│                                                             │
│   "Bereit, Ihre Praxis zu entlasten?"                       │
│   [CTA primary: 14 Tage kostenlos testen]                   │
│   [CTA secondary: 30 Min mit Gründer sprechen]              │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   FOOTER                                                    │
│   Pantra | Impressum | Datenschutz | AVV | Kontakt          │
│   © 2026 Pantra GmbH (o legal entity correspondiente)       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Copy Completo (referencia ES — traducir a DE + EN antes de publicar)

> **IMPORTANTE**: este copy está en español como referencia para review. Antes de publicar, el founder + amigo alemán deben:
> 1. Traducir al alemán manteniendo el tono profesional pero cálido
> 2. Traducir al inglés para el toggle
> 3. Validar que el alemán suena nativo, no traducido (Marketing-Deutsch, no Schul-Deutsch)

### 2.1 Hero

**H1**: El asistente de IA para tu clínica dental. 24/7. Multilingüe. Conforme con DSGVO.

**Subhead**: Pantra responde tus mensajes de WhatsApp, reserva turnos y reduce los no-shows en un 30%. En alemán, inglés y 2 idiomas más a tu elección.

**CTA primario**: Probá 14 días gratis
**CTA secundario**: Agendá una demo

**Trust pills (debajo del CTA)**:
- DSGVO-konform
- AVV inklusive
- Hosted in Frankfurt
- SEPA-Lastschrift

### 2.2 Problem Framing

**Headline**: ¿Estás perdiendo pacientes los fines de semana?

**3 estadísticas con icono**:
- **73%** de los mensajes a clínicas dentales se envían fuera del horario de atención
- **24%** de la población berlinesa tiene background migrante
- **30%** de los pacientes faltan al turno sin recordatorio activo

### 2.3 How It Works

**Headline**: Así funciona Pantra

**Paso 1 — Setup en 30 minutos**
Conectá tu WhatsApp Business, sincronizá tu calendario y listo. Sin configuraciones técnicas, sin training de IA. Tu equipo no tiene que aprender nada nuevo.

**Paso 2 — Pantra responde desde el día 1**
24/7, en alemán, inglés y los 2 idiomas que elijas. Conversaciones naturales, no robóticas. Si un paciente pide algo complejo, Pantra deriva al equipo automáticamente.

**Paso 3 — Vos ves los resultados**
Reporte semanal con cuántos turnos se reservaron, cuántos no-shows se evitaron y qué se respondió. Toma de decisiones con data, no con suposiciones.

### 2.4 Features (4 cards)

**Card 1 — Multilingüe**
Atendé pacientes en alemán, inglés y 2 idiomas adicionales a tu elección: turco, árabe, español, francés, ruso, italiano o portugués. ¿Necesitás un 3er idioma? Sumalo por +€39/mes.

**Card 2 — Mensajes de voz**
Tus pacientes mandan audio, Pantra los entiende, transcribe y responde. Si querés, también puede responder con audio. Crítico para pacientes mayores y migrantes que prefieren hablar a escribir.

**Card 3 — Reserva de turnos**
Pantra reserva directo en Google Calendar, iCal o tu PVS (Dampsoft, CHARLY, Z1). Sin doble entrada, sin errores. Confirma con el paciente antes de cerrar el turno.

**Card 4 — No-Show Recovery**
Recordatorios automáticos a 48h, 24h y 2h antes del turno. Si el paciente cancela, Pantra ofrece automáticamente el slot al siguiente en lista de espera. Tus turnos no quedan vacíos.

### 2.5 Social Proof (placeholder)

**Hasta tener 3 testimonios alemanes (mes 3)**:

> "Hasta septiembre 2026: clínicas piloto están usando Pantra en programa beta. Próximamente publicaremos los primeros casos de éxito."

**Logos slot**: 3 logos de clínicas (cuando firmen design partners)

**Después (mes 4+)**:
- Testimonio en video del primer dentista berlinés con métricas
- Quote del segundo
- Quote del tercero
- Logos de las 3 clínicas

### 2.6 Pricing (single tier — Solo Plus)

**Tier name**: Solo Plus
**Tagline**: Para tu Einzelpraxis

**Precio**: €349 / mes
**Setup fee**: + €399 una sola vez

**Incluido**:
- DE + EN + 2 idiomas a tu elección (TR, AR, ES, FR, RU, IT, PT)
- Mensajes de voz (entrada y opcionalmente salida)
- Hasta 2.000 conversaciones por mes
- Reserva de turnos + integración con tu PVS
- No-Show Recovery automático
- Escalación a humano por Telegram + Email
- AVV incluido (DSGVO)
- Servidores en Frankfurt
- Soporte premium (respuesta en 24h)

**Promo destacada**: Pago anual → 2 meses gratis (paga 10, recibe 12)

**CTA primario**: Probá 14 días gratis
**CTA secundario**: Agendá una demo en vivo

**Métodos de pago**: SEPA-Lastschrift o tarjeta de crédito

### 2.7 Trust / DSGVO Block

**Headline**: Compliance que las clínicas alemanas exigen

**4 trust badges**:
1. **DSGVO-konform** — Procesamiento de datos según el reglamento europeo
2. **AVV inkl.** — Auftragsverarbeitungsvertrag firmable [Descargar PDF]
3. **Server in Deutschland** — Hosted in Frankfurt
4. **SEPA-Lastschrift** — Pago como cualquier proveedor alemán

**Links**:
- AVV als PDF herunterladen
- Datenschutzerklärung

### 2.8 FAQ

**Q: ¿Es Pantra conforme con DSGVO?**
A: Sí. Pantra procesa todos los datos según el reglamento europeo. Firmamos AVV (Auftragsverarbeitungsvertrag) con cada clínica antes de procesar mensajes de pacientes. Los servidores están en Frankfurt.

**Q: ¿Dónde se almacenan los datos de los pacientes?**
A: En servidores ubicados en Frankfurt, Alemania (AWS Frankfurt eu-central-1). Los logs se redactan de PII automáticamente y se retienen por 7 días máximo.

**Q: ¿Qué sistemas de gestión de pacientes (PVS) son compatibles?**
A: Dampsoft, CHARLY, Z1 vía webhook. Otros sistemas se integran vía Google Calendar como fallback. Si tu PVS no está en la lista, contactanos.

**Q: ¿Cuánto tarda la configuración?**
A: 30 minutos. Te ayudamos a conectar tu WhatsApp Business y tu calendario. No necesitás conocimientos técnicos.

**Q: ¿Qué pasa si Pantra no entiende una pregunta?**
A: Pantra deriva automáticamente a una persona de tu equipo vía Telegram o email. Vos siempre tenés el control final. Pantra nunca toma decisiones médicas ni comerciales sensibles.

**Q: ¿Puedo cancelar Pantra cuando quiera?**
A: Sí. Cancelación mensual sin compromiso (excepto si optás por el plan anual prepago). Tus datos se exportan y borran según DSGVO.

**Q: ¿Qué número de WhatsApp se usa?**
A: El número de tu clínica. Conectamos vía WhatsApp Business Cloud API (oficial de Meta). No se cambia el número que tus pacientes ya conocen.

### 2.9 Final CTA

**Headline**: ¿Listo para descargarte tu equipo?

**Subhead**: Probá Pantra 14 días sin compromiso. Sin tarjeta. Sin instalación.

**CTA primario**: Probá 14 días gratis
**CTA secundario**: 30 min con el founder

### 2.10 Footer

- Pantra | Impressum | Datenschutz | AVV | Kontakt
- © 2026 Pantra (legal entity)
- Made in Berlin

---

## 3. Componentes Técnicos

### 3.1 Stack recomendado (consistente con repo actual)

**Opción A — FastAPI + Jinja (recomendado para MVP)**
- Reutiliza el stack existente del repo (`src/pantra/api/` + `templates/`)
- Nuevo route: `GET /einzelpraxis` y `GET /pricing`
- Templates en `templates/landing/einzelpraxis.html.j2` y `templates/landing/pricing.html.j2`
- Estilos: TailwindCSS via CDN o build local
- Forms (trial + demo) → endpoints `POST /api/leads/trial` y `POST /api/leads/demo`
- Validación pydantic, persistencia en `leads` table

**Opción B — Astro / Next.js separado** (mejor SEO + performance, más trabajo)
- Repo separado o `/landing` directory
- Static generation, deploy a Vercel/Netlify
- Pros: mejor Core Web Vitals, SEO superior, A/B testing más fácil
- Cons: 2 codebases, requiere setup adicional

**Recomendación**: arrancar con **Opción A (Jinja)** para validar conversion. Migrar a Astro si SEO se vuelve la principal palanca de growth (mes 5+).

### 3.2 Componentes a desarrollar

| Componente | Ubicación | Detalle |
|-----------|-----------|---------|
| Landing route | `src/pantra/api/landing.py` | Renderiza Jinja, expone formularios |
| Templates | `templates/landing/einzelpraxis.html.j2`, `templates/landing/pricing.html.j2` | HTML + Tailwind |
| Lead capture endpoint | `src/pantra/api/leads.py` | `POST /api/leads/{trial,demo}` |
| Lead model | `src/pantra/models/lead.py` | SQLAlchemy: name, email, clinic_name, message, source, language |
| Email notificación | `src/pantra/handoff/email.py` (existente) | Notificar founder cuando hay nuevo lead |
| WhatsApp UI mockup animado | `static/landing/whatsapp-mockup.svg` o componente JS | Mostrar conversación real Pantra |
| AVV PDF | `static/legal/avv.pdf` | Subir versión firmable cuando esté listo |
| Privacy policy + Impressum | `templates/legal/{datenschutz,impressum}.html.j2` | Páginas legales DSGVO |

### 3.3 Forms y validación

**Trial form**:
```python
class TrialRequest(BaseModel):
    clinic_name: str
    contact_name: str
    email: EmailStr
    phone: str  # optional
    languages_interested: list[str]  # ["DE", "EN", "TR", ...]
    consent_dsgvo: bool  # required True
    consent_marketing: bool  # optional
```

**Demo form**:
```python
class DemoRequest(BaseModel):
    clinic_name: str
    contact_name: str
    email: EmailStr
    phone: str
    preferred_time: str  # "morning" / "afternoon" / "evening"
    notes: str  # optional
    consent_dsgvo: bool  # required True
```

**Anti-spam**: honeypot field + rate limiting por IP (Redis-based).

### 3.4 Analytics

**Recomendado**: **Plausible** (DSGVO-friendly, sin cookies, alemán-first)
- Costo: €9/mes para sitios pequeños
- Sin banner de cookies necesario
- Métricas: pageviews, conversion rate por CTA, bounce rate

**Alternativa**: PostHog self-hosted (más data, más complejo)

**Eventos a trackear**:
- `landing_view` con source (utm parameters)
- `cta_trial_clicked`
- `cta_demo_clicked`
- `form_trial_submitted`
- `form_demo_submitted`
- `language_toggled`
- `pdf_avv_downloaded`

---

## 4. SEO y Schema

### 4.1 Meta tags

```html
<title>Pantra — KI-Assistent für Zahnarztpraxen | WhatsApp 24/7 mehrsprachig</title>
<meta name="description" content="Pantra ist der KI-WhatsApp-Assistent für Ihre Zahnarztpraxis in Berlin. Termine buchen, Erinnerungen senden, No-Shows reduzieren — in DE, EN + 2 Sprachen Ihrer Wahl. DSGVO-konform.">
<meta property="og:title" content="Pantra — KI-Assistent für Zahnarztpraxen">
<meta property="og:description" content="Mehrsprachiger WhatsApp-Assistent für Zahnarztpraxen. DSGVO-konform.">
<meta property="og:image" content="/static/og/landing-einzelpraxis.png">
<meta property="og:locale" content="de_DE">
```

### 4.2 Schema.org (JSON-LD)

```json
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "Pantra",
  "applicationCategory": "BusinessApplication",
  "applicationSubCategory": "Healthcare AI Assistant",
  "operatingSystem": "Web-based",
  "offers": {
    "@type": "Offer",
    "price": "349",
    "priceCurrency": "EUR",
    "priceSpecification": {
      "@type": "UnitPriceSpecification",
      "price": "349",
      "priceCurrency": "EUR",
      "billingDuration": "P1M"
    }
  },
  "areaServed": "DE",
  "audience": {
    "@type": "BusinessAudience",
    "audienceType": "Dental practices"
  }
}
```

### 4.3 Keywords target (alemán)

**Primarios**:
- "KI Assistent Zahnarztpraxis"
- "WhatsApp Assistent Zahnarzt"
- "Zahnarztpraxis Berlin Software"
- "mehrsprachiger Chatbot Zahnarzt"

**Long-tail**:
- "WhatsApp Assistent für Zahnarztpraxis Berlin"
- "Termine buchen WhatsApp Zahnarzt"
- "DSGVO konformer KI Assistent Zahnarzt"
- "No-Show Reduktion Zahnarztpraxis"

**Estrategia SEO**: arrancar con landing optimizada + 5-8 artículos de blog en alemán mes 4-5 (sobre temas como "Wie reduziere ich No-Shows in meiner Praxis", "DSGVO und KI in der Zahnmedizin", etc.).

---

## 5. Trust Signals (CRÍTICO en healthcare DACH)

### 5.1 Visibles desde el hero

- Pill: "DSGVO-konform"
- Pill: "AVV inklusive"
- Pill: "Hosted in Frankfurt"
- Pill: "SEPA-Lastschrift"

### 5.2 Sección dedicada (mid-page)

Bloque visual con 4 badges + iconos SVG:
1. DSGVO compliance
2. AVV (PDF descargable)
3. Server in Deutschland
4. SEPA payment

### 5.3 Footer

- Link a Impressum (obligatorio en Alemania)
- Link a Datenschutzerklärung
- Link a AVV PDF
- Link a Kontakt

### 5.4 Otros trust elements

- **Security badges** (cuando los tengamos): SOC 2, DIN ISO 27001
- **Testimonials con foto + nombre + clínica + ciudad** (mes 3+)
- **Casos de éxito con métricas verificables** (mes 4+)
- **Founder LinkedIn link** visible para "human accountability"

---

## 6. Implementación Recomendada (orden y tiempos)

### Sprint 1 (semana 1-2 de mes 1)

- [ ] Setup landing route en FastAPI (`/einzelpraxis`, `/pricing`)
- [ ] Template Jinja base con TailwindCSS
- [ ] Hero + Problem Framing + How it works (secciones 1-3)
- [ ] Lead capture endpoints + DB model
- [ ] Plausible analytics integrado

### Sprint 2 (semana 3-4 de mes 1)

- [ ] Features cards + Pricing card + Trust block
- [ ] FAQ section
- [ ] Final CTA + Footer
- [ ] WhatsApp UI mockup animado (puede ser SVG simple o video corto)
- [ ] Versión EN del copy (toggle)

### Sprint 3 (mes 2)

- [ ] AVV PDF subido cuando esté firmado por abogado
- [ ] Datenschutzerklärung + Impressum publicados
- [ ] Schema.org JSON-LD
- [ ] OG images
- [ ] Forms tested end-to-end (trial + demo)
- [ ] Email notification al founder por cada lead

### Sprint 4 (mes 3, post-design partners)

- [ ] Reemplazar testimonial placeholders con real social proof
- [ ] Agregar logos de design partners
- [ ] Caso de éxito #1 publicado
- [ ] A/B test del Hero (variar headline)

---

## 7. Métricas de éxito de la landing

| Métrica | Target mes 2 | Target mes 6 |
|---------|-------------|--------------|
| Visitas únicas/mes | 50-100 (solo outbound) | 500-1.000 (outbound + SEO) |
| Conversion rate trial | 8-12% | 15-20% (con social proof) |
| Conversion rate demo | 3-5% | 6-10% |
| Bounce rate | <60% | <45% |
| Tiempo promedio en página | >1:30 | >2:00 |

---

## 8. Notas para el founder

1. **No publicar la landing sin AVV firmado**. Sin AVV no podés vender en healthcare alemán; mejor tenerla en draft que pública sin compliance.

2. **El copy en alemán DEBE ser revisado por nativo**. Marketing-Deutsch no es Schul-Deutsch. Tu amigo alemán debe pasar por cada sección.

3. **WhatsApp UI mockup**: si no tenés tiempo de hacer animación compleja, un screenshot con conversación real anclada arriba ya impacta. Lo importante es transmitir "esto es WhatsApp real, no un chatbot raro".

4. **El single-tier en /einzelpraxis es estratégico**. No agregues "Solo €149" ahí pensando que ayuda — empuja a Solo Plus, donde está el valor real y el margen.

5. **El plan anual prepago se vende AHÍ en la landing**. No esperes a que pidan trial. Mostrarlo en pricing lock-in pricing antes de que LLM costs cambien.

6. **La sección de testimonios en placeholder no es vergüenza**. Es honestidad. Mejor "estamos en piloto, casos de éxito en septiembre" que un testimonial inventado o genérico.

---

## 9. Anexo — Checklist legal antes de publicar

- [ ] AVV (Auftragsverarbeitungsvertrag) firmable con abogado alemán
- [ ] Datenschutzerklärung redactada por abogado (NO usar generador online genérico)
- [ ] Impressum completo con datos legales (Inhaber, Anschrift, Kontakt, Steuernummer si aplica)
- [ ] Cookie policy (aunque uses Plausible y no requiera consent, mejor tener el documento)
- [ ] Términos y condiciones (AGB) si vas a vender
- [ ] DSGVO opt-in en formularios (checkbox required)
- [ ] Doble opt-in para newsletter si vas a tener uno
- [ ] Backup de logs server-side por 7 días máximo
- [ ] Process de borrado de datos (right to erasure) documentado
