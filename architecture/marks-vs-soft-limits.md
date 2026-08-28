<link rel="stylesheet" type="text/css" href="../tools/SliderCtrl.css">
<style>
:root {
  --doc-title: "Architecture — Marks vs working window (legacy alias)";
  --doc-path: ".\\SliderDoc\\architecture\\marks-vs-soft-limits.md";
}
</style>

# Architecture — Marks vs working window (legacy alias)

This page is kept as a compatibility alias. The canonical explanation is [marks-vs-working-window.md](marks-vs-working-window.md).

The project uses these terms consistently:

- **JKSlider marks** = A/B/C waypoints stored in the UIC app.
- **B4Slider working window** = session soft ends (`SL` / `SR` or `soft_limit_L` / `soft_limit_R`) that clip travel on the MC.
- “A/B” in the B4 user manual is the panel shorthand for the working window, not a bookmark.

For the full explanation, including the layer model, workflow differences, and trade-offs, see [marks-vs-working-window.md](marks-vs-working-window.md).

This alias exists only to avoid stale external links and older references; it is not a separate architecture concept.
