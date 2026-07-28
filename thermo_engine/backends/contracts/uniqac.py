"""UNIQUAC [CONTRACT - Phase 4].
"""
from thermo_engine.backends.base import BackendAdapter
from thermo_engine.schemas import EquilibriumResult, ModelCard, ModelStatus, ParameterSpec, TaskManifest, TaskType

class UniquacAdapter(BackendAdapter):
    model_id = "UNIQUAC"
    display_name = "UNIQUAC"
    model_type = "activity_coefficient"
    status = ModelStatus.CONTRACT
    supported_tasks = [TaskType.BUBBLE_T, TaskType.BUBBLE_P]
    def calculate(self, m):
        return EquilibriumResult(status="error", model_id=self.model_id,
            task_type=m.task_type, components=m.components,
            error_message="UNIQUAC solver not deployed (Phase 4)")
    def get_model_card(self):
        return ModelCard(model_id=self.model_id, display_name=self.display_name,
            model_type="activity_coefficient", status=ModelStatus.CONTRACT,
            description="UNIQUAC activity coefficient model",
            applicable_tasks=self.supported_tasks,
            applicable_systems=["polar", "nonpolar", "polymer"],
            pressure_range="< 2 MPa", temperature_range="depends on parameters",
            max_components=5, limitations=["No gas nonideality", "Needs r/q parameters"],
            parameters=[
                ParameterSpec(name="tau_coeffs", type="ndarray(N,N,6)", required=True, description="tau coefficients"),
                ParameterSpec(name="rs", type="ndarray(N,)", required=False, description="volume params", default="auto"),
            ], routing_priority=35)