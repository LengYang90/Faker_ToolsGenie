#!/bin/bash
set -e
echo "--- Starting dependency installation ---"
pip install matplotlib seaborn
echo "--- Dependency installation complete ---"
echo "--- Starting main script execution ---"
python script.py
echo "--- Main script execution complete ---"
