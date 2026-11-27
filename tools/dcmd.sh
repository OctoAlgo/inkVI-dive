#!/bin/sh
# dcmd.sh <folder> <command line...>: (inkVI-dive) sends command lines to a running diag build with VICTORY_DEBUG=<folder>
# (as the Windows path of that folder) and prints the reply. Waits up to DWAIT seconds (60) for `done`.
# Several lines: dcmd.sh <folder> "pos" "time 7 30". Lines beginning with @w<N> run at world frame N (`done` comes after
# the last of them). DQUIET=1: only the answers (no echo of the commands, no line per native call), e.g.
#   DQUIET=1 dcmd.sh /path/to/channel pos      ->  pos -2755.401 -2914.841 12.284 heading 1.36 time 07:30:00
F=$1; shift; [ -d "$F" ] || { echo "no folder $F"; exit 1; }
rm -f "$F/done" "$F/reply.txt"
printf '%s\n' "$@" > "$F/cmd.tmp" && mv "$F/cmd.tmp" "$F/cmd"
i=0; while [ ! -f "$F/done" ]; do sleep 0.5; i=$((i+1)); [ $i -ge $(( ${DWAIT:-60} * 2 )) ] && { echo "timeout: no done in $F (game not up, or the command is waiting for its world frame)"; exit 2; }; done
if [ "${DQUIET:-0}" = 1 ]; then grep -a -v '^\[present [0-9]* world [-0-9]*\] \(> \|#[0-9]\)\|^queued #' "$F/reply.txt"; else cat "$F/reply.txt"; fi
