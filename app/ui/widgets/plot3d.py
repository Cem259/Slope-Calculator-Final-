"""3D profile visualisation using Plotly with PyQt fallback."""
from __future__ import annotations

from typing import Optional

import numpy as np
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

from ...core.models import Profile

try:
    from PyQt6.QtWebEngineWidgets import QWebEngineView

    _HAS_WEB = True
except Exception:  # pragma: no cover - optional dependency
    QWebEngineView = None  # type: ignore
    _HAS_WEB = False

try:  # pragma: no cover - optional dependency
    import pyqtgraph.opengl as gl

    _HAS_GL = True
except Exception:  # pragma: no cover - optional dependency
    gl = None  # type: ignore
    _HAS_GL = False


class Plot3DWidget(QWidget):
    """Widget that renders 3D view with Plotly or PyQtGraph."""

    def __init__(self, translator, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._translator = translator
        self._layout = QVBoxLayout(self)
        self._web_view: Optional[QWebEngineView] = None
        self._gl_view = None
        if _HAS_WEB:
            self._web_view = QWebEngineView(self)
            self._layout.addWidget(self._web_view)
        elif _HAS_GL:
            self._gl_view = gl.GLViewWidget(self)
            self._gl_view.opts["distance"] = 40
            grid = gl.GLGridItem()
            grid.scale(2, 2, 1)
            self._gl_view.addItem(grid)
            self._layout.addWidget(self._gl_view)
        else:
            self._layout.addWidget(QLabel(self._translator.translate("plot3d_missing")))

    def update_profile(self, profile: Profile) -> None:
        if self._web_view is not None:
            self._update_plotly(profile)
        elif self._gl_view is not None and _HAS_GL:
            self._update_gl(profile)

    def retranslate(self) -> None:
        if self._web_view is None and self._gl_view is None:
            if self.layout().count():
                widget = self.layout().itemAt(0).widget()
                if isinstance(widget, QLabel):
                    widget.setText(self._translator.translate("plot3d_missing"))

    def _update_plotly(self, profile: Profile) -> None:
        import plotly.graph_objs as go

        xs = [p.x for p in profile.points]
        zs = [p.z for p in profile.points]
        ys = np.zeros(len(xs))
        trace = go.Scatter3d(
            x=xs,
            y=ys,
            z=zs,
            mode="lines+markers",
            marker=dict(size=6, color="orange"),
            line=dict(width=4, color="royalblue"),
        )
        layout = go.Layout(
            title=self._translator.translate("plot3d_title"),
            scene=dict(
                xaxis=dict(title=self._translator.translate("plot3d_axis_x")),
                yaxis=dict(title=self._translator.translate("plot3d_lateral")),
                zaxis=dict(title=self._translator.translate("plot3d_axis_z")),
            ),
            height=500,
        )
        fig = go.Figure(data=[trace], layout=layout)
        html = fig.to_html(include_plotlyjs="cdn", full_html=False)
        self._web_view.setHtml(html)

    def _update_gl(self, profile: Profile) -> None:
        if not _HAS_GL:
            return
        self._gl_view.clear()
        grid = gl.GLGridItem()
        grid.scale(2, 2, 1)
        self._gl_view.addItem(grid)
        if len(profile.points) < 2:
            return
        pts = np.array([[p.x, 0.0, p.z] for p in profile.points])
        plt = gl.GLLinePlotItem(pos=pts, color=(0.2, 0.4, 1, 1), width=2, antialias=True)
        self._gl_view.addItem(plt)

