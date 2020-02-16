import logging
import hashlib

logger = logging.getLogger('movietv')

class BraceMessage:
    def __init__(self, fmt, *args, **kwargs):
        self.fmt = fmt
        self.args = args
        self.kwargs = kwargs

    def __str__(self):
        return self.fmt.format(*self.args, **self.kwargs)

def hash6(l):
    m = hashlib.sha256()
    for s in l:
        m.update(s.encode())

    return m.hexdigest()[:6]

def flatten2D(ll):
    for r in ll:
        for c in r:
            yield c

def colorMap(l):
    colors = ['xkcd:red', 'xkcd:pink', 'xkcd:blue', 'xkcd:green', 'xkcd:purple',
              'xkcd:brown', 'xkcd:yellow', 'xkcd:orange', 'xkcd:teal', 'xkcd:magenta',
              'xkcd:violet', 'xkcd:cyan', 'xkcd:turquoise', 'xkcd:tan', 'xkcd:aqua',
              'xkcd:maroon', 'xkcd:salmon', 'xkcd:hot pink', 'xkcd:gold', 'xkcd:light orange',
              'xkcd:goldenrod', 'xkcd:seablue', 'xkcd:coral', 'xkcd:azure', 'xkcd:pinkish',
              'xkcd:scarlet', 'xkcd:pumpkin', 'xkcd:tangerine', 'xkcd:orchid', 'xkcd:jade',
              'xkcd:bright yellow', 'xkcd:terra cotta', 'xkcd:lemon', 'xkcd:dusky rose',
              'xkcd:rust orange', 'xkcd:ice', 'xkcd:sand brown', 'xkcd:desert', 'xkcd:dust']

    r = []
    for t in l:
        r.append(colors[int(hash6(t), 16) % len(colors)])

    return r
