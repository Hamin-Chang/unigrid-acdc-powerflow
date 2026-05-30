"""Loop example: run several scenarios by changing a parameter each time.

This shows how to simulate many scenarios in a loop. Here we scale the AC load
up step by step and check the lowest bus voltage in each run.

Parameters you can edit live in the case tables, for example:
    case.AC_PLoad_dat   # AC load
    case.AC_gen_dat     # AC generators
    case.AC_Line_dat    # AC lines (status / impedance ...)
    case.IC_dat         # AC/DC converter settings
To run a different scenario, change the line inside the "edit parameter here" box.
"""

from pathlib import Path

import pandas as pd

from load_case import load_acdc_case
from acdc_engine import run_acdc


# >>> Change this filename to run your own grid file. <<<
excel = Path(__file__).resolve().parent / "grids" / "ACDC_matacdc_case24_ieee_rts1996_3zones.xlsx"

scenarios = [1.0, 1.1, 1.2, 1.3]   # load scale factors to try

for scale in scenarios:
    case = load_acdc_case(excel)          # start from a clean case each time

    # --- edit parameter here (now: scale the AC load) -----------------
    case.AC_PLoad_dat.iloc[:, 1:] *= scale
    case.AC_QLoad_dat.iloc[:, 1:] *= scale
    # --- to change generators/lines instead, edit that table above ----

    result = run_acdc(case)
    min_vm = pd.DataFrame(result["AC_result"])[1].min()   # column 1 = voltage [pu]
    print(f"load x{scale:.1f}  ->  min voltage {min_vm:.4f} pu")
