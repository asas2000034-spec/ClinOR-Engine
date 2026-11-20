# Mathematical model (demonstration)

A user supplies \(n\) options and manually reviewed normalized scores for benefit \(b_i\), burden \(r_i\), and cost \(c_i\). Selection decision \(x_i \in \{0,1\}\).

Maximize:

\[\sum_i (w_b b_i - w_r r_i - w_c c_i)x_i\]

Subject to:

- Selection bounds: \(L \leq \sum_i x_i \leq U\).
- Optional financial budget: \(\sum_i c_i x_i \leq B\).
- Absolute exclusion: \(x_i = 0\) for a forbidden option.
- Pairwise incompatibility: \(x_i + x_j \leq 1\).
- Prerequisite: \(x_i \leq x_j\) when i requires j.

This is a **toy linear-additive utility model** for constrained choice research. Summing hypothetical benefit scores across combinations does not generally capture clinical additivity, interactions, sequence, evidence certainty, contraindications, or patient-specific outcomes. Real clinical use needs full clinical modeling, medical expert review and prospective evaluation. The mathematical optimum is conditional on the supplied utility function, eligibility constraints and data.

SciPy MILP returns an optimum or feasible incumbent; status distinguishes proofs of optimality from non-proven feasible solutions. Infeasible hard constraints are never relaxed automatically.
