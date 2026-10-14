# Dev Journey Agent — Brand Guidelines

## Core idea

The identity represents a vague request becoming an evidence-backed delivery
plan. The `D` is a delay gate shaped like a flag, while the `J` becomes the
stable flagpole beneath it. The blue route begins at the central checkpoint,
reaches the `D` boundary, and finishes with a contained upper-right arrow:
pause, understand, then accelerate.

The visual tone is sober and portfolio-ready: confident navy foundations,
focused indigo action, restrained teal for evidence and progress, and a small
gold accent for milestones.

## Color system

| Token | Hex | Use |
|---|---|---|
| Ink | `#0B1220` | Header, primary text, high-contrast surfaces |
| Ink Soft | `#1E293B` | Secondary dark surfaces and code blocks |
| Slate | `#475569` | Body text and supporting labels |
| Muted | `#64748B` | Metadata and captions |
| Mist | `#F4F7FB` | Page background |
| Paper | `#FFFFFF` | Cards and report surfaces |
| Indigo | `#3157D5` | Links, active states, primary action |
| Teal | `#0F8B8D` | Evidence, progress, positive status |
| Gold | `#C89B3C` | Milestone accent and the route nodes |
| Line | `#D8E0EC` | Borders, dividers, table rules |

Use the dark Ink and Mist/Paper as the foundation. Indigo and Teal should
carry functional meaning; Gold should remain an accent rather than a large
surface.

## Typography

- Display and headings: `Plus Jakarta Sans`, falling back to `Inter`, then
  system sans-serif.
- Body and UI text: `Inter`, falling back to system sans-serif.
- Technical snippets and identifiers: `JetBrains Mono`, falling back to a
  system monospace font.

The report uses restrained uppercase labels, generous whitespace, and short
metadata lines to keep technical content legible for stakeholders.

## Logo rules

- Approved logo: v19, the smooth joined-ribbon mark with the contained gold arrow.
- Approved source file: `docs/assets/logo-smooth-junction-v19.png`.
- Runtime asset: `src/templates/assets/dj-mark.png`.
- Documentation copy: `docs/assets/dj-mark.png`.
- The `D` flag and `J` flagpole should remain visually centered as one mark.
- The teal path must terminate at the white `D` boundary; the gold arrow must
  remain inside that boundary and never enter the surrounding Ink background.
- Keep the mark on Ink or Paper with adequate clear space around it.
- Do not stretch, rotate, recolor, add effects, or place it over busy imagery.
- Use the full lockup (`DEV JOURNEY` plus `AGENT · FEATURE PLANNING COPILOT`)
  in report headers and portfolio surfaces.
- Use the standalone mark for compact navigation, favicons, and slide corners.

## Cross-medium application

- HTML: load `src/templates/assets/brand.css`; preserve the semantic tokens and
  the report header hierarchy.
- PDF: render the same HTML/CSS at A4; retain the Ink header, Paper cards,
  visible section labels, and print-safe borders.
- Presentation: use Ink as the base, Paper cards for content, Indigo for
  structure, Teal for proof/results, and Gold only for milestones or highlights.
- Portfolio case studies: pair each claim with an evidence or traceability ID;
  the visual language should reinforce the project's auditability.

## Voice

Clear, evidence-led, and calm. Prefer specific statements over hype. Use
labels such as `approved`, `needs input`, `requirement`, and `test` when they
help the reader understand the state of the work.

