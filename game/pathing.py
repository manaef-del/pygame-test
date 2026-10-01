"""Wegefeld: jeder Mann sucht sich seinen Weg zu seinem Platz selbst.

Die Karte wird in kleine Zellen geteilt (``config.FIELD_CELL`` Kacheln).
Von den Plätzen der Zielaufstellung aus rechnet ein Dijkstra für jede
Zelle die Weglänge dorthin; Palisade, geschlossenes Tor, stehende eigene
Gruppen und feindliche Formationen sind Hindernisse. Ein Mann, der seinen
Platz nicht geradeaus erreicht, geht bergab im Feld, und zwar gleich so
weit, wie er von seiner Stelle aus frei sieht. Auf- und Abstiege am Wall
(Leiter, Turm) gehören nicht hierher, die regelt ``Battle.route_from``.
"""

from __future__ import annotations

import heapq
import math
from typing import Callable, Iterable

Point = tuple[float, float]

_STEPS = ((1, 0, 1.0), (-1, 0, 1.0), (0, 1, 1.0), (0, -1, 1.0),
          (1, 1, math.sqrt(2)), (1, -1, math.sqrt(2)), (-1, 1, math.sqrt(2)), (-1, -1, math.sqrt(2)))


class Field:
    """Weglängen (in Zellen) von jeder Zelle zur nächsten Zielzelle."""

    def __init__(self, cols: float, rows: float, cell: float, blocked: bytearray,
                 goals: Iterable[Point], needed: Iterable[Point] = (), slack: float = 12.0) -> None:
        """``needed``: die Stellen, für die der Weg gebraucht wird (die Männer). Sind sie
        alle erreicht, rechnet das Feld nur noch ``slack`` Zellen weiter und hört auf."""
        self.cell = cell
        self.nx = int(math.ceil(cols / cell))
        self.ny = int(math.ceil(rows / cell))
        self.blocked = blocked
        n = self.nx * self.ny
        inf = math.inf
        self.dist = [inf] * n
        heap: list[tuple[float, int]] = []
        for p in goals:
            i = self.index(p)
            if i is not None and not blocked[i] and self.dist[i] > 0.0:
                self.dist[i] = 0.0
                heap.append((0.0, i))
        heapq.heapify(heap)
        nx, ny, dist_ = self.nx, self.ny, self.dist
        # wer gebraucht wird: seine Zelle, oder wenn sie zu ist, die freien Nachbarn
        wanted: dict[int, list[int]] = {}
        open_ = 0
        for k, p in enumerate(needed):
            i = self.index(p)
            if i is None:
                continue
            cells = [i] if not blocked[i] else [j for j in self._neighbours(i) if not blocked[j]]
            if not cells:
                continue
            open_ += 1
            for j in cells:
                wanted.setdefault(j, []).append(k)
        done: set[int] = set()
        limit = inf
        while heap:
            d, i = heapq.heappop(heap)
            if d > dist_[i]:
                continue
            if d > limit:
                break
            if open_ and i in wanted:
                for k in wanted.pop(i):
                    if k not in done:
                        done.add(k)
                        open_ -= 1
                if open_ == 0:
                    limit = d + slack
            x, y = i % nx, i // nx
            for dx, dy, c in _STEPS:
                x2, y2 = x + dx, y + dy
                if not (0 <= x2 < nx and 0 <= y2 < ny):
                    continue
                j = y2 * nx + x2
                if blocked[j]:
                    continue
                if dx and dy and (blocked[y * nx + x2] or blocked[y2 * nx + x]):
                    continue                      # nicht über die Ecke eines Hindernisses
                nd = d + c
                if nd < dist_[j]:
                    dist_[j] = nd
                    heapq.heappush(heap, (nd, j))

    # ------------------------------------------------------------ Zellen
    def index(self, p: Point) -> int | None:
        x, y = int(p[0] / self.cell), int(p[1] / self.cell)
        if 0 <= x < self.nx and 0 <= y < self.ny:
            return y * self.nx + x
        return None

    def centre(self, i: int) -> Point:
        return ((i % self.nx + 0.5) * self.cell, (i // self.nx + 0.5) * self.cell)

    def free(self, p: Point) -> bool:
        i = self.index(p)
        return i is not None and not self.blocked[i]

    def clear(self, a: Point, b: Point) -> bool:
        """Geht es von ``a`` geradeaus nach ``b``, ohne ein Hindernis zu berühren?
        Die Zellen an beiden Enden zählen nicht (man steht vielleicht schon dicht daran)."""
        d = math.hypot(b[0] - a[0], b[1] - a[1])
        n = max(1, int(d / (self.cell * 0.5)))
        ia, ib = self.index(a), self.index(b)
        for k in range(1, n):
            t = k / n
            i = self.index((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
            if i is None:
                return False
            if i != ia and i != ib and self.blocked[i]:
                return False
        return True

    def reachable(self, p: Point) -> bool:
        i = self.index(p)
        return i is not None and self.dist[i] < math.inf

    def near_reachable(self, p: Point) -> bool:
        """Erreichbar von hier oder einer Nachbarzelle (wer dicht an einem Hindernis steht)."""
        i = self.index(p)
        if i is None:
            return False
        if self.dist[i] < math.inf:
            return True
        x, y = i % self.nx, i // self.nx
        for dx, dy, _ in _STEPS:
            x2, y2 = x + dx, y + dy
            if 0 <= x2 < self.nx and 0 <= y2 < self.ny and self.dist[y2 * self.nx + x2] < math.inf:
                return True
        return False

    def waypoint(self, pos: Point, goal: Point, look: int = 10) -> Point:
        """Nächster Punkt auf dem Weg von ``pos`` zu ``goal``: das Ziel selbst, wenn
        es frei zu sehen ist, sonst die fernste frei sichtbare Zelle bergab."""
        if self.clear(pos, goal):
            return goal
        i = self.index(pos)
        if i is None:
            return goal
        if self.blocked[i] or self.dist[i] == math.inf:
            # dicht an einem Hindernis (oder darin): in die beste freie Nachbarzelle
            j = self._best_neighbour(i, any_lower=False)
            return self.centre(j) if j is not None else goal
        chain = [i]
        for _ in range(look):
            j = self._best_neighbour(chain[-1], any_lower=True)
            if j is None:
                break
            chain.append(j)
            if self.dist[j] == 0.0:
                break
        if self.dist[chain[-1]] == 0.0 and self.clear(pos, goal):
            return goal
        for j in reversed(chain[1:]):
            c = self.centre(j)
            if self.clear(pos, c):
                return c
        return self.centre(chain[1]) if len(chain) > 1 else goal

    def _neighbours(self, i: int) -> list[int]:
        x, y = i % self.nx, i // self.nx
        return [(y + dy) * self.nx + x + dx for dx, dy, _ in _STEPS
                if 0 <= x + dx < self.nx and 0 <= y + dy < self.ny]

    def _best_neighbour(self, i: int, any_lower: bool) -> int | None:
        nx, ny = self.nx, self.ny
        x, y = i % nx, i // nx
        best, best_d = None, self.dist[i] if any_lower else math.inf
        for dx, dy, _ in _STEPS:
            x2, y2 = x + dx, y + dy
            if not (0 <= x2 < nx and 0 <= y2 < ny):
                continue
            j = y2 * nx + x2
            if self.blocked[j]:
                continue
            if self.dist[j] < best_d:
                best, best_d = j, self.dist[j]
        return best


def grid(cols: float, rows: float, cell: float, is_blocked: Callable[[float, float], bool]) -> bytearray:
    """Feste Hindernisse (Palisade, geschlossenes Tor) als Zellraster."""
    nx, ny = int(math.ceil(cols / cell)), int(math.ceil(rows / cell))
    out = bytearray(nx * ny)
    for y in range(ny):
        for x in range(nx):
            if is_blocked((x + 0.5) * cell, (y + 0.5) * cell):
                out[y * nx + x] = 1
    return out


def mark(blocked: bytearray, cols: float, rows: float, cell: float, centre: Point, reach: float,
         inside: Callable[[Point], bool]) -> None:
    """Zellen um ``centre`` (bis ``reach``), für die ``inside`` gilt, als Hindernis markieren."""
    nx, ny = int(math.ceil(cols / cell)), int(math.ceil(rows / cell))
    x0, x1 = max(0, int((centre[0] - reach) / cell)), min(nx - 1, int((centre[0] + reach) / cell))
    y0, y1 = max(0, int((centre[1] - reach) / cell)), min(ny - 1, int((centre[1] + reach) / cell))
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if inside(((x + 0.5) * cell, (y + 0.5) * cell)):
                blocked[y * nx + x] = 1
