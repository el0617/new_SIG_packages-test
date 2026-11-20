# View sheets

Analysts copy `view_sheet_template.csv` to `view_sheet.csv` each Week 6+ Wednesday. One row per view.

| Column | Meaning | Rule |
| --- | --- | --- |
| sector | config key, e.g. `energy` | must exist in config.yaml |
| direction | `overweight` or `underweight` | |
| expected_rel_return_pp_12m | expected return vs the S&P 500, next 12 months, in pp | sign must match direction |
| confidence_1to5 | 1 = hunch, 5 = would bet the club on it | 4-5 needs two independent sources |
| kill_trigger | the indicator level that would reverse the view | required; must be checkable |
| source | `analyst` | signal views are added by the engine |
| owner | analyst name | |

Example (not a real view): `energy, overweight, 3.0, 3, "WTI below $60 for two consecutive months", analyst, Analyst 5`
