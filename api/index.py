
import sys
import os
from pathlib import Path

# Add project root to path so we can import phase2, phase3, etc.
# Vercel's current working directory is the project root.
_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from phase2.api.main import app

# For Vercel, the entry point is the 'app' object
# The routes are defined in phase2.api.main and phase2.api.routes.recommendations
