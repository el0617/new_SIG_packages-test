"""M7 acceptance: the backtest is provably point-in-time."""

from sigtd.risk.backtest import walk_forward


def test_engine_never_sees_future(cfg, panel, benchmark):
    seen = []

    def spy(p, as_of):
        seen.append((as_of, p.returns_through(as_of).index.max()))
        return benchmark

    walk_forward(cfg, start="2010-01-31", engine=spy, panel=panel)
    assert seen
    assert all(last <= as_of for as_of, last in seen)


def test_benchmark_engine_has_only_cost_drag(cfg, panel, benchmark):
    out = walk_forward(cfg, start="2010-01-31", engine=lambda p, d: benchmark, panel=panel)
    assert out["active_return"].abs().max() < 1e-4
