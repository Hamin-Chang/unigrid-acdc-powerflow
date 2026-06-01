#!/usr/bin/env bash
# setup_mac.sh — one-time setup for UniGrid on macOS.
# Creates a Python 3.12 virtual environment (.venv) and installs dependencies.
# After this, run:  ./run_mac.sh   (or: .venv/bin/python run_unigrid.py)

set -e
cd "$(dirname "$0")"

echo "[UniGrid] macOS setup starting..."

# 1) Find a supported Python (3.9-3.12). Prefer 3.12.
PY=""
for cand in \
    /opt/homebrew/opt/python@3.12/bin/python3.12 \
    /opt/homebrew/opt/python@3.11/bin/python3.11 \
    /opt/homebrew/opt/python@3.10/bin/python3.10 \
    python3.12 python3.11 python3.10 python3.9 ; do
    if command -v "$cand" >/dev/null 2>&1; then PY="$cand"; break; fi
done

# 2) If none found, install Python 3.12 via Homebrew.
if [ -z "$PY" ]; then
    if command -v brew >/dev/null 2>&1; then
        echo "[UniGrid] No Python 3.9-3.12 found. Installing python@3.12 via Homebrew..."
        brew install python@3.12
        PY="/opt/homebrew/opt/python@3.12/bin/python3.12"
    else
        echo "[UniGrid] ERROR: need Python 3.9-3.12 but none found, and Homebrew is not installed."
        echo "  Install Homebrew (https://brew.sh) or Python 3.12 manually, then re-run."
        exit 1
    fi
fi
echo "[UniGrid] Using Python: $PY ($($PY --version))"

# 3) Create the virtual environment (mwpython on macOS requires a real venv).
"$PY" -m venv .venv

# 4) Install dependencies into the venv.
.venv/bin/python -m pip install --upgrade pip >/dev/null
.venv/bin/python -m pip install pandas openpyxl

echo ""
echo "[UniGrid] Setup complete."
echo "  Run it with:   ./run_mac.sh"
echo "  Or:            .venv/bin/python run_unigrid.py"
