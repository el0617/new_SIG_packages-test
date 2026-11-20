"""Constants that are already fixed: these pass from day one."""

from sigtd.portfolio.views import COLUMNS, CONFIDENCE_TO_IDZOREK


def test_confidence_map_is_monotone_and_bounded():
    vals = [CONFIDENCE_TO_IDZOREK[k] for k in range(1, 6)]
    assert vals == sorted(vals)
    assert 0 < vals[0] and vals[-1] < 1


def test_view_sheet_requires_a_kill_trigger():
    assert "kill_trigger" in COLUMNS
