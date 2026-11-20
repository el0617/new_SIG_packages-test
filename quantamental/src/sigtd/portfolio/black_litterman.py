"""Black-Litterman posterior with Idzorek-style confidences (annual units)."""

from __future__ import annotations

import numpy as np
import pandas as pd


def posterior(
    pi: pd.Series,
    cov: pd.DataFrame,
    P: pd.DataFrame,
    Q: pd.Series,
    confidence: pd.Series,
    tau: float = 0.05,
) -> pd.Series:
    """mu_BL = [(tau S)^-1 + P' W^-1 P]^-1 [(tau S)^-1 pi + P' W^-1 Q], S = 12 x monthly cov.

    Each view's uncertainty W_kk = (1 - c)/c * tau * p_k S p_k', so c = 0.5 sits halfway between
    prior and view, and c -> 1 approaches the view itself (Walters' closed form of Idzorek).
    """
    if P is None or len(P) == 0:
        return pi.copy()
    S = 12 * cov.loc[pi.index, pi.index].values
    Pm = P[pi.index].values
    c = np.clip(np.asarray(confidence, float), 0.01, 0.99)
    omega = np.diag(((1 - c) / c) * tau * np.einsum("ij,jk,ik->i", Pm, S, Pm))
    tS_inv = np.linalg.inv(tau * S)
    o_inv = np.linalg.inv(omega)
    A = tS_inv + Pm.T @ o_inv @ Pm
    b = tS_inv @ pi.values + Pm.T @ o_inv @ np.asarray(Q, float)
    return pd.Series(np.linalg.solve(A, b), index=pi.index, name="mu_bl")
