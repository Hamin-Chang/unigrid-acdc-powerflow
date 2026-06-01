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

Use the helper scripts. They pick a supported Python (3.9–3.12), install
dependencies, and run the example. **Python 3.13+ is not supported** by the MATLAB
Runtime, so the scripts will find or install Python 3.12 for you.

### macOS
```bash
bash setup_mac.sh      # one-time: creates a Python 3.12 venv and installs deps
bash run_mac.sh        # run the power flow
```
(If Python 3.12 is missing, `setup_mac.sh` installs it via Homebrew.)

### Windows
```bat
setup_windows.bat      :: one-time: installs the package and deps
run_windows.bat        :: run the power flow
```
(Double-click the `.bat` files in Explorer, or run them from a terminal.)

A successful run prints the result tables (AC / DC / branch / VSC) and saves CSV
files under `results/`.

<details><summary>Manual setup (without the scripts)</summary>

macOS (needs a Python 3.9–3.12 venv — mwpython requires a real venv):
```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install pandas openpyxl
.venv/bin/python run_unigrid.py
```
Windows:
```bat
py -m pip install .\runpfacdc_pkg_win\for_redistribution_files_only
py -m pip install pandas openpyxl
py run_unigrid.py
```
</details>

## Run from your editor (the easy way)

1. Run setup once (`bash setup_mac.sh` on macOS / `setup_windows.bat` on Windows).
2. Open this folder in your editor (e.g. VS Code: File → Open Folder).
   On macOS, VS Code auto-uses the `.venv` created by setup.
3. Open **`run_unigrid.py`**, edit the **SETTINGS** block at the top, press **Run (▶)**.

The SETTINGS block lets you, without touching the rest of the code:
- **pick a grid** — uncomment one `GRID = ...` line,
- **scale the load** — set `LOAD_SCALE` (e.g. `1.10` for +10%).

```python
# 1) Pick a grid: keep ONE line without the leading "#".
GRID = "grids/ACDC_matacdc_case24_ieee_rts1996_3zones.xlsx"
# GRID = "grids/ACDC_CIGRE_Benchmark.xlsx"
# ...

# 2) (optional) Scale all AC loads. 1.0 = no change, 1.1 = +10%.
LOAD_SCALE = 1.0
```

## Changing settings in more detail

- **Different grid** → change the `GRID` line in `run_unigrid.py`, or use your own
  `.xlsx` (same sheet layout as the files in `grids/`).
- **Loads / generators / lines** → easiest is to **open the grid's Excel file and edit
  the numbers** (that file *is* the input). For code-based tweaks, add lines after the
  case is loaded, e.g. `case.AC_gen_dat.iloc[0, 5] *= 1.2`. Editable tables include
  `AC_PLoad_dat`, `AC_gen_dat`, `AC_Line_dat`, `IC_dat`, `DC_PLoad_dat`, and more.
- **Many scenarios at once** → see `run_unigrid_scenarios.py` (a template that loops
  over parameter values; adapt it to your study).

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
| **`setup_mac.sh` / `setup_windows.bat`** | One-time setup (Python + deps) |
| **`run_mac.sh` / `run_windows.bat`** | Run the power flow |
| `run_unigrid.py` | The basic example the run scripts call |
| `run_unigrid_scenarios.py` | Loop / scenario example (a template to adapt) |
| `load_case.py` | Engine: load Excel into editable tables |
| `acdc_engine.py` | Engine: run the power flow (auto-selects the OS package) |
| `_mac_worker.py` | Internal helper used on macOS only |
| `grids/` | Example grids (Excel) |
| `runpfacdc_pkg_win/` | Compiled solver for Windows |
| `runpfacdc_pkg_mac/` | Compiled solver for macOS |
