from core.monitor import Monitor

def test_monitor_sample():
    m = Monitor(history_max=10)
    m.sample()
    assert len(m.cpu_hist) > 0
    assert len(m.ram_hist) > 0
