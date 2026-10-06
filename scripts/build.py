#!/usr/bin/env python3
"""Profile cards for github.com/envyxyz.

    python scripts/build.py [outdir]

Writes hero, terminal, ledger and footer SVGs. Live numbers come from the GitHub
GraphQL API when GH_TOKEN is set; without it, mock numbers are used for local previews.
"""
import base64
import xml.dom.minidom
import datetime as dt
import json
import os
import random
import sys
import urllib.request
from html import escape

import art

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGIN = 'envyxyz'
PKT = dt.timezone(dt.timedelta(hours=5))
W = 1000

BG, FG, SOFT, MUTED, LINE = '#0D1117', '#E8E6E1', '#B9BDC4', '#8B949E', '#30363D'

CSS = (".s{font-family:S,Georgia,'Times New Roman',serif}"
       ".si{font-family:SI,Georgia,'Times New Roman',serif;font-style:italic}"
       ".m{font-family:M,ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-feature-settings:'calt' 0,'liga' 0}"
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


def text(x, y, s, cls='m', size=13, fill=FG, anchor='start', extra=''):
    return (f'<text x="{x:.1f}" y="{y:.1f}" class="{cls}" font-size="{size}" fill="{fill}" '
            f'text-anchor="{anchor}" {extra}>{escape(s)}</text>')


def star(cx, cy, r, fill=FG, tail=1.0, extra=''):
    """Four-point sparkle; tail > 1 stretches the bottom ray like the poster star."""
    k = r * .14
    b = r * tail
    return (f'<path d="M{cx},{cy - r} C{cx + k},{cy - k} {cx + k},{cy - k} {cx + r},{cy} '
            f'C{cx + k},{cy + k} {cx + k},{cy + k} {cx},{cy + b} C{cx - k},{cy + k} {cx - k},{cy + k} {cx - r},{cy} '
            f'C{cx - k},{cy - k} {cx - k},{cy - k} {cx},{cy - r}Z" fill="{fill}" {extra}/>')


# ---------------------------------------------------------------- wallpaper + glass

# soft light behind the terminal window: (cx, cy, rx, ry) as fractions of the card, opacity
LIGHT = [(.20, .72, .44, .40, .34), (.80, .30, .40, .40, .16), (.55, 1.05, .60, .30, .22)]


def blobs(uid, w, h, spread):
    return ''.join(f'<ellipse cx="{cx * w:.0f}" cy="{cy * h:.0f}" rx="{rx * w * spread:.0f}" ry="{ry * h * spread:.0f}" '
                   f'fill="url(#{uid}b{i})"/>' for i, (cx, cy, rx, ry, _) in enumerate(LIGHT))


def wallpaper(uid, w, h, seed=7, stars=22):
    rnd = random.Random(seed)
    defs = ''.join(f'<radialGradient id="{uid}b{i}"><stop offset="0" stop-color="{FG}" stop-opacity="{op}"/>'
                   f'<stop offset=".5" stop-color="{FG}" stop-opacity="{op * .45:.3f}"/>'
                   f'<stop offset="1" stop-color="{FG}" stop-opacity="0"/></radialGradient>'
                   for i, (*_, op) in enumerate(LIGHT))
    dots = ''.join(f'<circle cx="{rnd.uniform(10, w - 10):.0f}" cy="{rnd.uniform(6, h * .5):.0f}" '
                   f'r="{rnd.uniform(.5, 1.2):.1f}" fill="{FG}" opacity="{rnd.uniform(.2, .7):.2f}"/>' for _ in range(stars))
    return f'<defs>{defs}</defs><rect width="{w}" height="{h}" fill="#090B0F"/>{blobs(uid, w, h, 1)}{dots}'


def window(uid, x, y, w, h, title, W_, H_):
    """macOS style frosted window. The inside repeats the wallpaper light, spread wider (the blur)."""
    clip = f'<clipPath id="{uid}c"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12"/></clipPath>'
    shadow = ''.join(f'<rect x="{x - s}" y="{y + s * 1.6}" width="{w + 2 * s}" height="{h + s}" rx="{12 + s}" '
                     f'fill="#000" opacity="{o}"/>' for s, o in ((4, .14), (9, .08), (16, .05)))
    glass = (f'<g clip-path="url(#{uid}c)"><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#15181E"/>'
             f'{blobs(uid, W_, H_, 1.5)}'
             f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#0B0D11" opacity=".66"/>'
             f'<rect x="{x}" y="{y}" width="{w}" height="34" fill="{FG}" opacity=".035"/></g>')
    rim = (f'<linearGradient id="{uid}r" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{FG}" stop-opacity=".38"/>'
           f'<stop offset=".5" stop-color="{FG}" stop-opacity=".08"/><stop offset="1" stop-color="{FG}" stop-opacity=".2"/></linearGradient>'
           f'<rect x="{x + .5}" y="{y + .5}" width="{w - 1}" height="{h - 1}" rx="11.5" fill="none" stroke="url(#{uid}r)"/>'
           f'<line x1="{x}" y1="{y + 34.5}" x2="{x + w}" y2="{y + 34.5}" stroke="{FG}" stroke-opacity=".08"/>')
    lights = ''.join(f'<circle cx="{x + 20 + i * 19}" cy="{y + 17}" r="5.5" fill="{FG}" opacity="{o}"/>'
                     for i, o in enumerate((.5, .32, .18)))
    return (f'<defs>{clip}</defs>{shadow}{glass}{rim}{lights}'
            + text(x + w / 2, y + 21.5, title, size=11.5, fill=MUTED, anchor='middle'))


def panel(h, inner, split=None):
    """Flat card: GitHub's dark canvas, one hairline, an optional vertical rule."""
    rule = f'<line x1="{split}.5" y1="1" x2="{split}.5" y2="{h - 1}" stroke="{LINE}"/>' if split else ''
    return f'<rect x=".5" y=".5" width="{W - 1}" height="{h - 1}" rx="6" fill="{BG}" stroke="{LINE}"/>{rule}{inner}'


def caps(x, y, s, size=11, anchor='start', cls='m'):
    return text(x, y, s, cls, size, MUTED, anchor, 'letter-spacing="2.2"')


def ascii_block(lines, x, y, size, fill=FG, lh=None, extra=''):
    lh = lh or size * 1.2
    rows = ''.join(f'<text x="{x:.1f}" y="{y + i * lh:.1f}" xml:space="preserve">{escape(s)}</text>'
                   for i, s in enumerate(lines) if s.strip())
    return f'<g class="m" font-size="{size}" fill="{fill}" {extra}>{rows}</g>'


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
    if 5 <= h < 12:
        return 'Good morning'
    if 12 <= h < 17:
        return 'Good afternoon'
    return 'Bonsoir' if 17 <= h < 22 else 'Bonne nuit'


def uptime(created, now):
    months = (now.year - created.year) * 12 + now.month - created.month - (now.day < created.day)
    return f'{months // 12} yrs, {months % 12} mos'


# ---------------------------------------------------------------- cards

def hero(d, now):
    h, split = 380, 470
    body = []
    # the eye: ASCII, blinking, with a star glint in the pupil
    lines, (pc, pr) = art.eye(68, 19)
    fs, lh = 9.4, 9.4 * 1.15
    cw = fs * .6
    cx, cy = split / 2, h / 2
    ex, ey = cx - pc * cw, cy - pr * lh + fs * 1.05  # text sits on baselines; nudge so cell centres line up
    body.append(f'<g transform="translate(0 {cy:.1f})"><g>'
                f'<animateTransform attributeName="transform" type="scale" values="1 1;1 1;1 .06;1 1" '
                f'keyTimes="0;.955;.975;1" dur="7s" repeatCount="indefinite"/>'
                f'<g transform="translate(0 {-cy:.1f})">' + ascii_block(lines, ex, ey, fs, FG, lh, 'opacity=".9"')
                + star(round(cx), round(cy), 8, FG, 2.0) + '</g></g></g>')

    tx = split + 56
    body.append(caps(tx, 96, 'LAHORE · 31.52°N 74.36°E'))
    body.append(text(tx - 2, 154, 'Ameer Hussain', size=46, extra='letter-spacing="-1.5"'))
    body.append(text(tx, 194, 'AI & Full-Stack Engineer', size=17))
    body.append(f'<line x1="{tx}" y1="218.5" x2="{tx + 28}" y2="218.5" stroke="{MUTED}"/>')
    for i, s in enumerate(('RAG · LangGraph · Agent Systems', 'Web, desktop, Android & iOS apps',
                           'I automate the boring stuff in businesses.')):
        body.append(text(tx, 248 + i * 24, s, size=13.5, fill=SOFT))
    return svg(h, panel(h, ''.join(body), split), 'Ameer Hussain. AI and full-stack engineer in Lahore.', 'M')


def terminal(d, now):
    h = 536
    wx, wy, ww, wh = 40, 28, 920, 476
    body = [f'<clipPath id="tcard"><rect width="{W}" height="{h}" rx="6"/></clipPath><g clip-path="url(#tcard)">',
            wallpaper('t', W, h), '</g>', window('t', wx, wy, ww, wh, 'ameer@envyxyz: ~ · zsh', W, h)]
    body.append(ascii_block(art.rose(40, 24), wx + 50, wy + 106, 11.4, SOFT, 13.1))
    py = wy + wh - 22
    body.append(text(wx + 26, py, 'ameer@envyxyz ~ %', size=12.5, fill=MUTED))
    body.append(f'<rect x="{wx + 26 + 18 * 7.5:.1f}" y="{py - 11}" width="7.5" height="14" fill="{FG}" class="blink"/>')

    ix, iy, bw = wx + 380, wy + 74, 500
    body.append(text(ix, iy, greeting(now) + ', Ameer.', size=13.5, fill=FG))
    total = sum(d['langs'].values()) or 1
    langs = sorted(d['langs'].items(), key=lambda kv: -kv[1])[:4]
    groups = [
        ('Profile', [('ROLE', 'AI & Full-Stack Engineer'), ('BASE', 'Lahore, Pakistan'),
                     ('STACK', 'React · Tailwind · TypeScript'), ('', 'C++ · .NET · Python · Java'),
                     ('FOCUS', 'RAG · LangGraph · Agent Systems'),
                     ('BUILDS', 'Web · Electron desktop · Android & iOS'),
                     ('NOW', 'OpenHelios · a personal harness, stripped and fast')]),
        ('System', [('REPOS', f"{d['repos']} public · {d['stars']} stars"), ('LANGS', None),
                    ('UPTIME', uptime(d['created'], now) + ' on GitHub'),
                    ('SYNCED', now.strftime('%a %d %b %Y, %H:%M') + ' PKT')]),
    ]
    y = iy + 30
    for name, rows in groups:
        gh = 24 + len(rows) * 22
        tw = len(name) * 7.2 + 18
        body.append(f'<path d="M{ix + (bw - tw) / 2:.1f},{y} H{ix} V{y + gh} H{ix + bw} V{y} H{ix + (bw + tw) / 2:.1f}" '
                    f'fill="none" stroke="{FG}" stroke-opacity=".22"/>')
        body.append(text(ix + bw / 2, y + 4, name, size=12, fill=SOFT, anchor='middle'))
        for i, (k, v) in enumerate(rows):
            ry = y + 30 + i * 22
            body.append(text(ix + 22, ry, k, size=12, fill=MUTED))
            if v is not None:
                body.append(text(ix + 96, ry, v, size=12.5, fill=FG))
                continue
            bx, bwid, acc, lx = ix + 96, 150, 0, ix + 96 + 150 + 16
            for j, ((lang, size), op) in enumerate(zip(langs, (1, .6, .35, .18))):
                part = bwid * size / total
                body.append(f'<rect x="{bx + acc:.1f}" y="{ry - 9}" width="{max(part - 1.5, 1):.1f}" height="8" fill="{FG}" opacity="{op}"/>')
                acc += part
                if j < 3:
                    label = {'JavaScript': 'JS', 'TypeScript': 'TS'}.get(lang, lang) + f' {round(100 * size / total)}%'
                    body.append(f'<rect x="{lx}" y="{ry - 8}" width="6" height="6" fill="{FG}" opacity="{op}"/>'
                                + text(lx + 10, ry, label, size=11, fill=MUTED))
                    lx += 10 + len(label) * 6.6 + 14
        y += gh + 24
    return svg(h, ''.join(body), 'Terminal card: profile and live GitHub stats', 'M')


def ledger(d, now):
    h = 300
    days = [x for w in d['weeks'] for x in w]
    cur, best = streaks(days)
    peak = max(days, key=lambda x: x[1])
    peak_day = dt.date.fromisoformat(peak[0])
    cell, gap = 12, 3.2
    step = cell + gap
    weeks = d['weeks']
    gx = (W - len(weeks) * step + gap) / 2
    gy, right = 132, (W + len(weeks) * step - gap) / 2
    body = [text(gx - 1, 62, f"{d['total']:,}", size=32, extra='letter-spacing="-1"'), caps(gx, 86, 'CONTRIBUTIONS, LAST TWELVE MONTHS')]
    stats = [('STREAK', f'{cur} day' + ('s' if cur != 1 else '') if cur else 'resting'), ('BEST', f'{best} days'),
             ('PEAK', f"{peak[1]} on {peak_day.day} {peak_day.strftime('%b')}")]
    x = right
    for k, v in reversed(stats):
        body.append(text(x, 60, v, size=16, anchor='end'))
        body.append(caps(x + 2.2, 86, k, anchor='end'))
        x -= max(len(v) * 9.6 + 44, 110)

    alpha = [.07, .28, .5, .75, 1]
    month, target = None, (gx, gy)
    for c, week in enumerate(weeks):
        for date, n, lvl in week:
            day = dt.date.fromisoformat(date)
            r = (day.weekday() + 1) % 7
            x, y = gx + c * step, gy + r * step
            body.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{cell}" height="{cell}" rx="2" fill="{FG}" opacity="{alpha[lvl]}"/>')
            if date == peak[0]:
                target = (x + cell / 2, y + cell / 2)
            if r == 0 and day.month != month and c < len(weeks) - 2:
                month = day.month
                body.append(text(x, gy - 10, day.strftime('%b'), size=10.5, fill=MUTED))
    tx, ty = target  # crosshair on the busiest day
    body.append(f'<g transform="translate({tx:.1f} {ty:.1f})" fill="none" stroke="{FG}" stroke-width="1.2">'
                f'<circle r="10.5"/><path d="M-18,0h8M10,0h8M0,-18v8M0,10v8"/></g>')
    ly = gy + 7 * step + 22
    lx = right - 5 * step + gap - 40
    body.append(text(lx - 8, ly, 'Less', size=11, fill=MUTED, anchor='end'))
    body.append(''.join(f'<rect x="{lx + i * step:.1f}" y="{ly - 10}" width="{cell}" height="{cell}" rx="2" '
                        f'fill="{FG}" opacity="{a}"/>' for i, a in enumerate(alpha)))
    body.append(text(right, ly, 'More', size=11, fill=MUTED, anchor='end'))
    return svg(h, panel(h, ''.join(body)), f"{d['total']} contributions in the last year", 'M')


def footer():
    h = 170
    body = [text(W / 2, 92, 'Festina lente.', 'si', 40, FG, anchor='middle'),
            caps(W / 2, 122, 'X.COM/ENVYXYZ7', 13, 'middle', 's')]
    sx = 880
    body.append(f'<g><animateTransform attributeName="transform" type="rotate" values="-4 {sx} 0;4 {sx} 0;-4 {sx} 0" '
                f'dur="7s" calcMode="spline" keyTimes="0;.5;1" keySplines=".45 0 .55 1;.45 0 .55 1" repeatCount="indefinite"/>'
                f'<line x1="{sx}" y1="1" x2="{sx}" y2="58" stroke="{MUTED}"/>'
                + ascii_block(art.SPIDER, sx - 8.5 * 6.6, 66, 11, SOFT, 13) + '</g>')
    return svg(h, panel(h, ''.join(body)), 'Festina lente. x.com/envyxyz7', 'SI', 'S', 'M')


# ---------------------------------------------------------------- main

def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'dist')
    os.makedirs(out, exist_ok=True)
    d, now = fetch(), dt.datetime.now(PKT)
    cards = {'hero': hero(d, now), 'terminal': terminal(d, now), 'ledger': ledger(d, now), 'footer': footer()}
    for name, s in cards.items():
        xml.dom.minidom.parseString(s)  # fail the run rather than publish a broken image
        with open(os.path.join(out, name + '.svg'), 'w', encoding='utf-8') as f:
            f.write(s)
        print(f'{name}.svg  {len(s) // 1024} KB')


if __name__ == '__main__':
    assert [greeting(dt.datetime(2026, 1, 1, h)) for h in (2, 6, 13, 19, 23)] == \
        ['Bonne nuit', 'Good morning', 'Good afternoon', 'Bonsoir', 'Bonne nuit']
    main()
