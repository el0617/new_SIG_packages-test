"""Power checks: run these BEFORE a test, and write the answer in research_log.md."""

from __future__ import annotations

import math

from scipy.stats import norm


def min_detectable_corr(n_obs: int, alpha: float = 0.05, power: float = 0.80) -> float:
    """(z_{1-alpha} + z_{power}) / sqrt(n_obs), one-sided."""
    return (norm.ppf(1 - alpha) + norm.ppf(power)) / math.sqrt(n_obs)


def min_detectable_ic(
    n_sectors: int, n_months: int, alpha: float = 0.05, power: float = 0.80
) -> float:
    """Same, for a monthly cross-sectional IC whose null s.d. is about 1/sqrt(n_sectors - 1)."""
    return (norm.ppf(1 - alpha) + norm.ppf(power)) / math.sqrt((n_sectors - 1) * n_months)
