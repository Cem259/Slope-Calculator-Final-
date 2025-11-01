"""Application entry point for the slope calculator GUI."""
from __future__ import annotations

from app.main import run


def main() -> int:
    """Entrypoint used by the CLI and module execution."""
    run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
