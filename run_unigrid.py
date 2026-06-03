"""UniGrid — run one AC/DC power flow.

HOW TO USE: edit the SETTINGS block below, then press Run (the ▶ button).
"""

from pathlib import Path

import pandas as pd

from load_case import load_acdc_case
from acdc_engine import run_acdc
from result_columns import to_df


# ════════════════════════════════════════════════════════════════
#  SETTINGS  —  edit here, then press Run (▶)
# ════════════════════════════════════════════════════════════════

# 1) Pick a grid: keep ONE line without the leading "#".
GRID = "grids/ACDC_matacdc_case24_ieee_rts1996_3zones.xlsx"   # transmission  50/7
# GRID = "grids/ACDC_matacdc_stagg5_droop.xlsx"               # transmission   5/3
# GRID = "grids/ACDC_CIGRE_Benchmark.xlsx"                    # distribution  14/11
# GRID = "grids/ACDC_91bus_regional_distribution.xlsx"        # distribution  91/3
# GRID = "grids/ACDC_71bus_3IC_parallel.xlsx"                 # microgrid     38/33
# GRID = "grids/ACDC_12bus_paper.xlsx"                        # microgrid      6/6
# GRID = "grids/your_own_file.xlsx"                           # your own grid

# 2) (optional) Finer tweaks: edit the Excel file directly, or add lines such as
#       case.AC_gen_dat.iloc[0, 5] *= 1.2          # +20% on the first generator
#    just below where `case` is loaded (see "apply settings" section).
# ════════════════════════════════════════════════════════════════


here = Path(__file__).resolve().parent
pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)

# ── Load the grid, (optionally edit), run ───────────────────────
case = load_acdc_case(here / GRID)

# (optional) edit the case here, e.g.  case.AC_gen_dat.iloc[0, 5] *= 1.2

result = run_acdc(case)

# ── Build labeled result tables ─────────────────────────────────
ac     = to_df(result, "AC_result")
dc     = to_df(result, "DC_result")
branch = to_df(result, "Branch_result")
loss   = to_df(result, "total_loss_table")
has_vsc = "VSC_Bus_result" in result

# ── Summary ─────────────────────────────────────────────────────
print("grid                :", GRID)
print("baseMVA             :", round(float(result["baseMVA"]), 4))
print("AC buses / DC buses :", len(ac), "/", len(dc))
print("AC voltage min/max  :", round(ac["VM[pu]"].min(), 4), "/", round(ac["VM[pu]"].max(), 4), "pu")
print("total AC load [MW]  :", round(ac["Load_P[MW]"].sum(), 2))
print("detailed VSC        :", "yes" if has_vsc else "no")

# ── Full result tables (like the MATLAB command window) ─────────
print("\n===== AC bus result =====")
print(ac.to_string(index=False))
print("\n===== DC bus result =====")
print(dc.to_string(index=False))
print("\n===== Branch (line) result =====")
print(branch.to_string(index=False))
print("\n===== Total loss =====")
print(loss.to_string(index=False))

if has_vsc:
    vsc_bus  = to_df(result, "VSC_Bus_result")
    vsc_grid = to_df(result, "VSC_GridPower_result")
    vsc_pow  = to_df(result, "VSC_Power_result")
    print("\n===== VSC bus result =====")
    print(vsc_bus.to_string(index=False))
    print("\n===== VSC grid power =====")
    print(vsc_grid.to_string(index=False))
    print("\n===== VSC power / losses =====")
    print(vsc_pow.to_string(index=False))

# ── Save CSV (first row = unit-labeled headers) ─────────────────
out = here / "results" / "runACDC_ex"
out.mkdir(parents=True, exist_ok=True)
ac.to_csv(out / "AC_result.csv", index=False)
dc.to_csv(out / "DC_result.csv", index=False)
branch.to_csv(out / "Branch_result.csv", index=False)
loss.to_csv(out / "total_loss.csv", index=False)
if has_vsc:
    vsc_bus.to_csv(out / "VSC_Bus_result.csv", index=False)
    vsc_grid.to_csv(out / "VSC_GridPower_result.csv", index=False)
    vsc_pow.to_csv(out / "VSC_Power_result.csv", index=False)
print("\nresults saved to    :", out)
