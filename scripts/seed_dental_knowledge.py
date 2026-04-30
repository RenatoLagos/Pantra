"""Populate the dental clinic knowledge base.

Loads ~50 FAQs (DE + EN), insurance/practical/safety/pricing entries, and
extends the existing 6 services with long-form treatment details
(details_long, pre_care, post_care, contraindications, insurance_notes).

Idempotent: re-running wipes the previous knowledge_entries for
`demo-dental` and re-creates them. Service rows are UPDATED in place.

Usage:
    python -m scripts.seed_dental_knowledge
"""
from __future__ import annotations

import asyncio

from sqlalchemy import delete, select

from pantra.db import session_scope
from pantra.models import Business, KnowledgeEntry, Service


# ─── FAQs (DE primary, EN translation) ──────────────────────────────────
# Each tuple: (category, [tags], title_de, body_de, title_en, body_en)
FAQS: list[tuple[str, list[str], str, str, str, str]] = [
    # ─── Booking ─────────────────────────────────────────────────
    ("faq", ["booking"],
     "Wie kann ich einen Termin buchen?",
     "Sie können Termine direkt über WhatsApp buchen, telefonisch unter +49 30 1234 5678 oder per E-Mail. Wir bestätigen Ihren Termin innerhalb weniger Minuten.",
     "How do I book an appointment?",
     "You can book directly via WhatsApp, by phone at +49 30 1234 5678, or by email. We confirm your appointment within minutes."),

    ("faq", ["booking"],
     "Wie weit im Voraus kann ich Termine buchen?",
     "Termine können bis zu 3 Monate im Voraus gebucht werden. Für Notfälle haben wir täglich Reservezeiten.",
     "How far in advance can I book?",
     "Appointments can be booked up to 3 months in advance. We hold daily reserve slots for emergencies."),

    ("faq", ["booking", "confirmation"],
     "Bekomme ich eine Terminbestätigung?",
     "Ja. Nach der Buchung erhalten Sie eine Bestätigung per WhatsApp oder E-Mail. 24 Stunden vor dem Termin schicken wir eine Erinnerung, 2 Stunden vorher noch eine letzte Nachricht.",
     "Will I get a confirmation?",
     "Yes. After booking you'll receive a confirmation by WhatsApp or email. We send a reminder 24h before the appointment and another 2h before."),

    ("faq", ["booking", "late"],
     "Was passiert, wenn ich zu spät komme?",
     "Bei Verspätungen unter 10 Minuten behandeln wir Sie meist noch im verkürzten Rahmen. Über 15 Minuten Verspätung müssen wir den Termin häufig verschieben — bitte rufen Sie uns an, wenn Sie merken, dass Sie zu spät kommen.",
     "What if I'm late?",
     "Up to 10 minutes late we'll usually still see you (shortened slot). More than 15 minutes late we often need to reschedule — please call ahead if you notice you'll be late."),

    ("faq", ["booking", "rescheduling"],
     "Wie kann ich einen Termin verschieben?",
     "Schreiben Sie uns einfach per WhatsApp oder rufen Sie an. Solange genug Vorlauf da ist, finden wir kostenfrei einen neuen Termin.",
     "How do I reschedule?",
     "Just message us on WhatsApp or call. With enough advance notice we'll find a new slot at no charge."),

    # ─── Cancellation ────────────────────────────────────────────
    ("policy", ["cancellation"],
     "Wie kann ich einen Termin absagen?",
     "Sie können bis 24 Stunden vor dem Termin kostenfrei absagen — per WhatsApp, Telefon oder E-Mail. Bei späterer Absage berechnen wir 50 % des Behandlungspreises.",
     "How do I cancel?",
     "You can cancel free of charge up to 24 hours before the appointment — via WhatsApp, phone, or email. Later cancellations incur 50% of the treatment fee."),

    ("policy", ["cancellation", "no-show"],
     "Was passiert, wenn ich nicht erscheine?",
     "Bei unentschuldigtem Nichterscheinen erheben wir eine Pauschale von 50 €. Im Krankheitsfall mit ärztlichem Attest entfällt die Gebühr.",
     "What happens if I don't show up?",
     "Unexcused no-shows are charged a flat €50 fee. The fee is waived for medical emergencies with a doctor's note."),

    ("policy", ["cancellation", "fee"],
     "Was sind die Stornierungsgebühren?",
     "Bis 24 h vorher: kostenfrei. Innerhalb 24 h: 50 % des Behandlungspreises. Nichterscheinen: 50 € Pauschale.",
     "What are the cancellation fees?",
     "Up to 24h before: free. Within 24h: 50% of treatment price. No-show: €50 flat fee."),

    # ─── Insurance ───────────────────────────────────────────────
    ("insurance", ["insurance"],
     "Welche Versicherungen werden akzeptiert?",
     "Wir behandeln gesetzlich und privat versicherte Patienten. Auch Selbstzahler sind willkommen. Bei privaten Versicherungen rechnen wir nicht direkt ab — Sie reichen die Rechnung selbst bei Ihrer Versicherung ein.",
     "Which insurances do you accept?",
     "We treat statutory (Kasse) and private insurance patients, as well as self-pay. With private insurance, we don't bill directly — you submit the invoice to your insurer yourself."),

    ("insurance", ["insurance", "kasse"],
     "Was übernimmt die gesetzliche Krankenkasse?",
     "Die Kasse übernimmt regelmäßige Kontrollen, einfache Füllungen (mit Eigenanteil bei Composite), Wurzelbehandlungen bei erhaltungswürdigen Zähnen und Zahnersatz auf Festzuschuss-Basis. Bleaching, ästhetische Behandlungen und Implantate sind in der Regel Selbstzahler-Leistungen.",
     "What does statutory insurance cover?",
     "Statutory insurance covers regular check-ups, basic fillings (with co-pay for composite), root canals for teeth worth saving, and a fixed contribution toward dentures. Bleaching, cosmetic procedures, and implants are usually self-pay."),

    ("insurance", ["insurance", "private"],
     "Werden private Versicherungen direkt abgerechnet?",
     "Nein. Sie erhalten von uns eine Rechnung nach GOZ und reichen diese bei Ihrer privaten Krankenversicherung ein. Auf Wunsch erstellen wir vorab einen Heil- und Kostenplan.",
     "Do you bill private insurance directly?",
     "No. We provide a GOZ-based invoice that you submit to your private insurer. On request we prepare a treatment plan with cost estimate in advance."),

    ("insurance", ["insurance", "co-pay"],
     "Was bedeutet Eigenanteil?",
     "Der Eigenanteil ist der Betrag, den Sie selbst tragen, wenn die Krankenkasse nicht die volle Leistung übernimmt — z. B. bei höherwertigen Composite-Füllungen statt einfacher Amalgam-Füllungen oder bei Zahnersatz über die Festzuschüsse hinaus.",
     "What does 'Eigenanteil' (co-pay) mean?",
     "The co-pay is the amount you pay yourself when statutory insurance doesn't cover the full treatment — e.g. premium composite fillings instead of basic amalgam, or denture options beyond the fixed contribution."),

    ("insurance", ["insurance", "bleaching"],
     "Wird Bleaching von der Kasse übernommen?",
     "Nein. Bleaching ist eine ästhetische Leistung und wird nicht von der gesetzlichen Krankenkasse übernommen. Auch private Versicherungen erstatten Bleaching meistens nicht.",
     "Does insurance cover bleaching?",
     "No. Bleaching is a cosmetic service and is not covered by statutory insurance. Most private insurances also do not reimburse bleaching."),

    ("insurance", ["insurance", "cleaning"],
     "Übernimmt die Kasse die professionelle Zahnreinigung?",
     "Die meisten gesetzlichen Krankenkassen übernehmen 1× pro Jahr einen Zuschuss zur professionellen Zahnreinigung (PZR), oft 60–80 €. Den Rest tragen Sie selbst. Private Versicherungen erstatten in der Regel die volle PZR.",
     "Does insurance cover professional teeth cleaning?",
     "Most statutory insurers contribute once a year toward professional cleaning (PZR), typically €60–80. You pay the rest. Private insurers usually reimburse the full PZR cost."),

    # ─── Pricing (typical ranges) ────────────────────────────────
    ("pricing", ["pricing", "checkup"],
     "Was kostet eine Kontrolluntersuchung?",
     "Die regelmäßige Kontrolle ist für gesetzlich Versicherte kostenfrei. Selbstzahler zahlen ca. 50 €.",
     "How much does a check-up cost?",
     "Routine check-ups are free for statutory-insured patients. Self-pay rate: approx. €50."),

    ("pricing", ["pricing", "cleaning"],
     "Was kostet eine professionelle Zahnreinigung?",
     "Eine PZR kostet bei uns ca. 90 €. Mit Kassenzuschuss zahlen Sie meist 10–30 € selbst. Private Versicherungen erstatten in der Regel die volle Summe.",
     "How much is a professional cleaning?",
     "Our PZR (professional cleaning) costs approx. €90. With statutory insurance contribution you typically pay €10–30 out of pocket; private insurers usually reimburse the full amount."),

    ("pricing", ["pricing", "filling"],
     "Was kostet eine Füllung?",
     "Eine Composite-Füllung kostet ab ca. 120 €, je nach Größe und Position des Zahns. Amalgam-Füllungen werden von der Kasse voll übernommen, bieten wir aber nicht mehr aktiv an.",
     "How much is a filling?",
     "A composite filling starts at approx. €120, depending on size and tooth position. Amalgam is fully covered by statutory insurance but we no longer actively offer it."),

    ("pricing", ["pricing", "implant"],
     "Was kostet ein Implantat?",
     "Ein einzelnes Zahnimplantat kostet inklusive Krone ca. 1.800–2.800 €, je nach Komplexität. Bei der Erstberatung erstellen wir einen detaillierten Kostenplan.",
     "How much is a dental implant?",
     "A single dental implant including crown costs approx. €1,800–2,800, depending on complexity. We prepare a detailed cost plan at the initial consultation."),

    ("pricing", ["pricing", "bleaching"],
     "Was kostet Bleaching?",
     "Professionelles In-Office-Bleaching kostet 350 € pro Sitzung. Home-Bleaching mit individuellen Schienen ca. 280 €.",
     "How much is bleaching?",
     "In-office professional bleaching costs €350 per session. Home bleaching with custom trays approx. €280."),

    ("pricing", ["pricing", "endodontics"],
     "Was kostet eine Wurzelbehandlung?",
     "Bei erhaltungswürdigen Zähnen übernimmt die Kasse die Grundleistung. Hochwertige Wurzelbehandlung mit Mikroskop und modernen Materialien: 240–600 € Eigenanteil, je nach Zahn.",
     "How much is a root canal?",
     "Statutory insurance covers basic treatment for teeth worth saving. Premium root canal with microscope and modern materials: €240–600 co-pay depending on tooth."),

    # ─── Treatments — pain, anxiety, recovery ─────────────────────
    ("faq", ["treatment", "pain"],
     "Tut die Behandlung weh?",
     "Die meisten Behandlungen führen wir unter lokaler Anästhesie durch. Schmerzen während der Behandlung sind selten. Bei Implantaten und Wurzelbehandlungen kann es nach der Behandlung etwas drücken — wir geben Ihnen Schmerzmittel-Empfehlungen mit.",
     "Will it hurt?",
     "Most treatments are done under local anesthesia. Pain during the treatment is rare. After implants or root canals there may be some pressure for a day or two — we'll recommend pain medication."),

    ("faq", ["treatment", "anxiety"],
     "Was tun bei Zahnarztangst?",
     "Wir nehmen uns Zeit. Sagen Sie uns vorher, dass Sie Angst haben — wir erklären jeden Schritt. Bei stärkerer Angst bieten wir Lachgas-Sedierung an. Für sehr ängstliche Patienten ist auf Wunsch auch Dämmerschlaf möglich (über einen kooperierenden Anästhesisten).",
     "What if I'm afraid of the dentist?",
     "We take our time. Let us know in advance that you're anxious — we'll explain every step. For stronger anxiety we offer nitrous oxide sedation. For very anxious patients, twilight sleep is available on request (via a partner anesthesiologist)."),

    ("faq", ["treatment", "anesthesia"],
     "Bekomme ich eine Spritze?",
     "Bei den meisten Behandlungen außer Kontrolle und Reinigung verwenden wir lokale Anästhesie. Die Einstichstelle wird vorher betäubt, sodass die Spritze selbst kaum spürbar ist.",
     "Will I get a shot?",
     "For most treatments other than check-ups and cleanings we use local anesthesia. We numb the injection site first so the shot itself is barely noticeable."),

    ("faq", ["treatment", "after"],
     "Kann ich nach der Behandlung Auto fahren?",
     "Nach lokaler Anästhesie ja, sobald die Taubheit nachlässt. Nach Lachgas dürfen Sie nach 30 Minuten wieder fahren. Nach Dämmerschlaf dürfen Sie 24 Stunden lang weder Auto fahren noch wichtige Entscheidungen treffen — bitte lassen Sie sich abholen.",
     "Can I drive after treatment?",
     "After local anesthesia, yes — once numbness wears off. After nitrous oxide, you can drive after 30 minutes. After twilight sedation, no driving and no important decisions for 24h — please arrange a ride."),

    ("faq", ["treatment", "frequency"],
     "Wie oft sollte ich zur Kontrolle kommen?",
     "Wir empfehlen alle 6 Monate eine Kontrolle und 1–2× jährlich eine professionelle Zahnreinigung. Bei Risikofaktoren (Parodontitis, Implantate) öfter.",
     "How often should I come for a check-up?",
     "We recommend a check-up every 6 months and a professional cleaning 1–2 times a year. More often if you have risk factors (periodontitis, implants)."),

    # ─── Implants ────────────────────────────────────────────────
    ("treatment_detail", ["implant"],
     "Wie läuft eine Implantatbehandlung ab?",
     "1. Erstberatung mit 3D-Röntgen und Kostenplan. 2. Einsetzen des Implantats unter lokaler Anästhesie (ca. 60 min). 3. Einheilphase 3–6 Monate. 4. Aufsetzen der Krone in einem zweiten Termin. Die meisten Patienten kehren nach 1–2 Tagen zur Arbeit zurück.",
     "How does an implant procedure work?",
     "1. Initial consultation with 3D X-ray and cost plan. 2. Implant placement under local anesthesia (~60 min). 3. Healing period 3–6 months. 4. Crown placement at a second appointment. Most patients return to work after 1–2 days."),

    ("treatment_detail", ["implant", "longevity"],
     "Wie lange hält ein Implantat?",
     "Bei guter Pflege halten moderne Titan-Implantate 20+ Jahre — viele halten lebenslang. Entscheidend sind regelmäßige Kontrollen, professionelle Reinigung und gute Mundhygiene zu Hause.",
     "How long do implants last?",
     "With good care, modern titanium implants last 20+ years — many last a lifetime. Key factors: regular check-ups, professional cleaning, and good home oral hygiene."),

    # ─── Endodontics ─────────────────────────────────────────────
    ("treatment_detail", ["endodontics"],
     "Wie funktioniert eine Wurzelbehandlung?",
     "Bei einer Wurzelbehandlung entfernen wir entzündetes Gewebe aus dem Zahninneren, reinigen und desinfizieren die Wurzelkanäle und füllen sie luftdicht. Wir arbeiten mit Mikroskop und elektronischer Längenmessung. Meist 1–2 Sitzungen à 60 min.",
     "How does a root canal work?",
     "In a root canal we remove inflamed tissue from inside the tooth, clean and disinfect the root canals, and fill them airtight. We use a microscope and electronic length measurement. Usually 1–2 sessions of 60 min."),

    # ─── Bleaching ───────────────────────────────────────────────
    ("treatment_detail", ["bleaching"],
     "Wie funktioniert Bleaching?",
     "Beim In-Office-Bleaching tragen wir ein hochkonzentriertes Gel auf Ihre Zähne auf, das mit einer speziellen Lampe aktiviert wird. Eine Sitzung dauert ca. 90 min und hellt die Zähne meist um mehrere Stufen auf. Beim Home-Bleaching erhalten Sie Schienen mit niedriger dosiertem Gel zum Tragen über 1–2 Wochen.",
     "How does bleaching work?",
     "In-office bleaching applies a high-concentration gel activated by a special lamp. One session takes ~90 min and lightens teeth several shades. Home bleaching uses custom trays with lower-dose gel worn over 1–2 weeks."),

    ("faq", ["bleaching", "safety"],
     "Ist Bleaching schädlich für die Zähne?",
     "Bei professioneller Anwendung ist Bleaching sicher. Vorübergehend können die Zähne empfindlicher sein. Wir prüfen vorher, ob Ihre Zähne und Zahnfleisch geeignet sind.",
     "Is bleaching harmful?",
     "When done professionally, bleaching is safe. Teeth may be temporarily more sensitive. We check beforehand whether your teeth and gums are suitable."),

    # ─── Emergencies ─────────────────────────────────────────────
    ("faq", ["emergency", "pain"],
     "Was tun bei akuten Zahnschmerzen?",
     "Rufen Sie uns sofort an — +49 30 1234 5678. Wir versuchen, Sie noch am gleichen Tag zu sehen. Bis dahin: ein kühlender Wickel von außen, Ibuprofen 400 mg (wenn keine Kontraindikation), nicht auf der schmerzenden Seite kauen.",
     "What to do for acute toothache?",
     "Call us immediately — +49 30 1234 5678. We try to see you the same day. Until then: cold compress on the outside, ibuprofen 400 mg (if no contraindications), don't chew on the painful side."),

    ("faq", ["emergency", "after-hours"],
     "Was tun außerhalb der Öffnungszeiten?",
     "Bei zahnärztlichen Notfällen außerhalb unserer Öffnungszeiten wenden Sie sich an den zahnärztlichen Notdienst Berlin (Tel. 030 89 00 43 33) oder fahren Sie zur Charité-Notaufnahme.",
     "What to do outside opening hours?",
     "For dental emergencies outside our hours, contact the Berlin dental emergency service (tel. 030 89 00 43 33) or go to the Charité emergency room."),

    ("faq", ["emergency", "trauma"],
     "Wie verhalte ich mich bei einem ausgeschlagenen Zahn?",
     "Den Zahn nur an der Krone anfassen, nicht an der Wurzel. In H-Milch oder einer Zahnrettungsbox aufbewahren. Innerhalb 30 Minuten zum Zahnarzt — die Chancen, den Zahn zu retten, sind in der ersten Stunde am besten.",
     "What if a tooth gets knocked out?",
     "Hold the tooth only by the crown, not the root. Store it in long-life milk or a tooth rescue box. See a dentist within 30 minutes — chances of saving the tooth are best in the first hour."),

    # ─── Practical ───────────────────────────────────────────────
    ("practical", ["address", "location"],
     "Wo befindet sich die Praxis?",
     "Friedrichstraße 100, 10117 Berlin. Direkt am S-Bahnhof Friedrichstraße, etwa 5 Minuten zu Fuß vom Bundestag.",
     "Where is the practice located?",
     "Friedrichstraße 100, 10117 Berlin. Right at Friedrichstraße S-Bahn station, about 5 minutes walk from the Bundestag."),

    ("practical", ["parking"],
     "Gibt es Parkmöglichkeiten?",
     "Direkt vor der Praxis gibt es bewirtschaftete Stellplätze (1,50 €/h). Das nächste Parkhaus ist die Tiefgarage Friedrichstadt-Passagen, ca. 3 Minuten zu Fuß.",
     "Is there parking?",
     "Metered street parking right outside the practice (€1.50/h). The nearest parking garage is the Friedrichstadt-Passagen underground garage, ~3 minutes walk."),

    ("practical", ["public-transport"],
     "Wie komme ich mit öffentlichen Verkehrsmitteln?",
     "S-Bahn S1, S2, S25, S26 oder U-Bahn U6 bis Friedrichstraße — die Praxis ist 1 Minute Fußweg vom Ausgang.",
     "How do I get there by public transport?",
     "S-Bahn S1, S2, S25, S26 or U-Bahn U6 to Friedrichstraße — the practice is 1 minute walk from the exit."),

    ("practical", ["accessibility"],
     "Ist die Praxis barrierefrei?",
     "Ja. Es gibt einen Aufzug bis zur Praxisetage und barrierefreie Behandlungsräume. Auch eine behindertengerechte Toilette ist vorhanden.",
     "Is the practice wheelchair-accessible?",
     "Yes. There's an elevator to our floor and accessible treatment rooms. We also have a wheelchair-accessible restroom."),

    ("practical", ["hours"],
     "Wie sind die Öffnungszeiten?",
     "Montag bis Freitag 8:00–19:00 Uhr, Samstag 9:00–13:00 Uhr. Sonntag geschlossen. Notfälle werden am gleichen Tag eingeplant.",
     "What are the opening hours?",
     "Monday to Friday 8:00–19:00, Saturday 9:00–13:00. Closed Sunday. Emergencies are scheduled the same day."),

    ("practical", ["languages"],
     "Welche Sprachen spricht das Team?",
     "Alle Behandler sprechen fließend Deutsch und Englisch.",
     "What languages does the team speak?",
     "All practitioners speak fluent German and English."),

    # ─── Children & Pregnancy ────────────────────────────────────
    ("faq", ["children"],
     "Behandeln Sie auch Kinder?",
     "Ja. Wir behandeln Kinder ab 3 Jahren. Erste Termine sind oft eine spielerische Eingewöhnung.",
     "Do you treat children?",
     "Yes. We treat children from age 3. First appointments are often a playful introduction."),

    ("faq", ["children", "first-visit"],
     "Ab welchem Alter sollte ein Kind zum Zahnarzt?",
     "Wir empfehlen den ersten Zahnarztbesuch mit dem ersten Geburtstag oder spätestens mit dem Durchbruch der ersten Zähne. Frühe Kontrolltermine bauen Vertrauen auf.",
     "At what age should a child first see a dentist?",
     "We recommend the first dental visit at age 1, or at the latest when the first teeth come in. Early visits build trust."),

    ("faq", ["pregnancy"],
     "Kann ich während der Schwangerschaft zum Zahnarzt?",
     "Ja, und Sie sollten auch. Routinekontrollen und Reinigungen sind in jedem Trimester sicher. Größere Eingriffe (Implantate, ausgedehnte Wurzelbehandlungen) verschieben wir nach Möglichkeit auf nach der Geburt. Bitte teilen Sie uns mit, in welcher Schwangerschaftswoche Sie sind.",
     "Can I see the dentist during pregnancy?",
     "Yes — and you should. Routine check-ups and cleanings are safe in any trimester. Major procedures (implants, extensive root canals) we try to defer until after birth. Please tell us how many weeks pregnant you are."),

    ("faq", ["pregnancy", "xray"],
     "Sind Röntgenaufnahmen in der Schwangerschaft sicher?",
     "Routine-Röntgenaufnahmen vermeiden wir während der Schwangerschaft. Bei dringenden Fällen verwenden wir digitale Aufnahmen mit Bleischürze — die Strahlendosis ist sehr niedrig.",
     "Are X-rays safe during pregnancy?",
     "We avoid routine X-rays during pregnancy. For urgent cases we use digital imaging with a lead apron — the radiation dose is very low."),

    # ─── Hygiene & Safety ────────────────────────────────────────
    ("safety", ["hygiene"],
     "Welche Hygienestandards gelten in der Praxis?",
     "Wir erfüllen alle Anforderungen der RKI-Richtlinie und des Medizinprodukte-Gesetzes. Alle Instrumente werden in zertifizierten Sterilisatoren aufbereitet, Behandlungsflächen werden zwischen Patienten desinfiziert.",
     "What hygiene standards do you follow?",
     "We meet all RKI guidelines and the German Medical Devices Act. All instruments are reprocessed in certified sterilizers; treatment surfaces are disinfected between patients."),

    ("safety", ["hygiene", "sterilization"],
     "Wie werden die Instrumente sterilisiert?",
     "Mit einem validierten B-Klasse-Autoklaven bei 134 °C unter Druck. Jeder Sterilisationszyklus wird elektronisch protokolliert.",
     "How are instruments sterilized?",
     "Using a validated Class B autoclave at 134 °C under pressure. Every sterilization cycle is electronically logged."),

    ("safety", ["xray"],
     "Wie sicher sind Röntgenaufnahmen?",
     "Wir verwenden ausschließlich digitale Sensoren mit deutlich reduzierter Strahlendosis. Eine einzelne Zahnaufnahme entspricht etwa der natürlichen Hintergrundstrahlung von 1–2 Tagen.",
     "Are X-rays safe?",
     "We use only digital sensors with significantly reduced radiation dose. A single tooth X-ray is equivalent to about 1–2 days of natural background radiation."),

    # ─── First-time visit ────────────────────────────────────────
    ("faq", ["first-visit"],
     "Was muss ich zum ersten Termin mitbringen?",
     "Bitte bringen Sie Ihre Versichertenkarte, eine Liste aktueller Medikamente und — falls vorhanden — Vorbefunde oder Röntgenaufnahmen vom letzten Zahnarzt mit.",
     "What should I bring to my first appointment?",
     "Please bring your insurance card, a list of current medications, and — if available — prior records or X-rays from your previous dentist."),

    ("faq", ["first-visit"],
     "Wie läuft der erste Termin ab?",
     "Beim ersten Termin nehmen wir uns ca. 45 Minuten Zeit: kurze Anamnese, vollständige Befundaufnahme, eventuell Röntgenaufnahmen, und am Ende ein gemeinsamer Behandlungsplan mit transparentem Kostenüberblick.",
     "What happens at the first appointment?",
     "We take about 45 minutes for the first visit: brief medical history, full examination, possibly X-rays, and finally a shared treatment plan with a transparent cost overview."),

    # ─── Payment ─────────────────────────────────────────────────
    ("faq", ["payment", "methods"],
     "Welche Zahlungsmethoden akzeptieren Sie?",
     "Wir akzeptieren EC-Karte, Kreditkarte (Visa, Mastercard) und Überweisung. Selbstzahler erhalten direkt eine Rechnung.",
     "What payment methods do you accept?",
     "We accept debit card, credit card (Visa, Mastercard), and bank transfer. Self-pay patients receive an invoice directly."),

    ("faq", ["payment", "installments"],
     "Bieten Sie Ratenzahlung an?",
     "Ab 500 € Behandlungssumme bieten wir Ratenzahlung über unseren Partner Medikredit an. Wir besprechen die Optionen gerne im Behandlungsplan.",
     "Do you offer payment plans?",
     "From €500 treatment cost we offer financing via our partner Medikredit. We're happy to discuss options in the treatment plan."),

    ("faq", ["payment", "invoice"],
     "Bekomme ich eine Rechnung für die Versicherung?",
     "Ja. Selbstzahler und privat Versicherte erhalten automatisch eine Rechnung nach GOZ. Diese können Sie bei Ihrer Versicherung einreichen.",
     "Will I get an invoice for insurance?",
     "Yes. Self-pay and privately insured patients automatically receive a GOZ-based invoice you can submit to your insurer."),
]


# ─── Long-form treatment details (per service code) ────────────────────
# Keys map to Service.code in seed_dental_clinic.py.
TREATMENT_DETAILS: dict[str, dict] = {
    "checkup": {
        "details_long": {
            "de": "Eine Kontrolluntersuchung dauert ca. 30 Minuten. Wir prüfen Zähne, Zahnfleisch und Mundschleimhaut, machen bei Bedarf eine Bissflügelaufnahme und besprechen Ihre Mundhygiene. Frühzeitig erkannte Probleme lassen sich meist mit minimalen Eingriffen behandeln.",
            "en": "A check-up takes ~30 minutes. We examine teeth, gums, and oral mucosa, take bite-wing X-rays if needed, and review your oral hygiene. Problems caught early can usually be treated with minimal intervention.",
        },
        "pre_care": {
            "de": "Bitte bringen Sie Ihre Versichertenkarte mit. Putzen Sie wie gewohnt — keine besonderen Vorbereitungen nötig.",
            "en": "Please bring your insurance card. Brush as usual — no special preparation needed.",
        },
        "post_care": {
            "de": "Keine besonderen Maßnahmen nötig. Sie können sofort essen und trinken.",
            "en": "No special measures needed. You can eat and drink immediately afterward.",
        },
        "insurance_notes": {
            "de": "Für gesetzlich Versicherte: zweimal jährlich kostenfrei. Selbstzahler ca. 50 €.",
            "en": "Statutory-insured: covered twice a year. Self-pay approx. €50.",
        },
    },
    "cleaning": {
        "details_long": {
            "de": "Die professionelle Zahnreinigung (PZR) dauert ca. 45 Minuten. Wir entfernen Zahnstein und Verfärbungen mit Ultraschall und Pulverstrahl, polieren die Zähne und tragen abschließend Fluorid auf.",
            "en": "Professional teeth cleaning (PZR) takes ~45 minutes. We remove tartar and stains with ultrasonic scaler and air-flow polishing, polish the teeth, and apply fluoride at the end.",
        },
        "pre_care": {
            "de": "Vermeiden Sie 24 h vor dem Termin stark färbende Lebensmittel (Rotwein, schwarzer Tee, Kurkuma).",
            "en": "Avoid strongly staining food and drink 24h before the appointment (red wine, black tea, turmeric).",
        },
        "post_care": {
            "de": "Verzichten Sie für 1–2 Stunden auf färbende Speisen und Getränke. Für 24 h kein Kaffee, Tee, Rotwein, Curry oder Tabak — die Zähne sind direkt nach der PZR besonders aufnahmefähig.",
            "en": "Avoid staining food and drink for 1–2 hours. For 24h no coffee, tea, red wine, curry, or tobacco — teeth are particularly absorbent right after cleaning.",
        },
        "insurance_notes": {
            "de": "Gesetzliche Krankenkassen erstatten 1× jährlich einen Zuschuss von 60–80 €. Privat versicherte Patienten erhalten in der Regel die volle Erstattung.",
            "en": "Statutory insurance covers a €60–80 contribution once a year. Private insurance usually reimburses in full.",
        },
    },
    "filling": {
        "details_long": {
            "de": "Eine Composite-Füllung dauert je nach Größe 30–60 Minuten. Wir entfernen die Karies unter lokaler Anästhesie, modellieren die Füllung in mehreren Schichten und härten sie mit UV-Licht aus. Anschließend wird die Form an Ihren Biss angepasst.",
            "en": "A composite filling takes 30–60 minutes depending on size. We remove decay under local anesthesia, build up the filling in layers, and cure each layer with UV light. The shape is then adjusted to your bite.",
        },
        "pre_care": {
            "de": "Bitte essen Sie eine Kleinigkeit vor dem Termin — die Anästhesie wirkt 2–3 Stunden, in dieser Zeit sollten Sie nicht essen, um sich nicht zu verletzen.",
            "en": "Please eat something before the appointment — anesthesia lasts 2–3 hours, during which you shouldn't eat to avoid injuring yourself.",
        },
        "post_care": {
            "de": "Composite ist sofort belastbar. Vermeiden Sie für 24 h sehr harte Speisen (Nüsse, Eis). Bei Empfindlichkeit auf Kalt/Warm: meist nach 1–2 Wochen vorbei.",
            "en": "Composite is immediately load-bearing. Avoid very hard foods (nuts, ice) for 24h. Cold/heat sensitivity: usually subsides within 1–2 weeks.",
        },
        "contraindications": {
            "de": "Bei Allergie auf Composite-Bestandteile (selten) verwenden wir alternativ Keramikinlays.",
            "en": "For allergies to composite components (rare) we offer ceramic inlays as an alternative.",
        },
        "insurance_notes": {
            "de": "Im Frontzahnbereich werden Composite-Füllungen von der Kasse voll übernommen. Im Seitenzahnbereich: Eigenanteil ca. 50–100 € pro Füllung.",
            "en": "Front teeth: composite fillings fully covered by statutory insurance. Back teeth: co-pay ~€50–100 per filling.",
        },
    },
    "implant": {
        "details_long": {
            "de": "Ein Implantat ist eine künstliche Zahnwurzel aus Titan, die im Kieferknochen verankert wird. Erstberatung: 60 min. Inseration des Implantats: 60–90 min. Einheilphase: 3–6 Monate. Krone aufsetzen: 30–45 min. Insgesamt 4–6 Monate vom ersten Termin bis zur Versorgung.",
            "en": "An implant is an artificial tooth root made of titanium, anchored in the jawbone. Initial consultation: 60 min. Implant placement: 60–90 min. Healing phase: 3–6 months. Crown placement: 30–45 min. Total: 4–6 months from first appointment to final restoration.",
        },
        "pre_care": {
            "de": "Wir benötigen aktuelle 3D-Aufnahmen (DVT) und ein Blutbild. Bei Blutverdünnern bitte vorher mit Hausarzt abstimmen. Rauchen vor und nach der OP erhöht das Risiko von Komplikationen erheblich — wir empfehlen mindestens 2 Wochen Pause.",
            "en": "We need current 3D imaging (CBCT) and blood work. If you take blood thinners, please coordinate with your GP first. Smoking before and after surgery significantly increases complication risk — we recommend at least 2 weeks abstinence.",
        },
        "post_care": {
            "de": "Erste 24 h: kühlen, weiche Kost, kein Sport. Erste Woche: Mund mit Chlorhexidin spülen, OP-Bereich beim Putzen aussparen. Nach 7–10 Tagen Fadenentfernung. Während der Einheilphase: regelmäßige Kontrollen.",
            "en": "First 24h: ice the area, soft food, no sports. First week: rinse with chlorhexidine, avoid the surgical site when brushing. Suture removal after 7–10 days. During healing: regular check-ups.",
        },
        "contraindications": {
            "de": "Unkontrollierte Diabetes, schwere Osteoporose unter Bisphosphonaten, aktive Parodontitis und starkes Rauchen sind relative Kontraindikationen — wir besprechen das individuell.",
            "en": "Uncontrolled diabetes, severe osteoporosis on bisphosphonates, active periodontitis, and heavy smoking are relative contraindications — we discuss individually.",
        },
        "insurance_notes": {
            "de": "Implantate werden von der gesetzlichen Krankenkasse nur in Ausnahmefällen übernommen (z. B. nach Tumor-OP). Private Versicherungen erstatten je nach Tarif 50–100 %. Vorab Heil- und Kostenplan zur Einreichung.",
            "en": "Statutory insurance covers implants only in exceptional cases (e.g. after tumor surgery). Private insurers reimburse 50–100% depending on plan. We provide a cost plan for pre-approval.",
        },
    },
    "bleaching": {
        "details_long": {
            "de": "Beim In-Office-Bleaching tragen wir nach gründlicher Reinigung ein hochkonzentriertes Wasserstoffperoxid-Gel auf, das mit einer LED-Lampe aktiviert wird. Eine Sitzung dauert 90 min und hellt die Zähne meist um 4–8 Stufen auf. Effekt hält 1–3 Jahre.",
            "en": "For in-office bleaching, after thorough cleaning we apply a high-concentration hydrogen peroxide gel activated by an LED lamp. One session takes 90 min and lightens teeth by 4–8 shades. Effect lasts 1–3 years.",
        },
        "pre_care": {
            "de": "Eine PZR sollte 1–2 Wochen vor dem Bleaching erfolgen. Bestehende Karies oder undichte Füllungen müssen vorher behandelt werden, sonst dringt das Gel ein und verursacht Schmerzen.",
            "en": "A professional cleaning should be done 1–2 weeks before bleaching. Existing decay or leaky fillings must be treated first, otherwise the gel can penetrate and cause pain.",
        },
        "post_care": {
            "de": "48 h keine färbenden Speisen oder Getränke (Kaffee, Tee, Rotwein, Curry, Tabak). Erhöhte Empfindlichkeit ist normal und klingt meist innerhalb 24–72 h ab. Bei Bedarf Sensitive-Zahnpasta verwenden.",
            "en": "48h no staining food or drink (coffee, tea, red wine, curry, tobacco). Increased sensitivity is normal and usually subsides within 24–72h. Use sensitivity toothpaste if needed.",
        },
        "contraindications": {
            "de": "Schwangere und stillende Frauen, Patienten unter 18 Jahren, ausgedehnte Frontzahnfüllungen oder Kronen (diese werden nicht aufgehellt), schwere Zahnfleischentzündungen.",
            "en": "Pregnant or breastfeeding women, patients under 18, extensive front-tooth fillings or crowns (which won't lighten), severe gum inflammation.",
        },
        "insurance_notes": {
            "de": "Bleaching ist eine ästhetische Leistung und wird weder von der gesetzlichen noch typischerweise von der privaten Krankenversicherung übernommen.",
            "en": "Bleaching is a cosmetic service and is not covered by statutory insurance, nor typically by private insurance.",
        },
    },
    "root_canal": {
        "details_long": {
            "de": "Bei einer Wurzelbehandlung entfernen wir entzündetes Nervengewebe aus dem Zahninneren, reinigen und desinfizieren die Wurzelkanäle und füllen sie luftdicht. Wir arbeiten mit Mikroskop, elektronischer Längenmessung und maschineller Aufbereitung — modernes Niveau erhält den Zahn meist langfristig.",
            "en": "In a root canal we remove inflamed nerve tissue from inside the tooth, clean and disinfect the root canals, and fill them airtight. We work with a microscope, electronic length measurement, and rotary instrumentation — modern protocols typically preserve the tooth long-term.",
        },
        "pre_care": {
            "de": "Bei akuten Schmerzen ggf. Antibiotika-Vorbehandlung 1–2 Tage. Sonst keine besondere Vorbereitung — bitte vorher essen.",
            "en": "For acute pain, sometimes antibiotic pre-treatment for 1–2 days. Otherwise no special preparation — please eat beforehand.",
        },
        "post_care": {
            "de": "Leichte Druck-Empfindlichkeit für 2–4 Tage ist normal. Schonen Sie den Zahn, vermeiden Sie harte Kost. Eine endgültige Krone ist meist nach 2–4 Wochen empfehlenswert, um den geschwächten Zahn zu schützen.",
            "en": "Mild pressure sensitivity for 2–4 days is normal. Be gentle on the tooth, avoid hard food. A final crown is typically recommended 2–4 weeks later to protect the weakened tooth.",
        },
        "contraindications": {
            "de": "Bei nicht erhaltungswürdigen Zähnen oder fortgeschrittener Parodontitis wird Extraktion empfohlen. Wir besprechen die Alternativen.",
            "en": "For teeth not worth saving or in advanced periodontitis, extraction is recommended. We'll discuss alternatives.",
        },
        "insurance_notes": {
            "de": "Bei erhaltungswürdigen Zähnen übernimmt die Kasse die Grundleistung. Höherwertige Methoden (Mikroskop, maschinelle Aufbereitung): Eigenanteil 240–600 €.",
            "en": "Statutory insurance covers basic treatment for teeth worth saving. Premium methods (microscope, rotary): co-pay €240–600.",
        },
    },
}


async def seed() -> None:
    async with session_scope() as session:
        biz = (
            await session.execute(select(Business).where(Business.slug == "demo-dental"))
        ).scalar_one_or_none()
        if not biz:
            raise SystemExit("demo-dental business not found — run scripts/seed_demos.py first")

        # ─ Wipe previous knowledge entries ────────────────────────
        await session.execute(
            delete(KnowledgeEntry).where(KnowledgeEntry.business_id == biz.id)
        )

        # ─ Insert FAQs (DE + EN per row) ──────────────────────────
        added = 0
        for category, tags, title_de, body_de, title_en, body_en in FAQS:
            session.add(
                KnowledgeEntry(
                    business_id=biz.id,
                    category=category,
                    language="de",
                    title=title_de,
                    body=body_de,
                    tags=tags,
                    is_active=True,
                    is_demo=biz.is_demo,
                )
            )
            session.add(
                KnowledgeEntry(
                    business_id=biz.id,
                    category=category,
                    language="en",
                    title=title_en,
                    body=body_en,
                    tags=tags,
                    is_active=True,
                    is_demo=biz.is_demo,
                )
            )
            added += 2

        # ─ Update Service rows with long-form details ─────────────
        services = (
            await session.execute(select(Service).where(Service.business_id == biz.id))
        ).scalars().all()
        services_updated = 0
        for svc in services:
            details = TREATMENT_DETAILS.get(svc.code)
            if not details:
                continue
            svc.details_long = details.get("details_long", {})
            svc.pre_care = details.get("pre_care", {})
            svc.post_care = details.get("post_care", {})
            svc.contraindications = details.get("contraindications", {})
            svc.insurance_notes = details.get("insurance_notes", {})
            services_updated += 1

        await session.flush()

        print(f"  [seeded] knowledge_entries={added} ({added // 2} FAQs × 2 languages)")
        print(f"  [seeded] services_updated={services_updated} (long-form details)")


if __name__ == "__main__":
    asyncio.run(seed())
