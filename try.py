import numpy as np
import pyvista as pv

# ---------------- INPUT PARAMETERS ----------------
L = 6.0        # beam length (m)
P = 20.0       # point load (kN)
a = 2.5        # load distance from left support (m)

b = 0.3        # beam width (m)
h = 0.5        # beam height (m)

# ---------------- REACTIONS ----------------
RA = P * (L - a) / L
RB = P * a / L

print(f"RA = {RA:.2f} kN")
print(f"RB = {RB:.2f} kN")

# ---------------- BEAM GEOMETRY ----------------
nx = 100
x = np.linspace(0, L, nx)

# rectangular beam mesh
beam = pv.Box(bounds=(0, L, -b/2, b/2, -h/2, h/2))

# ---------------- SECTION PROPERTIES ----------------
I = b * h**3 / 12
y_max = h / 2

# ---------------- BENDING MOMENT ----------------
M = np.zeros_like(x)

for i, xi in enumerate(x):
    if xi < a:
        M[i] = RA * xi
    else:
        M[i] = RA * xi - P * (xi - a)

# ---------------- STRESS CALCULATION ----------------
sigma = M * y_max / I  # max bending stress

# normalize stress for visualization
stress_norm = (sigma - sigma.min()) / (sigma.max() - sigma.min())

# Map stress along beam length
cell_centers = beam.cell_centers().points
stress_field = np.interp(cell_centers[:, 0], x, stress_norm)

beam["Stress"] = stress_field

# ---------------- VISUALIZATION ----------------
plotter = pv.Plotter()
plotter.add_mesh(
    beam,
    scalars="Stress",
    cmap="jet",
    show_edges=True,
)

plotter.add_axes()
plotter.add_text("Beam Bending Stress Visualization", font_size=12)

plotter.show()