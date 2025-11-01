"""Matplotlib based 2D profile plot."""
from __future__ import annotations

from typing import Optional

import matplotlib
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHeaderView, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from ...core.models import Profile

class Plot2DWidget(QWidget):
    """Widget containing matplotlib 2D plot and segment table."""

    def __init__(self, translator, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._translator = translator
        self._figure = Figure(figsize=(5, 4), tight_layout=True)
        self._canvas = FigureCanvas(self._figure)
        self._axes = self._figure.add_subplot(111)
        self._axes.grid(True)
        self._table = QTableWidget(0, 4)
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout = QVBoxLayout(self)
        layout.addWidget(self._canvas)
        layout.addWidget(self._table)
        self._hover_label = None
        self._canvas.mpl_connect("motion_notify_event", self._on_motion)
        self.retranslate()

    def retranslate(self) -> None:
        t = self._translator.translate
        self._axes.set_title(t("plot2d_title"))
        self._axes.set_xlabel(t("plot2d_xlabel"))
        self._axes.set_ylabel(t("plot2d_ylabel"))
        headers = [
            t("segments_delta_x"),
            t("segments_delta_z"),
            t("segments_percent"),
            t("segments_angle"),
        ]
        self._table.setHorizontalHeaderLabels(headers)
        self._canvas.draw_idle()

    def update_profile(self, profile: Profile) -> None:
        self._axes.clear()
        self._axes.grid(True)
        t = self._translator.translate
        segments = profile.as_segments()
        if len(profile.points) >= 2:
            xs = [p.x for p in profile.points]
            zs = [p.z for p in profile.points]
            colors = ["tab:green" if abs(s.slope_percent) <= 8 else "tab:red" for s in segments]
            for idx, segment in enumerate(segments):
                self._axes.plot(
                    [segment.start.x, segment.end.x],
                    [segment.start.z, segment.end.z],
                    color=colors[idx],
                    linewidth=2,
                )
            self._axes.scatter(xs, zs, color="black", s=30)
            legend_handles = [
                matplotlib.lines.Line2D([], [], color="tab:green", label=t("segments_safe")),
                matplotlib.lines.Line2D([], [], color="tab:red", label=t("segments_steep")),
            ]
            self._axes.legend(handles=legend_handles)
        else:
            self._axes.text(0.5, 0.5, t("plot2d_empty"), transform=self._axes.transAxes, ha="center")
        self._canvas.draw_idle()

        self._table.setRowCount(len(segments))
        for row, segment in enumerate(segments):
            delta_x = segment.end.x - segment.start.x
            delta_z = segment.end.z - segment.start.z
            items = [
                f"{delta_x:.3f}",
                f"{delta_z:.3f}",
                f"{segment.slope_percent:.3f}",
                f"{segment.angle_degrees:.3f}",
            ]
            for col, text in enumerate(items):
                item = QTableWidgetItem(text)
                if col == 2 and abs(segment.slope_percent) > 8:
                    item.setBackground(Qt.GlobalColor.red)
                    item.setForeground(Qt.GlobalColor.white)
                self._table.setItem(row, col, item)

    def _on_motion(self, event) -> None:
        if event.inaxes != self._axes or event.xdata is None or event.ydata is None:
            self._canvas.setToolTip("")
            return
        xs = event.xdata
        zs = event.ydata
        self._canvas.setToolTip(f"x={xs:.2f}, z={zs:.2f}")

