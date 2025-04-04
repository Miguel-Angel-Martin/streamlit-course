#!/bin/bash

BASE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"

# Activate the virtual environment
source "$BASE_DIR/.venv/bin/activate"
cd "$BASE_DIR/app"

python cron.py import-gr-files || echo "Error importing GR files"

python cron.py import-po-files || echo "Error importing PO files"

# Deactivate the virtual environment
deactivate
