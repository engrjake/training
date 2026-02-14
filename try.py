import tkinter as tk
from tkinter import messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def calculate_capacity():
    try:
        L = float(entry_L.get())
        D = float(entry_D.get())
        ks = float(entry_ks.get())   # shaft spring constant
        kb = float(entry_kb.get())   # base spring constant
        dz = 0.1                     # depth increment (m)

        if L <= 0 or D <= 0:
            raise ValueError

        # Depth discretization
        z = np.arange(0, L, dz)

        # Shaft resistance accumulation
        shaft_force = ks * z * np.pi * D * dz
        Qs = np.sum(shaft_force)

        # Base resistance
        Ab = np.pi * D**2 / 4
        Qb = kb * Ab

        Qu = Qs + Qb

        result_label.config(
            text=(
                f"Shaft Capacity (Qs): {Qs:.1f} kN\n"
                f"Base Capacity (Qb): {Qb:.1f} kN\n"
                f"Ultimate Capacity (Qu): {Qu:.1f} kN"
            )
        )

        # Load distribution diagram
        cumulative_load = np.cumsum(shaft_force)

        for widget in plot_frame.winfo_children():
            widget.destroy()

        fig, ax = plt.subplots(figsize=(5, 5), dpi=100)
        ax.plot(cumulative_load, z, linewidth=2)
        ax.invert_yaxis()

        ax.set_title("Pile Load–Depth Diagram")
        ax.set_xlabel("Axial Load (kN)")
        ax.set_ylabel("Depth (m)")
        ax.grid(True)

        canvas = FigureCanvasTkAgg(fig, master=plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack()

    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid positive values.")

# ---------------- GUI ---------------- #
root = tk.Tk()
root.title("Bored Pile Capacity (JRA Method)")
root.geometry("700x650")

input_frame = tk.Frame(root)
input_frame.pack(pady=10)

tk.Label(input_frame, text="Pile Length L (m)").grid(row=0, column=0, pady=5, sticky="e")
entry_L = tk.Entry(input_frame)
entry_L.grid(row=0, column=1)

tk.Label(input_frame, text="Pile Diameter D (m)").grid(row=1, column=0, pady=5, sticky="e")
entry_D = tk.Entry(input_frame)
entry_D.grid(row=1, column=1)

tk.Label(input_frame, text="Shaft Spring Constant ks (kN/m³)").grid(row=2, column=0, pady=5, sticky="e")
entry_ks = tk.Entry(input_frame)
entry_ks.grid(row=2, column=1)

tk.Label(input_frame, text="Base Spring Constant kb (kN/m²)").grid(row=3, column=0, pady=5, sticky="e")
entry_kb = tk.Entry(input_frame)
entry_kb.grid(row=3, column=1)

tk.Button(root, text="Calculate Capacity", command=calculate_capacity).pack(pady=10)

result_label = tk.Label(root, text="", font=("Arial", 11), fg="blue", justify="left")
result_label.pack(pady=5)

plot_frame = tk.Frame(root)
plot_frame.pack(fill=tk.BOTH, expand=True)

root.mainloop()
