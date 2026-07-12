import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import os
import sys

PHI = (1 + np.sqrt(5)) / 2


def eval_poly(coeffs, t):
    result = np.zeros_like(t, dtype=float)
    for i, c in enumerate(coeffs):
        result += c * t ** i
    return result


def eval_superformula(sf_params, theta):
    m, n1, n2, n3, a, b = sf_params
    t1 = np.abs(np.cos(m * theta / 4) / a)
    t2 = np.abs(np.sin(m * theta / 4) / b)
    with np.errstate(divide='ignore', invalid='ignore'):
        r = np.where(t1 == 0, 0, t1 ** n2) + np.where(t2 == 0, 0, t2 ** n3)
        r = np.where(r == 0, 0, r ** (-1.0 / n1))
    return r


class PolyartViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("PolyArt Viewer — Полиномиальный Рендерер")
        self.root.geometry("1200x800")
        self.root.configure(bg="#2a2a2a")

        self.data = None
        self.filepath = None

        self._build_ui()
        self._bind_keys()

    def _build_ui(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Dark.TFrame", background="#2a2a2a")
        style.configure("Dark.TLabel", background="#2a2a2a", foreground="#e0d8c8",
                         font=("Consolas", 10))
        style.configure("Header.TLabel", background="#2a2a2a", foreground="#c8a040",
                         font=("Consolas", 12, "bold"))
        style.configure("Dark.TButton", background="#3a3a3a", foreground="#e0d8c8",
                         font=("Consolas", 9))
        style.configure("Treeview", background="#1a1a1a", foreground="#e0d8c8",
                         fieldbackground="#1a1a1a", font=("Consolas", 9))
        style.configure("Treeview.Heading", background="#3a3a3a", foreground="#c8a040",
                         font=("Consolas", 9, "bold"))

        # Main paned window
        main_pane = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True)

        # === LEFT PANEL: файлы, слои, свойства ===
        left_frame = ttk.Frame(main_pane, style="Dark.TFrame")
        main_pane.add(left_frame, weight=1)

        # Заголовок
        ttk.Label(left_frame, text="◆ POLYART VIEWER",
                   style="Header.TLabel").pack(pady=(10, 5), anchor="w", padx=10)

        # Кнопки управления
        btn_frame = ttk.Frame(left_frame, style="Dark.TFrame")
        btn_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Button(btn_frame, text="📂 Открыть .polyart",
                    style="Dark.TButton",
                    command=self.open_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="💾 Экспорт PNG",
                    style="Dark.TButton",
                    command=self.export_png).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="🔄 Обновить",
                    style="Dark.TButton",
                    command=self.refresh).pack(side=tk.LEFT, padx=2)

        # Информация о файле
        self.info_frame = ttk.LabelFrame(left_frame, text=" Информация ",
                                          style="Dark.TFrame")
        self.info_frame.pack(fill=tk.X, padx=10, pady=5)

        self.info_labels = {}
        for key in ["name", "author", "format", "phi", "canvas_size", "objects"]:
            row = ttk.Frame(self.info_frame, style="Dark.TFrame")
            row.pack(fill=tk.X, padx=5, pady=1)
            ttk.Label(row, text=f"{key}:", width=14, style="Dark.TLabel").pack(side=tk.LEFT)
            lbl = ttk.Label(row, text="—", style="Dark.TLabel")
            lbl.pack(side=tk.LEFT)
            self.info_labels[key] = lbl

        # Слои — дерево объектов
        layers_label = ttk.Label(left_frame, text=" Слои и объекты:",
                                  style="Dark.TLabel")
        layers_label.pack(anchor="w", padx=10, pady=(10, 2))

        tree_frame = ttk.Frame(left_frame, style="Dark.TFrame")
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.tree = ttk.Treeview(tree_frame, show="tree headings",
                                  columns=("type", "color"))
        self.tree.heading("#0", text="Объект")
        self.tree.heading("type", text="Тип")
        self.tree.heading("color", text="Цвет")
        self.tree.column("#0", width=180)
        self.tree.column("type", width=100)
        self.tree.column("color", width=70)

        tree_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL,
                                     command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        # Формулы
        formulas_label = ttk.Label(left_frame, text=" Формулы:",
                                    style="Dark.TLabel")
        formulas_label.pack(anchor="w", padx=10, pady=(5, 2))

        self.formulas_text = tk.Text(left_frame, height=5, bg="#1a1a1a",
                                      fg="#c8a040", font=("Consolas", 9),
                                      insertbackground="#c8a040",
                                      relief=tk.FLAT, padx=8, pady=5)
        self.formulas_text.pack(fill=tk.X, padx=10, pady=5)

        # Статус бар
        self.status = ttk.Label(left_frame, text="Готов к загрузке .polyart",
                                 style="Dark.TLabel")
        self.status.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)

        # === RIGHT PANEL: холст matplotlib ===
        right_frame = ttk.Frame(main_pane, style="Dark.TFrame")
        main_pane.add(right_frame, weight=3)

        self.fig = Figure(figsize=(8, 8), facecolor="#f5efe0", dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor("#f5efe0")
        self.ax.set_aspect('equal')
        self.ax.axis('off')

        self.canvas = FigureCanvasTkAgg(self.fig, master=right_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        toolbar_frame = ttk.Frame(right_frame, style="Dark.TFrame")
        toolbar_frame.pack(fill=tk.X)
        self.toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
        self.toolbar.update()

    def _bind_keys(self):
        self.root.bind("<Control-o>", lambda e: self.open_file())
        self.root.bind("<Control-s>", lambda e: self.export_png())
        self.root.bind("<F5>", lambda e: self.refresh())
        self.root.bind("<Escape>", lambda e: self.root.quit())

    def open_file(self):
        path = filedialog.askopenfilename(
            title="Открыть .polyart",
            filetypes=[
                ("PolyArt файлы", "*.polyart"),
                ("JSON файлы", "*.json"),
                ("Все файлы", "*.*")
            ],
            initialdir=os.path.dirname(self.filepath) if self.filepath else "."
        )
        if not path:
            return
        try:
            with open(path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            self.filepath = path
            self.root.title(f"PolyArt Viewer — {os.path.basename(path)}")
            self._update_info()
            self._update_tree()
            self._update_formulas()
            self.render()
            self.status.config(text=f"Загружен: {os.path.basename(path)}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть файл:\n{e}")

    def _update_info(self):
        if not self.data:
            return
        meta = self.data.get("meta", {})
        canvas = self.data.get("canvas", {})
        total_obj = sum(len(l.get("objects", [])) for l in self.data.get("layers", []))

        self.info_labels["name"].config(text=meta.get("name", "—"))
        self.info_labels["author"].config(text=meta.get("author", "—"))
        self.info_labels["format"].config(text=f"polyart v{self.data.get('version', '?')}")
        self.info_labels["phi"].config(text=f"{meta.get('phi', PHI):.6f}")
        self.info_labels["canvas_size"].config(
            text=f"{canvas.get('width', '?')}×{canvas.get('height', '?')}")
        self.info_labels["objects"].config(text=str(total_obj))

    def _update_tree(self):
        self.tree.delete(*self.tree.get_children())
        if not self.data:
            return
        for layer in self.data.get("layers", []):
            layer_id = self.tree.insert("", "end",
                                         text=f"📁 {layer['name']}",
                                         values=("", ""))
            for i, obj in enumerate(layer.get("objects", [])):
                otype = obj.get("type", "parametric")
                color = obj.get("color", "?")
                fill_mark = "■" if obj.get("fill") else "□"
                n_coeffs = len(obj.get("poly_x", []))
                label = f"{fill_mark} [{i}] poly({n_coeffs - 1}°)"
                self.tree.insert(layer_id, "end",
                                  text=label,
                                  values=(otype, color))

    def _update_formulas(self):
        self.formulas_text.delete("1.0", tk.END)
        if not self.data:
            return
        for f in self.data.get("formulas", []):
            self.formulas_text.insert(tk.END, f"  {f['expr']}\n")

    def _on_select(self, event):
        pass  # Можно добавить подсветку объекта

    def render(self):
        if not self.data:
            return

        self.ax.clear()
        canvas = self.data.get("canvas", {})
        self.ax.set_xlim(canvas.get("xlim", [-5, 5]))
        self.ax.set_ylim(canvas.get("ylim", [-5, 5]))
        self.ax.set_facecolor(canvas.get("background", "#f5efe0"))
        self.ax.set_aspect('equal')
        self.ax.axis('off')

        for layer in self.data.get("layers", []):
            for obj in layer.get("objects", []):
                self._draw_object(obj)

        # Формулы на холсте
        for f in self.data.get("formulas", []):
            self.ax.text(f["x"], f["y"], f["expr"],
                         fontsize=f.get("fontsize", 8),
                         fontfamily='serif',
                         color=f.get("color", "#8a6a4a"),
                         fontstyle='italic',
                         ha=f.get("ha", "left"))

        self.canvas.draw()

    def _draw_object(self, obj):
        otype = obj.get("type", "parametric")
        color = obj.get("color", "#1a1008")
        alpha = obj.get("alpha", 1.0)
        lw = obj.get("linewidth", 1.0)
        style_str = obj.get("style", "solid")
        n_pts = obj.get("n_points", 300)

        ls = {"solid": "-", "dashed": "--", "dotted": ":"}.get(style_str, "-")

        if otype in ("parametric", "parametric_fill"):
            t_range = obj.get("t_range", [0, 1])
            t = np.linspace(t_range[0], t_range[1], n_pts)
            x = eval_poly(obj.get("poly_x", [0]), t)
            y = eval_poly(obj.get("poly_y", [0]), t)

            fill_color = obj.get("fill_color", color)
            if obj.get("fill", False):
                fill_alpha = obj.get("fill_alpha", 0.5)
                self.ax.fill(x, y, color=fill_color, alpha=fill_alpha)

            self.ax.plot(x, y, color=color, alpha=alpha, linewidth=lw, linestyle=ls)

        elif otype == "superformula":
            sf_params = obj.get("sf_params", [6, 1, 1, 1, 1, 1])
            center = obj.get("center", [0, 0])
            scale = obj.get("scale", 1.0)
            theta = np.linspace(0, 2 * np.pi, n_pts)
            r = eval_superformula(sf_params, theta)
            x = center[0] + scale * r * np.cos(theta)
            y = center[1] + scale * r * np.sin(theta)

            fill_color = obj.get("fill_color", color)
            if obj.get("fill", False):
                fill_alpha = obj.get("fill_alpha", 0.5)
                self.ax.fill(x, y, color=fill_color, alpha=fill_alpha)

            self.ax.plot(x, y, color=color, alpha=alpha, linewidth=lw, linestyle=ls)

    def export_png(self):
        if not self.data:
            messagebox.showwarning("Внимание", "Сначала откройте .polyart файл")
            return
        path = filedialog.asksaveasfilename(
            title="Экспорт в PNG",
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("SVG", "*.svg"), ("PDF", "*.pdf")],
            initialfile=os.path.splitext(os.path.basename(self.filepath))[0] + ".png"
        )
        if not path:
            return
        try:
            self.fig.savefig(path, dpi=200, bbox_inches='tight',
                              facecolor=self.data.get("canvas", {}).get("background", "#f5efe0"))
            self.status.config(text=f"Экспортирован: {os.path.basename(path)}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка экспорта:\n{e}")

    def refresh(self):
        if self.filepath:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            self.render()
            self.status.config(text="Обновлено")


def main():
    root = tk.Tk()
    app = PolyartViewer(root)

    # Открыть файл из командной строки
    if len(sys.argv) > 1 and os.path.isfile(sys.argv[1]):
        app.filepath = sys.argv[1]
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            app.data = json.load(f)
        app.root.title(f"PolyArt Viewer — {os.path.basename(sys.argv[1])}")
        app._update_info()
        app._update_tree()
        app._update_formulas()
        app.render()

    root.mainloop()


if __name__ == "__main__":
    main()
