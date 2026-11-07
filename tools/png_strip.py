"""Join PNG screenshots side by side (pure Python, no PIL): python3 tools/png_strip.py out.png a.png b.png ..."""
import struct
import sys
import zlib


def read_png_rgb(path):
    """Decode to rows of RGB bytes (handles RGBA by keeping the unfiltered RGBA row for the next filter step)."""
    data = open(path, "rb").read()
    pos, idat = 8, b""
    while pos < len(data):
        length, kind = struct.unpack(">I4s", data[pos:pos + 8])
        chunk = data[pos + 8:pos + 8 + length]
        if kind == b"IHDR":
            width, height, depth, color = struct.unpack(">IIBB", chunk[:10])
            bpp = 4 if color == 6 else 3
        elif kind == b"IDAT":
            idat += chunk
        pos += 12 + length
    raw = zlib.decompress(idat)
    stride = width * bpp
    out, prev, i = [], bytearray(stride), 0
    for _ in range(height):
        f, line = raw[i], bytearray(raw[i + 1:i + 1 + stride])
        i += 1 + stride
        for x in range(stride):
            a = line[x - bpp] if x >= bpp else 0
            b = prev[x]
            c = prev[x - bpp] if x >= bpp else 0
            if f == 1:
                line[x] = (line[x] + a) & 255
            elif f == 2:
                line[x] = (line[x] + b) & 255
            elif f == 3:
                line[x] = (line[x] + (a + b) // 2) & 255
            elif f == 4:
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                line[x] = (line[x] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 255
        prev = line
        out.append(bytes(line) if bpp == 3 else bytes(v for k, v in enumerate(line) if k % 4 != 3))
    return width, height, out


def write_png(path, width, height, rows):
    raw = b"".join(b"\x00" + r for r in rows)

    def chunk(kind, payload):
        return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")
    open(path, "wb").write(png)


def main(out, *paths, gap=6):
    images = [read_png_rgb(p) for p in paths]
    height = max(h for _, h, _ in images)
    rows = []
    for y in range(height):
        parts = []
        for w, h, img_rows in images:
            parts.append(img_rows[y] if y < h else b"\xff" * (w * 3))
            parts.append(b"\xff" * (gap * 3))
        rows.append(b"".join(parts[:-1]))
    width = sum(w for w, _, _ in images) + gap * (len(images) - 1)
    write_png(out, width, height, rows)
    print(out, width, "x", height)


if __name__ == "__main__":
    main(sys.argv[1], *sys.argv[2:])
