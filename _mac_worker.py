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


# 후보 순서대로 탐색: 새 통합 패키지(unigrid_pkg_<os>) 우선, 옛 하이브리드 패키지 fallback.
PACKAGE_CANDIDATES = {
    "Darwin": ("unigrid_pkg_mac", "runpfacdc_pkg_mac"),
    "Windows": ("unigrid_pkg_win", "runpfacdc_pkg_win"),
    "Linux": ("unigrid_pkg_linux", "runpfacdc_pkg_linux"),
}
_HERE = Path(__file__).resolve().parent


def _pick_package() -> str:
    candidates = PACKAGE_CANDIDATES.get(platform.system(), ("unigrid_pkg",))
    for name in candidates:
        if (_HERE / name).is_dir():
            return name
    return candidates[0]


PKG_NAME = _pick_package()
PACKAGE_ROOT = _HERE / PKG_NAME / "for_testing"
sys.path.insert(0, str(PACKAGE_ROOT))


def _fix_apple_silicon_detection() -> None:
    """Restore Apple Silicon detection on hosts where mac_ver() comes back empty.

    The MATLAB-generated package __init__.py decides the architecture with
    ``platform.mac_ver()[-1] == 'arm64'``. On some hosts mac_ver() returns
    ``('', ('', '', ''), '')`` under mwpython: MATLAB puts its own library
    directory first, and an older libexpat shipped there can break pyexpat,
    which breaks plistlib, which is what mac_ver() reads. The empty value
    makes an Apple Silicon Mac look like an Intel one (maci64), which
    contradicts the runtime path (.../runtime/maca64), and the import fails
    before the solver ever starts.

    Fill the machine field from platform.machine() only when it is empty, so
    hosts that report it correctly are left untouched.
    """
    original = platform.mac_ver

    def patched():
        version, dev_stage, machine = original()
        if not machine:
            return (version, dev_stage, platform.machine())
        return (version, dev_stage, machine)

    platform.mac_ver = patched  # type: ignore[assignment]


if platform.system() == "Darwin":
    _fix_apple_silicon_detection()

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
        mode = float(case["mode"])
        entry = getattr(app, "runpf_unigrid_py", None)
        if entry is None:
            entry = getattr(app, "runpfACDC_py", None)
            if entry is not None and int(round(mode)) != 0:
                raise SystemExit(
                    "설치된 패키지는 하이브리드(Mode 0)만 지원합니다. "
                    "AC-only/DC-only는 runpf_unigrid_py로 재컴파일하세요."
                )
        if entry is None:
            raise SystemExit("runpf_unigrid_py / runpfACDC_py 진입점을 찾지 못했습니다.")
        result = entry(
            case["case_name"],
            mode,
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
