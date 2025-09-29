#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Guitar Life - Цветовые палитры
=============================

Все функции цветовых палитр и управление палитрами.
"""

import colorsys
import math
import random
from functools import lru_cache
from typing import Tuple, Dict, Any

from .constants import HSV_DESIGN_PALETTES, HSV_COLOR_PALETTES, PALETTE_OPTIONS

# ==================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ====================

def clamp01(x: float) -> float:
    """Ограничивает значение в диапазоне [0, 1]"""
    return max(0.0, min(1.0, x))

def lerp(a: float, b: float, t: float) -> float:
    """Линейная интерполяция между a и b"""
    return a + (b - a) * t

@lru_cache(maxsize=1024)
def _cached_hsv_to_rgb(h: float, s: float, v: float) -> tuple[int, int, int]:
    """Кэшированная конверсия HSV в RGB"""
    r, g, b = colorsys.hsv_to_rgb((h % 360) / 360.0, clamp01(s), clamp01(v))
    return (int(r * 255), int(g * 255), int(b * 255))

def get_hsv_design_palettes():
    """Возвращает палитры для HSV-дизайнов (комбинированный режим)"""
    return HSV_DESIGN_PALETTES

def get_hsv_color_palettes():
    """Возвращает палитры для HSV палитр (только RMS режим)"""
    return HSV_COLOR_PALETTES

def get_palette_by_category(category: str):
    """Возвращает палитры по категории"""
    if category == "Возраст + RMS":
        return HSV_DESIGN_PALETTES
    elif category == "Только RMS":
        return HSV_COLOR_PALETTES
    else:
        return PALETTE_OPTIONS

# ==================== БАЗОВЫЕ ФУНКЦИИ ПАЛИТР ====================

def hue_bgyr_from_t(t: float) -> float:
    t = clamp01(t)
    if t < 1/3:   return lerp(220.0, 120.0, t*3.0)
    elif t < 2/3: return lerp(120.0, 60.0, (t-1/3)*3.0)
    else:         return lerp(60.0, 0.0, (t-2/3)*3.0)

def hue_br_from_t(t: float) -> float:
    return lerp(220.0, 0.0, clamp01(t))

# ==================== МАТЕРИАЛЬНЫЕ ПАЛИТРЫ ====================

def hue_bronze_from_t(t: float) -> tuple[float, float, float]:
    """Бронза: коричнево-оранжевый переход"""
    t = clamp01(t)
    hue = 30.0 + 15.0 * t  # 30 (коричневый) -> 45 (оранжевый)
    sat = 0.7 + 0.1 * t
    val = 0.7 + 0.2 * t
    return (hue, sat, val)

def hue_pearl_from_t(t: float) -> tuple[float, float, float]:
    """Жемчуг: бело-розовый переход"""
    t = clamp01(t)
    hue = 0.0 + 10.0 * t  # 0 (белый) -> 10 (розоватый)
    sat = 0.05 + 0.15 * t
    val = 1.0 - 0.1 * t
    return (hue, sat, val)

def hue_coral_from_t(t: float) -> tuple[float, float, float]:
    """Коралл: розово-оранжевый переход"""
    t = clamp01(t)
    hue = 10.0 + 20.0 * t  # 10 (розовый) -> 30 (оранжевый)
    sat = 0.8 - 0.1 * t
    val = 0.9 - 0.1 * t
    return (hue, sat, val)

def hue_jade_from_t(t: float) -> tuple[float, float, float]:
    """Нефрит: зеленый переход"""
    t = clamp01(t)
    hue = 140.0 + 20.0 * t  # 140 (зеленый) -> 160 (сине-зеленый)
    sat = 0.7 + 0.1 * t
    val = 0.8 + 0.1 * t
    return (hue, sat, val)

def hue_topaz_from_t(t: float) -> tuple[float, float, float]:
    """Топаз: желто-голубой переход"""
    t = clamp01(t)
    hue = 50.0 + 70.0 * t  # 50 (желтый) -> 120 (голубой)
    sat = 0.7 + 0.2 * t
    val = 0.9 - 0.1 * t
    return (hue, sat, val)

def hue_gold_from_t(t: float) -> tuple[float, float, float]:
    """Золотой: желто-оранжевый переход"""
    t = clamp01(t)
    hue = 47.0 + 25.0 * t  # 47 (желтый) -> 72 (оранжевый)
    sat = 0.85 - 0.15 * t
    val = 1.0 - 0.1 * t
    return (hue, sat, val)

def hue_silver_from_t(t: float) -> tuple[float, float, float]:
    """Серебро: бело-серый переход"""
    t = clamp01(t)
    hue = 0.0
    sat = 0.0 + 0.05 * t
    val = 1.0 - 0.3 * t
    return (hue, sat, val)

def hue_copper_from_t(t: float) -> tuple[float, float, float]:
    """Медь: красно-оранжевый переход"""
    t = clamp01(t)
    hue = 18.0 + 18.0 * t  # 18 (оранжевый) -> 36 (красно-оранжевый)
    sat = 0.8 - 0.1 * t
    val = 0.9 - 0.2 * t
    return (hue, sat, val)

def hue_emerald_from_t(t: float) -> tuple[float, float, float]:
    """Изумруд: зеленый переход"""
    t = clamp01(t)
    hue = (0.33 + 0.07 * t) * 360.0  # 0.33 (зеленый) -> 0.40 (сине-зеленый) in degrees
    sat = 0.85 - 0.1 * t
    val = 1.0 - 0.1 * t
    return (hue, sat, val)

def hue_sapphire_from_t(t: float) -> tuple[float, float, float]:
    """Сапфир: синий переход"""
    t = clamp01(t)
    hue = (0.58 + 0.07 * t) * 360.0  # 0.58 (синий) -> 0.65 (фиолетово-синий)
    sat = 0.85 - 0.1 * t
    val = 1.0 - 0.1 * t
    return (hue, sat, val)

def hue_ruby_from_t(t: float) -> tuple[float, float, float]:
    """Рубин: красно-розовый переход"""
    t = clamp01(t)
    hue = (0.97 - 0.07 * t) * 360.0  # 0.97 (красный) -> 0.90 (розовый)
    sat = 0.85 - 0.1 * t
    val = 1.0 - 0.1 * t
    return (hue, sat, val)

def hue_amethyst_from_t(t: float) -> tuple[float, float, float]:
    """Аметист: фиолетовый переход"""
    t = clamp01(t)
    hue = (0.76 + 0.07 * t) * 360.0  # 0.76 (фиолетовый) -> 0.83 (сине-фиолетовый)
    sat = 0.85 - 0.1 * t
    val = 1.0 - 0.1 * t
    return (hue, sat, val)

# ==================== БАЗОВЫЕ ЦВЕТОВЫЕ ПАЛИТРЫ ====================

def hue_grayscale_from_t(t: float) -> tuple:
    """Градиент от белого к черному"""
    t = clamp01(t)
    h = 0.0
    s = 0.0
    v = 1.0 - t
    return h, s, v

def hue_red_darkred_gray_black_from_t(t: float) -> tuple:
    """Красный -> темно-красный -> серый -> черный"""
    t = clamp01(t)
    if t < 0.33:
        # Красный к темно-красному
        h = 0.0
        s = 1.0
        v = 1.0 - t * 0.5
    elif t < 0.66:
        # Темно-красный к серому
        h = 0.0
        s = 0.5 - (t-0.33)*1.5
        v = 0.5 - (t-0.33)*0.5
    else:
        # Серый к черному
        h = 0.0
        s = 0.0
        v = 0.5 - (t-0.66)*1.5
    return h, s, v

def hue_sepia_from_t(t: float) -> tuple[float, float, float]:
    """Sepia palette: brownish-yellow gradient"""
    t = clamp01(t)
    h = 30.0
    s = lerp(0.5, 0.2, t)
    v = lerp(0.9, 0.6, t)
    return h, s, v

# ==================== ПРИРОДНЫЕ ПАЛИТРЫ ====================

def hue_fire_from_t(t: float) -> Tuple[float, float, float]:
    """Огненная палитра"""
    t = clamp01(t)
    if t < 0.25:
        h, s, v = 0.0, 1.0, lerp(0.05, 0.25, t/0.25)
    elif t < 0.5:
        k = (t-0.25)/0.25
        h, s, v = 0.0, 1.0, lerp(0.25, 0.6, k)
    elif t < 0.75:
        k = (t-0.5)/0.25
        h, s, v = lerp(20.0, 50.0, k), 1.0, lerp(0.6, 0.9, k)
    else:
        k = (t-0.75)/0.25
        h, s, v = 55.0, lerp(1.0, 0.0, k), 1.0
    return h, s, v

def hue_ocean_from_t(t: float) -> Tuple[float, float, float]:
    """Океанская палитра"""
    t = clamp01(t)
    if t < 0.5:
        k = t/0.5; h = lerp(220.0, 200.0, k); s = 1.0; v = lerp(0.35, 0.85, k)
    else:
        k = (t-0.5)/0.5; h = lerp(200.0, 180.0, k); s = lerp(1.0, 0.2, k); v = lerp(0.85, 1.0, k)
    return h, s, v

def hue_neon_from_t(t: float) -> Tuple[float, float, float]:
    """Неоновая палитра"""
    t = clamp01(t)
    if t < 1/3:      h = lerp(285.0, 240.0, t*3.0)
    elif t < 2/3:    h = lerp(240.0, 120.0, (t-1/3)*3.0)
    else:            h = lerp(120.0, 315.0, (t-2/3)*3.0)
    s = 1.0; v = 1.0
    return h, s, v

def hue_ukraine_from_t(t: float) -> Tuple[float, float, float]:
    """Украинская палитра"""
    t = clamp01(t)
    if t < 0.5:
        k = t/0.5; h = 50.0; s = lerp(1.0, 0.6, k); v = lerp(0.95, 1.0, k)
    else:
        k = (t-0.5)/0.5; h = lerp(50.0, 220.0, k); s = lerp(0.6, 1.0, k); v = lerp(1.0, 0.9, k)
    return h, s, v

# ==================== СЕЗОННЫЕ ПАЛИТРЫ ====================

def hue_spring_from_t(t: float) -> tuple:
    """Весенняя палитра: зеленый -> желтый -> розовый"""
    t = clamp01(t)
    if t < 0.5:
        h = 90 + t * 60  # 90-120 (зел) -> 150 (желт)
        s = 0.8 + 0.2 * t
        v = 0.8 + 0.2 * t
    else:
        h = 150 + (t-0.5)*120  # 150-210 (розовый)
        s = 1.0
        v = 1.0
    return h, s, v

def hue_summer_from_t(t: float) -> tuple:
    """Летняя палитра: желтый -> оранжевый -> красный"""
    t = clamp01(t)
    h = 50 + t * 40  # 50-90
    s = 1.0
    v = 1.0
    return h, s, v

def hue_autumn_from_t(t: float) -> tuple:
    """Осенняя палитра: оранжевый -> коричневый -> красный"""
    t = clamp01(t)
    h = 30 + t * 30  # 30-60
    s = 0.7 + 0.3 * t
    v = 0.7 + 0.3 * (1-t)
    return h, s, v

def hue_winter_from_t(t: float) -> tuple:
    """Зимняя палитра: голубой -> синий -> белый"""
    t = clamp01(t)
    if t < 0.7:
        h = 180 + t * 60  # 180-222
        s = 0.5 + 0.5 * (1-t)
        v = 0.8 + 0.2 * t
    else:
        h = 222
        s = 0.2
        v = 1.0
    return h, s, v

def hue_ice_from_t(t: float) -> tuple:
    """Ледяная палитра: голубой -> белый"""
    t = clamp01(t)
    h = 190 + t * 20
    s = 0.3 + 0.7 * (1-t)
    v = 0.9 + 0.1 * t
    return h, s, v

def hue_forest_from_t(t: float) -> tuple:
    """Лесная палитра: зеленый -> темно-зеленый"""
    t = clamp01(t)
    h = 120 + t * 30
    s = 0.7 + 0.3 * (1-t)
    v = 0.6 + 0.4 * t
    return h, s, v

def hue_desert_from_t(t: float) -> tuple:
    """Пустынная палитра: песочный -> желтый -> светло-коричневый"""
    t = clamp01(t)
    h = 40 + t * 20
    s = 0.6 + 0.4 * (1-t)
    v = 0.9
    return h, s, v

# ==================== НАУЧНЫЕ ПАЛИТРЫ ====================

def hue_viridis_from_t(t: float) -> tuple:
    """Viridis палитра: зеленый -> синий -> желтый"""
    t = clamp01(t)
    if t < 0.5:
        h = 90 + t * 60  # 90-120
        s = 1.0
        v = 0.8 + 0.2 * t
    else:
        h = 120 + (t-0.5)*120  # 120-180
        s = 1.0
        v = 1.0
    return h, s, v

def hue_inferno_from_t(t: float) -> tuple:
    """Inferno палитра: темно-красный -> оранжевый -> желтый"""
    t = clamp01(t)
    h = 10 + t * 50
    s = 1.0
    v = 0.7 + 0.3 * t
    return h, s, v

def hue_magma_from_t(t: float) -> tuple:
    """Magma палитра: фиолетовый -> красный -> желтый"""
    t = clamp01(t)
    h = 300 - t * 120
    s = 1.0
    v = 0.7 + 0.3 * t
    return h, s, v

def hue_plasma_from_t(t: float) -> tuple:
    """Plasma палитра: синий -> фиолетовый -> желтый"""
    t = clamp01(t)
    h = 240 + t * 60
    s = 1.0
    v = 0.8 + 0.2 * t
    return h, s, v

def hue_cividis_from_t(t: float) -> tuple:
    """Cividis палитра: зеленый -> желтый -> коричневый"""
    t = clamp01(t)
    h = 90 + t * 60
    s = 0.8 + 0.2 * t
    v = 0.7 + 0.3 * (1-t)
    return h, s, v

def hue_twilight_from_t(t: float) -> tuple:
    """Twilight палитра: синий -> фиолетовый -> розовый"""
    t = clamp01(t)
    h = 240 + t * 60
    s = 0.7 + 0.3 * t
    v = 0.8 + 0.2 * (1-t)
    return h, s, v

# ==================== СЛОЖНЫЕ ПАЛИТРЫ ====================

def hue_rainbow_smooth_from_t(t: float) -> Tuple[float, float, float]:
    """Плавная радужная палитра через весь спектр HSV"""
    t = clamp01(t)
    h = 360.0 * (1.0 - t)  # От красного (0°) до фиолетового (360°)
    s = 1.0
    v = 1.0
    return h, s, v

def hue_sunset_from_t(t: float) -> Tuple[float, float, float]:
    """Закатная палитра: фиолетовый -> розовый -> оранжевый -> желтый"""
    t = clamp01(t)
    if t < 0.25:
        # Темно-фиолетовый к фиолетовому
        k = t / 0.25
        h = lerp(280.0, 300.0, k)
        s = 1.0
        v = lerp(0.3, 0.6, k)
    elif t < 0.5:
        # Фиолетовый к розовому
        k = (t - 0.25) / 0.25
        h = lerp(300.0, 320.0, k)
        s = lerp(1.0, 0.8, k)
        v = lerp(0.6, 0.9, k)
    elif t < 0.75:
        # Розовый к оранжевому
        k = (t - 0.5) / 0.25
        h = lerp(320.0, 30.0, k)
        s = lerp(0.8, 1.0, k)
        v = lerp(0.9, 1.0, k)
    else:
        # Оранжевый к желтому
        k = (t - 0.75) / 0.25
        h = lerp(30.0, 60.0, k)
        s = lerp(1.0, 0.8, k)
        v = 1.0
    return h, s, v

def hue_aurora_from_t(t: float) -> Tuple[float, float, float]:
    """Палитра северного сияния: зеленый -> синий -> фиолетовый -> розовый"""
    t = clamp01(t)
    if t < 0.33:
        # Зеленый к сине-зеленому
        k = t / 0.33
        h = lerp(120.0, 180.0, k)
        s = lerp(1.0, 0.8, k)
        v = lerp(0.7, 1.0, k)
    elif t < 0.66:
        # Сине-зеленый к синему
        k = (t - 0.33) / 0.33
        h = lerp(180.0, 240.0, k)
        s = lerp(0.8, 1.0, k)
        v = 1.0
    else:
        # Синий к фиолетово-розовому
        k = (t - 0.66) / 0.34
        h = lerp(240.0, 300.0, k)
        s = lerp(1.0, 0.9, k)
        v = lerp(1.0, 0.9, k)
    return h, s, v

def hue_galaxy_from_t(t: float) -> Tuple[float, float, float]:
    """Галактическая палитра: черный -> фиолетовый -> синий -> белый"""
    t = clamp01(t)
    if t < 0.25:
        # Черный к темно-фиолетовому
        k = t / 0.25
        h = 270.0
        s = 1.0
        v = lerp(0.05, 0.3, k)
    elif t < 0.5:
        # Темно-фиолетовый к фиолетовому
        k = (t - 0.25) / 0.25
        h = lerp(270.0, 250.0, k)
        s = 1.0
        v = lerp(0.3, 0.6, k)
    elif t < 0.75:
        # Фиолетовый к синему
        k = (t - 0.5) / 0.25
        h = lerp(250.0, 220.0, k)
        s = lerp(1.0, 0.7, k)
        v = lerp(0.6, 0.9, k)
    else:
        # Синий к белому
        k = (t - 0.75) / 0.25
        h = 220.0
        s = lerp(0.7, 0.0, k)
        v = lerp(0.9, 1.0, k)
    return h, s, v

def hue_tropical_from_t(t: float) -> Tuple[float, float, float]:
    """Тропическая палитра: темно-зеленый -> зеленый -> желто-зеленый -> желтый"""
    t = clamp01(t)
    if t < 0.33:
        # Темно-зеленый к зеленому
        k = t / 0.33
        h = 140.0
        s = 1.0
        v = lerp(0.4, 0.8, k)
    elif t < 0.66:
        # Зеленый к ярко-зеленому
        k = (t - 0.33) / 0.33
        h = lerp(140.0, 120.0, k)
        s = 1.0
        v = lerp(0.8, 1.0, k)
    else:
        # Ярко-зеленый к желтому
        k = (t - 0.66) / 0.34
        h = lerp(120.0, 80.0, k)
        s = lerp(1.0, 0.8, k)
        v = 1.0
    return h, s, v

def hue_volcano_from_t(t: float) -> Tuple[float, float, float]:
    """Вулканическая палитра: черный -> красный -> оранжевый -> желтый -> белый"""
    t = clamp01(t)
    if t < 0.2:
        # Черный к темно-красному
        k = t / 0.2
        h = 0.0
        s = 1.0
        v = lerp(0.05, 0.3, k)
    elif t < 0.4:
        # Темно-красный к красному
        k = (t - 0.2) / 0.2
        h = 0.0
        s = 1.0
        v = lerp(0.3, 0.8, k)
    elif t < 0.6:
        # Красный к оранжевому
        k = (t - 0.4) / 0.2
        h = lerp(0.0, 30.0, k)
        s = 1.0
        v = lerp(0.8, 1.0, k)
    elif t < 0.8:
        # Оранжевый к желтому
        k = (t - 0.6) / 0.2
        h = lerp(30.0, 60.0, k)
        s = lerp(1.0, 0.8, k)
        v = 1.0
    else:
        # Желтый к белому
        k = (t - 0.8) / 0.2
        h = 60.0
        s = lerp(0.8, 0.0, k)
        v = 1.0
    return h, s, v

def hue_deepsea_from_t(t: float) -> Tuple[float, float, float]:
    """Глубоководная палитра: черный -> темно-синий -> синий -> сине-зеленый"""
    t = clamp01(t)
    if t < 0.33:
        # Черный к темно-синему
        k = t / 0.33
        h = 240.0
        s = 1.0
        v = lerp(0.05, 0.4, k)
    elif t < 0.66:
        # Темно-синий к синему
        k = (t - 0.33) / 0.33
        h = lerp(240.0, 220.0, k)
        s = 1.0
        v = lerp(0.4, 0.8, k)
    else:
        # Синий к сине-зеленому
        k = (t - 0.66) / 0.34
        h = lerp(220.0, 180.0, k)
        s = lerp(1.0, 0.8, k)
        v = lerp(0.8, 1.0, k)
    return h, s, v

def hue_cyberpunk_from_t(t: float) -> Tuple[float, float, float]:
    """Киберпанк палитра: фиолетовый -> розовый -> неоновый синий -> неоновый зеленый"""
    t = clamp01(t)
    if t < 0.25:
        # Темно-фиолетовый к фиолетовому
        k = t / 0.25
        h = 280.0
        s = 1.0
        v = lerp(0.4, 0.8, k)
    elif t < 0.5:
        # Фиолетовый к розовому
        k = (t - 0.25) / 0.25
        h = lerp(280.0, 320.0, k)
        s = 1.0
        v = lerp(0.8, 1.0, k)
    elif t < 0.75:
        # Розовый к неоновому синему
        k = (t - 0.5) / 0.25
        h = lerp(320.0, 200.0, k)
        s = 1.0
        v = 1.0
    else:
        # Неоновый синий к неоновому зеленому
        k = (t - 0.75) / 0.25
        h = lerp(200.0, 120.0, k)
        s = 1.0
        v = 1.0
    return h, s, v

# ==================== УПРАВЛЕНИЕ ПАЛИТРАМИ ====================

class PaletteState:
    """Состояние палитры с настройками"""
    
    def __init__(self):
        self.hue_offset = 0.0
        self.invert = False
        self.rms_palette_choice = "Blue->Green->Yellow->Red"
        self.age_palette_choice = "Blue->Green->Yellow->Red"

    def randomize(self):
        """Случайные настройки палитры"""
        self.hue_offset = random.uniform(0, 360)
        self.invert = random.random() < 0.5
        palette_list = [
            "Blue->Red", "Blue->Green->Yellow->Red", "White->LightGray->Gray->DarkGray", 
            "BrightRed->DarkRed->DarkGray->Black", "Fire", "Ocean", "Neon", "Ukraine",
            "Rainbow", "Sunset", "Pastel", "Viridis", "Inferno", "Magma", "Plasma", 
            "Cividis", "Twilight", "Spring", "Summer", "Autumn", "Winter",
            "Ice", "Forest", "Desert", "Candy", "Retro", "Cyberpunk", "Gold", "Silver", 
            "Copper", "Emerald", "Sapphire", "Ruby", "Amethyst",
            "Lime", "Mint", "Peach", "Lavender", "Rose", "Sky", "Sand", "Charcoal", 
            "Steel", "Bronze", "Pearl", "Coral", "Jade", "Topaz",
            "Galaxy", "Aurora", "Tropical", "Vintage", "Monochrome", "Sepia", 
            "HighContrast", "LowContrast", "DeepSea", "Volcano", "Clouds", "Flame"
        ]
        self.rms_palette_choice = random.choice(palette_list)
        self.age_palette_choice = random.choice(palette_list)

    def to_dict(self) -> Dict[str, Any]:
        """Сохранение в словарь"""
        return {
            "hue_offset": float(self.hue_offset),
            "invert": bool(self.invert),
            "rms_palette_choice": str(self.rms_palette_choice),
            "age_palette_choice": str(self.age_palette_choice),
        }

    def from_dict(self, d: dict):
        """Загрузка из словаря"""
        self.hue_offset = float(d.get("hue_offset", 0.0))
        self.invert = bool(d.get("invert", False))
        self.rms_palette_choice = str(d.get("rms_palette_choice", "Blue->Green->Yellow->Red")).replace("→","->")
        self.age_palette_choice = str(d.get("age_palette_choice", "Blue->Green->Yellow->Red")).replace("→","->")

# Глобальное состояние палитры
PALETTE_STATE = PaletteState()

# Алиасы палитр для обратной совместимости
_PALETTE_ALIASES = {
    # Базовые палитры
    "Blue->Green->Yellow->Red": "BGYR",
    "White->LightGray->Gray->DarkGray": "GRAYSCALE",
    "BrightRed->DarkRed->DarkGray->Black": "RED_DARKRED_GRAY_BLACK",
    "Red->DarkRed->Gray->Black": "RED_DARKRED_GRAY_BLACK",
    "BGYR": "BGYR", 
    "GrayScale": "GRAYSCALE",
    
    # HSV дизайн палитры (новые)
    "Blue->Red": "BGYR",  # Временно используем BGYR
    "Rainbow": "RAINBOWSMOOTH",
    "RainbowSmooth": "RAINBOWSMOOTH",
    "Sunset": "SUNSET",
    "Aurora": "AURORA", 
    "Ocean": "OCEAN",
    "Fire": "FIRE",
    "Galaxy": "GALAXY",
    "Tropical": "TROPICAL",
    "Volcano": "VOLCANO",
    "DeepSea": "DEEPSEA",
    "Spring": "SPRING",
    "Summer": "SUMMER",
    "Autumn": "AUTUMN",
    "Winter": "WINTER",
    "Ice": "ICE",
    "Forest": "FOREST",
    "Desert": "DESERT",
    "Viridis": "VIRIDIS",
    "Inferno": "INFERNO",
    "Magma": "MAGMA",
    "Plasma": "PLASMA",
    "Cividis": "CIVIDIS",
    "Twilight": "TWILIGHT",
    "Gold": "GOLD",
    "Silver": "SILVER",
    "Copper": "COPPER",
    "Emerald": "EMERALD",
    "Sapphire": "SAPPHIRE",
    "Ruby": "RUBY",
    "Amethyst": "AMETHYST",
    "Steel": "STEEL",
    "Bronze": "BRONZE",
    "Pearl": "PEARL",
    "Coral": "CORAL",
    "Jade": "JADE",
    "Topaz": "TOPAZ",
    "Ukraine": "UKRAINE",
    "Neon": "NEON",
    "Cyberpunk": "CYBERPUNK",
    "Sepia": "SEPIA",
    "Monochrome": "GRAYSCALE",
}

# Функции палитр
PALETTE_FUNCTIONS = {
    "FIRE": hue_fire_from_t,
    "OCEAN": hue_ocean_from_t,
    "NEON": hue_neon_from_t,
    "UKRAINE": hue_ukraine_from_t,
    "SPRING": hue_spring_from_t,
    "SUMMER": hue_summer_from_t,
    "AUTUMN": hue_autumn_from_t,
    "WINTER": hue_winter_from_t,
    "ICE": hue_ice_from_t,
    "FOREST": hue_forest_from_t,
    "DESERT": hue_desert_from_t,
    "VIRIDIS": hue_viridis_from_t,
    "INFERNO": hue_inferno_from_t,
    "MAGMA": hue_magma_from_t,
    "PLASMA": hue_plasma_from_t,
    "CIVIDIS": hue_cividis_from_t,
    "TWILIGHT": hue_twilight_from_t,
    "RAINBOWSMOOTH": hue_rainbow_smooth_from_t,
    "SUNSET": hue_sunset_from_t,
    "AURORA": hue_aurora_from_t,
    "GALAXY": hue_galaxy_from_t,
    "TROPICAL": hue_tropical_from_t,
    "VOLCANO": hue_volcano_from_t,
    "DEEPSEA": hue_deepsea_from_t,
    "CYBERPUNK": hue_cyberpunk_from_t,
    "GOLD": hue_gold_from_t,
    "SILVER": hue_silver_from_t,
    "COPPER": hue_copper_from_t,
    "EMERALD": hue_emerald_from_t,
    "SAPPHIRE": hue_sapphire_from_t,
    "RUBY": hue_ruby_from_t,
    "AMETHYST": hue_amethyst_from_t,
    "BRONZE": hue_bronze_from_t,
    "PEARL": hue_pearl_from_t,
    "CORAL": hue_coral_from_t,
    "JADE": hue_jade_from_t,
    "TOPAZ": hue_topaz_from_t,
    "GRAYSCALE": hue_grayscale_from_t,
    "RED_DARKRED_GRAY_BLACK": hue_red_darkred_gray_black_from_t,
    "SEPIA": hue_sepia_from_t,
}

@lru_cache(maxsize=256)
def _cached_palette_hsv(palette_name: str, t: float) -> tuple[float, float, float]:
    """Кэшированная генерация HSV для палитр"""
    t = clamp01(t)
    alias = _PALETTE_ALIASES.get(palette_name, palette_name.upper())
    
    if alias in PALETTE_FUNCTIONS:
        return PALETTE_FUNCTIONS[alias](t)
    elif alias == "BGYR":
        # Blue->Green->Yellow->Red
        hue = hue_bgyr_from_t(t)
        return (hue, 1.0, 1.0)
    else:
        # Default fallback
        return (hue_bgyr_from_t(t), 1.0, 1.0)

def palette_key(name: str) -> str:
    """Получить ключ палитры"""
    return _PALETTE_ALIASES.get(name, name.upper())

def apply_hue_offset(hue_deg: float) -> float:
    """Применить смещение оттенка"""
    return (hue_deg + PALETTE_STATE.hue_offset) % 360.0

def maybe_invert_t(t: float) -> float:
    """Возможно инвертировать t"""
    return (1.0 - t) if PALETTE_STATE.invert else t

def max_age_slider_to_value(slider_percent: float) -> int:
    """
    Преобразует позицию слайдера (0-100%) в логарифмическое значение max_age.
    Первая половина слайдера (0-50%) покрывает диапазон 10-70.
    Вторая половина слайдера (50-100%) покрывает диапазон 70-500.
    """
    slider_percent = max(0.0, min(100.0, slider_percent))
    
    if slider_percent <= 50.0:
        # Первая половина: линейно от 10 до 70
        normalized = slider_percent / 50.0
        return int(10 + normalized * 60)
    else:
        # Вторая половина: логарифмически от 70 до 500
        normalized = (slider_percent - 50.0) / 50.0
        # Логарифмическая шкала: log(1 + normalized * (e^k - 1)) / k
        k = 2.0  # Коэффициент логарифмичности
        log_value = math.log(1 + normalized * (math.exp(k) - 1)) / k
        return int(70 + log_value * 430)

def max_age_value_to_slider(max_age: int) -> float:
    """
    Преобразует значение max_age обратно в позицию слайдера (0-100%).
    """
    max_age = max(10, min(500, max_age))
    
    if max_age <= 70:
        # Первая половина: линейно от 10 до 70
        normalized = (max_age - 10) / 60.0
        return normalized * 50.0
    else:
        # Вторая половина: обратная логарифмическая
        k = 2.0
        normalized_value = (max_age - 70) / 430.0
        # Обратная формула: (exp(k * normalized_value) - 1) / (exp(k) - 1)
        log_normalized = (math.exp(k * normalized_value) - 1) / (math.exp(k) - 1)
        return 50.0 + log_normalized * 50.0

def age_to_t(age: int, max_age: int) -> float:
    """Преобразует возраст в параметр t для палитры"""
    if max_age <= 1:
        return 1.0
    k = max(6.0, max_age / 6.0)
    return clamp01(1.0 - math.exp(-age / k))
