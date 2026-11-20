PY ?= python

.PHONY: install lint test data dashboard weekly backtest research

install:            ## editable install (run `pre-commit install` once at the repo root)
	$(PY) -m pip install -e ".[dev]"

lint:
	ruff check .

test:
	pytest

data:               ## rebuild every cache from scratch (FRED, ALFRED, Yahoo, Bloomberg exports)
	$(PY) -m sigtd.cli data

dashboard:          ## macro dashboard -> reports/
	$(PY) -m sigtd.cli dashboard

weekly:             ## the Friday model brief -> reports/brief_<date>.html
	$(PY) -m sigtd.cli weekly

backtest:           ## walk-forward backtest of the systematic pipeline
	$(PY) -m sigtd.cli backtest

research:           ## re-run the frozen signal research -> outputs/scorecard.csv
	$(PY) -m sigtd.cli research
