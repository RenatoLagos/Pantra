---
version: alpha
name: Duno Inspired
description: An inspired interpretation of Duno's design language — a B2B compliance and onboarding platform whose marketing surfaces lean almost entirely on a single signature: hand-painted watercolor mountain-and-sky illustrations spanning the page top, a mid-page sky-blue callout band, and the page-base footer band. Type sets at extreme display sizes in a geometric humanist sans, the canvas stays pure white, and the only chromatic action color is a deep warm near-black that lives in CTA pills and dark testimonial slabs.

colors:
  primary: "#160f0c"
  on-primary: "#ffffff"
  ink: "#1a1816"
  ink-soft: "#1b0624"
  graphite: "#4d4846"
  stone: "#898683"
  canvas: "#ffffff"
  canvas-soft: "#f7f7f5"
  hairline: "#1a1715"
  callout-sky: "#67a0b4"
  callout-sky-deep: "#4f85a3"
  form-band-sage: "#46838c"
  canvas-cream: "#edece7"

typography:
  display-mega:
    fontFamily: GT America Trial Md
    fontSize: 80px
    fontWeight: 500
    lineHeight: 1.0
    letterSpacing: 0
    fontFeature: tnum, zero
  display-xl:
    fontFamily: GT America Regular
    fontSize: 72px
    fontWeight: 400
    lineHeight: 1.0
    letterSpacing: -4.32px
  display-lg:
    fontFamily: GT America Regular
    fontSize: 44px
    fontWeight: 400
    lineHeight: 1.10
    letterSpacing: -2.2px
    fontFeature: blwf, cv03, cv04, cv09, cv11
  heading-1:
    fontFamily: GT America Regular
    fontSize: 40px
    fontWeight: 400
    lineHeight: 1.20
    letterSpacing: -1.2px
  heading-2:
    fontFamily: GT America Regular
    fontSize: 32px
    fontWeight: 400
    lineHeight: 1.20
    letterSpacing: -0.96px
  heading-3:
    fontFamily: GT America Regular
    fontSize: 24px
    fontWeight: 400
    lineHeight: 1.40
    letterSpacing: -0.72px
  heading-4:
    fontFamily: GT America Regular
    fontSize: 20px
    fontWeight: 400
    lineHeight: 1.40
    letterSpacing: -0.4px
  body-md:
    fontFamily: GT America Regular
    fontSize: 18px
    fontWeight: 400
    lineHeight: 1.40
    letterSpacing: -0.1px
    fontFeature: blwf, cv03, cv04, cv09, cv11
  body-sm:
    fontFamily: GT America Regular
    fontSize: 16px
    fontWeight: 400
    lineHeight: 1.50
    letterSpacing: -0.16px
  body-xs:
    fontFamily: GT America Regular
    fontSize: 14px
    fontWeight: 400
    lineHeight: 1.50
    letterSpacing: 0
  body-md-medium:
    fontFamily: GT America Medium
    fontSize: 20px
    fontWeight: 500
    lineHeight: 1.50
    letterSpacing: -0.4px
    fontFeature: blwf, cv03, cv04, cv09, cv11
  body-md-feature:
    fontFamily: GT America Trial Md
    fontSize: 17px
    fontWeight: 500
    lineHeight: 1.76
    letterSpacing: -0.2px
  caption-sm:
    fontFamily: GT America Trial Rg
    fontSize: 14px
    fontWeight: 400
    lineHeight: 1.71
    letterSpacing: 0
  caption-uc:
    fontFamily: GT America Regular
    fontSize: 12px
    fontWeight: 400
    lineHeight: 1.30
    letterSpacing: 0.24px
    fontFeature: blwf, cv03, cv04, cv09, cv11
  caption-mono:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: 700
    lineHeight: 1.50
    letterSpacing: 0
  utility-xs:
    fontFamily: sans-serif
    fontSize: 12px
    fontWeight: 400
    lineHeight: 1.0
    letterSpacing: 0

rounded:
  none: 0px
  sm: 12px
  md: 16px
  lg: 24px
  xl: 60px
  xxl: 799px
  full: 999px

spacing:
  hairline: 1px
  xxxs: 4px
  xxs: 6px
  xs: 8px
  xs-plus: 10px
  sm: 12px
  sm-plus: 13px
  md: 16px
  md-plus: 20px
  lg: 24px
  xl: 40px
  xxl: 64px
  section-sm: 80px
  section-md: 96px
  section-lg: 128px

components:
  nav-bar:
    backgroundColor: "{colors.canvas}"
    textColor: "{colors.ink}"
    typography: "{typography.body-sm}"
    padding: 16px
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    typography: "{typography.body-sm}"
    rounded: "{rounded.full}"
  hero-illustration-band:
    backgroundColor: "{colors.canvas}"
    textColor: "{colors.ink}"
    typography: "{typography.display-mega}"
  callout-blue-band:
    backgroundColor: "{colors.callout-sky}"
    textColor: "{colors.ink}"
    typography: "{typography.display-lg}"
  testimonial-slab-dark:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    typography: "{typography.heading-2}"
    rounded: "{rounded.lg}"
    padding: 40px
  case-card:
    backgroundColor: "{colors.canvas}"
    textColor: "{colors.ink}"
    typography: "{typography.body-md}"
    rounded: "{rounded.md}"
    padding: 24px
  feature-tile:
    backgroundColor: "{colors.canvas-soft}"
    textColor: "{colors.ink}"
    typography: "{typography.body-md}"
    rounded: "{rounded.md}"
    padding: 24px
  product-mockup-frame:
    backgroundColor: "{colors.canvas-soft}"
    textColor: "{colors.ink}"
    rounded: "{rounded.sm}"
  benefit-card:
    backgroundColor: "{colors.canvas}"
    textColor: "{colors.ink}"
    typography: "{typography.body-sm}"
    padding: 16px
  investor-row:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    typography: "{typography.body-sm}"
    padding: 24px
  press-quote-card:
    backgroundColor: "{colors.canvas-soft}"
    textColor: "{colors.ink}"
    typography: "{typography.body-md}"
    rounded: "{rounded.md}"
    padding: 24px
  faq-row:
    backgroundColor: "{colors.canvas}"
    textColor: "{colors.ink}"
    typography: "{typography.heading-4}"
    padding: 24px
  footer-band:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    typography: "{typography.body-sm}"
    padding: 64px
  text-input-on-sage:
    backgroundColor: "{colors.form-band-sage}"
    textColor: "{colors.on-primary}"
    typography: "{typography.body-md}"
    rounded: "{rounded.full}"
    padding: 16px
  button-light-pill:
    backgroundColor: "{colors.canvas}"
    textColor: "{colors.ink}"
    typography: "{typography.body-md}"
    rounded: "{rounded.full}"
    padding: 16px
  get-started-form-band:
    backgroundColor: "{colors.form-band-sage}"
    textColor: "{colors.on-primary}"
    typography: "{typography.display-mega}"
    padding: 96px
  hairline-divider:
    backgroundColor: "{colors.hairline}"
    height: 1px
---

## Overview

Duno is a B2B compliance and onboarding platform, and its marketing surfaces are organized around a single recognisable signature: hand-painted watercolor mountain-and-sky illustrations that span the page-top hero, a mid-page sky-blue callout band, and the dark page-base footer band. The illustration is the brand's atmospheric mood; everything else — type, chrome, layout — is engineered to stay quiet around it.

The system rests on a pure white canvas (`{colors.canvas}`), with one off-white alternate (`{colors.canvas-soft}`) used to differentiate paired side-by-side feature tiles. The only chromatic action color is `{colors.primary}` — a deep warm near-black with a faint brown cast — used for the top-right pill CTA, the dark testimonial slab, the investor wall, and the footer band. There is no warm accent, no secondary brand color, no gradient ladder. The watercolor illustration is the chromatic event; the rest of the chrome is monochrome by design.

Display type sets at extreme sizes in a geometric humanist sans (the GT America family). Hero headlines reach `{typography.display-mega}` (80 px / weight 500) on the homepage and `{typography.display-xl}` (72 px / weight 400 with -4.32 px letter-spacing) on long-form content pages — both with line-height pinned at 1.0 so the headline reads as a stamped slab against the watercolor backdrop. Body type holds at `{typography.body-md}` (18 px) with relaxed 1.4 line-height and consistent slight negative letter-spacing across every size step.

**Key Characteristics:**
- A single deep warm near-black `{colors.primary}` carries every action and every dark surface — hero CTA, testimonial slab, investor wall, footer
- The watercolor mountain-and-sky illustration is the brand's atmospheric backdrop, recurring at three precise points: hero top, mid-page callout band, footer base
- One sky-blue surface `{colors.callout-sky}` exists exclusively as the mid-page "It's built for compliance" callout — it is the only non-illustration coloured surface in the system
- Display type runs extremely tall (`{typography.display-mega}` 80 px, `{typography.display-xl}` 72 px) on tight 1.0 line-heights with aggressive negative tracking (`-4.32 px` at 72 px)
- Pill geometry (`{rounded.full}` 999 px) is reserved for primary CTAs only; cards stay at modest `{rounded.md}` 16 px or `{rounded.lg}` 24 px corners
- White canvas everywhere except the three illustration moments and the dark testimonial / investor / footer slabs — colour-block transitions are how the page breathes
- Page rhythm: watercolor hero → cream-white feature row → sky-blue callout band → pure-white case rows → dark testimonial slab → press-quote band → dark footer with watercolor base

## Colors

> **Source pages:** Home (primary), `/product/onboard`, `/product/ai`, `/about`.

### Brand & Accent

- **Brand Ink** (`{colors.primary}` — `#160f0c`): The single chromatic action color. Used for the top-right pill CTA, the dark testimonial slab, the investor wall background on `/about`, and the footer-band slab. The faint brown cast (rather than a neutral dark grey) carries the warmth of the watercolor illustration into the chrome.
- **Sky Callout** (`{colors.callout-sky}` — `#67a0b4`): Used exclusively on the "It's built for compliance" mid-page band, where a watercolor cloud illustration sits behind a short headline. Treat as a one-of surface, not a reusable token.
- **Sky Callout Deep** (`{colors.callout-sky-deep}` — `#4f85a3`): The deeper end of the same sky-blue band gradient. Used to seat the headline against a slightly cooler region of the cloud illustration.
- **Form Band Sage** (`{colors.form-band-sage}` — `#46838c`): A darker, greyer-teal used exclusively as the surface of the "Get started" form CTA band on `/product/onboard`. Distinct from `{colors.callout-sky}` — slightly more grey, more saturated, used for an interactive form surface rather than a passive callout. Pairs with translucent-white pill inputs and a white CTA pill.

### Surface

- **Canvas** (`{colors.canvas}` — `#ffffff`): The default page surface. Every section, every card, every form sits on pure white unless it is one of the three illustration bands or the three dark slabs.
- **Canvas Soft** (`{colors.canvas-soft}` — `#f7f7f5`): A barely-warmer off-white used to differentiate paired feature tiles (e.g., the side-by-side product mockup tiles on `/product/onboard`). Used for surface-vs-surface contrast, not for full-section tinting.
- **Canvas Cream** (`{colors.canvas-cream}` — `#edece7`): A warmer-still off-white used as a section-level alternate surface on `/product/onboard` (the "Everything you need" feature row). Distinct from `{colors.canvas-soft}` — warmer cast, full-band scope, not just card-vs-card differentiation.
- **Hairline** (`{colors.hairline}` — `#1a1715`, applied at 13 % opacity): The single divider tone used between footer columns, between FAQ rows, and as the 1-pixel line under the top nav.

### Text

- **Ink** (`{colors.ink}` — `#1a1816`): Primary heading and body text on light surfaces. Same warm-dark cast as `{colors.primary}` but documented separately so semantics stay clean (the same hex is used as a fill on the CTA pill and as text on the canvas — naming them apart prevents downstream confusion).
- **Graphite** (`{colors.graphite}` — `#4d4846`): Secondary text — secondary navigation links, body-of-card detail copy, the smaller footer link rows.
- **Stone** (`{colors.stone}` — `#898683`): Tertiary text — caption rows under feature tiles, the press-quote source line, timestamp / metadata under news cards.
- **Ink Soft** (`{colors.ink-soft}` — `#1b0624`, applied at 60 % opacity): A slightly violet-shifted dark used for short transient text overlays (the small "It's built for compliance" tagline word that sits inside the sky band, where pure ink would feel too rigid against the watercolor).

### Semantic

The system does not document an explicit error / success / warning palette in its public marketing surfaces. Form fields render with the system / framework defaults; positive states are not colour-coded.

## Typography

### Font Family

The brand sets nearly every surface in a single proprietary geometric humanist sans (the GT America family — Trial Md for the boldest display, Regular for body and most heading steps, Medium for emphasis, Trial Rg for short captions). Inter is documented as a fallback for one specific caption style at weight 700; a generic system sans-serif fallback is used for the smallest 12 px utility labels.

When substituting in code, **Manrope** or **Inter** at `font-feature-settings: "blwf", "cv03", "cv04", "cv09", "cv11"` get close to the family's tall x-height and rounded geometric character. Reduce the headline letter-spacing slightly when substituting because the proprietary face's metrics absorb the aggressive negative tracking better than open-source neighbours.

### Hierarchy

| Token | Size | Weight | Line Height | Letter Spacing | Use |
|---|---|---|---|---|---|
| `{typography.display-mega}` | 80 px | 500 | 1.0 | 0 | Homepage hero headline ("The new standard in compliance.") |
| `{typography.display-xl}` | 72 px | 400 | 1.0 | -4.32 px | Long-form content hero ("Identity is one of the internet's biggest unsolved problems") |
| `{typography.display-lg}` | 44 px | 400 | 1.10 | -2.2 px | Section opener (e.g., "Drive revenues with Onboard") |
| `{typography.heading-1}` | 40 px | 400 | 1.20 | -1.2 px | Sub-section opener |
| `{typography.heading-2}` | 32 px | 400 | 1.20 | -0.96 px | Card group headline |
| `{typography.heading-3}` | 24 px | 400 | 1.40 | -0.72 px | Feature-tile headline |
| `{typography.heading-4}` | 20 px | 400 | 1.40 | -0.4 px | FAQ row title |
| `{typography.body-md}` | 18 px | 400 | 1.40 | -0.1 px | Default body copy |
| `{typography.body-md-medium}` | 20 px | 500 | 1.50 | -0.4 px | Inline emphasis, key product-page bullets |
| `{typography.body-md-feature}` | 17 px | 500 | 1.76 | -0.2 px | Feature lists with extra leading |
| `{typography.body-sm}` | 16 px | 400 | 1.50 | -0.16 px | Secondary body, footer link rows |
| `{typography.body-xs}` | 14 px | 400 | 1.50 | 0 | Tertiary body, table-of-contents links |
| `{typography.caption-sm}` | 14 px | 400 | 1.71 | 0 | Press-quote source line, news-card metadata |
| `{typography.caption-uc}` | 12 px | 400 | 1.30 | 0.24 px | Eyebrow above section openers (uppercase context) |
| `{typography.caption-mono}` | 14 px | 700 | 1.50 | 0 | Pull-quote attribution, "MEWS" / "moss" lockups |
| `{typography.utility-xs}` | 12 px | 400 | 1.0 | 0 | Smallest disclaimer / cookie-banner-style text |

### Principles
- Display sets at three specific sizes (80 px / 72 px / 44 px) — there is no continuous fluid scale; section headlines snap to one of these stops
- Weight is dominated by `400`; `500` is reserved for inline emphasis and the very tallest hero size; there is no `700` heading weight in the marketing surfaces
- Letter-spacing crashes negative as size grows: `0` at 80 px (the Trial Md weight absorbs it), `-4.32 px` at 72 px, `-2.2 px` at 44 px, `-0.16 px` at 16 px — the relationship is roughly `~6 %` of size, negative
- OpenType features (`blwf`, `cv03`, `cv04`, `cv09`, `cv11`) are stamped onto specific styles where the proprietary face's stylistic alternates render correctly — drop these on substitute fonts and the document still reads as intended

## Layout

### Spacing System
- **Base unit**: 8 px
- **Tokens (front matter)**: `{spacing.hairline}` 1 px · `{spacing.xxxs}` 4 px · `{spacing.xxs}` 6 px · `{spacing.xs}` 8 px · `{spacing.xs-plus}` 10 px · `{spacing.sm}` 12 px · `{spacing.sm-plus}` 13 px · `{spacing.md}` 16 px · `{spacing.md-plus}` 20 px · `{spacing.lg}` 24 px · `{spacing.xl}` 40 px · `{spacing.xxl}` 64 px · `{spacing.section-sm}` 80 px · `{spacing.section-md}` 96 px · `{spacing.section-lg}` 128 px
- Section vertical padding cycles between `{spacing.section-sm}` and `{spacing.section-lg}` — the rhythm is two long sections (`128 px`) bracketing one shorter section (`80 px`) and that pattern carries across pages
- Card internal padding holds at `{spacing.md}`–`{spacing.lg}`; tile / mockup-frame padding is consistently `{spacing.lg}`

### Grid & Container
- The marketing container holds at roughly 1180 px wide on desktop (the `1199 px` and `1600 px` breakpoint stops in the responsive ladder bracket this width)
- Card grids run 3-up at desktop (`/about` press grid, home page benefit row), 2-up on `/product/onboard` for product-feature pairs, and collapse to 1-up below the `810 px` breakpoint
- Long-read content sets to a narrower ~720 px reading column flanked by atmospheric whitespace; the watercolor illustration above sets the page width but the article column never matches it

### Whitespace Philosophy
The system gives the watercolor illustration full width and lets the canvas below it breathe at `{spacing.section-md}`–`{spacing.section-lg}`. There are no decorative borders separating sections, no hero frames, no ribbons — the illustration is the only visual structure at the page boundary, and inside the article the only structural device is the `{component-name}: hairline-divider` between FAQ / footer rows. The result is a page that reads like a gallery wall: one mural at the top, content hung below it with generous space, one mural at the bottom.

## Elevation & Depth

| Level | Treatment | Use |
|---|---|---|
| 0 — flush | No shadow, no border | Default for body copy, full-bleed colour blocks, watercolor illustration bands |
| 1 — soft hairline | `1 px` `{colors.hairline}` (13 % opacity) | Footer column dividers, FAQ row separators, the line under the sticky top nav |
| 2 — soft float | A faint warm-tinted shadow against canvas | Reserved for the floating press-quote card and the testimonial-slab-dark when overlapping illustration borders |

The system avoids stacked shadows entirely. Card-on-card elevation, popover blurs, modal scrim effects are all absent. Depth on Duno reads almost entirely through colour-block contrast — watercolor band → white canvas → dark slab — and through the testimonial slab's deeper warm tone against the surrounding white.

### Decorative Depth
The watercolor illustration is the sole atmospheric device. It appears in three precise placements (hero top, mid-page callout band, footer base) and never repeats inside content. There are no gradients applied programmatically, no decorative SVG patterns, no abstract shapes, no animated particles — every atmospheric moment in the brand traces back to a hand-painted asset.

## Shapes

### Border Radius Scale

| Token | Value | Use |
|---|---|---|
| `{rounded.none}` | 0 px | Full-bleed colour blocks (hero band, callout, footer) |
| `{rounded.sm}` | 12 px | Image frames, product-mockup tile interiors |
| `{rounded.md}` | 16 px | Content cards (case-card, press-quote-card), feature tiles |
| `{rounded.lg}` | 24 px | Larger photographed cards, the dark testimonial slab corners |
| `{rounded.xl}` | 60 px | Decorative spans inside hero text overlays |
| `{rounded.xxl}` | 799 px | Floating organic-shape decorative elements |
| `{rounded.full}` | 999 px | Top-nav CTA pill, in-page CTA pills (the brand's only true full-pill geometry) |

### Photography Geometry
- The watercolor illustration runs full-bleed at the top of every page, flush corners with the viewport (rounded radii would compete with the painterly edges of the illustration itself)
- Founder / investor portrait crops on `/about` are square 1:1 with `{rounded.md}` corners, treated like inset photographs against the dark investor-wall background
- Product-mockup tiles on `/product/onboard` use `{rounded.sm}` corners — a smaller radius than content cards, signalling "interface chrome" rather than "content"

## Components

### Buttons

**`button-primary`** — the only button variant the system documents
- Background `{colors.primary}`, text `{colors.on-primary}`, type `{typography.body-sm}`, rounded `{rounded.full}`
- Used for the top-right "Visit Duno" pill in the sticky nav and the in-page conversion CTAs ("Get started", "Talk to sales") on every section opener
- The brand uses no outlined / ghost / link-style button variants in the captured marketing surfaces — every action is rendered as a primary pill

### Cards & Containers

**`case-card`** — used inside the press / news grid on `/about` and the case rows on the homepage
- Background `{colors.canvas}`, text `{colors.ink}`, type `{typography.body-md}`, rounded `{rounded.md}`, padding `{spacing.lg}`
- Each card holds a small photograph at `{rounded.sm}`, a short headline at `{typography.body-md-medium}`, and a metadata line at `{typography.caption-sm}` in `{colors.stone}`

**`feature-tile`** — used in the side-by-side product-feature grid on `/product/onboard` and `/product/ai`
- Background `{colors.canvas-soft}`, text `{colors.ink}`, type `{typography.body-md}`, rounded `{rounded.md}`, padding `{spacing.lg}`
- Tiles pair in 2-up grids with consistent `{spacing.lg}` gutters; the cream-white tone differentiates them from the surrounding pure-white canvas

**`product-mockup-frame`** — interface mockups embedded inside feature tiles
- Background `{colors.canvas-soft}`, rounded `{rounded.sm}`
- The smaller radius (`12 px` vs. the 16 px tile around it) reads as "screen chrome", marking the contained surface as a UI mockup rather than content

**`testimonial-slab-dark`** — the full-width dark warm slab carrying a single quoted testimonial (homepage and `/product/ai`)
- Background `{colors.primary}`, text `{colors.on-primary}`, headline at `{typography.heading-2}`, padding `{spacing.xl}`, rounded `{rounded.lg}`
- The slab is the system's primary moment of high-contrast emphasis — the warm-dark backdrop makes the white pull-quote feel monumental against the surrounding whitespace

**`press-quote-card`** — small-format quotation cards used on `/product/ai` ("MEWS" / "moss") and across the press band on `/about`
- Background `{colors.canvas-soft}`, text `{colors.ink}`, type `{typography.body-md}`, rounded `{rounded.md}`, padding `{spacing.lg}`
- Header set in `{typography.caption-mono}` (Inter weight 700) — the only place the system reaches for an Inter pull, used to set company lockups apart from body type

**`benefit-card`** — small icon + title + description tiles in the homepage 3-up benefit row
- Background `{colors.canvas}`, text `{colors.ink}`, type `{typography.body-sm}`, padding `{spacing.md}`
- Card sits flush on canvas with no border or shadow — separation comes from `{spacing.xl}` gutters between cards and the headline / description gap inside

**`investor-row`** — the dark warm wall on `/about` listing investor names + portraits
- Background `{colors.primary}`, text `{colors.on-primary}`, type `{typography.body-sm}`, padding `{spacing.lg}`
- Investor names + their company / role render as a 4-column responsive grid; portrait photographs sit at `{rounded.md}` against the warm-dark slab as deliberately quiet inset chrome

**`faq-row`** — the FAQ accordion at the bottom of `/product/ai`
- Background `{colors.canvas}`, text `{colors.ink}`, headline at `{typography.heading-4}`, padding `{spacing.lg}`
- Rows separated by `{component-name}: hairline-divider`; the question line collapses; collapsed rows show only the question + a chevron

### Inputs & Forms

**`text-input-on-sage`** — the pill-shape input field used in the "Get started" form CTA on `/product/onboard`
- Background `{colors.form-band-sage}` (the form band itself; the input reads as an inset translucent overlay), text `{colors.on-primary}` (white), type `{typography.body-md}`, rounded `{rounded.full}` (999 px — the only fully-rounded input geometry in the system), padding `{spacing.md}` vertical, generous horizontal
- Placeholder text in `{colors.on-primary}` at reduced opacity; a translucent-white inset border defines the pill outline against the sage surface
- Used in 3 stacked rows (Name, Business email, Phone number) inside the form-band

**`button-light-pill`** — the white pill CTA used inside the "Get started" form ("Schedule a demo")
- Background `{colors.canvas}` (white), text `{colors.ink}`, type `{typography.body-md}`, rounded `{rounded.full}` (999 px), padding `{spacing.md}`
- The polarity-flip companion to `{component-name}: button-primary`: where the dark CTA appears on the white canvas, this white pill appears on the sage form-band

### Navigation

**`nav-bar`** — sticky top-of-page chrome on every route
- Background `{colors.canvas}`, text `{colors.ink}`, type `{typography.body-sm}`, padding `{spacing.md}`
- Layout: small Duno wordmark on the left, centred horizontal menu (Product · Customers · Investors · About), right-aligned `button-primary` pill ("Visit Duno"); a 1-pixel `{component-name}: hairline-divider` underlines the entire nav row when scrolled past hero
- The wordmark renders in `{typography.body-md-medium}` weight so it reads as a brand mark rather than a body word

### Signature Components

**`hero-illustration-band`** — the painted watercolor mountain-and-sky scene at the top of every page
- Background `{colors.canvas}`, text overlaid in `{colors.ink}`, headline at `{typography.display-mega}` (homepage) or `{typography.display-xl}` (interior pages)
- The illustration runs full-bleed, viewport-flush; the headline sets centred over the upper-third of the painting where the sky is calmest
- This is the brand's most recognisable signature — there is exactly one watercolor illustration above the fold on every captured page, and the design system is built to stay quiet around it

**`callout-blue-band`** — the mid-page "It's built for compliance" sky-blue band with a watercolor cloud illustration
- Background `{colors.callout-sky}` (deepening to `{colors.callout-sky-deep}` at the gradient base), text `{colors.ink}`, headline at `{typography.display-lg}`
- Used at most once per page, slotted between the upper feature row and the testimonial slab; the cloud illustration sits behind the headline and is never reused outside this band

**`get-started-form-band`** — the sage form CTA at the bottom of `/product/onboard` (and product pages generally) where lead capture happens
- Background `{colors.form-band-sage}` (`#46838c`), text `{colors.on-primary}` (white), headline ("Get started") at `{typography.display-mega}` weight 500
- Layout: left column carries the headline + subhead in white; right column carries 3 stacked `{component-name}: text-input-on-sage` pill fields (Name, Business email, Phone number) above a `{component-name}: button-light-pill` ("Schedule a demo")
- Sits between the canvas content area and the watercolor footer base — the only place pill inputs appear in the system

**`footer-band`** — the page-base dark warm slab carrying nav columns + a watercolor mountain illustration at its base
- Background `{colors.primary}`, text `{colors.on-primary}`, link rows in `{typography.body-sm}`, padding `{spacing.xxl}`
- Footer-column dividers use `{component-name}: hairline-divider` rendered at low opacity against the dark surface
- The watercolor illustration at the very bottom mirrors the hero top — same painter, same palette, completing the "gallery wall" framing of the page

**`hairline-divider`** — the system's only divider treatment
- Background `{colors.hairline}`, height 1 px
- Used between footer columns, between FAQ rows, under the sticky nav, and between paired feature tiles where the `{spacing.xl}` gutter alone reads as too generous

## Do's and Don'ts

### Do
- Reserve `{colors.primary}` for actions, the testimonial slab, the investor wall, and the footer — never for body copy or decorative fill
- Use the watercolor illustration only at the three documented placements (hero top, mid-page callout band, footer base) — it is a brand asset, not a recurring background motif
- Set hero headlines at `{typography.display-mega}` or `{typography.display-xl}` with line-height pinned at `1.0` — the stamped-slab effect against the illustration is the brand's typographic signature
- Keep `{colors.callout-sky}` for the single mid-page callout — promoting it elsewhere dilutes the "one cloud band per page" signal
- Default body copy to `{typography.body-md}` (18 px) with `1.40` line-height; reach for `{typography.body-md-medium}` for inline emphasis only

### Don't
- Don't introduce a second chromatic accent beyond `{colors.primary}` — the brand reads as monochrome-with-illustration and any added hue weakens it
- Don't apply `{rounded.full}` (999 px) to anything other than CTA pills — using full radius on cards or images breaks the "pills only" reading of the geometry
- Don't use `{colors.callout-sky}` on buttons, on cards, or as a background outside the single callout band
- Don't substitute the watercolor illustration with a programmatic gradient or pattern — the brand's atmosphere lives in hand-painted assets, not generated chrome
- Don't centre body paragraphs — long-form copy is left-aligned at the narrower reading column; centred text is reserved for short hero headlines and CTA labels
- Don't add card shadows beyond the soft-float on `{component-name}: testimonial-slab-dark`; flush colour-block contrast is how the brand creates depth

## Responsive Behavior

### Breakpoints

| Name | Width | Key Changes |
|---|---|---|
| 4xl | 1600 px | Container caps at maximum; watercolor illustration bleeds wider but stays anchored to its centred composition |
| 3xl | 1199 px | Container narrows; 3-up benefit row stays 3-up |
| 2xl | 999 px | Two-up product tiles continue 2-up; case-card grid steps to 2-up |
| xl | 810 px | Nav links collapse into a hamburger; hero headline drops to a smaller display step |
| lg | 809 px | Section paddings step down from `{spacing.section-lg}` to `{spacing.section-md}` |
| md | 720 px | Feature tile pairs collapse to 1-up; FAQ rows hold full width |
| sm | 719 px | Watercolor hero illustration scales to the new viewport width while keeping its painting centred |
| xxs | 98 px | Minimum supported viewport — content reflows but stays readable |

### Touch Targets
Top-right `{component-name}: button-primary` pill renders at a height satisfying WCAG AAA touch-target guidance on mobile. FAQ row tap targets extend the full row width to maximise touchable area.

### Collapsing Strategy
- Top nav: horizontal menu + right-side CTA pill at desktop → hamburger + CTA pill only at ≤ 810 px; menu opens to a full-screen `{colors.canvas}` overlay with link items stacked at `{typography.heading-4}`
- Hero: headline overlaid on full-width watercolor illustration at desktop → headline below the illustration on mobile, with the illustration scaled to viewport width and the headline reading at a smaller display step
- Case-card grids: 3-up → 2-up at 999 px → 1-up at 720 px
- Feature tiles: 2-up paired tiles → 1-up stacked at 720 px
- Footer: 4-column → 2-column at 810 px → single accordion at 720 px

### Image Behavior
- The watercolor illustration loads as a high-resolution painting at the hero band, mid-page callout, and footer base — it is the page's heaviest asset by design
- Investor / founder portraits load lazily below the fold; product-mockup tiles render the interface as embedded images at 4:3 aspect with `{rounded.sm}` corners

## Iteration Guide

1. Start every page with the watercolor `{component-name}: hero-illustration-band`. The brand reads off-key without it.
2. Reach for `{typography.display-mega}` (homepage) or `{typography.display-xl}` (long-form) for hero headlines — these are the only acceptable hero sizes; smaller sizes lose the brand's confident-quiet character.
3. Default body to `{typography.body-md}` (18 px / 1.4 line-height); promote to `{typography.body-md-medium}` only for inline emphasis. Avoid heading-weight body copy.
4. Reserve `{colors.primary}` and `{rounded.full}` for actions only. If two pill CTAs appear in the same viewport, demote one to a text link.
5. Run `npx @google/design.md lint DESIGN.md` after edits — `broken-ref`, `contrast-ratio`, and `orphaned-tokens` warnings flag issues automatically.
6. Add new variants as separate component entries (`-pressed`, `-disabled`, `-focused`) — do not bury variants inside prose.
7. The watercolor illustration is the brand's atmosphere. Don't substitute, regenerate, or AI-paint replacements — the painterly authorship is part of the brand identity.
