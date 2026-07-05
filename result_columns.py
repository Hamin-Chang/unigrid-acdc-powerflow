"""Column names (with units) for the run_acdc result tables.

Each result from run_acdc is a plain numeric array, so a saved CSV would have
meaningless headers (0, 1, 2, ...). These names give each column a clear label.
Use `to_df(result, key)` to get a labeled DataFrame.

모드에 따라 같은 key라도 열 수가 다르다(AC/DC-only는 하이브리드보다 열이 적거나
다르다). 그래서 일부 key는 {열수: 라벨목록} dict로 두고, to_df가 실제 열 수에
맞는 라벨을 고른다.
    - AC_result   : 13(Hybrid) / 11(AC-only, 변환기주입 toAC_P/Q 없음)
    - DC_result   :  9(Hybrid) /  7(DC-only, VM_norm·toDC_P 없음)
    - Branch_result: 11(Hybrid) / 12(AC-only, 무효손실 2종) / 8(DC-only)
    - total_loss  :  5(AC 포함) / 3(DC-only, 무효분 없음)
"""

import pandas as pd

COLUMNS = {
    "AC_result": {
        13: [
            "Bus", "VM[pu]", "Freq[pu]", "Angle[deg]", "Gen_P[MW]", "Gen_Q[MVAR]",
            "Load_P[MW]", "Load_Q[MVAR]", "toAC_P[MW]", "toAC_Q[MVAR]", "baseKV[kV]",
            "Vmin[pu]", "Vmax[pu]",
        ],
        11: [
            "Bus", "VM[pu]", "Freq[pu]", "Angle[deg]", "Gen_P[MW]", "Gen_Q[MVAR]",
            "Load_P[MW]", "Load_Q[MVAR]", "baseKV[kV]", "Vmin[pu]", "Vmax[pu]",
        ],
    },
    "DC_result": {
        9: [
            "Bus", "VM[pu]", "VM_norm[pu]", "Gen_P[MW]", "Load_P[MW]", "toDC_P[MW]",
            "baseKV[kV]", "Vmin[pu]", "Vmax[pu]",
        ],
        7: [
            "Bus", "VM[pu]", "Gen_P[MW]", "Load_P[MW]", "baseKV[kV]", "Vmin[pu]", "Vmax[pu]",
        ],
    },
    "Branch_result": {
        11: [
            "From", "To", "From_P[MW]", "To_P[MW]", "From_Q[MVAR]", "To_Q[MVAR]",
            "Loss_P[MW]", "Loss_Q[MVAR]", "Capacity[MVA]", "Loading[%]", "Status",
        ],
        12: [
            "From", "To", "From_P[MW]", "To_P[MW]", "From_Q[MVAR]", "To_Q[MVAR]",
            "Loss_P[MW]", "Loss_Q_Qft[MVAR]", "Loss_Q_I2X[MVAR]", "Capacity[MVA]",
            "Loading[%]", "Status",
        ],
        8: [
            "From", "To", "From_P[MW]", "To_P[MW]", "Loss_P[MW]", "Capacity[MVA]",
            "Loading[%]", "Status",
        ],
    },
    "Branch_result_3W": {
        11: [
            "From", "To", "From_P[MW]", "To_P[MW]", "From_Q[MVAR]", "To_Q[MVAR]",
            "Loss_P[MW]", "Loss_Q[MVAR]", "Capacity[MVA]", "Loading[%]", "Status",
        ],
        12: [
            "From", "To", "From_P[MW]", "To_P[MW]", "From_Q[MVAR]", "To_Q[MVAR]",
            "Loss_P[MW]", "Loss_Q_Qft[MVAR]", "Loss_Q_I2X[MVAR]", "Capacity[MVA]",
            "Loading[%]", "Status",
        ],
    },
    "total_loss_table": {
        5: ["Time[h]", "Ploss[W]", "Qloss[Var]", "Ploss[%]", "Qloss[%]"],
        3: ["Time[h]", "Ploss[W]", "Ploss[%]"],
    },
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
    """Return result[key] as a DataFrame whose columns carry unit labels.

    같은 key라도 모드마다 열 수가 다를 수 있으므로, 실제 열 수에 맞는 라벨을
    고른다. 라벨을 못 찾으면(폭 불일치) 라벨 없이 그대로 둔다(에러 안 남).
    """
    df = pd.DataFrame(result[key])
    spec = COLUMNS.get(key)
    cols = None
    if isinstance(spec, dict):
        cols = spec.get(df.shape[1])
    elif isinstance(spec, list):
        if df.shape[1] == len(spec):
            cols = spec
    if cols is not None:
        df.columns = cols
    return df
