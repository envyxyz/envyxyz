#!/usr/bin/env python3
"""Community chess. Plays open issues titled 'chess|e2e4' (or 'chess|new' after a game ends),
closes each with a note, then rewrites the move list between the board markers in README.md.

Issue titles are untrusted: only an exact match of TITLE is ever acted on.
Without GH_TOKEN it just refreshes the README block (local preview).
"""
import json
import os
import re
import subprocess
import urllib.parse

import chess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.environ.get('GITHUB_REPOSITORY', 'envyxyz/envyxyz')
STATE = os.path.join(ROOT, 'game', 'chess.json')
README = os.path.join(ROOT, 'README.md')
TITLE = re.compile(r'chess\|([a-h][1-8][a-h][1-8][qrbn]?|new)')
START, END = '<!-- board:start -->', '<!-- board:end -->'
NAMES = [(chess.PAWN, 'Pawn'), (chess.KNIGHT, 'Knight'), (chess.BISHOP, 'Bishop'),
         (chess.ROOK, 'Rook'), (chess.QUEEN, 'Queen'), (chess.KING, 'King')]


def gh(*args):
    return subprocess.run(['gh', *args, '--repo', REPO], check=True, capture_output=True, text=True).stdout


def load():
    try:
        with open(STATE) as f:
            return json.load(f)
    except FileNotFoundError:
        return {'fen': chess.STARTING_FEN, 'moves': [], 'players': [], 'finished': 0, 'result': None}


def play(state, cmd, user):
    b = chess.Board(state['fen'])
    if cmd == 'new':
        if not b.is_game_over():
            return 'This game is still going. A new board opens when it ends.'
        state.update(fen=chess.STARTING_FEN, moves=[], players=[], result=None)
        return 'A fresh board is set. White to play.'
    if b.is_game_over():
        return 'This game has ended. Set up a new board from the profile.'
    move = chess.Move.from_uci(cmd)
    if move not in b.legal_moves:
        return f'{cmd} is not legal on the current board; someone may have moved first. Fresh moves are on the profile.'
    san = b.san(move)
    b.push(move)
    state['fen'] = b.fen()
    state['moves'].append({'uci': cmd, 'san': san, 'by': user})
    if user not in state['players']:
        state['players'].append(user)
    outcome = b.outcome()
    if outcome:
        state['finished'] += 1
        state['result'] = (f"Checkmate, {'white' if outcome.winner else 'black'} wins." if outcome.winner is not None
                           else 'Drawn, ' + outcome.termination.name.lower().replace('_', ' ') + '.')
    return f'Played {san}. Thank you, @{user}.'


def issue_url(cmd, label):
    q = urllib.parse.urlencode({'title': f'chess|{cmd}',
                                'body': f'Submit this issue to play {label}. The board on the profile updates in about '
                                        'a minute and this issue closes itself.'})
    return f'https://github.com/{REPO}/issues/new?{q}'


def block(state):
    b = chess.Board(state['fen'])
    if b.is_game_over():
        return f'<p align="center"><a href="{issue_url("new", "a new game")}">Set up a new board</a></p>'
    rows = []
    for kind, name in NAMES:
        moves = sorted((b.san(m), m.uci()) for m in b.legal_moves if b.piece_type_at(m.from_square) == kind)
        if moves:
            rows.append(f'**{name}** &ensp; ' + ' &middot; '.join(f'[{san}]({issue_url(uci, san)})' for san, uci in moves))
    turn = 'white' if b.turn else 'black'
    return (f'<details>\n<summary>&nbsp;Choose the next move &nbsp;&middot;&nbsp; {turn} to play</summary>\n<br>\n\n'
            + '\n\n'.join(rows) + '\n\n<sub>Each move opens a prefilled issue. Submit it and the board answers in '
            'about a minute.</sub>\n\n</details>')


def main():
    state = load()
    if os.environ.get('GH_TOKEN'):
        issues = json.loads(gh('issue', 'list', '--state', 'open', '--limit', '100', '--json', 'number,title,author'))
        for issue in sorted(issues, key=lambda i: i['number']):
            m = TITLE.fullmatch(issue['title'].strip().lower())
            if m:
                note = play(state, m[1], issue['author']['login'])
                gh('issue', 'close', str(issue['number']), '--comment', note)
                print(f"#{issue['number']}: {note}")
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    with open(STATE, 'w') as f:
        json.dump(state, f, indent=1)
    with open(README) as f:
        readme = f.read()
    head, rest = readme.split(START, 1)
    tail = rest.split(END, 1)[1]
    with open(README, 'w') as f:
        f.write(f'{head}{START}\n{block(state)}\n{END}{tail}')


if __name__ == '__main__':
    main()
