# UniGrid — ACDC Power Flow (Python)

**UniGrid** is an AC/DC hybrid power flow solver, compiled from MATLAB and callable
from Python. You load a grid from Excel as an editable table, then run the power flow.
Works on both Windows and macOS (the matching compiled package is selected
automatically).

## Quick start

**1. One-time setup** (finds/installs Python 3.12 and the dependencies):

- **macOS** — in a terminal, from this folder: `bash setup_mac.sh`
- **Windows** — double-click `setup_windows.bat`

**2. Open this folder** in your editor (VS Code: File → Open Folder).
On macOS it auto-uses the environment that setup created.

**3. Open `run_unigrid.py`, edit the SETTINGS block at the top, and press Run (▶).**

```python
# Pick a grid — keep ONE line without the leading "#":
GRID = "grids/ACDC_matacdc_case24_ieee_rts1996_3zones.xlsx"
# GRID = "grids/ACDC_CIGRE_Benchmark.xlsx"
# GRID = "grids/ACDC_71bus_3IC_parallel.xlsx"
# ...
```

The results print in the terminal (AC / DC / branch / VSC tables) and are saved as
CSV files under `results/`.

> Prefer the terminal instead of an editor? After setup, run `bash run_mac.sh`
> (macOS) or `run_windows.bat` (Windows) — it runs the same `run_unigrid.py`.

## Requirements

- **MATLAB Runtime R2024b** for your OS (free). If full MATLAB R2024b is installed,
  it is already included. Otherwise download it from
  https://www.mathworks.com/products/compiler/matlab-runtime.html
- **Python 3.9 – 3.12** (3.13+ is not supported). The setup script handles this for you.

## Changing the grid and settings

Everything you normally change lives in the **SETTINGS block** at the top of
`run_unigrid.py` — edit it and press Run (▶):

- **Different grid** → switch the `GRID` line (all six example grids are listed there),
  or point it to your own `.xlsx` with the same sheet layout as the files in `grids/`.

For finer changes (individual buses, generators, lines), either **edit the grid's Excel
file directly** (that file *is* the input), or add a line after the case is loaded, e.g.
`case.AC_gen_dat.iloc[0, 5] *= 1.2`. Editable tables include `AC_PLoad_dat`,
`AC_gen_dat`, `AC_Line_dat`, `IC_dat`, `DC_PLoad_dat`, and more.

To run **many scenarios at once**, see `run_unigrid_scenarios.py` — a template that
loops over parameter values; adapt it to your own study.

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

## Files

| File | Role |
|------|------|
| **`run_unigrid.py`** | ▶ Edit the SETTINGS block and run this |
| `run_unigrid_scenarios.py` | Loop / scenario example (a template to adapt) |
| `setup_mac.sh` / `setup_windows.bat` | One-time setup (Python + deps) |
| `run_mac.sh` / `run_windows.bat` | Run from the terminal (alternative to ▶) |
| `load_case.py` | Engine: load Excel into editable tables |
| `acdc_engine.py` | Engine: run the power flow (auto-selects the OS package) |
| `_mac_worker.py` | Internal helper used on macOS only |
| `grids/` | Example grids (Excel) |
| `runpfacdc_pkg_win/` | Compiled solver for Windows |
| `runpfacdc_pkg_mac/` | Compiled solver for macOS |

<details><summary>Manual setup (without the scripts)</summary>

macOS (mwpython needs a real Python 3.9–3.12 venv):
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
