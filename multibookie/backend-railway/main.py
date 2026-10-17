"""
SureNaira — Main Entry Point
Run with:  uvicorn main:app --host 0.0.0.0 --port 8000 --reload
"""

import logging
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

# Configure logging — stdout only (Railway streams logs; file logging is unreliable)
_handlers: list[logging.Handler] = [logging.StreamHandler(sys.stdout)]

# Optional file logging when a writable logs dir exists (local dev)
_log_dir = os.path.join(os.path.dirname(__file__), "logs")
try:
    os.makedirs(_log_dir, exist_ok=True)
    _handlers.append(logging.FileHandler(os.path.join(_log_dir, "surenaira.log")))
except OSError:
    pass  # Ephemeral filesystem (Railway) — skip file logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    datefmt="%H:%M:%S",
    handlers=_handlers,
)

from api.server import app  # noqa: F401 — uvicorn targets this

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
        reload=False,  # Never reload in production
        log_level="info",
    )
