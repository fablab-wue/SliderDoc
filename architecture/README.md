# Architecture

Philosophy, system split, and competitive context for the Slider UIC + SliderMC design.

**Start here:** [overview.md](overview.md)

## Canonical terminology

The project uses these terms deliberately and consistently:

| Term | Meaning | Typical owner |
|------|---------|---------------|
| **Hard limit** | Physical end-stop or home/limit switch | MC hardware |
| **Envelope** | Rail limits configured in `slider_min` / `slider_max` | Installer / `CS` |
| **Working window** | Session soft ends (`SL` / `SR`) that clip travel for a shot | B4Slider / MC session |
| **Mark** | Waypoint stored in the app (A / B / C) | JKSlider |

The important distinction is that **A/B in JKSlider** means **marks**, while **A/B in B4Slider** means **the working window**. They are both called “A/B” in operator language, but they are not the same object.

| Document | Contents |
|----------|----------|
| [overview.md](overview.md) | Two-board split, pros/cons, interconnect, failure modes |
| [command-chains.md](command-chains.md) | `;` chains as in-move scripts (`WP` / `WC` / `WnC` / `Z` / `Xn`) |
| [marks-vs-working-window.md](marks-vs-working-window.md) | Canonical explanation: JKSlider A/B/C marks vs B4Slider A/B working window |
| [marks-vs-soft-limits.md](marks-vs-soft-limits.md) | Legacy alias kept for compatibility; same concept, older wording |
| [compare.md](compare.md) | Competitive scan vs commercial / DIY sliders |
| [marketing.md](marketing.md) | Short marketing overview |

**Related:** [contract/protocol.md](../contract/protocol.md) · [UIC API](../uic/api/overview.md) · [SliderCtrl](https://github.com/fablab-wue/SliderCtrl) · [SliderMC](https://github.com/fablab-wue/SliderMC)