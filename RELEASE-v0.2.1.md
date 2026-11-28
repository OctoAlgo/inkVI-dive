# inkVI-dive v0.2.1: the stage list

A small follow-up to v0.2. `stages` reads the running mission's full stage list from the title's memory, in play
order, right from the mission's start. `checkpoint #<n>` jumps to the n-th stage of it. You no longer need to know
a stage's hash, or to have reached a stage, to jump to it.

**Limits first.** The jump still works in the Chapter 1 opening only. In the cell mission `stages` reads a list of
12, but the jump finds no stage field there. A stage in the list is not always a checkpoint: in Chapter 1, #10 is
never written to the stage field. Jumps were tested to 7 of the 24 Chapter 1 stages. What the others start with is
not recorded. The game stands still for 6 to 10 s while `stages` searches. It needs a mission that has registered a
stage. If it does not find exactly one list, it says so and uses the table of the stages registered so far. The
jump itself is the same as in v0.2, with the same limits: a mission must be running, it is failed on purpose, and
forward jumps skip story state, so use copies of saves. Diagnostics build only, title build 1.0.2.1 (Series X
profile), Linux under Proton.

## New

- Patch 0014: the stage list. `stages` prints it with numbers and marks the stages registered so far, announced
  this session, and jump tested. `checkpoint #<n>` counts in it. `memfind` and `memdump`, the raw memory commands
  the list was found with. How it works: [docs/checkpoints.md](docs/checkpoints.md), "Stage list".
- Patch 0013: the stage table, recorded per registering script, with item counts and repeat registrations.
  `checkpoint list` prints it, and the channel's `log.txt` and the game log get one line per stage plus a summary.
  It is the fallback when the list is not found. [docs/checkpoints.md](docs/checkpoints.md), "Registration table".
- Names file: `MISSION_STAGE_ADD`, `MISSION_STAGE_ITEM`.

## Tested

Stage list: four scripted runs, RTX 5090, Linux, Proton 11, Series X profile, copies of saves. Two used builds made
with `build.sh` from a clean clone.

| save | what | result |
|---|---|---|
| start of Chapter 1 | `stages` right after the mission start (2 stages registered) | 24 stages in play order, the same 24 as found by hand before (2 runs) |
| start of Chapter 1 | `checkpoint #13` from ch1-s3 | landed on `0x835ea26a`; the title retried 26 s after the teleport |
| start of Chapter 1 | `checkpoint #14` from ch1-s3 | landed on `0x210e0f0b` (never jumped to before); retry 17 s after the teleport |
| start of Chapter 1 | `stages` after a jump's retry | the same 24 (2 runs) |
| prologue (the cell mission) | `stages` | 12 stages, with the two registered ones as #2 and #3 |

Stage table: three scripted runs, RTX 5070 Ti, same setup, no picture.

| save | what | result |
|---|---|---|
| start of Chapter 1 | table at mission start | 2 stages at the start (ch1-s1, ch1-s2); ch1-s3 and ch1-s4 added on entering them (2 runs) |
| start of Chapter 1 | `checkpoint #4` from ch1-s3 (table only, before patch 0014) | landed on ch1-s4; the title retried 14 s after the teleport, as with the hash (2 runs) |
| prologue (the cell mission) | tables | the mission registered 2 stages; three helper scripts registered 7, 2 and 1 |

Not tested: the stage list on the RTX 5070 Ti, a restart from the pause menu, and missions after the first one of
Chapter 1 (other than the cell mission).

## Credits

- Stage list, stage table and checkpoint command: octo / inkVI.
- Capture receipts: TomTomAIbot (ThomasHFWright).
- The base: fxceless/victory-fork and Marvisak/VIctory, through inkVI.

**Next:** shareable test cases (save, stage, scene and capture window in one file, with receipts), automatic cutscene
skipping to reach a test point fast, a one-key snapshot, a "seconds until settled" measure for streaming after a cut,
and picture diffs between two builds.

*(written with AI assistance)*
