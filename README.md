# new_SIG_packages-test

Two candidate top-down engines for the SIG sector portfolio, side by side. Each folder is a
self-contained Python package (`sigtd`) with its own config, Makefile, docs and tests.

| | [`forecast-light/`](forecast-light) (package 2) | [`quantamental/`](quantamental) (package 3) |
| --- | --- | --- |
| Question it answers | How much defensive insurance should we hold, given recession risk? | What should the 11 sector weights be, given tested signals and analyst views? |
| What moves the weights | One forecast: 12-month recession probability sets the tracking error spent on insurance (1.0%-3.5%) | Signals that pass a power-checked scorecard plus analyst view sheets, through Black-Litterman and a constrained optimizer (3% TE target) |
| Analyst input | Narrative and scenario weights | `views/view_sheet.csv`: direction, expected relative return, confidence, kill trigger |
| When evidence is weak | It is the weak-evidence design | Falls back to the forecast-light engine and says so in the brief |
| Modules | data, regime (context), recession probability, risk budget, risk, brief | all of package 2 plus sensitivities, signals, analog regimes, views, BL, optimizer, attribution |
| Build size | smaller | about 1.5x the code |

Read each folder's `README.md`, then `src/sigtd/pipeline.py`: it shows the whole weekly run.

> **Branch `demo/quantamental-runnable`** contains a working reference implementation of
> `quantamental/` that runs end to end on the fall repo's data cache (`make import-fall-cache && make demo`),
> with sample briefs in `quantamental/examples/`. `main` keeps the stubs for your own build.

## Status

Scaffolds. Infrastructure is written (config, CLI, pipeline wiring, fixtures, CI, docs). Model logic
raises `NotImplementedError` with a pointer to its roadmap phase, and the matching acceptance tests
are marked as expected failures until each module is written.

## Working in a package

```bash
cd quantamental            # or forecast-light
make install               # editable install of that package
make test
```

Run `pre-commit install` once at the repo root: it runs ruff and blocks licensed Bloomberg exports
in either package.
