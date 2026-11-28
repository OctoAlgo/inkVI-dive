# Checkpoints: jump to a mission stage

`checkpoint` is a test and debug tool. It gets a running mission to one of its stages (checkpoints) quickly, so a
tester can look at a stage again, or reach a later one, without playing there. It is not a mission skip, a save
editor or a trainer, and the jump works in one mission so far.

Diagnostics build only, with `VICTORY_NATIVES=1` and the kit's `tools/natives-names.txt` (it needs the name
`MISSION_STAGE_SET`). The title's Xbox Series X build **1.0.2.1**, Series X profile. **Use it on copies of saves.**

## Limits first

- **Jumps in Chapter 1 only.** `stages` reads the running mission's full list (24 stages in the Chapter 1 opening,
  12 in the cell mission; see "Stage list"), but the jump works only in the Chapter 1 opening so far. In another
  mission the command finds no stage field and writes nothing.
- **A jump changes the stage, not your state.** What you carry stays: after a jump back to a stage before a weapon is
  handed over, you still have the weapon. A death in the game restarts at the last stage the title wrote, the same
  way as the jump.
- **A mission must be running**, and it must be one that fails when the player is teleported far away. The Chapter 1
  opening does (between 200 and 300 m). Others may not: the prison cell mission, for one, did not fail from a 3 km
  teleport, so the jump does not work there yet.
- **The jump fails the mission on purpose.** The title's own retry is what restarts the mission at the chosen stage.
  You see the fail, then the retry.
- **Not shown:** passing a mission, starting the next one, free roam, any chapter after the first.
- **Forward jumps skip story state.** Whatever the skipped stages would have set (objects, flags, things picked up)
  is not set. The stage plays from its start as the title restarts it, but the rest of the game may not match.
  Never keep playing on a save that went through a forward jump.
- **Addresses differ by build.** The stage is kept in a field whose address changes with every build of the layer.
  `checkpoint` looks for it fresh every time and refuses when it does not find exactly one.
- **No teleport after a retry for a while.** A teleport about 40 s after a retry once crashed the title inside its own
  teleport. `checkpoint` refuses while the clock stands still and for 60 s after a retry, and it never teleports
  after the retry it caused. Some stages hold the clock (ch1-s4 does); `force` skips the clock test there, but still
  waits 120 s after a retry.
- **The far teleport can crash the title.** Its own teleport faulted in 2 of 17 far teleports in the Chapter 1
  opening so far: once about 40 s after a retry, once in a v0.2 test on the RTX 5090 with the clock moving and no
  retry before (the same fault both times). The next run of the same test passed. Keep nothing you need in that
  session.
- Tested on Linux under Proton with NVIDIA cards only (RTX 5090, RTX 5070 Ti).

## Commands

    checkpoint list
    checkpoint <stage> [dist=<m>] [wait=<s>] [slot=<addr>] [force]

`<stage>` is a label from the list (`ch1-s1` .. `ch1-s4`) or a stage hash (`0x33824f3b`).

| stage | hash | starts |
|---|---|---|
| ch1-s1 | `0x489b8c77` | the mission's first stage (opening cutscene) |
| ch1-s2 | `0x33824f3b` | from the montage |
| ch1-s3 | `0x7bf09c68` | boat gameplay at the dock |
| ch1-s4 | `0x8cf171f3` | in the boat on the river (control returned) |

`<stage>` can also be `#<n>`, the n-th stage of the running mission's full list (`stages`, see "Stage list"). Found
by playing on 11-28, in this order after ch1-s4 (no labels yet; use the hash or the number, e.g. `checkpoint
0x27788afc` or `checkpoint #9`; what each one starts is left out to avoid spoilers):

| order | hash | jump tested |
|---|---|---|
| 5 | `0x33202f8f` | yes |
| 6 | `0xfa7c8d56` | |
| 7 | `0x0fe610ad` | |
| 8 | `0x27788afc` | yes (straight from the start of the mission) |
| 9 | `0xf6787e02` | |
| 10 | `0xd9ddaa4f` | |

`0x4bb7a448` is announced between 8 and 9 but never written to the field, so it is not a checkpoint. The full list
has 24 stages; `stages` prints them all.

`checkpoint list` prints these, any stage hash the title announced this session that has no label yet, the
current stage read from the stage field, and the last stage the title announced.

A jump takes about half a minute; use a longer wait with `dcmd.sh`:

    DWAIT=300 tools/dcmd.sh <channel> "checkpoint ch1-s2"

The reply, step by step: the candidate fields, the field that is left after a second look, the write, the teleport,
then `checkpoint done: the title retried the mission ... at ch1-s2 ... the field reads ch1-s2`, or
`checkpoint STOPPED: <why>`. Options:

- `dist=<m>` how far west the teleport goes (300; 50 to 5000).
- `wait=<s>` how long to wait for the retry (120).
- `slot=<addr>` use this field instead of looking (only if you checked it with `checkpoint list` / `peek`).
- `force` teleport even though the clock stands still (see Limits).

## Stage list

Since v0.2.1, `stages` prints the running mission's full stage list, in play order, read from the title's memory.
No stage hash has to be known for it. `checkpoint #<n>` jumps to the n-th stage of this list.

    DWAIT=60 tools/dcmd.sh <channel> stages

Right after the start of the Chapter 1 opening mission (2 stages registered so far):

    stage list of script 0x72e73a29 (registered last): 24 stages in play order, read from memory: array 0x12c957218
    of list object 0x12cae9050 (count 24); the reversed copy at 0x12ca91700 agrees
      #1 0xc4c1cba4 (no label)
      #2 ch1-s1 (0x489b8c77)  registered  announced
      #3 ch1-s2 (0x33824f3b)  registered  jump tested
      #4 ch1-s3 (0x7bf09c68)
      ...
      #13 0x835ea26a (no label)  jump tested
      ...
      #24 0xc10ae147 (no label)  jump tested
    (2 of them registered so far; checkpoint #<n> counts in this list)

`registered`: the mission has registered it so far (see "Registration table" below). `announced`: the title
announced it this session. `jump tested`: a jump to it was run in our tests. `stages 0x<script>` reads the list of
another script that registered stages (a helper of the mission).

Limits:

- **A stage in the list is not always a checkpoint.** In Chapter 1, #10 (`0x4bb7a448`) is never written to the stage
  field. Jumps were tested to 7 of the 24 (#3, #5, #6, #9, #13, #14, #24). What the other stages start with is not
  recorded.
- **The jump itself still works in Chapter 1 only.** In the cell mission `stages` reads a list of 12, but
  `checkpoint` finds no stage field there and writes nothing.
- **The game stands still while it searches:** 6 to 10 s per `stages`, about 9.5 s for `checkpoint #<n>`
  (RTX 5090). It reads all of the process's writable memory three times.
- **It needs a mission that has registered a stage.** The registered stages are the anchors of the search.
- **Exact or nothing.** If it does not find exactly one list, it says what it found and uses the registration table
  instead. A helper script of the cell mission had no list it could find.
- The structure was read in build 1.0.2.1 only. Its addresses change between runs, so none is built in.

How it finds the list. The title keeps each stage of a mission as a 32-byte heap object `{type, stage hash, 0,
pointer, 0}`, all of one type. The mission's list is a list object `{type, data, count, capacity}`. Its `data` is an
array object: a short header that ends with the stage objects' type, then `count` pointers to the stage objects, in
play order. `stages` takes the stages the mission has registered so far, finds their objects by shape, then every
array of pointers to objects of that type that holds them, then each array's list object. It uses a list only if
exactly one (by content) has a list object whose count is the array's length and holds the registered stages in
the order they were registered. Our own search buffers are left out. A second copy, 16-byte slots `{type, stage
hash, 0}` in reverse order, is checked against it ("the reversed copy agrees"; after one of two retries it was not
found, which does not matter). After a retry the title builds the list again (new objects); it was found again.

`memfind <u32>...` and `memdump <addr> <len>` are the two raw commands the list was found with. `memfind` writes
every place a 4-byte value occurs (at most 2000 per value, with 64 bytes around it) to the channel's `find.txt`;
`memdump` saves raw bytes to `dump-<addr>.bin`. Our own buffers show up in `find.txt` too.

### Registration table (the fallback)

The hook also records stage tables. The title registers a mission's stages one by one through a native
(`MISSION_STAGE_ADD`, in the names file) and asks for the items of each stage through another (`MISSION_STAGE_ITEM`).
The hook keeps, per registering script (a mission, or a helper script of it), the stages in the order they were
registered, with how many items were asked for under each and how many times the stage was registered.
`checkpoint list` prints all tables after the known stages; the script that registered last comes last:

    stage table of script 0x72e73a29 (registered last): 4 stages in the order the title registered them
      #1 ch1-s1 (0x489b8c77)  items 0  registered 1x
      #2 ch1-s2 (0x33824f3b)  items 24  registered 2x  jump tested

The channel's `log.txt` (and the game log) get one line per registered stage and, when the registrations pause for
3 s, one summary line:

    [present .. world ..] stage table 0x72e73a29 #3: ch1-s3 (0x7bf09c68)
    [present .. world ..] stage table 0x72e73a29: 3 stages: 0x489b8c77 0x33824f3b 0x7bf09c68 (items 0,24,16)

`checkpoint #<n>` counts in this table only when the stage list is not found (the reply says which one it counted
in).

The table is not the whole mission. In the Chapter 1 opening the title registers the stages as the mission reaches
them: two at the start (ch1-s1, ch1-s2), one more on entering ch1-s3 (ch1-s2 is registered again then), the next on
entering ch1-s4. Other notes:

- "Items" counts the distinct keys the title asked for under the stage so far; what they are is not known. It grows
  while the stage plays (ch1-s4: 4 on entering, 28 after the retry). Take it as a size hint only.
- `registered 2x`: registered again, after a retry or on entering the next stage.
- Several scripts register: in the prologue (the cell mission) four scripts did (see Tested). The mission is the
  one whose hash the title's mission native returns; that native is not hooked, so the table is by script and the
  mission is told by its hash from the known list.
- Needs `VICTORY_NATIVES=1` and the two names in `tools/natives-names.txt`.

## How it works

The title keeps the running mission's current stage as two 4-byte words, `{stage hash, 1}`, in a field of a
long-lived script object (its +0x70). When the mission fails, the title's retry kills the mission script and starts
it again, and the new script starts at the stage in that field: that is what a checkpoint is.

`checkpoint <stage>`:

1. Finds the field: every 8-byte-aligned `{known stage, 1}` in the process's writable memory, then only those whose
   next 4-byte word is 1 too, that are not part of a run of holders 18h apart (the script engine's stacks), and that
   still hold a stage two seconds later. Exactly one must be left, or nothing is written and the reply lists what
   was found.
2. Reads the position and the clock twice: the clock must move.
3. Writes `{target, 1}` into the field.
4. Teleports the player 300 m west with the title's own setter. The mission fails by distance.
5. Waits for the title's retry. The title announces every stage, and the retry, through one native (stage hash,
   restart flag); the hook sees that call. The reply gives the stage the title restarted at and what the field
   reads.

The title then plays the stage with its own scenes, clock and placement: in our tests the montage and the boat
cutscene played again after a jump back, and after a jump forward the player sat in the boat on the river with the
route to the next objective on the map.

A cleaner way to fail the mission than the far teleport was not found with the existing commands; the teleport is
the one proven way.

## Recording new stages

Every stage the title announces goes into the channel's `log.txt` (and the game log) as it happens:

    [present 4120 world 2890] stage ch1-s3 (0x7bf09c68) (announced by script 0xb63fe7d7)
    [present 6012 world 4210] stage ch1-s2 (0x33824f3b) RETRY (announced by script 0xb63fe7d7)

Once `checkpoint` (or `checkpoint list`) has found the field, every change of it is logged too
(`stage field 0x...: ch1-s2 (0x33824f3b) -> ch1-s3 (0x7bf09c68)`). Stages of other missions show as
`0x........ (no label)`. Please report them with the mission, the build and what the stage starts with.
A hash that was announced this session can be used with `checkpoint 0x<hash>` while that mission runs; the jump
itself is only proven for Chapter 1.

## Tested

Four runs of a clean-clone build of this branch, Linux, Proton 11 (memory-view-tree wineserver), warm caches, Series X profile, copies of a save at the start of Chapter 1. The field was found unique every time (another address on each card). The far teleport crashed the title once (2 of 17 far teleports in the Chapter 1 opening so far, counting earlier tests).

| card | direction | from -> to | result |
|---|---|---|---|
| RTX 5070 Ti | backward | ch1-s3 -> ch1-s2 | retry 14 s after the teleport at ch1-s2; montage and boat cutscene again, then ch1-s3 by itself (2 runs) |
| RTX 5070 Ti | forward | ch1-s3 -> ch1-s4 | retry 14-15 s after the teleport at ch1-s4; in the boat on the river, control returned (2 runs) |
| RTX 5090 | backward | ch1-s3 -> ch1-s2 | 1st run: the title crashed in its own teleport (the fail step). 2nd run: retry 16 s after at ch1-s2, as on the Ti |
| RTX 5090 | forward | ch1-s3 -> ch1-s4 | retry 16 s after the teleport at ch1-s4; in the boat on the river, control returned |

Then a hand-played session on the RTX 5090 (same build, `VICTORY_DT_MAX=0.2`):

| from | to | result |
|---|---|---|
| start of the mission (ch1-s1) | ch1-s4 | the mission failed, retry at ch1-s4 |
| start of the mission (ch1-s1) | `0x27788afc` | retry 14 s after the teleport at `0x27788afc` |
| `0x27788afc` | `0x33202f8f` (back) | retry 21 s after the teleport; the weapon picked up later stayed |
| prison cell (another mission) | `0x27788afc` | refused: no stage field found, nothing written |

## Tested, stage list (v0.2.1)

Four runs, RTX 5090 (octo chose to watch), Linux, Proton 11, copies of saves, Enter held through cutscenes. The last
two used builds made with `build.sh` from a clean clone of the kit, on earlier states of patch 0014 (it changed after
them only in the text of the fallback reply and in the "jump tested" mark for #14). No crash, no unhandled
exception.

| save | what | result |
|---|---|---|
| start of Chapter 1 | `stages` right after the mission start (2 stages registered) | 24 stages in play order, the same 24 as found by hand in memory before (2 runs; the first run's search found the same array). The array and its list object sat at the same addresses in all three runs |
| start of Chapter 1 | `stages` at ch1-s3 (4 registered) and after a jump's retry | the same 24 (2 runs each; after a retry the list object is a new one) |
| start of Chapter 1 | `checkpoint #13` from ch1-s3 | resolved to `0x835ea26a`; the title retried 26 s after the teleport at it. Then at -3489 -4547, clock 16:00 |
| start of Chapter 1 | `checkpoint #14` from ch1-s3 (never jumped to before) | resolved to `0x210e0f0b`; retry 17 s after the teleport at it. Then at -3496 -4582, clock 16:59 |
| prologue (the cell mission) | `stages` (2 registered), and 120 s later | 12 stages; the two registered ones (`0x08f2445f`, `0x2ed3a984`) are #2 and #3. #1 is `0xc4c1cba4`, the same first stage as in Chapter 1 |
| prologue (the cell mission) | `stages 0x36e7f7bd` (a helper, 6 registered) | no list found; the registration table was used, as designed |
| start of Chapter 1 | first version of the search (one run, before the list-object rule) | found the list and our own search buffer (an array of the very pointers looked for), and refused as ambiguous. That led to the two rules: a list object with the right count, and our buffers left out |

Search time per `stages`: 6.6 to 10.4 s (8 measures); `checkpoint #<n>`: 9.2 and 9.6 s. Earlier, by hand (RTX 5070
Ti, by hash): jumps to #13 and to #24 (`0xc10ae147`, with `force`) worked.

## Tested, stage table (v0.2.1)

RTX 5070 Ti, Linux, Proton 11, copies of saves, same setup as above, Enter held through cutscenes.

| card | save | what | result |
|---|---|---|---|
| RTX 5070 Ti | start of Chapter 1 | table at mission start | 2 stages at the start (ch1-s1, ch1-s2; items 0, 24); ch1-s3 added on entering it (ch1-s2 registered again), ch1-s4 on entering it. The same in both runs |
| RTX 5070 Ti | start of Chapter 1 | `checkpoint #4` from ch1-s3 | `#4` resolved to ch1-s4; the title retried the mission 14 s after the teleport at ch1-s4, as with the hash (2 runs, the first on an earlier build of this patch with older label text). ch1-s4 was then registered again, items 4 -> 28. No crash |
| RTX 5070 Ti | prologue (the cell mission) | tables | mission `0xb5ddd565` registered 2 stages (`0x08f2445f`, `0x2ed3a984`, items 0); helper scripts registered `0x36e7f7bd` 7 stages, `0xcbc14f15` 2, `0x889f3695` 1. The mission stayed in its first scene for 8 min (Enter held), so no later stage was reached |
| not tested | restart mission from the pause menu | not reached (no menu driver); a retry registers again (`registered 2x`) |

## Credits

The checkpoint study and the command: octo / inkVI. Capture receipts (used to share frames from such runs):
TomTomAIbot (ThomasHFWright).
