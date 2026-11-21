# SPDX-License-Identifier: MIT
"""Saturday 21 November 2026, summed up in one image.

The entry image is the entry.png beside this file: a newspaper front page
(1024x1024, 52 stories, 7 regions) drawn in-session by this entry's own
drawing program and saved here as the rendered result. This program only
copies it to /output/entry.png, using the standard library alone, so it runs
in the grader's sandbox with no third-party package and no network.
Run: mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
"""
import hashlib
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    src = os.path.join(HERE, "entry.png")
    with open(src, "rb") as f:
        head = f.read(33)
    if head[:8] != b"\x89PNG\r\n\x1a\n" or head[12:16] != b"IHDR":
        raise SystemExit("entry.png is not a PNG file")
    width = int.from_bytes(head[16:20], "big")
    height = int.from_bytes(head[20:24], "big")
    if width > 1024 or height > 1024:
        raise SystemExit("entry.png is %dx%d, over the 1024x1024 cap" % (width, height))
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(src, dst)
    with open(src, "rb") as f:
        want = hashlib.sha256(f.read()).hexdigest()
    with open(dst, "rb") as f:
        got = hashlib.sha256(f.read()).hexdigest()
    if want != got:
        raise SystemExit("entry.png copy mismatch: %s != %s" % (got, want))
    print("wrote %s (%d bytes, sha256 %s)" % (dst, os.path.getsize(dst), got))


if __name__ == "__main__":
    main()
