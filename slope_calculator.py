import sys

import matplotlib.pyplot as plt
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QDialog,
    QComboBox,
    QHBoxLayout,
)
from PyQt6.QtGui import QFont


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
                background-color: #f4f4f4;
                color: #333;
            }
            QLabel {
                font-size: 12pt;
                color: #333;
            }
            QLineEdit {
                border: 2px solid #ccc;
                border-radius: 5px;
                padding: 5px;
                font-size: 12pt;
                color: #333;
                background-color: #ffffff;
            }
            QPushButton {
                background-color: #0078D7;
                color: white;
                border-radius: 5px;
                padding: 8px;
                font-size: 12pt;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            """,
            "dark": """
            QWidget {
                background-color: #1e1e1e;
                color: #f4f4f4;
            }
            QLabel {
                font-size: 12pt;
                color: #f4f4f4;
            }
            QLineEdit {
                border: 2px solid #555;
                border-radius: 5px;
                padding: 5px;
                font-size: 12pt;
                color: #f4f4f4;
                background-color: #2b2b2b;
            }
            QPushButton {
                background-color: #3a7bd5;
                color: white;
                border-radius: 5px;
                padding: 8px;
                font-size: 12pt;
            }
            QPushButton:hover {
                background-color: #2f66b8;
            }
            """,
        }
        super().__init__()

        self.translations = {
            "tr": {
                "window_title": "Eğim Hesaplayıcı",
                "distance_label": "Yatay Mesafe:",
                "first_height_label": "Birinci Nokta Yüksekliği:",
                "second_height_label": "İkinci Nokta Yüksekliği:",
                "calculate_button": "Eğimi Hesapla",
                "result_label_placeholder": "Eğim: -",
                "result_label_prefix": "Eğim:",
                "settings_button": "Ayarlar",
                "settings_title": "Ayarlar",
                "settings_language_label": "Dil",
                "settings_theme_label": "Görünüm",
                "settings_theme_light": "Açık",
                "settings_theme_dark": "Koyu",
                "settings_save": "Kaydet",
                "settings_cancel": "İptal",
                "input_error_title": "Giriş Hatası",
                "input_error_message": "Lütfen geçerli sayısal değerler girin.",
                "plot_title": "Eğim Görselleştirmesi",
                "plot_distance_label": "Mesafe (m)",
                "plot_height_label": "Yükseklik (m)",
                "plot_legend_distance": "Mesafe",
                "plot_legend_height": "Yükseklik",
                "plot_legend_slope": "Eğim Çizgisi",
                "plot_annotation": "Eğim: {value}",
            },
            "en": {
                "window_title": "Slope Calculator",
                "distance_label": "Horizontal Distance:",
                "first_height_label": "First Point Height:",
                "second_height_label": "Second Point Height:",
                "calculate_button": "Calculate Slope",
                "result_label_placeholder": "Slope: -",
                "result_label_prefix": "Slope:",
                "settings_button": "Settings",
                "settings_title": "Settings",
                "settings_language_label": "Language",
                "settings_theme_label": "Theme",
                "settings_theme_light": "Light",
                "settings_theme_dark": "Dark",
                "settings_save": "Save",
                "settings_cancel": "Cancel",
                "input_error_title": "Input Error",
                "input_error_message": "Please enter valid numerical values.",
                "plot_title": "Slope Visualization",
                "plot_distance_label": "Distance (m)",
                "plot_height_label": "Height (m)",
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

        self.setGeometry(100, 100, 400, 320)
        layout = QVBoxLayout()

        self.label1 = QLabel()
        layout.addWidget(self.label1)
        self.input_distance = QLineEdit()
        layout.addWidget(self.input_distance)

        self.label2 = QLabel()
        layout.addWidget(self.label2)
        self.input_h1 = QLineEdit()
        layout.addWidget(self.input_h1)

        self.label3 = QLabel()
        layout.addWidget(self.label3)
        self.input_h2 = QLineEdit()
        layout.addWidget(self.input_h2)

        self.calc_button = QPushButton()
        self.calc_button.clicked.connect(self.calculate_slope)
        layout.addWidget(self.calc_button)

        self.result_label = QLabel()
        layout.addWidget(self.result_label)

        self.settings_button = QPushButton()
        self.settings_button.clicked.connect(self.open_settings_dialog)
        layout.addWidget(self.settings_button)

        self.setLayout(layout)
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
            prefix = self.translations[self.current_language]["result_label_prefix"]
            self.result_label.setText(f"{prefix} {slope_text}")
            self.plot_graph(h_distance, h1, h2, slope)
        except ValueError:
            texts = self.translations[self.current_language]
            QMessageBox.critical(self, texts["input_error_title"], texts["input_error_message"])

    def plot_graph(self, distance, h1, h2, slope):
        texts = self.translations[self.current_language]
        style = "dark_background" if self.current_theme == "dark" else "default"

        with plt.style.context(style):
            fig, ax = plt.subplots(figsize=(6, 4))
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

        if self.last_result_value is None:
            self.result_label.setText(texts["result_label_placeholder"])
        else:
            prefix = texts["result_label_prefix"]
            self.result_label.setText(f"{prefix} {self.last_result_value}")

    def apply_theme(self):
        self.setStyleSheet(self.load_styles(self.current_theme))

    def load_styles(self, theme="light"):
        return self.theme_styles.get(theme, self.theme_styles["light"])


def run():
    """Launch the slope calculator application."""
    app = QApplication(sys.argv)
    win = SlopeCalculator()
    win.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(run())
