"""NRTL [CONTRACT - Phase 4].
"""
from thermo_engine.backends.base import BackendAdapter
from thermo_engine.schemas import EquilibriumResult, ModelCard, ModelStatus, ParameterSpec, TaskManifest, TaskType

class NrtlAdapter(BackendAdapter):
    model_id = "NRTL"
    display_name = "NRTL"
    model_type = "activity_coefficient"
    status = ModelStatus.CONTRACT
    supported_tasks = [TaskType.BUBBLE_T, TaskType.BUBBLE_P]
    def calculate(self, m):
        return EquilibriumResult(status="error", model_id=self.model_id,
            task_type=m.task_type, components=m.components,
            error_message="NRTL solver not deployed (Phase 4)")
    def get_model_card(self):
        return ModelCard(model_id=self.model_id, display_name=self.display_name,
            model_type="activity_coefficient", status=ModelStatus.CONTRACT,
            description="NRTL activity coefficient model",
            applicable_tasks=self.supported_tasks,
            applicable_systems=["polar", "hydrogen_bonding"],
            pressure_range="< 2 MPa", temperature_range="depends on parameters",
            max_components=5, limitations=["No gas nonideality", "Parameter quality dependent"],
            parameters=[
                ParameterSpec(name="tau_coeffs", type="ndarray(N,N,6)", required=True, description="tau coefficients"),
                ParameterSpec(name="alpha_coeffs", type="ndarray(N,N,2)", required=False, description="alpha, default 0.3"),
            ], routing_priority=30)

class NrtlLleContract(BackendAdapter):
    model_id = "NRTL-LLE"
    display_name = "NRTL LLE"
    model_type = "activity_coefficient"
    status = ModelStatus.CONTRACT
    supported_tasks = [TaskType.PHASE_CLASSIFY]
    def calculate(self, m):
        return EquilibriumResult(status="error", model_id=self.model_id,
            task_type=m.task_type, components=m.components,
            error_message="NRTL-LLE solver not deployed (Phase 4)")