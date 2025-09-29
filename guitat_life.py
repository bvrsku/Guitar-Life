#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Guitar-driven Cellular Automaton — v13 (Ultimate)
-------------------------------------------------
Major improvements over v12:
- GUI: Added "Modifiers" tab (post-processing effects) and "Runtime" (live control and presets).
- HUD: Compact mode [H], mini-HUD with [Tab] hold. Show/toggle options.
- Layers: solo/mute, blend mode (Normal/Additive), separate alpha for "live" and "old" cells.
- Soft-Clear: Fixed coefficients; two strategies - Kill and Fade with adjustable rates.
- Спавн: адаптивное распределение по слоям (разреженность+правило) + целочисленное округление методом наибольших остатков.
- Палитры: Fire/Ocean/Neon/Ukraine, инверсия, Hue offset.
- Пост‑эффекты (включаемые/выключаемые): Trails, Blur (scale‑blur), Bloom, Posterize, Dither, Scanlines, Pixelate, Outline.
- Пресеты: сохранение/загрузка полного runtime‑состояния из JSON.
- Хоткеи: см. раздел ниже в HUD. Отдельный хоткей «Joy Division» ([F3]) — монохром+сканлайны+постеризация.

Зависимости: numpy, pygame, sounddevice, librosa (необяз.)
  pip install numpy pygame sounddevice librosa

Примечание: структура кода спроектирована как эволюция v12.
"""







# === IMPORTS ===
from __future__ import annotations

# Стандартные библиотеки
import colorsys
import json
import math
import os
import queue
import random
import sys
import time
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional, Tuple

# Основные внешние зависимости
try:
    import numpy as np
except ImportError as e:
    raise SystemExit("NumPy is required. Install with: pip install numpy") from e

try:
    import pygame
except ImportError as e:
    raise SystemExit("pygame is required. Install with: pip install pygame") from e

# Дополнительные внешние зависимости (необязательные)
try:
    import sounddevice as sd
except ImportError:
    sd = None

try:
    import librosa  # type: ignore
except ImportError:
    librosa = None

try:
    import tkinter as tk
    from tkinter import ttk, filedialog
except ImportError:
    tk = None
    ttk = None 
    filedialog = None

# === CONSTANTS AND CONFIGURATION ===

# Audio settings
SAMPLE_RATE = 44100
BLOCK_SIZE = 2048
CHANNELS = 1
FPS = 60

# Grid and display settings
GRID_W, GRID_H = 120, 70
CELL_SIZE = 8
BG_COLOR = (10, 10, 12)
HUD_WIDTH = 520
FIELD_OFFSET_X = 0

# Cellular automaton rules
CA_RULES = [
    "Conway", "HighLife", "Day&Night", "Replicator", 
    "Seeds", "Maze", "Coral", "LifeWithoutDeath", "Gnarl"
]

# Available color palettes
PALETTE_OPTIONS = [
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

# Audio processing settings
SPAWN_BASE, SPAWN_SCALE = 1, 400  # Уменьшено для меньшего количества клеток
FREQ_MIN, FREQ_MAX = 70.0, 1500.0
MIN_NOTE_FREQ = 60.0
VOLUME_SCALE = 8.0  # Уменьшено для более мягкой реакции на звук

# Default timing and threshold values
DEFAULT_CLEAR_RMS = 0.004
DEFAULT_COLOR_RMS_MIN = 0.004
DEFAULT_COLOR_RMS_MAX = 0.30
DEFAULT_TICK_MS = 120
DEFAULT_PTICK_MIN_MS = 60
DEFAULT_PTICK_MAX_MS = 200

# Pitch-based coloring
PITCH_COLOR_MIN_HZ = 72.0
PITCH_COLOR_MAX_HZ = 1500.0

# File paths
PRESET_PATH = os.path.join(os.path.dirname(__file__) if "__file__" in globals() else ".", "runtime_state.json")
PALETTE_PATH = os.path.join(os.path.dirname(__file__) if "__file__" in globals() else ".", "palette_preset.json")

# -------------------- Темная современная цветовая схема для GUI --------------------
class SimpleColors:
    """Темная современная цветовая палитра для GUI"""
    # Основные цвета (темная тема)
    BACKGROUND = (15, 23, 42)             # Темно-синий фон
    SURFACE = (30, 41, 59)                # Темно-серые поверхности
    SURFACE_VARIANT = (51, 65, 85)        # Серо-синий вариант
    
    # Акцентные цвета (яркие для темной темы)
    PRIMARY = (96, 165, 250)              # Яркий синий основной
    PRIMARY_LIGHT = (147, 197, 253)       # Светло-синий
    SECONDARY = (52, 211, 153)            # Яркий зеленый вторичный
    
    # Нейтральные цвета (инвертированы для темной темы)
    GRAY_50 = (71, 85, 105)
    GRAY_100 = (100, 116, 139)
    GRAY_200 = (148, 163, 184)
    GRAY_300 = (203, 213, 225)
    GRAY_400 = (148, 163, 184)
    GRAY_500 = (100, 116, 139)
    GRAY_600 = (71, 85, 105)
    GRAY_700 = (51, 65, 85)
    GRAY_800 = (30, 41, 59)
    GRAY_900 = (15, 23, 42)
    
    # Текст (светлый для темной темы)
    TEXT_PRIMARY = (248, 250, 252)        # Белый текст
    TEXT_SECONDARY = (203, 213, 225)      # Светло-серый текст
    TEXT_DISABLED = (100, 116, 139)       # Отключенный текст
    
    # Границы (более видимые в темной теме)
    BORDER = (71, 85, 105)                # Темно-серые границы
    BORDER_FOCUS = (96, 165, 250)         # Синие границы при фокусе
    
    # Состояния (яркие цвета для темной темы)
    SUCCESS = (52, 211, 153)              # Яркий зеленый
    WARNING = (251, 191, 36)              # Яркий оранжевый  
    ERROR = (248, 113, 113)               # Яркий красный
    
    # Hover эффекты
    HOVER = (51, 65, 85)                  # Темно-серый при наведении
    SELECTED = (37, 99, 235)              # Синий при выборе
    ACTIVE = (30, 58, 138)                # Темно-синий при активности

pitch_queue = queue.Queue(maxsize=8)
rms_queue   = queue.Queue(maxsize=8)
running     = True
audio_gain  = 2.5  # Global variable for audio gain

# -------------------- Утилиты --------------------
def clamp01(x: float) -> float:
    return 0.0 if x < 0 else (1.0 if x > 1 else x)

def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t

# -------------------- Палитры и возраст/выцветание --------------------
def hue_bgyr_from_t(t: float) -> float:
    t = clamp01(t)
    if t < 1/3:   return lerp(220.0, 120.0, t*3.0)
    elif t < 2/3: return lerp(120.0, 60.0, (t-1/3)*3.0)
    else:         return lerp(60.0, 0.0, (t-2/3)*3.0)

def hue_br_from_t(t: float) -> float:
    return lerp(220.0, 0.0, clamp01(t))

# расширенные палитры (HSV-дизайнеры)
def hue_fire_from_t(t: float) -> Tuple[float, float, float]:
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
    t = clamp01(t)
    if t < 0.5:
        k = t/0.5; h = lerp(220.0, 200.0, k); s = 1.0; v = lerp(0.35, 0.85, k)
    else:
        k = (t-0.5)/0.5; h = lerp(200.0, 180.0, k); s = lerp(1.0, 0.2, k); v = lerp(0.85, 1.0, k)
    return h, s, v

def hue_neon_from_t(t: float) -> Tuple[float, float, float]:
    t = clamp01(t)
    if t < 1/3:      h = lerp(285.0, 240.0, t*3.0)
    elif t < 2/3:    h = lerp(240.0, 120.0, (t-1/3)*3.0)
    else:            h = lerp(120.0, 315.0, (t-2/3)*3.0)
    s = 1.0; v = 1.0
    return h, s, v

def hue_ukraine_from_t(t: float) -> Tuple[float, float, float]:
    t = clamp01(t)
    if t < 0.5:
        k = t/0.5; h = 50.0; s = lerp(1.0, 0.6, k); v = lerp(0.95, 1.0, k)
    else:
        k = (t-0.5)/0.5; h = lerp(50.0, 220.0, k); s = lerp(0.6, 1.0, k); v = lerp(1.0, 0.9, k)
    return h, s, v

class PaletteState:
    def __init__(self):
        self.hue_offset = 0.0
        self.invert = False
        self.rms_palette_choice = "Blue->Green->Yellow->Red"
        self.age_palette_choice = "Blue->Green->Yellow->Red"

    def randomize(self):
        self.hue_offset = random.uniform(-180.0, 180.0)
        self.invert = random.random() < 0.5
        palette_list = [
            "Blue->Red", "Blue->Green->Yellow->Red", "White->LightGray->Gray->DarkGray", "BrightRed->DarkRed->DarkGray->Black", "Fire", "Ocean", "Neon", "Ukraine",
            "Rainbow", "Sunset", "Pastel", "Viridis", "Inferno", "Magma", "Plasma", "Cividis", "Twilight", "Spring", "Summer", "Autumn", "Winter",
            "Ice", "Forest", "Desert", "Candy", "Retro", "Cyberpunk", "Gold", "Silver", "Copper", "Emerald", "Sapphire", "Ruby", "Amethyst",
            "Lime", "Mint", "Peach", "Lavender", "Rose", "Sky", "Sand", "Charcoal", "Steel", "Bronze", "Pearl", "Coral", "Jade", "Topaz",
            "Galaxy", "Aurora", "Tropical", "Vintage", "Monochrome", "Sepia", "HighContrast", "LowContrast", "DeepSea", "Volcano", "Clouds", "Flame"
        ]
        self.rms_palette_choice = random.choice(palette_list)
        self.age_palette_choice = random.choice(palette_list)

    def to_dict(self):
        return {
            "hue_offset": float(self.hue_offset),
            "invert": bool(self.invert),
            "rms_palette_choice": str(self.rms_palette_choice),
            "age_palette_choice": str(self.age_palette_choice),
        }

    def from_dict(self, d: dict):
        self.hue_offset = float(d.get("hue_offset", 0.0))
        self.invert = bool(d.get("invert", False))
        self.rms_palette_choice = str(d.get("rms_palette_choice", "Blue->Green->Yellow->Red")).replace("→","->")
        self.age_palette_choice = str(d.get("age_palette_choice", "Blue->Green->Yellow->Red")).replace("→","->")

PALETTE_STATE = PaletteState()

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
    "Spring": "FIRE",      # Временно используем похожие палитры
    "Summer": "SUNSET",
    "Autumn": "VOLCANO",
    "Winter": "OCEAN",
    "Ice": "OCEAN",
    "Forest": "TROPICAL",
    "Desert": "SUNSET",
    "Viridis": "OCEAN",    # Научные палитры временно
    "Inferno": "FIRE",
    "Magma": "VOLCANO",
    "Plasma": "NEON",
    "Cividis": "OCEAN",
    "Twilight": "AURORA",
    
    # Базовые названия
    "Neon": "NEON",
    "Ukraine": "UKRAINE",
    "Cyberpunk": "CYBERPUNK",
    
    # HSV цветовые палитры
    "Monochrome": "GRAYSCALE",
    "Sepia": "GRAYSCALE",
    "HighContrast": "RED_DARKRED_GRAY_BLACK",
    "LowContrast": "GRAYSCALE",
}

_PALETTE_OPTIONS = [
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

def palette_key(name: str) -> str:
    n = (name or "").replace("→","->").strip()
    return _PALETTE_ALIASES.get(n, "BGYR")

def apply_hue_offset(hue_deg: float) -> float:
    return (hue_deg + PALETTE_STATE.hue_offset) % 360.0

def maybe_invert_t(t: float) -> float:
    return 1.0 - t if PALETTE_STATE.invert else t

# возраст/выцветание

def age_to_t(age: int, max_age: int) -> float:
    if max_age <= 1:
        return 1.0
    k = max(6.0, max_age/6.0)
    return clamp01(1.0 - math.exp(-age / k))

def fade_factors(age: int, fade_start: int, max_age: int,
                 sat_drop_pct: float, val_drop_pct: float) -> tuple[float,float]:
    if max_age <= 0:
        return 1.0, 1.0
    a = max(0, min(age, max_age))
    if a <= fade_start or fade_start >= max_age:
        return 1.0, 1.0
    t = (a - fade_start) / float(max(1, max_age - fade_start))
    sat_mul = 1.0 - clamp01(sat_drop_pct/100.0) * t
    val_mul = 1.0 - clamp01(val_drop_pct/100.0) * t
    return clamp01(sat_mul), clamp01(val_mul)

def norm_rms_for_color(rms: float, color_rms_min: float, color_rms_max: float) -> float:
    if color_rms_max <= color_rms_min:
        color_rms_max = color_rms_min + 1e-6
    return clamp01((rms - color_rms_min) / (color_rms_max - color_rms_min))

# -------------------- Цветовые функции --------------------

def _rgb_from_hsv(h: float, s: float, v: float) -> Tuple[int,int,int]:
    r, g, b = colorsys.hsv_to_rgb((h%360)/360.0, clamp01(s), clamp01(v))
    return (int(r*255), int(g*255), int(b*255))


def color_from_age_rms(age: int, rms: float, rms_strength: float,
                       fade_start: int, max_age: int,
                       sat_drop_pct: float, val_drop_pct: float,
                       color_rms_min: float, color_rms_max: float,
                       global_v_mul: float,
                       age_palette: str, rms_palette: str, rms_mode: str = "brightness") -> Tuple[int,int,int]:
    a = min(age, max_age if max_age>0 else age)
    t_age_raw = age_to_t(a, max_age if max_age>0 else max(12, a+1))
    t_age = maybe_invert_t(t_age_raw)

    t_rms = norm_rms_for_color(rms, color_rms_min, color_rms_max)
    strength = clamp01(rms_strength)

    # В режиме "palette" смешиваем цвета из age_palette и rms_palette
    if rms_mode == "palette":
        # Получаем цвет от возраста (без RMS модификации)
        age_color = color_from_rms(0.5, age_palette, color_rms_min, color_rms_max, global_v_mul)
        # Получаем цвет от RMS
        rms_color = color_from_rms(rms, rms_palette, color_rms_min, color_rms_max, global_v_mul)
        
        # Смешиваем цвета на основе силы RMS
        mix_factor = clamp01(t_rms * strength)
        
        # Линейная интерполяция RGB
        final_color = (
            int(lerp(age_color[0], rms_color[0], mix_factor)),
            int(lerp(age_color[1], rms_color[1], mix_factor)),
            int(lerp(age_color[2], rms_color[2], mix_factor))
        )
        
        # Применяем fade factors
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        # Простое затемнение для fade эффекта
        final_color = (
            int(final_color[0] * val_mul),
            int(final_color[1] * val_mul),
            int(final_color[2] * val_mul)
        )
        
        return final_color

    # Получаем базовый цвет из age_palette (режим "brightness")
    pal = palette_key(age_palette)
    
    # Получаем базовый цвет от возраста
    base_color = None

    if pal == "GRAYSCALE":
        if t_age < 1/3:      v_age = lerp(1.0, 0.8, t_age*3.0)
        elif t_age < 2/3:    v_age = lerp(0.8, 0.5, (t_age-1/3)*3.0)
        else:                v_age = lerp(0.5, 0.25, (t_age-2/3)*3.0)
        v = v_age * (0.65 + 0.35 * (t_rms * strength)) * clamp01(global_v_mul)
        _, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        v *= val_mul
        g = int(255*clamp01(v))
        base_color = (g,g,g)

    elif pal == "RED_DARKRED_GRAY_BLACK":
        if t_age < 1/3:
            s = 1.0; v_age = lerp(1.0, 0.65, t_age*3.0); hue_deg = 0.0
        elif t_age < 2/3:
            k = (t_age-1/3)*3.0; s = lerp(1.0, 0.0, k); v_age = lerp(0.65, 0.25, k); hue_deg = 0.0
        else:
            k = (t_age-2/3)*3.0; s = 0.0; v_age = lerp(0.25, 0.0, k); hue_deg = 0.0
        v = v_age * (0.65 + 0.35 * (t_rms * strength)) * clamp01(global_v_mul)
        hue_deg = apply_hue_offset(hue_deg)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        base_color = _rgb_from_hsv(hue_deg, s*sat_mul, v*val_mul)

    elif pal == "FIRE":
        h,s,v = hue_fire_from_t(t_age); h = apply_hue_offset(h)
        v *= (0.65 + 0.35 * (t_rms * strength)) * clamp01(global_v_mul)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        base_color = _rgb_from_hsv(h, s*sat_mul, v*val_mul)

    elif pal == "OCEAN":
        h,s,v = hue_ocean_from_t(t_age); h = apply_hue_offset(h)
        v *= (0.65 + 0.35 * (t_rms * strength)) * clamp01(global_v_mul)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        base_color = _rgb_from_hsv(h, s*sat_mul, v*val_mul)

    elif pal == "NEON":
        h,s,v = hue_neon_from_t(t_age); h = apply_hue_offset(h)
        v *= (0.65 + 0.35 * (t_rms * strength)) * clamp01(global_v_mul)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        base_color = _rgb_from_hsv(h, s*sat_mul, v*val_mul)

    elif pal == "UKRAINE":
        h,s,v = hue_ukraine_from_t(t_age); h = apply_hue_offset(h)
        v *= (0.65 + 0.35 * (t_rms * strength)) * clamp01(global_v_mul)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        base_color = _rgb_from_hsv(h, s*sat_mul, v*val_mul)

    elif pal == "BGYR":
        hue_deg = hue_bgyr_from_t(t_age)
        hue_deg = apply_hue_offset(hue_deg)
        v = (0.65 + 0.35 * (t_rms * strength)) * clamp01(global_v_mul)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        base_color = _rgb_from_hsv(hue_deg, 0.85*sat_mul, v*val_mul)
    
    else:
        # Fallback
        base_color = (128, 128, 128)
    
    # Теперь получаем цвет RMS влияния
    rms_color = color_from_rms(rms, rms_palette, color_rms_min, color_rms_max, global_v_mul)
    
    # Смешиваем цвета: базовый цвет от возраста с влиянием RMS
    # strength определяет, насколько сильно RMS влияет на итоговый цвет
    mix_factor = strength * 0.4  # ограничиваем влияние RMS чтобы возраст оставался доминирующим
    
    final_r = int(base_color[0] * (1 - mix_factor) + rms_color[0] * mix_factor)
    final_g = int(base_color[1] * (1 - mix_factor) + rms_color[1] * mix_factor)
    final_b = int(base_color[2] * (1 - mix_factor) + rms_color[2] * mix_factor)
    
    # Ограничиваем значения 0-255
    final_r = max(0, min(255, final_r))
    final_g = max(0, min(255, final_g))
    final_b = max(0, min(255, final_b))
    
    return (final_r, final_g, final_b)


def color_from_pitch(freq_hz: float, rms: float, rms_strength: float,
                     global_v_mul: float) -> Tuple[int,int,int]:
    try: f = float(freq_hz)
    except Exception: f = 0.0
    if not (f > 0.0):
        v = 0.25 * clamp01(global_v_mul)
        g = int(200*v)
        return (g,g,g)
    f = max(PITCH_COLOR_MIN_HZ, min(PITCH_COLOR_MAX_HZ, f))
    midi = 69.0 + 12.0 * math.log2(f / 440.0)
    hue_deg = ((midi % 12.0) / 12.0) * 360.0
    hue_deg = apply_hue_offset(hue_deg)
    t_rms = norm_rms_for_color(rms, DEFAULT_COLOR_RMS_MIN, DEFAULT_COLOR_RMS_MAX)
    v = (0.40 + 0.60 * (t_rms * clamp01(rms_strength))) * clamp01(global_v_mul)
    return _rgb_from_hsv(hue_deg, 0.9, v)


def color_from_rms(rms: float, palette: str,
                   color_rms_min: float, color_rms_max: float,
                   global_v_mul: float) -> Tuple[int,int,int]:
    palette_norm = palette_key(palette)
    t = maybe_invert_t(norm_rms_for_color(rms, color_rms_min, color_rms_max))

    if palette_norm == "BGYR":
        hue_deg = hue_bgyr_from_t(t)
        hue_deg = apply_hue_offset(hue_deg)
        return _rgb_from_hsv(hue_deg, 0.85, clamp01(global_v_mul))

    elif palette_norm == "GRAYSCALE":
        if t < 1/3: v = lerp(1.0, 0.8, t*3.0)
        elif t < 2/3: v = lerp(0.8, 0.5, (t-1/3)*3.0)
        else: v = lerp(0.5, 0.25, (t-2/3)*3.0)
        v *= clamp01(global_v_mul)
        g = int(255*clamp01(v)); return (g,g,g)

    elif palette_norm == "RED_DARKRED_GRAY_BLACK":
        if t < 1/3: s = 1.0; v = lerp(1.0, 0.65, t*3.0)
        elif t < 2/3:
            k = (t-1/3)*3.0; s = lerp(1.0, 0.0, k); v = lerp(0.65, 0.25, k)
        else:
            k = (t-2/3)*3.0; s = 0.0; v = lerp(0.25, 0.0, k)
        hue_deg = apply_hue_offset(0.0)
        return _rgb_from_hsv(hue_deg, s, v*clamp01(global_v_mul))

    elif palette_norm == "FIRE":
        h,s,v = hue_fire_from_t(t); h = apply_hue_offset(h)
        return _rgb_from_hsv(h, s, v*clamp01(global_v_mul))

    elif palette_norm == "OCEAN":
        h,s,v = hue_ocean_from_t(t); h = apply_hue_offset(h)
        return _rgb_from_hsv(h, s, v*clamp01(global_v_mul))

    elif palette_norm == "NEON":
        h,s,v = hue_neon_from_t(t); h = apply_hue_offset(h)
        return _rgb_from_hsv(h, s, v*clamp01(global_v_mul))

    elif palette_norm == "UKRAINE":
        h,s,v = hue_ukraine_from_t(t); h = apply_hue_offset(h)
        return _rgb_from_hsv(h, s, v*clamp01(global_v_mul))

    else:
        hue_deg = hue_br_from_t(t)
        hue_deg = apply_hue_offset(hue_deg)
        return _rgb_from_hsv(hue_deg, 0.85, clamp01(global_v_mul))

# -------------------- GUI (Notebook с доп. вкладками) --------------------

def choose_settings() -> Optional[dict]:
    """Запускает современный GUI для настройки приложения"""
    if tk is None or ttk is None:
        raise SystemExit("Tkinter недоступен — GUI отключён.")
    if sd is None:
        raise SystemExit("sounddevice недоступен — нет аудио-входа.")

    devices = sd.query_devices()
    input_devices = [{'name': d['name'], 'index': i} for i, d in enumerate(devices) if d['max_input_channels'] > 0]
    
    # Импортируем модуль с современным GUI
    try:
        from backups.modern_gui import show_modern_gui
        result = show_modern_gui(input_devices)
        
        # Преобразуем результат к ожидаемому формату
        if result:
            # Найдем индекс устройства по имени
            device_index = 0
            for i, device in enumerate(input_devices):
                if device['name'] == result.get('device', ''):
                    device_index = i
                    break
            
            # Конвертируем настройки слоев из нового редактора
            layers_cfg = []
            layer_count = result.get('layer_count', 3)
            
            # Если в результате есть готовая конфигурация слоев, используем её
            if 'layers_cfg' in result and result['layers_cfg']:
                layers_cfg = result['layers_cfg']
            else:
                # Иначе генерируем на основе старых настроек для совместимости
                diff_per_layer = result.get('diff_per_layer', True)
                base_rule = result.get('rule', 'Conway')
                base_age_palette = result.get('age_palette', 'Blue->Green->Yellow->Red')
                base_palette = result.get('palette', 'Blue->Green->Yellow->Red')
                
                rules_all = ["Conway", "HighLife", "Day&Night", "Replicator", "Seeds", "Maze", "Coral", "LifeWithoutDeath", "Gnarl"]
                age_palettes = [
                    "Blue->Green->Yellow->Red", "White->LightGray->Gray->DarkGray", "BrightRed->DarkRed->DarkGray->Black", "Fire", "Ocean", "Neon", "Ukraine",
                    "Rainbow", "Sunset", "Pastel", "Viridis", "Inferno", "Magma", "Plasma", "Cividis", "Twilight", "Spring", "Summer", "Autumn", "Winter",
                    "Ice", "Forest", "Desert", "Candy", "Retro", "Cyberpunk", "Gold", "Silver", "Copper", "Emerald", "Sapphire", "Ruby", "Amethyst",
                    "Lime", "Mint", "Peach", "Lavender", "Rose", "Sky", "Sand", "Charcoal", "Steel", "Bronze", "Pearl", "Coral", "Jade", "Topaz",
                    "Galaxy", "Aurora", "Tropical", "Vintage", "Monochrome", "Sepia", "HighContrast", "LowContrast", "DeepSea", "Volcano", "Clouds", "Flame"
                ]
                palettes = [
                    "Blue->Red", "Blue->Green->Yellow->Red", "White->LightGray->Gray->DarkGray", "BrightRed->DarkRed->DarkGray->Black", "Fire", "Ocean", "Neon", "Ukraine",
                    "Rainbow", "Sunset", "Pastel", "Viridis", "Inferno", "Magma", "Plasma", "Cividis", "Twilight", "Spring", "Summer", "Autumn", "Winter",
                    "Ice", "Forest", "Desert", "Candy", "Retro", "Cyberpunk", "Gold", "Silver", "Copper", "Emerald", "Sapphire", "Ruby", "Amethyst",
                    "Lime", "Mint", "Peach", "Lavender", "Rose", "Sky", "Sand", "Charcoal", "Steel", "Bronze", "Pearl", "Coral", "Jade", "Topaz",
                    "Galaxy", "Aurora", "Tropical", "Vintage", "Monochrome", "Sepia", "HighContrast", "LowContrast", "DeepSea", "Volcano", "Clouds", "Flame"
                ]
                
                if diff_per_layer:
                    for i in range(layer_count):
                        layers_cfg.append({
                            'rule': rules_all[i % len(rules_all)],
                            'color_mode': result.get('color_mode', 'Возраст + RMS'),
                            'age_palette': age_palettes[i % len(age_palettes)],
                            'rms_palette': palettes[(i+1) % len(palettes)],
                            'alpha_live': 220,
                            'alpha_old': 140,
                            'mix': 'Normal',
                            'solo': False,
                            'mute': False,
                        })
                else:
                    for i in range(layer_count):
                        layers_cfg.append({
                            'rule': base_rule,
                            'color_mode': result.get('color_mode', 'Возраст + RMS'),
                            'age_palette': base_age_palette,
                            'rms_palette': base_palette,
                            'alpha_live': 220,
                            'alpha_old': 140,
                            'mix': 'Normal',
                            'solo': False,
                            'mute': False,
                        })
            
            # Возвращаем совместимый формат
            return {
                'device': result.get('device', ''),
                'device_index': device_index,
                'rule': result.get('rule', 'Conway'),
                'palette': result.get('palette', 'Blue->Green->Yellow->Red'),
                'age_palette': result.get('age_palette', 'Blue->Green->Yellow->Red'),
                'color_mode': result.get('color_mode', 'Возраст + RMS'),
                'rms_modulation': result.get('rms_mod', True),
                'rms_strength': result.get('rms_strength', 100),
                'tick_ms': result.get('tick_ms', DEFAULT_TICK_MS),
                'pitch_to_tick': result.get('pitch_tick_enable', False),
                'pitch_tick_min_ms': result.get('pitch_tick_min_ms', DEFAULT_PTICK_MIN_MS),
                'pitch_tick_max_ms': result.get('pitch_tick_max_ms', DEFAULT_PTICK_MAX_MS),
                'max_age': result.get('max_age', 120),
                'fade_start_age': result.get('fade_start', 60),
                'fade_saturation_drop': result.get('fade_sat_drop', 70),
                'fade_value_drop': result.get('fade_val_drop', 60),
                'clear_rms_threshold': result.get('clear_rms', DEFAULT_CLEAR_RMS),
                'color_rms_min': result.get('color_rms_min', DEFAULT_COLOR_RMS_MIN),
                'color_rms_max': result.get('color_rms_max', DEFAULT_COLOR_RMS_MAX),
                'soft_clear_enable': result.get('soft_clear_enable', True),
                'soft_clear_mode': result.get('soft_mode', 'Удалять клетки'),
                'soft_kill_percentage': result.get('soft_kill_rate', 80),
                'soft_fade_floor': result.get('soft_fade_floor', 0.3),
                'soft_fade_down_percentage': result.get('soft_fade_down', 1),
                'soft_fade_up_percentage': result.get('soft_fade_up', 5),
                'layer_count': layer_count,
                'layers_different': result.get('diff_per_layer', True),
                'layers_cfg': layers_cfg,
                'auto_rule_change_sec': result.get('auto_rule_sec', 0),
                'auto_palette_change_sec': result.get('auto_palette_sec', 0),
                'mirror_x': result.get('mirror_x', False),
                'mirror_y': result.get('mirror_y', False),
                'fx': result.get('fx', {
                    'trails': True,
                    'trail_strength': 0.06,
                    'blur': False,
                    'blur_scale': 2,
                    'bloom': False,
                    'bloom_strength': 0.35,
                    'posterize': False,
                    'poster_levels': 5,
                    'dither': False,
                    'scanlines': False,
                    'scan_strength': 0.25,
                    'pixelate': False,
                    'pixel_block': 1,
                    'outline': False,
                    'outline_thick': 1,
                })
            }
        
        return None
        
    except ImportError:
        # Если по какой-то причине modern_gui недоступен, используем простую заглушку
        import tkinter
        from tkinter import messagebox
        
        root = tkinter.Tk()
        root.withdraw()
        messagebox.showerror("Ошибка", "Не удалось загрузить modern_gui.py")
        root.destroy()
        return None

# -------------------- Аудио --------------------

def audio_callback(indata, frames, time_info, status):
    global audio_gain
    if status:
        print("Audio status:", status, file=sys.stderr)
    mono = indata[:, 0].astype(np.float32)
    rms  = float(np.sqrt(np.mean(mono ** 2)))
    # Apply gain to RMS
    rms *= audio_gain
    try:
        f0 = librosa.yin(mono, fmin=FREQ_MIN, fmax=FREQ_MAX, sr=SAMPLE_RATE)
        pitch = float(np.median(f0[np.isfinite(f0)])) if np.any(np.isfinite(f0)) else 0.0
    except Exception:
        pitch = 0.0
    try:
        pitch_queue.put_nowait(pitch)
        rms_queue.put_nowait(rms)
    except queue.Full:
        pass

def start_audio_stream(device_name):
    if sd is None:
        raise SystemExit("sounddevice недоступен — нет аудио-входа.")
    device_id = None
    for i, d in enumerate(sd.query_devices()):
        if d['name'] == device_name:
            device_id = i; break
    if device_id is None:
        raise SystemExit("Устройство не найдено")
    stream = sd.InputStream(
        samplerate=SAMPLE_RATE, blocksize=BLOCK_SIZE, dtype='float32',
        channels=CHANNELS, device=device_id, callback=audio_callback
    )
    stream.start()
    return stream

# -------------------- Правила автомата --------------------

def step_life(grid: np.ndarray, rule: str) -> np.ndarray:
    H, W = grid.shape
    
    input_count = np.sum(grid)
    
    # ИСПРАВЛЕНИЕ: принудительно конвертируем в int, чтобы арифметика работала
    padded = np.pad(grid.astype(int), ((1,1),(1,1)), mode='constant', constant_values=0)
    neighbors = (
        padded[0:H,0:W] + padded[0:H,1:W+1] + padded[0:H,2:W+2] +
        padded[1:H+1,0:W] +                     padded[1:H+1,2:W+2] +
        padded[2:H+2,0:W] + padded[2:H+2,1:W+1] + padded[2:H+2,2:W+2]
    )
    new = np.zeros_like(grid, dtype=bool)

    if rule == "Conway":
        survive_mask = grid & ((neighbors==2)|(neighbors==3))
        birth_mask = (~grid) & (neighbors==3)
        new[survive_mask | birth_mask] = True
            
    elif rule == "HighLife":
        survive_mask = grid & ((neighbors==2)|(neighbors==3))
        birth_mask = (~grid) & ((neighbors==3)|(neighbors==6))
        new[survive_mask | birth_mask] = True
            
    elif rule == "Day&Night":
        survive_mask = grid & (((neighbors>=3)&(neighbors<=6)) | (neighbors==7) | (neighbors==8))
        birth_mask = (~grid) & ((neighbors==3)|(neighbors==6)|(neighbors==7)|(neighbors==8))
        new[survive_mask | birth_mask] = True
            
    elif rule == "Replicator":
        new[(neighbors % 2) == 1] = True
    elif rule == "Seeds":
        new[(~grid & (neighbors==2))] = True
    elif rule == "Maze":  # B3/S12345
        born = (~grid) & (neighbors==3)
        survive = grid & ((neighbors>=1)&(neighbors<=5))
        new[born | survive] = True
    elif rule == "Coral":  # B3/S45678
        born = (~grid) & (neighbors==3)
        survive = grid & ((neighbors>=4)&(neighbors<=8))
        new[born | survive] = True
    elif rule == "LifeWithoutDeath":  # B3/S012345678
        born = (~grid) & (neighbors==3)
        survive = grid
        new[born | survive] = True
                    
    elif rule == "Gnarl":  # B1/S1
        born = (~grid) & (neighbors==1)
        survive = grid & (neighbors==1)
        new[born | survive] = True
    else:
        new = grid.copy()
    
    return new

# -------------------- Спавн --------------------

def spawn_cells(grid: np.ndarray, count: int) -> None:
    H, W = grid.shape
    if count <= 0:
        return
    
    # Простые и гарантированно стабильные паттерны
    # Создаем только блоки 2x2 - они точно стабильны в Conway
    blocks_to_create = max(1, count // 4)  # Один блок = 4 клетки
    
    created_blocks = 0
    for _ in range(blocks_to_create):
        # Найдем свободное место для блока 2x2
        attempts = 0
        while attempts < 10:  # Максимум 10 попыток
            r = random.randrange(1, H - 3)  # Отступ от краев
            c = random.randrange(1, W - 3)
            
            # Проверим, свободно ли место 2x2
            if not grid[r:r+2, c:c+2].any():
                # Создаем блок 2x2
                grid[r:r+2, c:c+2] = True
                created_blocks += 1
                # Добавим отладку для проверки координат
                if r >= H-2 or c >= W-2 or r < 0 or c < 0:
                    print(f"WARNING: spawn_cells creating block at potentially invalid coords: r={r}, c={c}, H={H}, W={W}")
                break
            attempts += 1

# -------------------- Слои --------------------

@dataclass
class Layer:
    grid: np.ndarray
    age:  np.ndarray
    rule: str
    age_palette: str
    rms_palette: str
    color_mode: str  # "Возраст + RMS" | "Только RMS" | "Высота ноты (Pitch)"
    rms_mode: str = "brightness"  # "brightness" | "palette"
    alpha_live: int = 220  # 0..255
    alpha_old:  int = 140  # 0..255
    mix: str = "Normal"   # "Normal" | "Additive"
    solo: bool = False
    mute: bool = False
    
    @property
    def alpha(self):
        """Среднее значение прозрачности"""
        return (self.alpha_live + self.alpha_old) // 2
    
    @alpha.setter
    def alpha(self, value):
        """Устанавливает одинаковую прозрачность для live и old"""
        self.alpha_live = value
        self.alpha_old = value

# -------------------- Пост-обработка --------------------

def apply_trails(surface: pygame.Surface, trail_strength: float):
    if trail_strength <= 0: return
    fade = max(0.0, min(1.0, 1.0 - trail_strength))
    arr = pygame.surfarray.pixels3d(surface)
    arr[:] = (arr * fade).astype(arr.dtype)


def apply_scale_blur(surface: pygame.Surface, scale: int):
    if scale <= 1: return
    w, h = surface.get_size()
    dw, dh = max(1, w//scale), max(1, h//scale)
    small = pygame.transform.smoothscale(surface, (dw, dh))
    surface.blit(pygame.transform.smoothscale(small, (w, h)), (0,0))


def apply_bloom(surface: pygame.Surface, strength: float):
    if strength <= 0: return
    w,h = surface.get_size()
    arr = pygame.surfarray.pixels3d(surface)
    # простая яркостная маска
    lum = (0.2126*arr[:,:,0] + 0.7152*arr[:,:,1] + 0.0722*arr[:,:,2])
    mask = (lum > 180).astype(np.float32) * strength
    mask3 = np.dstack([mask, mask, mask])
    # downscale / upscale для мягкого свечения
    k = 4
    dw, dh = max(1, w // k), max(1, h // k)
    small = pygame.transform.smoothscale(surface, (dw, dh))
    blurred = pygame.transform.smoothscale(small, (w, h))
    arr_b = pygame.surfarray.pixels3d(blurred)
    arr   = pygame.surfarray.pixels3d(surface)
    # усиливаем только яркие места
    np.multiply(arr_b, mask3, out=arr_b, casting='unsafe')
    arr[:] = np.clip(arr.astype(np.float32) + arr_b.astype(np.float32) * strength, 0, 255).astype(np.uint8)


def apply_posterize(surface: pygame.Surface, levels: int):
    """Постеризация цветов до заданного числа уровней."""
    levels = max(2, int(levels))
    arr = pygame.surfarray.pixels3d(surface)
    step = 255 // (levels - 1)
    q = (arr.astype(np.int32) + step // 2) // step
    arr[:] = np.clip(q * step, 0, 255).astype(np.uint8)


def apply_dither(surface: pygame.Surface):
    """Упорядоченный дизеринг (Bayer 4x4). Делает постеризацию мягче."""
    bayer = (1/17.0) * np.array([[0,  8,  2, 10],
                                 [12, 4, 14,  6],
                                 [3, 11,  1,  9],
                                 [15, 7, 13,  5]], dtype=np.float32)
    arr = pygame.surfarray.pixels3d(surface).astype(np.float32)
    H, W = arr.shape[1], arr.shape[0]
    tile = np.tile(bayer, (W//4 + 1, H//4 + 1))[:W, :H].T[..., None]
    arr[:] = np.clip(arr + (tile * 8.0 - 4.0), 0, 255)


def apply_scanlines(surface: pygame.Surface, strength: float):
    """Сканлайны: затемнение каждой второй строки."""
    strength = clamp01(strength)
    if strength <= 0: return
    arr = pygame.surfarray.pixels3d(surface)
    arr[1::2, :, :] = (arr[1::2, :, :].astype(np.float32) * (1.0 - 0.5 * strength)).astype(np.uint8)


def apply_pixelate(surface: pygame.Surface, block: int):
    """Пикселизация: downscale → upscale с целочисленным блоком."""
    block = max(1, int(block))
    if block == 1: return
    w, h = surface.get_size()
    small = pygame.transform.scale(surface, (max(1, w // block), max(1, h // block)))
    surface.blit(pygame.transform.scale(small, (w, h)), (0, 0))


def apply_outline(surface: pygame.Surface, thickness: int = 1):
    """Контур по градиенту яркости (простая Sobel-like оценка)."""
    thickness = max(1, int(thickness))
    arr = pygame.surfarray.pixels3d(surface)
    gray = (0.2126*arr[:,:,0] + 0.7152*arr[:,:,1] + 0.0722*arr[:,:,2]).astype(np.float32)
    gx = np.zeros_like(gray); gy = np.zeros_like(gray)
    gx[:, 1:] += gray[:, 1:] - gray[:, :-1]
    gy[1:, :] += gray[1:, :] - gray[:-1, :]
    mag = np.clip(np.abs(gx) + np.abs(gy), 0, 255)
    for _ in range(thickness - 1):
        mag = np.maximum.reduce([
            mag,
            np.pad(mag[1:, :],  ((0,1),(0,0)), mode='edge'),
            np.pad(mag[:-1, :], ((1,0),(0,0)), mode='edge'),
            np.pad(mag[:, 1:],  ((0,0),(0,1)), mode='edge'),
            np.pad(mag[:, :-1], ((0,0),(1,0)), mode='edge'),
        ])
    edge = (mag > 64)
    arr[edge] = [255, 255, 255]


# -------------------- Рендерер и смешивание --------------------

class RenderManager:
    def __init__(self, w_cells: int, h_cells: int, cell_size: int):
        self.wc = w_cells; self.hc = h_cells; self.cs = cell_size
        self.canvas = pygame.Surface((w_cells * cell_size, h_cells * cell_size)).convert()

    def clear(self, color=BG_COLOR):
        self.canvas.fill(color)

    def blit_layer(self, color_img: np.ndarray, mix: str, alpha_live: int = 255, alpha_old: int = 255):
        """color_img: (H,W,3) uint8 в координатах клеток."""
        try:
            h, w = color_img.shape[:2]
            
            # ИСПРАВЛЕНИЕ: Используем nearest neighbor для точного масштабирования без интерполяции
            # Создаем поверхность точно по размеру клеток
            rgb_surf = pygame.surfarray.make_surface(np.transpose(color_img, (1, 0, 2)))
            
            # Масштабируем с nearest neighbor (без интерполяции) для четких границ
            scaled_size = (w * self.cs, h * self.cs)  # w*8, h*8
            rgb_surf = pygame.transform.scale(rgb_surf, scaled_size)
            
            # Применяем альфа
            rgb_surf.set_colorkey((0, 0, 0))  # Черный = прозрачный
            rgb_surf.set_alpha(alpha_live)
            
            # Применяем режим смешивания
            if mix == "Additive":
                rgb_surf.set_blendmode(pygame.BLEND_RGB_ADD)
            
            self.canvas.blit(rgb_surf, (0, 0))
            
        except Exception as e:
            print(f"ERROR in blit_layer: {e}")
            print(f"Image shape: {color_img.shape}, mix: {mix}")
            import traceback
            traceback.print_exc()
            
            # Fallback к оригинальному методу
            try:
                # Альтернативный метод - создаем две поверхности
                h, w = color_img.shape[:2]
                
                # Создаем RGB поверхность
                rgb_surf = pygame.surfarray.make_surface(np.transpose(color_img, (1, 0, 2)))
                rgb_surf = pygame.transform.scale(rgb_surf, self.canvas.get_size())
                
                # Создаем альфа-маску с учетом прозрачности слоя
                brightness = np.sum(color_img, axis=2)
                # Применяем альфа-значения к ярким пикселям (alpha_live для живых клеток)
                alpha_mask = np.where(brightness > 0, alpha_live, 0).astype(np.uint8)
                alpha_surf = pygame.surfarray.make_surface(np.transpose(alpha_mask, (1, 0)))
                alpha_surf = pygame.transform.scale(alpha_surf, self.canvas.get_size())
                
                # Создаем финальную поверхность с альфа-каналом
                final_surf = rgb_surf.convert_alpha()
                
                # Применяем альфа-маску через per-pixel alpha
                final_array = pygame.surfarray.array3d(final_surf)
                alpha_array = pygame.surfarray.array2d(alpha_surf)
                
                # Устанавливаем альфа-значения
                final_surf_alpha = pygame.Surface(self.canvas.get_size(), pygame.SRCALPHA)
                final_surf_alpha.fill((0, 0, 0, 0))  # Прозрачный фон
                
                # Применяем альфа к поверхности и копируем на финальную поверхность
                final_surf.set_alpha(alpha_live)
                final_surf.set_colorkey((0, 0, 0))
                final_surf_alpha.blit(final_surf, (0, 0))
                
                # Применяем режим смешивания
                if mix == "Additive":
                    final_surf_alpha.set_blendmode(pygame.BLEND_ADD)
                
                self.canvas.blit(final_surf_alpha, (0, 0))
                
            except Exception as e2:
                print(f"ERROR in fallback blit_layer: {e2}")
                
                # Простейший fallback
                surf = pygame.surfarray.make_surface(np.transpose(color_img, (1, 0, 2)))
                surf = pygame.transform.scale(surf, self.canvas.get_size())
                surf.set_colorkey((0, 0, 0))
                surf.set_alpha(alpha_live)
                if mix == "Additive":
                    surf.set_blendmode(pygame.BLEND_RGB_ADD)
                self.canvas.blit(surf, (0, 0))
            self.canvas.blit(surf, (0, 0))


# -------------------- HUD --------------------

class UISlider:
    """Интерактивный слайдер для HUD"""
    def __init__(self, x, y, width, height, min_val, max_val, current_val, label="", value_format="{:.0f}"):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.min_val = min_val
        self.max_val = max_val
        self.current_val = current_val
        self.label = label
        self.value_format = value_format
        self.dragging = False
        self.rect = pygame.Rect(x, y, width, height)
        
    def handle_event(self, event):
        """Обработка событий мыши"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
                self._update_value_from_mouse(event.pos)
                return True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self._update_value_from_mouse(event.pos)
            return True
        return False
    
    def _update_value_from_mouse(self, mouse_pos):
        """Обновляет значение на основе позиции мыши"""
        rel_x = mouse_pos[0] - self.rect.x  # Используем rect.x вместо self.x
        ratio = max(0.0, min(1.0, rel_x / self.width))
        self.current_val = self.min_val + ratio * (self.max_val - self.min_val)
    
    def draw(self, surface, font):
        """Отрисовка простого современного слайдера"""
        # Синхронизируем координаты с rect
        self.x = self.rect.x
        self.y = self.rect.y
        
        # Простой фон слайдера без тени
        bg_color = SimpleColors.GRAY_100 if self.dragging else SimpleColors.GRAY_50
        pygame.draw.rect(surface, bg_color, self.rect, border_radius=8)
        
        # Заполненная часть (прогресс)
        ratio = (self.current_val - self.min_val) / (self.max_val - self.min_val)
        fill_width = int(self.width * ratio)
        if fill_width > 4:  # Минимальная ширина для отображения
            fill_rect = pygame.Rect(self.x, self.y, fill_width, self.height)
            fill_color = SimpleColors.PRIMARY if self.dragging else SimpleColors.PRIMARY_LIGHT
            pygame.draw.rect(surface, fill_color, fill_rect, border_radius=8)
        
        # Простая рамка слайдера
        border_color = SimpleColors.BORDER_FOCUS if self.dragging else SimpleColors.BORDER
        pygame.draw.rect(surface, border_color, self.rect, 2, border_radius=8)
        
        # Простая круглая ручка слайдера
        if fill_width > 0:
            handle_x = self.x + fill_width
            handle_y = self.y + self.height // 2
            
            # Основа ручки
            handle_color = SimpleColors.PRIMARY if self.dragging else SimpleColors.GRAY_400
            pygame.draw.circle(surface, SimpleColors.SURFACE, (handle_x, handle_y), 8)  # Белый фон
            pygame.draw.circle(surface, handle_color, (handle_x, handle_y), 6)  # Цветной центр
            pygame.draw.circle(surface, SimpleColors.BORDER, (handle_x, handle_y), 8, 2)  # Рамка
        
        # Простой современный текст
        if self.label:
            try:
                # Классические шрифты без жирности
                label_font = pygame.font.SysFont("times new roman,georgia,serif", 14)
                value_font = pygame.font.SysFont("times new roman,georgia,serif", 13)
            except:
                label_font = pygame.font.Font(None, 14)
                value_font = pygame.font.Font(None, 13)
            
            try:
                # Безопасное отображение только ASCII символов
                label_text = str(self.label).encode('ascii', 'ignore').decode('ascii')
                value_text = str(self.value_format.format(self.current_val)).encode('ascii', 'ignore').decode('ascii')
                
                # Простые цвета текста
                label_color = SimpleColors.TEXT_PRIMARY
                value_color = SimpleColors.PRIMARY if self.dragging else SimpleColors.TEXT_SECONDARY
                
                label_surface = label_font.render(label_text, True, label_color)
                value_surface = value_font.render(value_text, True, value_color)
                
                # Размещаем текст ВНАДцм слайдером с достаточным отступом
                text_y = self.y - 25  # Увеличиваем отступ чтобы избежать наложения
                surface.blit(label_surface, (self.x, text_y))
                value_x = self.x + self.width - value_surface.get_width()
                surface.blit(value_surface, (value_x, text_y))
                    
            except Exception as e:
                # Fallback - отображаем только значение
                fallback_text = str(self.current_val)
                fallback_surface = label_font.render(fallback_text, True, SimpleColors.TEXT_SECONDARY)
                surface.blit(fallback_surface, (self.x, self.y - 25))

class UIButton:
    """Интерактивная кнопка для HUD"""
    def __init__(self, x, y, width, height, label, is_toggle=False, active=False):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.label = label
        self.is_toggle = is_toggle
        self.active = active
        self.rect = pygame.Rect(x, y, width, height)
        self.pressed = False
        
    def handle_event(self, event):
        """Обработка событий мыши"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.pressed = True
                if self.is_toggle:
                    self.active = not self.active
                return True
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.pressed:
                self.pressed = False
                if not self.is_toggle:
                    return True
        return False
    
    def draw(self, surface, font):
        """Отрисовка простой современной кнопки"""
        # Синхронизируем координаты с rect
        self.x = self.rect.x
        self.y = self.rect.y
        
        # Простой фон кнопки
        if self.is_toggle and self.active:
            # Активная кнопка-переключатель (простой синий)
            bg_color = SimpleColors.PRIMARY
            border_color = SimpleColors.PRIMARY
        elif self.pressed:
            # Нажатая кнопка
            bg_color = SimpleColors.ACTIVE
            border_color = SimpleColors.BORDER_FOCUS
        else:
            # Обычная кнопка
            bg_color = SimpleColors.SURFACE
            border_color = SimpleColors.BORDER
            
        # Рисуем простую кнопку
        pygame.draw.rect(surface, bg_color, self.rect, border_radius=8)
        pygame.draw.rect(surface, border_color, self.rect, 2, border_radius=8)
        
        # Простой индикатор для активных переключателей
        if self.is_toggle and self.active:
            # Маленький кружок в углу
            pygame.draw.circle(surface, SimpleColors.SURFACE, (self.x + 8, self.y + 8), 3)
        
        # Простой современный текст
        try:
            button_font = pygame.font.SysFont("times new roman,georgia,serif", 12)
        except:
            button_font = pygame.font.Font(None, 12)
            
        try:
            # Безопасное отображение только ASCII символов
            button_text = str(self.label).encode('ascii', 'ignore').decode('ascii')
            
            # Простой цвет текста
            if self.is_toggle and self.active:
                text_color = SimpleColors.SURFACE  # Белый на синем
            else:
                text_color = SimpleColors.TEXT_PRIMARY  # Темный на светлом
                
            text = button_font.render(button_text, True, text_color)
            text_rect = text.get_rect(center=self.rect.center)
            surface.blit(text, text_rect)
            
        except Exception as e:
            # Fallback для проблемных символов
            text = button_font.render("BTN", True, SimpleColors.TEXT_SECONDARY)
            text_rect = text.get_rect(center=self.rect.center)
            surface.blit(text, text_rect)

class UIComboBox:
    """Выпадающий список для HUD"""
    def __init__(self, x, y, width, height, label, options, current_index=0):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.label = label
        self.options = options
        self.current_index = current_index
        self.rect = pygame.Rect(x, y, width, height)
        self.is_open = False
        self.hover_index = -1
        
    @property
    def expanded(self):
        """Alias для is_open для совместимости с кодом отрисовки"""
        return self.is_open
        
    @property
    def current_value(self):
        if 0 <= self.current_index < len(self.options):
            return self.options[self.current_index]
        return ""
    
    def handle_event(self, event):
        """Обработка событий мыши"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            
            # Клик по основной области
            if self.rect.collidepoint(event.pos):
                if not self.is_open:
                    self.is_open = True
                    return True
                else:
                    # Клик по основной области когда список открыт - закрываем список
                    self.is_open = False
                    return True
            elif self.is_open:
                # Клик по элементу в открытом списке (вне основной области)
                list_start_y = self.y + self.height
                if mouse_y >= list_start_y:
                    relative_y = mouse_y - list_start_y
                    option_index = relative_y // self.height
                    if 0 <= option_index < len(self.options):
                        old_index = self.current_index
                        self.current_index = option_index
                        self.is_open = False
                        # Возвращаем True только если индекс действительно изменился
                        return old_index != option_index
                # Клик вне списка - закрываем
                self.is_open = False
                return True
                    
        elif event.type == pygame.MOUSEMOTION and self.is_open:
            # Отслеживаем наведение на элементы
            mouse_x, mouse_y = event.pos
            relative_y = mouse_y - (self.y + self.height)
            if relative_y >= 0:
                option_index = relative_y // self.height
                if 0 <= option_index < len(self.options):
                    self.hover_index = option_index
                else:
                    self.hover_index = -1
            else:
                self.hover_index = -1
                
        return False
    
    def draw(self, surface, font):
        """Отрисовка простого современного комбобокса"""
        # Синхронизируем координаты с rect
        self.x = self.rect.x
        self.y = self.rect.y
        
        # Простой фон комбобокса
        bg_color = SimpleColors.SURFACE_VARIANT if self.is_open else SimpleColors.SURFACE
        pygame.draw.rect(surface, bg_color, self.rect, border_radius=8)
        
        # Простая рамка
        border_color = SimpleColors.BORDER_FOCUS if self.is_open else SimpleColors.BORDER
        pygame.draw.rect(surface, border_color, self.rect, 2, border_radius=8)
        
        # Простые шрифты
        try:
            label_font = pygame.font.SysFont("times new roman,georgia,serif", 12)
            value_font = pygame.font.SysFont("times new roman,georgia,serif", 11)
        except:
            label_font = pygame.font.Font(None, 12)
            value_font = pygame.font.Font(None, 11)
        
        # Отображаем лейбл над комбобоксом
        label_surface = label_font.render(self.label, True, SimpleColors.TEXT_SECONDARY)
        surface.blit(label_surface, (self.x, self.y - 18))
        
        # Отображаем текущее значение
        current_text = self.current_value[:30] + "..." if len(self.current_value) > 30 else self.current_value
        text_color = SimpleColors.TEXT_PRIMARY
        text_surface = value_font.render(current_text, True, text_color)
        surface.blit(text_surface, (self.x + 8, self.y + 6))
        
        # Простая стрелка
        arrow_x = self.x + self.width - 20
        arrow_y = self.y + self.height // 2
        arrow_color = SimpleColors.PRIMARY if self.is_open else SimpleColors.TEXT_SECONDARY
        
        if self.is_open:
            # Стрелка вверх (закрыть)
            pygame.draw.polygon(surface, arrow_color, [
                (arrow_x + 2, arrow_y + 2),
                (arrow_x + 10, arrow_y + 2),
                (arrow_x + 6, arrow_y - 2)
            ])
        else:
            # Стрелка вниз (открыть)
            pygame.draw.polygon(surface, arrow_color, [
                (arrow_x + 2, arrow_y - 2),
                (arrow_x + 10, arrow_y - 2),
                (arrow_x + 6, arrow_y + 2)
            ])
        
        # Простой выпадающий список
        if self.is_open:
            dropdown_height = len(self.options) * self.height
            dropdown_rect = pygame.Rect(self.x, self.y + self.height, self.width, dropdown_height)
            
            # Простой фон списка
            pygame.draw.rect(surface, SimpleColors.SURFACE, dropdown_rect, border_radius=8)
            pygame.draw.rect(surface, SimpleColors.BORDER, dropdown_rect, 2, border_radius=8)
            
            # Элементы списка
            for i, option in enumerate(self.options):
                option_y = self.y + self.height + i * self.height
                option_rect = pygame.Rect(self.x, option_y, self.width, self.height)
                
                # Простая подсветка при наведении или выборе
                if i == self.hover_index:
                    pygame.draw.rect(surface, SimpleColors.HOVER, option_rect, border_radius=6)
                elif i == self.current_index:
                    pygame.draw.rect(surface, SimpleColors.SELECTED, option_rect, border_radius=6)
                
                # Текст элемента
                option_text = option[:30] + "..." if len(option) > 30 else option
                text_color = SimpleColors.TEXT_PRIMARY if i == self.current_index else SimpleColors.TEXT_SECONDARY
                option_surface = value_font.render(option_text, True, text_color)
                surface.blit(option_surface, (self.x + 8, option_y + 6))

class UISeparator:
    """Разделитель для группировки элементов в HUD"""
    def __init__(self, x, y, width, label=""):
        self.x = x
        self.y = y
        self.width = width
        self.label = label
        self.height = 15  # Высота разделителя
        self.rect = pygame.Rect(x, y, width, self.height)
        
    def handle_event(self, event):
        """Разделители не обрабатывают события"""
        return False
        
    def draw(self, surface, font):
        """Отрисовка простого разделителя"""
        # Синхронизируем координаты с rect
        self.x = self.rect.x
        self.y = self.rect.y
        
        # Рисуем лейбл если есть
        if self.label:
            try:
                label_font = pygame.font.SysFont("times new roman,georgia,serif", 12)
            except:
                label_font = pygame.font.Font(None, 12)
                
            label_surface = label_font.render(self.label, True, SimpleColors.TEXT_PRIMARY)
            label_width = label_surface.get_width()
            
            # Простой фон для лейбла
            bg_surface = pygame.Surface((label_width + 16, self.height + 4), pygame.SRCALPHA)
            pygame.draw.rect(bg_surface, SimpleColors.SURFACE, (0, 0, label_width + 16, self.height + 4), border_radius=6)
            pygame.draw.rect(bg_surface, SimpleColors.BORDER, (0, 0, label_width + 16, self.height + 4), 1, border_radius=6)
            
            # Простые точки по бокам
            pygame.draw.circle(bg_surface, SimpleColors.PRIMARY, (6, (self.height + 4) // 2), 2)
            pygame.draw.circle(bg_surface, SimpleColors.PRIMARY, (label_width + 10, (self.height + 4) // 2), 2)
            
            # Позиционируем лейбл по центру разделителя
            label_x = self.x + (self.width - label_width - 16) // 2
            
            # Рисуем простые линии по бокам от лейбла
            line_y = self.y + self.height // 2
            
            # Левая линия
            if label_x > self.x:
                pygame.draw.line(surface, SimpleColors.BORDER, (self.x, line_y), (label_x, line_y), 1)
            
            # Правая линия
            right_start = label_x + label_width + 16
            if right_start < self.x + self.width:
                pygame.draw.line(surface, SimpleColors.BORDER, (right_start, line_y), (self.x + self.width, line_y), 1)
            
            # Отрисовываем фон лейбла и сам лейбл

            surface.blit(bg_surface, (label_x, self.y - 2))
            surface.blit(label_surface, (label_x + 8, self.y + 1))
        else:
            # Простая линия если нет лейбла
            line_y = self.y + self.height // 2
            pygame.draw.line(surface, SimpleColors.BORDER, (self.x, line_y), (self.x + self.width, line_y), 1)

class UILabel:
    """Простая текстовая метка"""
    def __init__(self, x, y, width, height, text="", font_size=12):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.font_size = font_size
        self.rect = pygame.Rect(x, y, width, height)
        
    def handle_event(self, event):
        """Метки не обрабатывают события"""
        return False
        
    def draw(self, surface, font):
        """Отрисовка текстовой метки"""
        try:
            label_font = pygame.font.SysFont("times new roman,georgia,serif", self.font_size)
        except:
            label_font = pygame.font.Font(None, self.font_size)
            
        text_surface = label_font.render(self.text, True, SimpleColors.TEXT_PRIMARY)
        
        # Рисуем фон
        pygame.draw.rect(surface, SimpleColors.SURFACE, self.rect, border_radius=4)
        pygame.draw.rect(surface, SimpleColors.BORDER, self.rect, 1, border_radius=4)
        
        # Центрируем текст
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

class HUD:
    def __init__(self, font: pygame.font.Font, screen_height: int, layer_count: int = 3):
        self.font = font
        self.small_font = pygame.font.SysFont("times new roman,georgia,serif", 12)
        self.visible = True
        self.mini_held = False
        self.expanded = False  # Развернутый режим HUD
        self.H = screen_height  # Высота экрана
        self.layer_count = layer_count  # Количество слоёв
        
        # Переменные для скроллинга
        self.scroll_offset = 0  # Смещение скролла
        self.scroll_speed = 30  # Скорость скролла
        self.max_scroll = 0  # Максимальное смещение скролла
        self.scroll_dragging = False  # Флаг перетаскивания полосы прокрутки
        self.scroll_thumb_rect = None  # Область ползунка прокрутки
        self.scroll_drag_start_y = 0  # Начальная позиция при перетаскивании
        
        # Создаем UI элементы
        self._create_ui_elements()
        
        # Загружаем значения из конфига
        self._load_config_values()
        
        # Колбэки для изменений параметров
        self.on_parameter_change = None
        
    def _create_ui_elements(self):
        """Создает UI элементы HUD"""
        self.sliders = {}
        self.buttons = {}
        self.comboboxes = {}  # Добавляем комбобоксы
        self.separators = {}  # Добавляем разделители
        self.labels = {}  # Добавляем метки
        
        # Позиции для элементов (правая панель на всю ширину)
        # Располагаем панель после игрового поля на всю доступную ширину
        panel_x = GRID_W * CELL_SIZE + 20  # 990
        panel_width = HUD_WIDTH - 40  # 480 пикселей ширина
        y_pos = 60  # Начальная позиция - выше, чтобы поместиться в увеличенную панель
        slider_width = panel_width - 30  # 450 пикселей для слайдеров
        slider_height = 24  # Увеличиваем высоту слайдеров
        button_width = 80
        button_height = 22
        combo_width = 200
        combo_height = 22
        
        # === КОМБОБОКСЫ ===
        # Доступные палитры
        palette_options = [
            "Blue->Red", "Blue->Green->Yellow->Red", "White->LightGray->Gray->DarkGray", "BrightRed->DarkRed->DarkGray->Black", "Fire", "Ocean", "Neon", "Ukraine",
            "Rainbow", "Sunset", "Pastel", "Viridis", "Inferno", "Magma", "Plasma", "Cividis", "Twilight", "Spring", "Summer", "Autumn", "Winter",
            "Ice", "Forest", "Desert", "Candy", "Retro", "Cyberpunk", "Gold", "Silver", "Copper", "Emerald", "Sapphire", "Ruby", "Amethyst",
            "Lime", "Mint", "Peach", "Lavender", "Rose", "Sky", "Sand", "Charcoal", "Steel", "Bronze", "Pearl", "Coral", "Jade", "Topaz",
            "Galaxy", "Aurora", "Tropical", "Vintage", "Monochrome", "Sepia", "HighContrast", "LowContrast", "DeepSea", "Volcano", "Clouds", "Flame"
        ]
        
        # Доступные правила автомата
        rule_options = [
            "Conway",
            "HighLife", 
            "Day&Night",
            "Replicator",
            "Seeds",
            "Maze",
            "Coral",
            "LifeWithoutDeath",
        ]
        
        # Заголовок для настроек слоёв
        self.separators['layers'] = UISeparator(panel_x, y_pos, panel_width - 20, "LAYER SETTINGS")
        y_pos += 35
        
        # Кнопки управления отдельными слоями
        layer_button_width = 60
        layer_y = y_pos
        
        # Создаем кнопки и выпадающие списки для всех слоёв
        for layer_idx in range(self.layer_count):
            # Заголовок слоя - компактное расположение кнопок в одну строку
            x_pos = panel_x
            
            # Кнопки Solo/Mute для каждого слоя
            self.buttons[f'layer_{layer_idx}_solo'] = UIButton(x_pos, layer_y, layer_button_width, button_height, f"Solo {layer_idx+1}", True, False)
            x_pos += layer_button_width + 8
            
            self.buttons[f'layer_{layer_idx}_mute'] = UIButton(x_pos, layer_y, layer_button_width, button_height, f"Mute {layer_idx+1}", True, False)
            x_pos += layer_button_width + 8
            
            # Кнопка смены правила для слоя
            self.buttons[f'layer_{layer_idx}_rule'] = UIButton(x_pos, layer_y, 100, button_height, "LifeWithoutDeath", False, False)
            
            # Переходим на следующую строку для палитр
            layer_y += button_height + 8
            x_pos = panel_x
            
            # Выпадающие списки для палитр слоя в одну строку
            palette_combo_width = 220  # Увеличиваем ширину для длинных названий
            
            # Age палитра для слоя
            self.comboboxes[f'layer_{layer_idx}_age_palette'] = UIComboBox(
                x_pos, layer_y, palette_combo_width, combo_height, 
                f"Age {layer_idx+1}", palette_options, 3  # Fire по умолчанию
            )
            x_pos += palette_combo_width + 10  # Уменьшаем отступ
            
            # RMS палитра для слоя
            self.comboboxes[f'layer_{layer_idx}_rms_palette'] = UIComboBox(
                x_pos, layer_y, palette_combo_width, combo_height,
                f"RMS {layer_idx+1}", palette_options, 0  # Blue->Green->Yellow->Red
            )
            
            # Переходим на следующую строку для режима RMS
            layer_y += combo_height + 8
            x_pos = panel_x
            
            # Режим RMS для слоя  
            rms_mode_options = ["Brightness", "Palette"]
            self.comboboxes[f'layer_{layer_idx}_rms_mode'] = UIComboBox(
                x_pos, layer_y, 200, combo_height,
                f"RMS Mode {layer_idx+1}", rms_mode_options, 0  # Brightness по умолчанию
            )
            
            # Слайдер прозрачности для слоя
            layer_y += combo_height + 10
            x_pos = panel_x
            
            # Единый слайдер прозрачности
            alpha_slider_width = 380  # Используем всю доступную ширину
            self.sliders[f'layer_{layer_idx}_alpha'] = UISlider(
                x_pos, layer_y, alpha_slider_width, slider_height, 
                0, 255, 180, f"Alpha {layer_idx+1}", "{:.0f}"
            )
            
            layer_y += slider_height + 15
        
        y_pos = layer_y + 15
        
        # Разделитель - Основные параметры
        self.separators['main_params'] = UISeparator(panel_x, y_pos, panel_width - 20, "MAIN PARAMETERS")
        y_pos += 35
        
        # === СЛАЙДЕРЫ ===
        # Основные параметры
        self.sliders['layer_count'] = UISlider(panel_x, y_pos, slider_width, slider_height, 1, 5, 2, "Layer Count", "{:.0f}")
        y_pos += 55
        
        self.sliders['tick_ms'] = UISlider(panel_x, y_pos, slider_width, slider_height, 5, 1000, 323, "Tick (ms)", "{:.0f}")
        y_pos += 55  # Увеличиваем интервал для лучшего разделения между слайдерами
        
        self.sliders['rms_strength'] = UISlider(panel_x, y_pos, slider_width, slider_height, 0, 200, 187, "RMS Power (%)", "{:.0f}")
        y_pos += 55
        
        self.sliders['gain'] = UISlider(panel_x, y_pos, slider_width, slider_height, 0.1, 5.0, 2.5, "Gain", "{:.2f}")
        y_pos += 55
        
        self.sliders['max_age'] = UISlider(panel_x, y_pos, slider_width, slider_height, 10, 300, 282, "Max Age", "{:.0f}")
        y_pos += 55
        
        self.sliders['fade_start'] = UISlider(panel_x, y_pos, slider_width, slider_height, 10, 200, 60, "Fade Start", "{:.0f}")
        y_pos += 55
        
        # Разделитель - RMS параметры
        self.separators['rms_params'] = UISeparator(panel_x, y_pos, panel_width - 20, "RMS THRESHOLDS")
        y_pos += 35
        
        # RMS пороги
        self.sliders['clear_rms'] = UISlider(panel_x, y_pos, slider_width, slider_height, 0.001, 0.02, 0.004, "Clear Threshold", "{:.4f}")
        y_pos += 55
        
        self.sliders['color_rms_min'] = UISlider(panel_x, y_pos, slider_width, slider_height, 0.001, 0.1, 0.0961, "RMS Min", "{:.4f}")
        y_pos += 55
        
        self.sliders['color_rms_max'] = UISlider(panel_x, y_pos, slider_width, slider_height, 0.1, 1.0, 0.3, "RMS Max", "{:.3f}")
        y_pos += 55
        
        # Разделитель - Soft Clean
        self.separators['soft_clean'] = UISeparator(panel_x, y_pos, panel_width - 20, "SOFT CLEAN")
        y_pos += 35
        
        # Soft Clean параметры
        self.sliders['soft_kill_rate'] = UISlider(panel_x, y_pos, slider_width, slider_height, 0, 100, 80, "Soft Kill (%)", "{:.0f}")
        y_pos += 55
        
        self.sliders['soft_fade_floor'] = UISlider(panel_x, y_pos, slider_width, slider_height, 0.1, 1.0, 0.3, "Fade Floor", "{:.2f}")
        y_pos += 55
        
        # Новые параметры контроля популяции
        self.sliders['max_cells_percent'] = UISlider(panel_x, y_pos, slider_width, slider_height, 10, 90, 50, "Max Cells (%)", "{:.0f}")
        y_pos += 55
        
        self.sliders['soft_clear_threshold'] = UISlider(panel_x, y_pos, slider_width, slider_height, 40, 95, 70, "Clear At (%)", "{:.0f}")
        y_pos += 55
        
        self.sliders['age_bias'] = UISlider(panel_x, y_pos, slider_width, slider_height, 0, 100, 80, "Age Bias (%)", "{:.0f}")
        y_pos += 55
        
        # Информационная панель популяции
        self.labels['population_info'] = UILabel(panel_x, y_pos, panel_width - 20, 30, "Population: 0 / 0 (0%)", 12)
        y_pos += 35
        
        # Разделитель - Pitch Tick
        self.separators['pitch_tick'] = UISeparator(panel_x, y_pos, panel_width - 20, "PITCH TICK")
        y_pos += 35
        
        # Pitch Tick диапазон
        self.sliders['pitch_tick_min'] = UISlider(panel_x, y_pos, slider_width, slider_height, 10, 200, 60, "Pitch Tick Min", "{:.0f}")
        y_pos += 55
        
        self.sliders['pitch_tick_max'] = UISlider(panel_x, y_pos, slider_width, slider_height, 100, 500, 300, "Pitch Tick Max", "{:.0f}")
        y_pos += 55
        
        # Разделитель - Эффекты
        self.separators['effects'] = UISeparator(panel_x, y_pos, panel_width - 20, "EFFECTS PARAMETERS")
        y_pos += 35
        
        # === ЭФФЕКТЫ СЛАЙДЕРЫ ===
        self.sliders['trail_strength'] = UISlider(panel_x, y_pos, slider_width, slider_height, 0.01, 0.2, 0.06, "Trail Strength", "{:.3f}")
        y_pos += 55
        
        self.sliders['blur_scale'] = UISlider(panel_x, y_pos, slider_width, slider_height, 1, 10, 2, "Blur Scale", "{:.0f}")
        y_pos += 55
        
        self.sliders['bloom_strength'] = UISlider(panel_x, y_pos, slider_width, slider_height, 0.1, 1.0, 0.35, "Bloom Strength", "{:.2f}")
        y_pos += 55
        
        self.sliders['poster_levels'] = UISlider(panel_x, y_pos, slider_width, slider_height, 2, 16, 5, "Posterize Levels", "{:.0f}")
        y_pos += 55
        
        self.sliders['scan_strength'] = UISlider(panel_x, y_pos, slider_width, slider_height, 0.1, 1.0, 0.25, "Scanlines Strength", "{:.2f}")
        y_pos += 55
        
        self.sliders['pixel_block'] = UISlider(panel_x, y_pos, slider_width, slider_height, 1, 8, 1, "Pixelate Block", "{:.0f}")
        y_pos += 55
        
        self.sliders['outline_thick'] = UISlider(panel_x, y_pos, slider_width, slider_height, 1, 5, 1, "Outline Thickness", "{:.0f}")
        y_pos += 55
        
        # Разделитель - Кнопки управления
        self.separators['controls'] = UISeparator(panel_x, y_pos, panel_width - 20, "CONTROLS")
        y_pos += 35
        
        # === КНОПКИ ===
        # Первый ряд кнопок
        x_pos = panel_x
        
        self.buttons['pitch_tick_enable'] = UIButton(x_pos, y_pos, button_width, button_height, "Pitch→Tick", True, False)
        x_pos += button_width + 5
        
        self.buttons['rms_modulation'] = UIButton(x_pos, y_pos, button_width, button_height, "RMS Mod", True, True)
        x_pos = panel_x
        y_pos += button_height + 4
        
        # Второй ряд - Soft Clear
        self.buttons['soft_clear_enable'] = UIButton(x_pos, y_pos, button_width, button_height, "Soft Clear", True, True)
        x_pos += button_width + 5
        
        self.buttons['soft_mode_toggle'] = UIButton(x_pos, y_pos, button_width, button_height, "Kill/Fade", True, False)
        x_pos = panel_x
        y_pos += button_height + 4
        
        # Третий ряд - Зеркала
        self.buttons['mirror_x'] = UIButton(x_pos, y_pos, button_width, button_height, "Mirror X", True, False)
        x_pos += button_width + 5
        
        self.buttons['mirror_y'] = UIButton(x_pos, y_pos, button_width, button_height, "Mirror Y", True, False)
        x_pos = panel_x
        y_pos += button_height + 8
        
        # === FX КНОПКИ ===
        fx_button_width = 55
        
        # Ряд 1
        self.buttons['fx_trails'] = UIButton(x_pos, y_pos, fx_button_width, button_height, "Trails", True, True)
        x_pos += fx_button_width + 3
        
        self.buttons['fx_blur'] = UIButton(x_pos, y_pos, fx_button_width, button_height, "Blur", True, False)
        x_pos += fx_button_width + 3
        
        self.buttons['fx_bloom'] = UIButton(x_pos, y_pos, fx_button_width, button_height, "Bloom", True, False)
        x_pos = panel_x
        y_pos += button_height + 4
        
        # Ряд 2
        self.buttons['fx_posterize'] = UIButton(x_pos, y_pos, fx_button_width, button_height, "Poster", True, False)
        x_pos += fx_button_width + 3
        
        self.buttons['fx_dither'] = UIButton(x_pos, y_pos, fx_button_width, button_height, "Dither", True, False)
        x_pos += fx_button_width + 3
        
        self.buttons['fx_scanlines'] = UIButton(x_pos, y_pos, fx_button_width, button_height, "Scans", True, False)
        x_pos = panel_x
        y_pos += button_height + 4
        
        # Ряд 3
        self.buttons['fx_pixelate'] = UIButton(x_pos, y_pos, fx_button_width, button_height, "Pixel", True, False)
        x_pos += fx_button_width + 3
        
        self.buttons['fx_outline'] = UIButton(x_pos, y_pos, fx_button_width, button_height, "Line", True, False)
        x_pos = panel_x
        y_pos += button_height + 12
        
        # === АВТОСМЕНА ===
        # Разделитель для автосмены
        self.separators['auto_change'] = UISeparator(panel_x, y_pos, panel_width - 20, "AUTO CHANGE")
        y_pos += 35
        
        # Автосмена правил и палитр
        self.sliders['auto_rule_sec'] = UISlider(panel_x, y_pos, slider_width, slider_height, 0, 30, 5, "Auto Rule Change (sec)", "{:.0f}")
        y_pos += 55
        
        self.sliders['auto_palette_sec'] = UISlider(panel_x, y_pos, slider_width, slider_height, 0, 30, 5, "Auto Palette Change (sec)", "{:.0f}")
        y_pos += 55
        
        # === ДЕЙСТВИЯ ===
        # Разделитель для действий
        self.separators['actions'] = UISeparator(panel_x, y_pos, panel_width - 20, "ACTIONS")
        y_pos += 35
        
        action_button_width = 60
        x_pos = panel_x
        
        self.buttons['random'] = UIButton(x_pos, y_pos, action_button_width, button_height, "Random", False, False)
        x_pos += action_button_width + 5
        
        self.buttons['clear'] = UIButton(x_pos, y_pos, action_button_width, button_height, "Clear", False, False)
        x_pos += action_button_width + 5
        
        self.buttons['test'] = UIButton(x_pos, y_pos, action_button_width, button_height, "Test", False, False)
        x_pos = panel_x
        y_pos += button_height + 4
        
        # Кнопки сброса и пресеты
        self.buttons['reset_defaults'] = UIButton(x_pos, y_pos, 80, button_height, "Reset", False, False)
        x_pos += 85
        
        self.buttons['joy_division'] = UIButton(x_pos, y_pos, 100, button_height, "Joy Division", False, False)
        y_pos += button_height + 12
        
        # Переключатель режима HUD
        self.buttons['expand_hud'] = UIButton(panel_x, y_pos, 100, button_height, "Compact", True, False)
        y_pos += button_height + 8
        
        # Вычисляем общую высоту контента для скроллинга
        self.max_scroll = max(0, y_pos - (self.H - 100))
    
    def _load_config_values(self):
        """Загружает значения из app_config.json и устанавливает их в UI элементы"""
        try:
            with open('app_config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            layer_settings = config.get('layers', {}).get('layer_settings', [])
            layers_config = config.get('layers', {})
            
            print(f"🔧 DEBUG: Loading config with {len(layer_settings)} layer settings")
            
            # Настраиваем комбобоксы для каждого слоя
            for layer_idx, settings in enumerate(layer_settings):
                if layer_idx < self.layer_count:
                    print(f"🔧 DEBUG: Setting up layer {layer_idx}")
                    
                    # Устанавливаем правило для кнопки
                    rule_key = f'layer_{layer_idx}_rule'
                    if rule_key in self.buttons:
                        rule = settings.get('rule', 'Conway')
                        self.buttons[rule_key].text = rule
                        print(f"🔧 DEBUG: Set rule button {rule_key} = {rule}")
                    
                    # Устанавливаем палитры в комбобоксы
                    age_palette_key = f'layer_{layer_idx}_age_palette'
                    if age_palette_key in self.comboboxes:
                        age_palette = settings.get('age_palette', 'Fire')
                        combo = self.comboboxes[age_palette_key]
                        if age_palette in combo.options:
                            combo.current_index = combo.options.index(age_palette)
                            combo.current_value = age_palette
                            print(f"🔧 DEBUG: Set age palette {age_palette_key} = {age_palette}")
                        else:
                            print(f"❌ ERROR: Age palette '{age_palette}' not found in options: {combo.options}")
                    
                    rms_palette_key = f'layer_{layer_idx}_rms_palette'
                    if rms_palette_key in self.comboboxes:
                        rms_palette = settings.get('rms_palette', 'Blue->Green->Yellow->Red')
                        combo = self.comboboxes[rms_palette_key]
                        if rms_palette in combo.options:
                            combo.current_index = combo.options.index(rms_palette)
                            combo.current_value = rms_palette
                            print(f"🔧 DEBUG: Set rms palette {rms_palette_key} = {rms_palette}")
                        else:
                            print(f"❌ ERROR: RMS palette '{rms_palette}' not found in options: {combo.options}")
                    
                    # Устанавливаем состояния кнопок solo/mute
                    solo_key = f'layer_{layer_idx}_solo'
                    if solo_key in self.buttons:
                        self.buttons[solo_key].state = settings.get('solo', False)
                        print(f"🔧 DEBUG: Set solo {solo_key} = {settings.get('solo', False)}")
                    
                    mute_key = f'layer_{layer_idx}_mute'
                    if mute_key in self.buttons:
                        self.buttons[mute_key].state = settings.get('mute', False)
                        print(f"🔧 DEBUG: Set mute {mute_key} = {settings.get('mute', False)}")
            
            # Загружаем значения слайдеров автосмены из конфига
            if 'auto_rule_sec' in self.sliders:
                self.sliders['auto_rule_sec'].value = layers_config.get('auto_rule_sec', 5)
            
            if 'auto_palette_sec' in self.sliders:
                self.sliders['auto_palette_sec'].value = layers_config.get('auto_palette_sec', 5)
            
            # Загружаем состояния кнопок зеркал
            if 'mirror_x' in self.buttons:
                self.buttons['mirror_x'].state = layers_config.get('mirror_x', False)
            
            if 'mirror_y' in self.buttons:
                self.buttons['mirror_y'].state = layers_config.get('mirror_y', False)
        
        except Exception as e:
            print(f"❌ Error loading config values: {e}")
            import traceback
            traceback.print_exc()

    def handle_event(self, event):
        """Обработка событий для интерактивных элементов"""
        if not self.visible:
            return False
        
        # Обработка перетаскивания полосы прокрутки
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.scroll_thumb_rect and self.scroll_thumb_rect.collidepoint(event.pos):
                self.scroll_dragging = True
                self.scroll_drag_start_y = event.pos[1]
                return True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.scroll_dragging = False
        elif event.type == pygame.MOUSEMOTION and self.scroll_dragging:
            # Вычисляем смещение при перетаскивании
            panel_x = GRID_W * CELL_SIZE + 5
            panel_width = HUD_WIDTH - 10
            panel_height = self.H - 10
            
            dy = event.pos[1] - self.scroll_drag_start_y
            scroll_area_height = panel_height - 145  # Доступная область для прокрутки
            
            if scroll_area_height > 0 and self.max_scroll > 0:
                # Преобразуем смещение мыши в смещение контента
                scroll_ratio = dy / scroll_area_height
                new_offset = self.scroll_offset + scroll_ratio * self.max_scroll
                self.scroll_offset = max(0, min(new_offset, self.max_scroll))
                self.scroll_drag_start_y = event.pos[1]
            return True
        
        # Обработка скролла колесиком мыши
        if event.type == pygame.MOUSEWHEEL:
            # Проверяем, что мышь находится в области HUD панели
            panel_x = GRID_W * CELL_SIZE + 5
            panel_width = HUD_WIDTH - 10
            mouse_x, mouse_y = pygame.mouse.get_pos()
            
            if panel_x <= mouse_x <= panel_x + panel_width:
                # Скроллим вверх/вниз
                self.scroll_offset -= event.y * self.scroll_speed
                # Ограничиваем скролл
                self.scroll_offset = max(0, min(self.scroll_offset, self.max_scroll))
                return True
        
        # Обработка клавиш для скролла
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                self.scroll_offset = max(0, self.scroll_offset - self.scroll_speed)
                return True
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.scroll_offset = min(self.max_scroll, self.scroll_offset + self.scroll_speed)
                return True
            elif event.key == pygame.K_HOME:
                self.scroll_offset = 0
                return True
            elif event.key == pygame.K_END:
                self.scroll_offset = self.max_scroll
                return True
            
        # Корректируем позиции элементов с учетом скролла
        scroll_y = -self.scroll_offset
        
        # Обработка комбобоксов с учетом скролла
        for name, combobox in self.comboboxes.items():
            # Временно смещаем комбобокс для проверки событий
            original_y = combobox.y
            original_rect_y = combobox.rect.y
            combobox.y += scroll_y
            combobox.rect.y += scroll_y
            
            if combobox.handle_event(event):
                # Возвращаем оригинальную позицию
                combobox.y = original_y
                combobox.rect.y = original_rect_y
                if self.on_parameter_change:
                    self.on_parameter_change(name, combobox.current_value)
                return True
            
            # Возвращаем оригинальную позицию
            combobox.y = original_y
            combobox.rect.y = original_rect_y
        
        # Обработка слайдеров с учетом скролла
        for name, slider in self.sliders.items():
            # Временно смещаем слайдер для проверки событий
            original_y = slider.y
            slider.y += scroll_y
            slider.rect.y += scroll_y
            
            if slider.handle_event(event):
                # Возвращаем оригинальную позицию
                slider.y = original_y
                slider.rect.y = original_y
                if self.on_parameter_change:
                    self.on_parameter_change(name, slider.current_val)
                return True
            
            # Возвращаем оригинальную позицию
            slider.y = original_y
            slider.rect.y = original_y
        
        # Обработка кнопок с учетом скролла
        for name, button in self.buttons.items():
            # Временно смещаем кнопку для проверки событий
            original_y = button.y
            button.y += scroll_y
            button.rect.y += scroll_y
            
            if button.handle_event(event):
                # Возвращаем оригинальную позицию
                button.y = original_y
                button.rect.y = original_y
                if name == 'expand_hud':
                    self.expanded = button.active
                elif self.on_parameter_change:
                    if button.is_toggle:
                        self.on_parameter_change(name, button.active)
                    else:
                        self.on_parameter_change(name, True)  # Для действий
                return True
            
            # Возвращаем оригинальную позицию
            button.y = original_y
            button.rect.y = original_y
        
        return False

    def update_from_app(self, app):
        """Обновляет значения UI элементов из состояния приложения"""
        # Обновляем информацию о популяции
        total_cells = sum(np.sum(layer.grid) for layer in app.layers)
        total_possible = len(app.layers) * GRID_H * GRID_W
        percentage = (total_cells / total_possible * 100) if total_possible > 0 else 0
        
        if 'population_info' in self.labels:
            self.labels['population_info'].text = f"Population: {total_cells} / {total_possible} ({percentage:.1f}%)"
        
        # Обновляем слайдеры
        if 'tick_ms' in self.sliders:
            self.sliders['tick_ms'].current_val = app.tick_ms
        if 'rms_strength' in self.sliders:
            self.sliders['rms_strength'].current_val = app.rms_strength
        if 'gain' in self.sliders:
            self.sliders['gain'].current_val = app.gain
        if 'max_age' in self.sliders:
            self.sliders['max_age'].current_val = app.max_age
        if 'fade_start' in self.sliders:
            self.sliders['fade_start'].current_val = app.fade_start
        if 'clear_rms' in self.sliders:
            self.sliders['clear_rms'].current_val = app.sel.get('clear_rms', DEFAULT_CLEAR_RMS)
        if 'color_rms_min' in self.sliders:
            self.sliders['color_rms_min'].current_val = app.color_rms_min
        if 'color_rms_max' in self.sliders:
            self.sliders['color_rms_max'].current_val = app.color_rms_max
        if 'soft_kill_rate' in self.sliders:
            self.sliders['soft_kill_rate'].current_val = app.soft_kill_rate
        if 'soft_fade_floor' in self.sliders:
            self.sliders['soft_fade_floor'].current_val = app.soft_fade_floor
        if 'max_cells_percent' in self.sliders:
            self.sliders['max_cells_percent'].current_val = app.max_cells_percent
        if 'soft_clear_threshold' in self.sliders:
            self.sliders['soft_clear_threshold'].current_val = app.soft_clear_threshold
        if 'age_bias' in self.sliders:
            self.sliders['age_bias'].current_val = app.age_bias
        if 'pitch_tick_min' in self.sliders:
            self.sliders['pitch_tick_min'].current_val = app.pitch_tick_min
        if 'pitch_tick_max' in self.sliders:
            self.sliders['pitch_tick_max'].current_val = app.pitch_tick_max
            
        # Обновляем слайдеры эффектов
        if 'trail_strength' in self.sliders:
            self.sliders['trail_strength'].current_val = app.fx.get('trail_strength', 0.06)
        if 'blur_scale' in self.sliders:
            self.sliders['blur_scale'].current_val = app.fx.get('blur_scale', 2)
        if 'bloom_strength' in self.sliders:
            self.sliders['bloom_strength'].current_val = app.fx.get('bloom_strength', 0.35)
        if 'poster_levels' in self.sliders:
            self.sliders['poster_levels'].current_val = app.fx.get('poster_levels', 5)
        if 'scan_strength' in self.sliders:
            self.sliders['scan_strength'].current_val = app.fx.get('scan_strength', 0.25)
        if 'pixel_block' in self.sliders:
            self.sliders['pixel_block'].current_val = app.fx.get('pixel_block', 1)
        if 'outline_thick' in self.sliders:
            self.sliders['outline_thick'].current_val = app.fx.get('outline_thick', 1)
            
        # Обновляем кнопки
        if 'pitch_tick_enable' in self.buttons:
            self.buttons['pitch_tick_enable'].active = app.pitch_tick_enable
        if 'rms_modulation' in self.buttons:
            self.buttons['rms_modulation'].active = getattr(app, 'rms_modulation', True)
        if 'soft_clear_enable' in self.buttons:
            self.buttons['soft_clear_enable'].active = app.soft_clear_enable
        if 'soft_mode_toggle' in self.buttons:
            self.buttons['soft_mode_toggle'].active = app.soft_mode != 'Удалять клетки'
        if 'mirror_x' in self.buttons:
            self.buttons['mirror_x'].active = app.mirror_x
        if 'mirror_y' in self.buttons:
            self.buttons['mirror_y'].active = app.mirror_y
            
        # FX кнопки
        fx_mapping = {
            'fx_trails': 'trails',
            'fx_blur': 'blur', 
            'fx_bloom': 'bloom',
            'fx_posterize': 'posterize',
            'fx_dither': 'dither',
            'fx_scanlines': 'scanlines',
            'fx_pixelate': 'pixelate',
            'fx_outline': 'outline'
        }
        
        for hud_name, fx_name in fx_mapping.items():
            if hud_name in self.buttons:
                self.buttons[hud_name].active = app.fx.get(fx_name, False)
                
        # Обновляем состояние редактора слоев
        if 'layer_count' in self.sliders:
            self.sliders['layer_count'].current_val = len(app.layers)
        if 'layers_different' in self.buttons:
            self.buttons['layers_different'].active = getattr(app, 'layers_different', True)
            
        # Обновляем палитры и настройки отдельных слоев
        for layer_idx in range(min(self.layer_count, len(app.layers))):  # Используем реальное количество слоёв
            layer = app.layers[layer_idx]
            
            # Обновляем Age палитру слоя
            age_combo_name = f'layer_{layer_idx}_age_palette'
            if age_combo_name in self.comboboxes:
                try:
                    if layer.age_palette in self.comboboxes[age_combo_name].options:
                        self.comboboxes[age_combo_name].current_index = self.comboboxes[age_combo_name].options.index(layer.age_palette)
                except Exception as e:
                    pass
            
            # Обновляем RMS палитру слоя
            rms_combo_name = f'layer_{layer_idx}_rms_palette'
            if rms_combo_name in self.comboboxes:
                try:
                    if layer.rms_palette in self.comboboxes[rms_combo_name].options:
                        self.comboboxes[rms_combo_name].current_index = self.comboboxes[rms_combo_name].options.index(layer.rms_palette)
                except Exception as e:
                    pass
            
            # Обновляем RMS режим слоя
            rms_mode_combo_name = f'layer_{layer_idx}_rms_mode'
            if rms_mode_combo_name in self.comboboxes:
                try:
                    # Преобразуем внутреннее значение в UI значение
                    ui_value = "Brightness" if layer.rms_mode == "brightness" else "Palette"
                    if ui_value in self.comboboxes[rms_mode_combo_name].options:
                        self.comboboxes[rms_mode_combo_name].current_index = self.comboboxes[rms_mode_combo_name].options.index(ui_value)
                except Exception as e:
                    pass
            
            # Обновляем слайдер прозрачности слоя
            alpha_name = f'layer_{layer_idx}_alpha'
            if alpha_name in self.sliders:
                # Используем новое свойство alpha
                self.sliders[alpha_name].current_val = layer.alpha
            
            # Обновляем кнопки Solo/Mute слоя
            solo_button_name = f'layer_{layer_idx}_solo'
            if solo_button_name in self.buttons:
                self.buttons[solo_button_name].active = layer.solo
                
            mute_button_name = f'layer_{layer_idx}_mute'
            if mute_button_name in self.buttons:
                self.buttons[mute_button_name].active = layer.mute
                
            # Обновляем кнопку правила слоя
            rule_button_name = f'layer_{layer_idx}_rule'
            if rule_button_name in self.buttons:
                self.buttons[rule_button_name].label = layer.rule[:8]  # Обрезаем название если длинное
        if 'auto_rule_sec' in self.sliders:
            self.sliders['auto_rule_sec'].current_val = app.auto_rule_sec
        if 'auto_palette_sec' in self.sliders:
            self.sliders['auto_palette_sec'].current_val = app.auto_palette_sec
            
        # Обновляем кнопки слоев
        for layer_idx in range(min(5, len(app.layers))):  # Максимум 5 слоев в HUD
            layer = app.layers[layer_idx]
            
            if f'layer_{layer_idx}_solo' in self.buttons:
                self.buttons[f'layer_{layer_idx}_solo'].active = layer.solo
            if f'layer_{layer_idx}_mute' in self.buttons:
                self.buttons[f'layer_{layer_idx}_mute'].active = layer.mute
            if f'layer_{layer_idx}_rule' in self.buttons:
                # Сокращаем название правила для экономии места
                rule_short = layer.rule[:7] if len(layer.rule) > 7 else layer.rule
                self.buttons[f'layer_{layer_idx}_rule'].label = rule_short

    def draw(self, screen, info: Dict[str, str]):
        if not self.visible and not self.mini_held:
            return
            
        # Быстрая информация (всегда показываем)
        lines = []
        if self.mini_held or not self.expanded:
            lines.append("[H] HUD  [Tab] mini-HUD  [ESC] Exit")
            lines.append("Click 'Compact' to expand control panel")
            
        # Добавляем основную информацию
        lines += [f"{k}: {v}" for k, v in info.items()]
        
        # Рисуем базовую информацию
        y = 6
        for ln in lines:
            try:
                # Безопасное отображение ASCII символов
                safe_text = str(ln).encode('ascii', 'ignore').decode('ascii')
                s = self.font.render(safe_text, True, (230, 230, 235))
                screen.blit(s, (8, y))
                y += s.get_height() + 2
            except Exception as e:
                # Пропускаем проблемные строки
                continue
        
        # Если HUD видимый, всегда показываем панель управления
        if self.visible:
            # Современная панель управления - увеличиваем размер и убираем отступ сверху
            panel_x = GRID_W * CELL_SIZE + 5  # 965
            panel_width = HUD_WIDTH - 10  # 510 пикселей
            panel_height = self.H - 10  # Увеличиваем высоту, убираем отступ сверху
            
            # Простая панель - начинаем с самого верха
            panel_rect = pygame.Rect(panel_x, 5, panel_width, panel_height)
            
            # Простой фон панели
            pygame.draw.rect(screen, SimpleColors.SURFACE, panel_rect, border_radius=12)
            pygame.draw.rect(screen, SimpleColors.BORDER, panel_rect, 2, border_radius=12)
            
            # Простая верхняя линия
            top_accent = pygame.Rect(panel_x + 8, 7, panel_width - 16, 2)
            pygame.draw.rect(screen, SimpleColors.PRIMARY, top_accent, border_radius=1)
            
            # Простой заголовок - перемещаем выше
            try:
                title_text = "CONTROL PANEL"
                title_font = pygame.font.SysFont("times new roman,georgia,serif", 16)
                title = title_font.render(title_text, True, SimpleColors.TEXT_PRIMARY)
                screen.blit(title, (panel_x + 15, 15))
            except Exception as e:
                # Fallback заголовок
                title = self.font.render("CONTROL PANEL", True, SimpleColors.TEXT_PRIMARY)
                screen.blit(title, (panel_x + 15, 15))
            
            # Простой статус активных элементов
            active_count = sum(1 for s in self.sliders.values() if s.dragging)
            if active_count > 0:
                status_text = f"Active: {active_count}"
                status_surface = self.small_font.render(status_text, True, SimpleColors.PRIMARY)
                screen.blit(status_surface, (panel_x + panel_width - status_surface.get_width() - 15, 17))
            
            # Простые инструкции по скроллу
            if self.max_scroll > 0:
                scroll_info = "Scroll: Wheel / W,S / Home,End"
                scroll_surface = self.small_font.render(scroll_info, True, SimpleColors.TEXT_SECONDARY)
                screen.blit(scroll_surface, (panel_x + 15, 37))
                
                # Современный индикатор скролла с поддержкой мыши
                if self.max_scroll > 0:
                    scroll_progress = self.scroll_offset / self.max_scroll
                    scroll_bar_height = min(60, panel_height // 4)
                    scroll_bar_y = 60 + scroll_progress * (panel_height - scroll_bar_height - 85)
                    
                    # Простой трек скролла
                    track_rect = pygame.Rect(panel_x + panel_width - 12, 60, 4, panel_height - 85)
                    pygame.draw.rect(screen, SimpleColors.SURFACE_VARIANT, track_rect, border_radius=2)
                    
                    # Простой ползунок скролла с увеличенной областью для клика
                    thumb_rect = pygame.Rect(panel_x + panel_width - 16, scroll_bar_y - 2, 12, scroll_bar_height + 4)
                    self.scroll_thumb_rect = thumb_rect  # Сохраняем для обработки событий
                    pygame.draw.rect(screen, SimpleColors.PRIMARY, thumb_rect, border_radius=4)
            
            # Создаем поверхность для обрезки (clipping) элементов - корректируем область
            content_rect = pygame.Rect(panel_x, 50, panel_width, panel_height - 20)
            
            # Сохраняем текущую область обрезки
            original_clip = screen.get_clip()
            screen.set_clip(content_rect)
            
            # Смещение для скролла
            scroll_y = -self.scroll_offset
            
            # Рисуем все слайдеры, кнопки, разделители с учетом скролла (кроме комбобоксов)
            for separator in self.separators.values():
                # Временно смещаем элемент для отрисовки
                original_y = separator.y
                original_rect_y = separator.rect.y
                separator.y += scroll_y
                separator.rect.y += scroll_y
                
                # Рисуем только если элемент видим
                if content_rect.top <= separator.y + separator.height <= content_rect.bottom:
                    separator.draw(screen, None)
                
                # Возвращаем оригинальные позиции
                separator.y = original_y
                separator.rect.y = original_rect_y
                
            # Рисуем метки
            for label in self.labels.values():
                # Временно смещаем элемент для отрисовки
                original_y = label.y
                original_rect_y = label.rect.y
                label.y += scroll_y
                label.rect.y += scroll_y
                
                # Рисуем только если элемент видим
                if content_rect.top <= label.y + label.height <= content_rect.bottom:
                    label.draw(screen, None)
                
                # Возвращаем оригинальные позиции
                label.y = original_y
                label.rect.y = original_rect_y
                
            for slider in self.sliders.values():
                # Временно смещаем элемент для отрисовки
                original_y = slider.y
                original_rect_y = slider.rect.y
                slider.y += scroll_y
                slider.rect.y += scroll_y
                
                # Рисуем только если элемент видим
                if content_rect.top <= slider.y + 25 <= content_rect.bottom:
                    slider.draw(screen, None)
                
                # Возвращаем оригинальные позиции
                slider.y = original_y
                slider.rect.y = original_rect_y
                
            for button in self.buttons.values():
                # Временно смещаем элемент для отрисовки
                original_y = button.y
                button.y += scroll_y
                button.rect.y += scroll_y
                
                # Рисуем только если элемент видим
                if content_rect.top <= button.y + button.height <= content_rect.bottom:
                    button.draw(screen, None)
                
                # Возвращаем оригинальную позицию
                button.y = original_y
                button.rect.y = original_y
            
            # Рисуем комбобоксы с учетом обрезки, но позволяем выпадающим спискам выходить за границы
            # Сначала рисуем все закрытые комбобоксы с обрезкой
            for combobox in self.comboboxes.values():
                if not combobox.expanded:  # Только закрытые
                    # Временно смещаем элемент для отрисовки
                    original_y = combobox.y
                    original_rect_y = combobox.rect.y
                    combobox.y += scroll_y
                    combobox.rect.y += scroll_y
                    
                    # Рисуем только если элемент видим в области содержимого
                    if content_rect.top <= combobox.y + 30 <= content_rect.bottom:
                        combobox.draw(screen, None)
                    
                    # Возвращаем оригинальные позиции
                    combobox.y = original_y
                    combobox.rect.y = original_rect_y
            
            # Восстанавливаем область обрезки для основных элементов
            screen.set_clip(original_clip)
            
            # Затем рисуем все открытые комбобоксы поверх всех остальных БЕЗ обрезки
            for combobox in self.comboboxes.values():
                if combobox.expanded:  # Только открытые
                    # Временно смещаем элемент для отрисовки
                    original_y = combobox.y
                    original_rect_y = combobox.rect.y
                    combobox.y += scroll_y
                    combobox.rect.y += scroll_y
                    
                    # Проверяем, что основная часть комбобокса видна
                    if content_rect.top <= combobox.y + 30 <= content_rect.bottom + 100:
                        # Рисуем комбобокс без ограничений области видимости для выпадающих списков
                        combobox.draw(screen, None)
                    
                    # Возвращаем оригинальные позиции
                    combobox.y = original_y
                    combobox.rect.y = original_rect_y


# -------------------- Помощник формирования цвета клетки --------------------

def build_color_image(layer_grid: np.ndarray, layer_age: np.ndarray, mode: str,
                      rms: float, pitch: float, cfg: Dict[str, Any],
                      age_palette: str, rms_palette: str, rms_mode: str = "brightness") -> np.ndarray:
    H, W = layer_grid.shape
    # Временно возвращаемся к RGB (3 канала) для отладки
    img = np.zeros((H, W, 3), dtype=np.uint8)

    rms_strength = cfg.get('rms_strength', 100) / 100.0
    fade_start   = cfg.get('fade_start', 60)
    max_age      = cfg.get('max_age', 120)
    sat_drop     = cfg.get('fade_sat_drop', 70)
    val_drop     = cfg.get('fade_val_drop', 60)
    v_mul        = cfg.get('global_v_mul', 1.0)
    cmin         = cfg.get('color_rms_min', DEFAULT_COLOR_RMS_MIN)
    cmax         = cfg.get('color_rms_max', DEFAULT_COLOR_RMS_MAX)

    # быстрый проход по True-ячейкам
    ys, xs = np.nonzero(layer_grid)
    for i, j in zip(ys, xs):
        if mode == "Только RMS":
            color = color_from_rms(rms, rms_palette, cmin, cmax, v_mul)
        elif mode == "Высота ноты (Pitch)":
            color = color_from_pitch(pitch, rms, rms_strength, v_mul)
        else:
            color = color_from_age_rms(int(layer_age[i, j]), rms, rms_strength,
                                       fade_start, max_age, sat_drop, val_drop,
                                       cmin, cmax, v_mul, age_palette, rms_palette, rms_mode)
        
        # Устанавливаем RGB цвет
        img[i, j] = color
    
    return img


# -------------------- Приложение --------------------

class App:
    def __init__(self, sel: Dict[str, Any]):
        self.sel = sel
        self.W = GRID_W * CELL_SIZE + FIELD_OFFSET_X
        self.H = GRID_H * CELL_SIZE

        pygame.init()
        self.screen = pygame.display.set_mode((self.W + HUD_WIDTH, self.H))  # Добавляем HUD_WIDTH
        pygame.display.set_caption("Guitar Life v13 — Ultimate")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("times new roman,georgia,serif", 16)
        self.hud  = HUD(self.font, self.H, 5)  # Поддерживаем до 5 слоёв в GUI
        self.hud.on_parameter_change = self.on_hud_parameter_change
        self.renderer = RenderManager(GRID_W, GRID_H, CELL_SIZE)

        # слои
        self.layers: List[Layer] = []
        print(f"DEBUG: Creating {sel['layer_count']} layers...")
        
        # Проверяем, используем ли мы конфигурацию слоёв из sel или из app_config.json
        use_config_file = sel.get('layers_different', True) and ('layers_cfg' not in sel or not sel['layers_cfg'])
        
        for i in range(sel['layer_count']):
            grid = np.zeros((GRID_H, GRID_W), dtype=bool)
            age = np.zeros((GRID_H, GRID_W), dtype=np.int32)
            
            # Проверяем размеры сетки
            if grid.shape != (GRID_H, GRID_W):
                print(f"ERROR: Layer {i} grid has wrong shape: {grid.shape}, expected: ({GRID_H}, {GRID_W})")
            
            # Добавляем начальные клетки для каждого слоя
            print(f"DEBUG: Adding initial cells to layer {i}...")
            # Создаем только стабильные блоки 2x2
            cells_added = 0
            for _ in range(5):  # 5 блоков на слой
                r = random.randrange(5, GRID_H - 5)
                c = random.randrange(5, GRID_W - 5)
                # Создаем блок 2x2
                grid[r:r+2, c:c+2] = True
                age[r:r+2, c:c+2] = 1
                cells_added += 4
            
            print(f"DEBUG: Layer {i} created with {cells_added} initial cells")
            
            # Определяем параметры слоя
            if use_config_file:
                # Используем базовые настройки, они будут перезаписаны apply_different_layer_settings()
                layer_params = {
                    'rule': 'Conway',
                    'age_palette': 'Blue->Green->Yellow->Red',
                    'rms_palette': 'Fire',
                    'color_mode': 'age',
                    'rms_mode': 'brightness',
                    'alpha_live': 255,
                    'alpha_old': 255,
                    'mix': 'Normal',
                    'solo': False,
                    'mute': False
                }
            else:
                # Используем конфигурацию из sel['layers_cfg']
                row = sel['layers_cfg'][i]
                layer_params = {
                    'rule': row['rule'],
                    'age_palette': row['age_palette'],
                    'rms_palette': row['rms_palette'],
                    'color_mode': row['color_mode'],
                    'rms_mode': row.get('rms_mode', 'brightness'),
                    'alpha_live': row['alpha_live'],
                    'alpha_old': row['alpha_old'],
                    'mix': row['mix'],
                    'solo': row['solo'],
                    'mute': row['mute']
                }
            
            layer = Layer(
                grid=grid,
                age=age,
                **layer_params
            )
            self.layers.append(layer)
            print(f"DEBUG: Layer {i} added with solo={layer.solo}, mute={layer.mute}")

        print(f"DEBUG: Total {len(self.layers)} layers created")

        # FX
        self.fx = dict(sel.get('fx', {}))

        # слои
        self.layers_different = sel.get('layers_different', True)

        # тайминги
        self.tick_ms = sel.get('tick_ms', DEFAULT_TICK_MS)
        self.pitch_tick_enable = sel.get('pitch_tick_enable', False)
        self.pitch_tick_min = sel.get('pitch_tick_min_ms', DEFAULT_PTICK_MIN_MS)
        self.pitch_tick_max = sel.get('pitch_tick_max_ms', DEFAULT_PTICK_MAX_MS)
        self.last_tick = pygame.time.get_ticks()

        # цвет/возраст
        self.max_age = sel.get('max_age', 120)
        self.fade_start = sel.get('fade_start', 60)
        self.fade_sat_drop = sel.get('fade_sat_drop', 70)
        self.fade_val_drop = sel.get('fade_val_drop', 60)
        self.color_rms_min = sel.get('color_rms_min', DEFAULT_COLOR_RMS_MIN)
        self.color_rms_max = sel.get('color_rms_max', DEFAULT_COLOR_RMS_MAX)
        self.rms_strength  = sel.get('rms_strength', 100)
        self.gain = sel.get('gain', 2.5)  # Audio gain multiplier

        # soft clear
        self.soft_clear_enable = sel.get('soft_clear_enable', True)
        self.soft_mode = sel.get('soft_mode', 'Удалять клетки')
        self.soft_kill_rate = sel.get('soft_kill_rate', 80)
        self.soft_fade_floor = sel.get('soft_fade_floor', 0.3)
        self.soft_fade_down  = sel.get('soft_fade_down', 1)
        self.soft_fade_up    = sel.get('soft_fade_up', 5)
        
        # Новые параметры контроля популяции
        self.max_cells_percent = sel.get('max_cells_percent', 50)  # Максимальный процент заполнения сетки
        self.soft_clear_threshold = sel.get('soft_clear_threshold', 70)  # При каком проценте начинать очистку
        self.age_bias = sel.get('age_bias', 80)  # Вероятность удаления старых клеток vs случайных

        # зеркала
        self.mirror_x = sel.get('mirror_x', False)
        self.mirror_y = sel.get('mirror_y', False)

        # авто-циклы
        self.auto_rule_sec = sel.get('auto_rule_sec', 0)
        self.auto_palette_sec = sel.get('auto_palette_sec', 0)
        self._auto_rule_t0 = time.time()
        self._auto_pal_t0  = time.time()

        self.global_v_mul = 1.0
        
        # Применяем настройки палитр из GUI к глобальному состоянию
        PALETTE_STATE.rms_palette_choice = sel.get('palette', 'Blue->Green->Yellow->Red')
        PALETTE_STATE.age_palette_choice = sel.get('age_palette', 'Blue->Green->Yellow->Red')
        print(f"DEBUG: Applied GUI palette settings - RMS: {PALETTE_STATE.rms_palette_choice}, Age: {PALETTE_STATE.age_palette_choice}")
        
        # Отладка: проверяем инициализацию
        total_cells = sum(np.sum(L.grid) for L in self.layers)
        print(f"DEBUG: Initialized {len(self.layers)} layers with {total_cells} total seed cells")
        
        # Обновляем HUD после инициализации
        self.hud.update_from_app(self)

    # ---------- хоткей-пресет ----------
    def apply_joy_division(self):
        self.fx['scanlines'] = True
        self.fx['scan_strength'] = 0.35
        self.fx['posterize'] = True
        self.fx['poster_levels'] = 5
        PALETTE_STATE.invert = False
        PALETTE_STATE.hue_offset = 0.0
        for L in self.layers:
            L.age_palette = "White->LightGray->Gray->DarkGray"
            L.rms_palette = "White->LightGray->Gray->DarkGray"

    def on_hud_parameter_change(self, param_name: str, value):
        """Обработчик изменений параметров из HUD"""
        # Более информативный вывод
        if param_name.startswith('fx_'):
            fx_name = param_name[3:]
            status = "ON" if value else "OFF"
            print(f"🎨 FX {fx_name.upper()}: {status}")
        elif isinstance(value, bool):
            status = "✓" if value else "✗"
            print(f"⚙️ {param_name}: {status}")
        else:
            print(f"🎛️ {param_name}: {value}")
        
        # Обновляем параметры приложения
        if param_name == 'tick_ms':
            self.tick_ms = int(value)
        elif param_name == 'rms_strength':
            self.rms_strength = int(value)
        elif param_name == 'gain':
            global audio_gain
            self.gain = float(value)
            audio_gain = self.gain  # Update global variable for audio callback
        elif param_name == 'max_age':
            self.max_age = int(value)
        elif param_name == 'fade_start':
            self.fade_start = int(value)
        elif param_name == 'clear_rms':
            self.sel['clear_rms'] = float(value)
        elif param_name == 'color_rms_min':
            self.color_rms_min = float(value)
        elif param_name == 'color_rms_max':
            self.color_rms_max = float(value)
        elif param_name == 'soft_kill_rate':
            self.soft_kill_rate = int(value)
        elif param_name == 'soft_fade_floor':
            self.soft_fade_floor = float(value)
        elif param_name == 'max_cells_percent':
            self.max_cells_percent = int(value)
        elif param_name == 'soft_clear_threshold':
            self.soft_clear_threshold = int(value)
        elif param_name == 'age_bias':
            self.age_bias = int(value)
        elif param_name == 'pitch_tick_min':
            self.pitch_tick_min = int(value)
        elif param_name == 'pitch_tick_max':
            self.pitch_tick_max = int(value)
            
        # Булевые параметры
        elif param_name == 'pitch_tick_enable':
            self.pitch_tick_enable = bool(value)
        elif param_name == 'rms_modulation':
            # Добавляем поддержку RMS модуляции если ее нет
            self.rms_modulation = bool(value)
        elif param_name == 'soft_clear_enable':
            self.soft_clear_enable = bool(value)
        elif param_name == 'soft_mode_toggle':
            self.soft_mode = 'Затухание клеток' if value else 'Удалять клетки'
        elif param_name == 'mirror_x':
            self.mirror_x = bool(value)
        elif param_name == 'mirror_y':
            self.mirror_y = bool(value)
            
        # FX параметры
        elif param_name.startswith('fx_'):
            fx_name = param_name[3:]  # Убираем префикс 'fx_'
            self.fx[fx_name] = bool(value)
            
        # Действия
        elif param_name == 'random':
            self.generate_random_patterns()
        elif param_name == 'clear':
            self.clear_all_layers()
        elif param_name == 'test':
            self.create_test_pattern()
        elif param_name == 'reset_defaults':
            self.reset_to_defaults()
        elif param_name == 'joy_division':
            self.apply_joy_division()
            # Для Joy Division нужно обновить HUD так как он меняет много параметров
            self.hud.update_from_app(self)
            
        # Палитры для отдельных слоев
        elif param_name.startswith('layer_') and '_age_palette' in param_name:
            # Извлекаем номер слоя из имени параметра
            layer_idx = int(param_name.split('_')[1])
            if layer_idx < len(self.layers):
                self.layers[layer_idx].age_palette = str(value)
                print(f"🎨 Layer {layer_idx+1} Age Palette changed to: {value}")
                self.save_layer_settings()  # Сохраняем настройки
        elif param_name.startswith('layer_') and '_rms_palette' in param_name:
            # Извлекаем номер слоя из имени параметра
            layer_idx = int(param_name.split('_')[1])
            if layer_idx < len(self.layers):
                self.layers[layer_idx].rms_palette = str(value)
                print(f"🎨 Layer {layer_idx+1} RMS Palette changed to: {value}")
                self.save_layer_settings()  # Сохраняем настройки
        elif param_name.startswith('layer_') and '_rms_mode' in param_name:
            # Извлекаем номер слоя из имени параметра
            layer_idx = int(param_name.split('_')[1])
            if layer_idx < len(self.layers):
                # Преобразуем UI значение в внутреннее
                rms_mode = "brightness" if value == "Brightness" else "palette"
                self.layers[layer_idx].rms_mode = rms_mode
                print(f"🔊 Layer {layer_idx+1} RMS Mode changed to: {value}")
                self.save_layer_settings()  # Сохраняем настройки
                
        # Обработка кнопок для отдельных слоев (Solo/Mute/Rule)
        elif param_name.startswith('layer_') and '_solo' in param_name:
            layer_idx = int(param_name.split('_')[1])
            if layer_idx < len(self.layers):
                # Переключаем solo режим
                self.layers[layer_idx].solo = not self.layers[layer_idx].solo
                # Если включили solo, выключаем у всех остальных
                if self.layers[layer_idx].solo:
                    for i, layer in enumerate(self.layers):
                        if i != layer_idx:
                            layer.solo = False
                print(f"🎯 Layer {layer_idx+1} Solo: {'ON' if self.layers[layer_idx].solo else 'OFF'}")
                self.save_layer_settings()  # Сохраняем настройки
                self.hud.update_from_app(self)
        elif param_name.startswith('layer_') and '_mute' in param_name:
            layer_idx = int(param_name.split('_')[1])
            if layer_idx < len(self.layers):
                self.layers[layer_idx].mute = not self.layers[layer_idx].mute
                print(f"🔇 Layer {layer_idx+1} Mute: {'ON' if self.layers[layer_idx].mute else 'OFF'}")
                self.save_layer_settings()  # Сохраняем настройки
                self.hud.update_from_app(self)
            
        # Параметры эффектов
        elif param_name == 'trail_strength':
            self.fx['trail_strength'] = float(value)
        elif param_name == 'blur_scale':
            self.fx['blur_scale'] = int(value)
        elif param_name == 'bloom_strength':
            self.fx['bloom_strength'] = float(value)
        elif param_name == 'poster_levels':
            self.fx['poster_levels'] = int(value)
        elif param_name == 'scan_strength':
            self.fx['scan_strength'] = float(value)
        elif param_name == 'pixel_block':
            self.fx['pixel_block'] = int(value)
        elif param_name == 'outline_thick':
            self.fx['outline_thick'] = int(value)
            
        # Редактор слоев
        elif param_name == 'layer_count':
            self.change_layer_count(int(value))
        elif param_name == 'layers_different':
            self.layers_different = bool(value)
            if value:
                # Logic for different layers would be here if needed
                pass
        # Прозрачность слоев
        elif param_name.startswith('layer_') and param_name.endswith('_alpha'):
            layer_index = int(param_name.split('_')[1])  # layer_idx уже правильный индекс
            if 0 <= layer_index < len(self.layers):
                # Используем новое свойство alpha для установки обоих значений
                self.layers[layer_index].alpha = int(value)
        elif param_name == 'auto_rule_sec':
            self.auto_rule_sec = int(value)
        elif param_name == 'auto_palette_sec':
            self.auto_palette_sec = int(value)
        elif param_name.startswith('layer_') and '_solo' in param_name:
            layer_idx = int(param_name.split('_')[1])
            if layer_idx < len(self.layers):
                self.layers[layer_idx].solo = bool(value)
                print(f"🎭 Layer {layer_idx + 1} Solo: {'ON' if value else 'OFF'}")
        elif param_name.startswith('layer_') and '_mute' in param_name:
            layer_idx = int(param_name.split('_')[1])
            if layer_idx < len(self.layers):
                self.layers[layer_idx].mute = bool(value)
                print(f"🔇 Layer {layer_idx + 1} Mute: {'ON' if value else 'OFF'}")
        elif param_name.startswith('layer_') and '_rule' in param_name:
            layer_idx = int(param_name.split('_')[1])
            if layer_idx < len(self.layers):
                self.cycle_layer_rule(layer_idx)

    def change_layer_count(self, new_count: int):
        """Изменяет количество слоев"""
        new_count = max(1, min(5, new_count))  # Ограничиваем от 1 до 5 слоев
        current_count = len(self.layers)
        
        if new_count > current_count:
            # Загружаем настройки из конфигурации
            try:
                with open('app_config.json', 'r', encoding='utf-8') as f:
                    config = json.load(f)
                layer_settings = config.get('layers', {}).get('layer_settings', [])
            except:
                layer_settings = []
                
            # Добавляем новые слои
            for i in range(current_count, new_count):
                grid = np.zeros((GRID_H, GRID_W), dtype=bool)
                age = np.zeros((GRID_H, GRID_W), dtype=np.int32)
                
                # Добавляем начальные клетки
                for _ in range(5):
                    r = random.randrange(5, GRID_H - 5)
                    c = random.randrange(5, GRID_W - 5)
                    grid[r:r+2, c:c+2] = True
                    age[r:r+2, c:c+2] = 1
                
                # Получаем настройки для слоя из конфигурации или используем defaults
                if i < len(layer_settings):
                    settings = layer_settings[i]
                    rule = settings.get('rule', 'Conway')
                    age_palette = settings.get('age_palette', 'Blue->Green->Yellow->Red')
                    rms_palette = settings.get('rms_palette', 'Fire')
                    solo = settings.get('solo', False)
                    mute = settings.get('mute', False)
                else:
                    # Fallback: выбираем правило и палитры в зависимости от настроек
                    rules = ["Conway", "HighLife", "Day&Night", "Replicator", "Seeds", "Maze", "Coral"]
                    palettes = ["Blue->Green->Yellow->Red", "Fire", "Ocean", "Neon", "Ukraine"]
                    
                    rule = rules[i % len(rules)] if getattr(self, 'layers_different', True) else self.layers[0].rule if self.layers else "Conway"
                    age_palette = palettes[i % len(palettes)] if getattr(self, 'layers_different', True) else self.layers[0].age_palette if self.layers else "Blue->Green->Yellow->Red"
                    rms_palette = palettes[(i+1) % len(palettes)] if getattr(self, 'layers_different', True) else self.layers[0].rms_palette if self.layers else "Blue->Green->Yellow->Red"
                    solo = False
                    mute = False
                
                self.layers.append(Layer(
                    grid=grid, age=age, rule=rule,
                    age_palette=age_palette, rms_palette=rms_palette,
                    color_mode="Возраст + RMS", rms_mode="brightness", alpha_live=220, alpha_old=140,
                    mix="Normal", solo=solo, mute=mute
                ))
                print(f"➕ Added Layer {i + 1}: {rule}, {age_palette} + {rms_palette} (solo={solo}, mute={mute})")
                
        elif new_count < current_count:
            # Удаляем лишние слои
            removed_layers = self.layers[new_count:]
            self.layers = self.layers[:new_count]
            print(f"➖ Removed {len(removed_layers)} layers")
        
        # Обновляем HUD
        self.hud.update_from_app(self)
        
    def save_layer_settings(self):
        """Сохраняет настройки слоев в app_config.json"""
        try:
            # Загружаем текущую конфигурацию
            try:
                with open('app_config.json', 'r', encoding='utf-8') as f:
                    config = json.load(f)
            except:
                config = {"layers": {}}
                
            # Обновляем настройки слоев
            if "layers" not in config:
                config["layers"] = {}
                
            config["layers"]["layer_count"] = len(self.layers)
            config["layers"]["layer_settings"] = []
            
            for i, layer in enumerate(self.layers):
                layer_config = {
                    "rule": layer.rule,
                    "age_palette": layer.age_palette,
                    "rms_palette": layer.rms_palette,
                    "solo": layer.solo,
                    "mute": layer.mute,
                    "alpha_live": layer.alpha_live,
                    "alpha_old": layer.alpha_old,
                    "alpha": layer.alpha  # Добавляем общее значение alpha
                }
                config["layers"]["layer_settings"].append(layer_config)
            
            # Сохраняем конфигурацию
            with open('app_config.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
                
            print(f"💾 Layer settings saved to app_config.json")
            
        except Exception as e:
            print(f"❌ Error saving layer settings: {e}")
    
    def apply_different_layer_settings(self):
        """Применяет разные настройки для каждого слоя на основе конфигурации"""
        print("🔧 DEBUG: Applying layer settings from app_config.json...")
        try:
            # Загружаем настройки из конфигурации
            with open('app_config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            layer_settings = config.get('layers', {}).get('layer_settings', [])
            print(f"🔧 DEBUG: Found {len(layer_settings)} layer settings in config")
            
            # Применяем настройки из конфигурации
            for i, layer in enumerate(self.layers):
                if i < len(layer_settings):
                    settings = layer_settings[i]
                    old_age_palette = layer.age_palette
                    old_rms_palette = layer.rms_palette
                    
                    layer.rule = settings.get('rule', 'Conway')
                    layer.age_palette = settings.get('age_palette', 'Blue->Green->Yellow->Red')
                    layer.rms_palette = settings.get('rms_palette', 'Fire')
                    layer.solo = settings.get('solo', False)
                    layer.mute = settings.get('mute', False)
                    
                    # Загружаем alpha - сначала пытаемся загрузить общее значение, 
                    # если его нет, то используем отдельные alpha_live и alpha_old
                    if 'alpha' in settings:
                        layer.alpha = settings['alpha']
                    else:
                        layer.alpha_live = settings.get('alpha_live', 220)
                        layer.alpha_old = settings.get('alpha_old', 140)
                    
                    print(f"🎨 Layer {i}: {layer.rule}, age: {old_age_palette} -> {layer.age_palette}, rms: {old_rms_palette} -> {layer.rms_palette} (solo={layer.solo}, mute={layer.mute})")
                else:
                    # Fallback для слоев без настроек
                    default_rules = ["Conway", "HighLife", "Day&Night", "Replicator", "Seeds", "Maze", "Coral"]
                    default_age_palettes = [
                        "Blue->Green->Yellow->Red", "White->LightGray->Gray->DarkGray", "BrightRed->DarkRed->DarkGray->Black", "Fire", "Ocean", "Neon", "Ukraine",
                        "Rainbow", "Sunset", "Pastel", "Viridis", "Inferno", "Magma", "Plasma", "Cividis", "Twilight", "Spring", "Summer", "Autumn", "Winter",
                        "Ice", "Forest", "Desert", "Candy", "Retro", "Cyberpunk", "Gold", "Silver", "Copper", "Emerald", "Sapphire", "Ruby", "Amethyst",
                        "Lime", "Mint", "Peach", "Lavender", "Rose", "Sky", "Sand", "Charcoal", "Steel", "Bronze", "Pearl", "Coral", "Jade", "Topaz",
                        "Galaxy", "Aurora", "Tropical", "Vintage", "Monochrome", "Sepia", "HighContrast", "LowContrast", "DeepSea", "Volcano", "Clouds", "Flame"
                    ]
                    default_rms_palettes = [
                        "Blue->Red", "Blue->Green->Yellow->Red", "White->LightGray->Gray->DarkGray", "BrightRed->DarkRed->DarkGray->Black", "Fire", "Ocean", "Neon", "Ukraine",
                        "Rainbow", "Sunset", "Pastel", "Viridis", "Inferno", "Magma", "Plasma", "Cividis", "Twilight", "Spring", "Summer", "Autumn", "Winter",
                        "Ice", "Forest", "Desert", "Candy", "Retro", "Cyberpunk", "Gold", "Silver", "Copper", "Emerald", "Sapphire", "Ruby", "Amethyst",
                        "Lime", "Mint", "Peach", "Lavender", "Rose", "Sky", "Sand", "Charcoal", "Steel", "Bronze", "Pearl", "Coral", "Jade", "Topaz",
                        "Galaxy", "Aurora", "Tropical", "Vintage", "Monochrome", "Sepia", "HighContrast", "LowContrast", "DeepSea", "Volcano", "Clouds", "Flame"
                    ]
                    
                    layer.rule = default_rules[i % len(default_rules)]
                    layer.age_palette = default_age_palettes[i % len(default_age_palettes)]
                    layer.rms_palette = default_rms_palettes[i % len(default_rms_palettes)]
                    layer.solo = False
                    layer.mute = False
                    print(f"🎨 Layer {i}: using defaults - {layer.rule}, {layer.age_palette} + {layer.rms_palette}")
                    
        except Exception as e:
            print(f"❌ Error loading layer settings: {e}")
            
        print("🔧 DEBUG: Layer settings applied successfully")
        
        self.hud.update_from_app(self)
    
    def apply_same_layer_settings(self):
        """Применяет одинаковые настройки для всех слоев"""
        if not self.layers:
            return
            
        base_layer = self.layers[0]
        for layer in self.layers[1:]:
            layer.rule = base_layer.rule
            layer.age_palette = base_layer.age_palette
            layer.rms_palette = base_layer.rms_palette
        
        print("🔄 Applied same settings to all layers")
        self.hud.update_from_app(self)
    
    def cycle_layer_rule(self, layer_idx: int):
        """Циклично меняет правило для конкретного слоя"""
        if layer_idx >= len(self.layers):
            return
            
        rules = ["Conway", "HighLife", "Day&Night", "Replicator", "Seeds", "Maze", "Coral", "LifeWithoutDeath", "Gnarl"]
        current_rule = self.layers[layer_idx].rule
        
        try:
            current_idx = rules.index(current_rule)
            new_idx = (current_idx + 1) % len(rules)
        except ValueError:
            new_idx = 0
        
        new_rule = rules[new_idx]
        self.layers[layer_idx].rule = new_rule
        
        # Обновляем текст кнопки в HUD
        if f'layer_{layer_idx}_rule' in self.hud.buttons:
            self.hud.buttons[f'layer_{layer_idx}_rule'].label = new_rule[:7]  # Сокращаем для экономии места
        
        print(f"🔄 Layer {layer_idx + 1} rule changed to: {new_rule}")

    def generate_random_patterns(self):
        """Генерирует случайные стабильные паттерны"""
        print("DEBUG: Generating stable life patterns...")
        for L in self.layers:
            L.grid[:] = False  
            L.age[:] = 0
            
            stable_patterns = [
                [(0,0), (0,1), (1,0), (1,1)],  # Блок
                [(0,1), (0,2), (1,0), (1,3), (2,1), (2,2)],  # Улей
                [(1,0), (1,1), (1,2)],  # Блинкер
                [(0,1), (0,2), (0,3), (1,0), (1,1), (1,2)],  # Жаба
                [(0,1), (0,2), (1,0), (1,1), (2,1)]  # R-пентомино
            ]
            
            for _ in range(15):
                pattern = random.choice(stable_patterns)
                cr = random.randrange(5, GRID_H - 10)
                cc = random.randrange(5, GRID_W - 10)
                for dr, dc in pattern:
                    r, c = cr + dr, cc + dc
                    if 0 <= r < GRID_H and 0 <= c < GRID_W:
                        L.grid[r, c] = True
                        L.age[r, c] = 1
        total = sum(np.sum(L.grid) for L in self.layers)
        print(f"DEBUG: Generated {total} cells in stable patterns")

    def clear_all_layers(self):
        """Очищает все слои"""
        for L in self.layers:
            L.grid[:] = False
            L.age[:] = 0
        print("DEBUG: Cleared all layers")

    def create_test_pattern(self):
        """Создает тестовый паттерн (блок 2x2)"""
        print("DEBUG: Testing stable 2x2 block...")
        for L in self.layers:
            L.grid[:] = False
            L.age[:] = 0
            center_r, center_c = GRID_H // 2, GRID_W // 2
            L.grid[center_r:center_r+2, center_c:center_c+2] = True
            L.age[center_r:center_r+2, center_c:center_c+2] = 1
        print("DEBUG: Created 2x2 test block")

    def reset_to_defaults(self):
        """Сбрасывает все параметры к значениям по умолчанию"""
        print("🔄 Сброс параметров к значениям по умолчанию")
        
        # Основные параметры
        self.tick_ms = DEFAULT_TICK_MS
        self.rms_strength = 100
        self.max_age = 120
        self.fade_start = 60
        self.sel['clear_rms'] = DEFAULT_CLEAR_RMS
        self.color_rms_min = DEFAULT_COLOR_RMS_MIN
        self.color_rms_max = DEFAULT_COLOR_RMS_MAX
        self.soft_kill_rate = 80
        self.soft_fade_floor = 0.3
        self.max_cells_percent = 50  # Максимальный процент заполнения сетки
        self.soft_clear_threshold = 70  # При каком проценте начинать очистку
        self.age_bias = 80  # Вероятность удаления старых клеток vs случайных
        self.pitch_tick_min = DEFAULT_PTICK_MIN_MS
        self.pitch_tick_max = DEFAULT_PTICK_MAX_MS
        
        # Булевые параметры
        self.pitch_tick_enable = False
        self.rms_modulation = True
        self.soft_clear_enable = True
        self.soft_mode = 'Удалять клетки'
        self.mirror_x = False
        self.mirror_y = False
        
        # FX эффекты
        self.fx = {
            'trails': True,
            'blur': False,
            'bloom': False,
            'posterize': False,
            'dither': False,
            'scanlines': False,
            'pixelate': False,
            'outline': False
        }
        
        # Палитра
        PALETTE_STATE.hue_offset = 0.0
        PALETTE_STATE.invert = False
        
        # Обновляем HUD
        self.hud.update_from_app(self)
        print("✅ Параметры сброшены")

    # ---------- внутренняя логика ----------
    def maybe_tick_interval(self, pitch_hz: float) -> int:
        if not self.pitch_tick_enable or pitch_hz <= 0:
            return self.tick_ms
        # логарифмическая проекция частоты в интервал тика
        p = np.clip((math.log2(pitch_hz) - math.log2(80.0)) /
                    (math.log2(1500.0) - math.log2(80.0)), 0.0, 1.0)
        return int(self.pitch_tick_max + (self.pitch_tick_min - self.pitch_tick_max) * p)

    def soft_clear(self):
        if not self.soft_clear_enable:
            return
        if self.soft_mode == "Удалять клетки":
            for L in self.layers:
                g = L.grid
                if not g.any(): continue
                alive = np.argwhere(g)
                k = int(len(alive) * self.soft_kill_rate / 100.0)
                if k > 0:
                    pick = alive[np.random.choice(len(alive), size=k, replace=False)]
                    g[pick[:, 0], pick[:, 1]] = False
        else:
            # мягкое затухание яркости
            self.global_v_mul = max(self.soft_fade_floor,
                                    self.global_v_mul * (1.0 - self.soft_fade_down / 100.0))

    def soft_population_control(self):
        """Универсальная мягкая система контроля популяции для всех правил"""
        if not self.soft_clear_enable:
            return
            
        total_grid_size = GRID_H * GRID_W
        max_allowed_cells = int(total_grid_size * self.max_cells_percent / 100.0)
        clear_threshold_cells = int(total_grid_size * self.soft_clear_threshold / 100.0)
        
        for i, L in enumerate(self.layers):
            total_cells = np.sum(L.grid)
            
            if total_cells > clear_threshold_cells:
                # Вычисляем сколько клеток нужно удалить
                excess_ratio = min(1.0, (total_cells - max_allowed_cells) / max_allowed_cells)
                removal_rate = max(5, int(self.soft_kill_rate * excess_ratio / 100.0))
                
                alive_positions = np.where(L.grid)
                if len(alive_positions[0]) == 0:
                    continue
                    
                ages = L.age[alive_positions]
                
                # Умное удаление: комбинируем возраст и случайность
                if self.age_bias > np.random.randint(0, 100):
                    # Удаляем по возрасту (старые клетки)
                    sorted_indices = np.argsort(ages)[::-1]  # Сортировка от старых к молодым
                else:
                    # Случайное удаление
                    sorted_indices = np.random.permutation(len(ages))
                
                num_to_remove = min(removal_rate, len(alive_positions[0]))
                if num_to_remove > 0:
                    remove_indices = sorted_indices[:num_to_remove]
                    remove_r = alive_positions[0][remove_indices]
                    remove_c = alive_positions[1][remove_indices]
                    
                    if self.soft_mode == "Удалять клетки":
                        # Мгновенное удаление
                        L.grid[remove_r, remove_c] = False
                        L.age[remove_r, remove_c] = 0
                    else:
                        # Мягкое затухание через уменьшение возраста
                        L.age[remove_r, remove_c] = np.maximum(0, L.age[remove_r, remove_c] - 10)
                        # Удаляем клетки с нулевым возрастом
                        zero_age_mask = L.age == 0
                        L.grid[zero_age_mask] = False

    def soft_recover(self):
        self.global_v_mul = min(1.0, self.global_v_mul * (1.0 + self.soft_fade_up / 100.0))

    def update_layers(self, births: int):
        # распределение рождений по слоям
        if births > 0 and self.layers:
            per = max(1, births // len(self.layers))
            for i, L in enumerate(self.layers):
                spawn_cells(L.grid, per)

        for i, L in enumerate(self.layers):
            L.age[L.grid] += 1
            L.age[~L.grid] = 0
            L.grid = step_life(L.grid, L.rule)
            
            # ИСПРАВЛЕНИЕ: Принудительно очищаем края сетки для предотвращения 
            # визуального "выползания" клеток при масштабировании
            L.grid[0, :] = False    # Верхний край
            L.grid[-1, :] = False   # Нижний край
            L.grid[:, 0] = False    # Левый край
            L.grid[:, -1] = False   # Правый край
            
            # Проверяем размеры после step_life
            if L.grid.shape != (GRID_H, GRID_W):
                print(f"ERROR: Layer {i} grid shape changed to {L.grid.shape} after step_life")
            
            # Проверим координаты всех живых клеток
            live_coords = np.where(L.grid)
            if len(live_coords[0]) > 0:
                max_r, max_c = np.max(live_coords[0]), np.max(live_coords[1])
                min_r, min_c = np.min(live_coords[0]), np.min(live_coords[1])
                if max_r >= GRID_H or max_c >= GRID_W or min_r < 0 or min_c < 0:
                    print(f"WARNING: Layer {i} has cells at invalid coords: r=[{min_r}, {max_r}], c=[{min_c}, {max_c}]")
                
                # Проверим клетки на краях (возможная причина визуального "выползания")
                if max_r >= GRID_H-1 or max_c >= GRID_W-1 or min_r <= 0 or min_c <= 0:
                    print(f"EDGE CHECK: Layer {i} has cells near edges: r=[{min_r}, {max_r}], c=[{min_c}, {max_c}]")
            
            if self.mirror_x: L.grid = np.fliplr(L.grid)
            if self.mirror_y: L.grid = np.flipud(L.grid)
        
        # Применяем мягкий контроль популяции для всех слоев
        self.soft_population_control()

    def render(self, rms: float, pitch: float):
        self.renderer.clear(BG_COLOR)
        cfg = dict(
            rms_strength=self.rms_strength,
            fade_start=self.fade_start,
            max_age=self.max_age,
            fade_sat_drop=self.fade_sat_drop,
            fade_val_drop=self.fade_val_drop,
            color_rms_min=self.color_rms_min,
            color_rms_max=self.color_rms_max,
            global_v_mul=self.global_v_mul,
        )

        # Solo/mute
        solos = [L for L in self.layers if L.solo and not L.mute]
        layers = solos if solos else [L for L in self.layers if not L.mute]

        print(f"RENDER DEBUG: Total layers={len(self.layers)}")
        for idx, L in enumerate(self.layers):
            print(f"  Layer {idx}: solo={L.solo}, mute={L.mute}, rule={L.rule}, cells={np.sum(L.grid)}")
        print(f"RENDER DEBUG: Solos found={len(solos)}, Will render={len(layers)} layers")
        
        # Отрисовываем каждый слой
        for i, L in enumerate(layers):
            live_cells = np.sum(L.grid)
            print(f"RENDER DEBUG: Layer {i} ({L.rule}): {live_cells} live cells, solo={L.solo}, mute={L.mute}")
            
            img = build_color_image(L.grid, L.age, L.color_mode, rms, pitch, cfg,
                                    L.age_palette, L.rms_palette, L.rms_mode)
            self.renderer.blit_layer(img, L.mix, L.alpha_live, L.alpha_old)

        frame = self.renderer.canvas

        # FX chain (включаемые опции из GUI)
        if self.fx.get('trails', False):
            apply_trails(frame, float(self.fx.get('trail_strength', 0.06)))
        if self.fx.get('blur', False):
            apply_scale_blur(frame, int(self.fx.get('blur_scale', 2)))
        if self.fx.get('bloom', False):
            apply_bloom(frame, float(self.fx.get('bloom_strength', 0.35)))
        if self.fx.get('posterize', False):
            apply_posterize(frame, int(self.fx.get('poster_levels', 5)))
        if self.fx.get('dither', False):
            apply_dither(frame)
        if self.fx.get('scanlines', False):
            apply_scanlines(frame, float(self.fx.get('scan_strength', 0.25)))
        if self.fx.get('pixelate', False):
            apply_pixelate(frame, int(self.fx.get('pixel_block', 1)))
        if self.fx.get('outline', False):
            apply_outline(frame, int(self.fx.get('outline_thick', 1)))

        self.screen.blit(frame, (0, 0))

    def run(self):
        global audio_gain
        rms = 0.0; pitch = 0.0
        running = True
        
        # Initialize global audio gain for audio callback
        audio_gain = self.gain
        
        # Инициализация HUD с текущими значениями
        print("🔄 DEBUG: Initializing HUD from app state...")
        
        # Применяем настройки из app_config.json если включен режим разных слоев
        if getattr(self, 'layers_different', True):
            self.apply_different_layer_settings()
        
        self.hud.update_from_app(self)
        print(f"🔄 DEBUG: HUD initialized. Layer count: {len(self.layers)}")
        
        # Проверяем, что палитры слоев установлены правильно
        for i, layer in enumerate(self.layers):
            print(f"🎨 DEBUG: Layer {i}: rule={layer.rule}, age={layer.age_palette}, rms={layer.rms_palette}")
        
        
        while running:
            for ev in pygame.event.get():
                # Сначала проверяем события HUD
                if self.hud.handle_event(ev):
                    continue  # Если HUD обработал событие, пропускаем дальнейшую обработку
                    
                if ev.type == pygame.QUIT:
                    running = False
                elif ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_ESCAPE:
                        running = False
                    elif ev.key == pygame.K_h:
                        self.hud.visible = not self.hud.visible
                    elif ev.key == pygame.K_TAB:
                        self.hud.mini_held = True
                    elif ev.key == pygame.K_r:
                        self.generate_random_patterns()
                    elif ev.key == pygame.K_c:
                        self.clear_all_layers()
                    elif ev.key == pygame.K_t:
                        self.create_test_pattern()
                    elif ev.key == pygame.K_F3:
                        self.apply_joy_division()
                        self.hud.update_from_app(self)  # Обновляем HUD после изменений
                    elif ev.key == pygame.K_F1:
                        self.fx['trails'] = not self.fx.get('trails', True)
                        self.hud.update_from_app(self)  # Обновляем HUD после изменений
                    elif ev.key == pygame.K_F2:
                        self.fx['blur'] = not self.fx.get('blur', False)
                        self.hud.update_from_app(self)  # Обновляем HUD после изменений
                elif ev.type == pygame.KEYUP:
                    if ev.key == pygame.K_TAB:
                        self.hud.mini_held = False

            # снять свежие значения аудио
            try:
                while True:
                    pitch = pitch_queue.get_nowait()
                    rms   = rms_queue.get_nowait()
            except queue.Empty:
                pass

            # тик автомата
            now = pygame.time.get_ticks()
            dyn_ms = self.maybe_tick_interval(pitch)
            if now - self.last_tick >= dyn_ms:
                self.last_tick = now
                births = int(SPAWN_BASE + SPAWN_SCALE *
                             clamp01(math.log10(1.0 + VOLUME_SCALE * max(0.0, rms))))
                
                # Отладка: выводим информацию о спавне только при значительном RMS
                if births > 0 and rms > 0.001:
                    print(f"DEBUG: RMS={rms:.4f}, births={births}")
                
                if rms < self.sel.get('clear_rms', DEFAULT_CLEAR_RMS):
                    self.soft_clear()
                else:
                    self.soft_recover()
                self.update_layers(births)
                
                # Отладка: подсчитываем живые клетки после обновления
                total_alive = sum(np.sum(L.grid) for L in self.layers)
                if total_alive > 0:
                    print(f"DEBUG: {total_alive} cells alive after tick")

            # рендер
            self.render(rms, pitch)

            # HUD
            total_alive = sum(np.sum(L.grid) for L in self.layers)
            info = {
                "RMS": f"{rms:.4f}",
                "Pitch": f"{pitch:.1f} Hz" if pitch > 0 else "—",
                "Tick": f"{dyn_ms} ms",
                "Alive": f"{total_alive} cells",
                "Layers": f"{len(self.layers)}",
                "FX": ", ".join([k for k in ['trails','blur','bloom','posterize','dither','scanlines','pixelate','outline']
                                 if self.fx.get(k, False)]) or "none",
            }
            self.hud.draw(self.screen, info)

            pygame.display.flip()
            self.clock.tick(FPS)
        pygame.quit()


# -------------------- Запуск --------------------

def main():
    sel = choose_settings()
    if not sel:
        return
    
    print("🚀 DEBUG: Starting application...")
    print(f"DEBUG: Config layer_count = {sel.get('layer_count', 'not set')}")
    
    stream = start_audio_stream(sel['device'])
    try:
        app = App(sel)
        
        # Быстрая проверка состояния слоев после создания
        print("\n🔍 DEBUG: Layer state after creation:")
        for i, layer in enumerate(app.layers):
            cells = np.sum(layer.grid)
            print(f"  Layer {i}: {cells} cells, solo={layer.solo}, mute={layer.mute}")
        
        # Создаем тестовый паттерн для быстрой проверки
        print("\n📝 DEBUG: Creating test pattern...")
        app.create_test_pattern()
        
        print("🎯 DEBUG: Layer state after test pattern:")
        for i, layer in enumerate(app.layers):
            cells = np.sum(layer.grid)
            print(f"  Layer {i}: {cells} cells, solo={layer.solo}, mute={layer.mute}")
        
        app.run()
    finally:
        try:
            stream.stop(); stream.close()
        except Exception:
            pass


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("Fatal:", e, file=sys.stderr)
