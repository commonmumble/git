"""SRK [CONTRACT]. Use PR instead.
"""
from thermo_engine.backends.base import BackendAdapter
from thermo_engine.schemas import EquilibriumResult, ModelCard, ModelStatus, ParameterSpec, TaskManifest, TaskType

class SrkAdapter(BackendAdapter):
    model_id = "SRK"
    display_name = "SRK"
    model_type = "equation_of_state"
    status = ModelStatus.CONTRACT
    supported_tasks = [TaskType.BUBBLE_T]
    def calculate(self, m):
        return EquilibriumResult(status="error", model_id=self.model_id,
            task_type=m.task_type, components=m.components,
            error_message="SRK not deployed, use Peng-Robinson")
    def get_model_card(self):
        return ModelCard(model_id=self.model_id, display_name=self.display_name,
            model_type="equation_of_state", status=ModelStatus.CONTRACT,
            description="SRK EOS (overlaps with PR)",
            applicable_tasks=self.supported_tasks,
            applicable_systems=["nonpolar", "hydrocarbon"],
            pressure_range="medium-high", temperature_range="subcritical",
            max_components=5, limitations=["Not deployed, use PR"],
            parameters=[
                ParameterSpec(name="kijs", type="ndarray(N,N)", required=False, description="kij", default="zeros"),
            ], routing_priority=90)