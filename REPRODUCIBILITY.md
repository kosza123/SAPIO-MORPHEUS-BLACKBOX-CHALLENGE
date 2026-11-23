# Reproduce the verification

Run the following commands from this directory with Python 3.10 or newer. The public verification and analysis use only the standard library.

```text
python -B verify.py
python -B analyze.py
```

The checker validates the 20 graphs, all 300 scheduled trial identities, graph and solution SHA-256, all returned partition lengths and weighted cuts, and each eligible candidate's recorded receive timestamp. It treats weights as signed integers. The analysis recalculates graph-level paired medians, the sign-test tail, family results and resource summaries. Expected output is in [RESULTS.json](RESULTS.json).

Each `benchmark/*.mc` file has header `vertices edges` followed by the two 1-based endpoints and signed integer weight of each undirected edge. Use `generate.py` with CPython 3.12 to regenerate the 15 newly generated files. The five external BQP inputs are identified by exact file path and hash in [benchmark/UPSTREAM.json](benchmark/UPSTREAM.json).

Each `solutions/*.txt` file holds one bit for each vertex in that order. The CSV contains one row per method, graph and seed with CPU ID, CPU seconds, wall nanoseconds, sampled RSS in KiB, process status and both SHA-256 values. `candidate_ns` measures the elapsed time when the full winning partition was received. A deadline kill with an eligible partition is a valid row.

## Public references

MQLib source commit `585496274af5abb0849d0d47e135496b4688680b` is pinned. Run `make CXX=g++-13` in that checkout and link the public adapter with `g++-13 -O2 -std=c++17 -Iinclude /path/to/mqlib_output.cpp bin/MQLib.a -o mqlib_output`. The source defines its four-argument interface. The `PORTFOLIO` label selects alternating BURER2002 and FESTA2002GVNSPR calls. The measured external supervisor started the executable with 23.965 as its internal seconds argument and stopped the group at 24 seconds from dispatch. The benchmark advances by the explicit order and CPU in `FREEZE.json`.

The CPU TabuSampler used Python 3.12 with dwave-samplers 1.8.0, dimod 0.12.22, NumPy 2.5.3 and NetworkX 3.6.1. `tabu_output.py` takes a graph, an absolute monotonic-clock deadline in nanoseconds and a seed. As an illustration, create a fresh subprocess with `time.monotonic_ns() + 24_000_000_000` for the deadline, pin it to one logical CPU and impose the same external deadline. The solver reports each completed half-budget result as a line beginning with `CUT`.

Owing to finite time and OS scheduling, a rerun can produce different partitions. The preserved witnesses are sufficient for exact recalculation of the reported scores. The closed Morpheus implementation is evaluated through its inputs and returned partitions. Pre-registration and archived artifact hashes identify the comparison used here.

Download the preprint and archive from [the publication record](https://github.com/kosza123/SAPIO-MORPHEUS-BLACKBOX-CHALLENGE/releases/tag/v1.0.0).
