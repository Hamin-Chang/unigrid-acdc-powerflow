"""Column names (with units) for the run_acdc result tables.

Each result from run_acdc is a plain numeric array, so a saved CSV would have
meaningless headers (0, 1, 2, ...). These names give each column a clear label
with its unit. Use `to_df(result, key)` to get a labeled DataFrame.
"""

import pandas as pd

COLUMNS = {
    "AC_result": [
        "Bus", "VM[pu]", "Freq[pu]", "Angle[deg]", "Gen_P[MW]", "Gen_Q[MVAR]",
        "Load_P[MW]", "Load_Q[MVAR]", "toAC_P[MW]", "toAC_Q[MVAR]", "baseKV[kV]",
        "Vmin[pu]", "Vmax[pu]",
    ],
    "DC_result": [
        "Bus", "VM[pu]", "VM_norm[pu]", "Gen_P[MW]", "Load_P[MW]", "toDC_P[MW]",
        "baseKV[kV]", "Vmin[pu]", "Vmax[pu]",
    ],
    "Branch_result": [
        "From", "To", "From_P[MW]", "To_P[MW]", "From_Q[MVAR]", "To_Q[MVAR]",
        "Loss_P[MW]", "Loss_Q[MVAR]", "Capacity[MVA]", "Loading[%]", "Status",
    ],
    "Branch_result_3W": [
        "From", "To", "From_P[MW]", "To_P[MW]", "From_Q[MVAR]", "To_Q[MVAR]",
        "Loss_P[MW]", "Loss_Q[MVAR]", "Capacity[MVA]", "Loading[%]", "Status",
    ],
    "total_loss_table": ["Time[h]", "Ploss[W]", "Qloss[Var]", "Ploss[%]", "Qloss[%]"],
    "Line_loading_percent": ["Loading[%]"],
    "VSC_Bus_result": [
        "BusAC", "BusDC", "VSC_VM[pu]", "VSC_Angle[deg]", "Inj_P[MW]", "Inj_Q[MVAR]", "Loss[MW]",
    ],
    "VSC_GridPower_result": [
        "BusAC", "BusDC", "Grid_P[MW]", "Grid_Q[MVAR]", "TrafFilter_P[MW]", "TrafFilter_Q[MVAR]",
        "Filter_Q[MVAR]", "VSCFilter_Q[MVAR]", "VSC_P[MW]", "VSC_Q[MVAR]",
    ],
    "VSC_Power_result": [
        "BusAC", "BusDC", "VSC_P[MW]", "VSC_Q[MVAR]", "Filter_Q[MVAR]",
        "TransfoLoss_P[MW]", "TransfoLoss_Q[MVAR]", "ReactorLoss_P[MW]", "ReactorLoss_Q[MVAR]", "VSCLoss_P[MW]",
    ],
}


def to_df(result, key):
    """Return result[key] as a DataFrame whose columns carry units.

    Falls back to default columns if the width doesn't match (so it never errors).
    """
    df = pd.DataFrame(result[key])
    cols = COLUMNS.get(key)
    if cols is not None and df.shape[1] == len(cols):
        df.columns = cols
    return df
