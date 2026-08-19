# QD / Denoiser API

MicroPython helpers on the RP2040 PIO for a rotary **quadrature encoder** (`QD`) and an optional per-line **Denoiser**. Both live in [`QD.py`](../QD.py). They are **not** wired together in software — the application constructs them and, if used, HW-couples Denoiser outputs to the GPIOs that `QD` reads.

---

## Terminology

| Term | Meaning |
|------|---------|
| **Edge** | One accepted A or B transition → **one** FIFO word → `position` ±1 |
| **A/B cycle** (“pulse”) | One full Gray period = **4 edges** (4× decoding) |
| **PPR** | Pulses per revolution = A cycles per rev (common datasheet meaning) |
| **Count** | `QD.position` unit = one edge |

---

## Class `QD`

Bounce-immune quadrature decoder. The PIO waits on one channel at a time and **ignores chatter on the other** while waiting. Each accepted edge pushes a direction bit into the RX FIFO; MicroPython `StateMachine.irq` uses **RX FIFO not-empty** (no PIO `irq` instruction). The IRQ handler (or `poll()`) updates public `position`.

**`pin_b` must be `pin_a + 1`**, because B waits use `in_base + 1`. `jmp_pin` is only for `jmp(pin, …)` (sample B after an A edge).

Prefer **SM id 2** (PIO0) so Denoisers can use PIO1 (SM 4–7). The QD PIO program fills the **32-instruction** memory of its PIO block — do not load Denoiser on the same PIO instance.

### PIO states

| State | Wait | Direction after edge |
|-------|------|----------------------|
| s0 | A↓ | B high → rev (−1) → s3; B low → for (+1) → s1 |
| s1 | B↑ | A high → rev (−1) → s0; A low → for (+1) → s2 |
| s2 | A↑ | B high → for (+1) → s3; B low → rev (−1) → s1 |
| s3 | B↓ | A high → for (+1) → s0; A low → rev (−1) → s2 |

Cold start at AB=00 enters **s2** (after the drained startup push).

- **A leads B** → every edge takes **rev** → `position` **decreases** (−1 per edge). Stall order: s2 → s1 → s0 → s3.
- **B leads A** → every edge takes **for** → `position` **increases** (+1 per edge). Stall order: s2 → s3 → s0 → s1 (first B↑ while in s2 is ignored until A↑ syncs).
- Swap the A/B encoder wires to flip the sign.

Direction is decided on the accepted edge; `push()` runs at the start of the next wait-state.

### Timing legend

- Prefix width 7 (`state: `, `    A: `, `    B: `, ` edge: `, ` FIFO: `).
- Graphs 1–2 use 6-character cells; edge at the left of its cell (`/` rise, `\` fall).
- `state` = stalling state during that interval (one FIFO word when the edge at the left of the next interval is accepted).
- `(B↑)` / similar = physical edge **ignored** (SM waiting on the other channel).

### Timing — Graph 1: A leads B (3 cycles) → all FIFO −1

```
    A: ______/¯¯¯¯¯¯¯¯¯¯¯\___________/¯¯¯¯¯¯¯¯¯¯¯\___________/¯¯¯¯¯¯¯¯¯¯¯\_________
    B: ____________/¯¯¯¯¯¯¯¯¯¯¯\___________/¯¯¯¯¯¯¯¯¯¯¯\___________/¯¯¯¯¯¯¯¯¯¯¯\___
 edge:       A↑    B↑    A↓    B↓    A↑    B↑    A↓    B↓    A↑    B↑    A↓    B↓
state: s2    s1    s0    s3    s2    s1    s0    s3    s2    s1    s0    s3    s2
 FIFO:       -1    -1    -1    -1    -1    -1    -1    -1    -1    -1    -1    -1
```

### Timing — Graph 2: B leads A (ignored first B↑) → all FIFO +1

```
    A: ____________/¯¯¯¯¯¯¯¯¯¯¯\___________/¯¯¯¯¯¯¯¯¯¯¯\___________/¯¯¯¯¯¯¯¯¯¯¯\___
    B: ______/¯¯¯¯¯¯¯¯¯¯¯\___________/¯¯¯¯¯¯¯¯¯¯¯\___________/¯¯¯¯¯¯¯¯¯¯¯\_________
 edge:       (B↑)  A↑    B↓    A↓    B↑    A↑    B↓    A↓    B↑    A↑    B↓    A↓
state: s2    s2    s3    s0    s1    s2    s3    s0    s1    s2    s3    s0    s1
 FIFO:             +1    +1    +1    +1    +1    +1    +1    +1    +1    +1    +1
```

`(B↑)` = ignored while s2 waits for A↑.

### Timing — Graph 3: Noisy environment

`|` = narrow glitch. `state` / `edge` / `FIFO` share the same horizontal index as the A/B transitions.

```
    A: ____________/¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯\___|__|_________________/¯\/¯¯¯¯¯¯¯¯¯¯¯\______
    B: ______/¯¯¯¯¯¯¯¯¯¯¯\/¯\/\______________/¯¯¯|¯¯|¯\/¯¯¯¯¯¯¯¯¯¯¯¯¯\_____________
 edge:       (B↑)  A↑    B↓         A↓       B↑              A↑      B↓     A↓
state: s2..........s3....s0.........s1.......s2..............s3......s0.....s1
 FIFO:             +1    +1         +1       +1              +1      +1     +1
```

Other-channel chatter and glitches are rejected; valid Gray edges still count (+1 on this B-leads-style sync).

### Timing — Graph 4: bounce / spikes (event columns)

Each column is 8 characters. `state in` / `state out` bracket that column’s activity.

```
column:   |1       |2       |3       |4       |5       |6       |7       |8       |9       |
state in: |s2      |s2      |s1      |s1      |s0      |s0      |s3      |s3      |s2      |
       A: |________|/¯¯¯¯¯¯¯|¯\_/¯¯¯¯|¯¯¯¯¯¯¯¯|¯¯¯¯¯¯¯¯|\_______|_/¯\____|________|_/¯\____|
       B: |__/¯\___|________|________|/¯¯¯¯¯¯¯|¯\_/¯¯¯¯|¯¯¯¯¯¯¯¯|¯¯¯¯¯¯¯¯|\_______|________|
activity: |B noise |A rise  |A noise |B rise  |B noise |A fall  |A noise |B fall  |A spike |
accepted: |--      |A↑      |--      |B↑      |--      |A↓      |--      |B↓      |A↑ only |
FIFO:     |--      |-1      |--      |-1      |--      |-1      |--      |-1      |-1      |
state out:|s2      |s1      |s1      |s0      |s0      |s3      |s3      |s2      |s1      |
```

- Noise on the **other** channel while waiting → ignored (no FIFO word).
- A spike on the **waited** line can accept a false edge → `position` off by **±1** and the state advances (A↑-only spike in column 9: s2→s1, −1; returning A↓ ignored because s1 now waits for B↑).
- The QD program is full (32 instructions); use `Denoiser` on the other PIO if hardware debounce is needed.

### Speed limits

SM clock: **125 MHz**. About **6–8** SM cycles of work between consecutive `wait`s → PIO-bound ceiling ≈ **15 M edges/s** ≈ **4 MHz** A/B cycles (FIFO always drained).

RX FIFO depth with `JOIN_RX` is **8**. If the soft IRQ handler does not drain in time, `push()` **blocks** the SM and edges can be **missed**. Keep the handler minimal (only drain / update `position`).

**Example — 500 pulses per rotation** (500 A cycles/rev → **2000** QD counts/rev):

- PIO bound (~4 MHz A cycles): `RPM_max ≈ 4e6 / 500 × 60` ≈ **480 000 RPM** (not mechanically realistic; the decoder is not the bottleneck).
- Example practical budget **25 kHz** A cycles (100 k edges/s): `RPM_max ≈ 25000 / 500 × 60` ≈ **3000 RPM**.
- Formula: `RPM_max ≈ (f_A_Hz / PPR) × 60` with `f_A_Hz = f_edges / 4`.

### Caviat

By design for noise immunity the algorithm has a caviat. On direction change the given position is 1 cound behind. because of the edge detection. Meaning, if you drive the same mechanical position from left and from right, there is a difference of 1. There is no loss of counts on multiple change of directions!
### API

```python
from QD import QD

enc = QD(2, 14, 15)      # sm_id, pin_a, pin_b [, use_irq=True]; pin_b == pin_a + 1
print(enc.position)
enc.poll()               # optional: drain FIFO without waiting for IRQ
enc.reset(0)
enc.stop()               # or enc.deinit()
```

| Member / method | Notes |
|-----------------|--------|
| `QD(sm_id, pin_a, pin_b, use_irq=True)` | `sm_id` in 0..7; `pin_b == pin_a + 1`; pull-ups on A/B; starts SM; drains startup FIFO word; installs RXNEMPTY IRQ if `use_irq` (else call `poll()`) |
| `position` | Public int, updated from FIFO (+1 / −1) |
| `poll()` | Drain FIFO into `position` |
| `reset(value=0)` | Set `position` |
| `stop()` / `deinit()` | `sm.active(0)` |

### Wiring

- Internal **pull-ups** enabled on A/B.
- **`pin_b` must be the next GPIO after `pin_a`** (e.g. GP14/GP15).
- Common **GND** with the encoder.
- Prefer short wires; use external pulls if the encoder is open-collector and internal pulls are not enough.

---

## Class `Denoiser`

Cleans **one** GPIO. It does not know about quadrature or the other line. Use **two** instances for A and B. The **app** jumpers each `pin_out` to the GPIO that `QD` uses as A or B.

**Algorithm:** N is **`pull`ed once** at start (`sm.put(n)`). The output follows the input only after **N consecutive agreeing samples** (unanimous window of length N — a strict majority filter). Spikes shorter than N sample periods are rejected. Odd `n` is recommended for consistency with majority-style APIs; even `n` is allowed.

Place Denoiser SMs on the **other** PIO block from `QD` (e.g. SM **4** and **5** = PIO1).

### HW coupling (app responsibility)

```
encoder A ──► Denoiser(sm4, ain, a_clean) ──jumper──► QD pin_a
encoder B ──► Denoiser(sm5, bin, b_clean) ──jumper──► QD pin_b
                                      QD(2, pin_a, pin_b)
```

No references between `Denoiser` and `QD` in code.

### API

```python
from QD import QD, Denoiser

dn_a = Denoiser(4, pin_in=10, pin_out=12, n=15)
dn_b = Denoiser(5, pin_in=11, pin_out=13, n=15)
# jumpers: 12→14, 13→15
enc = QD(2, 14, 15)
```

| Member / method | Notes |
|-----------------|--------|
| `Denoiser(sm_id, pin_in, pin_out, n=15)` | `sm_id` 0..7; `n` in 1..31; pull-up on input; PIO `set_base` = output; `put(n)` once |
| `stop()` / `deinit()` | `sm.active(0)` |

Sample rate is the SM clock divided by the instructions per sample loop iteration (~a few cycles at 125 MHz when the input is stable in `hold_*`, or N loops when debouncing a transition). Debounce time ≈ `N / f_sample` on a transition.

---

## REPL demo

Running `QD.py` as a script (`__name__ == "__main__"`) constructs `QD(2, 14, 15)` and prints `position` every 250 ms. Importing the module does not start the demo.
