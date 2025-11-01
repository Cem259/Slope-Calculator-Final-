"""Main application window."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import qtawesome as qta
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QMainWindow,
    QMessageBox,
    QSplitter,
    QStackedWidget,
    QStatusBar,
    QToolBar,
    QWidget,
)

from ..core import io
from ..core.slope import percent_from_rise_run
from ..core.translator import Translator
from ..core.units import UnitPreferences, UnitSystem
from .dialogs import SettingsDialog, ask_open_csv, ask_save_csv
from .widgets.plot2d import Plot2DWidget
from .widgets.plot3d import Plot3DWidget
from .widgets.slope_form import SlopeFormWidget, SlopeValues


class MainWindow(QMainWindow):
    """Top-level UI combining input form and visualisations."""

    def __init__(self, translator: Translator, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._translator = translator
        self._unit_preferences = UnitPreferences(UnitSystem.METRIC)
        self._profile = io.profile_from_basic(100.0, 10.0, 18.0)
        self._current_view = 0
        self._current_theme = "light"
        self._build_ui()
        self.form_widget.distance_input.setValue(100.0)
        self.form_widget.h1_input.setValue(10.0)
        self.form_widget.h2_input.setValue(18.0)
        self.retranslate_ui()
        self._apply_profile()
        self._update_status()

    def _build_ui(self) -> None:
        self._create_actions()
        self._create_toolbar()
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        central = QWidget(self)
        central_layout = QHBoxLayout(central)
        central_layout.setContentsMargins(8, 8, 8, 8)
        central_layout.setSpacing(12)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        central_layout.addWidget(splitter)

        self.form_widget = SlopeFormWidget(self._translator, self._unit_preferences)
        self.form_widget.values_changed.connect(self._on_values_changed)
        self.form_widget.profile_requested.connect(self._import_polyline)
        splitter.addWidget(self.form_widget)

        self.view_stack = QStackedWidget()
        self.plot2d = Plot2DWidget(self._translator)
        self.plot3d = Plot3DWidget(self._translator)
        self.view_stack.addWidget(self.plot2d)
        self.view_stack.addWidget(self.plot3d)
        splitter.addWidget(self.view_stack)
        splitter.setStretchFactor(1, 1)

        self.setCentralWidget(central)

    # ------------------------------------------------------------------ actions
    def _create_actions(self) -> None:
        t = self._translator.translate
        self.new_action = self._make_action("fa5s.file", t("action_new"), self._new_profile)
        self.open_action = self._make_action("fa5s.folder-open", t("action_open"), self._open_project)
        self.save_action = self._make_action("fa5s.save", t("action_save"), self._save_project)
        self.import_action = self._make_action("fa5s.upload", t("action_import"), self._import_csv)
        self.export_action = self._make_action("fa5s.download", t("action_export"), self._export_csv)
        self.view2d_action = self._make_action(
            "fa5s.chart-line", t("action_view2d"), lambda _: self._set_view(0), checkable=True
        )
        self.view3d_action = self._make_action(
            "fa5s.cube", t("action_view3d"), lambda _: self._set_view(1), checkable=True
        )
        self.theme_action = self._make_action("fa5s.sun", t("action_theme"), self._toggle_theme)
        self.settings_action = self._make_action("fa5s.cog", t("action_settings"), self._open_settings)

    def _make_action(self, icon_name: str, text: str, slot, checkable: bool = False) -> QAction:
        action = QAction(qta.icon(icon_name), text, self)
        if checkable:
            action.triggered.connect(slot)
        else:
            action.triggered.connect(lambda _: slot())
        action.setCheckable(checkable)
        return action

    def _create_toolbar(self) -> None:
        toolbar = QToolBar(self)
        toolbar.setMovable(False)
        toolbar.addAction(self.new_action)
        toolbar.addAction(self.open_action)
        toolbar.addAction(self.save_action)
        toolbar.addSeparator()
        toolbar.addAction(self.import_action)
        toolbar.addAction(self.export_action)
        toolbar.addSeparator()
        toolbar.addAction(self.view2d_action)
        toolbar.addAction(self.view3d_action)
        toolbar.addSeparator()
        toolbar.addAction(self.theme_action)
        toolbar.addAction(self.settings_action)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolbar)
        self.view2d_action.setChecked(True)

    # ---------------------------------------------------------------- profile ops
    def _on_values_changed(self, values: SlopeValues) -> None:
        if len(self._profile.points) == 2:
            self._profile.points[0].x = 0.0
            self._profile.points[0].z = values.h1
            self._profile.points[1].x = values.distance
            self._profile.points[1].z = values.h2
        self._apply_profile()
        self._update_status(values)

    def _apply_profile(self) -> None:
        self.plot2d.update_profile(self._profile)
        self.plot3d.update_profile(self._profile)

    def _update_status(self, values: Optional[SlopeValues] = None) -> None:
        if values is None and len(self._profile.points) >= 2:
            start = self._profile.points[0]
            end = self._profile.points[-1]
            distance = end.x - start.x
            rise = end.z - start.z
            percent = percent_from_rise_run(rise, distance) if distance != 0 else 0.0
            values = SlopeValues(distance, start.z, end.z, rise, distance, percent, 0.0, 0.0)
        if values:
            text = self._translator.translate("status_template").format(
                units=self._unit_preferences.length_label,
                theme=self._translator.translate(f"theme_{self._current_theme}"),
                percent=f"{values.percent:.2f}%",
            )
            self.status_bar.showMessage(text)

    # --------------------------------------------------------------- command handlers
    def _new_profile(self) -> None:
        self._profile = io.profile_from_basic(100.0, 0.0, 0.0)
        self.form_widget.distance_input.setValue(100.0)
        self.form_widget.h1_input.setValue(0.0)
        self.form_widget.h2_input.setValue(0.0)
        self._apply_profile()
        self._update_status()

    def _open_project(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, self._translator.translate("dialog_open_project"), "", "Project (*.json)"
        )
        if not path:
            return
        profile = io.load_project(Path(path))
        if not profile.points:
            QMessageBox.warning(self, "", self._translator.translate("error_empty_profile"))
            return
        self._profile = profile
        first = profile.points[0]
        last = profile.points[-1]
        self.form_widget.distance_input.setValue(last.x - first.x)
        self.form_widget.h1_input.setValue(first.z)
        self.form_widget.h2_input.setValue(last.z)
        self._apply_profile()
        self._update_status()

    def _save_project(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self, self._translator.translate("dialog_save_project"), "", "Project (*.json)"
        )
        if not path:
            return
        io.save_project(Path(path), self._profile)

    def _import_csv(self) -> None:
        path = ask_open_csv(self, self._translator.translate("dialog_import_csv"))
        if not path:
            return
        try:
            profile = io.read_profile_csv(path)
        except io.CSVProfileError as exc:
            QMessageBox.critical(self, self._translator.translate("error_title"), str(exc))
            return
        self._profile = profile
        first = profile.points[0]
        last = profile.points[-1]
        self.form_widget.distance_input.setValue(last.x - first.x)
        self.form_widget.h1_input.setValue(first.z)
        self.form_widget.h2_input.setValue(last.z)
        self._apply_profile()
        self._update_status()

    def _export_csv(self) -> None:
        path = ask_save_csv(self, self._translator.translate("dialog_export_csv"))
        if not path:
            return
        io.write_profile_csv(path, self._profile)

    def _import_polyline(self) -> None:
        self._import_csv()

    def _set_view(self, index: int) -> None:
        self.view_stack.setCurrentIndex(index)
        if index == 0:
            self.view2d_action.setChecked(True)
            self.view3d_action.setChecked(False)
        else:
            self.view3d_action.setChecked(True)
            self.view2d_action.setChecked(False)

    def _toggle_theme(self) -> None:
        self._current_theme = "dark" if self._current_theme == "light" else "light"
        self.retranslate_ui()
        self._update_status()

    def _open_settings(self) -> None:
        dialog = SettingsDialog(
            self._translator,
            language=self._translator.language,
            theme=self._current_theme,
            languages=self._translator.available_languages().keys(),
            parent=self,
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            result = dialog.result_data()
            if result.language != self._translator.language:
                self._translator.load(result.language)
            self._current_theme = result.theme
            self.retranslate_ui()
            self._apply_profile()
            self._update_status()

    # ---------------------------------------------------------------- retranslate/theme
    def retranslate_ui(self) -> None:
        t = self._translator.translate
        self.setWindowTitle(t("window_title"))
        self.new_action.setText(t("action_new"))
        self.open_action.setText(t("action_open"))
        self.save_action.setText(t("action_save"))
        self.import_action.setText(t("action_import"))
        self.export_action.setText(t("action_export"))
        self.view2d_action.setText(t("action_view2d"))
        self.view3d_action.setText(t("action_view3d"))
        self.theme_action.setText(t("action_theme"))
        self.settings_action.setText(t("action_settings"))
        theme_icon = "fa5s.sun" if self._current_theme == "light" else "fa5s.moon"
        self.theme_action.setIcon(qta.icon(theme_icon))
        self.plot2d.retranslate()
        self.plot3d.retranslate()
        self.form_widget.retranslate()
        palette = self._light_palette() if self._current_theme == "light" else self._dark_palette()
        self.setStyleSheet(palette)

    def _light_palette(self) -> str:
        return """
        QWidget { background-color: #f4f4f4; color: #1f1f1f; }
        QGroupBox { border: 1px solid #ccc; border-radius: 8px; margin-top: 12px; padding: 8px; }
        QPushButton { background-color: #0b6efd; color: white; border-radius: 6px; padding: 6px 12px; }
        QPushButton:hover { background-color: #0a58ca; }
        QLineEdit, QDoubleSpinBox { border-radius: 6px; padding: 4px; border: 1px solid #bbb; }
        """

    def _dark_palette(self) -> str:
        return """
        QWidget { background-color: #1e1e1e; color: #e6e6e6; }
        QGroupBox { border: 1px solid #444; border-radius: 8px; margin-top: 12px; padding: 8px; }
        QPushButton { background-color: #2563eb; color: white; border-radius: 6px; padding: 6px 12px; }
        QPushButton:hover { background-color: #1d4ed8; }
        QLineEdit, QDoubleSpinBox { border-radius: 6px; padding: 4px; border: 1px solid #555; background-color: #2b2b2b; }
        """

