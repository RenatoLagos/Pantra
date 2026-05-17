# Pantra — Plan de Negocios 6 Meses

- **Status**: active — living document
- **Fecha de creación**: 2026-05-08
- **Autor**: Renato Lagos
- **Período cubierto**: mayo 2026 → octubre 2026
- **Hito principal**: alcanzar €10K MRR con 30-40 clientes pago en clínicas dentales digital-native de Berlin

---

## 0. Resumen Ejecutivo

Pantra es un asistente conversacional de IA multilingüe (DE/EN/ES/TR/AR/FR/RU/IT/PT) por WhatsApp para clínicas dentales en Berlin. Maneja booking, recordatorios, no-show recovery y handoff a humano sin requerir un dashboard administrativo.

**Tesis comercial**: el 70% de las clínicas dentales alemanas son Einzelpraxen. Berlin tiene ~2.500-2.800 clínicas con población 24% extranjera, lo que crea demanda real por un asistente que hable múltiples idiomas. Las clínicas digital-native (<40 años, fundadas post-2018) son nuestro ICP fase 1: deciden en 4-8 semanas vs los 6+ meses del mercado tradicional.

**Estrategia de 6 meses**:
1. Conseguir 3 design partners gratis en 30-45 días para tener testimonios alemanes
2. Construir compliance DSGVO + AVV firmable
3. Outbound híbrido (Lead Scout + outreach personalizado) sobre ~400 clínicas digital-native filtradas
4. Llegar a 30-40 clientes pago en mes 6 = €10K MRR

**Pricing**: Solo €149/mes (DE+EN) o Solo Plus €349/mes (DE+EN + 2 idiomas a elección + audio + integración PVS). Add-ons: idiomas extra +€39/mes.

**Riesgo principal**: el sales cycle alemán en healthcare (3-6 meses) y la necesidad de DSGVO/AVV antes del primer pago. Mitigación: target digital-native + 3 testimonios alemanes antes de escalar outbound.

---

## 1. Producto y Diferenciación

### 1.1 Qué es Pantra

Asistente conversacional de IA que atiende WhatsApp 24/7 en nombre de la clínica:

- Responde mensajes con tono natural humano (no chatbot rígido)
- Reserva turnos en Google Calendar / iCal / PVS
- Manda recordatorios automáticos (T-24h y T-2h vía templates aprobados)
- Detecta no-shows y reagenda automáticamente
- Triaja urgencias y deriva a humano cuando es necesario (Telegram + email)
- Maneja FAQs (horarios, dirección, tratamientos, precios, seguros)
- Procesa audio bidireccional (paciente graba voice note → transcribe → responde → opcionalmente devuelve audio)

### 1.2 Wedge competitivo (lo que NO tiene la competencia)

| Diferenciador | Por qué importa en Berlin |
|---------------|--------------------------|
| **Multilingüe nativo (8 idiomas)** | 24% de la población berlinesa tiene background extranjero. Ningún competidor ofrece TR+AR+ES nativo. |
| **Audio bidireccional** | Pacientes mayores y migrantes prefieren audio sobre texto. Killer feature. |
| **WhatsApp-first** | El canal donde YA viven las clínicas. Cero fricción de adopción. |
| **Vertical dental específico** | Prompts y workflows entrenados para Kontrolle/Reinigung/Füllung/Bleaching/Notfall. |
| **No requiere dashboard admin** | Setup en horas, no semanas. |

### 1.3 Comparación competitiva

| Competidor | Precio | Lengua | Audio | Vertical dental | WhatsApp |
|------------|--------|--------|-------|-----------------|----------|
| BotPenguin / Tars | €49-200 | EN/DE | ❌ | Genérico | ✓ |
| Videa / Overjet / Pearl | €800-3.000 | EN | ❌ | Sí (clínico) | ❌ |
| Doctolib | Setup +commission | DE | ❌ | Sí | Parcial |
| **Pantra** | **€149-349** | **8 idiomas** | **✓** | **Sí** | **✓** |

---

## 2. Mercado y Segmentación

### 2.1 TAM (Total Addressable Market)

- **Alemania total**: 37.527 clínicas dentales (CAGR -2.6% por consolidación DSO)
- **Berlin metro**: ~2.500-2.800 clínicas (densidad 848 hab/dentista, mayor a promedio nacional)
- **Industria total**: €37.000M anuales en Alemania
- **Umsatz promedio Einzelpraxis**: €677.000/año (KZBV 2025) → ~€56.400/mes

### 2.2 Segmentación de TAM Berlin por adoptabilidad

| Segmento | % del mercado | Cantidad estimada | ¿Pagarán €149-349? | Tiempo a primer pago |
|----------|--------------|-------------------|--------------------|--------------------|
| Dentistas <40, digital-native | ~25% | ~625 | Sí, fácil | 4-8 semanas |
| Dentistas 40-55, modernos | ~35% | ~875 | Sí, con prueba social | 8-16 semanas |
| Dentistas >55, tradicionales | ~30% | ~750 | Resistencia fuerte | 6+ meses o nunca |
| Adquiridos por DSO | ~10% | ~250 | El DSO decide | Vender a DSO directo |

### 2.3 ICP Fase 1 (próximos 6 meses): Digital-natives <40 años

**TAM direccionable real fase 1**: ~625 clínicas en Berlin metro

**Señales de detección (Lead Scout filtros)**:

| Señal | Detección automática |
|-------|---------------------|
| Web post-2020 | Stack moderno (Next.js, Tailwind), schema.org, fotos profesionales |
| Instagram activo | >300 followers, posts en últimas 2 semanas, equipo joven |
| Online booking ya implementado | Doctolib, Jameda Premium, Google Reservas |
| Reviews mencionan "modern/young/digital" | NLP sobre Google Reviews |
| Practice founded post-2018 | Datos de handelsregister.de |
| Owner LinkedIn activo | Posts/comments propios, no perfil zombie |
| Barrio target | Mitte, Friedrichshain, Prenzlauer Berg, Neukölln, Wedding, Kreuzberg |

### 2.4 ICP Fase 2 (mes 6+): expansión

- **Gemeinschaftspraxen** (15-20% del mercado, 2-4 dentistas) → tier "Multi" cuando lo pidan
- **DSO chains** (10-15%, zahneins, EVI Dental, dentolution, MEDI+, dent.SOS, Acura) → tier "Enterprise" via venta C-level por LinkedIn

---

## 3. Pricing y Unit Economics

### 3.1 Estructura de pricing v4 (final)

| Plan | Precio mensual | Setup | Para quién |
|------|---------------|-------|-----------|
| **Solo** | €149/mes | €199 one-time | Einzelpraxis tradicional, ~150 conv/mes, DE+EN solamente |
| **Solo Plus** | €349/mes | €399 one-time | Einzelpraxis moderna, ~500 conv/mes, DE+EN + 2 idiomas a elección |
| Idioma extra | +€39/mes | — | 3er, 4to idioma (TR/AR/ES/FR/RU/IT/PT) |
| Onboarding presencial | +€199 one-time | — | Opcional, alta conversión |

### 3.2 Reglas de pricing no negociables

- **Hard limits**: Solo 600 conv/mes, Solo Plus 2.000 conv/mes
- **Excedente**: €0.15 por conversación adicional
- **Anual prepago**: 2 meses gratis (paga 10 recibe 12) — locks-in pricing antes de subidas futuras
- **Cláusula de ajuste**: hasta 8% anual con 60 días aviso (cláusula contractual estándar)
- **Setup fee siempre se cobra**: filtra compromiso, paga el primer mes de costos, separa de chatbots de €49

### 3.3 Costos por cliente (Solo Plus referencial)

Modelo por conversación típica (5-8 mensajes, 1 audio, multilingüe):

| Componente | Costo unitario |
|------------|---------------|
| Claude Sonnet 4.6 (con prompt caching 10%) | ~€0.025/conv |
| Claude Haiku 4.5 (classifier) | ~€0.008/conv |
| Whisper STT | ~€0.003/audio |
| WhatsApp service msg (paciente-iniciado) | €0 |
| **Subtotal LLM por conv** | **~€0.04** |

**Costo mensual marginal por cliente Solo Plus** (~600 conv + recordatorios):

| Componente | Costo |
|------------|-------|
| LLM (600 conv × €0.04) | €24 |
| WhatsApp utility templates (1.000 reminders × €0.045) | €45 |
| Audio (~50 audios × €0.003) | €1 |
| Infra fija prorrateada (Postgres, Redis, hosting, monitoring) | ~€10 |
| **Total marginal** | **~€80/cliente/mes** |

**Gross Margin Solo Plus**: (€349 - €80) / €349 = **77%**

### 3.4 Buffer estratégico ya incorporado

El precio €349 (vs €299 inicial) absorbe:
- +30-40% costo efectivo por tokenizer changes (Anthropic Opus 4.7 ya genera +35% tokens)
- +10-20% potencial subida WhatsApp templates DACH
- Reasoning models si los necesitamos (50-100% más caros)

Se proyecta **GM se mantiene entre 70-80%** durante los próximos 18-24 meses incluso con cost drift moderado.

### 3.5 Math para €10K MRR

**Mix realista (recomendado)**:

| Tier | Cantidad | MRR contribución |
|------|---------|------------------|
| Solo (€149) | 8 | €1.192 |
| Solo Plus (€349) | 25 | €8.725 |
| Idiomas extra (€39 promedio 1.3/cliente) | ~8 idiomas | €312 |
| **Total** | **33 clientes pago** | **€10.229 MRR** |

**Mix alternativo (más simple, anual prepago)**:
- 30 Solo Plus anuales prepagos (€349 × 12 - 2 meses gratis = €3.490/año/cliente)
- ARR: €104.700, MRR equivalente: €8.725
- + 5 mensuales Solo Plus = +€1.745
- Total: €10.470 MRR

---

## 4. Go-to-Market Strategy

Tres vectores complementarios. Por ahora el #1 es la prioridad porque es el más rápido a primer revenue. Los otros dos arrancan a mes 3-4.

### 4.1 Vector #1 — Outbound híbrido + Lead Scout (PRIMARIO)

**Tesis**: tu unfair advantage es Pantra Lead Scout. Ya tenés enrichment de 300+ clínicas Berlin. Esto es oro y nadie más lo tiene.

**Mecánica**:

1. Lead Scout genera lista priorizada de clínicas digital-native con scoring por:
   - Probabilidad de necesitar multilingüe (idiomas en web, reviews, equipo)
   - Volumen estimado de mensajes (online booking, hours visible, tamaño)
   - Adoptabilidad tech (modernidad de web, presencia digital)
2. Personalización forense por clínica (no AI mass-blast):
   - "Vi en tus reviews 3 menciones de pacientes turcos esperando 2 días"
   - "Tu Instagram tiene 800 followers, Pantra te ayuda a no perder los DMs del fin de semana"
3. Canal de contacto **NO es WhatsApp** (Meta cobra €0.11-0.14/marketing msg en DE = veneno). Usar:
   - **Email principal** a info@praxis-X.de o al owner si está identificado
   - **Carta física certificada** al Inhaber (señal de seriedad alemana, €3 por carta)
   - **Xing InMail** (22% mejor response rate B2B regional vs LinkedIn en DACH)
   - **LinkedIn** SOLO para C-level de DSO chains (segmento enterprise futuro)
4. **Hybrid AI+human**: research/draft con AI, último toque humano (38% mayor revenue growth vs full-auto, +25% reply rate vs blast genérico)

**Targets de conversion (industria 2026 vertical SaaS healthcare)**:

```
Cold outbound → respuesta:        15% (con Lead Scout personalización)
Respuesta → demo agendado:         30%
Demo → trial activado:             50%
Trial → paid:                      25%
─────────────────────────────────────
Cold → cliente pago:               0.56%
```

Para cerrar 30 clientes pago netos = ~5.300 contactos cold. Berlin TAM digital-native (~625) es insuficiente solo, hay que expandir a Hamburg + München o subir conversion (testimonios alemanes son la palanca).

### 4.2 Vector #2 — Community-led (Berlin dental network)

**Tesis**: los dentistas se conocen TODOS entre ellos. Una clínica feliz trae 5 referencias.

**Tácticas**:
- Penetrar **Zahnärztekammer Berlin** y **KZV Berlin** — gatekeepers institucionales
- Sponsoreo de eventos pequeños / Stammtische dentales (Berlin tiene 8-10 al año)
- Contenido en alemán: blog SEO ("WhatsApp Assistent für Zahnarztpraxis Berlin"), LinkedIn del founder + amigo alemán
- **3 design partners gratis** = 3 evangelistas internos del gremio
- Listing en **medondo**, **Quintessenz**, otros directorios dentales DACH
- **Aprovechar mandato ePA enero 2026**: las clínicas están en crisis de compliance, Pantra entra a la conversación con "te ayudo a digitalizar la atención al paciente, no solo el expediente"

**Timeline**: arranque mes 3, resultados visibles mes 5-6. Es plazo más largo pero compuesto.

### 4.3 Vector #3 — PLG con "Pantra Weekend" (mes 4+)

**Tesis**: PLG = 3-5x menor CAC para SMB. Pero requiere infraestructura de billing + onboarding self-service que aún no tenés.

**Mecánica** (cuando esté listo):
- Free trial 72hs, viernes a domingo, cero configuración
- Lunes el dueño ve: "23 mensajes atendidos, 7 turnos reservados, 0 quejas" → wow moment
- Funnel: free → starter mensual → upgrade

**Por qué se difiere a mes 4+**:
- Requiere Stripe + métered billing implementado
- Requiere onboarding self-service maduro
- Requiere métricas de "patient saves" para mostrar ROI
- Foco fase 1 es validar pricing y conseguir testimonios, no escalar volumen

---

## 5. Roadmap 6 Meses

### Mes 1 (mayo 2026) — Fundación

**Objetivo**: dejar los rieles puestos para vender.

- [ ] Validar pricing v4 (esta semana)
- [ ] Contratar abogado alemán para AVV firmable + DSGVO compliance review (~€1.500-3.000 one-time)
- [ ] Implementar prompt caching agresivo en classifier + main LLM
- [ ] Implementar Haiku-first routing (classifier escala a Sonnet solo cuando es necesario)
- [ ] Definir scoring criteria de Lead Scout para digital-natives Berlin
- [ ] Generar lista priorizada de **top 50 clínicas digital-native Berlin** con enrichment completo
- [ ] Conversación con amigo alemán sobre rol formal (partner, advisor o customer success contractor)
- [ ] Spec de landing /einzelpraxis (entregable de esta sesión)

**Entregables fin de mes 1**:
- AVV en revisión legal
- Lead Scout output con 50 clínicas scored
- Arquitectura de costos LLM optimizada
- Landing /einzelpraxis en draft (copy + wireframe)

**MRR target mes 1**: €0 (fase de preparación)

### Mes 2 (junio 2026) — Primeros 3 design partners

**Objetivo**: cerrar 3 clínicas piloto gratis.

- [ ] Implementar landing /einzelpraxis (FastAPI + Jinja, integrado al stack existente)
- [ ] AVV firmado y publicado en /legal/avv
- [ ] Implementar hard limits + billing de excedente (Stripe metered)
- [ ] Outreach personalizado a top 30 clínicas digital-native con oferta:
  - 3 meses gratis Solo Plus + onboarding presencial
  - A cambio de: testimonio en video + caso de éxito documentado + permission para usar logo
- [ ] Cerrar **3 design partners** con AVV firmado y onboarding completado
- [ ] Crear página de casos de éxito (placeholder hasta tener data)

**Entregables fin de mes 2**:
- 3 clínicas usando Pantra activamente
- Landing pública con AVV
- Sistema de billing operativo

**MRR target mes 2**: €0 (design partners gratis)

### Mes 3 (julio 2026) — Primeros clientes pago

**Objetivo**: convertir design partners en testimonios + cerrar primeros clientes pago.

- [ ] Recolectar testimonios + métricas de los 3 design partners (turnos reservados, no-shows reducidos, mensajes atendidos)
- [ ] Producir 3 case studies en alemán (con amigo alemán supervisando copy)
- [ ] Actualizar landing con social proof real
- [ ] Re-arrancar outbound con testimonios → expectativa: 5x mejora en reply rate
- [ ] Cerrar **5 clientes pago** (mix 1-2 Solo + 3-4 Solo Plus)
- [ ] Diseñar in-product upsell triggers (tooltips bloqueados, emails métricas)

**MRR target mes 3**: €1.500-2.000

### Mes 4 (agosto 2026) — Escala de outbound

**Objetivo**: validar funnel y duplicar base.

- [ ] Outbound a 200 clínicas adicionales (Berlin + expansión a Hamburg)
- [ ] Onboardar amigo alemán formalmente para sales calls + customer success
- [ ] Implementar el primer upsell trigger (tooltip "activar 3er idioma")
- [ ] Cerrar 7-10 clientes adicionales
- [ ] Iniciar contenido en LinkedIn (founder + amigo alemán) — thought leadership
- [ ] Iniciar penetración Zahnärztekammer Berlin (asistir a 1 evento)

**MRR target mes 4**: €4.000-5.000

### Mes 5 (septiembre 2026) — Aceleración

**Objetivo**: producirla ICP y empezar a generar inbound orgánico.

- [ ] Listing en medondo + Quintessenz + otros directorios DACH
- [ ] Iniciar SEO con 5-8 artículos en alemán
- [ ] Primer contacto outbound a 2-3 DSO chains (LinkedIn al C-level)
- [ ] Cerrar 10-12 clientes adicionales
- [ ] Lanzar plan anual prepago (descuento 2 meses)
- [ ] Considerar contratar primer SDR alemán part-time si pipeline lo justifica

**MRR target mes 5**: €7.000-8.000

### Mes 6 (octubre 2026) — €10K MRR

**Objetivo**: cerrar el hito y dejar el motor andando.

- [ ] 10-15 clientes adicionales para llegar a 30-40 totales
- [ ] Considerar tier Multi (Gemeinschaftspraxis €499) si hay demanda real
- [ ] Primer DSO en exploratorio activo (NDA firmado, demo a Head of Operations)
- [ ] Retrospectiva del semestre + plan de Fase 2 (mes 7-12)

**MRR target mes 6**: **€10.000+**

---

## 6. KPIs y Targets

### 6.1 KPIs primarios (north star)

| KPI | Mes 3 | Mes 6 | Mes 12 (proyectado) |
|-----|-------|-------|---------------------|
| **MRR** | €1.500-2.000 | €10.000 | €30.000-40.000 |
| **Clientes pago** | 5-7 | 30-40 | 90-120 |
| **Gross Margin** | 70%+ | 75%+ | 78%+ |
| **CAC** | <€500 (alto, founder-led) | <€350 | <€250 |
| **CAC Payback** | <6 meses | <4 meses | <3 meses |
| **Net Revenue Retention** | N/A | 100%+ | 115%+ |
| **Logo Churn mensual** | <5% | <3% | <2% |

### 6.2 KPIs operacionales (semanales)

- Outbound contactos enviados
- Reply rate (target: 15%+ con Lead Scout)
- Demos agendados
- Demos → trial activación rate
- Trial → paid conversion rate
- Tiempo medio de close (sales cycle)
- AVV firmados / pendientes

### 6.3 KPIs de producto (post-launch)

- Mensajes atendidos / cliente / mes (volumen)
- Turnos reservados / cliente / mes (valor entregado)
- No-show rate antes vs después de Pantra (KPI vendible)
- Tasa de handoff a humano (target: <15%)
- Tiempo medio de respuesta (target: <30s)
- Customer satisfaction (NPS post-mes-1)

---

## 7. Equipo y Recursos

### 7.1 Equipo actual

| Rol | Persona | Capacidad | Limitaciones |
|-----|---------|-----------|--------------|
| Founder técnico + producto + ventas EN | Renato Lagos | 100% tiempo | No habla alemán nativo |
| **Partner de ventas/CS alemán** (a confirmar) | Amigo alemán | TBD (parcial recomendado) | Pendiente conversación formal |

### 7.2 Roles a contratar/incorporar en 6 meses

| Rol | Cuándo | Modelo | Costo estimado |
|-----|--------|--------|---------------|
| Customer Success en alemán | Cuando lleguen 5+ clientes (mes 3-4) | Freelance 10-15h/sem | €500-800/mes |
| SDR alemán part-time | Mes 5+ si pipeline lo justifica | Comisión + base baja | €1.500-2.500/mes |
| Abogado alemán (AVV + compliance) | Mes 1 | One-time + retainer | €1.500-3.000 + €200/mes |
| Diseñador freelance (landing + casos) | Mes 1-2 | Project-based | €1.500-2.500 one-time |

### 7.3 Stack y herramientas operativas

| Categoría | Herramienta | Costo |
|-----------|------------|-------|
| Backend/infra | FastAPI, Postgres, Redis, hosting cloud | €100-300/mes |
| LLM | Anthropic API (Sonnet 4.6 + Haiku 4.5) | €200-1.000/mes (escala con clientes) |
| WhatsApp | Cloud API o 360dialog | Setup gratis + per-msg |
| Email | Resend o AWS SES | €20-50/mes |
| CRM lite | Notion o Airtable | €0-30/mes |
| Outbound tooling | Lemlist / Instantly | €100-200/mes |
| Analytics web | Plausible (DSGVO-friendly) | €9-19/mes |
| Calendario | Cal.com o Google Calendar | €0-15/mes |
| Pago | Stripe + SEPA Direct Debit | 1.4% + €0.25/transacción |

---

## 8. Costos Operativos Mensuales (proyección)

### 8.1 Mes 1-3 (fase de fundación)

| Categoría | Costo mensual |
|-----------|---------------|
| Infra (hosting, DB, Redis) | €100 |
| LLM (testing + 3 design partners) | €100 |
| WhatsApp templates | €50 |
| Email | €20 |
| Tooling (CRM, analytics, outbound) | €150 |
| Abogado (AVV one-time prorrateado) | €500 (3 meses) |
| **Total mes 1-3** | **~€920/mes** |
| One-time setup (legal + landing diseño) | €3.000-5.500 |

### 8.2 Mes 4-6 (fase de escala)

| Categoría | Costo mensual |
|-----------|---------------|
| Infra | €200 |
| LLM (escala con clientes) | €400-800 |
| WhatsApp | €200-400 |
| Customer Success freelance (alemán) | €600 |
| SDR (mes 5-6) | €1.500-2.500 |
| Tooling | €200 |
| Marketing (contenido, SEO, eventos) | €300-500 |
| **Total mes 4-6** | **~€3.400-5.200/mes** |

### 8.3 Cash flow mes a mes (proyección)

| Mes | Revenue | Costos | Cash Flow Mensual |
|-----|---------|--------|------------------|
| 1 | €0 | €920 | -€920 |
| 2 | €0 | €920 | -€920 |
| 3 | €1.750 | €1.500 | +€250 |
| 4 | €4.500 | €3.400 | +€1.100 |
| 5 | €7.500 | €4.500 | +€3.000 |
| 6 | €10.200 | €5.200 | +€5.000 |
| **Acumulado 6 meses** | **€23.950** | **€16.440** | **+€7.510** |

**+ Setup fees** (one-time, no incluidos en MRR): ~30 clientes × €399 promedio = +€12.000 adicionales
**+ Anual prepago bonus** (si se vende): cash adelantado adicional

**Cash a inyectar para arrancar**: ~€5.000-8.000 (cubre los primeros 3 meses + legal + diseño)

---

## 9. Riesgos y Mitigación

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|-----------|
| **Sales cycle alemán >6 meses bloquea revenue** | Alta | Alto | Foco digital-natives <40, 3 design partners gratis para social proof |
| **DSGVO/AVV bloquea ventas hasta tenerlo firmable** | Alta | Alto | Contratar abogado alemán mes 1 como prioridad #1 |
| **Founder no habla alemán** | Confirmada | Alto | Onboardar amigo alemán como partner/advisor o contratar CS freelance alemán mes 3 |
| **LLM cost drift (tokenizer changes Anthropic)** | Media | Medio | Buffer en pricing (€349 vs €299), prompt caching agresivo, hard limits |
| **WhatsApp Meta sube precios DACH** | Media | Medio | Limitar templates outbound, paciente-iniciado, fair use limits |
| **DSO consolidación reduce TAM SMB** | Media (a 24 meses) | Medio | Desarrollar tier Enterprise para vender al DSO directo |
| **Competidor establecido (Doctolib, Videa) lanza algo similar** | Baja-Media | Alto | Velocidad de niche dominance, multilingüe es moat estructural |
| **Trial → paid conversion <25%** | Media | Alto | Iterar onboarding, agregar onboarding asistido, bajar fricción de setup |
| **Churn temprano alto (<6 meses)** | Media | Alto | Focus en time-to-value (primer turno reservado en semana 1), monthly check-ins |

---

## 10. Próximos Pasos (próximos 14 días)

**Acciones inmediatas a confirmar/arrancar**:

1. **Validar pricing v4** (esta semana)
2. **Conversación formal con amigo alemán** sobre rol y compromiso
3. **Contactar abogado alemán** para cotización AVV + DSGVO review
4. **Implementar prompt caching agresivo** en el pipeline LLM (1-2 días dev)
5. **Implementar Haiku-first routing** en classifier (1 día dev)
6. **Spec de landing /einzelpraxis** (entregable de esta sesión — ver `LANDING_SPEC.md`)
7. **Definir filtros Lead Scout** para digital-natives Berlin
8. **Arrancar generación de top 50 lista** con scoring digital-native

**Decisiones pendientes que NO podemos diferir**:
- ¿Pricing v4 confirmado?
- ¿Amigo alemán partner o contractor?
- ¿Cuánto cash hay disponible para los primeros 3 meses (€5-8K objetivo)?

---

## Anexo A — Histórico de decisiones de pricing

| Versión | Fecha | Estructura | Por qué se cambió |
|---------|-------|-----------|-------------------|
| v0 (PROJECT_SPEC) | 2026-04-27 | Single tier €450 | Pricing arbitrario sin segmentación |
| v1 | 2026-05-08 | Starter €149 / Pro €399 / Enterprise €999 | Demasiados tiers para fundador solo, segmentación por tamaño confusa |
| v2 | 2026-05-08 | Solo €99 / Solo Plus €249 + idiomas €49 add-on | Foco en Einzelpraxis (70% del mercado), modulariza idiomas |
| v3 | 2026-05-08 | Solo €129 / Solo Plus €299 + bundle 2 idiomas | Bundle simplifica decisión, +€30 por psicología B2B alemana |
| **v4 (final)** | **2026-05-08** | **Solo €149 / Solo Plus €349 + leverage points** | **Buffer estratégico para LLM cost drift, fair use limits, anual prepago, cláusula ajuste 8%/año** |

---

## Anexo B — Math de unit economics detallada

### LTV estimado (Solo Plus)

- Precio mensual: €349
- Gross margin: 77% → contribución mensual €269
- Churn anual asumido: 25% (alto en early stage)
- LTV = €269 / 0.25/12 = **~€12.900 por cliente**

### CAC objetivo

- Founder-led con outbound: €300-500/cliente (tiempo + tooling)
- Con SDR mes 5+: €600-900/cliente (incluye base + comisión)
- Con referrals/community: €100-200/cliente (mucho menor)

### LTV/CAC ratio

- Mes 3-4: ~25-40x (founder-led, outbound puro)
- Mes 5-6: ~15-20x (con SDR)
- Target sano vertical SaaS 2026: >3x. Pantra está holgadamente arriba.

### Payback period

- Solo Plus: €349 - €80 cost = €269 contribution
- CAC €400 / €269 contribution = **1.5 meses payback** → excelente

---

## Anexo C — Referencias de mercado citadas

- KZBV Jahrbuch 2025 (Umsatz Einzelpraxis, densidad)
- Statista — Zahnarztpraxen Einnahmen 2023
- Destatis — Arztpraxen 2023 PD25_269_52911
- IBISWorld — Dental Practices Germany 2026
- Anthropic API pricing (mayo 2026)
- WhatsApp Business API Germany rates (Meta + BSP markup)
- Industria SaaS vertical 2026 — conversion benchmarks
