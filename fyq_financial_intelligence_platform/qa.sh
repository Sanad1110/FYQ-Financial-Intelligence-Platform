#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
if [ -f .venv/bin/activate ]; then source .venv/bin/activate; elif [ -f "$HOME/.venv/bin/activate" ]; then source "$HOME/.venv/bin/activate"; fi
python qa_fyq_v7.py
