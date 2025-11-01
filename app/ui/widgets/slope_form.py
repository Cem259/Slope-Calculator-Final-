"""Input panel for slope calculations."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ...core.slope import (
    angle_from_percent,
    percent_from_angle,
    percent_from_ratio,
    ratio_from_percent,
    sanitize_ratio_display,
)
from ...core.units import UnitPreferences, UnitSystem


@dataclass
class SlopeValues:
    distance: float
    h1: float
    h2: float
    rise: float
    run: float
    percent: float
    ratio: float
    angle: float


class SlopeFormWidget(QGroupBox):
    """Widget containing slope inputs and conversions."""

    values_changed = pyqtSignal(SlopeValues)
    profile_requested = pyqtSignal()

    def __init__(self, translator, unit_preferences: UnitPreferences, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._translator = translator
        self._unit_preferences = unit_preferences
        self._updating = False
        self._build_ui()
        self.retranslate()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        self.setLayout(layout)

        form_layout = QFormLayout()
        layout.addLayout(form_layout)

        self.distance_input = QDoubleSpinBox()
        self.distance_input.setRange(-1e6, 1e6)
        self.distance_input.setDecimals(3)
        self.distance_input.valueChanged.connect(self._emit_changes)
        form_layout.addRow("", self.distance_input)

        self.h1_input = QDoubleSpinBox()
        self.h1_input.setRange(-1e6, 1e6)
        self.h1_input.setDecimals(3)
        self.h1_input.valueChanged.connect(self._emit_changes)
        form_layout.addRow("", self.h1_input)

        self.h2_input = QDoubleSpinBox()
        self.h2_input.setRange(-1e6, 1e6)
        self.h2_input.setDecimals(3)
        self.h2_input.valueChanged.connect(self._emit_changes)
        form_layout.addRow("", self.h2_input)

        self.rise_input = QDoubleSpinBox()
        self.rise_input.setRange(-1e6, 1e6)
        self.rise_input.setDecimals(3)
        self.rise_input.valueChanged.connect(self._on_rise_changed)
        form_layout.addRow("", self.rise_input)

        self.run_input = QDoubleSpinBox()
        self.run_input.setRange(-1e6, 1e6)
        self.run_input.setDecimals(3)
        self.run_input.valueChanged.connect(self._on_run_changed)
        form_layout.addRow("", self.run_input)

        self.percent_input = QDoubleSpinBox()
        self.percent_input.setRange(-1e4, 1e4)
        self.percent_input.setDecimals(4)
        self.percent_input.valueChanged.connect(self._on_percent_changed)
        form_layout.addRow("", self.percent_input)

        self.angle_input = QDoubleSpinBox()
        self.angle_input.setRange(-90.0, 90.0)
        self.angle_input.setDecimals(4)
        self.angle_input.valueChanged.connect(self._on_angle_changed)
        form_layout.addRow("", self.angle_input)

        ratio_layout = QHBoxLayout()
        self.ratio_input = QDoubleSpinBox()
        self.ratio_input.setRange(0.0, 1e6)
        self.ratio_input.setDecimals(4)
        self.ratio_input.valueChanged.connect(self._on_ratio_changed)
        ratio_layout.addWidget(self.ratio_input)
        self.ratio_label = QLabel("1:∞")
        ratio_layout.addWidget(self.ratio_label)
        form_layout.addRow("", ratio_layout)

        self.unit_combo = QComboBox()
        self.unit_combo.addItem("Metric", UnitSystem.METRIC)
        self.unit_combo.addItem("Imperial", UnitSystem.IMPERIAL)
        self.unit_combo.setCurrentIndex(0)
        self.unit_combo.currentIndexChanged.connect(self._on_unit_changed)
        form_layout.addRow("", self.unit_combo)

        self.profile_button = QPushButton()
        self.profile_button.clicked.connect(self.profile_requested.emit)
        layout.addWidget(self.profile_button)
        layout.addStretch()

    def _on_unit_changed(self) -> None:
        old_system = self._unit_preferences.system
        system = self.unit_combo.currentData()
        if system == old_system:
            return
        self._unit_preferences.system = system
        factor = 1.0
        if old_system == UnitSystem.METRIC and system == UnitSystem.IMPERIAL:
            factor = 3.280839895
        elif old_system == UnitSystem.IMPERIAL and system == UnitSystem.METRIC:
            factor = 0.3048
        for spin in (
            self.distance_input,
            self.h1_input,
            self.h2_input,
            self.rise_input,
            self.run_input,
        ):
            spin.setValue(spin.value() * factor)
        self._emit_changes()

    def _on_rise_changed(self, value: float) -> None:
        if self._updating:
            return
        self._update_from_core(rise=value, trigger="rise")

    def _on_run_changed(self, value: float) -> None:
        if self._updating:
            return
        self._update_from_core(run=value, trigger="run")

    def _on_percent_changed(self, value: float) -> None:
        if self._updating:
            return
        self._update_from_core(percent=value, trigger="percent")

    def _on_angle_changed(self, value: float) -> None:
        if self._updating:
            return
        self._update_from_core(angle=value, trigger="angle")

    def _on_ratio_changed(self, value: float) -> None:
        if self._updating:
            return
        if value == 0:
            return
        percent = percent_from_ratio(value)
        self._update_from_core(percent=percent, trigger="ratio")

    def _update_from_core(self, **overrides) -> None:
        self._updating = True
        try:
            distance = self.distance_input.value()
            h1 = self.h1_input.value()
            h2 = self.h2_input.value()
            rise = self.rise_input.value()
            run = self.run_input.value()
            percent = self.percent_input.value()
            angle = self.angle_input.value()
            ratio = self.ratio_input.value()

            values = {
                "distance": distance,
                "h1": h1,
                "h2": h2,
                "rise": rise,
                "run": run,
                "percent": percent,
                "angle": angle,
                "ratio": ratio,
            }
            trigger = overrides.pop("trigger", None)
            values.update(overrides)
            if trigger == "rise":
                if values["run"] != 0:
                    values["percent"] = (values["rise"] / values["run"]) * 100.0
                    values["angle"] = angle_from_percent(values["percent"])
            elif trigger == "run":
                if values["run"] != 0:
                    values["percent"] = (values["rise"] / values["run"]) * 100.0
                    values["angle"] = angle_from_percent(values["percent"])
            elif trigger == "percent":
                values["angle"] = angle_from_percent(values["percent"])
                values["rise"] = (values["percent"] / 100.0) * values["run"]
            elif trigger == "angle":
                values["percent"] = percent_from_angle(values["angle"])
                values["rise"] = (values["percent"] / 100.0) * values["run"]
            elif trigger == "ratio":
                values["ratio"] = ratio_from_percent(values["percent"])
                values["angle"] = angle_from_percent(values["percent"])
                values["rise"] = (values["percent"] / 100.0) * values["run"]

            values["distance"] = values["run"]
            values["h2"] = values["h1"] + values["rise"]

            self.distance_input.setValue(values["distance"])
            self.h1_input.setValue(values["h1"])
            self.h2_input.setValue(values["h2"])
            self.rise_input.setValue(values["rise"])
            self.run_input.setValue(values["run"])
            self.percent_input.setValue(values["percent"])
            self.angle_input.setValue(values["angle"])
            ratio_value = ratio_from_percent(values["percent"])
            self.ratio_input.setValue(ratio_value if ratio_value != float("inf") else 0.0)
            self.ratio_label.setText(sanitize_ratio_display(ratio_value))

            self._emit_changes()
        finally:
            self._updating = False

    def _emit_changes(self) -> None:
        if self._updating:
            return
        self._updating = True
        try:
            distance = self.distance_input.value()
            h1 = self.h1_input.value()
            h2 = self.h2_input.value()
            rise = h2 - h1
            run = distance
            percent = (rise / run) * 100.0 if run != 0 else 0.0
            angle = angle_from_percent(percent)
            ratio = ratio_from_percent(percent)

            self.rise_input.setValue(rise)
            self.run_input.setValue(run)
            self.percent_input.setValue(percent)
            self.angle_input.setValue(angle)
            self.ratio_input.setValue(ratio if ratio != float("inf") else 0.0)
            self.ratio_label.setText(sanitize_ratio_display(ratio))

            values = SlopeValues(
                distance=distance,
                h1=h1,
                h2=h2,
                rise=rise,
                run=run,
                percent=percent,
                ratio=ratio,
                angle=angle,
            )
            self.values_changed.emit(values)
        finally:
            self._updating = False

    def retranslate(self) -> None:
        t = self._translator.translate
        self.setTitle(t("inputs_title"))
        form_layout: QFormLayout = self.layout().itemAt(0).layout()  # type: ignore
        labels = [
            t("inputs_distance"),
            t("inputs_h1"),
            t("inputs_h2"),
            t("inputs_rise"),
            t("inputs_run"),
            t("inputs_percent"),
            t("inputs_angle"),
            t("inputs_ratio"),
            t("inputs_units"),
        ]
        for idx, label in enumerate(labels):
            form_layout.setWidget(idx, QFormLayout.ItemRole.LabelRole, QLabel(label))
        self.profile_button.setText(t("inputs_manage_profile"))
        self.unit_combo.setItemText(0, t("unit_metric"))
        self.unit_combo.setItemText(1, t("unit_imperial"))

