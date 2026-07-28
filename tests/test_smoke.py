"""Smoke tests. Sun Minghao: maintain.
"""
from thermo_engine.backends.registry import BackendRegistry
from thermo_engine.schemas import TaskManifest

reg = BackendRegistry()

def test_list():
    ids = [x["model_id"] for x in reg.list_models()]
    for n in ["Ideal","Peng-Robinson","NRTL","UNIQUAC","Wilson","SRK"]:
        assert n in ids

def test_runnable():
    r = reg.get_runnable_ids()
    assert "Ideal" in r and "Peng-Robinson" in r
    assert "NRTL" not in r

def test_ideal_bubble():
    m = TaskManifest(task_type="bubble_T", model_id="Ideal",
        components=["benzene","toluene"], pressure=101325.0, composition=[0.5,0.5])
    r = reg.get("Ideal").calculate(m)
    assert r.status == "success"
    assert r.temperature_K is not None

def test_ideal_txy():
    m = TaskManifest(task_type="isobaric_Txy", model_id="Ideal",
        components=["benzene","toluene"], pressure=101325.0, temperature_range=[353.0,383.0])
    r = reg.get("Ideal").calculate(m)
    assert r.curve_data is not None

def test_pr():
    m = TaskManifest(task_type="bubble_T", model_id="Peng-Robinson",
        components=["methane","ethane"], pressure=101325.0, composition=[0.5,0.5])
    r = reg.get("Peng-Robinson").calculate(m)
    assert r.status == "success"

def test_contracts():
    for mid in ["NRTL","UNIQUAC","Wilson","SRK"]:
        m = TaskManifest(task_type="bubble_T", model_id=mid,
            components=["a","b"], pressure=101325.0, composition=[0.5,0.5])
        r = reg.get(mid).calculate(m)
        assert r.status == "error"

def test_card():
    c = reg.get_model_card("NRTL")
    assert c["model_id"] == "NRTL"
    assert c["status"] == "contract"
