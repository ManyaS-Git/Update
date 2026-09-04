import sys
from pathlib import Path

# Enable importing app package when uvicorn is executed from repository root
backend_dir = Path(__file__).resolve().parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.main import app  # noqa: E402
