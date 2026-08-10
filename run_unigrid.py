"""UniGrid — run one power flow (AC/DC Hybrid, AC-only, or DC-only).

HOW TO USE: edit the SETTINGS block below, then press Run (the ▶ button).
The grid file may be a UniGrid Excel (.xlsx), a MATPOWER m-file (.m), or a
PSS/E raw file (.raw); the mode (Hybrid / AC-only / DC-only) is detected
automatically from the file.
"""

from pathlib import Path

import pandas as pd

from load_case import load_case
from acdc_engine import run_acdc
from result_columns import to_df


# ════════════════════════════════════════════════════════════════
#  SETTINGS  —  edit here, then press Run (▶)
# ════════════════════════════════════════════════════════════════

# 1) Pick a grid: keep ONE line without the leading "#".
#    The first block is the paper's case files, one line per scenario.
GRID = "grids/rts96_scenario1_constant_vdc.xlsx"     # AC/DC Hybrid  50/7
# GRID = "grids/rts96_scenario2_droop.xlsx"          # AC/DC Hybrid  50/7
# GRID = "grids/cigre_scenario1_constant_vdc.xlsx"   # AC/DC Hybrid  14/11
# GRID = "grids/cigre_scenario2_droop.xlsx"          # AC/DC Hybrid  14/11
# GRID = "grids/mg71_S1_baseline.xlsx"               # AC/DC Hybrid  38/33
# GRID = "grids/mg71_S2_deadband.xlsx"               # AC/DC Hybrid  38/33
# GRID = "grids/mg71_S3_gen_qlimit.xlsx"             # AC/DC Hybrid  38/33
# GRID = "grids/mg71_S4_ic_limit.xlsx"               # AC/DC Hybrid  38/33
# GRID = "grids/pandapower_3w.xlsx"                  # UniGrid Excel → AC-only, 3-winding
#    Other examples.
# GRID = "grids/stagg5_scenario1_constant_vdc.xlsx"  # AC/DC Hybrid   5/3
# GRID = "grids/stagg5_scenario2_droop.xlsx"         # AC/DC Hybrid   5/3
# GRID = "grids/matpower_ieee14.m"                   # MATPOWER  → AC-only
# GRID = "grids/matpower_ieee118.m"                  # MATPOWER  → AC-only
# GRID = "grids/psse_ieee14.raw"                     # PSS/E     → AC-only
# GRID = "grids/psse_ieee118.raw"                    # PSS/E     → AC-only
# GRID = "grids/psse_3w_sample.raw"                  # PSS/E, 3-winding → AC-only
# GRID = "grids/your_own_file.xlsx"                  # your own grid

# 2) (optional) Finer tweaks: edit the file directly, or add lines such as
#       case.AC_gen_dat.iloc[0, 5] *= 1.2          # +20% on the first generator
#    just below where `case` is loaded (see "apply settings" section).
# ════════════════════════════════════════════════════════════════


here = Path(__file__).resolve().parent
pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)

# ── Load the grid (Excel / MATPOWER .m / PSS/E .raw), (optionally edit), run ──
grid_path = GRID if Path(GRID).is_absolute() else here / GRID
case = load_case(grid_path)

# (optional) edit the case here, e.g.  case.AC_gen_dat.iloc[0, 5] *= 1.2

result = run_acdc(case)

# ── Which sections does this result carry? (mode-dependent) ─────
has_ac = "AC_result" in result and len(result["AC_result"]) > 0
has_dc = "DC_result" in result and len(result["DC_result"]) > 0
has_vsc = "VSC_Bus_result" in result
mode = int(round(float(result.get("mode", 0 if has_dc and has_ac else (1 if has_ac else 2)))))
mode_name = {0: "AC/DC Hybrid", 1: "AC-only", 2: "DC-only"}.get(mode, "?")

branch = to_df(result, "Branch_result")
loss = to_df(result, "total_loss_table")
ac = to_df(result, "AC_result") if has_ac else None
dc = to_df(result, "DC_result") if has_dc else None

# ── Summary ─────────────────────────────────────────────────────
print("grid                :", GRID)
print("mode                :", mode_name)
print("baseMVA             :", round(float(result["baseMVA"]), 4))
if has_ac:
    print("AC buses            :", len(ac))
    print("AC voltage min/max  :", round(ac["VM[pu]"].min(), 4), "/", round(ac["VM[pu]"].max(), 4), "pu")
    print("total AC load [MW]  :", round(ac["Load_P[MW]"].sum(), 2))
if has_dc:
    print("DC buses            :", len(dc))
    print("DC voltage min/max  :", round(dc["VM[pu]"].min(), 4), "/", round(dc["VM[pu]"].max(), 4), "pu")
print("detailed VSC        :", "yes" if has_vsc else "no")

# ── Full result tables (like the MATLAB command window) ─────────
if has_ac:
    print("\n===== AC bus result =====")
    print(ac.to_string(index=False))
if has_dc:
    print("\n===== DC bus result =====")
    print(dc.to_string(index=False))
print("\n===== Branch (line) result =====")
print(branch.to_string(index=False))
print("\n===== Total loss =====")
print(loss.to_string(index=False))

if has_vsc:
    vsc_bus = to_df(result, "VSC_Bus_result")
    vsc_grid = to_df(result, "VSC_GridPower_result")
    vsc_pow = to_df(result, "VSC_Power_result")
    print("\n===== VSC bus result =====")
    print(vsc_bus.to_string(index=False))
    print("\n===== VSC grid power =====")
    print(vsc_grid.to_string(index=False))
    print("\n===== VSC power / losses =====")
    print(vsc_pow.to_string(index=False))

# ── Save CSV (first row = unit-labeled headers) ─────────────────
out = here / "results" / "runUniGrid_ex"
out.mkdir(parents=True, exist_ok=True)
if has_ac:
    ac.to_csv(out / "AC_result.csv", index=False)
if has_dc:
    dc.to_csv(out / "DC_result.csv", index=False)
branch.to_csv(out / "Branch_result.csv", index=False)
loss.to_csv(out / "total_loss.csv", index=False)
if has_vsc:
    vsc_bus.to_csv(out / "VSC_Bus_result.csv", index=False)
    vsc_grid.to_csv(out / "VSC_GridPower_result.csv", index=False)
    vsc_pow.to_csv(out / "VSC_Power_result.csv", index=False)
print("\nresults saved to    :", out)
