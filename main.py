"""Application entry point for the slope calculator GUI."""

from slope_calculator import run


def main() -> int:
    """Entrypoint used by the CLI and module execution."""
    return run()


if __name__ == "__main__":
    raise SystemExit(main())
