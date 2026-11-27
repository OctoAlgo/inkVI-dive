#!/bin/sh
# inkVI-dive: fetch inkVI at the pinned commit, apply its series to its pinned victory-fork base, add this kit's
# patches on top, build the diagnostics build (the only one the tools are in).
# Usage: sh build.sh <empty-or-existing-work-dir> [--release-too | --check]
#   --release-too  also the release build (it has none of the tools: they are diagnostics-only)
#   --check        no build: cargo check of the diagnostics build only (quick proof that the series is whole)
# Cross build from Linux needs an MSVC SDK (e.g. xwin): set XWIN=<sdk dir>, or set LIB/INCLUDE yourself.
# On Windows, run the same steps in Git Bash without XWIN.
# Offline: INKVI_KIT=<an inkVI checkout at INKVI_COMMIT> and FORK_URL=<a victory-fork clone holding inkVI's base commit>.
# While BASE's INKVI_COMMIT is the placeholder TO-BE-SET-AT-RELEASE, INKVI_KIT is required (nothing is fetched for
# inkVI) and is used as it is: not pinned, local changes allowed; its own patches are still checked.
set -eu
kit=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
val() { sed -n "s/^$1=//p" "$2" | head -1; }   # read KEY=value lines without running the file
INKVI_URL=$(val INKVI_URL "$kit/BASE"); INKVI_COMMIT=$(val INKVI_COMMIT "$kit/BASE")
INKVI_BASE_COMMIT=$(val INKVI_BASE_COMMIT "$kit/BASE")
unpinned=0; [ "$INKVI_COMMIT" = TO-BE-SET-AT-RELEASE ] && unpinned=1
[ $# -ge 1 ] || { echo "usage: sh build.sh <work-dir> [--release-too | --check]" >&2; exit 1; }
mkdir -p "$1"; work=$(CDPATH= cd -- "$1" && pwd); mode=${2:-diag}
src=$work/src

# 1. this kit's inputs: every patch listed in series, nothing else, sha256 as recorded
(cd "$kit/patches" && sha256sum -c --quiet SHA256SUMS && ls *.patch | cmp -s - series) ||
    { echo "$kit/patches: checksums or series do not match" >&2; exit 1; }

# 2. inkVI at the pinned commit
if [ $unpinned = 1 ] && [ -z "${INKVI_KIT:-}" ]; then
    echo "$kit/BASE: INKVI_COMMIT is still the placeholder TO-BE-SET-AT-RELEASE (inkVI v0.2.1 is not published yet)," >&2
    echo "so there is no inkVI commit to fetch. Build from a local inkVI v0.2.1 kit: INKVI_KIT=<its dir> sh build.sh ..." >&2
    exit 1
fi
ink=${INKVI_KIT:-$work/inkvi}
if [ -z "${INKVI_KIT:-}" ] && [ ! -d "$ink/.git" ]; then
    git init -q "$ink"
    git -C "$ink" fetch -q --depth=1 "$INKVI_URL" "$INKVI_COMMIT"
    git -C "$ink" checkout -q --detach FETCH_HEAD
fi
if [ $unpinned = 1 ]; then
    echo "UNPINNED: inkVI taken as it is from $ink (BASE has no inkVI commit yet; its patches are still checked)" >&2
else
    [ "$(git -C "$ink" rev-parse HEAD)" = "$INKVI_COMMIT" ] || {
        echo "$ink is not at the pinned inkVI commit $INKVI_COMMIT" >&2; exit 1; }
    [ -z "$(git -C "$ink" status --porcelain)" ] || { echo "$ink has local changes" >&2; exit 1; }
fi
(cd "$ink/patches" && sha256sum -c --quiet SHA256SUMS && ls *.patch | cmp -s - series) ||
    { echo "$ink/patches: checksums or series do not match" >&2; exit 1; }
BASE_URL=${FORK_URL:-$(val BASE_URL "$ink/BASE")}; BASE_COMMIT=$(val BASE_COMMIT "$ink/BASE")
[ -z "$INKVI_BASE_COMMIT" ] || [ "$BASE_COMMIT" = "$INKVI_BASE_COMMIT" ] || {
    echo "$ink pins victory-fork $BASE_COMMIT, this kit expects $INKVI_BASE_COMMIT (another inkVI version?)" >&2; exit 1; }
BRIGHTEN_FROM=$(val BRIGHTEN_FROM "$ink/BASE"); BRIGHTEN_SHA256=$(val BRIGHTEN_SHA256 "$ink/BASE")

# 3. inkVI's base, its series, then ours, in order, as commits (git am keeps authors and sources)
if [ ! -d "$src/.git" ]; then
    git init -q "$src"
    git -C "$src" fetch -q --depth=1 "$BASE_URL" "$BASE_COMMIT"
    git -C "$src" checkout -q --detach FETCH_HEAD
fi
[ "$(git -C "$src" rev-parse HEAD)" = "$BASE_COMMIT" ] || {
    echo "$src is not at inkVI's base $BASE_COMMIT (already patched? use a fresh dir)" >&2; exit 1; }
[ -z "$(git -C "$src" status --porcelain)" ] || { echo "$src has local changes" >&2; exit 1; }
am() { git -C "$src" -c user.name=inkvi -c user.email=inkvi@localhost am -q --committer-date-is-author-date "$@"; }
am $(sed "s|^|$ink/patches/|" "$ink/patches/series")
am $(sed "s|^|$kit/patches/|" "$kit/patches/series")
echo "applied: $(wc -l < "$ink/patches/series") inkVI patches + $(wc -l < "$kit/patches/series") inkVI-dive patches"

# 4. #995's compiled compute shader (VICTORY_BRIGHTEN), as inkVI's build.sh gets it (not shipped in either kit)
cso=crates/victory-gpu/src/brighten.cso
if [ ! -f "$src/$cso" ]; then
    if [ -n "${DXC:-}" ]; then
        "$DXC" -T cs_6_0 -E main -Fo "$src/$cso" "$src/crates/victory-gpu/src/brighten.hlsl"
    else
        git -C "$src" fetch -q --depth=1 "$BASE_URL" "$BRIGHTEN_FROM"
        git -C "$src" show "FETCH_HEAD:$cso" > "$src/$cso"
        echo "$BRIGHTEN_SHA256  $src/$cso" | sha256sum -c --quiet
    fi
fi

# 5. build
if [ -n "${XWIN:-}" ]; then
    vcd=$(ls -d "$XWIN"/VC/Tools/MSVC/* | head -1)
    kl="$XWIN/Windows Kits/10/Lib/10.0.26100"; ki="$XWIN/Windows Kits/10/Include/10.0.26100"
    export LIB="$vcd/lib/x64;$kl/ucrt/x64;$kl/um/x64"
    export INCLUDE="$vcd/include;$ki/ucrt;$ki/um;$ki/shared"
    export CC_x86_64_pc_windows_msvc=clang-cl AR_x86_64_pc_windows_msvc=llvm-lib
    export CARGO_TARGET_X86_64_PC_WINDOWS_MSVC_LINKER=lld-link
fi
cd "$src"
if [ "$mode" = --check ]; then
    cargo check --locked --target x86_64-pc-windows-msvc --profile diag --features diagnostics -p victory
    echo "checked: the diagnostics build of $src (no binary made)"; exit 0
fi
cargo build --locked --target x86_64-pc-windows-msvc --profile diag --features diagnostics -p victory
[ "$mode" = --release-too ] && cargo build --locked --target x86_64-pc-windows-msvc --release -p victory
echo "built: $src/target/x86_64-pc-windows-msvc/diag/victory.exe$( [ "$mode" = --release-too ] && echo ' and .../release/victory.exe')"
