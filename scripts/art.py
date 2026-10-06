"""Procedural ASCII art: luminance fields mapped onto a character ramp."""
import math

RAMP = " .:-=+*#%@"


def shade(fn, cols, rows):
    out = []
    for r in range(rows):
        line = ''
        for c in range(cols):
            v = fn((c + .5 - cols / 2) / (cols / 2), (r + .5 - rows / 2) / (rows / 2))
            line += v if isinstance(v, str) else RAMP[max(0, min(9, round(v * 9)))]
        out.append(line.rstrip())
    return out


def _eye(x, y):
    X, Y, w = x, y * .62, .94
    if abs(X) >= w:
        return 0
    t = 1 - (X / w) ** 2
    top, bot = -.36 * t ** .8, .27 * t ** .95
    if Y < top:
        # lashes: short strokes leaning away from the centre
        if top - Y < .13 and abs(X) < .82 and (X * 11) % 1 < .2:
            return '/' if X > .12 else '\\' if X < -.12 else '|'
        return 0
    if Y > bot + .025:
        return 0
    if Y > bot - .02:
        return '.' if abs(X) > .5 else ':'
    if Y < top + .04:
        return .97
    r = math.hypot(X, Y)
    if r < .09:
        return 0  # pupil, the star glint sits here
    if r < .28:
        a = math.atan2(Y, X)
        v = .2 + .38 * (.5 + .5 * math.sin(a * 24 + r * 30)) * (r / .28) ** .6
        return .72 if r > .25 else v
    lid = max(0, .14 - (Y - top)) / .14
    return max(.1, .8 - .5 * (X / w) ** 2 - .4 * lid)


def _flower(x, y):
    X, Y = x, y * 1.2
    # stem with a gentle sway
    sx = .05 * math.sin(Y * 2.6 + .4)
    if Y > -.02 and abs(X - sx) < .03:
        return '|'
    for side, ly in ((-1, .38), (1, .62)):
        ux, uy = X - side * .2, Y - ly
        ang = side * -.55
        px = ux * math.cos(ang) - uy * math.sin(ang)
        py = ux * math.sin(ang) + uy * math.cos(ang)
        e = (px / .21) ** 2 + (py / .075) ** 2
        if e < 1:
            return '-' if abs(py) < .014 else .55 - .32 * e
    dx, dy = X, Y + .42
    r, a = math.hypot(dx, dy), math.atan2(dy, dx)
    if r < .085:
        return .98 if r < .05 else .12
    outer = .5 * (.6 + .4 * abs(math.cos(3.5 * a)))
    inner = .34 * (.58 + .42 * abs(math.cos(3.5 * a + math.pi / 2)))
    if r < inner:
        return .95 - .55 * r / inner
    if r < outer:
        return .78 - .58 * (r - inner) / (outer - inner) + .08 * math.cos(7 * a)
    return 0


def eye(cols=64, rows=21):
    return shade(_eye, cols, rows)


def flower(cols=40, rows=26):
    return shade(_flower, cols, rows)


SPIDER = [
    "   /\\ .-. /\\",
    "  /  (o.o)  \\",
    " /  /(_ _)\\  \\",
    "   /  / \\  \\",
]
