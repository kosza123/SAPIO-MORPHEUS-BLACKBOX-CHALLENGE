"""Recalculate all paired margins from the verified published trial table."""

from collections import defaultdict
import csv
import json
import math
from pathlib import Path
from statistics import mean, median

from verify import audit


def summary(margins, weights):
    normalized = [100.0 * value / weights[graph] for graph, value in margins.items()]
    wins = sum(value > 0 for value in margins.values())
    ties = sum(value == 0 for value in margins.values())
    losses = sum(value < 0 for value in margins.values())
    nonzero = wins + losses
    p = sum(math.comb(nonzero, i) for i in range(wins, nonzero + 1)) / (2 ** nonzero)
    return {"graphs": len(margins), "wins": wins, "ties": ties, "losses": losses,
            "median_cut_margin": median(margins.values()) if margins else None,
            "median_normalized_pp": median(normalized) if normalized else None,
            "mean_normalized_pp": mean(normalized) if normalized else None,
            "sign_test_one_sided": p}


def evaluate(root):
    checks = audit(root)
    spec = json.loads((root / "FREEZE.json").read_bytes())
    graphs = {row["id"]: row for row in spec["graphs"]}
    methods = spec["methods"]
    observations = defaultdict(dict)
    costs = defaultdict(list)
    with (root / "results.csv").open(encoding="utf8", newline="") as handle:
        for row in csv.DictReader(handle):
            if row["status"] == "valid":
                observations[row["graph"], int(row["seed"])][row["method"]] = int(row["cut"])
            if row["wall_ns"]:
                costs[row["method"]].append(row)
    weights = {gid: graph["absolute_weight"] for gid, graph in graphs.items()}
    margins = {}
    for other in [*methods[1:], "Best public reference"]:
        differences = defaultdict(list)
        for (graph, _), values in observations.items():
            if methods[0] not in values:
                continue
            if other in values:
                reference = values[other]
            elif other == "Best public reference" and all(m in values for m in methods[1:]):
                reference = max(values[m] for m in methods[1:])
            else:
                continue
            differences[graph].append(values[methods[0]] - reference)
        observed = {graph: median(values) for graph, values in differences.items() if len(values) == 3}
        groups = {family: summary({graph: value for graph, value in observed.items()
                                   if graphs[graph]["family"] == family}, weights)
                  for family in sorted({g["family"] for g in graphs.values()})}
        margins[other] = {"total": summary(observed, weights), "family": groups,
                          "graph_margins": observed, "complete_paired_blocks": sum(map(len, differences.values()))}
    primary = margins["Best public reference"]["total"]
    success = (checks["missing_or_invalid"] == 0 and primary["median_cut_margin"] > 0
               and primary["sign_test_one_sided"] <= 0.05)
    resources = {
        method: {
            "total_cpu_s": sum(float(r["cpu_user_s"]) + float(r["cpu_system_s"]) for r in rows),
            "median_wall_s": median(int(r["wall_ns"]) for r in rows) / 1e9,
            "median_sampled_rss_kib": median(int(r["sampled_rss_kib"]) for r in rows),
            "max_sampled_rss_kib": max(int(r["sampled_rss_kib"]) for r in rows),
            "deadline_count": sum(r["end_reason"] == "deadline" for r in rows),
            "observed_runs": len(rows),
        } for method, rows in costs.items()
    }
    return {"audit": checks, "primary_success": success, "comparisons": margins,
            "resources": resources}


if __name__ == "__main__":
    path = Path(__file__).resolve().parent
    print(json.dumps(evaluate(path), indent=2, sort_keys=True))
