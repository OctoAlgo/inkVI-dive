# Changelog

## v0.2.1 - the stage list (on inkVI v0.2.1, fourteen patches)

- Patch 0014: `stages` reads the running mission's full stage list from the title's memory, in play order. No
  stage hash has to be known: the stages the mission registered so far are the anchors. It uses a list only when
  it finds exactly one, else it says what it found. `checkpoint #<n>` counts in this list; the table of patch 0013
  is the fallback. `memfind` and `memdump`, the raw commands the list was found with, stay. docs/checkpoints.md,
  "Stage list".
- Patch 0013: the hook records the stages a mission registers at its start (`MISSION_STAGE_ADD`), in registration
  order, with a count of items per stage (`MISSION_STAGE_ITEM`). One line per stage and a summary line go to the
  channel's `log.txt` and the game log. `checkpoint list` prints the running mission's table. `checkpoint #<n>` jumps
  to the n-th stage of the table. The jump itself is unchanged. docs/checkpoints.md, "Stage table".
- Names file: `MISSION_STAGE_ADD`, `MISSION_STAGE_ITEM`.

Checked, stage list: four scripted runs on the RTX 5090 (Linux, Proton 11, Series X profile, copies of saves), two
of them on builds made with `build.sh` from a clean clone. Chapter 1: right after the mission start (2 stages
registered) `stages` lists 24 stages, the same 24 found by hand before; `checkpoint #13` and `checkpoint #14` from
ch1-s3 land there (retry 26 s and 17 s after the teleport). The cell mission: 12 stages, the two registered ones
among them. One search takes 6.6 to 10.4 s, and the game stands still meanwhile. docs/checkpoints.md, "Tested, stage
list".

Checked, stage table: three scripted runs on the RTX 5070 Ti (Linux, Proton 11, Series X profile, copies of saves,
no picture): two from the start of Chapter 1 (table built as the stages are reached; `checkpoint #4` from ch1-s3
lands on ch1-s4 both times) and one in the prologue (the cell mission: four registering scripts).
docs/checkpoints.md, "Tested, stage table".

## v0.2 - checkpoints (on inkVI v0.2.1, twelve patches)

- `checkpoint list` and `checkpoint <stage>` (patch 0012): jump to a stage of the running mission by writing the
  stage into the field the title keeps it in, failing the mission once with a far teleport and letting the title's
  own retry restart it there. Works from the start of the mission too. Chapter 1 only: ten stages known so far
  (`ch1-s1` .. `ch1-s4` plus six by hash, found by playing). A jump changes the stage, not what you carry.
  docs/checkpoints.md.
- The channel's `log.txt` gets a line for every stage the title announces (and every change of the stage field once
  it is known), so new stages can be recorded.
- Names file: `MISSION_STAGE_SET`, the native the title announces stages with.
- Capture receipts (`tools/capture-receipt.py`, by TomTomAIbot (ThomasHFWright), PR #1) are part of this version.
- New: a worked example, [A study on "clown vomit" (user-coined term)](docs/case-study-clown-vomit.md): how to use
  dive to catch a picture fault that only shows sometimes.

Checked: Four runs of a clean-clone build of this branch, Linux, Proton 11 (memory-view-tree wineserver), warm caches, Series X profile, copies of a save at the start of Chapter 1. The field was found unique every time (another address on each card). The far teleport crashed the title once (2 of 17 far teleports in the Chapter 1 opening so far, counting earlier tests).

| card | direction | from -> to | result |
|---|---|---|---|
| RTX 5070 Ti | backward | ch1-s3 -> ch1-s2 | retry 14 s after the teleport at ch1-s2; montage and boat cutscene again, then ch1-s3 by itself (2 runs) |
| RTX 5070 Ti | forward | ch1-s3 -> ch1-s4 | retry 14-15 s after the teleport at ch1-s4; in the boat on the river, control returned (2 runs) |
| RTX 5090 | backward | ch1-s3 -> ch1-s2 | 1st run: the title crashed in its own teleport (the fail step). 2nd run: retry 16 s after at ch1-s2, as on the Ti |
| RTX 5090 | forward | ch1-s3 -> ch1-s4 | retry 16 s after the teleport at ch1-s4; in the boat on the river, control returned |

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
