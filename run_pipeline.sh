#!/bin/bash
# Run Phase 1 pipeline end-to-end (Load -> Clean -> Engineer -> Store)
# Requires network for first run (Hugging Face dataset ~574MB)
# Execute from project root: ./run_pipeline.sh

set -e
cd "$(dirname "$0")"
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)"

# Use project-local Hugging Face cache
export HF_HOME="$(pwd)/backend/data/.hf_cache"
export HUGGINGFACE_HUB_CACHE="${HF_HOME}"

source .venv/bin/activate 2>/dev/null || true
python backend/main.py
