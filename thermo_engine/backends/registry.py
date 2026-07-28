"""BackendRegistry. Central model management.
Chen Shaohui: registry.get(id) for API.
Xia Xinhua: registry.list_models() for UI.
Ma Maosen/He Qi: registry.get_model_card(id).
"""
from typing import Any
from thermo_engine.backends.base import BackendAdapter
from thermo_engine.backends.ideal_raoult import IdealRaoultAdapter
from thermo_engine.backends.peng_robinson import PengRobinsonAdapter
from thermo_engine.backends.contracts.nrtl import NrtlAdapter, NrtlLleContract
from thermo_engine.backends.contracts.uniqac import UniquacAdapter
from thermo_engine.backends.contracts.wilson import WilsonAdapter
from thermo_engine.backends.contracts.srk import SrkAdapter

class BackendRegistry:
    def __init__(self):
        self._adapters: dict[str, BackendAdapter] = {}
        for a in [IdealRaoultAdapter(), PengRobinsonAdapter(), NrtlAdapter(),
                  NrtlLleContract(), UniquacAdapter(), WilsonAdapter(), SrkAdapter()]:
            self._adapters[a.model_id] = a

    def get(self, mid: str) -> BackendAdapter:
        if mid not in self._adapters: raise ValueError(f"Unknown: {mid}")
        return self._adapters[mid]

    def register(self, a: BackendAdapter): self._adapters[a.model_id] = a

    def list_models(self) -> list[dict]:
        return [{"model_id": a.model_id, "display_name": a.display_name,
                 "model_type": a.model_type, "status": a.status.value,
                 "supported_tasks": [t.value for t in a.supported_tasks]}
                for a in self._adapters.values()]

    def get_model_card(self, mid: str) -> dict:
        return self.get(mid).get_model_card().model_dump()

    def get_runnable_ids(self) -> list[str]:
        return [mid for mid, a in self._adapters.items() if a.status.value == "runnable"]
