<link rel="stylesheet" type="text/css" href="../tools/SliderCtrl.css">
<style>
:root {
  --doc-title: "Architecture — Marks vs working window";
  --doc-path: ".\\SliderDoc\\architecture\\marks-vs-working-window.md";
}
</style>

# Architecture — Marks vs working window

Same motion board, two operator models. **JKSlider** stores **A/B/C marks** (waypoints). **B4Slider** uses an **A/B window (working window)** — a travel clip that *is* the shot.

B4 **user manuals keep the word A/B on purpose.** Most motorized-slider operators look for “A/B”, not “window”. Headings such as *Soft limits (A / B window)* exist so they find the similar feature. The two A/B’s are **not the same job**.

How-to: [JKSlider — A / B / C](../uic/projects/jkslider/user-manual.md#a--b--c) · [B4Slider — A / B window](../uic/projects/b4slider/user-manual.md#soft-limits-a--b-window). Faces: [marketing.md](marketing.md).

## Layers

Both faces talk millimetres to SliderMC. Hardware and the planner always clip travel. The UIC then chooses **marks** or a **working window**.

| Layer | What it is | Who |
|-------|------------|-----|
| **Hard limit** | Switch (`SW_HOME` / `SW_LIMIT_*`); red LED | Both apps |
| **Envelope** | `slider_min` / `slider_max` — mechanical rail (homing, `CG`) | Installer / `CS` / `mc.ini` |
| **Mark** | PosA / PosB / PosC — goto target, **not** a wall | JKSlider |
| **Working window** (manuals: **A/B**) | Session `SL` / `SR` (`GL` / `GR`) — wall **and** B4 MOVE target | B4Slider via `MC_Client.setSoftLimits` / `setLeft` |

B4Slider implements the working window with **session** `SL` / `SR` (not `CS`). Reboot restores the full envelope. JKSlider leaves the session at full rail and stores marks in the app. Integrator guide: [working-window.md](../mc/working-window.md).

MOVE / FAST / joystick on JKSlider can still travel the full MC clip. Goto and loops **aim at** a mark. On B4Slider, MOVE_L/R cruise **to** the window ends; the carriage **cannot** leave until you reset a side (or both).

## Marks (JKSlider A/B/C)

Search term and mechanism match: A/B/C are waypoints, the language most motorized-slider operators already know.

**What it does.** A mark is a **bookmark** on the rail. You store the carriage pose as A, B, or C. Later you tap that key and the slider **goes there**. The rest of the rail stays usable: MOVE / FAST / joystick are not trapped between A and B.

**Short workflow**

1. Jog to the start of the shot. Hold **A** to save PosA.
2. Jog to the end. Hold **B** to save PosB.
3. Tap **A** to return to start; tap **B** to play the move.
4. Optional: hold **C** for a third pose — tap B, wait, tap C for the second beat.
5. You can still MOVE or FAST **past** A/B if you need to reframe (that is the point of a mark, not a wall).

**Pros**

- Even with A, B, or C set, the slider can still move **outside** the marks (reframe, home, FAST to the rail end).
- Natural **flow:** A→B, wait, B→C (third beat). Loops AB / AC / BC.
- OLED ETAs between marks; positions remembered after power-off.

**Cons**

- Needs **A/B/C keys** (or a keypad) — larger panel.
- MOVE can **leave the framed shot** unless the operator uses goto.
- Three marks and chords (A+B, OPTION+A, …) are more to learn.
- Loops are explicit pairs, not “whatever the current window is.”

## Working window (B4Slider A/B)

Here **A/B** is the **label** for the working window, not a bookmark. Keys stay SET + MOVE_L/R. API names stay `soft_limit_L` / `soft_limit_R`. Architecture does not call this a “limit window” — “limit” reads as a safety end-stop (hard switch / full-rail clip), which is the layer **above**.

**What it does.** The working window is the **allowed stretch of rail**. You set a left end and a right end. Those ends are both a **wall** (you cannot leave) and the **MOVE target** (MOVE_L cruises to the left end and stops). There is no separate “go to A” key — left and right **are** A/B in the manual.

**Short workflow**

1. Jog to the first pose. **SET + MOVE_L** tap — that is now the left end (A).
2. Jog to the second pose. **SET + MOVE_R** tap — that is now the right end (B).
3. Tap **MOVE_L** or **MOVE_R** — the carriage cruises to that end and **stops**. You cannot roll past it.
4. To reframe outside, hold **SET + MOVE** on that side to open it back to full rail (or reset both).

**Pros**

- **Fewer buttons** — SET + MOVE_L/R instead of A/B/C.
- **Easier handling:** MOVE_L/R **is** the A/B move (cruise to the soft end).
- Stop-at-end behaviour **already exists** at the mechanical / MC limit; the shot just **shrinks** that same stop.

**Cons**

- You **cannot sneak past** the framed ends to reframe without resetting the window (or opening one side).
- **No C** — no A→B wait B→C story beat on this panel.
- The similar-looking “A/B” **clips travel**; it is not a bookmark you can leave and return to while jogging the rest of the rail.
- Accidental SET + MOVE tap **shrinks the whole rail** until hold-reset (white blip).
- B4 **does not remember** the window after power-off (full travel again). JKSlider **does** remember PosA/B/C.

## When to pick which

Not a third product — pick the UIC that matches the shoot and the plate.

| Pick | When |
|------|------|
| **JKSlider / marks** | Narrative moves, timelapse with three poses, need to jog **past** the shot, OLED ETAs between marks, operators who want Kessler-style A/B **as waypoints** |
| **B4Slider / working window** | 4-button plate, no OLED, “left and right **are** the A/B window,” ping-pong loops between ends, slim or budget remote |

**Do not put both models on one panel without a mode switch.** Mixing “A is a mark” and “L is a wall” on the same keys is how operators overshoot or trap the carriage.

A later hybrid is possible (for example a B4 chord to restore full MC travel without forgetting L/R, or JKSlider MOVE clipped to A–B while FAST still leaves the window). Shipping apps stay **one model each**.
