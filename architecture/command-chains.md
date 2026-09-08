<link rel="stylesheet" type="text/css" href="../tools/SliderCtrl.css">
<style>
:root {
  --doc-title: "Architecture — Command chains";
  --doc-path: ".\\SliderDoc\\architecture\\command-chains.md";
}
</style>

# Architecture — Command chains

One UART/USB line of `;`-separated commands is a **lightweight moving script** on SliderMC. Live `SS` / `SA`, waypoints (`WP`), cruise edges (`WC` / `WN`), extender (`EO`), and beep (`BE`) run **during** a single seek. The carriage does not stop between A/B/C/D.

That is the opposite of JKSlider **A/B/C marks**, which are goto targets that finish a move before the next action. Command reference: [protocol.md — W](../contract/protocol.md#w--wait-silent). Marks vs window: [marks-vs-working-window.md](marks-vs-working-window.md).

It is **not** a full language: no loops, no branches, **one wait at a time**. The UIC can send the next line when `IW` clears. `HT` cancels the wait and the rest of the chain.

## How waits compose

`MT` / `MJ` start motion and return immediately. The next wait (`WP` / `WC` / `WN` / `WM` / `WT`) pauses **only the chain**. Motion keeps running. Non-waits (`SS`, `SA`, `EO1 1`, `BE`) run the instant the previous wait completes.

Start `MT` **before** `WP` / `WC` / `WN`. Those three return immediately when idle (not moving).

Optional timeout on `WP` / `WC` / `WN` / `WM` / `WH`: `!E:timeout`, remainder of the line dropped, motion **not** halted. Path-mode (`PG`) rejects these waits (`!E:busy`). `BE` never waits.

## Speed profile (no stop)

```text
SS20;MT300;WP100;SS50;WP200;SS20;WM
```

Start a 300 mm seek at 20. At 100 (~1/3) bump cruise to 50 (live retarget). At 200 (~2/3) drop back to 20 so the last third and the sine stop stay gentle. `WM` holds the line until idle.

## Hard accel, soft stop

```text
SA100;MT300;WC;SA5;WM
```

Hard acceleration until cruise (`WC` / status letter `M`), then `SA 5` so braking is very soft. Same seek, two accel personalities, no pause in the middle.

## Extender cue (lights / Start)

```text
SE 1; SS 40; MT 500; WP 250; EO1 1; WM
```

At the midpoint, `EXT_1` goes active — a lamp, a relay, or a **Start** line into another device (camera rec, fog, practical). Hold high until idle, or pulse while still moving:

```text
MT 500; WP 250; EO1 1; WT 0.15; EO1 0; WM
```

`WT` after the mark is a chain delay; the axis **keeps moving**.

## More examples

| Chain | Intent |
|-------|--------|
| `SA200; MT 600; WP 400; SA 15; WM` | Fast most of the way; only the last third brakes softly |
| `MT 300; WC; BE; WN; EO2 1; WM; EO2 0` | Beep at cruise; fire EXT_2 when braking starts |
| `BE; WT 2; MT 300; WM` | Audible pre-roll, then go |
| `EO1 1; MT 500; WM; EO1 0` | Hold record/start for the whole move |
| `MH; WH; SA100; MT 300; WC; SA5; WM` | Home, then the soft-stop seek |
| `SS20; MT 300; WP 100; SS50; BE; WP 200; SS20; WM` | 1/3–2/3 speed profile with a beep at the speed-up mark |
| `MT 400 90; WP 200; SS 15; WM` | Dual-axis: after master halfway, slow both (`WP` is the time-sync master) |

`WP` watches the **time-sync master** (first motor with a distance, else first servo). A second number on `WP` is an optional **timeout**, not a second-axis position. See [dual-movement.md](../mc/dual-movement.md).

Loops and take-counts stay on the UIC (JKSlider), not a longer chain.
