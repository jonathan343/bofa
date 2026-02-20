from __future__ import annotations

import math
import random
import shutil

from bofa import BOFA

CHAR_ASPECT = 2.0
CRATERS = ("()", "o", ".", "o", ".", "()")


def _render_moon() -> str:
    cols, rows = shutil.get_terminal_size(fallback=(80, 24))
    R = min(rows // 2 - 1, 10)
    W = int(R * CHAR_ASPECT)
    if W * 2 + 1 > cols:
        W = (cols - 1) // 2
        R = int(W / CHAR_ASPECT)

    payload = BOFA.decode("utf-8")
    rng = random.Random(42)
    lines: list[str] = []

    for y in range(-R, R + 1):
        row = list(" " * (W * 2 + 1))
        for x in range(-W, W + 1):
            dist = math.sqrt((x / CHAR_ASPECT) ** 2 + y ** 2)
            cx = x + W
            if abs(dist - R) < 0.5:
                row[cx] = "#"

        # fill craters inside the circle
        if y == 0:
            # place payload centered
            start = W - len(payload) // 2
            for j, ch in enumerate(payload):
                row[start + j] = ch
        else:
            # scatter craters inside
            inner_positions = [
                x + W
                for x in range(-W, W + 1)
                if math.sqrt((x / CHAR_ASPECT) ** 2 + y ** 2) < R - 0.5
                and row[x + W] == " "
            ]
            if inner_positions:
                for _ in range(max(1, len(inner_positions) // 12)):
                    c = rng.choice(CRATERS)
                    pos = rng.choice(inner_positions)
                    for j, ch in enumerate(c):
                        if pos + j < len(row) and row[pos + j] == " ":
                            row[pos + j] = ch

        lines.append("".join(row).rstrip())

    return "\n".join(lines)


def play_moon() -> None:
    print(_render_moon())
