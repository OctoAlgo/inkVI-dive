# inkVI-dive

Test tooling for VIctory: teleport, bookmarks, clock, cutscene replay and mission checkpoints from a command channel.

**A testing aid, work in progress.** It is for people who test VIctory builds and want to get the game to a place, a
time of day or a cutscene without playing there. Tested on Linux under Proton with NVIDIA cards only (RTX 5090,
RTX 5070 Ti), with the title's Xbox Series X build **1.0.2.1** on the Series X profile. It is not a script hook or a
mod API: nothing is loaded into the game's scripts, and no command works on another build of the title.

Source only: a pinned [inkVI](https://github.com/OctoAlgo/inkVI) version (v0.2.1), twelve patches on top of it, a build
script, a few small scripts and this README. Every tool is in the **diagnostics build** only and stays off unless its
switch is set. GPL-3.0, like inkVI and victory-fork.

## What's in it

| patches | what | switch |
|---|---|---|
| 0001 | A command channel: a folder whose file `cmd` the layer reads every fourth frame; the answers go to `reply.txt` and `log.txt`, and `done` appears when everything is back. Raw memory commands (`peek`, `poke`, `base`, ...). | `VICTORY_DEBUG=<folder>` |
| 0002-0006 | The title's script natives from the channel: the layer hooks the call the title's script interpreter makes for every native, and runs queued calls on a script thread, where the title calls them itself. On top: `pos`, `tp`, `time`, `date`, bookmarks, cutscenes (`scene ...`), any native by name or hash (`ncall`), a trace of what the scripts call. | `VICTORY_NATIVES=1` (`trace`, `log` for the traces) |
| 0007 | The two hook sites found by byte pattern (each must occur exactly once in the executable's code), not by fixed address. | - |
| 0012 | `checkpoint`: jump to a stage (checkpoint) of the running mission, and a log line for every stage the title announces. Chapter 1 stages only so far; see [docs/checkpoints.md](docs/checkpoints.md). | `VICTORY_NATIVES=1` |
| 0008-0011 | Captures for testing pictures: full-size frames, raw rows, a wall-clock window, a window after every start of a chosen cutscene, `cap [<n>]` from the channel, and captures when no swap chain can be made (headless second cards). | `VICTORY_CAPTURE_*` (below) |

`patches/README.md` lists every patch with its files and licence.

## How to build

The same needs as inkVI (git, the base's Rust toolchain; for a Linux cross build clang-cl, lld-link, llvm-lib and an
MSVC SDK, e.g. from xwin):

    XWIN=/path/to/xwin-sdk sh build.sh /path/to/empty-dir        # --check: cargo check only; --release-too: + release

Output: `<dir>/src/target/x86_64-pc-windows-msvc/diag/victory.exe` (the diagnostics build; the release build has none of
the tools). Offline: `INKVI_KIT=<inkVI checkout at the pinned commit>` and `FORK_URL=<victory-fork clone>`.

## How to run

Launch the diagnostics build the way inkVI's `launch/README.md` says, with these in the game's environment (Windows
paths, as the layer sees them; under Proton `Z:\` is the Linux root):

    VICTORY_DEBUG='Z:\home\you\dive\channel'                   # the channel's folder (made if missing)
    VICTORY_NATIVES=1                                            # the natives hook
    VICTORY_NATIVES_NAMES='Z:\home\you\inkVI-dive\tools\natives-names.txt'
    VICTORY_DEBUG_BOOKMARKS='Z:\home\you\dive\bookmarks.txt'    # optional; tools/bookmarks.example.txt to start from

**Which Proton:** we run on Proton 11 with a patched wineserver that keeps memory views in a tree
([CachyOS/wine-cachyos PR #50](https://github.com/CachyOS/wine-cachyos/pull/50),
[Wine bug 60868](https://bugs.winehq.org/show_bug.cgi?id=60868)) and with warm shader and pipeline caches. On stock
Proton 11 with cold caches the same build ran at 1-2 frames a second and models and textures did not stream in, on both
cards. If your Wine already has that fix you need nothing extra; say which Proton and whether the caches were warm
next to any number you report.

Then, from any shell, while the game runs:

    tools/dcmd.sh ~/dive/channel pos
    tools/dcmd.sh ~/dive/channel "time 7 30" "tpgo cell"          # several lines, run in order
    DQUIET=1 tools/dcmd.sh ~/dive/channel pos date                # only the answers

`dcmd.sh` writes the lines to `cmd`, waits for `done` (`DWAIT` seconds, 60) and prints `reply.txt`: each command, one
line per native call it made, and the answer. By hand: `printf 'pos\n' > cmd.tmp && mv cmd.tmp cmd`, then read
`reply.txt` once `done` exists. A line `@w<N> <command>` waits for world frame N, so a `cmd` file written before the
launch runs without anyone at the keyboard (`@w600 tpgo cell`).

Commands that call natives are queued and run when the next script calls a native (the same frame in the world,
within a second on the start screen). While the title's scripts stand still (some loading phases) nothing comes back.

## Commands

Checked in the game (build 1.0.2.1, Series X profile). The last line of each reply is the answer.

| command | does | example answer |
|---|---|---|
| `pos` | the player's position, heading and the clock | `pos -2755.401 -2914.841 12.284 heading 1.36 time 07:30:00` |
| `tp <x> <y> <z> [<heading>]` | teleports with the title's own setter: the area streams in and the player is held until the ground is there. Heading in degrees (0 = north / +y, 90 = west / -x) | `pos -2754.900 -2914.600 12.300 heading 90.00 time 07:30:00` |
| `tpsave <name>` / `tpgo <name>` / `tpmarks` | bookmarks: save here, go there (position, heading and, if saved, the time of day), list | `saved `cell -2755.401 -2914.841 12.284 1.36 0.00 07:30` in ...` |
| `time` / `time <hh> <mm> [<ss>]` | read / set the time of day (an earlier hour moves to the next day) | `time 09:15:30` |
| `date` / `date <day> <month> <year>` | read / set the date (month 1-12); a day the month does not have is refused by the title | `date 24 12 2025` |
| `scene ...` | cutscenes, see below | |
| `cap [<n>]` | save the next n frames (needs `VICTORY_CAPTURE`) | `cap: presents 1873..1874 are saved` |
| `ncall <NAME\|0x<hash>\|+0x<rva>\|m+0x<rva>> [ret=<n>] [><var>] [wait=<secs>] [<arg>...]` | any native or script-class method | `#310 SET_CLOCK_TIME ... 9 15 30 -> ret [0x0]` |
| `checkpoint list` / `checkpoint <stage>` | the known mission stages and the current one / jump to a stage of the running mission (see Checkpoints) | `checkpoint done: the title retried the mission 21 s after the teleport at ch1-s2 (0x33824f3b) ...` |
| `nstat`, `nfind`, `nscript`, `ntrace`, `nmark`, `nwatch`, `ndump`, `nlog`, `nhelp` | the hook's state, which script runs queued calls, traces | |
| `peek`, `peekf`, `poke`, `pokef`, `base`, `help` | raw memory (no natives needed) | |

`ncall` arguments are 8-byte slots: `12`, `-5`, `0x1f`, `1.5`, `h:TEXT` (the title's name hash of the lower-cased
text), `s:TEXT` (a C string; `~` = space), `v:x,y,z` (a vector, two slots), `buf:<n>`, `$var` / `$var.<i>` (what an
earlier call stored with `>var`). `ret=<n>`: slots returned (2 for a vector or an entity). `wait=<secs>`: repeat every
100 ms until the first returned slot is not 0.

    ncall PLAYER_PED_ID ret=2 >p
    ncall GET_ENTITY_COORDS ret=2 $p 0        -> ret [...] vec(x, y, z)
    ncall SET_FOCUS_POS v:-2367.2,-4399.4,1.9 25.0 1

Names are in `tools/natives-names.txt`: `NAME 0x<hash>` for natives (the hashes are the title's own, kept in each
native), `NAME m+0x<rva>` for methods. The names are ours, given by what the natives were seen to do; the title
ships no names.

Traces: `VICTORY_NATIVES=trace` counts every native and keeps its first three calls (`ndump` writes
`natives-trace.tsv`); `VICTORY_NATIVES=log` keeps every call (`nlog` writes `natives-log.tsv`;
`VICTORY_NATIVES_LOG_PER=400` keeps only each native's first 400). `tools/ntrace.py` and `tools/nlogx.py` read them.
Finding the natives behind something new: run with `log`, do the thing, `nlog`, then
`nlogx.py natives-log.tsv ms=<from>-<to> max=12` (rare calls in that time window).

## Checkpoints

A test tool for reaching a mission stage quickly: `checkpoint <stage>` writes the stage into the field where the title
keeps the running mission's current stage, makes the mission fail once with a far teleport, and lets the title's own
retry restart the mission at that stage, with its own scenes, clock and placement. Backward and forward jumps work in
the Chapter 1 opening (four known stages, `ch1-s1` .. `ch1-s4`); nothing else is shown yet.

    DWAIT=300 tools/dcmd.sh <channel> "checkpoint list"
    DWAIT=300 tools/dcmd.sh <channel> "checkpoint ch1-s2"

Limits, up front: Chapter 1 stages only; a mission must be running (one that fails by distance); the jump fails the
mission on purpose; passing a mission, free roam and later chapters are not shown; a forward jump skips whatever the
skipped stages would have set, so never keep playing on that save; the field's address differs by build (it is found
fresh every time, and the command refuses if it does not find exactly one); the far teleport it uses crashed the
title in 2 of 17 tries so far; copies of saves only. Every stage the
title announces is written to the channel's `log.txt`, so new stages can be recorded. Details, options and how it
works: [docs/checkpoints.md](docs/checkpoints.md).

## Cutscenes

The title makes a cutscene ("scene") with one native from a name hash and drives it through methods of the object
it returns: give entities their roles, load, wait until ready, start, wait until ended. The names are hashes of texts
that are not in the executable, so scenes are addressed by the hashes the scripts use (`scene list` shows them).

    scene list                       every scene a script (or the channel) made: name, flags, object, script, time
    scene use <0xobject|0xname>      the next scene commands act on that existing object
    scene state                      -> scene <obj> ready <0|1> playing <0|1> phase <0..1> ended <0|1>
    scene start | stop
    scene new <0xname|text> [<flags>]    a new scene object (flags 0x220 = cutscene)
    scene ent <role>                 the player gets the role (lucia, jason) in it
    scene load ; scene wait [<secs>]
    scene play <0xname> [<flags>] [as=<role>]    = new + ent + load + wait + start + state

Known scenes of 1.0.2.1: `0xfa252252` the prison cell's opening cutscene (`as=lucia`); `0xf2d9d324` the first cutscene
of Chapter 1; `0x97f69b27` the Chapter 1 montage with the iguana shot (`as=jason`, about 60 s); `0x2981b9ff` the
cinematic-bars timeline. `nscript 0x<script id>` before `scene new` runs the calls inside that mission script
(`nscript any` undoes it): the cell's mission script is `0xb5ddd565`, Chapter 1's `0x72e73a29`.

## Captures

Diagnostics build, with `VICTORY_CAPTURE=<folder>`:

| switch | does |
|---|---|
| `VICTORY_CAPTURE_FULL=1` | full-size frames (default: every second pixel and row) |
| `VICTORY_CAPTURE_RAW=1` | raw rows (`frame-<n>-<w>x<h>-<rgba\|bgra>-p<pitch>.raw`) instead of PNG: much faster to save |
| `VICTORY_CAPTURE_SECS=<a>-<b>` | with `VICTORY_CAPTURE_WORLD=1`: every frame from a to b seconds after world frame 0 |
| `VICTORY_CAPTURE_SCENE=0x<name>:<a>-<b>` | every frame from a to b seconds after each start of that cutscene, the title's or the channel's (needs `VICTORY_NATIVES`) |
| `cap [<n>]` (channel) | the next n frames |

To share the exact frames from a running session, request a short burst
and wait for the corresponding PNG or raw files to finish writing:

```sh
python3 tools/capture-receipt.py ~/dive/channel ~/dive/captures --count 3 > capture.json
```

The JSON gives each title Present number, local filename, dimensions, byte
count and file SHA-256. Use a separate capture directory per run and one
command sender per channel. Attach the receipt with your scene, build,
profile and settings when reporting a comparison. Image hashes identify
the files from that run. Independently rendered frames can differ.

Cutscenes keep to the wall clock, not to frames: at a low frame rate a short shot is only a few frames, wherever the
capture starts. Without a swap chain (a second card on a virtual X server: "surface is not supported for
presentation") wanted frames are still read back and saved.

## Worked example: catching a fault that only shows sometimes

[A study on "clown vomit" (user-coined term)](docs/case-study-clown-vomit.md): how to use dive to catch a picture fault
that only shows sometimes (captures pinned to a cutscene's clock, one change per run, a control run).

## Worked example: the iguana shot, played twice

The Chapter 1 montage has a 1.2-second close-up of an iguana on a road under an overpass. To look at it again and
again without playing through the opening:

1. Run a copy of a save at the start of Chapter 1 with `VICTORY_DEBUG`, `VICTORY_NATIVES=1`, the names file, and
   `VICTORY_CAPTURE=<folder> VICTORY_CAPTURE_FULL=1 VICTORY_CAPTURE_RAW=1 VICTORY_CAPTURE_SCENE=0x97f69b27:12-17`. Only the
   start screen needs a key. The title plays the montage once; the capture switch saves the frames 12-17 s after its
   start (the iguana is about 13-15 s in).
2. Wait until the montage and the mission's next cutscene (the boat, "Gone Fishing", `0x048647ec`) have ended and the
   player is in control at the dock:

       dcmd.sh <channel> "scene use 0x048647ec" "scene state"       # ... ended 1
       dcmd.sh <channel> "cap 1" pos                                 # a frame at the dock

3. Play the montage again from the channel; the same capture switch saves the same moment of the replay:

       dcmd.sh <channel> "nscript 0x72e73a29" "scene play 0x97f69b27 as=jason"

What we saw (RTX 5090, 3840x2160, render scale 1.0, 5-6 frames a second; 32:9 tests will come with the next
inkVI-ultrawide update): the iguana is the full textured model in
the title's own pass and in the replays. The replays are lit differently: bright and sunlit in one, a black
silhouette in the others (also on an RTX 5070 Ti). A replay from the channel runs without the title's cutscene handlers (see Limits), so take
lighting differences between passes as an effect of the tool, not of the game. At about 1-2 frames a second the first
pass showed no iguana at all (the road was not drawn either) and later replays a stand-in model: streaming had not
caught up, and a replay sees what the first pass loaded.

Tip: the replay can be started right after the montage, but then it runs over the mission's boat cutscene and the two
take turns on screen. Wait for `ended 1` of `0x048647ec` first.

## How it works

The title has no table of natives. Each of its 6820 native handlers starts with `cmp dword [rcx+10h], 0` and holds
its own 64-bit hash; the layer finds them through the executable's function table by that shape. Scripts call a
native from the interpreter's NATIVE opcode, `lea rcx,[rsp+disp32] ; vzeroupper ; call r15`, and class methods
through a by-ID call, `lea rcx,[rsp+28h] ; lea r14,[rbx+disp32] ; lea rdi,[rbx+disp32] ; call [rax]`. Both sites are
found by these byte patterns, displacements open, and are used only if each occurs exactly once in the executable's
code sections; in 1.0.2.1 they are at +0x3de7503 and +0x3de2331 (a host test checks this against the executable when
`VICTORY_TITLE_EXE` is set). Each site is replaced by a call to a small stub near the image that passes the call's
context, the handler and the calling script to the layer, which first runs any queued calls, then the one the
script asked for. The hook is applied only to the executable whose BLAKE3 starts with `b99f876b74d4a77f`
(Series X 1.0.2.1).

Teleports, the clock and cutscenes use the title's own natives, so the title does what it does when its scripts call
them: a `tp` streams the area in and holds the player until the ground is there.

## Limits

- **1.0.2.1 only.** The hook refuses any other executable. The method addresses in the names file (`m+0x...`: the
  scene methods) and two structure offsets in the code (which script is calling, a scene's id) are those of this
  build; the hook sites themselves are found by pattern.
- **Cutscenes by hash.** The scene names are hashes of texts that are not in the executable; only scenes a script has
  made (`scene list`) or whose hash you already know can be played.
- **A replayed cutscene lacks the title's handlers.** The title subscribes its own script functions to a scene's
  events (camera, player, light). A scene started from the channel has none: between its shots the gameplay camera
  shows for some frames, the player is not frozen, the mission's own scenes keep running, and the lighting can differ
  from the title's pass. The player is left where the cutscene put them (after the cell's cutscene: 3.3 km away, clock
  15:00); `tpgo` back.
- **A scene made from the channel is never freed** (its id is taken from the garbage-collected script object on
  purpose, or the scene dies within seconds). Fine for a test session, not for hours of replays.
- **Far teleports and missions.** During a mission a far `tp` fails the mission by distance, not because of the
  jump: in the Chapter 1 opening (boat stage) steps of 25, 50, 100 and 200 m west of the dock held, and at 300 m the
  mission restarted within 10 s (the player put back, the clock frozen). A `tp` shortly after such a restart crashed
  the game inside the title's own teleport: wait until the mission runs again (`pos` shows the clock moving). Far
  teleports outside missions are untested (we have no free-roam save yet). `checkpoint` keeps to this: it refuses
  while the clock stands still and for 60 s after a retry, and never teleports after the retry it caused.
- **Checkpoints:** Chapter 1 stages only, and the jump fails the mission on purpose (docs/checkpoints.md).
- **One crash cause to avoid:** never call `SCENE_ON_EVENT` (`m+0x4bfdb10` / `m+0x4bfdbb0`) by hand. Its second
  argument is a script function; anything else is called as one when the event fires and the game faults.
- `ncall` with a wrong argument count or a made-up pointer can crash the game, and `m+0x<rva>` with a wrong address
  or object will: it is a debugging tool. Use copies of saves; the commands change the game state.
- `time` to an earlier hour moves the date one day on.

## Next

Next: shareable test cases (stage, scene and capture window in one file, with receipts), a 'seconds until settled' measure for how long a scene takes to stream in after a cut, and stages beyond Chapter 1.

After that: a basic UI for the commands, an in-game menu or overlay, so the commands need no terminal.

Looking into, not promised: the title's own camera and player handlers for replayed cutscenes, weather, and checkpoint
stages of more missions.

## Credits

- [fxceless/victory-fork](https://github.com/fxceless/victory-fork) and [Marvisak/VIctory](https://github.com/Marvisak/VIctory):
  the base, through inkVI.
- The name hash (Jenkins one-at-a-time over lower-cased text) and the naming style of the script natives are community
  knowledge; every hash, address and behaviour here was read from our own copy of the title and checked in the game.
- Checkpoints (the study and the `checkpoint` command): octo / inkVI.
- Capture receipts (`tools/capture-receipt.py`): TomTomAIbot.

## What this kit ships, and what it does not

Ships: twelve patches (all our own, GPL-3.0), a build script, `tools/` (`dcmd.sh`, the trace readers `ntrace.py` and
`nlogx.py`, `capture-receipt.py` and its test, `natives-names.txt`, `bookmarks.example.txt`), this README, `docs/`, a
changelog and the licence.
Does not ship: any binary, the title or any of its files, inkVI's or victory-fork's code (fetched at pinned commits by
`build.sh`), saves, traces, logs, frames, screenshots or other game images (one exception: the cropped two-frame comparison
of a shirt collar in `docs/images/`, for the case study), and no strings or tables extracted from the title. Of the title it contains only facts needed to find and call things: the two byte patterns above, the build's
hash prefix, native hashes and method addresses in the names file, four Chapter 1 stage hashes, and a few addresses in
comments and examples.

## Licence

GPL-3.0 (`LICENSE`).
