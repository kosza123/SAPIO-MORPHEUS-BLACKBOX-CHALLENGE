"""Stream weighted Max-Cut candidates from a local D-Wave CPU sampler."""

from pathlib import Path
import sys
import time


def main():
    source, deadline, seed = sys.argv[1:]
    deadline = int(deadline)
    seed = int(seed)
    import dimod
    from dwave.samplers import TabuSampler

    lines = Path(source).read_text(encoding="ascii").splitlines()
    vertices, _ = map(int, lines[0].split())
    edges = [tuple(map(int, line.split())) for line in lines[1:] if line.strip()]
    # E = sum(w*s_i*s_j) = sum(w) - 2*cut.
    model = dimod.BinaryQuadraticModel(
        dict.fromkeys(range(1, vertices + 1), 0),
        {(u, v): w for u, v, w in edges}, 0, dimod.SPIN,
    )
    sampler = TabuSampler()
    start = time.monotonic_ns()
    for part in (1, 2):
        boundary = start + (deadline - start) * part // 2
        duration_ms = (boundary - time.monotonic_ns()) // 1_000_000 - 60
        if duration_ms <= 0:
            break
        result = sampler.sample(model, num_reads=1, timeout=duration_ms, seed=seed + part - 1)
        states = result.first.sample
        value = sum(w for u, v, w in edges if states[u] != states[v])
        bits = "".join("1" if states[i] == 1 else "0" for i in range(1, vertices + 1))
        print(f"CUT {value} {bits}", flush=True)


if __name__ == "__main__":
    main()
