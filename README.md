# Slope Calculator V1

Modernized PyQt6 desktop application for slope analysis with bilingual interface, 2D/3D visualisation, and CSV tooling.

## Features

- Modular PyQt6 application with toolbar icons via QtAwesome.
- Live slope conversions across percent, angle, rise/run, and grade ratio.
- Polyline profile support with coloured segment table and interactive Matplotlib plot.
- Plotly-powered 3D view (with PyQtGraph fallback) embedded in the UI.
- CSV import/export for both basic and polyline profiles plus JSON project saves.
- Runtime theme (light/dark) and language (EN/TR) switching with persistent status feedback.

## Installation

Create a virtual environment (recommended) and install the dependencies:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
```

## Running

Launch the application via the new package entry point:

```bash
python -m app.main
```

On startup the demo values match the acceptance test (distance 100, heights 10 → 18). Switch views from the toolbar. CSV samples are provided in the `samples/` directory.

## Optional Dependencies

- `PyQt6-WebEngine` enables the Plotly 3D view. If it is missing, the app attempts to fall back to `pyqtgraph` for a lightweight 3D scene.

## Testing Checklist

1. Adjust inputs (e.g., 100 m, 10 m, 18 m) and verify calculated slope metrics update instantly.
2. Import `samples/polyline.csv` and confirm the 2D profile colours high-gradient segments and table values.
3. Toggle between light/dark themes and English/Turkish to ensure all strings and palette updates apply.
4. Export a profile to CSV and re-import to validate round-tripping of the computed data.
5. Interact with the 3D view (orbit/zoom) and use toolbar buttons to switch between 2D and 3D.

