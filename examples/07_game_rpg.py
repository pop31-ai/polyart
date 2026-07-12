import sys, io, os
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, r"C:\Users\e\Desktop\6756756756756756")

import numpy as np

PI = np.pi

from polyart_api import Canvas, PolyObj, PolyCoeffs, TWO_PI
from polyart_sculpture import GameAssets

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "07_game_rpg.png")
c = Canvas(name="GameRPG", width=14, height=10,
           xlim=(-7, 7), ylim=(-5, 5), background="#1a1a2e")

c.layer("tilemap")
GameAssets.render_game_assets(c, GameAssets.tilemap(
    rows=10, cols=12, tile_size=1.0, cx=0, cy=-1,
    ground_color="#3a6a2a", wall_color="#6a5a4a",
    water_color="#2a4a7a", seed=42))

c.layer("characters")
chars = [
    ("warrior", -4.5, 2.5, 1.0),
    ("mage", -2.0, 2.5, 1.0),
    ("archer", 0.5, 2.5, 1.0),
    ("healer", 3.0, 2.5, 1.0),
]
for char_class, cx_p, cy_p, scale in chars:
    GameAssets.render_game_assets(c, GameAssets.character_sprite(
        char_class, cx_p, cy_p, scale))

c.layer("hp_mp_bars")
bar_data = [
    (-4.5, 3.8, 0.8, "#cc3333", "HP"),
    (-4.5, 3.5, 0.5, "#3333cc", "MP"),
    (-2.0, 3.8, 0.6, "#cc3333", "HP"),
    (-2.0, 3.5, 0.9, "#3333cc", "MP"),
    (0.5, 3.8, 0.9, "#cc3333", "HP"),
    (0.5, 3.5, 0.3, "#3333cc", "MP"),
    (3.0, 3.8, 0.7, "#cc3333", "HP"),
    (3.0, 3.5, 0.8, "#3333cc", "MP"),
]
for bx, by, val, col, label in bar_data:
    GameAssets.render_game_assets(c, GameAssets.health_bar(
        bx - 1, by, 2, 0.2, val, col))

c.layer("minimap")
GameAssets.render_game_assets(c, GameAssets.minimap(
    cx=5.5, cy=3.5, size=2.5, explored_pct=0.5, seed=42))

c.layer("compass")
GameAssets.render_game_assets(c, GameAssets.compass_rose(
    cx=5.5, cy=-3.5, size=1.2, color="#c8a040"))

c.layer("trees_deco")
for tx, ty, ts in [(-5.5, -3.5, 1.5), (4.5, -3, 1.8), (-6, 0, 1.2)]:
    GameAssets.render_game_assets(c, GameAssets.tree(tx, ty, ts, seed=abs(int(ty * 100)) + 1))

c.layer("ui_frame")
ui_x, ui_y = -6.5, 4.0
c.polygon([(ui_x, ui_y), (ui_x + 4.5, ui_y), (ui_x + 4.5, ui_y - 1.2),
           (ui_x, ui_y - 1.2)], fill=True, fill_color="#0a0a1e",
          fill_alpha=0.7, color="#c8a040", linewidth=1.0)
c.add_formula("Party Status", ui_x + 0.2, ui_y - 0.3, fontsize=8, color="#c8a040")
c.add_formula("Lv.12  Gold: 1250", ui_x + 0.2, ui_y - 0.8, fontsize=6, color="#aaa888")

c.add_formula("RPG World Map", -6.5, -4.5, fontsize=9, color="#c8a040")

print("[OK] Game RPG complete")
c.render(OUT, dpi=200)
c.info()
