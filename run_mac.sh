#!/usr/bin/env bash
# run_mac.sh — run UniGrid using the .venv created by setup_mac.sh.
set -e
cd "$(dirname "$0")"
if [ ! -x ".venv/bin/python" ]; then
    echo "[UniGrid] .venv not found. Run ./setup_mac.sh first."
    exit 1
fi
.venv/bin/python run_unigrid.py
