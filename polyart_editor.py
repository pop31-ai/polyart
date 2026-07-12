import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
import json
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from matplotlib.patches import Polygon as MplPolygon
import copy, os, sys

PHI = (1 + np.sqrt(5)) / 2


def eval_poly(coeffs, t):
    r = np.zeros_like(t, dtype=float)
    for i, c in enumerate(coeffs):
        r += c * t ** i
    return r


def eval_superformula(sf_params, theta):
    m, n1, n2, n3, a, b = sf_params
    t1 = np.abs(np.cos(m * theta / 4) / a)
    t2 = np.abs(np.sin(m * theta / 4) / b)
    with np.errstate(divide='ignore', invalid='ignore'):
        r = np.where(t1 == 0, 0, t1 ** n2) + np.where(t2 == 0, 0, t2 ** n3)
        r = np.where(r == 0, 0, r ** (-1.0 / n1))
    return r


def default_obj():
    return {
        "type": "parametric",
        "poly_x": [0.0, 1.0],
        "poly_y": [0.0, 1.0],
        "t_range": [0.0, 1.0],
        "n_points": 300,
        "color": "#1a1008",
        "alpha": 1.0,
        "linewidth": 1.5,
        "fill": False,
        "fill_alpha": 0.5,
        "fill_color": "#c8a888",
        "style": "solid",
    }


def default_layer(name="Слой 1"):
    return {"name": name, "objects": []}


def default_data():
    return {
        "format": "polyart",
        "version": "1.0.0",
        "meta": {"name": "Новый файл", "author": "Artist",
                  "description": "", "phi": PHI},
        "canvas": {"width": 10, "height": 10, "background": "#f5efe0",
                    "xlim": [-5, 5], "ylim": [-5, 5]},
        "layers": [default_layer()],
        "formulas": [],
    }


PRESETS = {
    "Эллипс": {"poly_x": [0, 0, -0.65, 0, 0.054, 0, -0.0018],
                "poly_y": [0, 1.8, 0, -0.3, 0, 0.015, 0],
                "t_range": [0, 6.283], "fill": True,
                "fill_color": "#e0c8a8", "color": "#c8a888"},
    "Парабола": {"poly_x": [-2, 4], "poly_y": [0, 1],
                  "t_range": [0, 1], "linewidth": 2.0},
    "Кубика": {"poly_x": [-1, 0, 0, 2], "poly_y": [-1, 0, 2, -1],
               "t_range": [0, 1], "linewidth": 2.0},
    "Синусоида": {"poly_x": [-3, 6], "poly_y": [0, 0],
                   "t_range": [0, 3.14159], "linewidth": 1.5,
                   "n_points": 500},
    "Спираль": {"poly_x": [0, 0.3, 0, -0.02, 0, 0.0005],
                 "poly_y": [0, 0, 0.3, 0, -0.02, 0],
                 "t_range": [0, 12.566], "n_points": 500,
                 "linewidth": 1.5},
    "Круг": {"poly_x": [0, 0, -0.5, 0, 0.0417, 0, -0.00139],
              "poly_y": [0, 0.5, 0, -0.0833, 0, 0.00417, 0],
              "t_range": [0, 6.283], "fill": True,
              "fill_color": "#e0c8a8", "color": "#c8a888"},
    "Цветок": {"type": "superformula", "sf_params": [6, 1, 1, 1, 1, 1],
               "center": [0, 0], "scale": 1.0,
               "fill": True, "fill_color": "#d89090"},
    "Звезда": {"type": "superformula", "sf_params": [5, 2, 7, 7, 1, 1],
               "center": [0, 0], "scale": 1.0,
               "fill": True, "fill_color": "#c8a040"},
}


class PolyartEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("PolyArt Editor — Редактор Полиномиального Искусства")
        self.root.geometry("1400x900")
        self.root.configure(bg="#1a1a1a")

        self.data = default_data()
        self.filepath = None
        self.changed = False
        self.undo_stack = []
        self.redo_stack = []
        self.current_layer_idx = 0
        self.current_obj_idx = -1
        self._cooldown = False

        self._build_ui()
        self._bind_keys()
        self.render()
        self._update_all()

    # ================================================================
    # UI CONSTRUCTION
    # ================================================================
    def _build_ui(self):
        s = ttk.Style()
        s.theme_use("clam")
        s.configure("D.TFrame", background="#1a1a1a")
        s.configure("D.TLabel", background="#1a1a1a", foreground="#d0c8b8",
                     font=("Consolas", 9))
        s.configure("H.TLabel", background="#1a1a1a", foreground="#c8a040",
                     font=("Consolas", 11, "bold"))
        s.configure("D.TButton", background="#2a2a2a", foreground="#d0c8b8",
                     font=("Consolas", 9))
        s.configure("Accent.TButton", background="#4a3a20", foreground="#c8a040",
                     font=("Consolas", 9, "bold"))
        s.configure("D.TEntry", fieldbackground="#2a2a2a", foreground="#d0c8b8",
                     insertcolor="#c8a040")
        s.configure("D.TSpinbox", fieldbackground="#2a2a2a", foreground="#d0c8b8")
        s.configure("TNotebook", background="#1a1a1a")
        s.configure("TNotebook.Tab", background="#2a2a2a", foreground="#d0c8b8",
                     font=("Consolas", 9), padding=[10, 4])
        s.map("TNotebook.Tab",
               background=[("selected", "#3a3a2a")],
               foreground=[("selected", "#c8a040")])
        s.configure("D.TCheckbutton", background="#1a1a1a", foreground="#d0c8b8",
                     font=("Consolas", 9))
        s.configure("D.TScale", background="#1a1a1a", troughcolor="#2a2a2a")
        s.configure("Treeview", background="#1a1a1a", foreground="#d0c8b8",
                     fieldbackground="#1a1a1a", font=("Consolas", 9))
        s.configure("Treeview.Heading", background="#2a2a2a", foreground="#c8a040")

        main = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main.pack(fill=tk.BOTH, expand=True)

        # === LEFT: инструменты + слои ===
        left = ttk.Frame(main, style="D.TFrame")
        main.add(left, weight=1)

        ttk.Label(left, text="◆ POLYART EDITOR", style="H.TLabel").pack(
            anchor="w", padx=8, pady=(8, 4))

        # Меню кнопки
        mf = ttk.Frame(left, style="D.TFrame")
        mf.pack(fill=tk.X, padx=8, pady=2)
        for txt, cmd in [("Новый", self.new_file), ("📂", self.open_file),
                          ("💾", self.save_file), ("📥", self.save_as),
                          ("↩", self.undo), ("↪", self.redo)]:
            ttk.Button(mf, text=txt, style="D.TButton", command=cmd,
                       width=6).pack(side=tk.LEFT, padx=1)

        nb = ttk.Notebook(left)
        nb.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)

        # --- TAB: Слои ---
        tab_layers = ttk.Frame(nb, style="D.TFrame")
        nb.add(tab_layers, text="Слои")

        lf_btn = ttk.Frame(tab_layers, style="D.TFrame")
        lf_btn.pack(fill=tk.X, pady=2)
        ttk.Button(lf_btn, text="+ Слой", style="D.TButton",
                   command=self.add_layer).pack(side=tk.LEFT, padx=2)
        ttk.Button(lf_btn, text="− Слой", style="D.TButton",
                   command=self.del_layer).pack(side=tk.LEFT, padx=2)

        self.layer_list = tk.Listbox(tab_layers, bg="#1a1a1a", fg="#d0c8b8",
                                      selectbackground="#3a3a2a",
                                      selectforeground="#c8a040",
                                      font=("Consolas", 9), relief=tk.FLAT,
                                      activestyle='none', height=4)
        self.layer_list.pack(fill=tk.X, pady=2)
        self.layer_list.bind("<<ListboxSelect>>", self._on_layer_select)

        # Объекты в слое
        ttk.Label(tab_layers, text="Объекты слоя:", style="D.TLabel").pack(
            anchor="w", pady=(6, 2))

        obj_btn = ttk.Frame(tab_layers, style="D.TFrame")
        obj_btn.pack(fill=tk.X, pady=2)
        for txt, cmd in [("＋ Объект", self.add_object), ("− Удалить", self.del_object),
                          ("▲ Вверх", self.obj_up), ("▼ Вниз", self.obj_down),
                          ("📋 Копия", self.dup_object)]:
            ttk.Button(obj_btn, text=txt, style="D.TButton", command=cmd,
                       width=8).pack(side=tk.LEFT, padx=1)

        self.obj_list = tk.Listbox(tab_layers, bg="#1a1a1a", fg="#d0c8b8",
                                    selectbackground="#3a3a2a",
                                    selectforeground="#c8a040",
                                    font=("Consolas", 9), relief=tk.FLAT,
                                    activestyle='none', height=8)
        self.obj_list.pack(fill=tk.BOTH, expand=True, pady=2)
        self.obj_list.bind("<<ListboxSelect>>", self._on_obj_select)

        # --- TAB: Свойства ---
        tab_props = ttk.Frame(nb, style="D.TFrame")
        nb.add(tab_props, text="Свойства")

        self.props_canvas = tk.Canvas(tab_props, bg="#1a1a1a",
                                       highlightthickness=0)
        props_scroll = ttk.Scrollbar(tab_props, orient=tk.VERTICAL,
                                      command=self.props_canvas.yview)
        self.props_inner = ttk.Frame(self.props_canvas, style="D.TFrame")
        self.props_inner.bind("<Configure>",
                               lambda e: self.props_canvas.configure(
                                   scrollregion=self.props_canvas.bbox("all")))
        self.props_canvas.create_window((0, 0), window=self.props_inner,
                                         anchor="nw")
        self.props_canvas.configure(yscrollcommand=props_scroll.set)
        self.props_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        props_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.prop_widgets = {}
        self._build_props_panel()

        # --- TAB: Пресеты ---
        tab_presets = ttk.Frame(nb, style="D.TFrame")
        nb.add(tab_presets, text="Пресеты")

        ttk.Label(tab_presets, text="Полиномиальные фигуры:",
                  style="D.TLabel").pack(anchor="w", padx=4, pady=4)
        for name, preset in PRESETS.items():
            row = ttk.Frame(tab_presets, style="D.TFrame")
            row.pack(fill=tk.X, padx=4, pady=1)
            ttk.Label(row, text=name, style="D.TLabel", width=12).pack(side=tk.LEFT)
            ttk.Button(row, text="＋", style="D.TButton", width=3,
                       command=lambda p=preset: self.add_preset(p)).pack(side=tk.LEFT)

        # --- TAB: Мета ---
        tab_meta = ttk.Frame(nb, style="D.TFrame")
        nb.add(tab_meta, text="Мета")

        self.meta_entries = {}
        for key, label in [("name", "Название"), ("author", "Автор"),
                            ("description", "Описание")]:
            row = ttk.Frame(tab_meta, style="D.TFrame")
            row.pack(fill=tk.X, padx=8, pady=3)
            ttk.Label(row, text=f"{label}:", style="D.TLabel", width=12).pack(side=tk.LEFT)
            e = ttk.Entry(row, style="D.TEntry", width=30)
            e.pack(side=tk.LEFT, fill=tk.X, expand=True)
            self.meta_entries[key] = e

        for key, label in [("width", "Ширина"), ("height", "Высота"),
                            ("background", "Фон")]:
            row = ttk.Frame(tab_meta, style="D.TFrame")
            row.pack(fill=tk.X, padx=8, pady=3)
            ttk.Label(row, text=f"{label}:", style="D.TLabel", width=12).pack(side=tk.LEFT)
            e = ttk.Entry(row, style="D.TEntry", width=20)
            e.pack(side=tk.LEFT)
            self.meta_entries[key] = e

        ttk.Button(tab_meta, text="Применить мета", style="Accent.TButton",
                   command=self._apply_meta).pack(pady=8)

        # === RIGHT: холст ===
        right = ttk.Frame(main, style="D.TFrame")
        main.add(right, weight=4)

        self.fig = Figure(figsize=(9, 9), facecolor="#f5efe0", dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor("#f5efe0")
        self.ax.set_aspect('equal')
        self.ax.axis('off')

        self.canvas_widget = FigureCanvasTkAgg(self.fig, master=right)
        self.canvas_widget.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        tb_frame = ttk.Frame(right, style="D.TFrame")
        tb_frame.pack(fill=tk.X)
        self.toolbar = NavigationToolbar2Tk(self.canvas_widget, tb_frame)

        # Статус
        self.status = ttk.Label(right, text="Готов", style="D.TLabel")
        self.status.pack(side=tk.BOTTOM, fill=tk.X, padx=8, pady=2)

    # ================================================================
    # PROPERTIES PANEL
    # ================================================================
    def _build_props_panel(self):
        p = self.props_inner
        self.prop_widgets = {}

        # Тип объекта
        row = ttk.Frame(p, style="D.TFrame")
        row.pack(fill=tk.X, padx=8, pady=2)
        ttk.Label(row, text="Тип:", style="D.TLabel", width=10).pack(side=tk.LEFT)
        self.prop_type_var = tk.StringVar(value="parametric")
        cb = ttk.Combobox(row, textvariable=self.prop_type_var,
                           values=["parametric", "parametric_fill", "superformula"],
                           state="readonly", width=18)
        cb.pack(side=tk.LEFT)
        cb.bind("<<ComboboxSelected>>", lambda e: self._apply_prop())

        # Цвет линии
        row = ttk.Frame(p, style="D.TFrame")
        row.pack(fill=tk.X, padx=8, pady=2)
        ttk.Label(row, text="Цвет:", style="D.TLabel", width=10).pack(side=tk.LEFT)
        self.color_var = tk.StringVar(value="#1a1008")
        self.color_entry = ttk.Entry(row, textvariable=self.color_var,
                                      style="D.TEntry", width=12)
        self.color_entry.pack(side=tk.LEFT)
        self.color_preview = tk.Canvas(row, width=20, height=20, bg="#1a1008",
                                        highlightthickness=1, highlightbackground="#555")
        self.color_preview.pack(side=tk.LEFT, padx=4)
        ttk.Button(row, text="🎨", style="D.TButton", width=3,
                   command=self._pick_color).pack(side=tk.LEFT)

        # Заливка
        row = ttk.Frame(p, style="D.TFrame")
        row.pack(fill=tk.X, padx=8, pady=2)
        self.fill_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(row, text="Заливка", variable=self.fill_var,
                         style="D.TCheckbutton",
                         command=self._apply_prop).pack(side=tk.LEFT)
        ttk.Label(row, text="Цвет зал.:", style="D.TLabel").pack(side=tk.LEFT, padx=(10, 0))
        self.fill_color_var = tk.StringVar(value="#c8a888")
        ttk.Entry(row, textvariable=self.fill_color_var,
                  style="D.TEntry", width=10).pack(side=tk.LEFT)
        self.fill_color_preview = tk.Canvas(row, width=18, height=18, bg="#c8a888",
                                             highlightthickness=1, highlightbackground="#555")
        self.fill_color_preview.pack(side=tk.LEFT, padx=2)
        ttk.Button(row, text="🎨", style="D.TButton", width=3,
                   command=self._pick_fill_color).pack(side=tk.LEFT)

        # Alpha, linewidth
        for name, label, var_default, vfrom, vto in [
            ("alpha", "Прозрач.", 1.0, 0.0, 1.0),
            ("fill_alpha", "Зал. альфа", 0.5, 0.0, 1.0),
            ("linewidth", "Толщина", 1.5, 0.1, 8.0),
        ]:
            row = ttk.Frame(p, style="D.TFrame")
            row.pack(fill=tk.X, padx=8, pady=2)
            ttk.Label(row, text=f"{label}:", style="D.TLabel", width=10).pack(side=tk.LEFT)
            var = tk.DoubleVar(value=var_default)
            setattr(self, f"prop_{name}_var", var)
            scale = ttk.Scale(row, from_=vfrom, to=vto, variable=var,
                               orient=tk.HORIZONTAL, length=150,
                               command=lambda v, n=name: self._apply_prop())
            scale.pack(side=tk.LEFT)
            lbl = ttk.Label(row, text=f"{var_default:.2f}", style="D.TLabel", width=5)
            lbl.pack(side=tk.LEFT)
            setattr(self, f"prop_{name}_lbl", lbl)

        # t_range
        for name, label, default in [("t_min", "t min", 0.0), ("t_max", "t max", 1.0)]:
            row = ttk.Frame(p, style="D.TFrame")
            row.pack(fill=tk.X, padx=8, pady=2)
            ttk.Label(row, text=f"{label}:", style="D.TLabel", width=10).pack(side=tk.LEFT)
            var = tk.DoubleVar(value=default)
            setattr(self, f"prop_{name}_var", var)
            ttk.Entry(row, textvariable=var, style="D.TEntry", width=10).pack(side=tk.LEFT)

        # Style
        row = ttk.Frame(p, style="D.TFrame")
        row.pack(fill=tk.X, padx=8, pady=2)
        ttk.Label(row, text="Стиль:", style="D.TLabel", width=10).pack(side=tk.LEFT)
        self.prop_style_var = tk.StringVar(value="solid")
        ttk.Combobox(row, textvariable=self.prop_style_var,
                      values=["solid", "dashed", "dotted"],
                      state="readonly", width=12).pack(side=tk.LEFT)

        ttk.Separator(p, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=8, pady=6)

        # Коэффициенты полиномов
        ttk.Label(p, text="Коэффициенты x(t) =", style="D.TLabel").pack(
            anchor="w", padx=8, pady=(4, 1))
        self.poly_x_text = tk.Text(p, height=4, bg="#2a2a2a", fg="#d0c8b8",
                                    insertbackground="#c8a040", font=("Consolas", 9),
                                    relief=tk.FLAT, padx=6, pady=4)
        self.poly_x_text.pack(fill=tk.X, padx=8, pady=1)
        self.poly_x_text.bind("<FocusOut>", lambda e: self._apply_prop())
        self.poly_x_text.bind("<Return>", lambda e: self._apply_prop())

        ttk.Label(p, text="Коэффициенты y(t) =", style="D.TLabel").pack(
            anchor="w", padx=8, pady=(4, 1))
        self.poly_y_text = tk.Text(p, height=4, bg="#2a2a2a", fg="#d0c8b8",
                                    insertbackground="#c8a040", font=("Consolas", 9),
                                    relief=tk.FLAT, padx=6, pady=4)
        self.poly_y_text.pack(fill=tk.X, padx=8, pady=1)
        self.poly_y_text.bind("<FocusOut>", lambda e: self._apply_prop())
        self.poly_y_text.bind("<Return>", lambda e: self._apply_prop())

        # n_points
        row = ttk.Frame(p, style="D.TFrame")
        row.pack(fill=tk.X, padx=8, pady=2)
        ttk.Label(row, text="Точек:", style="D.TLabel", width=10).pack(side=tk.LEFT)
        self.prop_npts_var = tk.IntVar(value=300)
        ttk.Entry(row, textvariable=self.prop_npts_var, style="D.TEntry", width=8).pack(side=tk.LEFT)

        ttk.Separator(p, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=8, pady=6)

        # Superformula params
        ttk.Label(p, text="Суперформула: m, n1, n2, n3, a, b", style="D.TLabel").pack(
            anchor="w", padx=8)
        sf_row = ttk.Frame(p, style="D.TFrame")
        sf_row.pack(fill=tk.X, padx=8, pady=2)
        self.sf_vars = []
        for val in [6, 1, 1, 1, 1, 1]:
            v = tk.DoubleVar(value=val)
            self.sf_vars.append(v)
            ttk.Entry(sf_row, textvariable=v, style="D.TEntry", width=5).pack(side=tk.LEFT, padx=1)

        ttk.Label(p, text="Центр x,y и масштаб:", style="D.TLabel").pack(
            anchor="w", padx=8)
        sf_row2 = ttk.Frame(p, style="D.TFrame")
        sf_row2.pack(fill=tk.X, padx=8, pady=2)
        self.sf_cx = tk.DoubleVar(value=0)
        self.sf_cy = tk.DoubleVar(value=0)
        self.sf_scale = tk.DoubleVar(value=1.0)
        ttk.Entry(sf_row2, textvariable=self.sf_cx, style="D.TEntry", width=6).pack(side=tk.LEFT, padx=1)
        ttk.Entry(sf_row2, textvariable=self.sf_cy, style="D.TEntry", width=6).pack(side=tk.LEFT, padx=1)
        ttk.Entry(sf_row2, textvariable=self.sf_scale, style="D.TEntry", width=6).pack(side=tk.LEFT, padx=1)

        ttk.Button(p, text="▶ Применить свойства", style="Accent.TButton",
                   command=self._apply_prop).pack(pady=8, padx=8, fill=tk.X)

    # ================================================================
    # FILE OPERATIONS
    # ================================================================
    def _push_undo(self):
        self.undo_stack.append(copy.deepcopy(self.data))
        if len(self.undo_stack) > 50:
            self.undo_stack.pop(0)
        self.redo_stack.clear()
        self.changed = True

    def new_file(self):
        if self.changed:
            if not messagebox.askyesno("Новый файл", "Сохранить текущий?"):
                return
            self.save_file()
        self.data = default_data()
        self.filepath = None
        self.current_layer_idx = 0
        self.current_obj_idx = -1
        self.undo_stack.clear()
        self.redo_stack.clear()
        self.changed = False
        self._update_all()
        self.render()
        self.status.config(text="Новый файл")

    def open_file(self):
        path = filedialog.askopenfilename(
            title="Открыть .polyart",
            filetypes=[("PolyArt", "*.polyart"), ("JSON", "*.json"), ("All", "*.*")])
        if not path:
            return
        with open(path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        self.filepath = path
        self.current_layer_idx = 0
        self.current_obj_idx = -1 if not self.data["layers"] else (
            -1 if not self.data["layers"][0]["objects"] else 0)
        self.undo_stack.clear()
        self.redo_stack.clear()
        self.changed = False
        self._update_all()
        self.render()
        self.status.config(text=f"Открыт: {os.path.basename(path)}")

    def save_file(self):
        if not self.filepath:
            return self.save_as()
        self._apply_meta()
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
        self.changed = False
        self.status.config(text=f"Сохранён: {os.path.basename(self.filepath)}")

    def save_as(self):
        path = filedialog.asksaveasfilename(
            title="Сохранить .polyart",
            defaultextension=".polyart",
            filetypes=[("PolyArt", "*.polyart"), ("JSON", "*.json")],
            initialfile="art.polyart")
        if not path:
            return
        self.filepath = path
        self.save_file()

    def undo(self):
        if not self.undo_stack:
            return
        self.redo_stack.append(copy.deepcopy(self.data))
        self.data = self.undo_stack.pop()
        self._update_all()
        self.render()

    def redo(self):
        if not self.redo_stack:
            return
        self.undo_stack.append(copy.deepcopy(self.data))
        self.data = self.redo_stack.pop()
        self._update_all()
        self.render()

    # ================================================================
    # LAYER / OBJECT MANAGEMENT
    # ================================================================
    def add_layer(self):
        self._push_undo()
        n = len(self.data["layers"]) + 1
        self.data["layers"].append(default_layer(f"Слой {n}"))
        self.current_layer_idx = len(self.data["layers"]) - 1
        self._update_all()

    def del_layer(self):
        if len(self.data["layers"]) <= 1:
            return
        self._push_undo()
        self.data["layers"].pop(self.current_layer_idx)
        self.current_layer_idx = min(self.current_layer_idx,
                                      len(self.data["layers"]) - 1)
        self.current_obj_idx = -1
        self._update_all()
        self.render()

    def add_object(self):
        self._push_undo()
        obj = default_obj()
        self.data["layers"][self.current_layer_idx]["objects"].append(obj)
        self.current_obj_idx = len(
            self.data["layers"][self.current_layer_idx]["objects"]) - 1
        self._update_all()
        self.render()

    def del_object(self):
        layer = self.data["layers"][self.current_layer_idx]
        if not layer["objects"]:
            return
        self._push_undo()
        layer["objects"].pop(self.current_obj_idx)
        self.current_obj_idx = min(self.current_obj_idx,
                                    len(layer["objects"]) - 1)
        self._update_all()
        self.render()

    def dup_object(self):
        layer = self.data["layers"][self.current_layer_idx]
        if not layer["objects"] or self.current_obj_idx < 0:
            return
        self._push_undo()
        obj = copy.deepcopy(layer["objects"][self.current_obj_idx])
        layer["objects"].insert(self.current_obj_idx + 1, obj)
        self.current_obj_idx += 1
        self._update_all()
        self.render()

    def obj_up(self):
        layer = self.data["layers"][self.current_layer_idx]
        i = self.current_obj_idx
        if i <= 0:
            return
        self._push_undo()
        layer["objects"][i], layer["objects"][i - 1] = (
            layer["objects"][i - 1], layer["objects"][i])
        self.current_obj_idx -= 1
        self._update_all()
        self.render()

    def obj_down(self):
        layer = self.data["layers"][self.current_layer_idx]
        i = self.current_obj_idx
        if i < 0 or i >= len(layer["objects"]) - 1:
            return
        self._push_undo()
        layer["objects"][i], layer["objects"][i + 1] = (
            layer["objects"][i + 1], layer["objects"][i])
        self.current_obj_idx += 1
        self._update_all()
        self.render()

    def add_preset(self, preset):
        self._push_undo()
        obj = default_obj()
        obj.update(copy.deepcopy(preset))
        self.data["layers"][self.current_layer_idx]["objects"].append(obj)
        self.current_obj_idx = len(
            self.data["layers"][self.current_layer_idx]["objects"]) - 1
        self._update_all()
        self.render()

    # ================================================================
    # PROPERTY APPLICATION
    # ================================================================
    def _apply_prop(self):
        if self._cooldown:
            return
        obj = self._current_obj()
        if not obj:
            return

        self._push_undo()

        obj["type"] = self.prop_type_var.get()
        obj["color"] = self.color_var.get()
        self.color_preview.configure(bg=obj["color"])
        obj["fill"] = self.fill_var.get()
        obj["fill_color"] = self.fill_color_var.get()
        self.fill_color_preview.configure(bg=obj["fill_color"])
        obj["alpha"] = self.prop_alpha_var.get()
        self.prop_alpha_lbl.config(text=f"{obj['alpha']:.2f}")
        obj["fill_alpha"] = self.prop_fill_alpha_var.get()
        self.prop_fill_alpha_lbl.config(text=f"{obj['fill_alpha']:.2f}")
        obj["linewidth"] = self.prop_linewidth_var.get()
        self.prop_linewidth_lbl.config(text=f"{obj['linewidth']:.2f}")
        obj["t_range"] = [self.prop_t_min_var.get(), self.prop_t_max_var.get()]
        obj["style"] = self.prop_style_var.get()
        obj["n_points"] = self.prop_npts_var.get()

        # Парсим полиномы
        try:
            x_text = self.poly_x_text.get("1.0", tk.END).strip()
            y_text = self.poly_y_text.get("1.0", tk.END).strip()
            if x_text:
                obj["poly_x"] = [float(v) for v in x_text.split(",")]
            if y_text:
                obj["poly_y"] = [float(v) for v in y_text.split(",")]
        except ValueError:
            pass

        # Superformula
        if obj["type"] == "superformula":
            obj["sf_params"] = [v.get() for v in self.sf_vars]
            obj["center"] = [self.sf_cx.get(), self.sf_cy.get()]
            obj["scale"] = self.sf_scale.get()

        self.render()
        self._update_obj_list()

    def _current_obj(self):
        try:
            layer = self.data["layers"][self.current_layer_idx]
            return layer["objects"][self.current_obj_idx]
        except (IndexError, KeyError):
            return None

    def _load_obj_to_props(self, obj):
        self._cooldown = True
        self.prop_type_var.set(obj.get("type", "parametric"))
        self.color_var.set(obj.get("color", "#1a1008"))
        self.color_preview.configure(bg=obj.get("color", "#1a1008"))
        self.fill_var.set(obj.get("fill", False))
        self.fill_color_var.set(obj.get("fill_color", "#c8a888"))
        self.fill_color_preview.configure(bg=obj.get("fill_color", "#c8a888"))
        self.prop_alpha_var.set(obj.get("alpha", 1.0))
        self.prop_alpha_lbl.config(text=f"{obj.get('alpha', 1.0):.2f}")
        self.prop_fill_alpha_var.set(obj.get("fill_alpha", 0.5))
        self.prop_fill_alpha_lbl.config(text=f"{obj.get('fill_alpha', 0.5):.2f}")
        self.prop_linewidth_var.set(obj.get("linewidth", 1.5))
        self.prop_linewidth_lbl.config(text=f"{obj.get('linewidth', 1.5):.2f}")
        t_range = obj.get("t_range", [0, 1])
        self.prop_t_min_var.set(t_range[0])
        self.prop_t_max_var.set(t_range[1])
        self.prop_style_var.set(obj.get("style", "solid"))
        self.prop_npts_var.set(obj.get("n_points", 300))

        self.poly_x_text.delete("1.0", tk.END)
        self.poly_x_text.insert("1.0", ", ".join(
            f"{c:.6g}" for c in obj.get("poly_x", [0])))
        self.poly_y_text.delete("1.0", tk.END)
        self.poly_y_text.insert("1.0", ", ".join(
            f"{c:.6g}" for c in obj.get("poly_y", [0])))

        sf = obj.get("sf_params", [6, 1, 1, 1, 1, 1])
        for i, v in enumerate(sf[:6]):
            self.sf_vars[i].set(v)
        center = obj.get("center", [0, 0])
        self.sf_cx.set(center[0])
        self.sf_cy.set(center[1])
        self.sf_scale.set(obj.get("scale", 1.0))

        self._cooldown = False

    # ================================================================
    # UI UPDATES
    # ================================================================
    def _update_all(self):
        self._update_layer_list()
        self._update_obj_list()
        self._update_meta_fields()

    def _update_layer_list(self):
        self.layer_list.delete(0, tk.END)
        for i, layer in enumerate(self.data["layers"]):
            n = len(layer.get("objects", []))
            prefix = "► " if i == self.current_layer_idx else "  "
            self.layer_list.insert(tk.END, f"{prefix}{layer['name']} ({n})")
        if 0 <= self.current_layer_idx < self.layer_list.size():
            self.layer_list.selection_set(self.current_layer_idx)

    def _update_obj_list(self):
        self.obj_list.delete(0, tk.END)
        try:
            layer = self.data["layers"][self.current_layer_idx]
        except IndexError:
            return
        for i, obj in enumerate(layer.get("objects", [])):
            otype = obj.get("type", "?")
            fill = "■" if obj.get("fill") else "□"
            deg = len(obj.get("poly_x", [])) - 1
            color = obj.get("color", "?")
            prefix = "► " if i == self.current_obj_idx else "  "
            label = f"{prefix}{fill} [{otype}] deg={deg} {color}"
            self.obj_list.insert(tk.END, label)
        if 0 <= self.current_obj_idx < self.obj_list.size():
            self.obj_list.selection_set(self.current_obj_idx)

    def _update_meta_fields(self):
        meta = self.data.get("meta", {})
        canvas = self.data.get("canvas", {})
        for key in ["name", "author", "description"]:
            if key in self.meta_entries:
                self.meta_entries[key].delete(0, tk.END)
                self.meta_entries[key].insert(0, meta.get(key, ""))
        for key in ["width", "height", "background"]:
            if key in self.meta_entries:
                self.meta_entries[key].delete(0, tk.END)
                self.meta_entries[key].insert(0, str(canvas.get(key, "")))

    def _apply_meta(self):
        meta = self.data.get("meta", {})
        canvas = self.data.get("canvas", {})
        for key in ["name", "author", "description"]:
            if key in self.meta_entries:
                meta[key] = self.meta_entries[key].get()
        for key in ["width", "height"]:
            if key in self.meta_entries:
                try:
                    canvas[key] = float(self.meta_entries[key].get())
                except ValueError:
                    pass
        if "background" in self.meta_entries:
            canvas["background"] = self.meta_entries["background"].get()

    # ================================================================
    # EVENT HANDLERS
    # ================================================================
    def _on_layer_select(self, event):
        sel = self.layer_list.curselection()
        if sel:
            self.current_layer_idx = sel[0]
            self.current_obj_idx = -1
            self._update_obj_list()

    def _on_obj_select(self, event):
        sel = self.obj_list.curselection()
        if sel:
            self.current_obj_idx = sel[0]
            obj = self._current_obj()
            if obj:
                self._load_obj_to_props(obj)
            self.render()

    def _pick_color(self):
        c = colorchooser.askcolor(initialcolor=self.color_var.get())
        if c[1]:
            self.color_var.set(c[1])
            self.color_preview.configure(bg=c[1])
            self._apply_prop()

    def _pick_fill_color(self):
        c = colorchooser.askcolor(initialcolor=self.fill_color_var.get())
        if c[1]:
            self.fill_color_var.set(c[1])
            self.fill_color_preview.configure(bg=c[1])
            self._apply_prop()

    def _bind_keys(self):
        self.root.bind("<Control-z>", lambda e: self.undo())
        self.root.bind("<Control-y>", lambda e: self.redo())
        self.root.bind("<Control-n>", lambda e: self.new_file())
        self.root.bind("<Control-o>", lambda e: self.open_file())
        self.root.bind("<Control-s>", lambda e: self.save_file())
        self.root.bind("<Control-Shift-S>", lambda e: self.save_as())
        self.root.bind("<Delete>", lambda e: self.del_object())
        self.root.bind("<F5>", lambda e: self.render())

    # ================================================================
    # RENDER
    # ================================================================
    def render(self):
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

        for f in self.data.get("formulas", []):
            self.ax.text(f["x"], f["y"], f["expr"],
                         fontsize=f.get("fontsize", 8),
                         fontfamily='serif',
                         color=f.get("color", "#8a6a4a"),
                         fontstyle='italic')

        self.canvas_widget.draw()

    def _draw_object(self, obj):
        otype = obj.get("type", "parametric")
        color = obj.get("color", "#1a1008")
        alpha = obj.get("alpha", 1.0)
        lw = obj.get("linewidth", 1.5)
        ls = {"solid": "-", "dashed": "--", "dotted": ":"}.get(
            obj.get("style", "solid"), "-")
        n = obj.get("n_points", 300)

        if otype in ("parametric", "parametric_fill"):
            tr = obj.get("t_range", [0, 1])
            t = np.linspace(tr[0], tr[1], n)
            x = eval_poly(obj.get("poly_x", [0]), t)
            y = eval_poly(obj.get("poly_y", [0]), t)

            if obj.get("fill"):
                fc = obj.get("fill_color", color)
                self.ax.fill(x, y, color=fc, alpha=obj.get("fill_alpha", 0.5))
            self.ax.plot(x, y, color=color, alpha=alpha, linewidth=lw,
                         linestyle=ls)

        elif otype == "superformula":
            sp = obj.get("sf_params", [6, 1, 1, 1, 1, 1])
            center = obj.get("center", [0, 0])
            scale = obj.get("scale", 1.0)
            theta = np.linspace(0, 2 * np.pi, n)
            r = eval_superformula(sp, theta)
            x = center[0] + scale * r * np.cos(theta)
            y = center[1] + scale * r * np.sin(theta)
            if obj.get("fill"):
                fc = obj.get("fill_color", color)
                self.ax.fill(x, y, color=fc, alpha=obj.get("fill_alpha", 0.5))
            self.ax.plot(x, y, color=color, alpha=alpha, linewidth=lw,
                         linestyle=ls)


def main():
    root = tk.Tk()
    app = PolyartEditor(root)

    if len(sys.argv) > 1 and os.path.isfile(sys.argv[1]):
        try:
            with open(sys.argv[1], 'r', encoding='utf-8') as f:
                app.data = json.load(f)
            app.filepath = sys.argv[1]
            app.current_layer_idx = 0
            app.current_obj_idx = (0 if app.data["layers"] and
                                    app.data["layers"][0]["objects"] else -1)
            app._update_all()
            app.render()
        except Exception:
            pass

    root.mainloop()


if __name__ == "__main__":
    main()
