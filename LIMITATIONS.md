# Scope and limitations

- The panel has five instances per family. The chosen 24-second horizon and one workload per trial do not characterize long runs or other budgets.
- The local experiment used six distinct cores as reported by WSL2, arranged so that all methods in a paired block used the same logical CPU. Host activity, filesystem cache and virtualization can still affect elapsed time.
- A sampled process-tree RSS sum may count shared pages more than once and miss short peaks. CPU usage includes the subprocesses accounted for by the supervisor.
- In 180 MQLib trials, the guest's `wait4` CPU time exceeded monotonic elapsed time by up to 0.71 s. The CSV preserves the values returned by the guest. Use the elapsed deadline and the certified cuts for the primary comparison. The CPU counters do not support claims about CPU efficiency.
- All scores certify feasible cuts. The trial does not establish global optimality, whole-system learning, component-level attribution or scientific priority.
- The four public references are selected, reproducible baselines. Broader claims require further independently selected datasets and stronger methods where appropriate, including Breakout Local Search and recent specialized solvers. MQLib and Ocean tabu methods share some algorithmic ancestry.
- The principal comparison uses a retrospective envelope across four separate public runs per block. It therefore does not describe one deployable method using 24 seconds.
- Three seeds provide limited information about timing-related variability. Family and individual baseline results are descriptive, and the primary sign test uses the independent fair-sign null for this panel.
- The history of the closed candidate can be audited separately by its maintainers. Published data cover the frozen experiment and the full partitions used to evaluate it.
