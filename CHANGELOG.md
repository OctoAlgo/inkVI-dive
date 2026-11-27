# Changelog

## v0.1 (first version, work in progress) - on inkVI v0.2.1, eleven patches

First packaging of our debug tooling as a kit: the command channel, the natives hook with its commands (pos, tp,
time, date, bookmarks, scenes, ncall, traces) and the capture switches used for testing pictures.

New against the tooling as it was used before packaging:
- The two hook sites (the NATIVE opcode's call and the by-ID call) are found by byte pattern and used only when each
  occurs exactly once in the executable's code; before they were fixed addresses with a byte check (patch 0007).
- The helper that finds memory near the image for the stubs is part of patch 0002 (it came from another patch set).

Checked: `git am` of inkVI's 38 + these 11 on a clean victory-fork `4c6046614` and a diagnostics build with
`build.sh` into an empty directory (Linux cross build); host tests of `natives.rs` (7 passed, including both
patterns occurring exactly once in the 1.0.2.1 executable at their known places); in the game (RTX 5070 Ti, Proton,
Series X profile, Chapter 1 opening, a build of this series): both sites found by pattern at their 1.0.2.1 places;
`pos`, `time`, `date`, `tpmarks`, setting time and date, `cap`, `scene list`, `nstat`, a montage replay with `scene
play` and captures after each start of it; the far-teleport steps of the README's Limits (and the crash after a
mission restart). Not run on Windows, on AMD or Intel cards, or on the Series S profile.
