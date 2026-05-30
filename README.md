# UniGrid — ACDC Power Flow (Python)

**UniGrid** is an AC/DC hybrid power flow solver, compiled from MATLAB and callable
from Python. You load a grid from Excel as an editable table, then run the power flow.
Works on both Windows and macOS (the matching compiled package is selected
automatically).

> **You only run the `run_unigrid*.py` scripts.** Everything else is the engine.

```python
from load_case import load_acdc_case
from acdc_engine import run_acdc

case   = load_acdc_case("grids/ACDC_matacdc_case24_ieee_rts1996_3zones.xlsx")   # load Excel as a table
result = run_acdc(case)                                      # run the power flow
```

## Requirements

- **MATLAB Runtime R2024b** for your OS (free). If full MATLAB R2024b is installed,
  it is already included. Otherwise download it from
  https://www.mathworks.com/products/compiler/matlab-runtime.html
- **Python 3.9 – 3.12** (3.13+ is not supported by the package).
- Python packages: `pandas`, `openpyxl`.

## Setup & run

### Windows
```bat
py -m pip install .\runpfacdc_pkg_win\for_redistribution_files_only
py -m pip install pandas openpyxl
py run_unigrid.py
```

### macOS
(Requires MATLAB R2024b, which provides `mwpython`.)
```bash
python3 -m pip install pandas openpyxl
python3 run_unigrid.py
```

A successful run prints a short summary (baseMVA, bus counts, voltage min/max,
total load) and saves result CSV files under `results/`.

## The two scripts you run

- **`run_unigrid.py`** — basic run: load a grid, run the power flow, print/save results.
- **`run_unigrid_scenarios.py`** — a **template you adapt yourself**. It shows the
  pattern for building your own study (change a parameter, run it in a `for` loop);
  edit it to fit your own scenarios rather than using it as-is.

## Using your own grid

Replace the Excel filename in the script, or pass your own file:
```python
case = load_acdc_case("my_grid.xlsx")
```
The Excel file must have the same sheet layout as the grids in `grids/`.

## Editing parameters (scenarios)

After loading, the grid lives in editable tables. Change them, then run again:
```python
case = load_acdc_case("grids/ACDC_matacdc_case24_ieee_rts1996_3zones.xlsx")
case.AC_PLoad_dat.iloc[:, 1:] *= 1.10   # +10% AC load
result = run_acdc(case)
```
Other tables you can edit: `AC_gen_dat` (generators), `AC_Line_dat` (lines),
`IC_dat` (AC/DC converters), `DC_PLoad_dat` (DC load), and more.

## Example grids (`grids/`)

Six AC/DC test systems used in the paper, across three scales:

| Grid file | Category | AC / DC buses |
|-----------|----------|---------------|
| `ACDC_matacdc_case24_ieee_rts1996_3zones.xlsx` | Transmission | 50 / 7 |
| `ACDC_matacdc_stagg5_droop.xlsx` | Transmission | 5 / 3 |
| `ACDC_CIGRE_Benchmark.xlsx` | Distribution | 14 / 11 |
| `ACDC_91bus_regional_distribution.xlsx` | Distribution | 91 / 3 |
| `ACDC_71bus_3IC_parallel.xlsx` | Microgrid | 38 / 33 |
| `ACDC_12bus_paper.xlsx` | Microgrid | 6 / 6 |

To run another grid, just point to it:
```python
case = load_acdc_case("grids/ACDC_CIGRE_Benchmark.xlsx")
result = run_acdc(case)
```

## Files

| File | Role |
|------|------|
| **`run_unigrid.py`** | ▶ Run one power flow (start here) |
| **`run_unigrid_scenarios.py`** | ▶ Run a loop of scenarios |
| `load_case.py` | Engine: load Excel into editable tables |
| `acdc_engine.py` | Engine: run the power flow (auto-selects the OS package) |
| `_mac_worker.py` | Internal helper used on macOS only |
| `grids/` | Example grids (Excel) |
| `runpfacdc_pkg_win/` | Compiled solver for Windows |
| `runpfacdc_pkg_mac/` | Compiled solver for macOS |
