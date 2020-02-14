import hashlib

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
