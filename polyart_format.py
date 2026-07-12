import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPolygon
from matplotlib.collections import PatchCollection
import os

# ============================================================
# ФОРМАТ POLYART (.polyart)
# Полиномиальный художественный формат
# ============================================================
#
# Структура JSON:
# {
#   "meta": { "name", "author", "version", "phi" },
#   "canvas": { "width", "height", "background" },
#   "layers": [
#     {
#       "name": "str",
#       "objects": [
#         {
#           "type": "parametric" | "implicit" | "parametric_fill" | "superformula" | "polygon_poly",
#           "poly_x": [a0, a1, a2, ...],    # коэффициенты полинома x(t) = Σ ai*t^i
#           "poly_y": [b0, b1, b2, ...],    # коэффициенты полинома y(t) = Σ bi*t^i
#           "t_range": [t_min, t_max],
#           "color": "#rrggbb",
#           "alpha": 0.0-1.0,
#           "linewidth": float,
#           "fill": bool,
#           "fill_alpha": float,
#           "style": "solid" | "dashed" | "dotted",
#           # Для implicit: f(x,y) = 0
#           "poly_implicit": [[cx,cy], [ax,ay,bx,by,cxy], ...],
#           "center": [x, y],
#           "radius": float,
#           # Для superformula
#           "sf_params": [m, n1, n2, n3, a, b],
#         }
#       ]
#     }
#   ],
#   "formulas": [ { "expr": str, "x": float, "y": float } ]
# }
# ============================================================

VERSION = "1.0.0"
PHI = (1 + np.sqrt(5)) / 2


def make_object(poly_x, poly_y, t_range=(0, 1), **kwargs):
    """Создать полиномиальный объект"""
    obj = {
        "type": kwargs.get("type", "parametric"),
        "poly_x": list(poly_x),
        "poly_y": list(poly_y),
        "t_range": list(t_range),
        "color": kwargs.get("color", "#1a1008"),
        "alpha": kwargs.get("alpha", 1.0),
        "linewidth": kwargs.get("linewidth", 1.0),
        "fill": kwargs.get("fill", False),
        "fill_alpha": kwargs.get("fill_alpha", 0.5),
        "style": kwargs.get("style", "solid"),
    }
    if "n_points" in kwargs:
        obj["n_points"] = kwargs["n_points"]
    return obj


def make_fill_object(poly_x, poly_y, t_range=(0, 1), **kwargs):
    """Заливаемый полиномиальный контур"""
    obj = make_object(poly_x, poly_y, t_range, **kwargs)
    obj["type"] = "parametric_fill"
    obj["fill"] = True
    obj["fill_alpha"] = kwargs.get("fill_alpha", 0.7)
    return obj


def make_circle(cx, cy, r, **kwargs):
    """Окружность = полином x(t)=cx+r*cos(t), y(t)=cy+r*sin(t)"""
    # Коэффициенты для cos/sin аппроксимации
    # cos(t) ≈ 1 - t²/2 + t⁴/24 - t⁶/720
    # Для точности используем n_points
    obj = {
        "type": "parametric",
        "poly_x": [cx, 0, -r/2, 0, r/24, 0, -r/720],
        "poly_y": [cy, r, 0, -r/6, 0, r/120, 0],
        "t_range": [0, 6.283185307],
        "n_points": kwargs.get("n_points", 200),
        "color": kwargs.get("color", "#1a1008"),
        "alpha": kwargs.get("alpha", 1.0),
        "linewidth": kwargs.get("linewidth", 1.0),
        "fill": kwargs.get("fill", False),
        "fill_alpha": kwargs.get("fill_alpha", 0.5),
    }
    return obj


def make_ellipse(cx, cy, a, b, **kwargs):
    """Эллипс — полиномиальный"""
    obj = {
        "type": "parametric",
        "poly_x": [cx, 0, -a/2, 0, a/24, 0, -a/720],
        "poly_y": [cy, b, 0, -b/6, 0, b/120, 0],
        "t_range": [0, 6.283185307],
        "n_points": kwargs.get("n_points", 200),
        "color": kwargs.get("color", "#1a1008"),
        "alpha": kwargs.get("alpha", 1.0),
        "linewidth": kwargs.get("linewidth", 1.0),
        "fill": kwargs.get("fill", False),
        "fill_alpha": kwargs.get("fill_alpha", 0.5),
    }
    return obj


def make_spiral(cx, cy, a, b, turns=3, **kwargs):
    """Логарифмическая спираль r = a*e^(b*θ)"""
    theta_max = turns * 2 * np.pi
    # Аппроксимация: x(t) = cx + r(t)*cos(t), y(t) = cy + r(t)*sin(t)
    # r(t) = a*e^(b*t) — аппроксимируем полиномом Чебышёва
    t_pts = np.linspace(0, theta_max, 500)
    r_pts = a * np.exp(b * t_pts)
    x_pts = cx + r_pts * np.cos(t_pts)
    y_pts = cy + r_pts * np.sin(t_pts)
    
    # Аппроксимация полиномами (minimax)
    deg = kwargs.get("degree", 15)
    t_norm = t_pts / theta_max
    coeffs_x = np.polyfit(t_norm, x_pts, deg)
    coeffs_y = np.polyfit(t_norm, y_pts, deg)
    
    obj = {
        "type": "parametric",
        "poly_x": list(reversed(coeffs_x)),
        "poly_y": list(reversed(coeffs_y)),
        "t_range": [0, 1],
        "n_points": kwargs.get("n_points", 300),
        "color": kwargs.get("color", "#1a1008"),
        "alpha": kwargs.get("alpha", 1.0),
        "linewidth": kwargs.get("linewidth", 1.0),
    }
    return obj


def make_superformula(m, n1, n2, n3, a=1, b=1, **kwargs):
    """Суперформула Лилиanked/Гielis: r(θ) = (|cos(mθ/4)/a|^n2 + |sin(mθ/4)/b|^n3)^(-1/n1)"""
    obj = {
        "type": "superformula",
        "sf_params": [m, n1, n2, n3, a, b],
        "center": kwargs.get("center", [0, 0]),
        "scale": kwargs.get("scale", 1.0),
        "color": kwargs.get("color", "#1a1008"),
        "alpha": kwargs.get("alpha", 1.0),
        "linewidth": kwargs.get("linewidth", 1.0),
        "fill": kwargs.get("fill", False),
        "fill_alpha": kwargs.get("fill_alpha", 0.5),
    }
    return obj


def make_polygon_poly(vertices, **kwargs):
    """Полигон, аппроксимированный полиномами (сплайн через вершины)"""
    n = len(vertices)
    verts = np.array(vertices)
    
    # Параметрические полиномы через вершины
    t_pts = np.linspace(0, 1, n + 1)
    t_verts = np.linspace(0, 1, n)
    t_fine = np.linspace(0, 1, n * 30)
    
    # Добавляем первую точку в конец для замыкания
    verts_closed = np.vstack([verts, verts[0]])
    t_closed = np.append(t_verts, 1.0)
    
    deg = min(n - 1, 20)
    coeffs_x = np.polyfit(t_closed, verts_closed[:, 0], deg)
    coeffs_y = np.polyfit(t_closed, verts_closed[:, 1], deg)
    
    obj = {
        "type": "parametric",
        "poly_x": list(reversed(coeffs_x)),
        "poly_y": list(reversed(coeffs_y)),
        "t_range": [0, 1],
        "n_points": kwargs.get("n_points", n * 30),
        "color": kwargs.get("color", "#1a1008"),
        "alpha": kwargs.get("alpha", 1.0),
        "linewidth": kwargs.get("linewidth", 1.0),
        "fill": kwargs.get("fill", False),
        "fill_alpha": kwargs.get("fill_alpha", 0.5),
    }
    return obj


def save_polyart(filename, meta, canvas, layers, formulas=None):
    """Сохранить в формат .polyart"""
    data = {
        "format": "polyart",
        "version": VERSION,
        "meta": {
            "name": meta.get("name", "Untitled"),
            "author": meta.get("author", "Mathematicus"),
            "description": meta.get("description", ""),
            "phi": PHI,
        },
        "canvas": {
            "width": canvas.get("width", 10),
            "height": canvas.get("height", 10),
            "background": canvas.get("background", "#f5efe0"),
            "xlim": canvas.get("xlim", [-5, 5]),
            "ylim": canvas.get("ylim", [-5, 5]),
        },
        "layers": layers,
    }
    if formulas:
        data["formulas"] = formulas
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"Сохранено: {filename} ({os.path.getsize(filename)} bytes)")
    return filename


def load_polyart(filename):
    """Загрузить .polyart файл"""
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)


def _eval_poly(coeffs, t):
    """Вычислить полином Σ aᵢtⁱ"""
    result = np.zeros_like(t, dtype=float)
    for i, c in enumerate(coeffs):
        result += c * t**i
    return result


def _eval_superformula(sf_params, theta):
    """Вычислить суперформулу"""
    m, n1, n2, n3, a, b = sf_params
    t1 = np.abs(np.cos(m * theta / 4) / a)
    t2 = np.abs(np.sin(m * theta / 4) / b)
    r = (t1**n2 + t2**n3) ** (-1.0 / n1)
    return r


def render_polyart(data, ax=None, save_png=None, dpi=200):
    """Рендер .polyart данных"""
    canvas = data["canvas"]
    
    if ax is None:
        fig, ax = plt.subplots(1, 1,
                                figsize=(canvas.get("width", 10), canvas.get("height", 10)),
                                facecolor=canvas.get("background", "#f5efe0"))
        ax.set_facecolor(canvas.get("background", "#f5efe0"))
        ax.set_aspect('equal')
        ax.axis('off')
    else:
        fig = ax.get_figure()
    
    xlim = canvas.get("xlim", [-5, 5])
    ylim = canvas.get("ylim", [-5, 5])
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    
    for layer in data["layers"]:
        for obj in layer.get("objects", []):
            obj_type = obj.get("type", "parametric")
            color = obj.get("color", "#1a1008")
            alpha = obj.get("alpha", 1.0)
            lw = obj.get("linewidth", 1.0)
            style = obj.get("style", "solid")
            n_pts = obj.get("n_points", 300)
            
            linestyle = {"solid": "-", "dashed": "--", "dotted": ":"}.get(style, "-")
            
            if obj_type in ("parametric", "parametric_fill"):
                t_range = obj.get("t_range", [0, 1])
                t = np.linspace(t_range[0], t_range[1], n_pts)
                x = _eval_poly(obj["poly_x"], t)
                y = _eval_poly(obj["poly_y"], t)
                
                if obj.get("fill", False):
                    fill_alpha = obj.get("fill_alpha", 0.5)
                    ax.fill(x, y, color=color, alpha=fill_alpha)
                
                ax.plot(x, y, color=color, alpha=alpha, linewidth=lw, linestyle=linestyle)
            
            elif obj_type == "superformula":
                sf_params = obj["sf_params"]
                center = obj.get("center", [0, 0])
                scale = obj.get("scale", 1.0)
                
                theta = np.linspace(0, 2 * np.pi, n_pts)
                r = _eval_superformula(sf_params, theta)
                x = center[0] + scale * r * np.cos(theta)
                y = center[1] + scale * r * np.sin(theta)
                
                if obj.get("fill", False):
                    fill_alpha = obj.get("fill_alpha", 0.5)
                    ax.fill(x, y, color=color, alpha=fill_alpha)
                
                ax.plot(x, y, color=color, alpha=alpha, linewidth=lw, linestyle=linestyle)
    
    # Формулы
    if "formulas" in data:
        for f in data["formulas"]:
            ax.text(f["x"], f["y"], f["expr"],
                    fontsize=f.get("fontsize", 8),
                    fontfamily='serif', color=f.get("color", "#8a6a4a"),
                    fontstyle='italic',
                    ha=f.get("ha", "left"))
    
    if save_png:
        plt.savefig(save_png, dpi=dpi, bbox_inches='tight',
                    facecolor=canvas.get("background", "#f5efe0"))
        print(f"Рендер сохранён: {save_png}")
    
    return ax


# ============================================================
# ДЕМОНСТРАЦИЯ: сохранение и рендер
# ============================================================

def demo_create_polyart():
    """Создать демо-файл .polyart — портрет Аполлона"""
    
    # --- Слой 1: Фон и рамка ---
    frame = make_polygon_poly([
        [-4.5, -4.5], [4.5, -4.5], [4.5, 4.5], [-4.5, 4.5]
    ], color="#c0a880", linewidth=1.5, alpha=0.5)
    
    # --- Слой 2: Овал лица ---
    face = make_ellipse(0, 0, 1.3, 1.8, color="#c8a888", linewidth=1.5,
                         fill=True, fill_alpha=0.9, fill_color="#e0c8a8")
    face["fill_color"] = "#e0c8a8"
    
    # --- Слой 3: Глаза ---
    left_eye = make_ellipse(-0.5, 0.15, 0.22, 0.09, color="#3a2818", linewidth=1.5,
                             fill=True, fill_alpha=0.9, fill_color="white")
    left_eye["fill_color"] = "white"
    right_eye = make_ellipse(0.5, 0.15, 0.22, 0.09, color="#3a2818", linewidth=1.5,
                              fill=True, fill_alpha=0.9, fill_color="white")
    right_eye["fill_color"] = "white"
    
    # Зрачки
    left_pupil = make_ellipse(-0.5, 0.14, 0.06, 0.05, color="#1a1008",
                               fill=True, fill_alpha=0.95)
    left_pupil["fill_color"] = "#1a1008"
    right_pupil = make_ellipse(0.5, 0.14, 0.06, 0.05, color="#1a1008",
                                fill=True, fill_alpha=0.95)
    right_pupil["fill_color"] = "#1a1008"
    
    # --- Слой 4: Брови (параболы) ---
    left_brow_x = [-0.7, -0.48, -0.28]
    left_brow_y = [0.3, 0.38, 0.33]
    left_brow = make_object(left_brow_x, left_brow_y, t_range=[0, 1],
                             color="#3a2818", linewidth=2.5)
    
    right_brow_x = [0.28, 0.48, 0.7]
    right_brow_y = [0.33, 0.38, 0.3]
    right_brow = make_object(right_brow_x, right_brow_y, t_range=[0, 1],
                              color="#3a2818", linewidth=2.5)
    
    # --- Слой 5: Нос ---
    nose_x = [0, 0.02, 0.03, 0.04, 0.03]
    nose_y = [0.2, 0.05, -0.1, -0.2, -0.3]
    nose = make_object(nose_x, nose_y, t_range=[0, 1],
                        color="#c8a888", linewidth=1.2)
    
    # --- Слой 6: Рот (лук Купидона) ---
    mouth_upper_x = [-0.3, -0.15, 0, 0.15, 0.3]
    mouth_upper_y = [-0.55, -0.52, -0.53, -0.52, -0.55]
    mouth_upper = make_object(mouth_upper_x, mouth_upper_y, t_range=[0, 1],
                               color="#b86858", linewidth=1.5)
    
    mouth_lower_x = [-0.3, 0, 0.3]
    mouth_lower_y = [-0.56, -0.62, -0.56]
    mouth_lower = make_object(mouth_lower_x, mouth_lower_y, t_range=[0, 1],
                               color="#b86858", linewidth=1.5)
    
    # --- Слой 7: Волосы (спирали) ---
    hair_spirals = []
    for i in range(8):
        angle = i * np.pi / 4
        hx = [0]
        hy = [1.5]
        for j in range(1, 12):
            r = 0.1 * j * 0.15
            hx.append(r * np.cos(angle + j * 0.5))
            hy.append(1.5 + r * np.sin(angle + j * 0.5))
        hair_spirals.append(make_object(hx, hy, t_range=[0, 1],
                                          color="#4a3a1a", linewidth=1.2, alpha=0.6))
    
    # --- Слой 8: Лавровый венок ---
    wreath_leaves = []
    for i in range(20):
        angle = -np.pi + i * 2 * np.pi / 20
        cx_w = 1.35 * np.cos(angle)
        cy_w = 1.5 + 0.9 * 1.35 * np.sin(angle)
        leaf = make_ellipse(cx_w, cy_w, 0.12, 0.04, color="#5a8a3a",
                             linewidth=0.5, fill=True, fill_alpha=0.7)
        leaf["fill_color"] = "#5a8a3a"
        wreath_leaves.append(leaf)
    
    # --- Слой 9: Нимб ---
    nimbus = make_circle(0, 0.2, 2.0, color="#e8c860", linewidth=1.0, alpha=0.3)
    
    # Собираем слои
    layers = [
        {"name": "frame", "objects": [frame]},
        {"name": "face", "objects": [face]},
        {"name": "eyes", "objects": [left_eye, right_eye, left_pupil, right_pupil]},
        {"name": "brows", "objects": [left_brow, right_brow]},
        {"name": "nose", "objects": [nose]},
        {"name": "mouth", "objects": [mouth_upper, mouth_lower]},
        {"name": "hair", "objects": hair_spirals},
        {"name": "wreath", "objects": wreath_leaves},
        {"name": "nimbus", "objects": [nimbus]},
    ]
    
    formulas = [
        {"expr": "Лицо: x²/1.3² + y²/1.8² = 1 (эллипс)", "x": -4.3, "y": 3.5,
         "fontsize": 7, "color": "#8a6a4a"},
        {"expr": "Волосы: спираль r = a·e^(bθ)", "x": -4.3, "y": 3.2,
         "fontsize": 7, "color": "#8a6a4a"},
        {"expr": "Брови: y = ax² + bx + c (полином 2°)", "x": -4.3, "y": 2.9,
         "fontsize": 7, "color": "#8a6a4a"},
        {"expr": "Нимб: r = 2.0 + 0.02sin(12θ)", "x": -4.3, "y": 2.6,
         "fontsize": 7, "color": "#8a6a4a"},
        {"expr": "φ = 1.618...", "x": 3.0, "y": -4.3,
         "fontsize": 9, "color": "#6a4a2a"},
    ]
    
    save_polyart(
        "apollo.polyart",
        meta={
            "name": "Аполлон Олимпийский",
            "author": "Mathematicus",
            "description": "Портрет Аполлона в формате polyart — все элементы заданы полиномами"
        },
        canvas={
            "width": 10, "height": 10,
            "background": "#f5efe0",
            "xlim": [-4.5, 4.5], "ylim": [-4.5, 4.5]
        },
        layers=layers,
        formulas=formulas
    )
    
    # Рендерим
    data = load_polyart("apollo.polyart")
    render_polyart(data, save_png="apollo_polyart_render.png")
    print("Готово! Формат .polyart создан и отрендерен.")


if __name__ == "__main__":
    demo_create_polyart()
