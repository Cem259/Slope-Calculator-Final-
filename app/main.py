"""Entrypoint for the slope calculator application."""
from __future__ import annotations

import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication, QMessageBox

from .core.translator import Translator
from .ui.main_window import MainWindow


def run() -> None:
    """Launch the Qt application."""
    app = QApplication(sys.argv)
    app.setApplicationName("Slope Calculator")
    i18n_path = Path(__file__).resolve().parent / "i18n"
    translator = Translator(i18n_path, "en")
    try:
        window = MainWindow(translator)
    except Exception as exc:  # pragma: no cover
        QMessageBox.critical(None, "Error", str(exc))
        raise
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":  # pragma: no cover
    run()

