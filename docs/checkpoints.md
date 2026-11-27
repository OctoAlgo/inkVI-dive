# Checkpoints: jump to a mission stage

`checkpoint` is a test and debug tool. It gets a running mission to one of its stages (checkpoints) quickly, so a
tester can look at a stage again, or reach a later one, without playing there. It is not a mission skip, a save
editor or a trainer, and it only knows a few stages so far.

Diagnostics build only, with `VICTORY_NATIVES=1` and the kit's `tools/natives-names.txt` (it needs the name
`MISSION_STAGE_SET`). The title's Xbox Series X build **1.0.2.1**, Series X profile. **Use it on copies of saves.**

## Limits first

- **Chapter 1 stages only.** Four stages of the Chapter 1 opening mission are known (`checkpoint list`). Other
  missions have stages too, but their hashes are not collected yet (see "Recording new stages").
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

See the release notes of v0.2 for the runs (cards, directions, stages, results).

## Credits

The checkpoint study and the command: octo / inkVI. Capture receipts (used to share frames from such runs):
TomTomAIbot.
