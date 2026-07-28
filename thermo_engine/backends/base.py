"""BackendAdapter ABC. All model adapters inherit this.
Wang Zhongshuo: implement calculate() for new models.
Chen Shaohui: uniform calling interface.
Sun Minghao: test against this interface.
"""
from abc import ABC, abstractmethod
from typing import Any
from thermo_engine.schemas import EquilibriumResult, ModelCard, ModelStatus, TaskManifest, TaskType

# === BackendAdapter Abstract Base Class ===
# All model adapters (both runnable and contract) inherit this.
# Subclasses MUST set: model_id, display_name, model_type, status
# Subclasses MUST implement: calculate()
# Subclasses MAY override: get_model_card()
class BackendAdapter(ABC):
    model_id: str = ""
    display_name: str = ""
    model_type: str = ""
    status: ModelStatus = ModelStatus.CONTRACT
    supported_tasks: list[TaskType] = []

    def __init__(self):
        self._validate_metadata()
    def _validate_metadata(self):
        if not self.model_id: raise NotImplementedError("model_id required")
        if not self.display_name: raise NotImplementedError("display_name required")

    # === Core calculation interface ===
    # Input: TaskManifest (task_type, components, conditions, parameters)
    # Output: EquilibriumResult (always returns, never raises)
    # Runnable models: perform actual computation
    # Contract models: return error status
    @abstractmethod
    def calculate(self, manifest: TaskManifest) -> EquilibriumResult:
        ...

    def get_model_card(self) -> ModelCard:
        return ModelCard(model_id=self.model_id, display_name=self.display_name,
            model_type=self._type(), status=self.status,
            description=self.display_name, applicable_tasks=self.supported_tasks,
            applicable_systems=["general"], pressure_range="",
            temperature_range="", max_components=5, limitations=[],
            parameters=[], routing_priority=50)

    def _type(self) -> str:
        if "equation" in self.model_type.lower(): return "equation_of_state"
        if "ideal" in self.model_type.lower(): return "ideal"
        return "activity_coefficient"
