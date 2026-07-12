"""
@file polyart_api.py
@brief Полиномиальное художественное API v2.0
@author PolyArt Project
@version 2.0.0
@date 2026

@par Описание
Библиотека для создания математических изображений на основе полиномов.
Поддерживает классические античные паттерны, золотое сечение,
суперформулы и произвольные параметрические кривые.

@par Быстрый старт
@code
from polyart_api import Canvas
c = Canvas(name="Art")
c.circle(0, 0, 1, fill=True, fill_color="#c8a040")
c.save("art.polyart")
c.render("art.png")
@endcode

@see polyart_format.py  Формат .polyart
@see polyart_editor.py  Визуальный редактор
@see polyart_viewer.py  Просмотрщик
"""

import numpy as np
import json
import os
from copy import deepcopy
from typing import List, Tuple, Optional, Union, Dict, Any

# ============================================================
# @defgroup constants Константы
# @{
# ============================================================

PHI = (1 + np.sqrt(5)) / 2
"""@brief Золотое сечение φ = 1.618033988749895"""

PHI_INV = 1.0 / PHI
"""@brief Обратное золотое сечение 1/φ = 0.618033988749895"""

PHI2_INV = 1.0 / (PHI * PHI)
"""@brief 1/φ² = 0.381966011250105"""

SQRT2 = np.sqrt(2)
"""@brief Корень из 2 = 1.414213562373095"""

SQRT3 = np.sqrt(3)
"""@brief Корень из 3 = 1.732050807568877"""

TWO_PI = 2 * np.pi
"""@brief 2π = 6.283185307179586"""

GOLDEN_ANGLE = np.pi * (3 - np.sqrt(5))
"""@brief Золотой угол = 2.399963229728653 рад (137.508°)"""


# @}
# ============================================================
# @defgroup greek_lines Греческие и римские линии
# @{
# ============================================================

class GreekLines:
    """
    @brief Коллекция классических линий греко-римского искусства.

    Все методы возвращают кортеж (poly_x, poly_y) — коэффициенты
    полиномов, пригодных для передачи в PolyObj или Canvas.

    @par Меандр (Greek Key)
    Прямоугольная спираль — основной орнамент греческой керамики.
    Задаётся как последовательность полиномиальных сегментов.

    @par Волюта (Ionic Scroll)
    Спираль, основанная на золотом сечении. Ионический ордер.

    @par Лотос (Lotus)
    Полумесяц с лепестками — египетско-греческий мотив.

    @par Пальметта (Palmette)
    Веер из лепестков — основной мотив декора колонн и ваз.
    """

    @staticmethod
    def meander_segment(x0, y0, step=0.3, height=0.15) -> List[Tuple[List[float], List[float]]]:
        """
        @brief Один сегмент меандра (греческого ключа).

        @param x0 Начальная X-координата
        @param y0 Начальная Y-координата
        @param step  Длина горизонтального сегмента
        @param height Высота вертикального сегмента

        @return Список из 5 полиномиальных сегментов (px, py)

        @code
        # Меандр из 10 сегментов
        segments = []
        for i in range(10):
            segs = GreekLines.meander_segment(i*0.3, 0)
            segments.extend(segs)
        @endcode
        """
        segs = [
            PolyCoeffs.line(x0, y0, x0 + step, y0),
            PolyCoeffs.line(x0 + step, y0, x0 + step, y0 + height),
            PolyCoeffs.line(x0 + step, y0 + height, x0, y0 + height),
            PolyCoeffs.line(x0, y0 + height, x0, y0 - height * 0.5),
            PolyCoeffs.line(x0, y0 - height * 0.5, x0 + step * 1.5, y0 - height * 0.5),
        ]
        return segs

    @staticmethod
    def meander(x0, y0, n_segments=8, step=0.3, height=0.15) -> List[Tuple[List[float], List[float]]]:
        """
        @brief Полный меандр — последовательность сегментов.

        @param x0 Начальная X-координата
        @param y0 Начальная Y-координата
        @param n_segments Количество сегментов
        @param step Длина одного сегмента
        @param height Высота меандра

        @return Список полиномиальных сегментов
        """
        all_segs = []
        for i in range(n_segments):
            all_segs.extend(
                GreekLines.meander_segment(x0 + i * step * 1.5, y0, step, height))
        return all_segs

    @staticmethod
    def meander_single_poly(x0, y0, n_segments=8, step=0.3, height=0.15) -> Tuple[List[float], List[float]]:
        """
        @brief Меандр как один полином (аппроксимация).

        @param x0 Начальная X
        @param y0 Начальная Y
        @param n_segments Количество сегментов
        @param step Длина сегмента
        @param height Высота

        @return (poly_x, poly_y) — один полином через все точки меандра

        Более компактный вариант — один полином большой степени
        вместо набора линейных сегментов.
        """
        points = []
        for i in range(n_segments):
            sx = x0 + i * step * 1.5
            points.extend([
                (sx, y0), (sx + step, y0),
                (sx + step, y0 + height), (sx, y0 + height),
                (sx, y0 - height * 0.5), (sx + step * 1.5, y0 - height * 0.5),
            ])
        return PolyCoeffs.from_points(points)

    @staticmethod
    def volute(cx, cy, a=0.5, b=0.1, turns=2.5, n_points=300) -> Tuple[List[float], List[float]]:
        """
        @brief Ионическая волюта — логарифмическая спираль.

        @param cx Центр X
        @param cy Центр Y
        @param a Начальный радиус
        @param b Параметр роста спирали
        @param turns Количество витков
        @param n_points Количество точек для аппроксимации

        @return (poly_x, poly_y)

        @par Формула
        r(θ) = a · e^(b·θ), где b = ln(φ) / (π/2) для золотой спирали

        @see GoldenRatio.golden_spiral_b()
        """
        theta_max = turns * TWO_PI
        t_pts = np.linspace(0, theta_max, n_points)
        r_pts = a * np.exp(b * t_pts)
        x_pts = cx + r_pts * np.cos(t_pts)
        y_pts = cy + r_pts * np.sin(t_pts)
        t_norm = t_pts / theta_max
        deg = min(20, n_points - 1)
        coeffs_x = np.polyfit(t_norm, x_pts, deg)
        coeffs_y = np.polyfit(t_norm, y_pts, deg)
        return list(reversed(coeffs_x)), list(reversed(coeffs_y))

    @staticmethod
    def lotus(cx, cy, r=0.3, n_petals=5, petal_ratio=2.5) -> List[Tuple[List[float], List[float]]]:
        """
        @brief Цветок лотоса — полумесяц с лепестками.

        @param cx Центр X
        @param cy Центр Y
        @param r Радиус основания
        @param n_petals Количество лепестков
        @param petal_ratio Соотношение длины лепестка к радиусу

        @return Список полиномов: основание + лепестки
        """
        curves = []
        # Полумесяц (основание)
        t = np.linspace(0, np.pi, 100)
        base_x = cx + r * np.cos(t)
        base_y = cy + r * 0.3 * np.sin(t)
        deg = min(10, 99)
        cx_b = np.polyfit(t / np.pi, base_x, deg)
        cy_b = np.polyfit(t / np.pi, base_y, deg)
        curves.append((list(reversed(cx_b)), list(reversed(cy_b))))

        # Лепестки
        for i in range(n_petals):
            angle = np.pi * 0.15 + i * np.pi * 0.7 / (n_petals - 1) if n_petals > 1 else np.pi / 2
            petal_t = np.linspace(0, 1, 80)
            petal_len = r * petal_ratio
            petal_w = r * 0.4
            px = cx + petal_len * petal_t * np.cos(angle)
            py = cy + petal_len * petal_t * np.sin(angle) + petal_w * np.sin(np.pi * petal_t)
            cx_p = np.polyfit(petal_t, px, min(8, 79))
            cy_p = np.polyfit(petal_t, py, min(8, 79))
            curves.append((list(reversed(cx_p)), list(reversed(cy_p))))

        return curves

    @staticmethod
    def palmette(cx, cy, r=0.5, n_leaves=7) -> List[Tuple[List[float], List[float]]]:
        """
        @brief Пальметта — веер из лепестков.

        @param cx Центр X
        @param cy Центр Y
        @param r Радиус (длина лепестка)
        @param n_leaves Количество лепестков (нечётное, 5-9)

        @return Список полиномов: лепестки + стебель

        @par Описание
        Пальметта — основной декоративный мотив ионического и
        коринфского ордеров. Встречается на капителях колонн,
        фризах и вазописи.
        """
        curves = []
        for i in range(n_leaves):
            angle = -np.pi / 2 + (i - (n_leaves - 1) / 2) * (np.pi / (n_leaves + 1))
            leaf_t = np.linspace(0, 1, 60)
            leaf_len = r * (1.0 - 0.15 * abs(i - (n_leaves - 1) / 2))
            leaf_w = r * 0.15 * np.sin(np.pi * leaf_t)
            lx = cx + leaf_len * leaf_t * np.cos(angle) + leaf_w * np.cos(angle + np.pi / 2)
            ly = cy + leaf_len * leaf_t * np.sin(angle) + leaf_w * np.sin(angle + np.pi / 2)
            deg = min(8, 59)
            cx_l = np.polyfit(leaf_t, lx, deg)
            cy_l = np.polyfit(leaf_t, ly, deg)
            curves.append((list(reversed(cx_l)), list(reversed(cy_l))))

        # Стебель
        stem_t = np.linspace(0, 1, 40)
        sx = cx + r * 0.3 * stem_t * np.cos(-np.pi / 2)
        sy = cy + r * 0.3 * stem_t * np.sin(-np.pi / 2)
        cx_s = np.polyfit(stem_t, sx, 3)
        cy_s = np.polyfit(stem_t, sy, 3)
        curves.append((list(reversed(cx_s)), list(reversed(cy_s))))

        return curves

    @staticmethod
    def acanthus_leaf(cx, cy, length=1.0, curl=0.3) -> Tuple[List[float], List[float]]:
        """
        @brief Акант — лист аканта (коринфский ордер).

        @param cx Центр X
        @param cy Центр Y
        @param length Длина листа
        @param curl Степень закручивания краёв

        @return (poly_x, poly_y) — один полином через контур листа
        """
        t = np.linspace(0, 1, 200)
        # Основная форма — заострённый лист
        base_x = length * t * np.sin(np.pi * t) * 0.5
        base_y = length * t
        # Закручивание краёв
        curl_x = curl * np.sin(3 * np.pi * t) * (1 - t)
        x = cx + base_x + curl_x
        y = cy + base_y
        deg = min(15, 199)
        cx_r = np.polyfit(t, x, deg)
        cy_r = np.polyfit(t, y, deg)
        return list(reversed(cx_r)), list(reversed(cy_r))

    @staticmethod
    def column_flute(n_flutes=20, height=3.0, width=0.3) -> List[Tuple[List[float], List[float]]]:
        """
        @brief Флейты колонны — вертикальные желобки.

        @param n_flutes Количество флейт
        @param height Высота колонны
        @param width Ширина (радиус колонны)

        @return Список вертикальных полиномических кривых
        """
        curves = []
        for i in range(n_flutes):
            angle = i * TWO_PI / n_flutes
            flute_x = width * np.cos(angle)
            curves.append(PolyCoeffs.line(flute_x, 0, flute_x, height))
        return curves

    @staticmethod
    def greek_key_border(x0, y0, length, height=0.15, repeat=5) -> List[Tuple[List[float], List[float]]]:
        """
        @brief Граница с греческим ключом (меандр-бордюр).

        @param x0 Начальная X
        @param y0 Начальная Y
        @param length Общая длина
        @param height Высота бордюра
        @param repeat Количество повторов

        @return Список полиномиальных сегментов
        """
        step = length / (repeat * 3)
        return GreekLines.meander(x0, y0, n_segments=repeat * 3, step=step, height=height)


class RomanLines:
    """
    @brief Римские архитектурные линии и паттерны.

    @par Арки
    Полукруглые и остроконечные арки — основа римской архитектуры.

    @par Колонны
    Ордерные колонны (дорический, ионический, коринфский).

    @par Своды
    Крестовые и цилиндрические своды.
    """

    @staticmethod
    def arch(cx, cy, width, height, style="roman") -> Tuple[List[float], List[float]]:
        """
        @brief Арка — римская полукруглая или готическая остроконечная.

        @param cx Центр основания X
        @param cy Центр основания Y
        @param width Ширина пролёта
        @param height Высота арки
        @param style "roman" (полукруг) или "gothic" (остроконечная)

        @return (poly_x, poly_y) — контур арки

        @par Формула (римская)
        y(t) = height · sin(πt), x(t) = cx + (width/2) · cos(πt)

        @par Формула (готическая)
        Две дуги окружностей, пересекающиеся в ключевом камне.
        """
        t = np.linspace(0, np.pi, 200)
        if style == "roman":
            x = cx + (width / 2) * np.cos(t)
            y = cy + height * np.sin(t)
        else:
            # Готическая: две смещённые дуги
            r = width * 0.7
            x1 = cx - width * 0.25 + r * np.cos(t)
            y1 = cy + r * np.sin(t)
            x2 = cx + width * 0.25 - r * np.cos(t)
            y2 = cy + r * np.sin(t)
            # Берём верхнюю часть
            mask = y1 > cy + 0.1
            x = np.concatenate([x1[mask], x2[mask][::-1]])
            y = np.concatenate([y1[mask], y2[mask][::-1]])

        deg = min(15, len(x) - 1)
        cx_p = np.polyfit(np.linspace(0, 1, len(x)), x, deg)
        cy_p = np.polyfit(np.linspace(0, 1, len(y)), y, deg)
        return list(reversed(cx_p)), list(reversed(cy_p))

    @staticmethod
    def column(cx, base_y, height, base_width=0.4, capital_width=0.5,
                order="ionic") -> Dict[str, Any]:
        """
        @brief Колонна в античном ордере.

        @param cx Центр X
        @param base_y Y основания
        @param height Высота
        @param base_width Ширина основания
        @param capital_width Ширина капителя
        @param order "doric", "ionic" или "corinthian"

        @return Словарь с компонентами колонны:
            - shaft: полином ствола
            - base: полином базы
            - capital: полином капителя
            - flutes: список флейт

        @par Entasis
        Колонны имеют утолщение (entasis) по параболе:
        w(t) = base_width + (capital_width - base_width) · t + δ · sin(πt)
        """
        result = {}

        # Ствол с entasis
        t = np.linspace(0, 1, 200)
        entasis = 0.02 * np.sin(np.pi * t)
        shaft_w = base_width + (capital_width - base_width) * t + entasis

        shaft_x_l = cx - shaft_w
        shaft_x_r = cx + shaft_w
        shaft_y = base_y + height * t

        deg = min(12, 199)
        result["shaft_left"] = (
            list(reversed(np.polyfit(shaft_y / height, shaft_x_l, deg).tolist())),
            list(reversed(np.polyfit(shaft_y / height, shaft_y, deg).tolist()))
        )
        result["shaft_right"] = (
            list(reversed(np.polyfit(shaft_y / height, shaft_x_r, deg).tolist())),
            list(reversed(np.polyfit(shaft_y / height, shaft_y, deg).tolist()))
        )

        # База
        base_t = np.linspace(-1, 1, 100)
        base_x = cx + base_width * 1.3 * (1 + 0.2 * base_t ** 2)
        base_y_arr = base_y + 0.15 * np.cos(np.pi * base_t)
        result["base"] = (
            list(reversed(np.polyfit(base_t, base_x, min(4, 99)).tolist())),
            list(reversed(np.polyfit(base_t, base_y_arr, min(4, 99)).tolist()))
        )

        # Капитель
        cap_t = np.linspace(-1, 1, 100)
        cap_w = capital_width * (1 + 0.4 * cap_t ** 2 - 0.1 * cap_t ** 4)
        cap_x = cx + cap_w
        cap_y = base_y + height + 0.3 + 0.15 * np.cos(np.pi * cap_t)
        result["capital"] = (
            list(reversed(np.polyfit(cap_t, cap_x, min(6, 99)).tolist())),
            list(reversed(np.polyfit(cap_t, cap_y, min(6, 99)).tolist()))
        )

        # Флейты
        n_flutes = {"doric": 20, "ionic": 24, "corinthian": 24}.get(order, 20)
        result["flutes"] = GreekLines.column_flute(n_flutes, height, (base_width + capital_width) / 2 * 0.85)

        return result

    @staticmethod
    def dome(cx, cy, radius, n_points=200) -> Tuple[List[float], List[float]]:
        """
        @brief Купол (Пантеон).

        @param cx Центр X
        @param cy Основание Y
        @param radius Радиус купола

        @return (poly_x, poly_y) — профиль купола

        @par Формула
        Полуэллипс: x(t) = cx + R·cos(t), y(t) = cy + R·sin(t)
        """
        t = np.linspace(0, np.pi, n_points)
        x = cx + radius * np.cos(t)
        y = cy + radius * np.sin(t)
        deg = min(10, n_points - 1)
        cx_p = np.polyfit(t / np.pi, x, deg)
        cy_p = np.polyfit(t / np.pi, y, deg)
        return list(reversed(cx_p)), list(reversed(cy_p))

    @staticmethod
    def vault(cx, cy, width, height, depth=0.3) -> Tuple[List[float], List[float]]:
        """
        @brief Цилиндрический свод.

        @param cx Центр X
        @param cy Основание Y
        @param width Ширина
        @param height Высота
        @param depth Глубина (3D-проекция)

        @return (poly_x, poly_y) — контур свода
        """
        t = np.linspace(0, np.pi, 200)
        x = cx + (width / 2) * np.cos(t) + depth * np.sin(t) * 0.3
        y = cy + height * np.sin(t)
        deg = min(10, 199)
        cx_p = np.polyfit(t / np.pi, x, deg)
        cy_p = np.polyfit(t / np.pi, y, deg)
        return list(reversed(cx_p)), list(reversed(cy_p))

    @staticmethod
    def triumphal_arch(cx, cy, w, h) -> List[Tuple[List[float], List[float]]]:
        """
        @brief Триумфальная арка (Константин, Тит).

        @param cx Центр X
        @param cy Основание Y
        @param w Общая ширина
        @param h Общая высота

        @return Список: стены + арки + антаблемент
        """
        curves = []
        # Стены
        curves.append(PolyCoeffs.line(cx - w / 2, cy, cx - w / 2, cy + h))
        curves.append(PolyCoeffs.line(cx + w / 2, cy, cx + w / 2, cy + h))
        # Антаблемент
        curves.append(PolyCoeffs.line(cx - w / 2, cy + h, cx + w / 2, cy + h))
        # Центральная арка
        curves.append(RomanLines.arch(cx, cy, w * 0.5, h * 0.6))
        # Боковые арки (меньше)
        curves.append(RomanLines.arch(cx - w * 0.35, cy, w * 0.25, h * 0.4))
        curves.append(RomanLines.arch(cx + w * 35, cy, w * 0.25, h * 0.4))
        return curves


# @}
# ============================================================
# @defgroup golden Золотое сечение
# @{
# ============================================================

class GoldenRatio:
    """
    @brief Утилиты золотого сечения (φ = 1.618...).

    @par Применение в искусстве
    - Пропорции лица: H/W = φ
    - Межглазовое расстояние: W/φ
    - Ширина глаза: W/φ²
    - Длина носа: H/3
    - Ширина рта: W/φ

    @par Спираль
    Золотая спираль: r(θ) = a · φ^(2θ/π)
    """

    @staticmethod
    def phi() -> float:
        """@brief Значение φ = 1.618033988749895"""
        return PHI

    @staticmethod
    def fibonacci(n: int) -> List[int]:
        """
        @brief Числа Фибоначчи.

        @param n Количество чисел
        @return Список из n чисел Фибоначчи
        """
        fib = [1, 1]
        for _ in range(n - 2):
            fib.append(fib[-1] + fib[-2])
        return fib[:n]

    @staticmethod
    def golden_spiral_b() -> float:
        """
        @brief Параметр b для золотой спирали.

        @return b = ln(φ) / (π/2) ≈ 0.306348962421189

        r(θ) = a · e^(b·θ), при θ=π/2: r = a·φ
        """
        return np.log(PHI) / (np.pi / 2)

    @staticmethod
    def golden_spiral(cx, cy, a=0.1, turns=4, n_points=500) -> Tuple[List[float], List[float]]:
        """
        @brief Золотая спираль (спираль Фибоначчи).

        @param cx Центр X
        @param cy Центр Y
        @param a Начальный радиус
        @param turns Количество витков
        @param n_points Точек для аппроксимации

        @return (poly_x, poly_y) — полиномиальная аппроксимация

        @par Формула
        r(θ) = a · e^(b·θ), b = ln(φ)/(π/2)
        """
        return GreekLines.volute(cx, cy, a, GoldenRatio.golden_spiral_b(), turns, n_points)

    @staticmethod
    def golden_rectangle(x0, y0, width) -> Tuple[List[float], List[float]]:
        """
        @brief Золотой прямоугольник.

        @param x0 Левый нижний угол X
        @param y0 Левый нижний угол Y
        @param width Ширина

        @return (poly_x, poly_y) — замкнутый прямоугольник

        @par Пропорция
        width / height = φ
        """
        height = width / PHI
        verts = [
            (x0, y0), (x0 + width, y0),
            (x0 + width, y0 + height), (x0, y0 + height)
        ]
        return PolyCoeffs.closed_polygon(verts)

    @staticmethod
    def golden_triad(x, y, size) -> List[Tuple[List[float], List[float]]]:
        """
        @brief Триада золотых прямоугольников (деление).

        @param x Центр X
        @param y Центр Y
        @param size Базовый размер

        @return Список из 3 полиномов
        """
        rects = []
        s = size
        cx, cy = x - size / 2, y - size / (2 * PHI)
        for i in range(3):
            rects.append(GoldenRatio.golden_rectangle(cx, cy, s))
            s /= PHI
            cx += s * PHI
        return rects

    @staticmethod
    def face_proportions() -> Dict[str, float]:
        """
        @brief Пропорции лица по золотому сечению (канон Поликлета).

        @return Словарь с пропорциями:
            - face_ratio: H/W = φ
            - eye_distance: W/φ
            - eye_width: W/φ²
            - nose_length: H/3
            - mouth_width: W/φ
            - brow_to_chin: H/3
            - chin_to_mouth: H/(3φ)
        """
        return {
            "face_ratio": PHI,
            "eye_distance": PHI_INV,
            "eye_width": PHI2_INV,
            "nose_length": 1.0 / 3.0,
            "mouth_width": PHI_INV,
            "brow_to_chin": 1.0 / 3.0,
            "chin_to_mouth": 1.0 / (3 * PHI),
        }

    @staticmethod
    def body_proportions(system="polykleitos") -> Dict[str, float]:
        """
        @brief Пропорции тела (канон Поликлета или Лизиппа).

        @param system "polykleitos" (7 голов) или "lysippos" (8 голов)

        @return Словарь с пропорциями
        """
        if system == "lysippos":
            heads = 8
        else:
            heads = 7
        return {
            "head_ratio": heads,
            "body_height": heads,
            "navel_position": 1.0 / PHI,
            "arm_span": 1.0,
            "shoulder_width": 1.0 / PHI,
        }


# @}
# ============================================================
# @defgroup math Полиномиальные конструкторы
# @{
# ============================================================

class PolyCoeffs:
    """
    @brief Генератор полиномиальных коэффициентов.

    Все методы возвращают (poly_x, poly_y) — списки коэффициентов
    полиномов x(t) = Σ aᵢtⁱ и y(t) = Σ bᵢtⁱ.

    @par Пример
    @code
    px, py = PolyCoeffs.line(0, 0, 1, 1)
    px, py = PolyCoeffs.ellipse_poly(0, 0, 2, 3)
    px, py = PolyCoeffs.spiral_poly(0, 0, 0.1, 0.3)
    @endcode
    """

    @staticmethod
    def line(x0, y0, x1, y1) -> Tuple[List[float], List[float]]:
        """
        @brief Линия от (x0,y0) до (x1,y1).

        @param x0 Начальная X
        @param y0 Начальная Y
        @param x1 Конечная X
        @param y1 Конечная Y

        @return (poly_x=[x0, x1-x0], poly_y=[y0, y1-y0])
        """
        return [float(x0), float(x1 - x0)], [float(y0), float(y1 - y0)]

    @staticmethod
    def parabola(x0, y0, xm, ym, x1, y1) -> Tuple[List[float], List[float]]:
        """
        @brief Парабола через 3 точки.

        @param x0, y0 Первая точка
        @param xm, ym Вершина (средняя точка)
        @param x1, y1 Третья точка

        @return Полиномы 2-й степени
        """
        t = np.array([0, 0.5, 1.0])
        cx = np.polyfit(t, [x0, xm, x1], 2)
        cy = np.polyfit(t, [y0, ym, y1], 2)
        return list(reversed(cx)), list(reversed(cy))

    @staticmethod
    def cubic(x0, y0, x1, y1, x2, y2, x3, y3) -> Tuple[List[float], List[float]]:
        """
        @brief Кубический полином через 4 точки.

        @return Полиномы 3-й степени
        """
        t = np.array([0, 1 / 3, 2 / 3, 1.0])
        cx = np.polyfit(t, [x0, x1, x2, x3], 3)
        cy = np.polyfit(t, [y0, y1, y2, y3], 3)
        return list(reversed(cx)), list(reversed(cy))

    @staticmethod
    def ellipse_poly(cx, cy, a, b, n_terms=6) -> Tuple[List[float], List[float]]:
        """
        @brief Эллипс: x = cx + a·cos(t), y = cy + b·sin(t).

        @param cx Центр X
        @param cy Центр Y
        @param a Большая полуось
        @param b Малая полуось
        @param n_terms Количество членов ряда Тейлора

        @return (poly_x, poly_y) для t ∈ [0, 2π]
        """
        px = [float(cx)] + [0.0] * (2 * n_terms)
        py = [float(cy)] + [0.0] * (2 * n_terms)
        fact = 1
        for k in range(1, n_terms + 1):
            fact *= (2 * k) * (2 * k - 1)
            px[2 * k] = a * ((-1) ** k) / fact
            fact2 = 1
            for j in range(1, 2 * k + 1):
                fact2 *= j
            py[2 * k - 1] = b * ((-1) ** (k - 1)) / fact2
        while len(px) > 1 and abs(px[-1]) < 1e-12:
            px.pop()
        while len(py) > 1 and abs(py[-1]) < 1e-12:
            py.pop()
        return px, py

    @staticmethod
    def circle_poly(cx, cy, r, n_terms=6) -> Tuple[List[float], List[float]]:
        """
        @brief Окружность = эллипс с a = b = r.

        @return (poly_x, poly_y) для t ∈ [0, 2π]
        """
        return PolyCoeffs.ellipse_poly(cx, cy, r, r, n_terms)

    @staticmethod
    def spiral_poly(cx, cy, a, b, turns=3, degree=15) -> Tuple[List[float], List[float]]:
        """
        @brief Логарифмическая спираль r = a·e^(b·θ).

        @param cx Центр X
        @param cy Центр Y
        @param a Начальный радиус
        @param b Параметр роста
        @param turns Количество витков
        @param degree Степень аппроксимирующего полинома

        @return (poly_x, poly_y)
        """
        theta_max = turns * TWO_PI
        t_pts = np.linspace(0, theta_max, 500)
        r_pts = a * np.exp(b * t_pts)
        x_pts = cx + r_pts * np.cos(t_pts)
        y_pts = cy + r_pts * np.sin(t_pts)
        t_norm = t_pts / theta_max
        coeffs_x = np.polyfit(t_norm, x_pts, degree)
        coeffs_y = np.polyfit(t_norm, y_pts, degree)
        return list(reversed(coeffs_x)), list(reversed(coeffs_y))

    @staticmethod
    def wave(x0, x1, amplitude, frequency, y_offset=0, n_pts=500) -> Tuple[List[float], List[float]]:
        """
        @brief Волновая кривая y = A·sin(f·π·t) + y0.

        @return (poly_x, poly_y)
        """
        t_pts = np.linspace(0, 1, n_pts)
        x_pts = np.linspace(x0, x1, n_pts)
        y_pts = amplitude * np.sin(frequency * np.pi * t_pts) + y_offset
        deg = min(20, n_pts - 1)
        cx = np.polyfit(t_pts, x_pts, deg)
        cy = np.polyfit(t_pts, y_pts, deg)
        return list(reversed(cx)), list(reversed(cy))

    @staticmethod
    def heart(scale=1.0, degree=20) -> Tuple[List[float], List[float]]:
        """
        @brief Сердце — параметрическая кривая.

        @param scale Масштаб
        @param degree Степень полинома

        @return (poly_x, poly_y)
        """
        t_pts = np.linspace(0, TWO_PI, 500)
        x_pts = scale * 16 * np.sin(t_pts) ** 3
        y_pts = scale * (13 * np.cos(t_pts) - 5 * np.cos(2 * t_pts)
                         - 2 * np.cos(3 * t_pts) - np.cos(4 * t_pts))
        t_norm = t_pts / TWO_PI
        cx = np.polyfit(t_norm, x_pts, degree)
        cy = np.polyfit(t_norm, y_pts, degree)
        return list(reversed(cx)), list(reversed(cy))

    @staticmethod
    def lissajous(a, b, freq_x, freq_y, delta=0, degree=20) -> Tuple[List[float], List[float]]:
        """
        @brief Кривая Лиссажу.

        @param a Амплитуда X
        @param b Амплитуда Y
        @param freq_x Частота X
        @param freq_y Частота Y
        @param delta Фазовый сдвиг

        @return (poly_x, poly_y)
        """
        t_pts = np.linspace(0, TWO_PI, 500)
        x_pts = a * np.sin(freq_x * t_pts + delta)
        y_pts = b * np.sin(freq_y * t_pts)
        t_norm = t_pts / TWO_PI
        cx = np.polyfit(t_norm, x_pts, degree)
        cy = np.polyfit(t_norm, y_pts, degree)
        return list(reversed(cx)), list(reversed(cy))

    @staticmethod
    def from_points(points: List[Tuple[float, float]], degree=None) -> Tuple[List[float], List[float]]:
        """
        @brief Полином через список точек.

        @param points Список точек [(x,y), ...]
        @param degree Степень полинома (авто = min(n-1, 20))

        @return (poly_x, poly_y)
        """
        pts = np.array(points)
        n = len(pts)
        if degree is None:
            degree = min(n - 1, 20)
        t = np.linspace(0, 1, n)
        cx = np.polyfit(t, pts[:, 0], degree)
        cy = np.polyfit(t, pts[:, 1], degree)
        return list(reversed(cx)), list(reversed(cy))

    @staticmethod
    def closed_polygon(vertices: List[Tuple[float, float]], degree=None) -> Tuple[List[float], List[float]]:
        """
        @brief Замкнутый полигон через вершины.

        @param vertices Вершины [(x,y), ...]
        @param degree Степень полинома

        @return (poly_x, poly_y) — замкнутый контур
        """
        verts = list(vertices) + [vertices[0]]
        return PolyCoeffs.from_points(verts, degree)

    @staticmethod
    def scale(coeffs_x, coeffs_y, sx, sy=1.0) -> Tuple[List[float], List[float]]:
        """@brief Масштабирование коэффициентов."""
        return [c * sx for c in coeffs_x], [c * sy for c in coeffs_y]

    @staticmethod
    def translate(coeffs_x, coeffs_y, dx, dy=0.0) -> Tuple[List[float], List[float]]:
        """@brief Перенос."""
        px = list(coeffs_x)
        py = list(coeffs_y)
        if px:
            px[0] += dx
        else:
            px = [dx]
        if py:
            py[0] += dy
        else:
            py = [dy]
        return px, py


# @}
# ============================================================
# @defgroup superformula Суперформула
# @{
# ============================================================

class SuperFormula:
    """
    @brief Суперформула Гелиса-Лилиanked.

    @par Формула
    r(θ) = (|cos(mθ/4)/a|^n2 + |sin(mθ/4)/b|^n3)^(-1/n1)

    @par Параметры
    - m: симметрия (количество «лепестков»)
    - n1: общий показатель
    - n2, n3: показатели для cos и sin
    - a, b: масштаб по осям
    """

    @staticmethod
    def flower(n_petals=6) -> dict:
        """@brief Цветок."""
        return {"sf_params": [n_petals, 1, 1, 1, 1, 1], "scale": 1.0}

    @staticmethod
    def star(n_points=5, sharpness=2) -> dict:
        """@brief Звезда."""
        return {"sf_params": [n_points, sharpness, 7, 7, 1, 1], "scale": 1.0}

    @staticmethod
    def circle() -> dict:
        """@brief Круг."""
        return {"sf_params": [0, 1, 1, 1, 1, 1], "scale": 1.0}

    @staticmethod
    def square() -> dict:
        """@brief Квадрат."""
        return {"sf_params": [4, 100, 100, 100, 1, 1], "scale": 1.0}

    @staticmethod
    def cross() -> dict:
        """@brief Крест."""
        return {"sf_params": [4, 1, 1, 1, 0.5, 0.5], "scale": 1.0}

    @staticmethod
    def blob(m=6, n1=0.5, n2=0.5, n3=0.5) -> dict:
        """@brief Блоб (неправильная форма)."""
        return {"sf_params": [m, n1, n2, n3, 1, 1], "scale": 1.0}

    @staticmethod
    def custom(m, n1, n2, n3, a=1, b=1) -> dict:
        """@brief Произвольная суперформула."""
        return {"sf_params": [m, n1, n2, n3, a, b], "scale": 1.0}


# @}
# ============================================================
# @defgroup objects Объекты и слои
# @{
# ============================================================

class PolyObj:
    """
    @brief Полиномиальный объект — основная единица изображения.

    @par Типы
    - parametric: параметрический x(t), y(t)
    - parametric_fill: параметрический с заливкой
    - superformula: суперформула Гелиса
    """

    def __init__(self, poly_x=None, poly_y=None, **kwargs):
        """
        @brief Конструктор объекта.

        @param poly_x Коэффициенты x(t)
        @param poly_y Коэффициенты y(t)
        @param **kwargs Свойства: color, alpha, linewidth, fill, fill_color, ...
        """
        self.data = {
            "type": kwargs.get("type", "parametric"),
            "poly_x": list(poly_x) if poly_x is not None else [0],
            "poly_y": list(poly_y) if poly_y is not None else [0],
            "t_range": list(kwargs.get("t_range", [0, 1])),
            "n_points": kwargs.get("n_points", 300),
            "color": kwargs.get("color", "#1a1008"),
            "alpha": kwargs.get("alpha", 1.0),
            "linewidth": kwargs.get("linewidth", 1.5),
            "fill": kwargs.get("fill", False),
            "fill_alpha": kwargs.get("fill_alpha", 0.5),
            "fill_color": kwargs.get("fill_color", kwargs.get("color", "#c8a888")),
            "style": kwargs.get("style", "solid"),
        }
        if "sf_params" in kwargs:
            self.data["type"] = "superformula"
            self.data["sf_params"] = kwargs["sf_params"]
            self.data["center"] = kwargs.get("center", [0, 0])
            self.data["scale"] = kwargs.get("scale", 1.0)

    def to_dict(self) -> dict:
        """@brief Сериализация в словарь."""
        return deepcopy(self.data)


class Layer:
    """
    @brief Слой — контейнер объектов.

    @par Описание
    Слои определяют порядок отрисовки (z-order).
    Нижний слой рисуется первым.
    """

    def __init__(self, name="Слой 1"):
        """
        @param name Имя слоя
        """
        self.name = name
        self.objects: List[PolyObj] = []

    def add(self, obj: PolyObj) -> "Layer":
        """@brief Добавить объект."""
        self.objects.append(obj)
        return self

    def to_dict(self) -> dict:
        """@brief Сериализация."""
        return {"name": self.name, "objects": [o.to_dict() for o in self.objects]}


# @}
# ============================================================
# @defgroup canvas Холст
# @{
# ============================================================

class Canvas:
    """
    @brief Полиномиальный холст — главный класс API.

    @par Описание
    Управляет слоями, объектами, сохранением и рендерингом.
    Поддерживает цепочки вызовов (fluent API).

    @par Пример
    @code
    c = Canvas(name="Арт", background="#1a1a2a")
    c.add_layer("Фон")
    c.circle(0, 0, 2, fill=True, fill_color="#c8a040")
    c.add_layer("Фигуры")
    c.flower(-2, 1, n=5, fill=True, fill_color="#d89090")
    c.save("art.polyart")
    c.render("art.png")
    @endcode
    """

    def __init__(self, width=10, height=10, background="#f5efe0",
                 xlim=(-5, 5), ylim=(-5, 5), name="Untitled", author="Artist"):
        """
        @brief Конструктор холста.

        @param width Ширина (в дюймах для figsize)
        @param height Высота
        @param background Цвет фона (#hex)
        @param xlim Пределы X [min, max]
        @param ylim Пределы Y [min, max]
        @param name Название произведения
        @param author Автор
        """
        self.data = {
            "format": "polyart",
            "version": "2.0.0",
            "meta": {"name": name, "author": author, "description": "", "phi": PHI},
            "canvas": {"width": width, "height": height, "background": background,
                        "xlim": list(xlim), "ylim": list(ylim)},
            "layers": [],
            "formulas": [],
        }
        self._current_layer = 0
        self.add_layer("Основной")

    # --- Слои ---
    def add_layer(self, name=None) -> "Canvas":
        """@brief Добавить слой."""
        if name is None:
            name = f"Слой {len(self.data['layers']) + 1}"
        self.data["layers"].append({"name": name, "objects": []})
        self._current_layer = len(self.data["layers"]) - 1
        return self

    def layer(self, index_or_name) -> "Canvas":
        """@brief Переключиться на слой по индексу или имени."""
        if isinstance(index_or_name, int):
            self._current_layer = index_or_name
        else:
            for i, l in enumerate(self.data["layers"]):
                if l["name"] == index_or_name:
                    self._current_layer = i
                    break
        return self

    def _add_obj(self, obj: PolyObj) -> "Canvas":
        self.data["layers"][self._current_layer]["objects"].append(obj.to_dict())
        return self

    # --- Формулы ---
    def add_formula(self, expr, x, y, fontsize=8, color="#8a6a4a") -> "Canvas":
        """@brief Добавить аннотацию-формулу."""
        self.data["formulas"].append({
            "expr": expr, "x": x, "y": y,
            "fontsize": fontsize, "color": color
        })
        return self

    # --- Быстрые методы ---
    def add(self, obj: PolyObj) -> "Canvas":
        """@brief Добавить PolyObj."""
        return self._add_obj(obj)

    def line(self, x0, y0, x1, y1, **kw) -> "Canvas":
        """@brief Линия."""
        px, py = PolyCoeffs.line(x0, y0, x1, y1)
        return self._add_obj(PolyObj(px, py, t_range=[0, 1], **kw))

    def polyline(self, points, **kw) -> "Canvas":
        """@brief Полилиния."""
        px, py = PolyCoeffs.from_points(points)
        return self._add_obj(PolyObj(px, py, t_range=[0, 1], **kw))

    def ellipse(self, cx, cy, a, b, **kw) -> "Canvas":
        """@brief Эллипс."""
        px, py = PolyCoeffs.ellipse_poly(cx, cy, a, b)
        return self._add_obj(PolyObj(px, py, t_range=[0, TWO_PI], **kw))

    def circle(self, cx, cy, r, **kw) -> "Canvas":
        """@brief Окружность."""
        px, py = PolyCoeffs.circle_poly(cx, cy, r)
        return self._add_obj(PolyObj(px, py, t_range=[0, TWO_PI], **kw))

    def spiral(self, cx, cy, a, b, turns=3, **kw) -> "Canvas":
        """@brief Логарифмическая спираль."""
        px, py = PolyCoeffs.spiral_poly(cx, cy, a, b, turns)
        return self._add_obj(PolyObj(px, py, t_range=[0, 1], **kw))

    def wave(self, x0, x1, amp, freq, y_off=0, **kw) -> "Canvas":
        """@brief Волна."""
        px, py = PolyCoeffs.wave(x0, x1, amp, freq, y_off)
        return self._add_obj(PolyObj(px, py, t_range=[0, 1], **kw))

    def heart(self, cx=0, cy=0, scale=1.0, **kw) -> "Canvas":
        """@brief Сердце."""
        px, py = PolyCoeffs.heart(scale)
        px[0] += cx
        py[0] += cy
        return self._add_obj(PolyObj(px, py, t_range=[0, 1], **kw))

    def lissajous(self, a, b, fx, fy, delta=0, **kw) -> "Canvas":
        """@brief Кривая Лиссажу."""
        px, py = PolyCoeffs.lissajous(a, b, fx, fy, delta)
        return self._add_obj(PolyObj(px, py, t_range=[0, 1], **kw))

    def star(self, cx=0, cy=0, scale=1.0, n=5, **kw) -> "Canvas":
        """@brief Звезда (суперформула)."""
        sf = SuperFormula.star(n)
        sf["scale"] = scale
        sf["center"] = [cx, cy]
        return self._add_obj(PolyObj(**sf, **kw))

    def flower(self, cx=0, cy=0, scale=1.0, n=6, **kw) -> "Canvas":
        """@brief Цветок (суперформула)."""
        sf = SuperFormula.flower(n)
        sf["scale"] = scale
        sf["center"] = [cx, cy]
        return self._add_obj(PolyObj(**sf, **kw))

    def blob(self, cx=0, cy=0, scale=1.0, m=6, **kw) -> "Canvas":
        """@brief Блоб."""
        sf = SuperFormula.blob(m)
        sf["scale"] = scale
        sf["center"] = [cx, cy]
        return self._add_obj(PolyObj(**sf, **kw))

    def superformula(self, cx=0, cy=0, scale=1.0, **sf_kw) -> "Canvas":
        """@brief Произвольная суперформула."""
        sf = SuperFormula.custom(**sf_kw)
        sf["scale"] = scale
        sf["center"] = [cx, cy]
        return self._add_obj(PolyObj(**sf))

    def polygon(self, vertices, **kw) -> "Canvas":
        """@brief Полигон."""
        px, py = PolyCoeffs.closed_polygon(vertices)
        kw.setdefault("fill", True)
        return self._add_obj(PolyObj(px, py, t_range=[0, 1], **kw))

    def meander(self, x0, y0, n=8, **kw) -> "Canvas":
        """@brief Меандр (греческий ключ)."""
        for seg in GreekLines.meander(x0, y0, n):
            px, py = seg
            self._add_obj(PolyObj(px, py, t_range=[0, 1], **kw))
        return self

    def arch(self, cx, cy, w, h, **kw) -> "Canvas":
        """@brief Римская арка."""
        px, py = RomanLines.arch(cx, cy, w, h)
        return self._add_obj(PolyObj(px, py, t_range=[0, 1], **kw))

    def golden_spiral(self, cx=0, cy=0, a=0.1, turns=4, **kw) -> "Canvas":
        """@brief Золотая спираль."""
        px, py = GoldenRatio.golden_spiral(cx, cy, a, turns)
        return self._add_obj(PolyObj(px, py, t_range=[0, 1], **kw))

    def golden_rectangle(self, x0, y0, width, **kw) -> "Canvas":
        """@brief Золотой прямоугольник."""
        px, py = GoldenRatio.golden_rectangle(x0, y0, width)
        return self._add_obj(PolyObj(px, py, t_range=[0, 1], fill=True, **kw))

    def volute(self, cx, cy, a=0.5, **kw) -> "Canvas":
        """@brief Ионическая волюта."""
        px, py = GreekLines.volute(cx, cy, a)
        return self._add_obj(PolyObj(px, py, t_range=[0, 1], **kw))

    # --- Файловые операции ---
    def save(self, filepath: str) -> "Canvas":
        """
        @brief Сохранить в .polyart.

        @param filepath Путь к файлу (.polyart)
        """
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
        print(f"[OK] Saved: {filepath} ({os.path.getsize(filepath)} bytes)")
        return self

    def load(self, filepath: str) -> "Canvas":
        """
        @brief Загрузить .polyart.

        @param filepath Путь к файлу
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        self._current_layer = 0
        print(f"[OK] Loaded: {filepath}")
        return self

    @classmethod
    def from_file(cls, filepath: str) -> "Canvas":
        """@brief Загрузить из файла (фабричный метод)."""
        c = cls()
        return c.load(filepath)

    def render(self, save_to=None, dpi=200, figsize=None) -> "Canvas":
        """
        @brief Рендер в PNG/SVG/PDF через matplotlib.

        @param save_to Путь для сохранения (если None — только показать)
        @param dpi Разрешение
        @param figsize Размер фигуры (auto из canvas)
        """
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt

        canvas = self.data["canvas"]
        w = figsize[0] if figsize else canvas.get("width", 10)
        h = figsize[1] if figsize else canvas.get("height", 10)
        fig, ax = plt.subplots(1, 1, figsize=(w, h),
                                facecolor=canvas.get("background", "#f5efe0"))
        ax.set_facecolor(canvas.get("background", "#f5efe0"))
        ax.set_xlim(canvas.get("xlim", [-5, 5]))
        ax.set_ylim(canvas.get("ylim", [-5, 5]))
        ax.set_aspect('equal')
        ax.axis('off')

        for layer in self.data.get("layers", []):
            for obj in layer.get("objects", []):
                self._draw(ax, obj)

        for f in self.data.get("formulas", []):
            ax.text(f["x"], f["y"], f["expr"],
                    fontsize=f.get("fontsize", 8),
                    fontfamily='serif', color=f.get("color", "#8a6a4a"),
                    fontstyle='italic')

        if save_to:
            fig.savefig(save_to, dpi=dpi, bbox_inches='tight',
                        facecolor=canvas.get("background", "#f5efe0"))
            print(f"[OK] Rendered: {save_to}")
        plt.close(fig)
        return self

    def _draw(self, ax, obj):
        """@brief Отрисовка одного объекта."""
        otype = obj.get("type", "parametric")
        color = obj.get("color", "#1a1008")
        alpha = obj.get("alpha", 1.0)
        lw = obj.get("linewidth", 1.5)
        ls = {"solid": "-", "dashed": "--", "dotted": ":"}.get(obj.get("style", "solid"), "-")
        n = obj.get("n_points", 300)

        def _eval(coeffs, t):
            r = np.zeros_like(t, dtype=float)
            for i, c in enumerate(coeffs):
                r += c * t ** i
            return r

        if otype in ("parametric", "parametric_fill"):
            tr = obj.get("t_range", [0, 1])
            t = np.linspace(tr[0], tr[1], n)
            x = _eval(obj.get("poly_x", [0]), t)
            y = _eval(obj.get("poly_y", [0]), t)
            if obj.get("fill"):
                fc = obj.get("fill_color", color)
                ax.fill(x, y, color=fc, alpha=obj.get("fill_alpha", 0.5))
            ax.plot(x, y, color=color, alpha=alpha, linewidth=lw, linestyle=ls)

        elif otype == "superformula":
            sp = obj.get("sf_params", [6, 1, 1, 1, 1, 1])
            center = obj.get("center", [0, 0])
            scale = obj.get("scale", 1.0)
            theta = np.linspace(0, TWO_PI, n)
            m, n1, n2, n3, a, b = sp
            t1 = np.abs(np.cos(m * theta / 4) / a)
            t2 = np.abs(np.sin(m * theta / 4) / b)
            with np.errstate(divide='ignore', invalid='ignore'):
                r = np.where(t1 == 0, 0, t1 ** n2) + np.where(t2 == 0, 0, t2 ** n3)
                r = np.where(r == 0, 0, r ** (-1.0 / n1))
            x = center[0] + scale * r * np.cos(theta)
            y = center[1] + scale * r * np.sin(theta)
            if obj.get("fill"):
                fc = obj.get("fill_color", color)
                ax.fill(x, y, color=fc, alpha=obj.get("fill_alpha", 0.5))
            ax.plot(x, y, color=color, alpha=alpha, linewidth=lw, linestyle=ls)

    def info(self):
        """@brief Вывод информации о холсте."""
        total = sum(len(l.get("objects", [])) for l in self.data["layers"])
        print(f"  Canvas: {self.data['canvas']['width']}x{self.data['canvas']['height']}")
        print(f"  Layers: {len(self.data['layers'])}")
        print(f"  Objects: {total}")
        for i, l in enumerate(self.data["layers"]):
            print(f"    [{i}] {l['name']}: {len(l.get('objects', []))} objects")
        return self

    def __repr__(self):
        total = sum(len(l.get("objects", [])) for l in self.data["layers"])
        return f"<Canvas '{self.data['meta']['name']}' | {len(self.data['layers'])} layers | {total} objects>"


# @}
# ============================================================
# @defgroup templates Готовые шаблоны
# @{
# ============================================================

class Templates:
    """@brief Готовые шаблоны полиномических композиций."""

    @staticmethod
    def apollo_face() -> Canvas:
        """@brief Лицо Аполлона по золотому сечению."""
        c = Canvas(name="Apollo", xlim=(-3, 3), ylim=(-3, 3))
        c.ellipse(0, 0, 1.3, 1.8, fill=True, fill_color="#e0c8a8", color="#c8a888")
        for ex in [-0.5, 0.5]:
            c.ellipse(ex, 0.15, 0.22, 0.09, fill=True, fill_color="white", color="#3a2818")
            c.ellipse(ex, 0.14, 0.06, 0.05, fill=True, fill_color="#1a1008")
        for bx in [-0.5, 0.5]:
            c.line(bx - 0.15, 0.33, bx + 0.15, 0.35, color="#3a2818", linewidth=2.5)
        c.circle(0, 0.2, 2.0, color="#e8c860", linewidth=1.0, alpha=0.3)
        return c

    @staticmethod
    def rose(n=5, layers=3) -> Canvas:
        """@brief Роза из суперформул."""
        c = Canvas(name="Rose", xlim=(-2, 2), ylim=(-2, 2))
        colors = ["#d85050", "#c04040", "#a03030"]
        for i in range(layers):
            sf = SuperFormula.flower(n * (i + 1))
            sf["scale"] = 1.5 - i * 0.3
            sf["center"] = [0, 0]
            c.add(PolyObj(fill=True, fill_color=colors[i % len(colors)],
                          fill_alpha=0.5, color="#8a2020", linewidth=1.0, **sf))
        return c

    @staticmethod
    def greek_vase() -> Canvas:
        """@brief Греческая ваза с меандром."""
        c = Canvas(name="GreekVase", xlim=(-2, 2), ylim=(-3, 3))
        # Тело вазы
        body_t = np.linspace(0, 2 * np.pi, 500)
        body_r = 1.0 + 0.15 * np.cos(2 * body_t) - 0.08 * np.cos(4 * body_t)
        bx = body_r * np.cos(body_t)
        by = -0.3 + 1.5 * np.sin(body_t)
        deg = min(15, 499)
        cpx = np.polyfit(body_t / TWO_PI, bx, deg)
        cpy = np.polyfit(body_t / TWO_PI, by, deg)
        c.add(PolyObj(list(reversed(cpx)), list(reversed(cpy)),
                       t_range=[0, TWO_PI], fill=True, fill_color="#c45a30",
                       color="#1a1008", linewidth=2))
        # Меандр
        c.meander(-0.8, 0.8, n=6, color="#1a1008", linewidth=1.2)
        c.meander(-0.8, -0.8, n=6, color="#1a1008", linewidth=1.2)
        return c

    @staticmethod
    def parthenon() -> Canvas:
        """@brief Парфенон — колонны + фронтон."""
        c = Canvas(name="Parthenon", xlim=(-4, 4), ylim=(-2, 4))
        # Колонны
        for x in np.arange(-3, 3.5, 0.8):
            c.line(x, 0, x, 3, color="#e8dcc8", linewidth=3)
            c.circle(x, 3.1, 0.15, fill=True, fill_color="#e8dcc8",
                      color="#b8a88a", linewidth=0.8)
        # Фронтон (парабола)
        fronton_x = np.linspace(-3.5, 3.5, 200)
        fronton_y = 3.5 - 0.3 * fronton_x ** 2
        deg = min(5, 199)
        c.add(PolyObj(list(reversed(np.polyfit(fronton_x / 3.5, fronton_x, deg).tolist())),
                       list(reversed(np.polyfit(fronton_x / 3.5, fronton_y, deg).tolist())),
                       t_range=[0, 1], color="#8B7355", linewidth=2))
        c.line(-3.5, 3, 3.5, 3, color="#8B7355", linewidth=1.5)
        return c

    @staticmethod
    def roman_arch() -> Canvas:
        """@brief Римская арка."""
        c = Canvas(name="RomanArch", xlim=(-3, 3), ylim=(-1, 4))
        c.arch(0, 0, 4, 3, color="#b8a88a", linewidth=2, fill=True, fill_color="#f0e8d8")
        c.line(-2, 0, -2, 3, color="#8B7355", linewidth=3)
        c.line(2, 0, 2, 3, color="#8B7355", linewidth=3)
        c.line(-2, 3, 2, 3, color="#8B7355", linewidth=2)
        return c

    @staticmethod
    def golden_composition() -> Canvas:
        """@brief Композиция в золотом сечении."""
        c = Canvas(name="Golden", xlim=(-5, 5), ylim=(-5, 5))
        c.golden_rectangle(-2.5, -2.5, 5, color="#c8a040", linewidth=1.5, fill=False)
        c.golden_spiral(0, 0, a=0.1, turns=4, color="#c8a040", linewidth=1.5)
        c.add_formula("phi = 1.618...", 2.5, -4.5, fontsize=12, color="#c8a040")
        return c

    @staticmethod
    def geometric_tile() -> Canvas:
        """@brief Геометрический узор (мозаика)."""
        c = Canvas(name="Mosaic", xlim=(-5, 5), ylim=(-5, 5), background="#2a1a0a")
        for x in range(-4, 5):
            for y in range(-4, 5):
                c.circle(x, y, 0.3, fill=True,
                          fill_color="#c8a040" if (x + y) % 2 == 0 else "#5a3a1a",
                          fill_alpha=0.6, color="#8a6a40", linewidth=0.3)
        return c


# @}

if __name__ == "__main__":
    print("[PolyArt API v2.0 - Demo]")

    c = Templates.greek_vase()
    c.save("demo_greek_vase.polyart")
    c.render("demo_greek_vase.png")
    c.info()

    c2 = Templates.parthenon()
    c2.save("demo_parthenon.polyart")
    c2.render("demo_parthenon.png")

    c3 = Templates.golden_composition()
    c3.save("demo_golden.polyart")
    c3.render("demo_golden.png")

    print("[OK] All demos saved!")
