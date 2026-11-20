"""Infrastructure tests: these pass from day one."""

from sigtd.data.registry import load_registry


def test_config_has_eleven_sectors(cfg):
    assert len(cfg.sectors) == 11


def test_limits_are_present(cfg):
    assert cfg.get("mandate.limits.active_weight_pp") == 5.0
    lo, hi = cfg.get("mandate.limits.te_budget")
    assert 0 < lo < hi < 0.1


def test_registry_is_valid(cfg):
    reg = load_registry(cfg)
    assert {"PAYEMS", "CPILFESL", "GS10", "TB3MS", "USREC"} <= set(reg.index)
    assert (reg["release_lag_days"] >= 0).all()


def test_insurance_band_is_ordered(cfg):
    assert cfg.get("insurance.te_min") < cfg.get("insurance.te_max")
    assert cfg.get("insurance.p_low") < cfg.get("insurance.p_high")
