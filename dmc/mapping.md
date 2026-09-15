<link rel="stylesheet" type="text/css" href="../tools/SliderCtrl.css">
<style>
:root {
  --doc-title: "SliderDMC command mapping";
  --doc-path: ".\\SliderDoc\\dmc\\mapping.md";
}
</style>

# SliderDMC command mapping

[← Index](README.md)

Dragonframe **DMC v2** opcodes SliderDMC honours, and where they go. Canonical wire format: [DMC-Protocol-2024-08-13.pdf](https://www.dragonframe.com/download/dmcproto/DMC-Protocol-2024-08-13.pdf). This page is **our** subset and the SliderMC / GPIO path only.

Motor payloads are **1-based**. Unknown types return ACK `0x0013` (unsupported).

| DMC | Meaning | MC / local |
|-----|---------|------------|
| `0x0001` | hello / identify | hello reply, no ACK |
| `0x0020` | live DMX | 512-ch buffer on GP0; RAMP=0 snap, RAMP=1 linear ramp. Per-frame `0x0102` → `ERR_UNSUPPORTED` |
| `0x0021` | GIO out | GP2–5 |
| `0x0022` | GIO in | GP6–9 (data reply) |
| `0x0023` | camera | shutter: GP14 + `CT`; meter: ACK only |
| `0x0030` | motor status | moving bitmask + DMX-ramp byte |
| `0x0031` | absolute move | `MT` (÷1000) |
| `0x0032` / `0x0033` | stop | `MS` |
| `0x0034` | get position | `IP` plus one DWORD per motor (×1000) |
| `0x0035` | reset position | `SP` (no motion) |
| `0x0036` | jog | `MT` |
| `0x0037` | configure | store enable flags |
| `0x0038` | set speed | `SS` / `SA` (÷1000, clamped to MC max) |
| `0x0039` | set limits | `SL` / `SR` |
| `0x003A` | hard stop | `MS` |
| `0x0100` / `0x0101` / `0x0103` | upload begin/axis/end | RAM table + `PC`/`PD` (µm = DMC step delta; split if \|delta\| > 32767) |
| `0x0104` | RT triggers | apply GIO OUT bits at those frames |
| `0x0110` | position frame | `MT` to that pose |
| `0x0111` | run move | FPS×1000 → `PS`; `MT` start; bloop GP15+`BE`; then `PG start end` |
| `0x0113` | go | `PG` range |
| `0x0114` | end | sent when path finishes |
| `0x0120` | jog all | FPS×1000 → `PS`; `PG` current→dest |

`MSG_HI` and local GIO/DMX are answered even before MC/simulator is ready. Motion commands without MC and with simulator **off** get DMC error `0x0015`.

E-stop / hard limit: MC `#E` / `#L` / `IE:1` is reported as DMC hard-stop.

## Path play (`PG`)

On SliderMC: bare `PG` plays the whole buffer; `PG <start> <end>` is **0-based inclusive** sample indices. `start > end` plays **reverse** with negated deltas. `PI` replies `PI:<play_index>`. See [motion-path.md](../mc/motion-path.md).
