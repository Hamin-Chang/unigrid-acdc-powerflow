"""run_acdc.py — AC/DC 하이브리드 조류계산 실행 (OS 자동 분기 + OS별 패키지 자동 선택)

사용법은 OS와 무관하게 동일하다:

    from load_case import load_acdc_case
    from run_acdc import run_acdc
    case = load_acdc_case("grids/ACDC_matacdc_case24_ieee_rts1996_3zones.xlsx")
    result = run_acdc(case)

컴파일된 MATLAB 패키지는 OS마다 따로 만들어야 하므로(한 패키지로 Mac+Windows 불가),
OS별로 다른 폴더/모듈 이름을 둔다. 내보낸 함수 이름(runpfACDC_py)은 동일하다.
  - macOS   : runpfacdc_pkg_mac   (개발/테스트, mwpython 경유)
  - Windows : runpfacdc_pkg_win   (배포, 직접 import)
  - Linux   : runpfacdc_pkg_linux
"""

from __future__ import annotations

import importlib
import json
import os
import platform
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from load_case import ACDCCase, TABLE_ORDER


_HERE = Path(__file__).resolve().parent

# OS → 컴파일 패키지 폴더/모듈 이름 (후보 순서대로 탐색: 새 이름 우선, 옛 이름 fallback).
# 새 통합 패키지 이름은 unigrid_pkg_<os> (runpf_unigrid_py 진입점, 전 모드).
# 옛 하이브리드 전용 패키지(runpfacdc_pkg_<os>)가 남아 있으면 그것도 인식한다.
PACKAGE_CANDIDATES = {
    "Darwin": ("unigrid_pkg_mac", "runpfacdc_pkg_mac"),
    "Windows": ("unigrid_pkg_win", "runpfacdc_pkg_win"),
    "Linux": ("unigrid_pkg_linux", "runpfacdc_pkg_linux"),
}

WORKER = _HERE / "_mac_worker.py"
DEFAULT_MWPYTHON = Path("/Applications/MATLAB_R2024b.app/bin/mwpython")


def _package_name() -> str:
    candidates = PACKAGE_CANDIDATES.get(platform.system(), ("unigrid_pkg",))
    for name in candidates:
        if (_HERE / name).is_dir():
            return name
    return candidates[0]


def _package_dir() -> Path:
    return _HERE / _package_name() / "for_testing"


def run_acdc(
    case: ACDCCase,
    *,
    backend: str = "auto",
    mwpython: str | Path | None = None,
) -> dict[str, Any]:
    """ACDC 조류계산을 실행하고 결과(dict)를 반환한다.

    backend: "auto"(기본) / "in_process"(Windows) / "mwpython"(macOS)
    """
    chosen = _resolve_backend(backend)
    if chosen == "in_process":
        return _run_in_process(case)
    return _run_via_mwpython(case, mwpython)


# ── backend 선택 ──────────────────────────────────────────
def _resolve_backend(backend: str) -> str:
    if backend in ("in_process", "mwpython"):
        return backend
    if backend != "auto":
        raise ValueError(
            f"backend must be 'auto', 'in_process', or 'mwpython' (got {backend!r})."
        )
    system = platform.system()
    if system == "Windows":
        return "in_process"
    if system == "Darwin":
        return "mwpython"
    return "in_process" if _in_process_available() else "mwpython"


def _in_process_available() -> bool:
    _ensure_pkg_on_path()
    try:
        importlib.import_module(_package_name())  # 패키지를 먼저 import해야 matlab 경로가 잡힘
        import matlab  # noqa: F401
    except Exception:
        return False
    return True


def _ensure_pkg_on_path() -> None:
    pkg_dir = str(_package_dir())
    if pkg_dir not in sys.path:
        sys.path.insert(0, pkg_dir)


# ── (1) 직접 import 방식 — Windows 배포용 ──────────────────
def _run_in_process(case: ACDCCase) -> dict[str, Any]:
    _ensure_pkg_on_path()
    pkg_name = _package_name()
    try:
        pkg = importlib.import_module(pkg_name)  # 먼저 패키지를 import해야 matlab 경로가 잡힘
        import matlab
    except Exception as exc:  # pragma: no cover
        raise RuntimeError(
            f"컴파일된 ACDC 패키지({pkg_name})를 import하지 못했습니다.\n"
            f"- 패키지 경로: {_package_dir()}\n"
            f"- 이 OS({platform.system()})에 맞게 컴파일된 {pkg_name}와 동일 버전의 "
            "MATLAB Runtime이 설치돼 있어야 합니다."
        ) from exc

    app = pkg.initialize()
    try:
        args = [_to_matlab_matrix(case.tables[name]) for name in TABLE_ORDER]
        entry = _resolve_entry(app, case.mode)
        result = entry(
            case.case_name,
            float(case.mode),
            *args,
            nargout=1,
        )
    finally:
        app.terminate()

    return _matlab_result_to_jsonable(result)


def _resolve_entry(app: Any, mode: float) -> Any:
    """컴파일 패키지에서 진입점 함수를 고른다.

    새 패키지(runpf_unigrid_py)면 전 모드 지원. 구 패키지(runpfACDC_py)만
    있으면 하이브리드(Mode 0)만 가능하므로 그 외 모드는 재컴파일을 안내한다.
    """
    fn = getattr(app, "runpf_unigrid_py", None)
    if fn is not None:
        return fn
    fn = getattr(app, "runpfACDC_py", None)
    if fn is not None:
        if int(round(mode)) != 0:
            raise RuntimeError(
                "설치된 컴파일 패키지는 하이브리드(Mode 0)만 지원합니다(runpfACDC_py).\n"
                "AC-only/DC-only(.m/.raw 포함)를 실행하려면 runpf_unigrid_py로 재컴파일하세요."
            )
        return fn
    raise RuntimeError(
        "컴파일 패키지에서 runpf_unigrid_py 또는 runpfACDC_py를 찾지 못했습니다."
    )


def _to_matlab_matrix(table: Any) -> Any:
    import matlab

    values = table.astype(float).to_numpy().tolist()
    if not values:
        return matlab.double([])
    return matlab.double(values)


def _matlab_result_to_jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: _matlab_result_to_jsonable(v) for k, v in value.items()}
    if hasattr(value, "tolist"):
        return value.tolist()
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, (list, tuple)):
        return [_matlab_result_to_jsonable(v) for v in value]
    try:
        return float(value)
    except (TypeError, ValueError):
        text = str(value)
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return text


# ── (2) mwpython 서브프로세스 — macOS 테스트용 ─────────────
def _run_via_mwpython(case: ACDCCase, mwpython: str | Path | None) -> dict[str, Any]:
    mw = Path(mwpython or os.environ.get("MWPYTHON") or DEFAULT_MWPYTHON)
    if not Path(mw).exists():
        raise RuntimeError(
            f"mwpython을 찾을 수 없습니다: {mw}\n"
            "- MATLAB(또는 Runtime) 경로를 확인하거나 환경변수 MWPYTHON / "
            "run_acdc(case, mwpython=...) 로 지정하세요."
        )

    with tempfile.TemporaryDirectory(prefix="run_acdc_") as tmp:
        tmp_dir = Path(tmp)
        input_path = tmp_dir / "case.json"
        output_path = tmp_dir / "result.json"
        input_path.write_text(json.dumps(_case_to_jsonable(case)), encoding="utf-8")

        command = [str(mw), str(WORKER), str(input_path), str(output_path)]
        env = os.environ.copy()
        # mwpython needs a Python 3.9-3.12 venv. Prefer the project's .venv (made by
        # setup_mac.sh) so it works even if this script was launched with a different
        # or unsupported Python (e.g. 3.13/3.14 from a VS Code Run button).
        local_venv = _HERE / ".venv"
        if (local_venv / "bin" / "python").exists():
            env["VIRTUAL_ENV"] = str(local_venv)
        else:
            env.setdefault("VIRTUAL_ENV", sys.prefix)
        completed = subprocess.run(
            command, cwd=_HERE, env=env, text=True, capture_output=True, check=False
        )
        if completed.returncode != 0:
            raise RuntimeError(
                "run_acdc worker failed.\n"
                f"STDOUT:\n{completed.stdout}\n"
                f"STDERR:\n{completed.stderr}"
            )
        return json.loads(output_path.read_text(encoding="utf-8"))


def _case_to_jsonable(case: ACDCCase) -> dict[str, Any]:
    return {
        "case_name": case.case_name,
        "mode": case.mode,
        "tables": {
            name: case.tables[name].astype(float).to_numpy().tolist()
            for name in TABLE_ORDER
        },
    }
