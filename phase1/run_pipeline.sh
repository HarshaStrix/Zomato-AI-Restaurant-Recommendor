#!/bin/bash
# Run Phase 1 pipeline end-to-end
# Execute from project root: ./phase1/run_pipeline.sh

set -e
cd "$(dirname "$0")/.."
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)"

# Use project-local Hugging Face cache
export HF_HOME="$(pwd)/phase1/data/.hf_cache"
export HUGGINGFACE_HUB_CACHE="${HF_HOME}"

source .venv/bin/activate 2>/dev/null || true
python phase1/main.py
