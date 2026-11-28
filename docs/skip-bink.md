# Skipping the intro videos (VICTORY_SKIP_BINK)

Patch 0015 skips the title's Bink movies when asked. It is not our code: C-GDev wrote it, CuteBooty ported it to
this tree, and we took it unchanged (see Credits).

**Limits first.** Off by default. Only the Bink exports bound when a DLL is loaded are wrapped; an export looked up
with `GetProcAddress`, or a second Bink DLL, is not skipped. `all` leaves the menu backgrounds dark. Measured with
`1` only, in one run each with and without, on the RTX 5070 Ti; `all` and the release build are not tested by us.
Unlike every other patch of this kit it is in both builds (diagnostics and release); unset, it binds nothing
differently.

| value | does |
|---|---|
| unset or `0` | nothing: every import is bound as before |
| `1` | skips the movies that play once (logos, the intro) |
| `all` | skips the looping ones too; the menu backgrounds stay dark |

For test runs we recommend `VICTORY_SKIP_BINK=1`.

## What it saves

The intro movie plays after the start screen, when you press A (Enter), not before it. So it does not change the
time to the start screen (about 7 s from launch in both runs), only the way from the start screen into the game.

| `VICTORY_SKIP_BINK` | Enter on the start screen -> world frame 25 |
|---|---|
| `0` | 34.5 s |
| `1` | 21.3 s (one movie skipped: 450 frames, 3840x2160) |

One run each, RTX 5070 Ti headless, Linux, Proton 11, warm caches, Series X profile, a copy of a save at the start
of Chapter 1, a clean-clone `build.sh` build. Times from the game log; Enter sent through the keys file when a
capture showed the start screen.

## How it works

The title's own Bink DLL stays loaded and opens every movie as before. Nine exports a player loop calls on an open
movie (`BinkWait`, `BinkDoFrame*`, `BinkNextFrame`, `BinkGoto`, `BinkShouldSkip`, `BinkClose`) are bound to small
wrappers. A movie that is skipped is put on its last frame before its first frame is shown, so the title's own
end-of-movie check ends it at once. Each movie is looked at once, when its looping flag is final, and the game log
gets one line for it (`Bink movie width=... frames=... looping=... skip=...`). No file, network or process access.

## Credits

- C-GDev wrote it: [fxceless/victory-fork PR #613](https://github.com/fxceless/victory-fork/pull/613), commit
  75fe122c (not merged in the fork).
- CuteBooty ported it to this tree: [trustno1-coder/VIctory-NVIDIA PR #26](https://github.com/trustno1-coder/VIctory-NVIDIA/pull/26),
  commit e31f4740. The patch is that commit, with CuteBooty as its author; we only added the kit's trailers.
- The idea is from XCL PR #1053.
- GPL-3.0, like the source repository (its `LICENSE`).
