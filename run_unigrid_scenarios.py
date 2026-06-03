"""Loop example: run several scenarios and save each result.

This shows how to simulate many scenarios in a loop. Here we scale the AC load
up step by step. Each run's full result tables are saved under
results/scenarios/scenario_<n>/ (the folder name is just an auto number, so you
never have to rename it when you sweep a different parameter), and a one-line
summary of every run is collected in results/scenarios/summary.csv.

Parameters you can edit live in the case tables, for example:
    case.AC_PLoad_dat   # AC load
    case.AC_gen_dat     # AC generators
    case.AC_Line_dat    # AC lines (status / impedance ...)
    case.IC_dat         # AC/DC converter settings
To run a different scenario, change only the line inside the "edit parameter
here" box — the saving code below stays the same.
"""

from pathlib import Path

import pandas as pd

from load_case import load_acdc_case
from acdc_engine import run_acdc
from result_columns import to_df


here = Path(__file__).resolve().parent

# >>> Change this filename to run your own grid file. <<<
excel = here / "grids" / "ACDC_matacdc_case24_ieee_rts1996_3zones.xlsx"

scenarios = [1.0, 1.1, 1.2, 1.3]   # values to try

# result tables saved in each scenario folder (key -> file name).
# VSC tables are written only when the grid has converters.
SAVE = {
    "AC_result": "AC_result.csv",
    "DC_result": "DC_result.csv",
    "Branch_result": "Branch_result.csv",
    "total_loss_table": "total_loss.csv",
    "VSC_Bus_result": "VSC_Bus_result.csv",
    "VSC_GridPower_result": "VSC_GridPower_result.csv",
    "VSC_Power_result": "VSC_Power_result.csv",
}

out_root = here / "results" / "scenarios"
summary = []

for i, value in enumerate(scenarios, start=1):
    case = load_acdc_case(excel)          # start from a clean case each time

    # --- edit parameter here (now: scale the AC load by `value`) ------
    case.AC_PLoad_dat.iloc[:, 1:] *= value
    case.AC_QLoad_dat.iloc[:, 1:] *= value
    # --- to change generators/lines instead, edit that table above ----

    result = run_acdc(case)

    # save this run's full result tables (folder name = auto number)
    out = out_root / f"scenario_{i}"
    out.mkdir(parents=True, exist_ok=True)
    for key, fname in SAVE.items():
        if key in result:
            to_df(result, key).to_csv(out / fname, index=False)

    min_vm = to_df(result, "AC_result")["VM[pu]"].min()
    summary.append({"scenario": i, "value": value, "min_VM[pu]": round(float(min_vm), 4)})
    print(f"scenario_{i}  (value={value})  ->  min voltage {min_vm:.4f} pu  ->  {out}")

# one row per scenario, so you remember which number was which value
pd.DataFrame(summary).to_csv(out_root / "summary.csv", index=False)
print(f"\nsummary saved to  {out_root / 'summary.csv'}")
