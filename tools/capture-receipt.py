#!/usr/bin/env python3
"""Request a capture and print a JSON receipt after its Present files arrive."""
import argparse
import hashlib
import json
import os
import re
import struct
import subprocess
import sys
import time
from pathlib import Path

DCMD = Path(__file__).with_name("dcmd.sh")
RAW = re.compile(r"frame-(\d+)-(\d+)x(\d+)-(rgba|bgra)-p(\d+)\.raw")
PNG_END = bytes.fromhex("0000000049454e44ae426082")


def stamp(stat):
    return stat.st_dev, stat.st_ino, stat.st_size, stat.st_mtime_ns, stat.st_ctime_ns


def read_frame(path, present, before):
    """Ignore old files and captures that are still being written."""
    with path.open("rb") as data:
        stat = os.fstat(data.fileno())
        if stamp(stat) == before.get(path):
            return None
        if path.suffix == ".png":
            if path.name != f"frame-{present}.png" or stat.st_size < 45:
                return None
            head = data.read(24)
            if head[:16] != bytes.fromhex("89504e470d0a1a0a0000000d49484452"):
                return None
            width, height = struct.unpack(">II", head[16:])
            data.seek(-12, os.SEEK_END)
            if data.read() != PNG_END:
                return None
        else:
            match = RAW.fullmatch(path.name)
            if not match or int(match[1]) != present:
                return None
            width, height, pitch = int(match[2]), int(match[3]), int(match[5])
            # D3D12 may omit padding after the last row of the footprint.
            if pitch < width * 4 or stat.st_size not in (pitch * height, pitch * (height - 1) + width * 4):
                return None
        if not width or not height:
            return None
        data.seek(0)
        digest = hashlib.sha256()
        while block := data.read(1024 * 1024):
            digest.update(block)
        if stamp(stat) != stamp(path.stat()):
            return None
        return dict(present=present, file=path.name, width=width, height=height,
                    bytes=stat.st_size, sha256=digest.hexdigest())


def capture(channel, folder, count, timeout):
    if not channel.is_dir() or not folder.is_dir():
        raise ValueError("channel and capture folder must both exist")
    before = {p: stamp(p.stat()) for p in folder.glob("frame-*") if p.is_file()}
    start = time.monotonic()
    result = subprocess.run(
        ["sh", str(DCMD), str(channel), f"cap {count}"], stdout=subprocess.PIPE,
        text=True, timeout=timeout, env={**os.environ, "DWAIT": str(timeout), "DQUIET": "1"})
    reply = result.stdout.strip()
    match = re.search(r"^cap: presents (\d+)\.\.(\d+) are saved$", reply, re.MULTILINE)
    if result.returncode or not match:
        raise ValueError(f"capture command failed: {reply}")
    first, last = map(int, match.groups())
    if last - first + 1 != count:
        raise ValueError(f"requested {count} Presents, received {first}..{last}")
    frames = []
    for present in range(first, last + 1):
        while True:
            candidates = [folder / f"frame-{present}.png", *folder.glob(f"frame-{present}-*.raw")]
            ready = []
            for path in candidates:
                try:
                    frame = read_frame(path, present, before)
                except FileNotFoundError:
                    continue
                if frame:
                    ready.append(frame)
            if len(ready) == 1:
                frames.append(ready[0])
                break
            if len(ready) > 1:
                raise ValueError(f"multiple fresh capture files for Present {present}")
            if time.monotonic() - start >= timeout:
                raise TimeoutError(f"waiting for Present {present} of {first}..{last}")
            time.sleep(0.1)
    return dict(first=first, last=last, elapsed_seconds=round(time.monotonic() - start, 3), frames=frames)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("channel", type=Path)
    parser.add_argument("capture_folder", type=Path)
    parser.add_argument("--count", type=int, default=1)
    parser.add_argument("--timeout", type=int, default=60, help="seconds for the command and its captures")
    args = parser.parse_args()
    if min(args.count, args.timeout) <= 0:
        parser.error("count and timeout must be positive")
    try:
        print(json.dumps(capture(args.channel, args.capture_folder, args.count, args.timeout), indent=2))
    except (OSError, ValueError, subprocess.TimeoutExpired) as error:
        sys.exit(str(error))


if __name__ == "__main__":
    main()
