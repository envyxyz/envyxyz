"""python scripts/test_play.py: the chess rules path, end to end through play() and block()."""
import play

s = {'fen': play.chess.STARTING_FEN, 'moves': [], 'players': [], 'finished': 0, 'result': None}
assert play.play(s, 'e2e5', 'a').endswith('Fresh moves are on the profile.') and not s['moves']
assert play.play(s, 'new', 'a').startswith('This game is still going')
for uci, who in (('f2f3', 'a'), ('e7e5', 'b'), ('g2g4', 'a'), ('d8h4', 'c')):  # fool's mate
    assert play.play(s, uci, who).startswith('Played')
assert s['result'] == 'Checkmate, black wins.' and s['finished'] == 1 and s['players'] == ['a', 'b', 'c']
assert 'Set up a new board' in play.block(s) and 'chess%7Cnew' in play.block(s)
assert play.play(s, 'e2e4', 'd').startswith('This game has ended')
assert play.play(s, 'new', 'd').startswith('A fresh board') and not s['moves']
assert 'chess%7Ce2e4' in play.block(s) and '[Nf3]' in play.block(s)
assert play.TITLE.fullmatch('chess|e7e8q') and not play.TITLE.fullmatch('chess|e2e4; rm -rf /')
print('ok')
