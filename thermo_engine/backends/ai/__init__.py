"""AI models (reserved)"""
from thermo_engine.backends.base import BackendAdapter
_ai=[]
def get():return _ai
def reg(a):_ai.append(a)
