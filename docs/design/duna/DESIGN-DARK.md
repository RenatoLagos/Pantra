---
version: alpha
name: Duno Dark Inspired
description: An inspired interpretation of Duno's design language adapted for dark mode — the same warm-near-black brand ink (now the canvas itself), a deepened indigo-tinted dark ladder for surfaces, the watercolor illustration preserved verbatim as the brand's atmospheric anchor, the sky-blue callout band darkened to a deep teal, and a translucent-white text opacity ladder that keeps long-form reading legible without flattening the warm cast of the brand.

colors:
  primary: "#160f0c"
  on-primary: "#ffffff"
  ink: "#ffffff"
  ink-soft: "#f0e9e3"
  graphite: "#aaa6a3"
  stone: "#7a7572"
  canvas: "#0e0a08"
  canvas-soft: "#1a1816"
  surface-elevated: "#231e1b"
  hairline: "#3a3431"
  hairline-bright: "#4d4846"
  callout-sky: "#274a5a"
  callout-sky-deep: "#1a3340"
  form-band-sage: "#1f4148"
  canvas-cream: "#1a1612"
  light-island: "#ffffff"
  light-island-ink: "#1a1816"

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
    backgroundColor: "{colors.ink}"
    textColor: "{colors.canvas}"
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
    backgroundColor: "{colors.surface-elevated}"
    textColor: "{colors.ink}"
    typography: "{typography.heading-2}"
    rounded: "{rounded.lg}"
    padding: 40px
  case-card:
    backgroundColor: "{colors.canvas-soft}"
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
    backgroundColor: "{colors.surface-elevated}"
    textColor: "{colors.ink}"
    rounded: "{rounded.sm}"
  benefit-card:
    backgroundColor: "{colors.canvas}"
    textColor: "{colors.ink}"
    typography: "{typography.body-sm}"
    padding: 16px
  investor-row:
    backgroundColor: "{colors.canvas-soft}"
    textColor: "{colors.ink}"
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
    backgroundColor: "{colors.canvas-soft}"
    textColor: "{colors.ink}"
    typography: "{typography.body-sm}"
    padding: 64px
  light-island-card:
    backgroundColor: "{colors.light-island}"
    textColor: "{colors.light-island-ink}"
    typography: "{typography.body-md}"
    rounded: "{rounded.md}"
    padding: 24px
  text-input-on-sage:
    backgroundColor: "{colors.form-band-sage}"
    textColor: "{colors.ink}"
    typography: "{typography.body-md}"
    rounded: "{rounded.full}"
    padding: 16px
  button-light-pill:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.canvas}"
    typography: "{typography.body-md}"
    rounded: "{rounded.full}"
    padding: 16px
  get-started-form-band:
    backgroundColor: "{colors.form-band-sage}"
    textColor: "{colors.ink}"
    typography: "{typography.display-mega}"
    padding: 96px
  hairline-divider:
    backgroundColor: "{colors.hairline}"
    height: 1px
---

> This is the **dark mode** version of the Duno design system. It is fully self-contained — use this document alone when building dark-themed interfaces.

## Overview

In dark mode, the Duno system inverts onto a deepened indigo-warm canvas: the brand's near-black `#160f0c` is the light-mode primary, but in dark mode the canvas itself becomes `{colors.canvas}` `#0e0a08` (one shade deeper than the brand ink), and the original ink hex resurfaces as the polarity-flip CTA fill. The watercolor mountain-and-sky illustration is preserved verbatim — its painterly authorship and warm-golden palette are the brand's atmospheric anchor and they read beautifully against the new dark canvas without re-tinting.

The palette stays disciplined: no second accent colour gets introduced for dark mode. Surfaces step through three warm-dark tiers (`{colors.canvas}` → `{colors.canvas-soft}` → `{colors.surface-elevated}`), all carrying the same faint brown cast that runs through the brand's near-black. The sky-blue callout band darkens to a deep teal `{colors.callout-sky}` (#274a5a) so it still reads as "the sky-coloured one" against the warm-dark canvas, but loses the watercolor-illustration brightness it carried in light mode.

The text ladder shifts to a translucent-white opacity scale: `{colors.ink}` 100 % white for display headlines and primary headings; `{colors.ink-soft}` (#f0e9e3) for body — a barely-warmer near-white that maintains the brand's golden warmth without making body copy harsh. Light-island components (the founder portraits on `/about`, certain product-mockup tiles where a captured screenshot is meant to be read as "this is exactly what the customer sees") stay on white surfaces — they are deliberate brand callbacks to the light-mode system.

**Key Characteristics:**
- Three-tier warm-dark surface ladder (`{colors.canvas}` → `{colors.canvas-soft}` → `{colors.surface-elevated}`) with the same brown-tint DNA as the light-mode brand ink — no neutral grey or pure black anywhere
- The watercolor illustration is preserved verbatim as the page-top atmospheric anchor; its warm-golden palette reads as a tonal companion to the dark canvas
- `{colors.primary}` (the original brand ink `#160f0c`) is now used as the polarity-flip surface for the testimonial slab and as the inset behind the white CTA pill on dark mode — it reads even darker than the canvas
- The CTA pill flips polarity: white fill `{colors.ink}`, ink text `{colors.canvas}`, full pill `{rounded.full}` — saffron / brand-accent colours are not introduced
- The sky-blue callout band darkens to a deep teal `{colors.callout-sky}` so it still differentiates as "the sky one" against the warm-dark canvas
- Light-island components (founder portraits, captured product screenshots) stay on white surfaces — deliberate brand callbacks to the light-mode system
- Translucent-white text opacity ladder: `{colors.ink}` 100 % for headings, `{colors.ink-soft}` (`#f0e9e3`) for body, `{colors.graphite}` (`#aaa6a3`) for secondary, `{colors.stone}` (`#7a7572`) for captions

## Colors

### Brand & Accent

- **Brand Ink** (`{colors.primary}` — `#160f0c`): The same hex as light mode. In dark mode, this acts as the polarity-flip surface — used as the deepest dark slab beneath the canvas tier, often paired with the white pill CTA for high-contrast emphasis.
- **Sky Callout** (`{colors.callout-sky}` — `#274a5a`): A deep teal — the dark-mode adaptation of the light-mode `#67a0b4`. Used exclusively on the mid-page "It's built for compliance" callout band, where the watercolor cloud illustration sits behind the headline.
- **Sky Callout Deep** (`{colors.callout-sky-deep}` — `#1a3340`): The deeper end of the sky band gradient, used at the headline base.
- **Form Band Sage** (`{colors.form-band-sage}` — `#1f4148`): A darker greyer-teal — the dark-mode adaptation of the light-mode `#46838c`. Used exclusively as the surface of the "Get started" form CTA band on `/product/onboard`. Pairs with translucent pill inputs and a polarity-flipped white CTA pill.
- **Canvas Cream** (`{colors.canvas-cream}` — `#1a1612`): The dark-mode adaptation of the light-mode `#edece7` cream alternate surface. A barely-warmer step than `{colors.canvas-soft}`, used as the section-level alternate band on `/product/onboard`.

### Surface — three-tier warm-dark ladder

- **Canvas** (`{colors.canvas}` — `#0e0a08`): The default page surface — a deepened tinted-brown dark, never pure black. Carries the brand's warm DNA into dark mode.
- **Canvas Soft** (`{colors.canvas-soft}` — `#1a1816`): One step lighter than canvas, used for the footer band, investor wall, case-card, feature-tile, and press-quote-card surfaces.
- **Surface Elevated** (`{colors.surface-elevated}` — `#231e1b`): The third tier, used for the testimonial slab and product-mockup frame — it lifts the surface enough to read as "elevated" without losing the warm-dark family.
- **Hairline** (`{colors.hairline}` — `#3a3431`): Tinted-warm divider lines. Quiet enough to fade into the dark surfaces but visible against them.
- **Hairline Bright** (`{colors.hairline-bright}` — `#4d4846`): The brighter divider tier used where a quiet hairline would disappear (footer column borders, card-on-card separation against the canvas-soft tier).

### Text — translucent-white opacity ladder

- **Ink** (`{colors.ink}` — `#ffffff`): Pure white. Display headlines and primary headings only. Top of the opacity ladder.
- **Ink Soft** (`{colors.ink-soft}` — `#f0e9e3`): A barely-warmer near-white that maintains the brand's golden warmth in body copy without making it harsh. Default body text.
- **Graphite** (`{colors.graphite}` — `#aaa6a3`): Secondary text — secondary navigation, body-of-card detail copy, footer link rows.
- **Stone** (`{colors.stone}` — `#7a7572`): Tertiary text — caption rows, press-quote source line, news-card metadata.

### Light-Island

- **Light Island** (`{colors.light-island}` — `#ffffff`): Pure white surface preserved from light mode for inset cards and captured product-screenshot frames. A deliberate brand callback inside the dark composition.
- **Light Island Ink** (`{colors.light-island-ink}` — `#1a1816`): The text colour used inside light-island components — original light-mode ink, unchanged.

### Semantic
The system continues to delegate explicit error / success / warning to framework defaults; positive states are not colour-coded.

## Typography

### Font Family
Identical to light mode — the proprietary geometric humanist sans (the GT America family — Trial Md, Regular, Medium, Trial Rg) carries the brand. Inter (weight 700) remains the press-quote-attribution typeface; a generic system sans-serif fallback is used for the smallest 12 px utility labels. When substituting in code, **Manrope** or **Inter** at `font-feature-settings: "blwf", "cv03", "cv04", "cv09", "cv11"` get close.

### Hierarchy

| Token | Size | Weight | Line Height | Letter Spacing | Use |
|---|---|---|---|---|---|
| `{typography.display-mega}` | 80 px | 500 | 1.0 | 0 | Homepage hero headline |
| `{typography.display-xl}` | 72 px | 400 | 1.0 | -4.32 px | Long-form hero headline |
| `{typography.display-lg}` | 44 px | 400 | 1.10 | -2.2 px | Section opener |
| `{typography.heading-1}` | 40 px | 400 | 1.20 | -1.2 px | Sub-section opener |
| `{typography.heading-2}` | 32 px | 400 | 1.20 | -0.96 px | Card group headline |
| `{typography.heading-3}` | 24 px | 400 | 1.40 | -0.72 px | Feature-tile headline |
| `{typography.heading-4}` | 20 px | 400 | 1.40 | -0.4 px | FAQ row title |
| `{typography.body-md}` | 18 px | 400 | 1.40 | -0.1 px | Default body copy |
| `{typography.body-md-medium}` | 20 px | 500 | 1.50 | -0.4 px | Inline emphasis |
| `{typography.body-md-feature}` | 17 px | 500 | 1.76 | -0.2 px | Feature lists with extra leading |
| `{typography.body-sm}` | 16 px | 400 | 1.50 | -0.16 px | Secondary body, footer link rows |
| `{typography.body-xs}` | 14 px | 400 | 1.50 | 0 | Tertiary body, ToC links |
| `{typography.caption-sm}` | 14 px | 400 | 1.71 | 0 | Press-quote source line |
| `{typography.caption-uc}` | 12 px | 400 | 1.30 | 0.24 px | Eyebrow above section openers |
| `{typography.caption-mono}` | 14 px | 700 | 1.50 | 0 | Pull-quote attribution |
| `{typography.utility-xs}` | 12 px | 400 | 1.0 | 0 | Smallest utility labels |

### Principles
Identical to light mode — the only shift is colour. Text now uses the `{colors.ink}` → `{colors.ink-soft}` → `{colors.graphite}` → `{colors.stone}` translucent-white opacity ladder.

## Layout

### Spacing System
- **Base unit**: 8 px
- **Tokens (front matter)**: `{spacing.hairline}` 1 px · `{spacing.xxxs}` 4 px · `{spacing.xxs}` 6 px · `{spacing.xs}` 8 px · `{spacing.xs-plus}` 10 px · `{spacing.sm}` 12 px · `{spacing.sm-plus}` 13 px · `{spacing.md}` 16 px · `{spacing.md-plus}` 20 px · `{spacing.lg}` 24 px · `{spacing.xl}` 40 px · `{spacing.xxl}` 64 px · `{spacing.section-sm}` 80 px · `{spacing.section-md}` 96 px · `{spacing.section-lg}` 128 px
- The `128 px / 80 px / 128 px` section-rhythm constant carries forward unchanged

### Grid & Container
Identical to light mode — generous max-width container at ~1180 px, narrower ~720 px reading column for long-form copy, 3-up case grids and 2-up feature-tile pairs.

### Whitespace Philosophy
Unchanged. The watercolor illustration carries the visual structure at the page boundary; the dark canvas inside breathes at `{spacing.section-md}`–`{spacing.section-lg}`.

## Elevation & Depth

| Level | Treatment | Use |
|---|---|---|
| 0 — flush | No shadow, no border | Default — full-bleed colour blocks, body copy, watercolor bands |
| 1 — tier shift | Background steps from `{colors.canvas}` to `{colors.canvas-soft}` to `{colors.surface-elevated}` | Cards, nav-bar, testimonial slab, feature tiles |
| 2 — soft hairline | `1 px` `{colors.hairline}` or `{colors.hairline-bright}` | Footer column dividers, FAQ rows, sticky-nav underline |
| 3 — soft float | `0 4 px 12 px rgba(0, 0, 0, 0.4)` | Reserved for the floating press-quote card and the testimonial slab when overlapping illustration borders |

Depth is communicated almost entirely through the three-tier warm-dark ladder. The single soft-float on `{component-name}: testimonial-slab-dark` is the only true shadow in the system; on dark mode it deepens for visibility.

### Decorative Depth
The watercolor illustration carries forward verbatim — its golden / coral / teal palette reads as a tonal companion to the dark canvas, not a clash. There are no programmatic gradients, no SVG patterns, no atmospheric synthetic effects.

## Shapes

### Border Radius Scale

| Token | Value | Use |
|---|---|---|
| `{rounded.none}` | 0 px | Full-bleed colour blocks |
| `{rounded.sm}` | 12 px | Image frames, product-mockup tile interiors |
| `{rounded.md}` | 16 px | Content cards (case-card, press-quote-card), feature tiles |
| `{rounded.lg}` | 24 px | Larger photographed cards, the testimonial-slab corners |
| `{rounded.xl}` | 60 px | Decorative spans inside hero overlays |
| `{rounded.xxl}` | 799 px | Floating organic-shape decorative elements |
| `{rounded.full}` | 999 px | CTA pills (the brand's only true full-pill geometry) |

### Photography Geometry
Unchanged. Watercolor full-bleed; portrait crops 1:1 with `{rounded.md}`; product-mockup tiles `{rounded.sm}`.

## Components

### Buttons

**`button-primary`** — the polarity-flipped CTA pill in dark mode
- Background `{colors.ink}` (white), text `{colors.canvas}` (deep brown-dark), type `{typography.body-sm}`, rounded `{rounded.full}`
- The brand's no-second-accent rule forces the polarity flip: the indigo / accent colour solution other systems use isn't available here. White-on-canvas pill is the highest-contrast pairing the system permits.

### Cards & Containers

**`case-card`** — listing-grid item used in the press / news grid on `/about` and the homepage case rows
- Background `{colors.canvas-soft}`, text `{colors.ink}`, type `{typography.body-md}`, rounded `{rounded.md}`, padding `{spacing.lg}`

**`feature-tile`** — side-by-side product-feature grid on `/product/onboard` and `/product/ai`
- Background `{colors.canvas-soft}`, text `{colors.ink}`, type `{typography.body-md}`, rounded `{rounded.md}`, padding `{spacing.lg}`

**`product-mockup-frame`** — interface mockups embedded inside feature tiles
- Background `{colors.surface-elevated}`, rounded `{rounded.sm}`
- One tier deeper than the feature tile around it, signalling "screen chrome" inside content

**`testimonial-slab-dark`** — the full-width emphasised testimonial slab
- Background `{colors.surface-elevated}`, text `{colors.ink}`, headline at `{typography.heading-2}`, padding `{spacing.xl}`, rounded `{rounded.lg}`
- One tier above the canvas-soft cards around it; reads as the deepest moment of emphasis on the page

**`press-quote-card`** — small-format quotation cards on `/product/ai` and `/about`
- Background `{colors.canvas-soft}`, text `{colors.ink}`, type `{typography.body-md}`, rounded `{rounded.md}`, padding `{spacing.lg}`
- Header attribution set in `{typography.caption-mono}`

**`benefit-card`** — small icon + title + description tiles in the homepage 3-up benefit row
- Background `{colors.canvas}`, text `{colors.ink}`, type `{typography.body-sm}`, padding `{spacing.md}`
- Sits flush on canvas — separation comes from `{spacing.xl}` gutters

**`investor-row`** — the investor wall on `/about`
- Background `{colors.canvas-soft}`, text `{colors.ink}`, type `{typography.body-sm}`, padding `{spacing.lg}`
- 4-column responsive grid; portrait photographs sit at `{rounded.md}` against the dark slab

**`faq-row`** — the FAQ accordion at the bottom of `/product/ai`
- Background `{colors.canvas}`, text `{colors.ink}`, headline at `{typography.heading-4}`, padding `{spacing.lg}`
- Rows separated by `{component-name}: hairline-divider`

**`light-island-card`** — components preserved verbatim on white surfaces inside the dark composition
- Background `{colors.light-island}` (`#ffffff`), text `{colors.light-island-ink}` (`#1a1816`), type `{typography.body-md}`, rounded `{rounded.md}`, padding `{spacing.lg}`
- Used at most twice per page (founder portraits with white-card surrounds on `/about`, captured product screenshots where the screen content is meant to read as the customer's actual UI) — deliberate brand callbacks to the light-mode system

### Inputs & Forms

**`text-input-on-sage`** — the pill-shape input field used in the "Get started" form CTA on `/product/onboard`
- Background `{colors.form-band-sage}` (the form band itself; the input reads as an inset translucent overlay), text `{colors.ink}` (white), type `{typography.body-md}`, rounded `{rounded.full}` (999 px), padding `{spacing.md}`
- A translucent-white inset border defines the pill outline against the deepened sage surface
- Used in 3 stacked rows (Name, Business email, Phone number) inside the form-band

**`button-light-pill`** — the polarity-flipped CTA pill inside the "Get started" form
- Background `{colors.ink}` (white in dark mode per the brand's no-second-accent rule), text `{colors.canvas}` (warm-dark), type `{typography.body-md}`, rounded `{rounded.full}` (999 px), padding `{spacing.md}`

### Navigation

**`nav-bar`** — sticky top-of-page chrome
- Background `{colors.canvas}`, text `{colors.ink}`, type `{typography.body-sm}`, padding `{spacing.md}`
- Layout: small Duno wordmark on the left, centred horizontal menu, right-aligned `{component-name}: button-primary` (white pill); a 1 px `{component-name}: hairline-divider` underlines the row when scrolled past hero
- The wordmark renders in `{typography.body-md-medium}` weight

### Signature Components

**`hero-illustration-band`** — the watercolor mountain-and-sky scene at the top of every page
- Background `{colors.canvas}`, text `{colors.ink}`, headline at `{typography.display-mega}` (homepage) or `{typography.display-xl}` (interior pages)
- The illustration runs full-bleed and is preserved verbatim from light mode — the painterly warm-golden palette reads as the brand's atmospheric anchor against the new dark canvas without re-tinting

**`callout-blue-band`** — the mid-page "It's built for compliance" sky band
- Background `{colors.callout-sky}` (deep teal), deepening to `{colors.callout-sky-deep}` at the gradient base, text `{colors.ink}`, headline at `{typography.display-lg}`
- The watercolor cloud illustration sits behind the headline; the deepened sky-blue lets it still read as "the cloud-band" against the warm-dark canvas

**`get-started-form-band`** — the sage form CTA at the bottom of `/product/onboard`
- Background `{colors.form-band-sage}` (`#1f4148` — deepened from light-mode `#46838c`), text `{colors.ink}` (white), headline ("Get started") at `{typography.display-mega}` weight 500
- Layout: left column carries the headline + subhead in white; right column carries 3 stacked `{component-name}: text-input-on-sage` pill fields above a `{component-name}: button-light-pill` ("Schedule a demo")
- The only place pill inputs appear in the system; the polarity-flipped white CTA pill replaces the light-mode dark pill

**`footer-band`** — the page-base slab carrying nav columns + watercolor mountain illustration
- Background `{colors.canvas-soft}`, text `{colors.ink}`, link rows in `{typography.body-sm}`, padding `{spacing.xxl}`
- Footer-column dividers use `{component-name}: hairline-divider` rendered at `{colors.hairline-bright}` for visibility against the canvas-soft tier
- Watercolor base illustration mirrors the hero top — preserved verbatim

**`hairline-divider`** — the system's only divider treatment
- Background `{colors.hairline}`, height 1 px
- Brighter `{colors.hairline-bright}` variant used where the quiet hairline would disappear

## Do's and Don'ts

### Do
- Stay on the three-step warm-dark surface ladder (`{colors.canvas}` → `{colors.canvas-soft}` → `{colors.surface-elevated}`). Reach for tier shifts before introducing a new colour
- Preserve the watercolor illustration verbatim — its warm-golden palette is the brand's dark-mode atmospheric anchor
- Flip the CTA pill to white-on-canvas (`button-primary`); the brand has no second accent colour to fall back on
- Use the translucent-white opacity ladder for text (`{colors.ink}` → `{colors.ink-soft}` → `{colors.graphite}` → `{colors.stone}`)
- Preserve light-island components verbatim where they appear (founder portraits, captured product screenshots) — they are deliberate brand callbacks
- Use `{colors.hairline-bright}` for dividers on `{colors.canvas-soft}` and brighter surfaces; reserve `{colors.hairline}` for dividers on `{colors.canvas}`

### Don't
- Don't use pure black (`#000000`) anywhere — the warm-dark family is the brand
- Don't tint or recolour the watercolor illustration in dark mode — its painted authorship is part of the brand identity
- Don't introduce a chromatic accent (saffron / blue / green) that wasn't in the light-mode brand; the no-second-accent rule carries forward
- Don't apply `{rounded.full}` to anything other than the CTA pill — pill geometry is reserved for actions
- Don't force-convert light-island components to a dark surface — they are preserved deliberately

## Responsive Behavior

### Breakpoints
| Name | Width | Key Changes |
|---|---|---|
| 4xl | 1600 px | Container caps; watercolor bleeds wider but stays anchored |
| 3xl | 1199 px | 3-up benefit row stays 3-up |
| 2xl | 999 px | 2-up product tiles continue; case-card grid steps to 2-up |
| xl | 810 px | Nav links collapse; hero headline drops to a smaller display step |
| lg | 809 px | Section paddings step down |
| md | 720 px | Feature tile pairs collapse to 1-up |
| sm | 719 px | Watercolor scales to viewport while keeping its centred composition |
| xxs | 98 px | Minimum supported viewport |

Breakpoint behaviour is identical to light mode.

### Touch Targets
`{component-name}: button-primary` reaches WCAG AAA touch-target guidance on mobile. FAQ rows extend the full row width as tap targets.

### Collapsing Strategy
- Top nav: horizontal menu + right-side white CTA pill at desktop → hamburger + CTA at ≤ 810 px; menu opens to a full-screen `{colors.canvas}` overlay
- Hero: headline overlaid on watercolor at desktop → headline below the illustration on mobile
- Case-card / feature-tile grids: 3-up → 2-up at 999 px → 1-up at 720 px
- Footer: 4-column → 2-column at 810 px → single accordion at 720 px

### Image Behavior
Watercolor illustration loads at full resolution at the three signature placements; portraits and product mockups load lazily below the fold.

## Iteration Guide

1. Always check that `{component-name}: button-primary` resolves to white-on-canvas; the brand has no second accent and forgetting the polarity flip leaves CTAs invisible
2. Reach for a tier of the warm-dark ladder before introducing a new surface colour
3. Run `npx @google/design.md lint DESIGN-DARK.md` after edits — `broken-ref`, `contrast-ratio`, and `orphaned-tokens` warnings flag issues automatically
4. Add new variants as separate component entries — do not bury variants inside prose
5. Body copy defaults to `{colors.ink-soft}`; reserve `{colors.ink}` (pure white) for display headings only — pure white in body copy reads cold against the warm-dark canvas
6. Light-island components are intentional. If you find yourself converting a light-island-card to a dark surface, stop and check whether you are losing a deliberate brand callback
