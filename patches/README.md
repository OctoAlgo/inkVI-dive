# The series

Applied in this order by `../build.sh`, after inkVI's own series (pinned in `../BASE`). Each patch carries
`Kit-Source:` and `Kit-Licence:` trailers. Everything is in the diagnostics build (`--features diagnostics`) and off
unless its switch is set; the release build is unchanged.

| # | patch | subject | switches | files | source | licence |
|---|-------|---------|----------|-------|--------|---------|
| 0001 | `0001-own-debug-channel.patch` | VICTORY_DEBUG command-file channel | `VICTORY_DEBUG`, `VICTORY_DEBUG_BOOKMARKS` | `crates/victory-gpu/src/{debugcmd.rs (new), lib.rs, queue.rs}` | own | GPL-3.0 |
| 0002 | `0002-own-natives-hook.patch` | VICTORY_NATIVES: the title's script natives from the channel (`ncall`, traces) | `VICTORY_NATIVES=1\|trace\|log`, `VICTORY_NATIVES_NAMES`, `VICTORY_NATIVES_WATCHMEM` | `Cargo.lock`, `crates/victory-gpu/{Cargo.toml, src/debugcmd.rs}`, `crates/victory-loader/src/{natives.rs (new), hooks.rs, lib.rs, windows.rs}` | own | GPL-3.0 |
| 0003 | `0003-own-natives-shorthands.patch` | pos, tp, time, date, bookmarks; the by-ID call path | `VICTORY_NATIVES_LOG_PER` | `crates/victory-loader/src/natives.rs` | own | GPL-3.0 |
| 0004 | `0004-own-scenes.patch` | scene (cutscene) commands, script-class methods, waiting calls | - | `crates/victory-gpu/src/debugcmd.rs`, `crates/victory-loader/src/natives.rs` | own | GPL-3.0 |
| 0005 | `0005-own-scene-play-no-events.patch` | `scene play` without event subscriptions | - | `crates/victory-loader/src/natives.rs` | own | GPL-3.0 |
| 0006 | `0006-own-channel-log.patch` | `log.txt` gets each reply once | - | `crates/victory-gpu/src/debugcmd.rs` | own | GPL-3.0 |
| 0007 | `0007-own-hook-site-patterns.patch` | the two hook sites by byte pattern, exactly once in the code sections | - | `crates/victory-loader/src/natives.rs` | own | GPL-3.0 |
| 0008 | `0008-own-capture-full.patch` | full-size captures | `VICTORY_CAPTURE_FULL=1` | `crates/victory-gpu/src/capture.rs` | own | GPL-3.0 |
| 0009 | `0009-own-capture-secs-raw.patch` | captures in a wall-clock window; raw rows | `VICTORY_CAPTURE_SECS=<a>-<b>`, `VICTORY_CAPTURE_RAW=1` | `crates/victory-gpu/src/capture.rs` | own | GPL-3.0 |
| 0010 | `0010-own-capture-scene.patch` | captures after every start of a cutscene; `cap [<n>]` | `VICTORY_CAPTURE_SCENE=0x<name>:<a>-<b>` | `crates/victory-gpu/src/{capture.rs, debugcmd.rs}`, `crates/victory-loader/src/natives.rs` | own | GPL-3.0 |
| 0011 | `0011-own-capture-headless.patch` | captures without a swap chain | - | `crates/victory-gpu/src/host.rs` | own | GPL-3.0 |
| 0012 | `0012-own-checkpoint.patch` | `checkpoint`: jump to a stage of the running mission; stage announcements in the channel's log | - (needs `VICTORY_NATIVES` and `MISSION_STAGE_SET` in the names file) | `crates/victory-gpu/src/{checkpoint.rs (new), debugcmd.rs, lib.rs}`, `crates/victory-loader/src/natives.rs` | own | GPL-3.0 |

Made against inkVI v0.2.1 (victory-fork `4c6046614` + inkVI's 38 patches). It uses inkVI's `hooks::write` (made
`pub(crate)` by 0002), `iterate::world_frame` and the presenting thread's hook point next to `shot::present`.
