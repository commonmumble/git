# thermo_engine 项目文档

## 项目概述

`thermo_engine` 是 **ThermoEqui-Agent** 的模型适配器层，将传统热力学模型（Ideal/Raoult、Peng-Robinson、NRTL、UNIQUAC、Wilson、SRK）封装成统一的 BackendAdapter 接口，并为未来 AI 模型预留接入空间。

项目地址：`D:\Codex\thermo_engine\`

---

## 团队分工（来自课题组任务分配）

| 成员 | 角色 | 涉及文件 |
|---|---|---|
| 孙铭浩 | 项目负责 + 测试 | 项目整体 + tests/ |
| 夏鑫华 | 前端 + 模型适用范围统筹 | 前端页面 + ModelCard |
| 陈少辉 | 后端 API | BackendRegistry 调用 |
| 马茂森、贺琪 | RAG/Skill/Prompt/知识图谱 | get_model_card() |
| 王中硕 | 传统模型整合 + AI 模型整合 | backends/（含 contracts/ 和 ai/） |

## 模型实现状态

| 模型 | 类型 | 状态 | 说明 |
|---|---|---|---|
| Ideal/Raoult | 活度系数（理想） | ✅ **RUNNABLE** | 低压基线，当前可使用 |
| Peng-Robinson | 状态方程 | ✅ **RUNNABLE** | 中高压体系，当前可使用 |
| NRTL | 活度系数 | 📝 **CONTRACT** | 仅接口+模型卡，求解器 Phase 4 |
| UNIQUAC | 活度系数 | 📝 **CONTRACT** | 仅接口+模型卡，求解器 Phase 4 |
| Wilson | 活度系数 | 📝 **CONTRACT** | 仅接口+模型卡，求解器 Phase 4 |
| SRK | 状态方程 | 📝 **CONTRACT** | 仅接口+模型卡，后续视需求升级 |

---

## 文件目录结构

```
D:\Codex\
├── thermo_engine\
│   ├── __init__.py                   # 包入口，导出核心类型
│   ├── schemas.py                    # 数据契约（TaskManifest / EquilibriumResult / ModelCard）
│   ├── backends\
│   │   ├── base.py                   # BackendAdapter 抽象基类
│   │   ├── registry.py               # BackendRegistry 注册表
│   │   ├── ideal_raoult.py           # Ideal/Raoult 适配器 [RUNNABLE]
│   │   ├── peng_robinson.py          # Peng-Robinson 适配器 [RUNNABLE]
│   │   ├── contracts\                # 合同层（Phase 4 实现求解器）
│   │   │   ├── nrtl.py               # NRTL 合同适配器 [CONTRACT]
│   │   │   ├── uniqac.py             # UNIQUAC 合同适配器 [CONTRACT]
│   │   │   ├── wilson.py             # Wilson 合同适配器 [CONTRACT]
│   │   │   └── srk.py                # SRK 合同适配器 [CONTRACT]
│   │   └── ai\__init__.py            # AI 模型预留目录（王中硕）
│   ├── params\binary_params.yaml     # 二元交互参数配置
│   ├── tests\test_smoke.py           # 7 个冒烟测试
│   └── examples\                     # 示例 JSON 文件
├── requirements.txt
├── README.md
└── 模型适用范围说明.md
```

---

## 核心用法

```python
from thermo_engine.backends.registry import BackendRegistry
from thermo_engine.schemas import TaskManifest

# 获取注册表
registry = BackendRegistry()

# 方法一：查询可用的模型
models = registry.list_models()
# [{"model_id": "Ideal", "status": "runnable", ...}, ...]

# 方法二：获取模型卡片（适用范围信息）
card = registry.get_model_card("NRTL")
# {"model_id": "NRTL", "limitations": [...], "applicable_systems": [...], ...}

# 方法三：执行计算
manifest = TaskManifest(
    task_type="isobaric_Txy",
    model_id="Ideal",
    components=["benzene", "toluene"],
    pressure=101325.0,
    temperature_range=[353.0, 383.0],
)
adapter = registry.get("Ideal")
result = adapter.calculate(manifest)
print(result.status, result.curve_data)
```

---

## 运行测试

```bash
cd D:\Codex
python -m pytest thermo_engine/tests/ -v
```

---

## 如何扩展（添加新模型）

### 添加传统模型（王中硕）
1. 在 `backends/` 下创建适配器文件（如 `wilson.py`）
2. 继承 `BackendAdapter`，实现 `calculate()` 和 `get_model_card()`
3. 在 `registry.py` 的 `_register_defaults()` 中注册

### 添加 AI 模型（王中硕）
1. 在 `backends/ai/` 下创建适配器文件
2. 继承 `BackendAdapter`，实现 `calculate()`
3. 通过 `register_ai_adapter()` 或 `registry.register()` 注册
4. 接口与纯传统模型完全相同

---

## 与其他模块的对接

| 对接人 | 接口 | 说明 |
|---|---|---|
| 后端 API | `registry.get(model_id).calculate(manifest)` | 直接 Python 调用，返回 EquilibriumResult |
| LLM/Skill | `registry.list_models()` + `get_model_card()` | 获取模型清单和适用范围，做模型选择 |
| 前端 | `registry.list_models()` | 获取模型下拉列表 |
