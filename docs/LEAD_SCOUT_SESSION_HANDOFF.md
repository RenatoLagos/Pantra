# Pantra Lead Scout — Session Handoff Prompt

Pegá este prompt **completo** como primer mensaje en una nueva sesión de
Claude Code abierta en `/home/rune/projects/Pantra_Leads/`.

La sesión nueva no tiene contexto de la sesión Pantra principal — todo lo
que necesite, lo recupera vía **engram** (memoria persistente cross-session)
o se lo provee este prompt.

## Cuándo usar este prompt

- Cuando estés listo para producir la lista priorizada de ~400-500
  clínicas digital-native en Berlin para arrancar outreach.
- Cuando necesites refrescar la enrichment data (web, Instagram,
  reviews) sobre un batch nuevo.

## Cómo usarlo

1. Abrí una nueva terminal o pane.
2. `cd /home/rune/projects/Pantra_Leads/`
3. Iniciá Claude Code en esa carpeta.
4. Pegá el prompt de la sección siguiente como primer mensaje.

---

## EL PROMPT (copiar todo lo que está entre las líneas)

---

Estás continuando trabajo en **Pantra Lead Scout** — un pipeline de
inteligencia de leads B2B para clínicas dentales en Berlin. Esta es una
sesión NUEVA: el founder está trabajando en el producto Pantra principal
en una sesión separada (en `/home/rune/projects/Pantra/`), y te spawnea
acá para avanzar el scoring de leads en paralelo.

## ACCIÓN CRÍTICA #1 — recuperar contexto antes de tocar nada

Llamá estas tools de engram **en paralelo** ANTES de cualquier otra cosa.
Lee los resultados con cuidado, contienen las decisiones estratégicas que
no debés rehacer:

```
mem_context(limit=30)
mem_search("Pantra Lead Scout MVP")
mem_search("ICP digital-natives Berlin dental clinics")
mem_search("Pantra pricing v4 Solo Plus")
mem_search("Pantra business plan 6 meses")
mem_search("outbound híbrido digital-native dentistas")
```

Lo que vas a encontrar:
- Pricing v4 confirmado (Solo €149 / Solo Plus €349 + idiomas extra €39)
- Business plan 6 meses con target €10K MRR
- ICP filters digital-natives <40 años en Berlin
- Estado del MVP de Lead Scout (offline, SQLite, ~300 clínicas ya scrapeadas)
- Estrategia GTM (outbound híbrido + 3 design partners gratis primero)

**No rehagas estrategia. Alinéate a lo que ya está decidido.**

## TU OBJETIVO

Producir una **lista priorizada y scoreada de ~400-500 clínicas dentales
digital-native en Berlin** que Pantra puede targetear para outbound.

Output esperado: CSV o JSON con los fields listados más abajo, listo para
que la sesión Pantra principal lo consuma.

## RESTRICCIONES DURAS

- **Working directory: `/home/rune/projects/Pantra_Leads/` — NUNCA toques
  `/home/rune/projects/Pantra/`.** Ese es territorio de la otra sesión.
- El MVP de Pantra Lead Scout YA EXISTE. Leé lo que hay (`README.md`,
  schema SQLite, dashboard, source data en `data/raw/`) ANTES de proponer
  código nuevo.
- Reusá el pipeline existente; extendé, no reconstruyas.
- Founder solo — mantené complejidad baja. SQLite alcanza. Cron jobs
  alcanzan. No Kubernetes ni microservicios.
- El founder habla inglés solamente; tiene un amigo alemán que valida
  copy en alemán antes de mandar nada.

## ICP FILTERS — Digital-natives, Berlin

Scoreá cada clínica con esta rúbrica (composite 0-100):

| Señal | Weight | Cómo detectar |
|-------|--------|--------------|
| Web moderna post-2020 | Alta | Stack Tailwind/Next.js, schema.org, fotografía pro, responsive |
| Instagram activo | Alta | >300 followers, posts en últimas 2 semanas, equipo joven |
| Online booking ya implementado | Alta | Doctolib, Jameda Premium, Google Reservas, Cal.com embedded |
| Reviews mencionan "modern/young/digital" | Media | NLP sobre Google Reviews |
| Practice founded post-2018 | Media | handelsregister.de o "Über uns" en su web |
| Owner LinkedIn activo (no zombie) | Media | Posts/comments propios, no solo perfil de fachada |
| Señales multilingüe (pacientes TR/AR/ES) | Alta | Reviews en idiomas no-DE, team con apellidos no-alemanes, demografía del barrio |
| Barrios target | Alta | Mitte, Friedrichshain, Prenzlauer Berg, Neukölln, Wedding, Kreuzberg |

Threshold tier 1 (outreach inmediato): score ≥70.
Threshold tier 2 (segundo batch): score 50-69.
Threshold tier 3 (descartar o reservar): <50.

## OUTPUT FIELDS POR CLÍNICA

```
clinic_name
address + neighborhood (Berlin Stadtteil)
website_url
phone
email
whatsapp_number (si visible públicamente)
instagram_handle
google_reviews_count
google_avg_rating
founded_year (estimación si no es exacto)
owner_name
owner_linkedin_url
detected_languages (lista: DE, EN, TR, AR, ES, ...)
suggested_extra_languages (para outreach: qué idiomas Pantra
                          le ayudarían a ESTA clínica específica)
icp_score (0-100)
icp_tier (1/2/3)
outreach_hook (1-2 oraciones en alemán para personalizar el outreach,
               ej: "Vi 3 reviews en turco esperando 2 días")
```

## PROTOCOLO ENGRAM (mandatorio, siempre activo)

Guardá proactivamente con `mem_save` cada vez que:
- Tomes una decisión de arquitectura/scoring/data source
- Descubras un gotcha en los datos (formato raro, fuente flaky, etc.)
- Establezcas una convención (naming, threshold, etc.)
- Resuelvas un bug (con root cause)

Usá `scope="project"` y `topic_key` como `pantra-leads/scoring-rubric`,
`pantra-leads/data-sources`, `pantra-leads/enrichment-pipeline`. Topics
distintos NO deben pisarse. Si no estás seguro del key, llamá
`mem_suggest_topic_key`.

**Antes de cerrar la sesión** llamá `mem_session_summary` con: Goal,
Discoveries, Accomplished, Next Steps, Relevant Files. Sin esto la
próxima sesión arranca a ciegas.

## TU PRIMERA ACCIÓN

1. Pull memory (los 6 `mem_search` de arriba en paralelo).
2. `cat README.md && ls -la`
3. Inspeccionar el schema de la DB: `sqlite3 pantra_leads.db ".schema"`
4. Ver qué hay en `data/raw/`: `ls data/raw/ && head -3 data/raw/*.txt`
5. Inspeccionar el CLI: `pantra-leads --help` (o equivalente)
6. **Proponer un plan**: qué está hecho, qué falta para el ICP scoring,
   esfuerzo estimado. PARÁ y esperá confirmación del founder antes de
   tirar código.

Importante: NO arranques a codear sin que el founder confirme el plan.
Tenemos contexto compartido vía engram pero la dirección la marca él.

---

## FIN DEL PROMPT
