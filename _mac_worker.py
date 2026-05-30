"""run_acdc_worker.py — macOS에서 mwpython으로 실행되는 ACDC 워커.

run_acdc.py(_run_via_mwpython)가 case.json을 만들고 이 워커를 mwpython으로
호출한다. 워커는 OS에 맞는 컴파일 패키지를 import해 runpfACDC_py를 실행한다.
"""

from __future__ import annotations

import importlib
import json
import platform
import sys
from pathlib import Path
from typing import Any


PACKAGE_NAMES = {
    "Darwin": "runpfacdc_pkg_mac",
    "Windows": "runpfacdc_pkg_win",
    "Linux": "runpfacdc_pkg_linux",
}
PKG_NAME = PACKAGE_NAMES.get(platform.system(), "runpfacdc_pkg")
PACKAGE_ROOT = Path(__file__).resolve().parent / PKG_NAME / "for_testing"
sys.path.insert(0, str(PACKAGE_ROOT))

pkg = importlib.import_module(PKG_NAME)
import matlab  # type: ignore


# runpfACDC_py.m 인자 순서
TABLE_ORDER = (
    "Base_dat", "AC_Bus_dat", "AC_Line_dat", "AC_gen_dat", "AC_3wtrans_dat",
    "DC_Bus_dat", "DC_Line_dat", "DC_gen_dat", "IC_dat", "DCDC_Conv_dat",
    "AC_PLoad_dat", "AC_QLoad_dat", "DC_PLoad_dat",
)


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("Usage: run_acdc_worker.py input_case.json output_result.json")

    case = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    tables = case["tables"]

    app = pkg.initialize()
    try:
        args = [_matrix(tables[name]) for name in TABLE_ORDER]
        result = app.runpfACDC_py(
            case["case_name"],
            float(case["mode"]),
            *args,
            nargout=1,
        )
    finally:
        app.terminate()

    Path(sys.argv[2]).write_text(json.dumps(_to_jsonable(result)), encoding="utf-8")


def _matrix(values: list[list[float]]) -> Any:
    if not values:
        return matlab.double([])
    return matlab.double(values)


def _to_jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: _to_jsonable(v) for k, v in value.items()}
    if hasattr(value, "tolist"):
        return value.tolist()
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, (list, tuple)):
        return [_to_jsonable(v) for v in value]
    try:
        return float(value)
    except (TypeError, ValueError):
        text = str(value)
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return text


if __name__ == "__main__":
    main()
