"""Widget keys, namespaced by generation id so a new generation gets fresh widgets."""


def cap(gid: int) -> str: return f"cap{gid}"
def tags(gid: int) -> str: return f"tag{gid}"
def variant(gid: int) -> str: return f"var{gid}"
def telegram(gid: int) -> str: return f"tg{gid}"
def whatsapp(gid: int) -> str: return f"wa{gid}"
def slide_h(gid: int, i: int) -> str: return f"h{gid}_{i}"
def slide_b(gid: int, i: int) -> str: return f"b{gid}_{i}"
def slide_s(gid: int, i: int) -> str: return f"s{gid}_{i}"
def instr(gid: int, kind: str, i: int = 0) -> str: return f"ins{gid}_{kind}_{i}"
