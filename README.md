# SAPIO MORPHEUS Black-Box Challenge

This one-core experiment measures the weighted Max-Cut achieved within 24 seconds. It uses a fixed panel of 20 graphs and three runs for each graph and method.

**Result** The verifier confirmed 300 of 300 scheduled partitions. Against the best observed public result in each seed block, the graph-level medians gave 5 wins, 7 ties and 8 losses over 20 fully paired graphs (one-sided sign-test p = 0.86658). The prespecified criterion for superiority on the fixed panel was not met.

| Comparator | Graph wins / ties / losses | Median margin (weight units) | Mean normalized margin (pp) |
|---|---:|---:|---:|
| BURER2002 | 9 / 3 / 8 | +0.0 | +0.0540 |
| PALUBECKIS2004bMST2 | 15 / 5 / 0 | +8.0 | +0.1878 |
| MQLib restart portfolio | 7 / 10 / 3 | +0.0 | +0.0616 |
| D-Wave CPU TabuSampler | 15 / 5 / 0 | +21.5 | +0.8607 |
| Per-seed public envelope | 5 / 7 / 8 | +0.0 | +0.0478 |

The last row compares against the maximum of four separately run references. Margins are computed from the median of three paired seed differences per graph. The independent verifier uses the signed integer edge weights to recalculate every published cut.

```text
python -B verify.py
python -B analyze.py
```

- [Preprint](https://github.com/kosza123/SAPIO-MORPHEUS-BLACKBOX-CHALLENGE/releases/tag/v1.0.0)
- [Protocol commit made before measurement](https://github.com/kosza123/SAPIO-MORPHEUS-BLACKBOX-CHALLENGE/commit/11fd536d75de096a872e9ba4f8599cfd6db688e9)
- [Complete results, including losses and ties](results.csv)
- [Analysis](RESULTS.json), [reproduction instructions](REPRODUCIBILITY.md) and [limitations](LIMITATIONS.md)
- [Data and code attribution](THIRD_PARTY.md)
