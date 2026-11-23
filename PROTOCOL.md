# SAPIO MORPHEUS Max-Cut challenge protocol

## Question

Does the fixed Morpheus implementation deliver a better weighted cut than the public references within 24 seconds on one CPU core? We assess a fixed panel of 20 graphs, with three independently seeded runs for each graph and method. Each method returns a full binary partition. Scores are sums of weights across that partition, with higher values preferred. Negative integer weights retain their sign.

## Inputs and methods

The panel has five signed square tori, five signed uniform sparse graphs, five positive modular graphs, and five independently sourced weighted BQP conversions. Use the first five numbered bqp500 instances in the Eržen, Hrga, Povh and Vodeb v0.0.4 archive (DOI 10.5281/zenodo.14290290), in original vertex order. The other three families use fixed generator seeds, with no selection by optimization results. The graph files, exact seeds and method-independent schedule are committed before any panel run. The same graph bytes are given to all methods. Calibration uses a separate tiny graph with a known optimum. We cite the historical G63 witness of 27,050 (DOI 10.5281/zenodo.24079948) as context and exclude that instance and its solutions from the panel and warm starts.

Freeze the existing Morpheus implementation before evaluations. The open references are MQLib BURER2002, MQLib PALUBECKIS2004bMST2, a portfolio of eight equal-time alternating BURER2002 and FESTA2002GVNSPR calls, and the CPU D-Wave TabuSampler. TabuSampler makes two calls with different seeds across the remaining time after building its input model. The portfolio has its own full 24-second allocation, including setup. All arms start cold with the graph and seed. The portfolio uses the same base seed as Morpheus in each block. Third-party solvers receive signed weighted objectives with exact integer equivalence.

## Resource accounting

Every trial runs in a fresh process group pinned to a single logical CPU. Within each graph and seed block, the arms run on the same CPU; rotate their order by block. Up to six blocks run at once on distinct physical cores on the same machine. Solver and numerical-library thread limits are one. All parsing, imports, conversion, method selection and solver subprocesses are inside the 24-second wall-clock limit from dispatch. Both user and system CPU time are measured for the process tree. Record wall time, and peak sampled sum of resident memory across the tree in KiB. Memory is a sampled diagnostic and may count shared pages multiple times. Preparation and offline verification are recorded separately.

Only a fully received partition with a timestamp at or before the deadline is eligible. Save the best such partition per trial, the time at which it was received and any timeout, missing output or error. Stop the process group at the deadline. A trial that reaches the deadline with a valid partition remains scored. Publish every scheduled row. Empty or invalid results have no cut value and fail the complete-panel requirement. No selective retries and no changes to methods or graph selection after any panel outcome.

## Analysis

For each graph and seed, compare Morpheus with each reference and with the maximum of the four separately run references. The latter is a conservative comparison with an observed envelope, not a single equal-budget competitor. Take the median of the three paired cut differences for each graph, then count graph wins, ties and losses. Primary success requires all 300 trials to have verified partitions, a positive median graph margin against the envelope, and a one-sided exact sign test (discarding ties) with p at most 0.05. Report the observed differences and denominator separately for each family, plus the median and mean margin normalized by the sum of absolute edge weights. Individual reference comparisons and family results are descriptive. The sign test is interpreted under the independent fair-sign null on this panel. No claims about a population of all Max-Cut graphs, global optimality or a record follow from the test.

Stop after the frozen panel and the independent audit. The independent verifier recomputes the score from the graph and submitted bits, checks the full schedule and verifies the digests of each instance and partition. Technical failures are retained with their scope. Results, including losses and ties, are disclosed with the verifier.
