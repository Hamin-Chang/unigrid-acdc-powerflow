"""Basic example: run one AC/DC power flow.

The two key lines are:
    case   = load_acdc_case(...)   # load an Excel grid file as an editable table
    result = run_acdc(case)        # run the AC/DC power flow
"""

from pathlib import Path

import pandas as pd

from load_case import load_acdc_case
from acdc_engine import run_acdc


here = Path(__file__).resolve().parent

# 1) Load the Excel grid file as a case (table).
#    >>> Change this filename to run your own grid file. <<<
case = load_acdc_case(here / "grids" / "ACDC_matacdc_case24_ieee_rts1996_3zones.xlsx")

# 2) Run the AC/DC power flow.
result = run_acdc(case)

# 3) Print a short summary.  (AC_result columns: 1=voltage[pu], 4=gen[MW], 6=load[MW])
ac = pd.DataFrame(result["AC_result"])
print("baseMVA             :", round(float(result["baseMVA"]), 4))
print("AC buses / DC buses :", len(result["AC_result"]), "/", len(result["DC_result"]))
print("AC voltage min/max  :", round(ac[1].min(), 4), "/", round(ac[1].max(), 4), "pu")
print("total AC load [MW]  :", round(ac[6].sum(), 2))

# 4) (optional) Save full results as CSV files.
out = here / "results" / "runACDC_ex"
out.mkdir(parents=True, exist_ok=True)
pd.DataFrame(result["AC_result"]).to_csv(out / "AC_result.csv", index=False)
pd.DataFrame(result["DC_result"]).to_csv(out / "DC_result.csv", index=False)
pd.DataFrame(result["Branch_result"]).to_csv(out / "Branch_result.csv", index=False)
print("results saved to    :", out)
