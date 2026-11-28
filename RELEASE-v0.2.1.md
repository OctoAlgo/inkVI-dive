# inkVI-dive v0.2.1: the stage list and skipping the intro videos

A follow-up to v0.2 with two things. `stages` reads the running mission's full stage list from the title's memory,
in play order, right from the mission's start, and `checkpoint #<n>` jumps to the n-th stage of it: you no longer
need to know a stage's hash, or to have reached it, to jump there. And `VICTORY_SKIP_BINK=1` skips the intro video
(a patch by C-GDev, ported by CuteBooty, taken unchanged).

**Limits first.** The jump still works in the Chapter 1 opening only. In the cell mission `stages` reads a list of
12, but the jump finds no stage field there. A stage in the list is not always a checkpoint: in Chapter 1, #10 is
never written to the stage field. Jumps were tested to 7 of the 24 Chapter 1 stages. What the others start with is
not recorded. The game stands still for 6 to 10 s while `stages` searches. It needs a mission that has registered a
stage. If it does not find exactly one list, it says so and uses the table of the stages registered so far. The
jump itself is the same as in v0.2, with the same limits: a mission must be running, it is failed on purpose, and
forward jumps skip story state, so use copies of saves. Finishing a mission after a jump and reaching free roam was
shown once, by hand; a jump in the next mission is not tested. The movie skip is off by default; we measured it
with `1` only, one run each with and without. It is the only patch of the kit that is in the release build too.
No ray tracing in this build. Diagnostics build only (except the movie skip), title build 1.0.2.1 (Series X
profile), Linux under Proton, NVIDIA cards.

## New

- Patch 0015: `VICTORY_SKIP_BINK`. Off by default. `1` skips the movies that play once (logos, the intro); `all`
  skips the looping ones too, and then the menu backgrounds stay dark. For test runs we recommend `1`. Not our
  code: C-GDev wrote it, CuteBooty ported it. [docs/skip-bink.md](docs/skip-bink.md).
- Patch 0014: the stage list. `stages` prints it with numbers and marks the stages registered so far, announced
  this session, and jump tested. `checkpoint #<n>` counts in it. `memfind` and `memdump`, the raw memory commands
  the list was found with. How it works: [docs/checkpoints.md](docs/checkpoints.md), "Stage list".
- Patch 0013: the stage table, recorded per registering script, with item counts and repeat registrations.
  `checkpoint list` prints it, and the channel's `log.txt` and the game log get one line per stage plus a summary.
  It is the fallback when the list is not found. [docs/checkpoints.md](docs/checkpoints.md), "Registration table".
- Names file: `MISSION_STAGE_ADD`, `MISSION_STAGE_ITEM`.

## Played by hand

octo, RTX 5090, a copy of a save at the start of Chapter 1 ("Gone Fishing"), this version with
`VICTORY_SKIP_BINK=1`: a jump to #24, the mission's last stage. He played the end of the mission. The mission
finished, and free roam came at Jason's house. A manual save and the autosave both worked; they showed in the
title's own save menu. One session, one mission.

**The way on: chain missions.** Jump to a mission's last stage, finish it, walk to the next mission, then `stages`
and `checkpoint #<n>` there. Whether the jump works in the next missions is not tested yet.

**Open: the real skip.** Starting any mission directly, without playing up to it, is an open question. We have no
lead that works yet. If you want to look into it, see [issue #ISSUE_NUMBER](https://github.com/OctoAlgo/inkVI-dive/issues/ISSUE_NUMBER).

## Tip: skip the start screen without a fixed timer

Watch two pixels of the game's picture at 1920x1080: one inside the white (A) circle of "PLAYER (A)" at the bottom
right, **x 1874, y 1034**, colour (249, 249, 249), and one on the dark background just right of it, **x 1900,
y 1034**, colour (32, 32, 44). Press A when the first is white (every channel 200 or more) and the second is dark
(every channel 80 or less) in two samples in a row. The background pixel is there so that a white flash does not
trigger it. In the title's own 3840x2160 frame (what `cap` saves on the Series X profile) the same points are
x 3748, y 2069 and x 3800, y 2069.

Checked on full-size captures from three runs (RTX 5070 Ti): the rule held on all 80 captures of the start screen
and on none of the 54 others (black frames, the intro movie, the loading screen, the world). We caught no white
flash. The 1920x1080 points are those of the full-size frame scaled down. Other sizes and aspects are not measured
yet. A built-in version is planned for a later dive version.

Until then, a simple way in: `VICTORY_SKIP_BINK=1 VICTORY_KEYS=r1/10:Enter` presses Enter every 10 presents from the
first one until the world runs, so the start screen is passed without watching it. On an RTX 5090 that took 29.6 s
from launch to world frame 25, in one run. It is a convenience, not a measured gain: in an earlier test on the
RTX 5070 Ti, pressing that often from the first frame was not faster than the slower timer (`r300/30:Enter`).

## Tested

Movie skip: a build made with `build.sh` from a clean clone (inkVI's 38 patches + these 15), its unit tests under
Wine (bink 2, stagelist 2, checkpoint 4: all pass), and three runs, RTX 5070 Ti headless, Linux, Proton 11, warm
caches, Series X profile, a copy of a save at the start of Chapter 1. No crash.

| `VICTORY_SKIP_BINK` | launch -> start screen | Enter on the start screen -> world frame 25 |
|---|---|---|
| `0` | 6.7 s | 34.5 s |
| `1` | 7.1 s (6.7 s in a third run) | 21.3 s; one movie skipped (450 frames, 3840x2160) |

The intro movie plays after the start screen, so the time to the start screen does not change. Launch is the game
log's first line; the start screen is the first capture that shows it (captures every 2.5 s). One run each.

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

Not tested: the stage list on the RTX 5070 Ti, `VICTORY_SKIP_BINK=all`, the release build, a restart from the
pause menu, and a jump in any mission after the first one of Chapter 1 (other than the cell mission).

## Credits

- Movie skip (patch 0015): written by C-GDev ([fxceless/victory-fork PR #613](https://github.com/fxceless/victory-fork/pull/613),
  not merged there); ported by CuteBooty ([trustno1-coder/VIctory-NVIDIA PR #26](https://github.com/trustno1-coder/VIctory-NVIDIA/pull/26),
  commit e31f4740); the idea from XCL PR #1053. Taken unchanged, GPL-3.0.
- Stage list, stage table and checkpoint command: octo / inkVI.
- Capture receipts: TomTomAIbot (ThomasHFWright).
- The base: fxceless/victory-fork and Marvisak/VIctory, through inkVI.

*(written with AI assistance)*
