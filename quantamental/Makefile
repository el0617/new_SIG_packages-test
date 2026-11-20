PY ?= python

.PHONY: install lint test import-fall-cache data dashboard weekly weekly-fallback backtest research demo

install:            ## editable install (run `pre-commit install` once at the repo root)
	$(PY) -m pip install -e ".[dev]"

lint:
	ruff check .

test:
	pytest

import-fall-cache:  ## copy the FRED/Yahoo CSV cache from SIG_FALL_26 into data/raw (no API key needed)
	bash scripts/import_fall_cache.sh

data:               ## re-download every series (needs FRED_API_KEY and network)
	$(PY) -m sigtd.cli data

dashboard:          ## macro dashboard -> reports/
	$(PY) -m sigtd.cli dashboard

weekly:             ## the Friday model brief -> reports/brief_<date>.html
	$(PY) -m sigtd.cli weekly

weekly-fallback:    ## the same brief with no analyst views (risk-budget mode)
	$(PY) -m sigtd.cli weekly --views none

backtest:           ## walk-forward backtest of the systematic pipeline
	$(PY) -m sigtd.cli backtest

research:           ## re-run the frozen signal research -> outputs/scorecard.csv
	$(PY) -m sigtd.cli research

demo:               ## research + backtest + dashboard + both brief modes (about 3 minutes)
	$(PY) -m sigtd.cli demo
