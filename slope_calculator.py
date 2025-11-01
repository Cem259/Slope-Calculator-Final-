import sys
from contextlib import suppress

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401  # Required for 3D projection registration
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


def compute_slope(distance, h1, h2):
    """Compute the slope percentage between two heights over a horizontal distance."""
    return ((h2 - h1) / distance) * 100 if distance != 0 else float("inf")


class ModernStyledWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setFont(QFont("Arial", 10))
        theme = getattr(self, "current_theme", "light")
        self.setStyleSheet(self.load_styles(theme))

    def load_styles(self, theme="light"):
        return ""


class SettingsDialog(QDialog):
    def __init__(self, current_language, current_theme, translations, language_display):
        super().__init__()
        self._translations = translations
        self._language_display = language_display
        self._current_language = current_language

        texts = self._translations[self._current_language]
        self.setWindowTitle(texts["settings_title"])

        layout = QVBoxLayout()

        language_label = QLabel(texts["settings_language_label"])
        layout.addWidget(language_label)

        self.language_combo = QComboBox()
        for code in ["tr", "en"]:
            self.language_combo.addItem(self._language_display[self._current_language][code], code)
        self.language_combo.setCurrentIndex(["tr", "en"].index(current_language))
        layout.addWidget(self.language_combo)

        theme_label = QLabel(texts["settings_theme_label"])
        layout.addWidget(theme_label)

        self.theme_combo = QComboBox()
        self.theme_combo.addItem(texts["settings_theme_light"], "light")
        self.theme_combo.addItem(texts["settings_theme_dark"], "dark")
        self.theme_combo.setCurrentIndex(0 if current_theme == "light" else 1)
        layout.addWidget(self.theme_combo)

        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        cancel_button = QPushButton(texts["settings_cancel"])
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_button)
        save_button = QPushButton(texts["settings_save"])
        save_button.clicked.connect(self.accept)
        buttons_layout.addWidget(save_button)
        layout.addLayout(buttons_layout)

        self.setLayout(layout)

    @property
    def selected_language(self):
        return self.language_combo.currentData()

    @property
    def selected_theme(self):
        return self.theme_combo.currentData()


class SlopeCalculator(ModernStyledWindow):
    def __init__(self):
        self.current_theme = "light"
        self.theme_styles = {
            "light": """
            QWidget {
                background-color: #eef1f5;
                color: #333333;
                font-size: 12pt;
            }
            QLabel {
                color: #2d2d2d;
            }
            QLabel#headerLabel {
                font-size: 20pt;
                font-weight: 600;
                color: #1a1a1a;
            }
            QLabel#subtitleLabel {
                font-size: 11pt;
                color: #666666;
            }
            QLabel#resultLabel {
                font-size: 16pt;
                font-weight: 600;
                color: #000000;
            }
            QLabel#resultTipLabel {
                font-size: 10pt;
                color: #666666;
            }
            QFrame#formCard, QFrame#resultCard {
                background-color: #ffffff;
                border-radius: 16px;
                border: 1px solid #d8e1eb;
                padding: 20px;
            }
            QLineEdit {
                border: 2px solid #cbd5e1;
                border-radius: 6px;
                padding: 6px 8px;
                font-size: 12pt;
                color: #d32f2f;
                background-color: #fdfdfd;
            }
            QLineEdit:focus {
                border-color: #0078d7;
                background-color: #ffffff;
            }
            QPushButton {
                background-color: #0078d7;
                color: #ffffff;
                border-radius: 6px;
                padding: 10px 18px;
                font-size: 12pt;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QPushButton#calculateButton {
                background-color: #8bc34a;
                color: #000000;
            }
            QPushButton#calculateButton:hover {
                background-color: #7cb342;
            }
            QPushButton#view3dButton {
                background-color: transparent;
                color: #0a64c9;
                border: 2px solid #0a64c9;
            }
            QPushButton#view3dButton:hover {
                background-color: rgba(10, 100, 201, 0.08);
            }
            QPushButton#view3dButton:disabled {
                color: #9ba4b5;
                border-color: #d0d7e2;
                background-color: transparent;
            }
            QPushButton#settingsButton {
                background-color: transparent;
                color: #465166;
                border: 2px solid transparent;
            }
            QPushButton#settingsButton:hover {
                color: #0a64c9;
            }
            """,
            "dark": """
            QWidget {
                background-color: #121417;
                color: #f4f4f4;
                font-size: 12pt;
            }
            QLabel {
                color: #f4f4f4;
            }
            QLabel#headerLabel {
                font-size: 20pt;
                font-weight: 600;
                color: #f4f7fb;
            }
            QLabel#subtitleLabel {
                font-size: 11pt;
                color: #a0a8b7;
            }
            QLabel#resultLabel {
                font-size: 16pt;
                font-weight: 600;
                color: #000000;
            }
            QLabel#resultTipLabel {
                font-size: 10pt;
                color: #a0a8b7;
            }
            QFrame#formCard, QFrame#resultCard {
                background-color: #1d2127;
                border-radius: 16px;
                border: 1px solid #2d333b;
                padding: 20px;
            }
            QLineEdit {
                border: 2px solid #2d333b;
                border-radius: 6px;
                padding: 6px 8px;
                font-size: 12pt;
                color: #ff6b6b;
                background-color: #15181d;
            }
            QLineEdit:focus {
                border-color: #3a7bd5;
                background-color: #1a1e24;
            }
            QPushButton {
                background-color: #3a7bd5;
                color: #ffffff;
                border-radius: 6px;
                padding: 10px 18px;
                font-size: 12pt;
            }
            QPushButton:hover {
                background-color: #2f66b8;
            }
            QPushButton#calculateButton {
                background-color: #66bb6a;
                color: #000000;
            }
            QPushButton#calculateButton:hover {
                background-color: #57a55b;
            }
            QPushButton#view3dButton {
                background-color: transparent;
                color: #8bbdff;
                border: 2px solid #8bbdff;
            }
            QPushButton#view3dButton:hover {
                background-color: rgba(139, 189, 255, 0.15);
            }
            QPushButton#view3dButton:disabled {
                color: #4b5462;
                border-color: #2d333b;
                background-color: transparent;
            }
            QPushButton#settingsButton {
                background-color: transparent;
                color: #a0a8b7;
                border: 2px solid transparent;
            }
            QPushButton#settingsButton:hover {
                color: #8bbdff;
            }
            """,
        }
        super().__init__()

        self.translations = {
            "tr": {
                "header_title": "Eğim Analiz Panosu",
                "subtitle": "Arazi ve yapı projelerinizi planlamak için eğim hesaplamalarını keşfedin.",
                "window_title": "Eğim Hesaplayıcı",
                "distance_label": "Yatay Mesafe:",
                "first_height_label": "Birinci Nokta Yüksekliği:",
                "second_height_label": "İkinci Nokta Yüksekliği:",
                "calculate_button": "Eğimi Hesapla",
                "result_label_placeholder": "Eğim: -",
                "result_label_prefix": "Eğim:",
                "result_tip_placeholder": "Başlamak için mesafe ve yükseklik değerlerini girin.",
                "result_tip_ready": "3B görünümü açarak eğim profilini farklı açılardan inceleyin.",
                "settings_button": "Ayarlar",
                "settings_title": "Ayarlar",
                "settings_language_label": "Dil",
                "settings_theme_label": "Görünüm",
                "settings_theme_light": "Açık",
                "settings_theme_dark": "Koyu",
                "settings_save": "Kaydet",
                "settings_cancel": "İptal",
                "view_3d_button": "3B Görünüm",
                "view_2d_button": "2B Görünüm",
                "view_3d_disabled_tooltip": "3B görünümünü açmak için önce eğimi hesaplayın.",
                "view_3d_enabled_tooltip": "Eğimi etkileşimli bir 3B grafikle görüntüleyin.",
                "view_2d_enabled_tooltip": "Eğimi klasik 2B grafikte görüntüleyin.",
                "input_error_title": "Giriş Hatası",
                "input_error_message": "Lütfen geçerli sayısal değerler girin.",
                "plot_title": "Eğim Görselleştirmesi",
                "plot_3d_title": "3B Eğim Görselleştirmesi",
                "plot_distance_label": "Mesafe (m)",
                "plot_height_label": "Yükseklik (m)",
                "plot_depth_label": "Yanal Ofset (m)",
                "plot_legend_distance": "Mesafe",
                "plot_legend_height": "Yükseklik",
                "plot_legend_slope": "Eğim Çizgisi",
                "plot_annotation": "Eğim: {value}",
            },
            "en": {
                "header_title": "Slope Analysis Dashboard",
                "subtitle": "Explore slope calculations to plan your terrain and construction projects.",
                "window_title": "Slope Calculator",
                "distance_label": "Horizontal Distance:",
                "first_height_label": "First Point Height:",
                "second_height_label": "Second Point Height:",
                "calculate_button": "Calculate Slope",
                "result_label_placeholder": "Slope: -",
                "result_label_prefix": "Slope:",
                "result_tip_placeholder": "Enter the distance and height values to get started.",
                "result_tip_ready": "Open the 3D view to inspect the slope profile from new angles.",
                "settings_button": "Settings",
                "settings_title": "Settings",
                "settings_language_label": "Language",
                "settings_theme_label": "Theme",
                "settings_theme_light": "Light",
                "settings_theme_dark": "Dark",
                "settings_save": "Save",
                "settings_cancel": "Cancel",
                "view_3d_button": "3D View",
                "view_2d_button": "2D View",
                "view_3d_disabled_tooltip": "Calculate the slope before opening the 3D view.",
                "view_3d_enabled_tooltip": "Display the slope using an interactive 3D chart.",
                "view_2d_enabled_tooltip": "Display the slope using the standard 2D chart.",
                "input_error_title": "Input Error",
                "input_error_message": "Please enter valid numerical values.",
                "plot_title": "Slope Visualization",
                "plot_3d_title": "3D Slope Visualization",
                "plot_distance_label": "Distance (m)",
                "plot_height_label": "Height (m)",
                "plot_depth_label": "Lateral Offset (m)",
                "plot_legend_distance": "Distance",
                "plot_legend_height": "Height",
                "plot_legend_slope": "Slope Line",
                "plot_annotation": "Slope: {value}",
            },
        }
        self.language_display = {
            "tr": {"tr": "Türkçe", "en": "İngilizce"},
            "en": {"tr": "Turkish", "en": "English"},
        }
        self.current_language = "tr"
        self.last_result_value = None
        self.current_view_mode = "2d"
        self.current_figure = None

        self.setGeometry(100, 100, 520, 420)
        self.last_inputs = None

        main_layout = QVBoxLayout()
        main_layout.setSpacing(18)
        main_layout.setContentsMargins(28, 28, 28, 28)

        self.header_label = QLabel()
        self.header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.header_label.setObjectName("headerLabel")
        main_layout.addWidget(self.header_label)

        self.subtitle_label = QLabel()
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle_label.setObjectName("subtitleLabel")
        self.subtitle_label.setWordWrap(True)
        main_layout.addWidget(self.subtitle_label)

        form_card = QFrame()
        form_card.setObjectName("formCard")
        form_layout = QGridLayout()
        form_layout.setHorizontalSpacing(16)
        form_layout.setVerticalSpacing(12)
        form_card.setLayout(form_layout)

        self.label1 = QLabel()
        form_layout.addWidget(self.label1, 0, 0)
        self.input_distance = QLineEdit()
        form_layout.addWidget(self.input_distance, 0, 1)

        self.label2 = QLabel()
        form_layout.addWidget(self.label2, 1, 0)
        self.input_h1 = QLineEdit()
        form_layout.addWidget(self.input_h1, 1, 1)

        self.label3 = QLabel()
        form_layout.addWidget(self.label3, 2, 0)
        self.input_h2 = QLineEdit()
        form_layout.addWidget(self.input_h2, 2, 1)

        controls_row = QHBoxLayout()
        controls_row.setSpacing(18)

        self.calc_button = QPushButton()
        self.calc_button.setObjectName("calculateButton")
        self.calc_button.clicked.connect(self.calculate_slope)
        calc_button_policy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        calc_button_policy.setHorizontalStretch(1)
        self.calc_button.setSizePolicy(calc_button_policy)
        self.calc_button.setMinimumWidth(150)
        controls_row.addWidget(self.calc_button)

        self.view3d_button = QPushButton()
        self.view3d_button.setObjectName("view3dButton")
        self.view3d_button.clicked.connect(self.toggle_view_mode)
        view_button_policy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        view_button_policy.setHorizontalStretch(1)
        self.view3d_button.setSizePolicy(view_button_policy)
        self.view3d_button.setMinimumWidth(150)
        controls_row.addWidget(self.view3d_button)

        controls_row.addStretch()

        self.settings_button = QPushButton()
        self.settings_button.setObjectName("settingsButton")
        self.settings_button.clicked.connect(self.open_settings_dialog)
        self.settings_button.setMinimumWidth(120)
        controls_row.addWidget(self.settings_button)

        form_layout.addLayout(controls_row, 3, 0, 1, 2)

        main_layout.addWidget(form_card)

        result_card = QFrame()
        result_card.setObjectName("resultCard")
        result_layout = QVBoxLayout()
        result_layout.setSpacing(6)
        result_card.setLayout(result_layout)

        self.result_label = QLabel()
        self.result_label.setObjectName("resultLabel")
        result_layout.addWidget(self.result_label)

        self.tip_label = QLabel()
        self.tip_label.setObjectName("resultTipLabel")
        self.tip_label.setWordWrap(True)
        result_layout.addWidget(self.tip_label)

        main_layout.addWidget(result_card)

        self.setLayout(main_layout)
        self.apply_language()
        self.apply_theme()

    def calculate_slope(self):
        try:
            h_distance = float(self.input_distance.text())
            h1 = float(self.input_h1.text())
            h2 = float(self.input_h2.text())
            slope = compute_slope(h_distance, h1, h2)
            slope_text = f"{slope:.2f}%"
            self.last_result_value = slope_text
            self.last_inputs = (h_distance, h1, h2)
            prefix = self.translations[self.current_language]["result_label_prefix"]
            self.result_label.setText(f"{prefix} {slope_text}")
            self.current_view_mode = "2d"
            self.plot_graph(h_distance, h1, h2, slope)
            texts = self.translations[self.current_language]
            self.tip_label.setText(texts["result_tip_ready"])
            self.update_view3d_button_state(texts)
        except ValueError:
            texts = self.translations[self.current_language]
            QMessageBox.critical(self, texts["input_error_title"], texts["input_error_message"])

    def plot_graph(self, distance, h1, h2, slope):
        texts = self.translations[self.current_language]
        style = "dark_background" if self.current_theme == "dark" else "default"

        with plt.style.context(style):
            fig, ax = plt.subplots(figsize=(6, 4))
            self._register_figure(fig)
            ax.plot(
                [0, distance],
                [h1, h1],
                linestyle="-",
                color="#ff6b6b",
                linewidth=2,
                label=texts["plot_legend_distance"],
            )
            ax.plot(
                [distance, distance],
                [h1, h2],
                linestyle="dashed",
                color="#bbbbbb",
                linewidth=2,
                label=texts["plot_legend_height"],
            )
            ax.plot(
                [0, distance],
                [h1, h2],
                marker="o",
                linestyle="-",
                color="#4d96ff",
                linewidth=2,
                label=texts["plot_legend_slope"],
            )

            ax.set_xlabel(texts["plot_distance_label"])
            ax.set_ylabel(texts["plot_height_label"])
            ax.set_title(texts["plot_title"])
            ax.legend()
            ax.grid(True)
            annotation = texts["plot_annotation"].format(value=f"{slope:.2f}%")
            ax.text(
                0.05 * distance if distance else 0,
                max(h1, h2) - 1 if h1 != h2 else h1,
                annotation,
                fontsize=12,
                color="#ffffff" if self.current_theme == "dark" else "#000000",
                bbox=dict(
                    facecolor="#333333" if self.current_theme == "dark" else "white",
                    alpha=0.5,
                ),
            )
            fig.tight_layout()
            plt.show()

    def toggle_view_mode(self):
        if not self.last_inputs:
            return
        distance, h1, h2 = self.last_inputs
        slope = compute_slope(distance, h1, h2)
        if self.current_view_mode == "2d":
            self.plot_3d_graph(distance, h1, h2, slope)
            self.current_view_mode = "3d"
        else:
            self.plot_graph(distance, h1, h2, slope)
            self.current_view_mode = "2d"
        self.update_view3d_button_state()

    def plot_3d_graph(self, distance, h1, h2, slope):
        texts = self.translations[self.current_language]
        style = "dark_background" if self.current_theme == "dark" else "default"

        with plt.style.context(style):
            fig = plt.figure(figsize=(6, 4))
            self._register_figure(fig)
            ax = fig.add_subplot(111, projection="3d")

            x_values = [0, distance]
            y_values = [0, 0]
            z_values = [h1, h2]

            ax.plot(
                x_values,
                y_values,
                [h1, h1],
                linestyle="-",
                color="#ff6b6b",
                linewidth=2,
                label=texts["plot_legend_distance"],
            )
            ax.plot(
                [distance, distance],
                [0, 0],
                [h1, h2],
                linestyle="dashed",
                color="#bbbbbb",
                linewidth=2,
                label=texts["plot_legend_height"],
            )
            ax.plot(
                x_values,
                y_values,
                z_values,
                marker="o",
                linestyle="-",
                color="#4d96ff",
                linewidth=3,
                label=texts["plot_legend_slope"],
            )

            ax.set_xlabel(texts["plot_distance_label"])
            ax.set_ylabel(texts["plot_depth_label"])
            ax.set_zlabel(texts["plot_height_label"])
            ax.set_title(texts["plot_3d_title"])
            ax.legend()

            annotation = texts["plot_annotation"].format(value=f"{slope:.2f}%")
            annotation_x = distance * 0.5
            annotation_z = h1 + (h2 - h1) * 0.5
            ax.text(
                annotation_x,
                0.2 * max(distance, 1),
                annotation_z,
                annotation,
                fontsize=11,
                color="#ffffff" if self.current_theme == "dark" else "#000000",
            )

            fig.tight_layout()
            plt.show()

    def _close_current_figure(self):
        if self.current_figure is not None:
            with suppress(Exception):
                plt.close(self.current_figure)
            self.current_figure = None

    def _register_figure(self, figure):
        self._close_current_figure()
        self.current_figure = figure
        if figure.canvas is not None:
            figure.canvas.mpl_connect("close_event", self._on_figure_closed)

    def _on_figure_closed(self, event):
        if event is not None and getattr(event, "canvas", None) is not None:
            figure = event.canvas.figure
            if figure is self.current_figure:
                self.current_figure = None

    def open_settings_dialog(self):
        dialog = SettingsDialog(
            self.current_language,
            self.current_theme,
            self.translations,
            self.language_display,
        )
        if dialog.exec():
            language_changed = dialog.selected_language != self.current_language
            theme_changed = dialog.selected_theme != self.current_theme
            self.current_language = dialog.selected_language
            self.current_theme = dialog.selected_theme
            if language_changed:
                self.apply_language()
            if theme_changed:
                self.apply_theme()

    def apply_language(self):
        texts = self.translations[self.current_language]
        self.setWindowTitle(texts["window_title"])
        self.label1.setText(texts["distance_label"])
        self.label2.setText(texts["first_height_label"])
        self.label3.setText(texts["second_height_label"])
        self.calc_button.setText(texts["calculate_button"])
        self.settings_button.setText(texts["settings_button"])
        self.header_label.setText(texts["header_title"])
        self.subtitle_label.setText(texts["subtitle"])

        if self.last_result_value is None:
            self.result_label.setText(texts["result_label_placeholder"])
            self.tip_label.setText(texts["result_tip_placeholder"])
        else:
            prefix = texts["result_label_prefix"]
            self.result_label.setText(f"{prefix} {self.last_result_value}")
            self.tip_label.setText(texts["result_tip_ready"])

        self.update_view3d_button_state(texts)

    def apply_theme(self):
        self.setStyleSheet(self.load_styles(self.current_theme))

    def load_styles(self, theme="light"):
        return self.theme_styles.get(theme, self.theme_styles["light"])

    def update_view3d_button_state(self, texts=None):
        if texts is None:
            texts = self.translations[self.current_language]
        if self.last_inputs is None:
            self.current_view_mode = "2d"
            self.view3d_button.setEnabled(False)
            self.view3d_button.setText(texts["view_3d_button"])
            self.view3d_button.setToolTip(texts["view_3d_disabled_tooltip"])
        else:
            self.view3d_button.setEnabled(True)
            if self.current_view_mode == "3d":
                self.view3d_button.setText(texts["view_2d_button"])
                self.view3d_button.setToolTip(texts["view_2d_enabled_tooltip"])
            else:
                self.view3d_button.setText(texts["view_3d_button"])
                self.view3d_button.setToolTip(texts["view_3d_enabled_tooltip"])


def run():
    """Launch the slope calculator application."""
    app = QApplication(sys.argv)
    win = SlopeCalculator()
    win.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(run())
