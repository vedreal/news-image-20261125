#!/usr/bin/env python3
"""news-image-20261125: one image summing up the world news of
Wednesday 25 November 2026.

A pure Python 3.13 standard-library program: it draws a newspaper
front page (masthead with the date, one lead story and eight more
stories across regions and fields) with a small raster engine and a
5x7 bitmap font, then writes it to /output/entry.png
(or $MAKEFUN_OUTPUT_DIR/entry.png outside the grader).

No network, no randomness, no clock: the two grader runs write
identical bytes.

Stories depicted (all events that happened or were first reported
on 25 November 2026, as carried by Reuters, CNN, AFP and other
wires that day):
  lead  - CIA and the U.S. Director of National Intelligence hit
          by a cyberattack (CNN, 25 Nov)
  row 2 - Zelenskyy confirms Ukraine struck Russian ships off
          Libya and in the Gulf of Finland; Putin says retaliation
          is inevitable as Ukraine keeps hitting oil refineries
  row 3 - WHO evacuates staff from an Ebola hospital in DR Congo
          amid fighting; Huawei found guilty by a U.S. jury on
          10 of 12 counts; Turkish military helicopter crash
          kills five on a training flight
  row 4 - about 175 migrants missing after a boat from Senegal
          vanishes; Sarkozy and Bruni ordered to trial over the
          Libya corruption case; Trump pardons turkeys Freedom
          and Feathers on Thanksgiving eve
"""

import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- font
# 5x7 bitmap glyphs, written out row by row ("#" = ink).
_GLYPHS = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00010", "00100", "01000", "11111"),
    "3": ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00010", "00100", "00000", "00100"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
}
FONT = {ch: tuple(int(row, 2) for row in rows) for ch, rows in _GLYPHS.items()}
_BLANK = (0, 0, 0, 0, 0, 0, 0)


def text_width(text, scale):
    """Pixel width of text drawn at the given scale."""
    return len(text) * 6 * scale - scale


def wrap_text(text, max_width, scale):
    """Greedy word wrap; returns a list of lines fitting max_width."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bytes(bg) * (w * h))

    def _set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = color

    def hline(self, x1, x2, y, color):
        if y < 0 or y >= self.h:
            return
        x1, x2 = max(0, x1), min(self.w - 1, x2)
        for x in range(x1, x2 + 1):
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = color

    def vline(self, x, y1, y2, color):
        if x < 0 or x >= self.w:
            return
        for y in range(max(0, y1), min(self.h - 1, y2) + 1):
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = color

    def fill_rect(self, x, y, w, h, color):
        for yy in range(max(0, y), min(self.h, y + h)):
            self.hline(x, x + w - 1, yy, color)

    def border(self, x, y, w, h, color, t=3):
        self.fill_rect(x, y, w, t, color)
        self.fill_rect(x, y + h - t, w, t, color)
        self.fill_rect(x, y, t, h, color)
        self.fill_rect(x + w - t, y, t, h, color)

    def fill_ellipse(self, cx, cy, rx, ry, color):
        if rx <= 0 or ry <= 0:
            self._set(cx, cy, color)
            return
        for y in range(cy - ry, cy + ry + 1):
            dy = (y - cy) / ry
            if abs(dy) > 1:
                continue
            dx = int(rx * (1 - dy * dy) ** 0.5)
            self.hline(cx - dx, cx + dx, y, color)

    def fill_circle(self, cx, cy, r, color):
        self.fill_ellipse(cx, cy, r, r, color)

    def circle_outline(self, cx, cy, r, color, t=3):
        for k in range(t):
            rr = r - k
            if rr <= 0:
                break
            for y in range(cy - rr, cy + rr + 1):
                dy = (y - cy) / rr
                if abs(dy) > 1:
                    continue
                dx = int(rr * (1 - dy * dy) ** 0.5)
                self._set(cx - dx, y, color)
                self._set(cx + dx, y, color)
            for x in range(cx - rr, cx + rr + 1):
                dx = (x - cx) / rr
                if abs(dx) > 1:
                    continue
                dy = int(rr * (1 - dx * dx) ** 0.5)
                self._set(x, cy - dy, color)
                self._set(x, cy + dy, color)

    def line(self, x1, y1, x2, y2, color, w=1):
        dx, dy = x2 - x1, y2 - y1
        steps = max(abs(dx), abs(dy), 1)
        r = max(w // 2, 0)
        for i in range(steps + 1):
            x = x1 + dx * i // steps
            y = y1 + dy * i // steps
            self.fill_circle(x, y, r, color)

    def fill_poly(self, pts, color):
        ys = [p[1] for p in pts]
        n = len(pts)
        for y in range(max(0, min(ys)), min(self.h - 1, max(ys)) + 1):
            xs = []
            for i in range(n):
                x1, y1 = pts[i]
                x2, y2 = pts[(i + 1) % n]
                if (y1 <= y < y2) or (y2 <= y < y1):
                    xs.append(x1 + (y - y1) * (x2 - x1) / (y2 - y1))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                self.hline(int(xs[i]), int(xs[i + 1]), y, color)

    def text(self, x, y, scale, color, s, align="left"):
        if align == "center":
            x -= text_width(s, scale) // 2
        elif align == "right":
            x -= text_width(s, scale)
        for ci, ch in enumerate(s):
            glyph = FONT.get(ch.upper(), _BLANK)
            ox = x + ci * 6 * scale
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits >> (4 - col) & 1:
                        self.fill_rect(ox + col * scale, y + row * scale,
                                       scale, scale, color)

    def text_lines(self, x, y, scale, color, lines, align="left",
                   line_h=None):
        if line_h is None:
            line_h = 8 * scale
        for i, ln in enumerate(lines):
            self.text(x, y + i * line_h, scale, color, ln, align)


# ---------------------------------------------------------------- png
def save_png(cv, path):
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * cv.w * 3:(y + 1) * cv.w * 3]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(kind, data):
        out = struct.pack(">I", len(data)) + kind + data
        return out + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
           + chunk(b"IDAT", comp) + chunk(b"IEND", b""))
    with open(path, "wb") as fh:
        fh.write(png)
    return len(png)

# ---------------------------------------------------------------- palette
PAPER = (246, 241, 227)
WHITE = (255, 255, 255)
INK = (18, 18, 18)
NAVY = (19, 33, 61)
NAVY_DK = (13, 24, 46)
RED = (193, 39, 45)
GOLD = (232, 180, 74)
BLUE = (29, 78, 137)
TEAL = (18, 92, 84)
GREEN = (30, 107, 58)
BROWN = (122, 74, 33)
ORANGE = (224, 122, 31)
YELLOW = (245, 197, 66)
GREY = (90, 96, 110)
TINT_BLUE = (220, 233, 245)
TINT_RED = (251, 233, 231)
TINT_GREEN = (234, 243, 236)
TINT_GOLD = (251, 238, 220)
TINT_GREY = (232, 238, 245)
TINT_PURPLE = (239, 234, 247)
TINT_TAN = (243, 237, 226)


# ---------------------------------------------------------------- icons
def icon_servers(cv, x, y, w, h):
    """Server rack + lightning bolt: the cyberattack (lead picture)."""
    cv.fill_rect(x, y, w, h, NAVY_DK)
    # server rack, left half
    rx, ry, rw, rh = x + 18, y + 18, 118, h - 36
    cv.fill_rect(rx, ry, rw, rh, (42, 58, 85))
    for k in range(3):
        uy = ry + 8 + k * (rh - 16) // 3
        uh = (rh - 16) // 3 - 8
        cv.fill_rect(rx + 8, uy, rw - 16, uh, (58, 78, 112))
        cv.fill_circle(rx + 20, uy + uh // 2, 4, (120, 200, 120))
        cv.fill_rect(rx + 34, uy + uh // 2 - 2, rw - 52, 4, (180, 190, 205))
    # lightning bolt, right half
    bx, by = x + w - 150, y + 12
    cv.fill_poly([(bx + 78, by), (bx + 18, by + 96), (bx + 52, by + 96),
                  (bx + 26, by + h - 24), (bx + 104, by + 78),
                  (bx + 66, by + 78)], YELLOW)
    # red alert dots on the rack
    cv.fill_circle(rx + rw - 16, ry + 22, 6, RED)
    cv.fill_circle(rx + rw - 16, ry + rh // 2, 6, RED)


def icon_ship(cv, x, y, w, h):
    """Warship on the sea with a blast: Ukraine's strikes at sea."""
    cv.fill_rect(x, y, w, h, TINT_BLUE)
    cv.fill_rect(x, y + h - 42, w, 42, (46, 109, 164))
    cv.line(x + 6, y + h - 30, x + w - 6, y + h - 30, WHITE, 4)
    cv.line(x + 10, y + h - 16, x + w - 10, y + h - 16, WHITE, 4)
    # hull
    hx, hy = x + 14, y + h - 78
    cv.fill_poly([(hx, hy + 26), (hx + w - 28, hy + 26),
                  (hx + w - 48, hy + 52), (hx + 16, hy + 52)], (31, 58, 95))
    cv.fill_rect(hx + 22, hy, 10, 26, (31, 58, 95))
    cv.fill_rect(hx + 52, hy + 8, 8, 18, (31, 58, 95))
    cv.fill_poly([(hx + 32, hy), (hx + 58, hy + 6), (hx + 32, hy + 10)], RED)
    # blast starburst above the bow
    bx, by = x + w - 42, y + 26
    star = []
    for k in range(12):
        ang = k * 30
        r = 26 if k % 2 == 0 else 11
        import math
        star.append((int(bx + r * math.cos(math.radians(ang))),
                     int(by + r * math.sin(math.radians(ang)))))
    cv.fill_poly(star, ORANGE)
    cv.fill_circle(bx, by, 10, YELLOW)


def icon_oil(cv, x, y, w, h):
    """Oil derrick and flame: Russia's refineries under attack."""
    cv.fill_rect(x, y, w, h, TINT_GOLD)
    dx, dy = x + 22, y + 14
    # derrick frame
    cv.line(dx, dy + h - 50, dx + 34, dy, (74, 50, 38), 6)
    cv.line(dx + 68, dy + h - 50, dx + 34, dy, (74, 50, 38), 6)
    cv.line(dx + 8, dy + h - 66, dx + 60, dy + h - 66, (74, 50, 38), 5)
    cv.line(dx + 16, dy + h - 88, dx + 52, dy + h - 88, (74, 50, 38), 5)
    cv.line(dx, dy + h - 50, dx + 68, dy + h - 50, (74, 50, 38), 6)
    # flame
    fx, fy = x + w - 52, y + h - 62
    cv.fill_poly([(fx, fy), (fx + 14, fy - 26), (fx + 26, fy - 8),
                  (fx + 38, fy - 34), (fx + 44, fy), (fx + 30, fy + 12),
                  (fx + 12, fy + 12)], (224, 90, 31))
    cv.fill_poly([(fx + 12, fy + 2), (fx + 22, fy - 14), (fx + 32, fy + 2)],
                 YELLOW)


def icon_cross(cv, x, y, w, h):
    """Red cross: the Ebola hospital evacuation in DR Congo."""
    cv.fill_rect(x, y, w, h, TINT_GREEN)
    cx, cy = x + w // 2, y + h // 2
    cv.fill_rect(cx - 12, cy - 26, 24, 52, RED)
    cv.fill_rect(cx - 26, cy - 12, 52, 24, RED)
    for px, py, r in ((x + 26, y + 16, 5), (x + w - 26, y + 18, 4),
                      (x + 34, y + h - 16, 4), (x + w - 34, y + h - 14, 5)):
        cv.fill_circle(px, py, r, GREEN)


def icon_chip(cv, x, y, w, h):
    """Microchip: Huawei's guilty verdict in a U.S. court."""
    cv.fill_rect(x, y, w, h, TINT_PURPLE)
    cx, cy = x + w // 2, y + h // 2
    for k in range(-1, 2):
        cv.fill_rect(cx - 26, cy + k * 14 - 2, 52, 4, (60, 60, 70))
        cv.fill_rect(cx + k * 14 - 2, cy - 26, 4, 52, (60, 60, 70))
    cv.fill_rect(cx - 22, cy - 22, 44, 44, (40, 40, 52))
    cv.fill_rect(cx - 12, cy - 12, 24, 24, (96, 110, 180))
    cv.fill_rect(cx - 6, cy - 6, 12, 12, (220, 225, 240))


def icon_heli(cv, x, y, w, h):
    """Helicopter: the Turkish training-flight crash."""
    cv.fill_rect(x, y, w, h, TINT_GREY)
    cx, cy = x + w // 2, y + h // 2
    cv.line(cx - 62, cy - 24, cx + 62, cy - 24, (51, 80, 122), 5)
    cv.fill_ellipse(cx - 8, cy, 34, 18, (51, 80, 122))
    cv.fill_ellipse(cx - 8, cy - 2, 20, 11, (140, 180, 215))
    cv.line(cx + 24, cy - 4, cx + 66, cy - 12, (51, 80, 122), 5)
    cv.fill_poly([(cx + 62, cy - 20), (cx + 70, cy - 4), (cx + 58, cy - 4)],
                 (51, 80, 122))
    cv.line(cx - 26, cy + 18, cx + 12, cy + 18, (51, 80, 122), 4)
    cv.line(cx - 20, cy + 18, cx - 26, cy + 24, (51, 80, 122), 4)
    cv.line(cx + 6, cy + 18, cx + 12, cy + 24, (51, 80, 122), 4)


def icon_boat(cv, x, y, w, h):
    """Small boat on waves: migrants missing off Senegal."""
    cv.fill_rect(x, y, w, h, TINT_BLUE)
    cx, cy = x + w // 2, y + h // 2 - 4
    cv.fill_poly([(cx - 66, cy + 2), (cx + 66, cy + 2), (cx + 50, cy + 18),
                  (cx - 50, cy + 18)], (31, 58, 95))
    for ox in (-30, 0, 30):
        cv.fill_circle(cx + ox, cy - 8, 8, (18, 18, 18))
    cv.line(x + 12, cy + 28, x + w - 12, cy + 28, WHITE, 4)
    cv.line(x + 24, cy + 36, x + w - 24, cy + 36, WHITE, 4)


def icon_court(cv, x, y, w, h):
    """Courthouse: Sarkozy and Bruni ordered to trial."""
    cv.fill_rect(x, y, w, h, TINT_TAN)
    cx, cy = x + w // 2, y + h // 2
    cv.fill_poly([(cx - 52, cy - 6), (cx + 52, cy - 6), (cx, cy - 24)],
                 (138, 123, 92))
    for k in (-1, 0, 1):
        cv.fill_rect(cx + k * 30 - 6, cy - 4, 12, 26, (90, 80, 64))
    cv.fill_rect(cx - 58, cy + 22, 116, 6, (90, 80, 64))


def icon_turkey(cv, x, y, w, h):
    """Turkey with fanned tail: the Thanksgiving pardon."""
    cv.fill_rect(x, y, w, h, TINT_GOLD)
    cx, cy = x + w // 2, y + h // 2 + 6
    import math
    for k in range(-2, 3):
        ang = -90 + k * 30
        tx = int(cx + 20 * math.cos(math.radians(ang)))
        ty = int(cy - 2 + 20 * math.sin(math.radians(ang)))
        cv.fill_ellipse(tx, ty, 10, 13, (150, 100, 50))
    cv.fill_ellipse(cx, cy + 8, 19, 13, BROWN)
    cv.fill_circle(cx + 14, cy - 8, 9, BROWN)
    cv.fill_poly([(cx + 22, cy - 10), (cx + 31, cy - 7), (cx + 22, cy - 4)],
                 ORANGE)
    cv.fill_circle(cx + 16, cy - 10, 2, WHITE)


# ---------------------------------------------------------------- panels
def kicker(cv, x, y, w, color, label):
    cv.fill_rect(x, y, w, 30, color)
    cv.text(x + 10, y + 5, 3, WHITE, label)


def panel(cv, x, y, w, h):
    cv.fill_rect(x, y, w, h, WHITE)
    cv.border(x, y, w, h, NAVY, 3)


def build():
    cv = Canvas(W, H, PAPER)

    # ---- masthead ------------------------------------------------------
    cv.fill_rect(0, 0, W, 96, NAVY)
    cv.circle_outline(52, 48, 26, GOLD, 3)
    cv.line(26, 48, 78, 48, GOLD, 2)
    cv.line(52, 22, 52, 74, GOLD, 2)
    cv.fill_ellipse(52, 48, 12, 26, NAVY)
    cv.circle_outline(52, 48, 12, GOLD, 2)
    cv.text(W // 2, 10, 6, WHITE, "ONE DAY IN THE NEWS", "center")
    cv.text(W // 2, 60, 4, GOLD, "WEDNESDAY 25 NOVEMBER 2026", "center")
    cv.fill_rect(0, 96, W, 4, GOLD)

    # ---- lead: CIA cyberattack ----------------------------------------
    panel(cv, 16, 108, 992, 272)
    kicker(cv, 16, 108, 992, RED, "UNITED STATES - CYBERATTACK")
    icon_servers(cv, 32, 152, 360, 212)
    hx = 416
    head = wrap_text("CIA AND U.S. SPY CHIEF'S OFFICE HIT IN CYBERATTACK",
                     992 - hx - 16, 5)
    cv.text_lines(hx, 158, 5, INK, head, line_h=40)
    deck = wrap_text("CNN: classified systems breached - the latest in a "
                     "string of U.S. cyber incidents.", 992 - hx - 16, 3)
    cv.text_lines(hx, 158 + len(head) * 40 + 12, 3, (60, 60, 60), deck,
                  line_h=27)

    # ---- row 2: Ukraine / Putin ---------------------------------------
    panel(cv, 16, 392, 488, 212)
    kicker(cv, 16, 392, 488, BLUE, "UKRAINE - WAR AT SEA")
    icon_ship(cv, 28, 434, 112, 158)
    tx = 156
    head = wrap_text("UKRAINE SINKS RUSSIAN WARSHIP", 488 - (tx - 16) - 16, 4)
    cv.text_lines(tx, 434, 4, INK, head, line_h=32)
    deck = wrap_text("Off Libya and the Gulf of Finland.",
                     488 - (tx - 16) - 16, 3)
    cv.text_lines(tx, 434 + len(head) * 32 + 8, 3, (60, 60, 60), deck,
                  line_h=27)

    panel(cv, 520, 392, 488, 212)
    kicker(cv, 520, 392, 488, (139, 30, 30), "RUSSIA - RETALIATION")
    icon_oil(cv, 532, 434, 112, 158)
    tx = 660
    head = wrap_text("PUTIN VOWS RETALIATION", 488 - (tx - 520) - 16, 4)
    cv.text_lines(tx, 434, 4, INK, head, line_h=32)
    deck = wrap_text("As Ukraine keeps hitting Russian oil refineries.",
                     488 - (tx - 520) - 16, 3)
    cv.text_lines(tx, 434 + len(head) * 32 + 8, 3, (60, 60, 60), deck,
                  line_h=27)

    # ---- row 3 ---------------------------------------------------------
    row3 = [
        (16, "DR CONGO - EBOLA", GREEN, icon_cross,
         "EBOLA HOSPITAL EVACUATED"),
        (352, "U.S. COURTS", (60, 40, 90), icon_chip,
         "HUAWEI FOUND GUILTY"),
        (688, "TURKIYE - CRASH", (51, 80, 122), icon_heli,
         "HELICOPTER CRASH KILLS FIVE"),
    ]
    for x, kick, kc, icon, head_text in row3:
        panel(cv, x, 616, 320, 196)
        kicker(cv, x, 616, 320, kc, kick)
        icon(cv, x + 10, 654, 300, 56)
        head = wrap_text(head_text, 300, 4)
        cv.text_lines(x + 10, 718, 4, INK, head, line_h=30)

    # ---- row 4 ---------------------------------------------------------
    row4 = [
        (16, "MIGRATION", (31, 58, 95), icon_boat,
         "175 MIGRANTS MISSING AT SEA"),
        (352, "FRANCE - COURTS", (90, 80, 64), icon_court,
         "SARKOZY AND BRUNI TO STAND TRIAL"),
        (688, "THANKSGIVING", BROWN, icon_turkey,
         "TRUMP PARDONS TWO TURKEYS"),
    ]
    for x, kick, kc, icon, head_text in row4:
        panel(cv, x, 824, 320, 192)
        kicker(cv, x, 824, 320, kc, kick)
        icon(cv, x + 10, 862, 300, 56)
        head = wrap_text(head_text, 300, 4)
        cv.text_lines(x + 10, 924, 4, INK, head, line_h=30)

    return cv


def main():
    out = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out, exist_ok=True)
    size = save_png(build(), os.path.join(out, "entry.png"))
    print(f"wrote entry.png ({size} bytes)")


if __name__ == "__main__":
    main()
