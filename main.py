#!/usr/bin/env python3
"""news-image-20261119 -- make.fun competition entry by dev-spark319.

Renders a 1024x768 newspaper-style front page summarising world news of
Thursday 19 November 2026 as a PNG, using only the Python standard library
(zlib + struct). No network access, fully deterministic bytes.

Usage:  python3 main.py            -> writes $MAKEFUN_OUTPUT_DIR/entry.png
                                    (fallback ./out/entry.png)
"""

import os
import struct
import zlib

# ---------------------------------------------------------------- image core
W, H = 1024, 768
WHITE = (247, 245, 240)
INK = (18, 20, 24)
GREY = (110, 112, 118)
RULE = (70, 72, 76)
ACCENT = (146, 34, 40)      # deep press red (seed: dev-spark319)
ACCENT2 = (24, 68, 110)     # navy for kicker strips
PAPER2 = (233, 229, 220)    # subtle panel tint


def clamp(v):
    return 0 if v < 0 else (255 if v > 255 else v)


class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bytes(bg) * (w * h))

    def rect(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(c) * (x1 - x0)
        for yy in range(y0, y1):
            o = (yy * self.w + x0) * 3
            self.px[o:o + len(row)] = row

    def frame(self, x, y, w, h, c, t=1):
        for i in range(t):
            self.rect(x + i, y + i, w - 2 * i, 1, c)
            self.rect(x + i, y + h - 1 - i, w - 2 * i, 1, c)
            self.rect(x + i, y + i, 1, h - 2 * i, c)
            self.rect(x + w - 1 - i, y + i, 1, h - 2 * i, c)

    def hline(self, x, y, w, c, t=1):
        self.rect(x, y, w, t, c)

    def png(self):
        raw = bytearray()
        for y in range(self.h):
            raw.append(0)
            raw += self.px[y * self.w * 3:(y + 1) * self.w * 3]

        def chunk(tag, data):
            c = tag + data
            return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)

        ihdr = struct.pack(">IIBBBBB", self.w, self.h, 8, 2, 0, 0, 0)
        idat = zlib.compress(bytes(raw), 9)
        return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
                + chunk(b"IDAT", idat) + chunk(b"IEND", b""))


# ------------------------------------------------------------- 5x7 font
# Rows are 7-bit patterns, MSB = leftmost of 5 columns.
F = {
    " ": [0x00] * 7, "!": [0x04, 0x04, 0x04, 0x04, 0x04, 0x00, 0x04],
    '"': [0x0A, 0x0A, 0x00, 0x00, 0x00, 0x00, 0x00],
    "#": [0x0A, 0x0A, 0x1F, 0x0A, 0x1F, 0x0A, 0x0A],
    "$": [0x04, 0x0F, 0x14, 0x0E, 0x05, 0x1E, 0x04],
    "%": [0x19, 0x1A, 0x02, 0x04, 0x08, 0x0B, 0x13],
    "&": [0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D],
    "'": [0x04, 0x04, 0x00, 0x00, 0x00, 0x00, 0x00],
    "(": [0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02],
    ")": [0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08],
    "*": [0x00, 0x04, 0x15, 0x0E, 0x15, 0x04, 0x00],
    "+": [0x00, 0x04, 0x04, 0x1F, 0x04, 0x04, 0x00],
    ",": [0x00, 0x00, 0x00, 0x00, 0x00, 0x04, 0x08],
    "-": [0x00, 0x00, 0x00, 0x1F, 0x00, 0x00, 0x00],
    ".": [0x00, 0x00, 0x00, 0x00, 0x00, 0x0C, 0x0C],
    "/": [0x01, 0x02, 0x02, 0x04, 0x08, 0x08, 0x10],
    "0": [0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E],
    "1": [0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E],
    "2": [0x0E, 0x11, 0x01, 0x02, 0x04, 0x08, 0x1F],
    "3": [0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E],
    "4": [0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02],
    "5": [0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E],
    "6": [0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E],
    "7": [0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08],
    "8": [0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E],
    "9": [0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C],
    ":": [0x00, 0x0C, 0x0C, 0x00, 0x0C, 0x0C, 0x00],
    ";": [0x00, 0x0C, 0x0C, 0x00, 0x04, 0x08, 0x00],
    "<": [0x02, 0x04, 0x08, 0x10, 0x08, 0x04, 0x02],
    "=": [0x00, 0x00, 0x1F, 0x00, 0x1F, 0x00, 0x00],
    ">": [0x08, 0x04, 0x02, 0x01, 0x02, 0x04, 0x08],
    "?": [0x0E, 0x11, 0x01, 0x02, 0x04, 0x00, 0x04],
    "@": [0x0E, 0x11, 0x01, 0x0D, 0x15, 0x15, 0x0E],
    "A": [0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11],
    "B": [0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E],
    "C": [0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E],
    "D": [0x1C, 0x12, 0x11, 0x11, 0x11, 0x12, 0x1C],
    "E": [0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F],
    "F": [0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10],
    "G": [0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F],
    "H": [0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11],
    "I": [0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E],
    "J": [0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C],
    "K": [0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11],
    "L": [0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F],
    "M": [0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11],
    "N": [0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11],
    "O": [0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E],
    "P": [0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10],
    "Q": [0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D],
    "R": [0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11],
    "S": [0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E],
    "T": [0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04],
    "U": [0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E],
    "V": [0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04],
    "W": [0x11, 0x11, 0x11, 0x15, 0x15, 0x1B, 0x11],
    "X": [0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11],
    "Y": [0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04],
    "Z": [0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F],
    "[": [0x0E, 0x08, 0x08, 0x08, 0x08, 0x08, 0x0E],
    "\\": [0x10, 0x08, 0x08, 0x04, 0x02, 0x02, 0x01],
    "]": [0x0E, 0x02, 0x02, 0x02, 0x02, 0x02, 0x0E],
    "^": [0x04, 0x0A, 0x00, 0x00, 0x00, 0x00, 0x00],
    "_": [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x1F],
    "`": [0x08, 0x04, 0x00, 0x00, 0x00, 0x00, 0x00],
    "a": [0x00, 0x00, 0x0E, 0x01, 0x0D, 0x13, 0x0D],
    "b": [0x10, 0x10, 0x1E, 0x11, 0x11, 0x11, 0x1E],
    "c": [0x00, 0x00, 0x0E, 0x10, 0x10, 0x11, 0x0E],
    "d": [0x01, 0x01, 0x0D, 0x13, 0x13, 0x13, 0x0D],
    "e": [0x00, 0x00, 0x0E, 0x11, 0x1F, 0x10, 0x0E],
    "f": [0x06, 0x08, 0x08, 0x1C, 0x08, 0x08, 0x08],
    "g": [0x00, 0x0D, 0x13, 0x13, 0x0D, 0x01, 0x0E],
    "h": [0x10, 0x10, 0x1E, 0x11, 0x11, 0x11, 0x11],
    "i": [0x04, 0x00, 0x0C, 0x04, 0x04, 0x04, 0x0E],
    "j": [0x02, 0x00, 0x06, 0x02, 0x02, 0x12, 0x0C],
    "k": [0x10, 0x10, 0x12, 0x14, 0x18, 0x14, 0x12],
    "l": [0x0C, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E],
    "m": [0x00, 0x00, 0x1A, 0x15, 0x15, 0x15, 0x15],
    "n": [0x00, 0x00, 0x1E, 0x11, 0x11, 0x11, 0x11],
    "o": [0x00, 0x00, 0x0E, 0x11, 0x11, 0x11, 0x0E],
    "p": [0x00, 0x00, 0x1E, 0x11, 0x11, 0x1E, 0x10],
    "q": [0x00, 0x00, 0x0D, 0x13, 0x13, 0x0D, 0x01],
    "r": [0x00, 0x00, 0x16, 0x19, 0x10, 0x10, 0x10],
    "s": [0x00, 0x00, 0x0F, 0x10, 0x0E, 0x01, 0x1E],
    "t": [0x08, 0x08, 0x1C, 0x08, 0x08, 0x0A, 0x04],
    "u": [0x00, 0x00, 0x11, 0x11, 0x11, 0x13, 0x0D],
    "v": [0x00, 0x00, 0x11, 0x11, 0x11, 0x0A, 0x04],
    "w": [0x00, 0x00, 0x11, 0x15, 0x15, 0x15, 0x0A],
    "x": [0x00, 0x00, 0x11, 0x0A, 0x04, 0x0A, 0x11],
    "y": [0x00, 0x00, 0x11, 0x11, 0x0F, 0x01, 0x0E],
    "z": [0x00, 0x00, 0x1F, 0x02, 0x04, 0x08, 0x1F],
    "{": [0x06, 0x04, 0x04, 0x08, 0x04, 0x04, 0x06],
    "|": [0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04],
    "}": [0x0C, 0x04, 0x04, 0x02, 0x04, 0x04, 0x0C],
    "~": [0x00, 0x00, 0x08, 0x15, 0x02, 0x00, 0x00],
}
GW, GH, GAP = 5, 7, 1  # glyph box, tracking


def text_w(s, sc=1):
    if not s:
        return 0
    return len(s) * (GW + GAP) * sc - GAP


def draw_text(cv, s, x, y, c=INK, sc=1):
    cx = x
    for ch in s:
        g = F.get(ch, F["?"])
        for r in range(GH):
            bi= g[r]
            for col in range(GW):
                if bi& (0x10 >> col):
                    cv.rect(cx + col * sc, y + r * sc, sc, sc, c)
        cx += (GW + GAP) * sc
    return cx


def fit(s, max_px, sc):
    """Trim string so it fimax_px at scale sc."""
    if text_w(s, sc) <= max_px:
        return s
    out = ""
    for ch in s:
        if text_w(out + ch + "...", sc) > max_px:
            return out.rstrip() + "..."
        out += ch
    return out


def wrap(s, max_px, sc):
    words, lines, cur = s.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if text_w(t, sc) <= max_px:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def lead_body(cv, s, x, y, w, nlines, sc=2, c=INK, lh=12):
    lines = wrap(s, w, sc)[:nlines]
    for i, ln in enumerate(lines):
        draw_text(cv, ln, x, y + i * lh, c, sc)
    return y + len(lines) * lh


# ------------------------------------------------------------- content
EDITION = "THURSDAY 19 NOVEMBER 2026"
MAST = "WORLD NEWS"
VOL = "No. 87658"

# (kicker, headline, body, col_span, box_bg)
STORIES = [
    ("GAMING", "GTA VI ARRIVES: MILLIONS QUEUE FOR DAY-ONE CONSOLES",
     "Rockstar's Grand Theft Auto VI lands today as retailers sell out of "
     "next-gen bundles; fans queue overnight for the November 19 release.",
     2, None),
    ("MARKETS", "STOCKS MIXED AS RATE-CUT BETS RESHUFFLE GLOBAL PORTFOLIOS",
     "Wall Street wavers and the dollar firms while bond yields ease; oil and "
     "gold edge higher as traders brace for central-bank signals.",
     1, None),
    ("CLIMATE", "COP31 TALKS ENTER FINAL DAY WITH FOSSIL-FUEL DEAL UNRESOLVED",
     "Delegates at the climate summit haggle over a transition roadmap and "
     "adaptation finance as ministers race to land a closing text.",
     1, PAPER2),
    ("WORLD", "WORLD LEADERS GATHER FOR G20 SUMMIT UNDER TIGHT SECURITY",
     "Diplomafine-tune communique language while protesand port "
     "closures test hosts; trade and AI safety top the agenda.",
     1, None),
    ("TECH & AI", "AI CHIPS, AGENTS AND RULES DOMINATE THE TECH AGENDA",
     "Data-centre spending hit new records as regulators sharpen AI rules; "
     "agent moves from demo to deployment across the enterprise.",
     1, None),
    ("SPORT", "WORLD CUP COUNTDOWN: PLAYOFFS SET FINAL SLOTS FOR 2026",
     "Hosfinalise preparations as the last qualifying spoare decided; "
     "squad announcemenand injury races dominate the buildup.",
     1, PAPER2),
]


def page():
    cv = Canvas(W, H, WHITE)
    M = 36  # margin

    # top strip
    cv.rect(0, 0, W, 10, ACCENT2)
    draw_text(cv, "INTERNATIONAL EDITION  *  DAILY", M, 16, GREY, 1)
    right = "PRICE: FREE  *  MAKE.FUN"
    draw_text(cv, right, W - M - text_w(right, 1), 16, GREY, 1)
    cv.hline(M, 30, W - 2 * M, RULE, 2)

    # masthead
    ms = 9
    my = 44
    draw_text(cv, MAST, M, my, INK, ms)
    # edition block right
    ex = W - M - 300
    cv.rect(ex - 16, 44, 300 + 12, 78, PAPER2)
    draw_text(cv, EDITION, ex, 54, INK, 2)
    draw_text(cv, VOL + "  *  DEV-SPARK319 DESK", ex, 78, ACCENT, 2)
    draw_text(cv, "THE WORLD IN SIX STORIES", ex, 102, GREY, 1)
    cv.hline(M, 136, W - 2 * M, INK, 3)
    cv.hline(M, 141, W - 2 * M, RULE, 1)

    # dateline banner
    banner = "LATE FINAL  *  ALL THE NEWS FIT TO PIXEL  *  19.11.2026"
    bw = W - 2 * M
    cv.rect(M, 152, bw, 30, INK)
    draw_text(cv, banner, M + (bw - text_w(banner, 2)) // 2, 162, WHITE, 2)

    # lead story (2 cols wide)
    y0 = 196
    gutter = 16
    colw = (bw - gutter) // 2
    k, h, body, span, bg = STORIES[0]
    leadw = colw * 2 + gutter
    box_h = 218
    if bg:
        cv.rect(M, y0, leadw, box_h, bg)
    draw_text(cv, k, M, y0 + 12, ACCENT, 2)
    cv.hline(M, y0 + 34, leadw, ACCENT, 1)
    draw_text(cv, fit(h, leadw, 3), M, y0 + 46, INK, 3)
    draw_text(cv, fit("GRAND THEFT AUTO VI HITS SHELVES; FANS CAMP OUT", leadw, 2),
              M, y0 + 78, INK, 2)
    cv.hline(M, y0 + 104, leadw, RULE, 1)
    lead_body(cv, body, M, y0 + 116, leadw, 5, sc=2, lh=14)

    # pixel art: GTA-style 'VI' mark on the right of lead box
    mx = M + leadw - 96
    cv.rect(mx, y0 + 24, 84, 96, INK)
    draw_text(cv, "VI", mx + 14, y0 + 40, WHITE, 8)
    draw_text(cv, "2026", mx + 12, y0 + 104, ACCENT, 1)

    # story grid: 2 columns x 2 rows of single-column story boxes
    gy = y0 + box_h + 16
    story = STORIES[1:]
    bh = 160
    for row in range(2):
        gy_row = gy + row * (bh + 16)
        bx = M
        for k2, h2, b2, span2, bg2 in story[row * 2:row * 2 + 2]:
            if bg2:
                cv.rect(bx, gy_row, colw, bh, bg2)
            cv.frame(bx, gy_row, colw, bh, RULE, 1)
            draw_text(cv, k2, bx + 10, gy_row + 10, ACCENT, 2)
            cv.hline(bx + 10, gy_row + 30, colw - 20, ACCENT, 1)
            lines = wrap(h2, colw - 20, 2)[:3]
            yy = gy_row + 38
            for ln in lines:
                draw_text(cv, ln, bx + 10, yy, INK, 2)
                yy += 14
            cv.hline(bx + 10, gy_row + 84, colw - 20, RULE, 1)
            lead_body(cv, b2, bx + 10, gy_row + 92, colw - 20, 5, sc=1, lh=9)
            bx += colw + gutter

    # bottom index strip (fills the space below the story grid)
    iy = gy + 2 * (bh + 16) + 4
    cv.hline(M, iy, W - 2 * M, RULE, 2)
    idx = "INSIDE: MARKETS  *  CLIMATE  *  WORLD  *  TECH & AI  *  SPORT  *  VIEWPOINT"
    draw_text(cv, idx, M, iy + 12, ACCENT, 1)
    quote = "\"THE WORLD IN SIX STORIES\"  --  THE DEV-SPARK319 DESK"
    draw_text(cv, quote, M, iy + 30, GREY, 1)

    # footer
    fy = H - 40
    cv.hline(M, fy, W - 2 * M, RULE, 2)
    draw_text(cv, "WORLD NEWS  *  " + EDITION + "  *  PAGE 1", M, fy + 14, GREY, 1)
    sig = "RENDERED WITH ZLIB  *  STDlib ONLY  *  SEED dev-spark319"
    draw_text(cv, sig, W - M - text_w(sig, 1), fy + 14, GREY, 1)

    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or os.path.join("out")
    os.makedirs(out_dir, exist_ok=True)
    data = page().png()
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    print("wrote", path, len(data), "bytes")


if __name__ == "__main__":
    main()
