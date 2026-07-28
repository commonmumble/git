"""Wilson [CONTRACT - Phase 4]. Cannot handle LLE.
"""
from thermo_engine.backends.base import BackendAdapter
from thermo_engine.schemas import EquilibriumResult, ModelCard, ModelStatus, ParameterSpec, TaskManifest, TaskType

class WilsonAdapter(BackendAdapter):
    model_id = "Wilson"
    display_name = "Wilson"
    model_type = "activity_coefficient"
    status = ModelStatus.CONTRACT
    supported_tasks = [TaskType.BUBBLE_T, TaskType.BUBBLE_P]
    def calculate(self, m):
        return EquilibriumResult(status="error", model_id=self.model_id,
            task_type=m.task_type, components=m.components,
            error_message="Wilson solver not deployed (Phase 4)")
    def get_model_card(self):
        return ModelCard(model_id=self.model_id, display_name=self.display_name,
            model_type="activity_coefficient", status=ModelStatus.CONTRACT,
            description="Wilson equation for fully miscible VLE",
            applicable_tasks=self.supported_tasks,
            applicable_systems=["fully_miscible", "VLE"],
            pressure_range="< 2 MPa", temperature_range="depends on parameters",
            max_components=5, limitations=["Cannot handle LLE", "No gas nonideality"],
            parameters=[
                ParameterSpec(name="Lambda_coeffs", type="ndarray(N,N,6)", required=True, description="Lambda coefficients"),
            ], routing_priority=40)