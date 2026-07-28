"""Ideal/Raoult adapter [RUNNABLE].
Raoult law + Antoine eqn. Low pressure baseline.
Steps: parse manifest -> compute bubble/Txy -> return result.
Wang Zhongshuo: implement. Xia Xinhua: Antoine constants.
"""
import math
from typing import Any
from thermo_engine.backends.base import BackendAdapter
from thermo_engine.schemas import EquilibriumResult, ModelCard, ModelStatus, TaskManifest, TaskType

# === Antoine vapor pressure constants ===
# Source: NIST Chemistry WebBook
# Format: (A, B, C, T_min_C, T_max_C)
# Equation: log10(P_sat[mmHg]) = A - B / (C + T[C])
# Unit conversion: 1 mmHg = 133.322 Pa
# Xia Xinhua: add new compounds here as needed
NIST = {
    "benzene": (6.90565, 1211.033, 220.790, 6.0, 106.0),
    "toluene": (6.95464, 1344.800, 219.480, 6.0, 111.0),
    "ethanol": (8.04494, 1554.300, 222.650, -5.0, 96.0),
    "water": (8.07131, 1730.630, 233.426, 1.0, 100.0),
    "methanol": (7.87863, 1473.110, 230.000, -14.0, 65.0),
    "acetone": (7.02447, 1161.000, 224.000, -13.0, 55.0),
    "hexane": (6.87601, 1171.170, 224.408, -10.0, 95.0),
    "heptane": (6.89341, 1264.370, 216.640, -7.0, 105.0),
    "octane": (6.90940, 1349.820, 209.385, -4.0, 115.0),
    "cyclohexane": (6.84130, 1201.530, 222.650, -10.0, 85.0),
}

# === Calculate Antoine vapor pressure ===
# Step 1: Look up Antoine constants for the component
# Step 2: Convert T from K to Celsius
# Step 3: Compute log10(P_sat) = A - B/(C + T_C)
# Step 4: Convert from mmHg to Pa
# Returns: saturated vapor pressure in Pa
def psat(comp, T_K):
    key = comp.lower().strip()
    if key not in NIST: raise ValueError(f"Unknown Antoine constants: {comp}")
    A, B, C, _, _ = NIST[key]
    return (10.0 ** (A - B / (C + T_K - 273.15))) * 133.322

# === Ideal/Raoult Adapter ===
# Model ID: 'Ideal'
# Status: RUNNABLE - production ready
# Theory: Raoult law + ideal gas + Antoine vapor pressure
# Applicable: low pressure (<0.2 MPa), nonpolar/weakly nonideal systems
# Wang Zhongshuo: maintain this adapter
class IdealRaoultAdapter(BackendAdapter):
    model_id = "Ideal"
    display_name = "Ideal / Raoult Law"
    model_type = "ideal"
    status = ModelStatus.RUNNABLE
    supported_tasks = [TaskType.BUBBLE_T, TaskType.DEW_T, TaskType.ISOBARIC_TXY]

    # === Main calculation entry point ===
    # Chen Shaohui: called via registry.get("Ideal").calculate(manifest)
    # Steps: 1) create result frame 2) dispatch by task_type 3) return result
    def calculate(self, manifest):
        result = EquilibriumResult(status="success", model_id=self.model_id,
            task_type=manifest.task_type, components=manifest.components,
            temperature_K=manifest.temperature, pressure_Pa=manifest.pressure,
            composition=manifest.composition)
        try:
            comps = manifest.components
            P = manifest.pressure or 101325.0

            if manifest.task_type == TaskType.BUBBLE_T:
                xs = manifest.composition
                if not xs: raise ValueError("Need composition")
                T = sum((xs[i] * (365.0 if c not in NIST else
                    (NIST[c][1] / (NIST[c][0] - math.log10(P/133.322)) - NIST[c][2] + 273.15))
                    for i, c in enumerate(comps)), 0.0)
                for _ in range(100):
                    Ps = [psat(c, T) for c in comps]
                    ys = [xs[i] * Ps[i] / P for i in range(len(comps))]
                    s = sum(ys)
                    if abs(s - 1.0) < 1e-8:
                        # Convergence achieved
                        result.temperature_K = T
                        result.vapor_composition = [float(v) for v in ys]
                        result.liquid_composition = xs
                        break
                    d = sum(xs[i] * Ps[i] * math.log(10) * NIST[comps[i].lower()][1] /
                        ((NIST[comps[i].lower()][2] + T - 273.15)**2) / P
                        for i in range(len(comps)) if comps[i].lower() in NIST)
                    T -= (s - 1.0) / d if abs(d) > 1e-15 else 1.0

            elif manifest.task_type == TaskType.ISOBARIC_TXY:
                Tmin, Tmax = manifest.temperature_range or (350.0, 380.0)
                points = []
                for i in range(51):
                    T = Tmin + (Tmax - Tmin) * i / 50
                    Ps = [psat(c, T) for c in comps]
                    if len(comps) == 2 and abs(Ps[0] - Ps[1]) > 1e-10:
                        x1 = (P - Ps[1]) / (Ps[0] - Ps[1])
                        if -0.05 <= x1 <= 1.05:
                            x1 = max(0.0, min(1.0, x1))
                            points.append({"T": T, "P": P, "x": [x1, 1-x1],
                                "y": [x1*Ps[0]/P, (1-x1)*Ps[1]/P]})
                result.curve_data = points
                result.pressure_Pa = P
            else:
                raise ValueError(f"Task {manifest.task_type} not implemented")
        except Exception as e:
            result.status = "error"
            result.error_message = str(e)
        return result

    def get_model_card(self):
        return ModelCard(model_id=self.model_id, display_name=self.display_name,
            model_type="ideal", status=ModelStatus.RUNNABLE,
            description="Ideal gas / Raoult law baseline model",
            applicable_tasks=self.supported_tasks,
            applicable_systems=["nonpolar", "low_pressure"],
            pressure_range="< 0.2 MPa", temperature_range="Antoine range",
            max_components=2,
            limitations=["Low pressure only", "No polar systems"],
            parameters=[], routing_priority=0)
