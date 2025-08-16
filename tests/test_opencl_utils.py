import sys, os, types, importlib
from unittest import mock
import pytest

ROOT=os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path: sys.path.insert(0, ROOT)

def fake_module(platforms):
    return types.SimpleNamespace(get_platforms=lambda: platforms,
                                 status_code=types.SimpleNamespace(SUCCESS=0,to_string=lambda c:f"ERR{c}"))

class D:
    def __init__(self,name="FakeDevice"): self.name=name

class P:
    def __init__(self,devices=None): self.devices=devices or []
    def get_devices(self): return self.devices

def test_available_with_device():
    fake_cl=fake_module([P([D()])])
    with mock.patch.dict(sys.modules,{"pyopencl":fake_cl}):
        import ready.opencl_utils as oc; importlib.reload(oc)
        assert oc.IsOpenCLAvailable()
        assert "Device 1" in oc.GetOpenCLDiagnostics()

def test_unavailable_no_device():
    fake_cl=fake_module([P([])])
    with mock.patch.dict(sys.modules,{"pyopencl":fake_cl}):
        import ready.opencl_utils as oc; importlib.reload(oc)
        assert not oc.IsOpenCLAvailable()
        assert "No devices" in oc.GetOpenCLDiagnostics()

def test_no_platforms():
    fake_cl=fake_module([])
    with mock.patch.dict(sys.modules,{"pyopencl":fake_cl}):
        import ready.opencl_utils as oc; importlib.reload(oc)
        assert not oc.IsOpenCLAvailable()
        assert "No OpenCL platforms available" in oc.GetOpenCLDiagnostics()

def test_throw_on_error():
    fake_cl=fake_module([])
    with mock.patch.dict(sys.modules,{"pyopencl":fake_cl}):
        import ready.opencl_utils as oc; importlib.reload(oc)
        oc.throwOnError(0,"ok")
        with pytest.raises(RuntimeError) as err:
            oc.throwOnError(1,"fail ")
    assert str(err.value)=="fail ERR1"
