# Pantra — Brief técnico para abogado alemán (AVV / DSGVO)

- **Status**: draft v1 — listo para enviar al abogado
- **Fecha**: 2026-05-08
- **Owner**: Renato Lagos
- **Producto**: Pantra (KI-WhatsApp-Assistent für Zahnarztpraxen)
- **Idioma del documento**: español (referencia interna) + términos técnicos alemanes
- **Output esperado del abogado**: AVV (Auftragsverarbeitungsvertrag) firmable + Datenschutzerklärung + Impressum + revisión de §7 UWG opt-out

---

## 0. Cómo usar este documento

1. **Vos** revisás todo el contenido y validás que refleja la realidad del producto
2. **Mandás al abogado** alemán especializado en Healthcare/IT-Recht el bloque de
   "Email al abogado" (Anexo D) + este documento como anexo PDF
3. El abogado redacta:
   - **AVV** (Auftragsverarbeitungsvertrag) para que cada clínica firme antes del primer pago
   - **Datenschutzerklärung** para `pantra.de/datenschutz`
   - **Impressum** para `pantra.de/impressum`
   - **AGB** (Allgemeine Geschäftsbedingungen) — opcional pero recomendado
4. Vos firmás el primer ejemplar de AVV cuando se cierre el primer cliente

**Costo estimado**: €1.500-3.000 one-time para los 4 documentos. Retainer
mensual €100-200 si querés revisar cambios futuros.

---

## 1. Contexto del producto (Was ist Pantra?)

Pantra es un asistente conversacional de IA que recibe mensajes de WhatsApp
de pacientes de clínicas dentales en Berlin, los procesa con LLM (Claude
de Anthropic), y responde en nombre de la clínica. Funciones:

- **Atender mensajes 24/7** en WhatsApp en alemán, inglés y otros idiomas
- **Reservar turnos** vía Google Calendar o sistema PVS de la clínica
- **Enviar recordatorios** automáticos 48h/24h/2h antes del turno
- **Reducir no-shows** ofreciendo el slot a lista de espera tras cancelaciones
- **Derivar a humano** cuando la conversación lo requiere (Telegram + email)
- **Multilingüe**: detecta el idioma del paciente y responde en el mismo

**Modelo de negocio**: SaaS B2B mensual (€349/mes Solo Plus) facturado a la
clínica dental. Cliente firma AVV antes del primer cobro.

**Stack técnico relevante para DSGVO**:
- Backend: Python + FastAPI hosted en AWS Frankfurt (eu-central-1)
- Database: PostgreSQL en AWS RDS Frankfurt
- Cache/queue: Redis en AWS Frankfurt
- LLM principal: Anthropic Claude API (USA, con DPA firmado por Anthropic)
- LLM clasificador: mismo Anthropic
- STT (audio → texto): OpenAI Whisper API (USA)
- TTS opcional: ElevenLabs (USA)
- Canal: WhatsApp Business Cloud API (Meta, EU + USA)
- Email transaccional: Resend (USA + EU)
- Telegram: Telegram Messenger LLP (UK)

---

## 2. Categorías de datos personales procesados (Personenbezogene Daten)

Lista exhaustiva de qué datos PII (Datenkategorien) toca Pantra:

### 2.1 Datos del paciente (datos del afectado / Betroffene)

| Categoría | Ejemplo | Origen | Storage |
|-----------|---------|--------|---------|
| **Identificadores de contacto** | Número de teléfono, nombre (si lo declara) | El paciente lo manda | Postgres `customers` table |
| **Contenido del mensaje** | Texto del WhatsApp incl. preguntas sobre síntomas, urgencias, etc. | El paciente | Postgres `messages` table |
| **Audio del paciente** | Voice notes (si los manda) | El paciente | Filesystem temp + transcripción en `messages` |
| **Datos de contexto sanitario** | Posible mención de síntomas, medicación, dolor (NO se solicita ni almacena estructuradamente) | El paciente lo escribe libremente | En texto del mensaje, **PII redaction aplicada en logs** |
| **Datos de booking** | Fecha/hora del turno, servicio, practicante asignado | Pantra crea via tool | Postgres `bookings` table + Google Calendar |
| **Idioma preferido** | DE/EN/TR/etc detectado por classifier | Inferido | Postgres `customers.preferred_language` |

### 2.2 Datos del personal de la clínica (Mitarbeiter)

- Nombres de practitioners (públicos en la web de la clínica): NO son datos personales sensibles, pero figuran en respuestas del bot
- Email del owner de la clínica (para recibir handoffs): Postgres `business.config`
- Número de teléfono del owner para Telegram bot: Postgres `business.config`

### 2.3 Datos NO procesados (importante para el AVV)

Para defaultear conservador — Pantra NO procesa:
- **Datos médicos sensibles estructurados** (diagnósticos, recetas, historia clínica). Si el paciente menciona algo en chat, queda en el mensaje pero NO se extrae a campo dedicado.
- **Datos de pago del paciente**: Pantra no toca billing del paciente.
- **Datos biométricos**: voz se transcribe a texto, audio se borra a las 24h (worker `audio_retention.py`).
- **Datos de menores no acompañados**: si el paciente declara <16, Pantra deriva a humano.

---

## 3. Sub-procesadores (Subunternehmer / Subprocessors)

Esta es la lista que el abogado necesita para redactar el Anhang del AVV.
Cada uno es un sub-procesador que procesa datos del paciente en nombre de
Pantra (que a su vez procesa en nombre de la clínica).

| Sub-procesador | Qué procesa | Ubicación | Mecanismo de transferencia | DPA del proveedor |
|---------------|-------------|-----------|---------------------------|-------------------|
| **AWS Frankfurt** (eu-central-1) | Hosting backend, Postgres, Redis, audio storage temp | EU 🇪🇺 | Sin transferencia a USA | [AWS DPA + EU SCC](https://aws.amazon.com/compliance/gdpr-center/) |
| **Anthropic** (Claude API) | Texto del mensaje del paciente para generar la respuesta | USA 🇺🇸 | EU SCC + Anthropic DPA | [Anthropic Trust Center DPA](https://www.anthropic.com/legal/dpa) |
| **OpenAI** (Whisper STT) | Audio del paciente (si manda voice note) | USA 🇺🇸 | EU SCC + OpenAI DPA | [OpenAI DPA](https://openai.com/policies/data-processing-addendum) |
| **ElevenLabs** (TTS opcional) | Texto a voz para responder con audio | USA 🇺🇸 | EU SCC | ElevenLabs DPA on request |
| **Meta WhatsApp Business Cloud API** | Mensajes ya están en WhatsApp del paciente; Pantra solo recibe webhooks | EU + USA | Meta tiene EU SCC + WhatsApp DPA | [WhatsApp Business DPA](https://www.whatsapp.com/legal/business-data-transfer-addendum) |
| **Resend** (email transaccional) | Email al owner sobre handoff o leads de marketing | USA + EU | EU SCC | [Resend DPA](https://resend.com/legal/dpa) |
| **Telegram** (bot para handoff al owner) | Mensaje resumen del handoff (sin PII completa, redactado) | UK + Distributed | UK adequacy decision | [Telegram Privacy Policy](https://telegram.org/privacy) |
| **Google Calendar** (opcional) | Booking events si la clínica usa Google Calendar | USA | EU SCC + Google DPA | [Google Cloud DPA](https://cloud.google.com/terms/data-processing-addendum) |

**Cláusula importante para el AVV**: la clínica acepta la lista de
sub-procesadores y Pantra notifica con 30 días de antelación cualquier
cambio (estándar §28 (2) DSGVO).

### Transferencia internacional (Drittlandsübermittlung)

Datos del paciente sí salen a USA (Anthropic, OpenAI, ElevenLabs, Meta).
Mecanismo legal: **EU Standard Contractual Clauses (2021/914)** + Anthropic
está bajo el **EU-US Data Privacy Framework** (certificado, octubre 2024).

El abogado tiene que confirmar que esto es suficiente o si necesitamos:
- Transfer Impact Assessment (TIA) por proveedor
- Información explícita en la Datenschutzerklärung sobre transferencias
- Consentimiento adicional del paciente (Art. 49 DSGVO) — probablemente NO necesario si SCC + DPF cubren

---

## 4. Medidas técnicas y organizativas (TOMs / Technische und organisatorische Maßnahmen)

Anhang 2 del AVV típicamente lista las TOMs. Acá están las que Pantra
implementa, ordenadas por categoría DSGVO Art. 32:

### 4.1 Confidencialidad (Vertraulichkeit)

- **Encryption in transit**: TLS 1.3 para todas las conexiones API + DB
- **Encryption at rest**: AWS RDS Postgres con AES-256 + KMS managed keys
- **PII redaction in logs**: regex automático antes de guardar logs (`src/pantra/privacy/pii.py`) — emails, teléfonos, nombres comunes, números de identificación
- **Audio retention**: 24 horas máximo (worker `audio_retention.py`), después borrado
- **Log retention**: 7 días (config `log_retention_days = 7`)
- **Acceso**: solo founder + futuro CS team con MFA + IAM individual
- **Aislamiento multi-tenant**: cada `business_id` separado, queries siempre con WHERE business_id = X

### 4.2 Integridad (Integrität)

- **Validación de input**: Pydantic strict en todos los endpoints
- **Idempotencia**: tool calls usan idempotency keys (`models/idempotency.py`)
- **Audit log**: todas las AI runs registradas en `ai_runs` table con prompt redactado, model, tokens
- **Backup**: AWS RDS automated backups, retention 7 días
- **Database constraints**: `UniqueConstraint` en mensajes, `SELECT FOR UPDATE` en booking concurrency

### 4.3 Disponibilidad (Verfügbarkeit)

- **Redundancia**: AWS multi-AZ para Postgres
- **Monitoring**: structlog → log aggregation (TBD)
- **Backup**: automated daily, point-in-time recovery hasta 7 días

### 4.4 Procedimientos de revisión y mejora (Verfahren zur regelmäßigen Überprüfung)

- **Code review**: cada cambio passa por revisión + CI tests (29 tests actualmente)
- **Eval pipeline**: `src/pantra/evals/runner.py` — corre cases YAML en cada cambio de prompt
- **DSGVO opt-out**: campo `customer.opted_out` respetado en pipeline (no se procesan más mensajes)

### 4.5 Datenminimierung

- **Solo se almacena** lo que es necesario para el servicio
- **PII redaction** en logs antes de persistir
- **Sliding window** de mensajes en memoria (last 20) + summary, no historial completo en context LLM
- **Right to erasure**: endpoint admin (TODO) que borra customer + cascada por foreign keys

### 4.6 Pseudonymisierung

- IDs de paciente son UUID (no contienen PII)
- Conversaciones identificadas por UUID + business_id
- Logs operativos referencian solo UUIDs, no nombres

---

## 5. Tiempos de retención y derechos del afectado (Aufbewahrung + Betroffenenrechte)

### 5.1 Retención por categoría

| Dato | Retention default | Justificación |
|------|------------------|---------------|
| Mensajes de WhatsApp | Mientras dure la relación cliente-clínica + 30 días post-cierre | Para que el paciente pueda referenciar conversaciones pasadas |
| Audio del paciente | **24 horas** (auto-delete) | Solo para transcripción; texto se conserva |
| Bookings | 3 años (Aufbewahrungspflichten zahnärztlich) | Documentación legal sanitaria |
| Logs operativos (con PII redacted) | 7 días | Debug + soporte |
| AI Run records (sin contenido PII) | 90 días | Cost analytics + observability |
| Customer record | Hasta opt-out o cierre del business | Para reidentificar al volver el paciente |

**Pregunta al abogado**: ¿coincide con BZÄK / KZBV requirements (Aufbewahrungsfristen für Zahnarztpraxen)? Algunas clínicas tienen 10 años para historias clínicas — pero Pantra NO almacena historia clínica, solo conversaciones + bookings.

### 5.2 Derechos del afectado (Art. 15-22 DSGVO)

Lo que tenemos que ofrecer:

- **Auskunft** (Art. 15): export JSON de todos los datos del paciente — endpoint admin pendiente
- **Berichtigung** (Art. 16): edit del nombre/teléfono — vía soporte
- **Löschung / "Right to erasure"** (Art. 17): delete cascade — endpoint admin pendiente, cumple con cascade en foreign keys
- **Einschränkung** (Art. 18): flag `customer.opted_out` ya implementado
- **Datenübertragbarkeit** (Art. 20): JSON export
- **Widerspruch** (Art. 21): opt-out flag
- **Automatisierte Einzelfallentscheidungen** (Art. 22): Pantra NO toma decisiones automatizadas con efecto legal (no aprueba créditos, no diagnostica, no rechaza tratamientos). Cualquier decisión sensible deriva a humano vía handoff.

### 5.3 Quejas (Beschwerden)

Datos de contacto del DPO (Datenschutzbeauftragter) — pregunta al abogado:
¿Pantra necesita un DPO formal? Por tamaño (1 founder + 0 empleados) probablemente **no obligatorio** pero recomendable nombrar contacto en `datenschutz@pantra.de`.

---

## 6. Cláusulas específicas que debe contener el AVV

Lista de comprobación basada en §28 DSGVO + IT-Sicherheitsrichtlinie BZÄK:

- [ ] **Gegenstand und Dauer der Verarbeitung** (servicio Pantra durante vigencia del contrato)
- [ ] **Art und Zweck der Verarbeitung** (procesamiento de mensajes WhatsApp para responder en nombre de la clínica)
- [ ] **Art der personenbezogenen Daten** (lista de la sección 2.1)
- [ ] **Kategorien der Betroffenen** (pacientes de la clínica)
- [ ] **Pflichten und Rechte des Verantwortlichen** (la clínica)
- [ ] **Weisungsbefugnis** (la clínica da instrucciones documentadas; Pantra solo procesa conforme)
- [ ] **Vertraulichkeit der Mitarbeiter** (Pantra garantiza que su personal está obligado a confidencialidad)
- [ ] **TOMs** (Anhang 2 — usar lo de la sección 4)
- [ ] **Sub-procesadores** (lista de la sección 3, derecho de objeción de la clínica)
- [ ] **Apoyo en derechos del afectado** (Pantra ayuda a la clínica a responder requests Art. 15-22)
- [ ] **Apoyo en seguridad y notificación de brechas** (data breach notification al cliente en <24h)
- [ ] **Audit rights** (la clínica puede auditar Pantra una vez al año, costo razonable)
- [ ] **Devolución/borrado de datos al fin del contrato** (export JSON + delete dentro de 30 días)
- [ ] **Information sobre Drittlandübermittlung** (sub-procesadores en USA + SCC)
- [ ] **Haftung und Schadenersatz** (limitación razonable, NO renunciamos a culpa grave)
- [ ] **Schlussbestimmungen** (lex loci, jurisdicción, escritura, idioma)

---

## 7. Datenschutzerklärung — contenido obligatorio

Para `pantra.de/datenschutz` el abogado tiene que cubrir:

1. **Verantwortlicher** (datos del responsable Pantra GmbH o legal entity)
2. **Datenschutzbeauftragter** si aplica
3. **Categorías de datos procesadas** (lista 2.1)
4. **Finalidad de cada procesamiento** + Rechtsgrundlage (Art. 6 (1) DSGVO):
   - Atender al paciente vía WhatsApp: **§6 (1) b** (cumplimiento de contrato entre paciente y clínica)
   - Outreach a clínicas (marketing): **§6 (1) f** + **§7 UWG** (legitimes Interesse B2B con opt-out)
   - Logs y analytics internos: **§6 (1) f** (legitimes Interesse en seguridad y mejora)
   - Cookies de Plausible (si los usás): **NO requiere consent banner** (Plausible es DSGVO-friendly sin cookies persistentes), pero igual mencionar
5. **Sub-procesadores y transferencias internacionales** (sección 3)
6. **Tiempos de retención** (sección 5.1)
7. **Derechos del afectado** (sección 5.2)
8. **Cookies/Tracking**: declarar Plausible o lo que uses
9. **Datenschutzbehörde de Berlin** como contacto de queja: Berliner Beauftragte für Datenschutz und Informationsfreiheit

---

## 8. Impressum — contenido obligatorio (§5 TMG)

Para `pantra.de/impressum`:

- Nombre y dirección del responsable (Pantra GmbH si entity, o "Renato Lagos, Einzelunternehmer")
- Contacto: email + teléfono
- Steuernummer / USt-IdNr (si tenés)
- Handelsregister (si entity registrada)
- Berufsbezeichnung (si aplica)
- Aufsichtsbehörde (si aplica)
- Inhaltlich Verantwortlicher según §55 RStV (Renato Lagos)

---

## 9. AGB (Allgemeine Geschäftsbedingungen) — opcional pero recomendado

Para `pantra.de/agb`:

- Vertragspartner (Pantra como Anbieter, clínica como Kunde)
- Leistungsbeschreibung (qué hace Pantra)
- Pricing (Solo Plus €349/mes + setup €399 + €0,15/conv excedente)
- Laufzeit + Kündigung (mensual sin compromiso, anual prepago opcional)
- **Ajuste de precios** — cláusula de hasta 8% anual con 60 días aviso (decisión de pricing v4)
- Hard limits + excedente cobrable
- Haftungsbegrenzung
- Lex loci + jurisdicción

---

## 10. Cuestiones específicas para discutir con el abogado

Lista de preguntas concretas (en alemán, para el email):

1. **DPO obligatorio para Pantra?** Founder solo + sub-procesadores. Tamaño debería excluir obligatoriedad por §38 BDSG, confirmar.
2. **Health data clasification**: los mensajes de pacientes pueden contener menciones casuales de síntomas. ¿Esto convierte a Pantra en "Verarbeiter besonderer Kategorien" (§9 DSGVO)? Si sí, requiere consentimiento explícito del paciente, lo cual choca con UX WhatsApp.
3. **Outreach §7 UWG**: planeamos outreach B2B a clínicas con email + carta + Xing InMail. La clínica es el target (Verantwortlicher futuro), no el paciente. ¿"Berechtigtes Interesse" es suficiente sin opt-in previo?
4. **DSGVO opt-out wording**: ¿el wording que tenemos en el footer del email outreach es suficiente?
   ```
   "Sie erhalten diese Nachricht, weil Pantra Sie als Zahnarztpraxis in
   Berlin identifiziert hat, die von unserem Service profitieren könnte
   (berechtigtes Interesse, §7 UWG). Falls Sie keine weiteren Nachrichten
   wünschen, antworten Sie mit 'STOP' oder schreiben Sie an
   renato@pantra.de."
   ```
5. **Audit rights de la clínica**: ¿es razonable cobrar un fee si la clínica pide auditoría más de 1× año? ¿Standard en mercado?
6. **Data breach notification**: ¿24h es estándar o las clínicas piden 12h?
7. **Haftungsbegrenzung**: límite razonable para SaaS B2B en Alemania para clínicas (mensual fee × 12? × 24?)
8. **Cláusula de ajuste 8% anual**: ¿es enforceable en B2B alemán? ¿Mejor formulación?
9. **Drittlandtransfer**: ¿necesitamos TIA (Transfer Impact Assessment) por proveedor (Anthropic, OpenAI, etc.) o EU SCC + DPF basta?
10. **Versicherung**: ¿tu firma trabaja con corredor de seguros para D&O / Cyber Insurance que necesitemos para vender a healthcare?

---

## Anexo A — Glosario de términos técnicos (DE)

| Alemán | Español | Definición |
|--------|---------|------------|
| AVV (Auftragsverarbeitungsvertrag) | Contrato de procesamiento de datos | Equivalente al DPA (Data Processing Agreement). Obligatorio §28 DSGVO. |
| Verantwortlicher | Responsable del tratamiento | La clínica dental |
| Auftragsverarbeiter | Encargado del tratamiento | Pantra |
| Subunternehmer / Subprocessor | Sub-procesador | Anthropic, AWS, etc. |
| Betroffene | Afectado | El paciente |
| Personenbezogene Daten | Datos personales | Nombres, teléfonos, mensajes, etc. |
| TOMs (Technische und organisatorische Maßnahmen) | Medidas técnicas y organizativas | Anhang 2 del AVV |
| BDSG | Ley federal alemana de protección de datos | Complemento al DSGVO |
| Datenschutzerklärung | Política de privacidad | Documento en `/datenschutz` |
| Impressum | Pie legal | Documento en `/impressum`, obligatorio §5 TMG |
| Drittlandübermittlung | Transferencia a tercer país | USA, UK, etc. |
| EU SCC | Cláusulas contractuales tipo UE | Mecanismo legal Art. 46 DSGVO |
| DPF (Data Privacy Framework) | Marco UE-EE.UU. de privacidad | Aprobado octubre 2024 |
| §7 UWG | Artículo 7 Ley contra Competencia Desleal | Permite outreach B2B con interés legítimo |
| Aufbewahrungsfristen | Plazos de retención | Legal vs. técnico |
| KZBV / BZÄK | Asociaciones dentales alemanas | Reglamentos sectoriales |
| ePA (elektronische Patientenakte) | Historia clínica electrónica | Mandato 1 enero 2026 — Pantra NO maneja ePA |

---

## Anexo B — Información de la entity legal (LLENAR antes de mandar)

```
Razón social:           ____________________________________________
Forma legal:            [ ] Einzelunternehmer  [ ] GmbH  [ ] UG  [ ] otro: ________
Dirección legal:        ____________________________________________
Email contacto:         renato@pantra.de (placeholder, confirmar)
Teléfono:               ____________________________________________
Steuernummer:           ____________________________________________
USt-IdNr (si aplica):   ____________________________________________
Handelsregister No.:    ____________________________________________
Geschäftsführer/Inhaber: Renato Lagos
DPO (si nombrado):      ____________________________________________
```

---

## Anexo C — Lista de documentos que el abogado debe entregar

1. **AVV Pantra ↔ Zahnarztpraxis** (PDF firmable, ~10-15 páginas)
   - Cuerpo principal en alemán (legal binding)
   - Anhang 1: Datenkategorien + Verarbeitungszweck
   - Anhang 2: TOMs
   - Anhang 3: Subunternehmerliste
2. **Datenschutzerklärung** para web (Markdown o HTML, mostrable en `/datenschutz`)
3. **Impressum** para web (Markdown o HTML, mostrable en `/impressum`)
4. **AGB** opcional (Markdown o HTML, mostrable en `/agb`)
5. **Revisión §7 UWG opt-out wording** (ya escrito por nosotros, validar)

---

## Anexo D — Email al abogado (LISTO PARA COPIAR Y MANDAR)

> Usar este email como primer contacto. Adjuntar este documento como PDF.

```
Subject: Erstanfrage — AVV + Datenschutzerklärung für SaaS Healthcare-Startup

Sehr geehrte Damen und Herren,

mein Name ist Renato Lagos. Ich gründe Pantra, einen KI-WhatsApp-
Assistenten speziell für Zahnarztpraxen in Berlin (B2B SaaS, Solo Plus
€349/Monat). Wir starten in den nächsten Wochen und benötigen vor dem
ersten zahlenden Kunden:

1. AVV (Auftragsverarbeitungsvertrag) — unterschriftsbereites PDF, das
   jede Zahnarztpraxis als Kunde unterschreibt, bevor Pantra Patient:
   innendaten verarbeitet.

2. Datenschutzerklärung für unsere Website (pantra.de/datenschutz).

3. Impressum (pantra.de/impressum).

4. AGB (optional, aber empfohlen).

5. Rechtliche Validierung unseres §7-UWG-Opt-out-Wordings für B2B-Outreach
   per E-Mail an Berliner Zahnarztpraxen.

Im Anhang finden Sie ein detailliertes technisches Briefing mit:
  • Beschreibung des Produkts und der verarbeiteten Datenkategorien
  • Vollständige Liste der Subunternehmer (Anthropic, AWS Frankfurt, OpenAI,
    Meta WhatsApp, Resend, ElevenLabs, Telegram, Google Calendar)
  • Implementierte technische und organisatorische Maßnahmen (TOMs)
  • Spezifische Fragen, die wir gerne im Erstgespräch klären würden

Drei Punkte, die ich besonders gerne mit Ihnen besprechen würde:

A) Müssen wir einen DSB (Datenschutzbeauftragten) formal bestellen, oder
   reicht ein interner Verantwortlicher? (Aktuell: Solo-Founder, keine
   Mitarbeiter, hosted in Frankfurt eu-central-1.)

B) Gelten Patient:innennachrichten, die zufällig gesundheitsbezogene
   Hinweise enthalten (z. B. "Mein Zahn tut weh"), bereits als "besondere
   Kategorien personenbezogener Daten" gemäß Art. 9 DSGVO? Oder reicht die
   Verarbeitung im Rahmen der Behandlungs-/Praxiskommunikation aus?

C) Drittlandtransfer USA: AWS Frankfurt deckt die Hauptverarbeitung ab,
   aber Anthropic (LLM), OpenAI (Whisper STT) und ElevenLabs (TTS) sind
   in den USA. Wir nutzen jeweils EU SCC + Anthropic ist im EU-US Data
   Privacy Framework zertifiziert. Ist das ausreichend, oder benötigen
   wir individuelle TIAs?

Können wir einen Termin für einen 30-minütigen Erstcall in den nächsten
zwei Wochen finden? Ein grober Kostenvoranschlag wäre für die
Geschäftsplanung sehr hilfreich.

Mit freundlichen Grüßen,
Renato Lagos
Gründer, Pantra
{telefon}
renato@pantra.de
```

---

## 11. Notas finales para el founder

1. **No firmes nada hasta que el abogado revise**. El AVV es contrato vinculante; un error de redacción te puede costar €€ en disputas futuras.

2. **Buscá un abogado especializado en IT-Recht + Healthcare**. NO un abogado generalista. Costo es similar (€200-300/hora) pero la calidad del output cambia drásticamente.

3. **Recomendaciones de firmas alemanas especializadas**:
   - **Schalast** (Frankfurt) — IT-Recht + Healthcare strong
   - **Heuking Kühn Lüer Wojtek** (Berlin office) — DSGVO específico
   - **GvW Graf von Westphalen** — startups + tech
   - **eRecht24** (online + más barato, ~€500-1.500 todo-en-uno) — para Datenschutzerklärung y Impressum standard, NO para AVV custom
   - **Schürmann Rosenthal Dreyer** (Berlin) — startup-friendly

4. **Timeline realista**: 1-3 semanas desde primera consulta hasta AVV firmado. Si te dicen 1 semana, probablemente están copiando templates. Si te dicen 2 meses, son demasiado lentos.

5. **Costo razonable esperado**:
   - eRecht24 todo-en-uno: €500-1.500 (templates customizados)
   - Abogado especializado custom: €1.500-3.000 (better quality, defensible)
   - Retainer mensual ongoing: €100-250

6. **El AVV se firma 1× con cada clínica**. No es por venta — es por relación. Vos firmás una vez como Pantra, la clínica lo tiene archivado, listo para auditoría.

7. **Cuando llegue el AVV firmado, subilo a `/static/legal/avv.pdf`** y descomentá el link de descarga en la landing.

---

## 12. Próximos pasos después de tener el AVV

1. **Subir AVV PDF** a `/static/legal/avv.pdf`
2. **Implementar páginas legales** (`/datenschutz`, `/impressum`, `/agb`) en FastAPI/Jinja siguiendo el design system Duna
3. **Update landing**: descomentar links de footer al AVV y privacy policy
4. **Self-hostear Manrope** woff2 en `/static/landing/fonts` (DSGVO-clean, sin Google Fonts CDN)
5. **Configurar Plausible analytics** (DSGVO-friendly, sin cookie banner)
6. **Email opt-out workflow** — endpoint `/api/unsubscribe?token=...` para responder al "STOP" en outreach
7. **Endpoint admin de Right-to-Erasure** para que la clínica pueda borrar pacientes a request

Eso desbloquea: poder vender legalmente + publicar la landing + arrancar outbound.
