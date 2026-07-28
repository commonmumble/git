"""Core data models (TaskManifest, EquilibriumResult, ModelCard).
Backend (Chen Shaohui): input/output types.
RAG/Skill (Ma Maosen, He Qi): ModelCard for model selection.
Frontend (Xia Xinhua): display model info.
"""
from __future__ import annotations
from enum import Enum
from typing import Any, Literal
from pydantic import BaseModel, Field, model_validator

# === Task type enum: what kind of calculation to perform ===
# Chen Shaohui: maps API endpoint to task type
class TaskType(str, Enum):
    BUBBLE_T = "bubble_T"
    BUBBLE_P = "bubble_P"
    DEW_T = "dew_T"
    DEW_P = "dew_P"
    TP_FLASH = "TP_flash"
    ISOBARIC_TXY = "isobaric_Txy"
    ISOTHERMAL_PXY = "isothermal_Pxy"
    AZEOTROPE = "azeotrope_search"
    PHASE_CLASSIFY = "phase_classify"

# === Model implementation status ===
# Xia Xinhua: frontend uses this to show availability
class ModelStatus(str, Enum):
    RUNNABLE = "runnable"
    CONTRACT = "contract"
    PLANNED = "planned"

# === Task manifest: universal input format ===
# Chen Shaohui: deserialize API request into this
# Wang Zhongshuo: pass to calculate()
class TaskManifest(BaseModel):
    task_type: TaskType = Field(...)
    model_id: str = Field(...)
    components: list[str] = Field(..., min_length=1, max_length=10)
    composition: list[float] | None = Field(None)
    temperature: float | None = Field(None, gt=0)
    pressure: float | None = Field(None, gt=0)
    temperature_range: tuple[float, float] | None = Field(None)
    pressure_range: tuple[float, float] | None = Field(None)
    parameters: dict[str, Any] | None = Field(None)
    max_iterations: int = Field(100)
    tolerance: float = Field(1e-8)

    @model_validator(mode="after")
    def validate_conditions(self) -> "TaskManifest":
        if not any([self.temperature, self.pressure, self.temperature_range, self.pressure_range]):
            raise ValueError("Need at least one condition")
        return self

    @model_validator(mode="after")
    def validate_composition_sum(self) -> "TaskManifest":
        if self.composition and abs(sum(self.composition) - 1.0) > 1e-6:
            raise ValueError(f"Composition must sum to 1.0")
        return self

    @model_validator(mode="after")
    def validate_length(self) -> "TaskManifest":
        if self.composition and self.components and len(self.composition) != len(self.components):
            raise ValueError("Length mismatch")
        return self

# === Validation result: physical constraint checks ===
# Sun Minghao: verify calculation physicality
class ValidationResult(BaseModel):
    passed: bool = Field(...)
    checks: list[dict[str, Any]] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

# === Equilibrium result: universal output format ===
# All adapters return this. Backend serializes to JSON for frontend.
class EquilibriumResult(BaseModel):
    status: Literal["success", "error", "warning"] = Field(...)
    model_id: str = Field(...)
    task_type: TaskType = Field(...)
    components: list[str] = Field(...)
    temperature_K: float | None = Field(None)
    pressure_Pa: float | None = Field(None)
    composition: list[float] | None = Field(None)
    vapor_composition: list[float] | None = Field(None)
    liquid_composition: list[float] | None = Field(None)
    vapor_fraction: float | None = Field(None, ge=0, le=1)
    K_values: list[float] | None = Field(None)
    activity_coefficients: list[float] | None = Field(None)
    lnphi_gas: list[float] | None = Field(None)
    lnphi_liquid: list[float] | None = Field(None)
    Z_gas: float | None = Field(None)
    Z_liquid: float | None = Field(None)
    curve_data: list[dict[str, Any]] | None = Field(None)
    validation: ValidationResult | None = Field(None)
    evidence: list[dict[str, Any]] | None = Field(None)
    error_message: str | None = Field(None)

# === Parameter specification: describes one model parameter ===
# Xia Xinhua: documents parameter requirements in model cards
class ParameterSpec(BaseModel):
    name: str = Field(...)
    type: str = Field(...)
    required: bool = Field(...)
    description: str = Field(...)
    default: Any | None = Field(None)
    unit: str | None = Field(None)

# === Model card: applicability documentation ===
# Ma Maosen/He Qi: read this for model selection routing
# Xia Xinhua: write applicable_systems, limitations content
class ModelCard(BaseModel):
    model_id: str = Field(...)
    display_name: str = Field(...)
    model_type: Literal["activity_coefficient", "equation_of_state", "ideal"] = Field(...)
    status: ModelStatus = Field(...)
    description: str = Field(...)
    applicable_tasks: list[TaskType] = Field(...)
    applicable_systems: list[str] = Field(...)
    pressure_range: str = Field(...)
    temperature_range: str = Field(...)
    max_components: int = Field(...)
    limitations: list[str] = Field(...)
    parameters: list[ParameterSpec] = Field(...)
    routing_priority: int = Field(0)
    routing_rules: list[str] = Field(default_factory=list)
    references: list[str] = Field(default_factory=list)
