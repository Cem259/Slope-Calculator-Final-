"""Application dialogs."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)


@dataclass
class SettingsResult:
    language: str
    theme: str


class SettingsDialog(QDialog):
    """Dialog to adjust language and theme."""

    def __init__(self, translator, language: str, theme: str, languages: Iterable[str], parent=None) -> None:
        super().__init__(parent)
        self._translator = translator
        self._language = language
        self._theme = theme
        self._languages = list(languages)
        self.setModal(True)
        self._build_ui()
        self.retranslate()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        self.setLayout(layout)
        form = QFormLayout()
        layout.addLayout(form)

        self.language_combo = QComboBox()
        for code in self._languages:
            self.language_combo.addItem(code.upper(), code)
        try:
            current_index = self._languages.index(self._language)
        except ValueError:
            current_index = 0
        self.language_combo.setCurrentIndex(current_index)
        form.addRow("", self.language_combo)

        self.theme_combo = QComboBox()
        self.theme_combo.addItem("light", "light")
        self.theme_combo.addItem("dark", "dark")
        index = self.theme_combo.findData(self._theme)
        self.theme_combo.setCurrentIndex(index if index >= 0 else 0)
        form.addRow("", self.theme_combo)

        buttons = QHBoxLayout()
        layout.addLayout(buttons)
        self.cancel_button = QPushButton()
        self.cancel_button.clicked.connect(self.reject)
        buttons.addWidget(self.cancel_button)
        self.ok_button = QPushButton()
        self.ok_button.clicked.connect(self.accept)
        buttons.addWidget(self.ok_button)

    def retranslate(self) -> None:
        t = self._translator.translate
        self.setWindowTitle(t("settings_title"))
        form: QFormLayout = self.layout().itemAt(0).layout()  # type: ignore
        form.setWidget(0, QFormLayout.ItemRole.LabelRole, QLabel(t("settings_language")))
        form.setWidget(1, QFormLayout.ItemRole.LabelRole, QLabel(t("settings_theme")))
        for idx, code in enumerate(self._languages):
            self.language_combo.setItemText(idx, t(f"language_{code}"))
        self.theme_combo.setItemText(0, t("theme_light"))
        self.theme_combo.setItemText(1, t("theme_dark"))
        self.cancel_button.setText(t("dialog_cancel"))
        self.ok_button.setText(t("dialog_ok"))

    def result_data(self) -> SettingsResult:
        return SettingsResult(
            language=self.language_combo.currentData(), theme=self.theme_combo.currentData()
        )


def ask_open_csv(parent, caption: str) -> Optional[Path]:
    filename, _ = QFileDialog.getOpenFileName(parent, caption, "", "CSV Files (*.csv)")
    return Path(filename) if filename else None


def ask_save_csv(parent, caption: str) -> Optional[Path]:
    filename, _ = QFileDialog.getSaveFileName(parent, caption, "", "CSV Files (*.csv)")
    return Path(filename) if filename else None

