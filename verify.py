"""Independently check the complete result table against the frozen panel."""

import argparse
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import re


INTEGER = re.compile(r"-?[0-9]+")
METHODS = ["Morpheus", "MQLib-Burer", "MQLib-Pal", "MQLib-Restarts", "DWave-Tabu"]


def fields(line, length):
    parts = line.split()
    if len(parts) != length or any(not INTEGER.fullmatch(p) for p in parts):
        raise ValueError(f"Malformed integer row {line!r}")
    return tuple(map(int, parts))


def graph_data(path):
    data = path.read_bytes()
    rows = [x for x in data.decode("ascii").splitlines() if x.strip()]
    n, m = fields(rows[0], 2)
    if n < 2 or m <= 0 or len(rows) != m + 1:
        raise ValueError(f"Incorrect graph size in {path.name}")
    seen = set()
    edges = []
    for row in rows[1:]:
        u, v, w = fields(row, 3)
        edge = min(u, v), max(u, v)
        if not 1 <= edge[0] < edge[1] <= n or edge in seen:
            raise ValueError(f"Invalid or duplicate edge in {path.name}: {row!r}")
        seen.add(edge)
        edges.append((u - 1, v - 1, w))
    return n, edges, hashlib.sha256(data).hexdigest()


def score(n, edges, bits):
    if len(bits) != n or re.fullmatch(r"[01]+", bits) is None:
        raise ValueError("Expected one bit per vertex")
    return sum(w for u, v, w in edges if bits[u] != bits[v])


def safe_file(root, label):
    path = (root / label).resolve()
    path.relative_to(root)
    if not path.is_file():
        raise ValueError(f"Missing {label}")
    return path


def audit(root):
    spec = json.loads((root / "FREEZE.json").read_bytes())
    if spec["methods"] != METHODS or spec["budget_ns"] != 24_000_000_000 or spec["threads_per_trial"] != 1:
        raise ValueError("Unexpected methods or budget")
    support = {"PROTOCOL.md": spec["protocol_sha256"], **spec["support_sha256"]}
    for path, checksum in support.items():
        if hashlib.sha256(safe_file(root, path).read_bytes()).hexdigest() != checksum:
            raise ValueError(f"Frozen support file changed: {path}")
    graphs = {}
    hashes = set()
    for row in spec["graphs"]:
        n, edges, digest = graph_data(safe_file(root, f"benchmark/{row['name']}"))
        if (n, len(edges), digest, sum(abs(w) for _, _, w in edges)) != (
            row["vertices"], row["edges"], row["sha256"], row["absolute_weight"]
        ) or digest in hashes or row["id"] in graphs:
            raise ValueError(f"Graph metadata mismatch or duplicate: {row['id']}")
        graphs[row["id"]] = n, edges, digest, row["family"]
        hashes.add(digest)
    if Counter(g[3] for g in graphs.values()) != {"torus": 5, "uniform": 5, "modular": 5, "bqp500": 5}:
        raise ValueError("The frozen panel must contain 5 graphs in each of the 4 families")
    expected = {}
    blocks = Counter()
    for b in spec["blocks"]:
        if sorted(b["order"]) != sorted(METHODS) or b["cpu"] not in spec["cpus"]:
            raise ValueError("Wrong block methods or CPU lane")
        if b["graph"] not in graphs or not 0 <= b["seed"] <= 65535 - 16:
            raise ValueError("Unexpected graph or seed in block")
        blocks[b["graph"]] += 1
        for method in b["order"]:
            key = b["graph"], b["seed"], method
            if key in expected:
                raise ValueError("Duplicate scheduled trial")
            expected[key] = b["cpu"]
    if set(blocks) != set(graphs) or set(blocks.values()) != {3} or len(expected) != 300:
        raise ValueError("The schedule must contain 3 separate blocks for each graph and 300 trials")
    used = set()
    scores = 0
    missing = 0
    with (root / "results.csv").open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            key = row["graph"], int(row["seed"]), row["method"]
            if key not in expected or key in used:
                raise ValueError(f"Unscheduled or duplicate row: {key}")
            used.add(key)
            n, edges, digest, family = graphs[key[0]]
            if (row["graph_sha256"], row["family"], int(row["cpu"])) != (digest, family, expected[key]):
                raise ValueError(f"Wrong graph hash, family or CPU for {key}")
            if row["status"] != "valid":
                if row["status"] not in ("no_partition", "invalid", "interrupted"):
                    raise ValueError(f"Unrecognized status for {key}")
                if any(row[name] for name in ("cut", "solution", "solution_sha256", "candidate_ns")):
                    raise ValueError(f"Unexpected score or file on failed row: {key}")
                missing += 1
                continue
            data = safe_file(root, row["solution"]).read_bytes()
            if hashlib.sha256(data).hexdigest() != row["solution_sha256"]:
                raise ValueError(f"Solution hash mismatch: {key}")
            if not 0 < int(row["candidate_ns"]) <= spec["budget_ns"]:
                raise ValueError(f"Partition arrived outside the fixed budget: {key}")
            if score(n, edges, data.decode("ascii").rstrip("\n")) != int(row["cut"]):
                raise ValueError(f"Cut mismatch: {key}")
            scores += 1
    if used != set(expected):
        raise ValueError(f"Missing {len(set(expected) - used)} scheduled rows")
    return {"graphs": len(graphs), "scheduled": len(expected), "verified_partitions": scores,
            "missing_or_invalid": missing}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    print(json.dumps(audit(args.root.resolve()), sort_keys=True))


if __name__ == "__main__":
    main()
