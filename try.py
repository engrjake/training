import sys
import numpy as np
import pyvista as pv
from PyQt5 import QtWidgets
from pyvistaqt import QtInteractor

PHI_FLEXURE = 0.9
PHI_SHEAR = 0.75

class AbutmentDesignApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Abutment Wall Design (AASHTO – Visualized Forces)")
        self.resize(1300, 800)

        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        layout = QtWidgets.QHBoxLayout(central)

        # ---------- INPUT PANEL ----------
        left = QtWidgets.QVBoxLayout()

        self.H = self.add_input(left, "Wall Height H (m)")
        self.gamma = self.add_input(left, "Soil Unit Weight γ (kN/m³)")
        self.phi = self.add_input(left, "Soil Friction Angle φ (deg)")
        self.q = self.add_input(left, "Surcharge Load q (kPa)")

        self.fc = self.add_input(left, "Concrete Strength f'c (MPa)")
        self.fy = self.add_input(left, "Steel Yield Strength fy (MPa)")
        self.t = self.add_input(left, "Wall Thickness (m)")
        self.d = self.add_input(left, "Effective Depth d (m)")
        self.As = self.add_input(left, "Steel Area As (m²/m)")

        run_btn = QtWidgets.QPushButton("Run Design & Visualize")
        run_btn.clicked.connect(self.design)
        left.addWidget(run_btn)

        self.result_label = QtWidgets.QLabel("")
        left.addWidget(self.result_label)

        left.addStretch()
        layout.addLayout(left, 1)

        # ---------- PYVISTA PANEL ----------
        self.plotter = QtInteractor(self)
        layout.addWidget(self.plotter.interactor, 3)

    def add_input(self, layout, label):
        layout.addWidget(QtWidgets.QLabel(label))
        box = QtWidgets.QLineEdit()
        layout.addWidget(box)
        return box

    def design(self):
        try:
            # ---- INPUTS ----
            H = float(self.H.text())
            gamma = float(self.gamma.text())
            phi = np.radians(float(self.phi.text()))
            q = float(self.q.text())

            fc = float(self.fc.text())
            fy = float(self.fy.text())
            t = float(self.t.text())
            d = float(self.d.text())
            As = float(self.As.text())

            # ---- EARTH PRESSURE ----
            Ka = np.tan(np.pi / 4 - phi / 2) ** 2
            z = np.linspace(0, H, 40)
            dz = z[1] - z[0]

            p = Ka * gamma * z + Ka * q  # kN/m²
            V = np.cumsum(p * dz)
            M = np.cumsum(V * dz)

            # ---- CAPACITY ----
            a = As * fy / (0.85 * fc * t)
            Mn = As * fy * (d - a / 2)
            phiMn = PHI_FLEXURE * Mn

            Vn = 0.17 * np.sqrt(fc) * t * d
            phiVn = PHI_SHEAR * Vn

            demand_ratio = np.maximum(M / phiMn, V / phiVn)

            self.result_label.setText(
                f"Ka = {Ka:.3f}\n"
                f"Max Moment = {M.max():.1f} kN·m/m\n"
                f"Max Shear = {V.max():.1f} kN/m\n"
                f"Max Demand Ratio = {demand_ratio.max():.2f}"
            )

            self.visualize_wall_and_forces(z, p, demand_ratio, H, t)

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", str(e))

    def visualize_wall_and_forces(self, z, pressure, ratio, H, t):
        self.plotter.clear()

        # ---- WALL GEOMETRY ----
        wall = pv.Box(bounds=(-t/2, t/2, -0.3, 0.3, -H, 0))
        self.plotter.add_mesh(wall, color="lightgray", opacity=0.6)

        # ---- DEMAND POINTS ----
        pts = np.column_stack((np.zeros_like(z), np.zeros_like(z), -z))
        cloud = pv.PolyData(pts)
        cloud["DemandRatio"] = ratio

        self.plotter.add_mesh(
            cloud,
            scalars="DemandRatio",
            cmap="jet",
            point_size=12,
            render_points_as_spheres=True
        )

        # ---- EARTH PRESSURE ARROWS ----
        arrow_scale = 0.02
        for zi, pi in zip(z[::3], pressure[::3]):
            start = np.array([-t/2 - 0.05, 0, -zi])
            direction = np.array([-pi * arrow_scale, 0, 0])
            arrow = pv.Arrow(start=start, direction=direction, scale="auto")
            self.plotter.add_mesh(arrow, color="brown")

        # ---- GROUND LINE ----
        ground = pv.Line(pointa=(-1, 0, 0), pointb=(1, 0, 0))
        self.plotter.add_mesh(ground, color="black", line_width=3)

        self.plotter.add_scalar_bar("Demand / Capacity")
        self.plotter.add_axes()
        self.plotter.show_grid()
        self.plotter.reset_camera()

# -------- RUN --------
app = QtWidgets.QApplication(sys.argv)
window = AbutmentDesignApp()
window.show()
sys.exit(app.exec_())