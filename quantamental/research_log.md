# Research log

One entry per test, failures included, written **before** looking at the result where possible.
This file is your defence against "did you overfit?" and the input for multiple-testing haircuts.

## Template

### YYYY-MM-DD: <question>

- **Module / version:** e.g. M4 signals, v0.4-dev
- **Pre-registration:** link to docs/prereg/... (or "exploratory")
- **Specification:** exact definition, sample, horizon
- **Power check:** N independent observations = ..., minimum detectable effect = ...
- **Result:** numbers, with standard errors
- **Decision:** what changes in the model, the weights or the brief (or "nothing", and why)

---

## Example entries from the reference run (demo branch)

### 2026-11-20: Do the pre-registered signals predict next-month sector relative returns?

- **Module / version:** M4 signals, reference implementation
- **Pre-registration:** docs/prereg/signals.md (priors: momentum strong; others weak)
- **Specification:** monthly scores 2001-2026, 11 sectors (proxies before XLRE/XLC), Spearman IC vs
  next-month return relative to SPY, Newey-West(1) t, Holm across signals
- **Power check:** about 309 months x 11 sectors: minimum detectable IC 0.045 (80% power, 5% one-sided)
- **Result:** momentum IC 0.017 (t 0.7); regime-conditional -0.014 (t -0.6); macro tilt -0.006
  (t -0.2); composite 0.003. Revision breadth and valuation not tested (no Bloomberg data).
- **Decision:** no signal views enter the portfolio. Re-test once the Bloomberg revision data exist;
  revisions had the strongest prior after momentum.

### 2026-11-20: Is the recession model calibrated out of sample?

- **Module / version:** M5, reference implementation
- **Specification:** logit on term spread, Baa-10y spread, 6-month change in claims; expanding
  window from 1985 with a 24-month label embargo; scored monthly 1995-2026
- **Result:** AUC 0.84, Brier skill -0.04 against the base rate
- **Decision:** report the probability with the warning "ranks well, calibrates poorly". Candidate
  fix to pre-register: add a financial-conditions term (NFCI) and test whether it cuts the 2022-24 false alarm.
