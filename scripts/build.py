#!/usr/bin/env python3
"""Profile cards for github.com/envyxyz.

    python scripts/build.py [outdir]

Writes hero, terminal, ledger, board and footer SVGs. Live numbers come from the GitHub
GraphQL API when GH_TOKEN is set; without it, mock numbers are used for local previews.
"""
import base64
import datetime as dt
import json
import math
import os
import random
import sys
import urllib.request
from html import escape

import chess
import chess.svg

import art

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGIN = 'envyxyz'
PKT = dt.timezone(dt.timedelta(hours=5))
W = 1000

INK, IVORY, SAND, GOLD, MUTED, ROSE = '#0D1420', '#F3EBDC', '#CDBEA4', '#D6B47E', '#8C93A0', '#C98B7B'
DOTS = ['#0D1420', '#2B4157', '#6F8294', '#8DAF7A', '#C98B7B', '#D6B47E', '#CDBEA4', '#F3EBDC']

CSS = (".s{font-family:S,Georgia,'Times New Roman',serif}"
       ".si{font-family:SI,Georgia,'Times New Roman',serif;font-style:italic}"
       ".m{font-family:M,ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}"
       ".pre{white-space:pre}"
       ".tw{animation:tw 5s ease-in-out infinite}"
       "@keyframes tw{0%,100%{opacity:.15}50%{opacity:1}}"
       ".blink{animation:blink 1.1s steps(1) infinite}"
       "@keyframes blink{50%{opacity:0}}"
       "@media (prefers-reduced-motion:reduce){*{animation:none!important}}")


def fonts(*fams):
    css = ''
    for fam, file, style in (('S', 'serif', 'normal'), ('SI', 'serif-italic', 'italic'), ('M', 'mono', 'normal')):
        if fam in fams:
            with open(os.path.join(ROOT, 'assets', 'fonts', file + '.woff2'), 'rb') as f:
                b64 = base64.b64encode(f.read()).decode()
            css += f"@font-face{{font-family:{fam};font-style:{style};src:url(data:font/woff2;base64,{b64}) format('woff2')}}"
    return css


def svg(h, body, label, *fams, extra_css=''):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {h}" width="{W}" height="{h}" '
            f'role="img" aria-label="{escape(label)}"><title>{escape(label)}</title>'
            f'<style>{fonts(*fams)}{CSS}{extra_css}</style>{body}</svg>')


def text(x, y, s, cls='m', size=13, fill=IVORY, anchor='start', extra=''):
    return (f'<text x="{x:.1f}" y="{y:.1f}" class="{cls}" font-size="{size}" fill="{fill}" '
            f'text-anchor="{anchor}" {extra}>{escape(s)}</text>')


def star(cx, cy, r, fill=GOLD, tail=1.0, extra=''):
    """Four-point sparkle; tail > 1 stretches the bottom ray like the poster star."""
    k = r * .14
    b = r * tail
    return (f'<path d="M{cx},{cy - r} C{cx + k},{cy - k} {cx + k},{cy - k} {cx + r},{cy} '
            f'C{cx + k},{cy + k} {cx + k},{cy + k} {cx},{cy + b} C{cx - k},{cy + k} {cx - k},{cy + k} {cx - r},{cy} '
            f'C{cx - k},{cy - k} {cx - k},{cy - k} {cx},{cy - r}Z" fill="{fill}" {extra}/>')


# ---------------------------------------------------------------- wallpaper + glass

# Monaco at dusk, as soft light blobs: (cx, cy, rx, ry) as fractions of the card, colour, opacity.
BLOBS = [
    (.50, -.10, .80, .55, '#070C17', .85),
    (.72, .70, .42, .34, '#E7B27C', .55),
    (.20, .62, .46, .34, '#B97568', .45),
    (.40, 1.05, .70, .36, '#1C4659', .70),
    (.72, .92, .07, .22, '#EBC690', .30),
    (.95, .30, .30, .30, '#2B3A5E', .50),
]


def wallpaper(uid, w, h, seed=7, stars=26):
    rnd = random.Random(seed)
    defs = [f'<linearGradient id="{uid}sky" x1="0" y1="0" x2="0" y2="1">'
            '<stop offset="0" stop-color="#0B1220"/><stop offset=".42" stop-color="#18223A"/>'
            '<stop offset=".6" stop-color="#3E3A50"/><stop offset=".7" stop-color="#8A6660"/>'
            '<stop offset=".77" stop-color="#26394F"/><stop offset="1" stop-color="#0A1522"/></linearGradient>'
            f'<pattern id="{uid}dot" width="6" height="6" patternUnits="userSpaceOnUse">'
            f'<circle cx="3" cy="3" r="1" fill="{IVORY}"/></pattern>'
            f'<linearGradient id="{uid}hm" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".5"/>'
            '<stop offset=".45" stop-color="#fff" stop-opacity="0"/><stop offset=".7" stop-color="#fff" stop-opacity=".25"/>'
            '<stop offset="1" stop-color="#fff" stop-opacity=".9"/></linearGradient>'
            f'<mask id="{uid}m"><rect width="{w}" height="{h}" fill="url(#{uid}hm)"/></mask>']
    for i, (_, _, _, _, col, op) in enumerate(BLOBS):
        defs.append(f'<radialGradient id="{uid}b{i}"><stop offset="0" stop-color="{col}" stop-opacity="{op}"/>'
                    f'<stop offset=".5" stop-color="{col}" stop-opacity="{op * .45:.3f}"/>'
                    f'<stop offset="1" stop-color="{col}" stop-opacity="0"/></radialGradient>')
    body = [f'<rect width="{w}" height="{h}" fill="url(#{uid}sky)"/>', blobs(uid, w, h, 1)]
    body.append(f'<rect width="{w}" height="{h}" fill="url(#{uid}dot)" mask="url(#{uid}m)" opacity=".09"/>')
    for _ in range(stars):
        x, y = rnd.uniform(10, w - 10), rnd.uniform(6, h * .5)
        d = f'style="animation-delay:-{rnd.uniform(0, 5):.1f}s;animation-duration:{rnd.uniform(3, 7):.1f}s"'
        if rnd.random() < .18:
            body.append(star(round(x), round(y), rnd.choice((3, 4, 5)), IVORY, extra=f'class="tw" {d}'))
        else:
            body.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{rnd.uniform(.5, 1.3):.1f}" fill="{IVORY}" class="tw" {d}/>')
    return '<defs>' + ''.join(defs) + '</defs>' + ''.join(body)


def blobs(uid, w, h, spread):
    return ''.join(f'<ellipse cx="{cx * w:.0f}" cy="{cy * h:.0f}" rx="{rx * w * spread:.0f}" ry="{ry * h * spread:.0f}" '
                   f'fill="url(#{uid}b{i})"/>' for i, (cx, cy, rx, ry, _, _) in enumerate(BLOBS))


def window(uid, x, y, w, h, title, W_, H_):
    """macOS style frosted window. The inside repeats the wallpaper light, spread wider (the blur)."""
    clip = f'<clipPath id="{uid}c"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12"/></clipPath>'
    shadow = ''.join(f'<rect x="{x - s}" y="{y + s * 1.6}" width="{w + 2 * s}" height="{h + s}" rx="{12 + s}" '
                     f'fill="#000" opacity="{o}"/>' for s, o in ((4, .14), (9, .08), (16, .05)))
    glass = (f'<g clip-path="url(#{uid}c)"><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#141B2B"/>'
             f'{blobs(uid, W_, H_, 1.5)}'
             f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#0B111D" opacity=".62"/>'
             f'<rect x="{x}" y="{y}" width="{w}" height="34" fill="{IVORY}" opacity=".035"/></g>')
    rim = (f'<linearGradient id="{uid}r" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{IVORY}" stop-opacity=".38"/>'
           f'<stop offset=".5" stop-color="{IVORY}" stop-opacity=".08"/><stop offset="1" stop-color="{IVORY}" stop-opacity=".2"/></linearGradient>'
           f'<rect x="{x + .5}" y="{y + .5}" width="{w - 1}" height="{h - 1}" rx="11.5" fill="none" stroke="url(#{uid}r)"/>'
           f'<line x1="{x}" y1="{y + 34.5}" x2="{x + w}" y2="{y + 34.5}" stroke="{IVORY}" stroke-opacity=".08"/>')
    lights = ''.join(f'<circle cx="{x + 20 + i * 19}" cy="{y + 17}" r="6" fill="{c}"/>'
                     for i, c in enumerate(('#D9776B', '#D8B06A', '#8EAD7A')))
    return (f'<defs>{clip}</defs>{shadow}{glass}{rim}{lights}'
            + text(x + w / 2, y + 21.5, title, size=11.5, fill=MUTED, anchor='middle'))


def card_frame(uid, h, inner):
    return (f'<defs><clipPath id="{uid}card"><rect width="{W}" height="{h}" rx="16"/></clipPath></defs>'
            f'<g clip-path="url(#{uid}card)">{inner}</g>')


def ascii_block(lines, x, y, size, fill=IVORY, lh=None, extra=''):
    lh = lh or size * 1.2
    rows = ''.join(f'<text x="{x:.1f}" y="{y + i * lh:.1f}">{escape(s)}</text>' for i, s in enumerate(lines) if s.strip())
    return f'<g class="m pre" font-size="{size}" fill="{fill}" {extra}>{rows}</g>'


# ---------------------------------------------------------------- data

QUERY = '''query($login:String!){user(login:$login){createdAt followers{totalCount}
repositories(ownerAffiliations:OWNER,first:100,isFork:false,privacy:PUBLIC){totalCount
nodes{stargazerCount languages(first:8,orderBy:{field:SIZE,direction:DESC}){edges{size node{name}}}}}
contributionsCollection{contributionCalendar{totalContributions
weeks{contributionDays{date contributionCount contributionLevel}}}}}}'''
LEVEL = {'NONE': 0, 'FIRST_QUARTILE': 1, 'SECOND_QUARTILE': 2, 'THIRD_QUARTILE': 3, 'FOURTH_QUARTILE': 4}


def fetch():
    token = os.environ.get('GH_TOKEN')
    if not token:
        return mock()
    req = urllib.request.Request('https://api.github.com/graphql',
                                 json.dumps({'query': QUERY, 'variables': {'login': LOGIN}}).encode(),
                                 {'Authorization': f'bearer {token}', 'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=30) as r:
        u = json.load(r)['data']['user']
    langs = {}
    for repo in u['repositories']['nodes']:
        for e in repo['languages']['edges']:
            langs[e['node']['name']] = langs.get(e['node']['name'], 0) + e['size']
    cal = u['contributionsCollection']['contributionCalendar']
    return {
        'created': dt.datetime.fromisoformat(u['createdAt'].replace('Z', '+00:00')),
        'repos': u['repositories']['totalCount'],
        'stars': sum(r['stargazerCount'] for r in u['repositories']['nodes']),
        'langs': langs,
        'total': cal['totalContributions'],
        'weeks': [[(d['date'], d['contributionCount'], LEVEL[d['contributionLevel']]) for d in w['contributionDays']]
                  for w in cal['weeks']],
    }


def mock():
    rnd = random.Random(3)
    start = dt.date.today() - dt.timedelta(days=364)
    start -= dt.timedelta(days=(start.weekday() + 1) % 7)
    weeks, day = [], start
    while day <= dt.date.today():
        week = []
        for _ in range(7):
            if day > dt.date.today():
                break
            n = 0 if rnd.random() < .45 else int(rnd.expovariate(.25)) + 1
            week.append((day.isoformat(), n, min(4, (n + 2) // 3)))
            day += dt.timedelta(days=1)
        weeks.append(week)
    return {'created': dt.datetime(2021, 3, 5, tzinfo=dt.timezone.utc), 'repos': 11, 'stars': 2,
            'langs': {'JavaScript': 610, 'HTML': 220, 'CSS': 90, 'TypeScript': 80},
            'total': sum(n for w in weeks for _, n, _ in w), 'weeks': weeks}


def streaks(days):
    best = run = 0
    for _, n, _ in days:
        run = run + 1 if n else 0
        best = max(best, run)
    seq = [n for _, n, _ in days]
    if seq and not seq[-1]:
        seq.pop()  # today is still young
    cur = 0
    for n in reversed(seq):
        if not n:
            break
        cur += 1
    return cur, best


def greeting(now):
    h = now.hour
    return 'Good morning' if 5 <= h < 12 else 'Good afternoon' if h < 17 else 'Bonsoir' if h < 22 else 'Bonne nuit'


def uptime(created, now):
    months = (now.year - created.year) * 12 + now.month - created.month - (now.day < created.day)
    return f'{months // 12} yrs, {months % 12} mos'


# ---------------------------------------------------------------- cards

def hero(d, now):
    h = 470
    wx, wy, ww, wh = 64, 66, 872, 352
    body = [wallpaper('h', W, h, seed=11, stars=34)]
    # menu bar
    body.append(f'<rect width="{W}" height="28" fill="#05080F" opacity=".45"/>')
    body.append(star(22, 14, 6.5, GOLD))
    body.append(text(40, 18.5, 'envyxyz', size=11.5, fill=IVORY))
    for i, s in enumerate(('Studio', 'Work', 'Ledger', 'Board')):
        body.append(text(112 + i * 62, 18.5, s, size=11.5, fill=IVORY, extra='opacity=".62"'))
    body.append(text(W - 20, 18.5, now.strftime('%a %-d %b') + '   33.68°N 73.05°E', size=11.5,
                     fill=IVORY, anchor='end', extra='opacity=".75"'))
    body.append(window('h', wx, wy, ww, wh, '~/envyxyz · portrait', W, h))

    # the eye, with a crosshair over the iris
    lines = art.eye(64, 21)
    fs, cw, lh = 8.6, 8.6 * .6, 10.4
    ex, ey = wx + 50, wy + 70
    cx, cy = ex + 32 * cw, ey + 10.5 * lh - lh * .3
    # blink: squash vertically around the eye's centre line
    body.append(f'<g transform="translate(0 {cy:.1f})"><g>'
                f'<animateTransform attributeName="transform" type="scale" values="1 1;1 1;1 .06;1 1" '
                f'keyTimes="0;.955;.975;1" dur="7s" repeatCount="indefinite"/>'
                f'<g transform="translate(0 {-cy:.1f})">' + ascii_block(lines, ex, ey, fs, IVORY, lh, 'opacity=".9"')
                + star(round(cx), round(cy), 7, GOLD, 1.9) + '</g></g></g>')
    ticks = ''.join(f'<line x1="{cx + math.cos(a) * 60:.1f}" y1="{cy + math.sin(a) * 60:.1f}" '
                    f'x2="{cx + math.cos(a) * 74:.1f}" y2="{cy + math.sin(a) * 74:.1f}"/>'
                    for a in (0, math.pi / 2, math.pi, 3 * math.pi / 2))
    body.append(f'<g stroke="{GOLD}" stroke-width="1" fill="none" opacity=".85">'
                f'<animateTransform attributeName="transform" type="rotate" from="0 {cx:.1f} {cy:.1f}" '
                f'to="360 {cx:.1f} {cy:.1f}" dur="40s" repeatCount="indefinite"/>'
                f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="54" stroke-dasharray="70 14.8"/>{ticks}</g>')

    # words
    tx = wx + 470
    body.append(text(tx, wy + 104, 'N° 001  ·  EST. 2021  ·  ISLAMABAD', size=11, fill=GOLD, extra='letter-spacing="2.2"'))
    body.append(text(tx - 4, wy + 186, 'Ameer', 'si', 88, IVORY))
    body.append(text(tx, wy + 226, 'Founder of AH Growth.', 's', 22, SAND))
    body.append(text(tx, wy + 254, 'Quiet, well-made software for good brands.', 's', 22, SAND))
    body.append(f'<line x1="{tx}" y1="{wy + 280}" x2="{tx + 36}" y2="{wy + 280}" stroke="{GOLD}"/>')
    body.append(typing(tx, wy + 310, ['building OpenHelios, a personal ops agent',
                                      'shipping websites for brands with taste',
                                      'automating the dull parts of business'], 13))
    return svg(h, card_frame('h', h, ''.join(body)), 'Ameer, founder of AH Growth', 'S', 'SI', 'M')


def typing(x, y, phrases, fs, slot=6.0):
    cw, total = fs * .6, slot * len(phrases)
    out = [text(x, y, '>', size=fs, fill=GOLD)]
    x += cw * 2
    for i, p in enumerate(phrases):
        t0, times, n = i * slot, [0.0], [0]
        for k in range(1, len(p) + 1):
            times.append(t0 + .4 + k * .05)
            n.append(k)
        end = t0 + slot - .5 - len(p) * .02
        for k in range(len(p) - 1, -1, -1):
            times.append(end + (len(p) - k) * .02)
            n.append(k)
        times.append(total)
        n.append(0)
        kt = ';'.join(f'{t / total:.4f}' for t in times)
        anim = f'keyTimes="{kt}" dur="{total}s" calcMode="discrete" repeatCount="indefinite"'
        out.append(f'<clipPath id="ty{i}"><rect x="{x}" y="{y - fs}" height="{fs * 1.6}" width="0">'
                   f'<animate attributeName="width" values="{";".join(f"{k * cw:.1f}" for k in n)}" {anim}/></rect></clipPath>'
                   + text(x, y, p, size=fs, fill=IVORY, cls='m pre', extra=f'clip-path="url(#ty{i})" opacity=".88"'))
        vis = f'0;{t0 / total:.4f};{(t0 + slot) / total:.4f}' if i else f'0;{slot / total:.4f}'
        vals = 'hidden;visible;hidden' if i else 'visible;hidden'
        out.append(f'<rect y="{y - fs * .85:.1f}" width="{cw:.1f}" height="{fs * 1.05:.1f}" fill="{GOLD}" x="{x}">'
                   f'<animate attributeName="x" values="{";".join(f"{x + k * cw:.1f}" for k in n)}" {anim}/>'
                   f'<animate attributeName="visibility" values="{vals}" keyTimes="{vis}" dur="{total}s" '
                   f'calcMode="discrete" repeatCount="indefinite"/>'
                   f'<animate attributeName="opacity" values="1;0" dur="1.1s" calcMode="discrete" repeatCount="indefinite"/></rect>')
    return ''.join(out)


def terminal(d, now):
    h = 452
    wx, wy, ww, wh = 40, 30, 920, 392
    body = [wallpaper('t', W, h, seed=5, stars=22), window('t', wx, wy, ww, wh, 'ameer@envyxyz: ~ · zsh', W, h)]
    body.append(text(wx + 26, wy + 62, 'zsh 5.9', size=12, fill='#B9C98A'))
    body.append(ascii_block(art.flower(40, 26), wx + 34, wy + 88, 10, SAND, 11.6, 'opacity=".92"'))

    ix, iy = wx + 360, wy + 66
    body.append(text(ix, iy, 'Hey, ', size=13, fill=IVORY) + text(ix + 39, iy, 'Ameer', size=13, fill=GOLD))
    total = sum(d['langs'].values()) or 1
    langs = sorted(d['langs'].items(), key=lambda kv: -kv[1])[:4]
    groups = [
        ('Profile', [('ROLE', 'Founder, AH Growth'), ('BASE', 'Islamabad, Pakistan'),
                     ('STACK', 'React · Supabase · Node · Python'), ('NOW', 'OpenHelios · Proposal Studio')]),
        ('System', [('REPOS', f"{d['repos']} public · {d['stars']} stars"), ('LANGS', None),
                    ('UPTIME', uptime(d['created'], now) + ' on GitHub'),
                    ('SYNCED', now.strftime('%a %d %b %Y, %H:%M') + ' PKT')]),
    ]
    y = iy + 22
    bw = 470
    for name, rows in groups:
        gh = 22 + len(rows) * 21
        body.append(f'<path d="M{ix},{y + 6} v{gh - 6} h{bw} v{-(gh - 6)}" fill="none" stroke="{SAND}" stroke-opacity=".4"/>')
        tw = len(name) * 7.2 + 16
        body.append(f'<path d="M{ix},{y + 6} h{(bw - tw) / 2:.1f} M{ix + (bw + tw) / 2:.1f},{y + 6} H{ix + bw}" '
                    f'stroke="{SAND}" stroke-opacity=".4"/>')
        body.append(text(ix + bw / 2, y + 10, name, size=12, fill=SAND, anchor='middle'))
        for i, (k, v) in enumerate(rows):
            ry = y + 32 + i * 21
            last = i == len(rows) - 1
            body.append(f'<path d="M{ix + 12},{ry - 15} V{ry - 4 if last else ry + 6} M{ix + 12},{ry - 4} h8" '
                        f'stroke="{SAND}" stroke-opacity=".45" fill="none"/>')
            body.append(text(ix + 26, ry, k, size=12, fill='#B9C98A'))
            if v is not None:
                body.append(text(ix + 100, ry, v, size=12.5, fill=IVORY))
            else:
                bx, bwid = ix + 100, 230
                body.append(f'<rect x="{bx}" y="{ry - 9}" width="{bwid}" height="8" rx="1" fill="{IVORY}" opacity=".08"/>')
                acc, legend = 0, []
                for (lang, size), col in zip(langs, (GOLD, ROSE, '#8DAF7A', '#6F8294')):
                    wpart = bwid * size / total
                    body.append(f'<rect x="{bx + acc:.1f}" y="{ry - 9}" width="{max(wpart - 1.5, 1):.1f}" height="8" fill="{col}"/>')
                    acc += wpart
                    legend.append(f'{lang[:2].upper() if lang != "JavaScript" else "JS"} {round(100 * size / total)}')
                body.append(text(bx + bwid + 12, ry, '  '.join(legend[:3]), size=11, fill=MUTED))
        y += gh + 16
    body.append(text(ix, y + 14, greeting(now) + ', Ameer.', size=13, fill=GOLD))
    body.append(''.join(f'<circle cx="{ix + 6 + i * 16}" cy="{y + 36}" r="4.5" fill="{c}" stroke="{IVORY}" stroke-opacity=".25"/>'
                        for i, c in enumerate(DOTS)))
    py = wy + wh - 24
    body.append(text(wx + 26, py, 'ameer@envyxyz ~ % ', size=12.5, fill='#B9C98A'))
    body.append(f'<rect x="{wx + 26 + 18 * 7.5:.1f}" y="{py - 11}" width="7.5" height="14" fill="{IVORY}" class="blink"/>')
    return svg(h, card_frame('t', h, ''.join(body)), 'Terminal card: profile and live GitHub stats', 'M')


def ledger(d, now):
    h = 300
    wx, wy, ww, wh = 40, 26, 920, 248
    body = [wallpaper('l', W, h, seed=3, stars=14), window('l', wx, wy, ww, wh, 'ledger · the last twelve months', W, h)]
    days = [x for w in d['weeks'] for x in w]
    cur, best = streaks(days)
    peak = max(days, key=lambda x: x[1])
    body.append(text(wx + 32, wy + 78, 'The Ledger', 'si', 30, IVORY))
    body.append(text(wx + 34, wy + 100, f"{d['total']:,} contributions in the last year", size=12, fill=MUTED))
    stats = [('STREAK', f'{cur} day' + ('s' if cur != 1 else '')), ('BEST', f'{best} days'), ('PEAK', f'{peak[1]}')]
    for i, (k, v) in enumerate(reversed(stats)):
        x = wx + ww - 34 - i * 110
        body.append(text(x, wy + 70, k, size=10.5, fill=GOLD, anchor='end', extra='letter-spacing="2"'))
        body.append(text(x, wy + 98, v, 's', 24, IVORY, anchor='end'))

    cell, gap = 12, 3.2
    weeks = d['weeks']
    gx = wx + (ww - len(weeks) * (cell + gap)) / 2
    gy = wy + 136
    alpha = [.07, .28, .5, .75, 1]
    month = None
    target = (gx, gy)
    for c, week in enumerate(weeks):
        for date, n, lvl in week:
            r = (dt.date.fromisoformat(date).weekday() + 1) % 7
            x, y = gx + c * (cell + gap), gy + r * (cell + gap)
            fill = IVORY if lvl == 0 else GOLD
            body.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{cell}" height="{cell}" rx="2.5" fill="{fill}" '
                        f'opacity="{alpha[lvl]}"/>')
            if (date, n, lvl) == peak:
                target = (x + cell / 2, y + cell / 2)
            m = date[5:7]
            if r == 0 and m != month and c < len(weeks) - 2:
                month = m
                body.append(text(x, gy - 10, dt.date.fromisoformat(date).strftime('%b'), size=10, fill=MUTED))
    # crosshair: sweeps in, locks on the peak day, pulses
    tx, ty = target
    sx, sy = gx - 30, gy + 3.5 * (cell + gap)
    path = f'M{sx - tx:.1f},{sy - ty:.1f} C{(sx - tx) * .3:.1f},{-60:.1f} {(sx - tx) * .1:.1f},{40:.1f} 0,0'
    reticle = (f'<circle r="11" fill="none" stroke="{IVORY}" stroke-width="1.2"/>'
               f'<path d="M-18,0h9M9,0h9M0,-18v9M0,9v9" stroke="{IVORY}" stroke-width="1.2"/>'
               f'<circle r="11" fill="none" stroke="{GOLD}"><animate attributeName="r" values="11;20" dur="1.8s" begin="2.6s" repeatCount="indefinite"/>'
               f'<animate attributeName="opacity" values=".9;0" dur="1.8s" begin="2.6s" repeatCount="indefinite"/></circle>')
    body.append(f'<g transform="translate({tx:.1f} {ty:.1f})"><g>'
                f'<animateMotion path="{path}" dur="2.4s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines=".6 0 .2 1"/>'
                f'{reticle}</g></g>')
    label = f"PEAK  {dt.date.fromisoformat(peak[0]).strftime('%d %b').upper()}  ·  {peak[1]}"
    lx = min(max(tx, gx + 90), gx + len(weeks) * (cell + gap) - 90)
    ly = gy + 7 * (cell + gap) + 24
    body.append(f'<text x="{lx:.1f}" y="{ly}" class="m" font-size="10.5" fill="{GOLD}" text-anchor="middle" '
                f'letter-spacing="1.5" opacity="0">{label}<animate attributeName="opacity" from="0" to="1" '
                f'begin="2.4s" dur=".6s" fill="freeze"/></text>')
    body.append(text(gx, ly, 'Sun · Sat rows, oldest week left', size=10, fill=MUTED))
    return svg(h, card_frame('l', h, ''.join(body)), f"{d['total']} contributions in the last year", 'SI', 'S', 'M')


def board(state):
    h = 470
    wx, wy, ww, wh = 40, 26, 920, 418
    body = [wallpaper('b', W, h, seed=9, stars=16), window('b', wx, wy, ww, wh, 'the open board · chess', W, h)]
    b = chess.Board(state['fen'])
    sq = 41
    bx, by = wx + 70, wy + 62
    light, dark = '#E9DFCB', '#6F8294'
    last = chess.Move.from_uci(state['moves'][-1]['uci']) if state['moves'] else None
    for s in chess.SQUARES:
        f, r = chess.square_file(s), chess.square_rank(s)
        x, y = bx + f * sq, by + (7 - r) * sq
        body.append(f'<rect x="{x}" y="{y}" width="{sq}" height="{sq}" fill="{light if (f + r) % 2 else dark}"/>')
        if last and s in (last.from_square, last.to_square):
            body.append(f'<rect x="{x}" y="{y}" width="{sq}" height="{sq}" fill="{GOLD}" opacity="{.35 if s == last.from_square else .55}"/>')
        if b.is_check() and s == b.king(b.turn):
            body.append(f'<rect x="{x}" y="{y}" width="{sq}" height="{sq}" fill="#9E3B3B" opacity=".55"/>')
        p = b.piece_at(s)
        if p:
            g = chess.svg.PIECES[p.symbol()]
            g = g.replace('#fff', '@L').replace('#000', '@D').replace('@L', IVORY).replace('@D', '#141B26')
            g = g.replace(' id="', ' data-id="')
            body.append(f'<g transform="translate({x + (sq - 45 * .86) / 2:.1f} {y + (sq - 45 * .86) / 2:.1f}) scale(.86)">{g}</g>')
    body.append(f'<rect x="{bx - .5}" y="{by - .5}" width="{sq * 8 + 1}" height="{sq * 8 + 1}" fill="none" stroke="{IVORY}" stroke-opacity=".35"/>')
    for i in range(8):
        body.append(text(bx + i * sq + sq / 2, by + 8 * sq + 18, 'abcdefgh'[i], size=10.5, fill=MUTED, anchor='middle'))
        body.append(text(bx - 14, by + i * sq + sq / 2 + 4, str(8 - i), size=10.5, fill=MUTED, anchor='middle'))
    if last:  # target brackets on the destination square
        x = bx + chess.square_file(last.to_square) * sq
        y = by + (7 - chess.square_rank(last.to_square)) * sq
        k, e = 9, 3
        body.append(f'<path d="M{x + e},{y + e + k}v{-k}h{k}M{x + sq - e - k},{y + e}h{k}v{k}M{x + sq - e},{y + sq - e - k}v{k}h{-k}'
                    f'M{x + e + k},{y + sq - e}h{-k}v{-k}" fill="none" stroke="#141B26" stroke-width="2"/>')

    tx = bx + 8 * sq + 66
    turn = 'White' if b.turn else 'Black'
    over = b.is_game_over()
    body.append(text(tx, wy + 88, 'THE OPEN BOARD', size=11, fill=GOLD, extra='letter-spacing="2.4"'))
    body.append(text(tx - 2, wy + 140, 'Game over.' if over else 'Your move.', 'si', 46, IVORY))
    status = state.get('result') if over else f'{turn} to play, move {b.fullmove_number}.'
    body.append(text(tx, wy + 176, status, 's', 21, SAND))
    for i, line in enumerate(('Anyone with a GitHub account can play the', 'next move. Choose one below; the board',
                              'answers in about a minute.')):
        body.append(text(tx, wy + 214 + i * 24, line, 's', 18, SAND, extra='opacity=".85"'))
    rows = [('LAST', f"{state['moves'][-1]['san']}  by @{state['moves'][-1]['by']}" if state['moves'] else 'none yet'),
            ('PLAYERS', str(len(state['players']))),
            ('FINISHED', f"{state['finished']} game" + ('s' if state['finished'] != 1 else ''))]
    for i, (k, v) in enumerate(rows):
        y = wy + 316 + i * 24
        body.append(text(tx, y, k, size=11, fill=GOLD, extra='letter-spacing="1.6"'))
        body.append(text(tx + 96, y, v, size=12.5, fill=IVORY))
    return svg(h, card_frame('b', h, ''.join(body)), f'Community chess, {turn} to play', 'S', 'SI', 'M')


def footer():
    h = 190
    body = [wallpaper('f', W, h, seed=2, stars=20)]
    body.append(f'<rect width="{W}" height="{h}" fill="#0B111D" opacity=".35"/>')
    body.append(text(W / 2, 92, 'Festina lente.', 'si', 40, IVORY, anchor='middle'))
    body.append(text(W / 2, 124, 'MAKE HASTE, SLOWLY', size=11, fill=GOLD, anchor='middle', extra='letter-spacing="3"'))
    sx = 860
    body.append(f'<g><animateTransform attributeName="transform" type="rotate" values="-3 {sx} 0;3 {sx} 0;-3 {sx} 0" '
                f'dur="6s" repeatCount="indefinite"/>'
                f'<line x1="{sx}" y1="0" x2="{sx}" y2="96" stroke="{IVORY}" stroke-opacity=".45"/>'
                + ascii_block(art.SPIDER, sx - 6.6 * 6.6, 110, 11, IVORY, 13) + '</g>')
    return svg(h, card_frame('f', h, ''.join(body)), 'Festina lente', 'SI', 'M')


# ---------------------------------------------------------------- main

def load_game():
    try:
        with open(os.path.join(ROOT, 'game', 'chess.json')) as f:
            return json.load(f)
    except FileNotFoundError:
        return {'fen': chess.STARTING_FEN, 'moves': [], 'players': [], 'finished': 0, 'result': None}


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'dist')
    os.makedirs(out, exist_ok=True)
    d, now = fetch(), dt.datetime.now(PKT)
    cards = {'hero': hero(d, now), 'terminal': terminal(d, now), 'ledger': ledger(d, now),
             'board': board(load_game()), 'footer': footer()}
    for name, s in cards.items():
        with open(os.path.join(out, name + '.svg'), 'w') as f:
            f.write(s)
        print(f'{name}.svg  {len(s) // 1024} KB')


if __name__ == '__main__':
    main()
