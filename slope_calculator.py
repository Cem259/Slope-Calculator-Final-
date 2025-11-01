import sys

import numpy as np
import matplotlib.pyplot as plt
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
)
from PyQt6.QtGui import QFont


def compute_slope(distance, h1, h2):
    """Compute the slope percentage between two heights over a horizontal distance."""
    return ((h2 - h1) / distance) * 100 if distance != 0 else float('inf')

class ModernStyledWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(self.load_styles())
        self.setFont(QFont("Arial", 10))
    
    def load_styles(self):
        return """
        QWidget {
            background-color: #f4f4f4;
            color: #333;
        }
        QLabel {
            font-size: 12pt;
        }
        QLineEdit {
            border: 2px solid #ccc;
            border-radius: 5px;
            padding: 5px;
            font-size: 12pt;
            color: red;
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
        """

class SlopeCalculator(ModernStyledWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Slope Calculator")
        self.setGeometry(100, 100, 400, 300)
        layout = QVBoxLayout()
        
        self.label1 = QLabel("Horizontal Distance:")
        layout.addWidget(self.label1)
        self.input_distance = QLineEdit()
        layout.addWidget(self.input_distance)
        
        self.label2 = QLabel("First Point Height:")
        layout.addWidget(self.label2)
        self.input_h1 = QLineEdit()
        layout.addWidget(self.input_h1)
        
        self.label3 = QLabel("Second Point Height:")
        layout.addWidget(self.label3)
        self.input_h2 = QLineEdit()
        layout.addWidget(self.input_h2)
        
        self.calc_button = QPushButton("Calculate Slope")
        self.calc_button.clicked.connect(self.calculate_slope)
        layout.addWidget(self.calc_button)
        
        self.result_label = QLabel("Slope: ")
        layout.addWidget(self.result_label)
        
        self.setLayout(layout)
    
    def calculate_slope(self):
        try:
            h_distance = float(self.input_distance.text())
            h1 = float(self.input_h1.text())
            h2 = float(self.input_h2.text())
            slope = compute_slope(h_distance, h1, h2)
            self.result_label.setText(f"Slope: {slope:.2f}%")
            self.plot_graph(h_distance, h1, h2, slope)
        except ValueError:
            QMessageBox.critical(self, "Input Error", "Please enter valid numerical values.")
    
    def plot_graph(self, distance, h1, h2, slope):
        plt.figure(figsize=(6, 4))
        plt.plot([0, distance], [h1, h1], linestyle='-', color='red', linewidth=2, label='Distance')
        plt.plot([distance, distance], [h1, h2], linestyle='dashed', color='black', linewidth=2, label='Height')
        plt.plot([0, distance], [h1, h2], marker='o', linestyle='-', color='blue', linewidth=2, label='Slope Line')
        
        plt.xlabel("Distance (m)")
        plt.ylabel("Height (m)")
        plt.title("Slope Visualization")
        plt.legend()
        plt.grid(True)
        plt.text(0.05 * distance, max(h1, h2) - 1, f"Slope: {slope:.2f}%", fontsize=12, color='black', bbox=dict(facecolor='white', alpha=0.5))
        plt.show()

def run():
    """Launch the slope calculator application."""
    app = QApplication(sys.argv)
    win = SlopeCalculator()
    win.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(run())
