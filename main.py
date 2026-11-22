#!/usr/bin/env python3
"""Cabe Merah - The Picture That Tastes of One Ingredient.

Still-life illustration of red chillies: a bowl of glossy red chillies
with green stems, a few chillies scattered on a wooden table, water
droplets and warm light on a dark background. Pure Python 3 stdlib only
(no Pillow / numpy): the PNG encoder below is hand-written with zlib
and struct, so it runs in a bare python:3.13-slim sandbox.

Output: /output/entry.png (or $MAKEFUN_OUTPUT), 1024x1024, <= 1 MiB.
"""

import math
import os
import struct
import zlib

W = H = 1024


# ---------------------------------------------------------------- canvas
class Canvas:
    """Simple RGB canvas with alpha-blended primitives."""

    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)

    def set(self, x, y, r, g, b):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i] = r
            self.px[i + 1] = g
            self.px[i + 2] = b

    def blend(self, x, y, r, g, b, a):
        """Blend colour (r,g,b) with opacity a (0..1) over the pixel."""
        if a <= 0:
            return
        if a >= 1:
            self.set(x, y, r, g, b)
            return
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i] = int(self.px[i] + (r - self.px[i]) * a)
            self.px[i + 1] = int(self.px[i + 1] + (g - self.px[i + 1]) * a)
            self.px[i + 2] = int(self.px[i + 2] + (b - self.px[i + 2]) * a)

    def hline(self, x0, x1, y, r, g, b, a=1.0):
        if y < 0 or y >= self.h:
            return
        x0 = max(0, int(x0))
        x1 = min(self.w - 1, int(x1))
        for x in range(x0, x1 + 1):
            self.blend(x, y, r, g, b, a)

    def disc(self, cx, cy, rad, r, g, b, a=1.0):
        """Filled circle."""
        rad = int(rad)
        if rad <= 0:
            return
        for dy in range(-rad, rad + 1):
            dx = int(math.sqrt(rad * rad - dy * dy))
            self.hline(cx - dx, cx + dx, cy + dy, r, g, b, a)

    def ellipse(self, cx, cy, rx, ry, r, g, b, a=1.0):
        """Filled ellipse."""
        rx = int(rx)
        ry = int(ry)
        if rx <= 0 or ry <= 0:
            return
        for dy in range(-ry, ry + 1):
            t = dy / ry
            dx = int(rx * math.sqrt(max(0.0, 1.0 - t * t)))
            self.hline(cx - dx, cx + dx, cy + dy, r, g, b, a)

    def poly(self, pts, r, g, b, a=1.0):
        """Filled polygon via scanlines."""
        if len(pts) < 3:
            return
        ys = [p[1] for p in pts]
        y0, y1 = int(max(0, min(ys))), int(min(self.h - 1, max(ys)))
        n = len(pts)
        for y in range(y0, y1 + 1):
            xs = []
            for i in range(n):
                x0, y0p = pts[i]
                x1, y1p = pts[(i + 1) % n]
                if (y0p <= y < y1p) or (y1p <= y < y0p):
                    t = (y - y0p) / (y1p - y0p)
                    xs.append(x0 + t * (x1 - x0))
            xs.sort()
            for j in range(0, len(xs) - 1, 2):
                self.hline(xs[j], xs[j + 1], y, r, g, b, a)

    def bezier(self, p0, p1, p2, t):
        """Quadratic bezier point."""
        u = 1.0 - t
        return (
            u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0],
            u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1],
        )


def lerp(a, b, t):
    return a + (b - a) * t


def lerp3(c0, c1, t):
    return (
        int(lerp(c0[0], c1[0], t)),
        int(lerp(c0[1], c1[1], t)),
        int(lerp(c0[2], c1[2], t)),
    )


def clamp01(t):
    return 0.0 if t < 0 else 1.0 if t > 1 else t


# ---------------------------------------------------------------- PNG out
def write_png(path, canvas):
    """Write RGB canvas as PNG (filter Sub per row, zlib level 9)."""
    w, h = canvas.w, canvas.h
    raw = bytearray()
    px = canvas.px
    for y in range(h):
        raw.append(1)  # filter type 1 = Sub (bpp = 3 for RGB)
        row = y * w * 3
        for x in range(w * 3):
            pred = px[row + x - 3] if x >= 3 else 0
            raw.append((px[row + x] - pred) & 0xFF)
    comp = zlib.compress(bytes(raw), 9)

    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", comp)
    png += chunk(b"IEND", b"")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


# ---------------------------------------------------------------- palette
RED_DEEP = (122, 10, 24)
RED_BASE = (198, 16, 46)
RED_BRIGHT = (232, 40, 63)
RED_HOT = (255, 107, 94)
GREEN_DARK = (46, 90, 32)
GREEN = (74, 138, 48)
GREEN_LIGHT = (122, 178, 74)
WOOD_DARK = (74, 44, 26)
WOOD = (122, 74, 40)
WOOD_LIGHT = (168, 108, 62)
CERAMIC = (58, 34, 30)
CERAMIC_LIGHT = (104, 58, 46)
CERAMIC_RIM = (140, 82, 58)


def background(cv):
    """Dark warm background with a soft radial glow behind the bowl."""
    for y in range(H):
        t = y / (H - 1)
        c = lerp3((22, 13, 11), (46, 26, 18), t)
        cv.hline(0, W - 1, y, *c)
    # warm glow, centre (512, 470)
    gx, gy, gr = 512, 470, 560
    for y in range(gy - gr, gy + gr):
        if y < 0 or y >= H:
            continue
        for x in range(gx - gr, gx + gr):
            d = math.hypot(x - gx, y - gy) / gr
            if d < 1.0:
                a = (1.0 - d) ** 2 * 0.34
                cv.blend(x, y, 214, 110, 52, a)


def table(cv):
    """Wooden table: bottom ~40% of the frame, planks + grain."""
    top = 620
    for y in range(top, H):
        t = (y - top) / (H - top)
        c = lerp3((96, 58, 34), (64, 36, 22), t)
        cv.hline(0, W - 1, y, *c)
    # plank seams
    for y in (726, 838, 946):
        cv.hline(0, W - 1, y, 40, 22, 14, 0.85)
        cv.hline(0, W - 1, y + 1, 150, 96, 56, 0.35)
    # grain: long wavy dark strokes
    for gy, amp, ph in ((680, 7, 0.0), (770, 9, 1.3), (880, 8, 2.6), (985, 6, 4.1)):
        for x in range(0, W, 4):
            y = gy + int(amp * math.sin(x / 170.0 + ph))
            cv.disc(x, y, 2, 52, 30, 18, 0.30)
    # soft shadow under the bowl
    for dy in range(0, 60):
        a = 0.30 * (1.0 - dy / 60.0)
        cv.ellipse(512, 905 + dy // 3, 330 - dy, 26, 20, 10, 6, a)


def bowl(cv):
    """Terracotta bowl: body, rim, dark interior."""
    # body
    cv.ellipse(512, 700, 308, 232, *CERAMIC)
    # body shading: lighter left, darker right
    cv.ellipse(430, 720, 190, 170, 84, 48, 38, 0.35)
    cv.ellipse(640, 760, 150, 140, 40, 24, 20, 0.35)
    # foot ring
    cv.ellipse(512, 918, 150, 26, 40, 24, 20, 0.9)
    cv.ellipse(512, 912, 150, 22, 74, 44, 34, 0.9)
    # rim
    cv.ellipse(512, 640, 308, 88, *CERAMIC_RIM)
    cv.ellipse(512, 640, 292, 78, *CERAMIC_LIGHT)
    # interior (dark, chillies sit in it)
    cv.ellipse(512, 640, 272, 64, 26, 10, 10)


def chilli(cv, p0, ctrl, p1, rmax, flip=False):
    """One curved red chilli along a quadratic bezier spine.

    Thick near the stem, tapering to a curved tip; glossy highlight
    stripe on the upper-left side; green stem at p0.
    """
    n = 70
    pts = [cv.bezier(p0, ctrl, p1, i / (n - 1)) for i in range(n)]
    # body: stacked discs, radius bulges then tapers to the tip
    for i, (x, y) in enumerate(pts):
        t = i / (n - 1)
        r = rmax * (1.0 - 0.88 * t ** 1.7) * (1.0 + 0.22 * math.sin(math.pi * t))
        # colour: deep at the edges of the pile, bright where light hits
        shade = clamp01(0.35 + 0.65 * math.sin(math.pi * clamp01(t * 1.15)))
        c = lerp3(RED_DEEP, RED_BRIGHT, shade)
        cv.disc(int(x), int(y), max(2, int(r)), *c)
    # glossy highlight: smaller discs offset up-left
    for i in range(6, n - 12):
        t = i / (n - 1)
        x, y = pts[i]
        r = rmax * (1.0 - 0.88 * t ** 1.7) * (1.0 + 0.22 * math.sin(math.pi * t))
        cv.disc(int(x - r * 0.38), int(y - r * 0.42), max(2, int(r * 0.34)),
                *RED_HOT, 0.55)
    # green stem at p0, pointing away from the body
    dx = p0[0] - ctrl[0]
    dy = p0[1] - ctrl[1]
    ln = math.hypot(dx, dy) or 1.0
    ux, uy = dx / ln, dy / ln
    sx, sy = p0
    for k in range(6):
        f = k / 5.0
        r = rmax * 0.34 * (1.0 - f * 0.75)
        c = lerp3(GREEN, GREEN_LIGHT, f)
        cv.disc(int(sx + ux * k * rmax * 0.28 + 6 * math.sin(f * 2.0)),
                int(sy + uy * k * rmax * 0.28), max(2, int(r)), *c)
    # calyx cap where stem meets the fruit
    cv.disc(int(p0[0]), int(p0[1]), int(rmax * 0.30), *GREEN_DARK)


def droplet(cv, x, y, r):
    """A water droplet: pale blue-white disc + bright speck."""
    cv.disc(x, y, r, 214, 232, 238, 0.55)
    cv.disc(x - r // 3, y - r // 3, max(1, r // 3), 255, 255, 255, 0.9)


def vignette(cv):
    """Darken the corners so the bowl stays the hero."""
    for y in range(0, H, 2):
        for x in range(0, W, 2):
            d = math.hypot(x - 512, y - 500) / 760.0
            if d > 0.62:
                a = min(0.5, (d - 0.62) * 1.1)
                cv.blend(x, y, 8, 5, 4, a)
                cv.blend(x + 1, y, 8, 5, 4, a)
                cv.blend(x, y + 1, 8, 5, 4, a)
                cv.blend(x + 1, y + 1, 8, 5, 4, a)


def draw():
    cv = Canvas(W, H)
    background(cv)
    table(cv)

    # --- back chillies: piled high behind the rim -------------------
    chilli(cv, (430, 645), (395, 500), (330, 445), 42)
    chilli(cv, (560, 648), (605, 500), (680, 440), 42)
    chilli(cv, (512, 642), (525, 490), (500, 420), 44)
    chilli(cv, (470, 645), (430, 530), (365, 480), 34)
    chilli(cv, (555, 645), (600, 530), (660, 478), 34)

    bowl(cv)

    # --- front chillies: spilling over the rim ----------------------
    chilli(cv, (468, 662), (380, 600), (296, 556), 30)
    chilli(cv, (560, 662), (652, 602), (734, 566), 30)
    chilli(cv, (512, 668), (478, 580), (428, 516), 28)
    chilli(cv, (542, 668), (584, 592), (626, 528), 28)

    # --- scattered chillies on the table ----------------------------
    chilli(cv, (168, 905), (262, 858), (356, 902), 30)
    chilli(cv, (830, 872), (762, 936), (676, 948), 28)
    chilli(cv, (752, 782), (800, 726), (862, 758), 24)

    # --- water droplets on fruit and table --------------------------
    for x, y, r in ((470, 560, 7), (560, 545, 6), (420, 620, 6),
                    (640, 610, 7), (300, 585, 5), (700, 590, 5),
                    (250, 885, 6), (790, 905, 6)):
        droplet(cv, x, y, r)
    # a few droplets on the wood near the bowl
    for x, y, r in ((360, 950, 5), (660, 960, 5), (600, 985, 4)):
        droplet(cv, x, y, r)

    vignette(cv)
    return cv


def main():
    out = os.environ.get("MAKEFUN_OUTPUT", "/output/entry.png")
    cv = draw()
    size = write_png(out, cv)
    print(f"wrote {out} ({cv.w}x{cv.h}, {size} bytes)")


if __name__ == "__main__":
    main()
