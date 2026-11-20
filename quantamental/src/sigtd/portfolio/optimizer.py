"""From Black-Litterman returns to weights, sized by the tracking-error target.

Step 1  Unconstrained BL optimum: w* = (delta S)^-1 mu_BL. Its active part w* - b is a combination
        of the view portfolios only (Black-Litterman's own result), so every tilt traces to a view.
Step 2  Size: shrink the active vector so ex-ante TE <= te_target (never scale weak views up).
Step 3  Project onto the policy limits (cvxpy): the feasible portfolio closest to the target in
        tracking-error terms, with sum(w)=1, w>=0, |w-b|<=limit, TE<=te_target.
"""

from __future__ import annotations

import cvxpy as cp
import numpy as np
import pandas as pd

from sigtd.config import Config


def optimize(
    mu: pd.Series, cov: pd.DataFrame, benchmark: pd.Series, cfg: Config, te_target: float
) -> pd.Series:
    sectors = list(benchmark.index)
    S = 12 * cov.loc[sectors, sectors].values
    S = (S + S.T) / 2 + 1e-10 * np.eye(len(sectors))
    b = benchmark.values
    delta = cfg.get("black_litterman.delta")
    limit = cfg.get("mandate.limits.active_weight_pp") / 100

    w_star = np.linalg.solve(delta * S, mu.reindex(sectors).values)
    active = w_star - b
    te = float(np.sqrt(max(active @ S @ active, 0.0)))
    if te < 1e-10:
        return benchmark.rename("weight")
    active *= min(1.0, te_target / te)
    target = b + active

    w = cp.Variable(len(sectors))
    Sp = cp.psd_wrap(S)
    constraints = [
        cp.sum(w) == 1,
        cp.abs(w - b) <= limit,
        cp.quad_form(w - b, Sp) <= te_target**2,
    ]
    if cfg.get("mandate.limits.long_only", True):
        constraints.append(w >= 0)
    problem = cp.Problem(cp.Minimize(cp.quad_form(w - target, Sp)), constraints)
    try:
        problem.solve(solver=cp.CLARABEL)
    except cp.SolverError:
        problem.solve()
    if w.value is None:
        return benchmark.rename("weight")
    out = pd.Series(np.clip(w.value, 0, None), index=sectors)
    return (out / out.sum()).rename("weight")
