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
    """Almond eye with lashes, striated iris and an empty pupil; x is pre-scaled so units are square."""
    w, y = 1.48, y - .1
    if abs(x) >= w:
        return 0
    t = 1 - (x / w) ** 2
    top, bot = -.66 * t ** .85, .52 * t ** .95
    if y < top:
        if top - y < .16 + .06 * t and abs(x) < w * .8 and (x * 5.5) % 1 < .17:
            return '/' if x > .2 else '\\' if x < -.2 else '|'
        return 0
    if y > bot + .05:
        return 0
    if y > bot - .03:
        return '.' if abs(x) > w * .55 else '-'
    if y < top + .07:
        return .97
    r = math.hypot(x, y)
    if r < .17:
        return 0  # pupil: the gold star glint sits here
    if r < .5:
        v = .22 + .4 * (.5 + .5 * math.sin(math.atan2(y, x) * 26 + r * 30)) * (r / .5) ** .5
        return .75 if r > .44 else v
    lid = max(0, .25 - (y - top)) / .25
    return max(.12, .82 - .5 * (x / w) ** 2 - .45 * lid)


def _stem(y):
    return .04 * math.sin(y * 2.6 + 1)


def _rose(x, y):
    """Top-down rose on a stem with two leaves; x is pre-scaled so units are square."""
    dx, dy = x, y + .44
    r, a = math.hypot(dx, dy) / .5, math.atan2(dy, dx)
    edge = 1 + .08 * math.cos(5 * a + .6)
    if r < edge:
        if r > edge - .09:
            return .3
        if r < .09:
            return 1
        s = (a / (2 * math.pi) - 1.1 * math.sqrt(r)) % .5 * 2  # spiral petals
        if s < .13:
            return 0
        return min(1, .25 + .55 * s + .25 * (.5 + .5 * math.cos(a + 2.3)) - .2 * r)
    if y > -.05 and abs(x - _stem(y)) < .02:
        return '|'
    for side, ly, ln, t in ((-1, .36, .26, .55), (1, .6, .22, .5)):
        d = (side * math.cos(t), -math.sin(t))
        cx, cy = _stem(ly) + d[0] * ln, ly + d[1] * ln
        px = (x - cx) * d[0] + (y - cy) * d[1]
        py = -(x - cx) * d[1] + (y - cy) * d[0]
        e = (px / ln) ** 2 + (py / (ln * .38)) ** 2
        if e < 1:
            if abs(py) < .018 and px < ln * .85:
                return '=' if px < 0 else '-'
            return .7 - .45 * e - (.12 if py * side > 0 else 0)
    return 0


EYE_K = .78  # zoom so the eye fills the frame


def eye(cols=70, rows=18):
    """Returns the lines and the pupil centre as (col, row) in character cells."""
    asp = cols * .6 / (rows * 1.15)
    lines = shade(lambda x, y: _eye(x * asp * EYE_K, y * EYE_K), cols, rows)
    return lines, (cols / 2, (.1 / EYE_K + 1) * rows / 2)


def rose(cols=46, rows=30):
    asp = cols * .6 / (rows * 1.15)
    return shade(lambda x, y: _rose(x * asp, y), cols, rows)


SPIDER = [
    r"    \  \  /  /",
    r"  \__\ (oo) /__/",
    r"  ___/ (::) \___",
    r" /   / (__) \   \ ",
    r"    /        \ ",
]
