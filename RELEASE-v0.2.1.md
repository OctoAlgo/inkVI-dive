# inkVI-dive v0.2.1: the stage table

A small follow-up to v0.2. dive now records the stages a mission registers, in the order the title registers them.
`checkpoint list` prints them, and `checkpoint #<n>` jumps to the n-th one. You no longer need to know a stage's hash
to jump to it.

**Limits first.** The table is not the whole mission. In the Chapter 1 opening, the title registers stages as the
mission reaches them, not all at its start. So the table lists only the stages reached so far, and you cannot read
the later ones from it in advance. A registered stage is not always a checkpoint you can jump to. "Items" is a size
hint whose meaning is not known. The jump itself is the same as in v0.2, with the same limits: a mission must be
running, it is failed on purpose, and forward jumps skip story state, so use copies of saves. Diagnostics build only,
title build 1.0.2.1 (Series X profile), Linux under Proton. This version was tested on the RTX 5070 Ti only, with no
picture.

## New

- Patch 0013: the stage table, recorded per registering script, with item counts and repeat registrations.
  `checkpoint list` prints it, the channel's `log.txt` and the game log get one line per stage plus a summary, and
  `checkpoint #<n>` jumps to a stage by its place in the table. How to read it:
  [docs/checkpoints.md](docs/checkpoints.md), "Stage table".
- Names file: `MISSION_STAGE_ADD`, `MISSION_STAGE_ITEM`.

## Tested

Three scripted runs, RTX 5070 Ti, Linux, Proton 11, Series X profile, copies of saves, no picture.

| save | what | result |
|---|---|---|
| start of Chapter 1 | table at mission start | 2 stages at the start (ch1-s1, ch1-s2); ch1-s3 and ch1-s4 added on entering them (2 runs) |
| start of Chapter 1 | `checkpoint #4` from ch1-s3 | landed on ch1-s4; the title retried 14 s after the teleport, as with the hash (2 runs) |
| prologue (the cell mission) | tables | the mission registered 2 stages; three helper scripts registered 7, 2 and 1 |

Not tested: the RTX 5090 for this version, and a restart from the pause menu.

## Credits

- Stage table and checkpoint command: octo / inkVI.
- Capture receipts: TomTomAIbot (ThomasHFWright).
- The base: fxceless/victory-fork and Marvisak/VIctory, through inkVI.

**Next:** shareable test cases (save, stage, scene and capture window in one file, with receipts), automatic cutscene
skipping to reach a test point fast, a one-key snapshot, a "seconds until settled" measure for streaming after a cut,
and picture diffs between two builds.

*(written with AI assistance)*
