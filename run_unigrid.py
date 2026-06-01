"""Basic example: run one AC/DC power flow.

The two key lines are:
    case   = load_acdc_case(...)   # load an Excel grid file as an editable table
    result = run_acdc(case)        # run the AC/DC power flow
"""

from pathlib import Path

import pandas as pd

from load_case import load_acdc_case
from acdc_engine import run_acdc
from result_columns import to_df


# Show full tables in the terminal (don't truncate rows/columns).
pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)

here = Path(__file__).resolve().parent

# 1) Load the Excel grid file as a case (table).
#    >>> Change this filename to run your own grid file. <<<
case = load_acdc_case(here / "grids" / "ACDC_matacdc_case24_ieee_rts1996_3zones.xlsx")

# 2) Run the AC/DC power flow.
result = run_acdc(case)

# 3) Build labeled result tables (each column carries its unit).
ac     = to_df(result, "AC_result")
dc     = to_df(result, "DC_result")
branch = to_df(result, "Branch_result")
loss   = to_df(result, "total_loss_table")

# VSC detail tables exist only when the case uses detailed (non-ideal) VSC converters.
has_vsc = "VSC_Bus_result" in result

# 4) Print a short summary.
print("baseMVA             :", round(float(result["baseMVA"]), 4))
print("AC buses / DC buses :", len(ac), "/", len(dc))
print("AC voltage min/max  :", round(ac["VM[pu]"].min(), 4), "/", round(ac["VM[pu]"].max(), 4), "pu")
print("total AC load [MW]  :", round(ac["Load_P[MW]"].sum(), 2))
print("detailed VSC        :", "yes" if has_vsc else "no")

# 5) Print the full result tables (like the MATLAB command window).
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

# 6) Save results as CSV. The first row is the column names with units.
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
