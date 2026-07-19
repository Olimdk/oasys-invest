#!/usr/bin/env python3
"""Generate minimal valid RGBA PNG icons for Tauri (requires alpha channel)."""
import struct, zlib, os

OUT = os.path.join(os.path.dirname(__file__), "icons")
os.makedirs(OUT, exist_ok=True)

def png(path, size):
    w = h = size
    raw = bytearray()
    cx, cy = w / 2, h / 2
    for y in range(h):
        raw.append(0)  # filter type 0
        for x in range(w):
            d = abs(x - cx) + abs(y - cy)
            if d < size * 0.28:
                raw += bytes((120, 180, 255, 255))   # glyph (RGBA)
            else:
                raw += bytes((40, 70, 140, 255))     # bg (RGBA)
    def chunk(typ, data):
        c = struct.pack(">I", len(data)) + typ + data
        c += struct.pack(">I", zlib.crc32(typ + data) & 0xffffffff)
        return c
    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0)  # 8-bit RGBA
    idat = zlib.compress(bytes(raw), 9)
    with open(path, "wb") as f:
        f.write(sig + chunk(b"IHDR", ihdr) + chunk(b"IDAT", idat) + chunk(b"IEND", b""))

for s in (32, 128):
    png(os.path.join(OUT, f"{s}x{s}.png"), s)
png(os.path.join(OUT, "128x128@2x.png"), 256)

def write_ico(path, png_path):
    with open(png_path, "rb") as f:
        pngdata = f.read()
    with open(path, "wb") as f:
        f.write(struct.pack("<HHH", 0, 1, 1))
        f.write(struct.pack("<BBBBHHII", 32, 32, 0, 0, 1, 32, len(pngdata), 22))
        f.write(pngdata)

def write_icns(path, png_path):
    with open(png_path, "rb") as f:
        pngdata = f.read()
    with open(path, "wb") as f:
        f.write(b"icns")
        f.write(struct.pack(">I", 8 + len(pngdata)))
        f.write(b"ic07")
        f.write(struct.pack(">I", 8 + len(pngdata)))
        f.write(pngdata)

write_ico(os.path.join(OUT, "icon.ico"), os.path.join(OUT, "32x32.png"))
write_icns(os.path.join(OUT, "icon.icns"), os.path.join(OUT, "128x128.png"))
print("RGBA icons written to", OUT)
