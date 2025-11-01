import ast
import math
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = PROJECT_ROOT / "slope_calculator.py"


def load_compute_slope():
    module_ast = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
    for node in module_ast.body:
        if isinstance(node, ast.FunctionDef) and node.name == "compute_slope":
            func_module = ast.Module(body=[node], type_ignores=[])
            ast.fix_missing_locations(func_module)
            namespace = {}
            code_obj = compile(func_module, str(MODULE_PATH), "exec")
            exec(code_obj, namespace)
            return namespace["compute_slope"]
    raise AttributeError("compute_slope function not found in module")


compute_slope = load_compute_slope()


def test_compute_slope_typical_positive_gradient():
    assert math.isclose(compute_slope(10, 2, 4), 20.0)


def test_compute_slope_typical_negative_gradient():
    assert math.isclose(compute_slope(5, 10, 5), -100.0)


def test_compute_slope_zero_distance_returns_infinity():
    assert compute_slope(0, 3, 7) == float("inf")
