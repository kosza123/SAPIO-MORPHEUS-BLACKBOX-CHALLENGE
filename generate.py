"""Recreate the three generated graph families."""

from pathlib import Path
import random

SEEDS = (2326011, 2326037, 2326103, 2326179, 2326227)
SIZES = (1024, 1156, 1296, 1444, 1600)


def ordered(u, v):
    return min(u, v), max(u, v)


def torus(side):
    edges = set()
    for row in range(side):
        for col in range(side):
            u = row * side + col
            edges.add(ordered(u, row * side + (col + 1) % side))
            edges.add(ordered(u, ((row + 1) % side) * side + col))
    return edges


def random_sparse(n, rng):
    edges = {ordered(u, (u + 1) % n) for u in range(n)}
    while len(edges) < 4 * n:
        u, v = rng.sample(range(n), 2)
        edges.add(ordered(u, v))
    return edges


def modular(n, rng):
    groups = [range(i * n // 8, (i + 1) * n // 8) for i in range(8)]
    edges = set()
    for group in groups:
        inside = set()
        while len(inside) < 4 * len(group):
            u, v = rng.sample(group, 2)
            inside.add(ordered(u, v))
        edges.update(inside)
    while len(edges) < 9 * n // 2:
        a, b = rng.sample(groups, 2)
        edges.add(ordered(rng.choice(a), rng.choice(b)))
    return edges


def graphs():
    for index, (seed, n) in enumerate(zip(SEEDS, SIZES), 1):
        for family in ("torus", "uniform", "modular"):
            rng = random.Random(f"{family}/{seed}")
            if family == "torus":
                edges = torus((30 + 2 * index))
            elif family == "uniform":
                edges = random_sparse(n, rng)
            else:
                edges = modular(n, rng)
            weights = (1, 2, 3, 4, 5) if family == "modular" else (-1, 1)
            edge_lines = [f"{u+1} {v+1} {rng.choice(weights)}\n" for u, v in sorted(edges)]
            yield f"{family}-{index:02d}.mc", f"{n} {len(edges)}\n" + "".join(edge_lines)


if __name__ == "__main__":
    target = Path(__file__).resolve().parent / "benchmark"
    target.mkdir(exist_ok=True)
    for name, graph in graphs():
        path = target / name
        encoded = graph.encode("ascii")
        if path.exists() and path.read_bytes() != encoded:
            raise SystemExit(f"Refusing to overwrite different graph: {name}")
        path.write_bytes(encoded)
