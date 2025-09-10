# === Standard library ===
import sys
import os
import json
import math
import random
import queue

# === Third-party (hard deps) ===
try:
    import numpy as np
except ImportError as e:
    raise SystemExit("NumPy is required. Install with: pip install numpy") from e

try:
    import pygame
except ImportError as e:
    raise SystemExit("pygame is required. Install with: pip install pygame") from e

# === Third-party (soft/optional deps) ===
try:
    import sounddevice as sd  # for audio I/O
except Exception:
    sd = None  # allow running without audio; handle at runtime

# librosa тяжёлая — лучше лениво импортировать в той функции, где реально нужно.
# Если всё же хочешь глобально:
try:
    import librosa  # type: ignore
except Exception:
    librosa = None

import colorsys  # один раз достаточно

# === GUI (optional) ===
# Используй Tk только для коротких модальных диалогов (выбор аудио-устройств),
# и обязательно закрывай окно перед запуском pygame loop.
try:
    import tkinter as tk
    from tkinter import ttk
except Exception:
    tk = None
    ttk = None
# -------------------- Параметры системы/рендера --------------------
SAMPLE_RATE = 44100
BLOCK_SIZE  = 2048
CHANNELS    = 1
FPS         = 60

GRID_W, GRID_H = 120, 70
CELL_SIZE = 8
BG_COLOR  = (10, 10, 12)

HUD_WIDTH = 420  # ширина панели справа
FIELD_OFFSET_X = 0  # если захотите сдвинуть поле влево

SPAWN_BASE, SPAWN_SCALE = 5, 380

# Диапазон частот для спавна/привязки
FREQ_MIN, FREQ_MAX = 70, 1200.0
MIN_NOTE_FREQ = 60.0  # игнор спавна ниже этого
VOLUME_SCALE  = 8.0

# Значения по умолчанию
DEFAULT_CLEAR_RMS        = 0.004
DEFAULT_COLOR_RMS_MIN    = 0.004
DEFAULT_COLOR_RMS_MAX    = 0.30
DEFAULT_TICK_MS          = 120
DEFAULT_PTICK_MIN_MS     = 60
DEFAULT_PTICK_MAX_MS     = 300

# Диапазон высоты для цветового режима по высоте ноты
PITCH_COLOR_MIN_HZ      = 80.0
PITCH_COLOR_MAX_HZ      = 1500.0

PRESET_PATH = "/mnt/data/palette_preset.json"

# Очереди аудио-данных
pitch_queue = queue.Queue(maxsize=8)
rms_queue   = queue.Queue(maxsize=8)
running     = True

# -------------------- Утилиты --------------------
def clamp01(x: float) -> float:
    if x < 0.0: return 0.0
    if x > 1.0: return 1.0
    return x

def lerp(a, b, t): return a + (b - a) * t

# -------------------- Палитры --------------------
def hue_bgyr_from_t(t: float) -> float:
    """Синий(220) → Зелёный(120) → Жёлтый(60) → Красный(0) по t∈[0..1]."""
    t = clamp01(t)
    if t < 1/3:
        return lerp(220.0, 120.0, t*3.0)
    elif t < 2/3:
        return lerp(120.0, 60.0, (t-1/3)*3.0)
    else:
        return lerp(60.0, 0.0, (t-2/3)*3.0)

def hue_br_from_t(t: float) -> float:
    """Синий(220) → Красный(0) линейно."""
    return lerp(220.0, 0.0, clamp01(t))

# -------------------- Возраст/выцветание --------------------
def age_to_t(age: int, max_age: int) -> float:
    if max_age <= 1:
        return 1.0
    k = max(6.0, max_age/6.0)  # мягкая кривая
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

# -------------------- Состояние палитры --------------------
class PaletteState:
    def __init__(self):
        self.hue_offset = 0.0
        self.invert = False
        self.rms_palette_choice = "Blue->Green->Yellow->Red"
        self.age_palette_choice = "Blue->Green->Yellow->Red"

    def randomize(self):
        self.hue_offset = random.uniform(-180.0, 180.0)
        self.invert = random.random() < 0.5
        self.rms_palette_choice = random.choice(["Blue->Red", "Blue->Green->Yellow->Red", "White->LightGray->Gray->DarkGray"])
        self.age_palette_choice = random.choice(["Blue->Green->Yellow->Red", "White->LightGray->Gray->DarkGray"])

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

def save_preset(path: str = PRESET_PATH) -> bool:
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(PALETTE_STATE.to_dict(), f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print("Не удалось сохранить пресет:", e, file=sys.stderr)
        return False

def load_preset(path: str = PRESET_PATH) -> bool:
    try:
        if not os.path.exists(path):
            return False
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        PALETTE_STATE.from_dict(data)
        return True
    except Exception as e:
        print("Не удалось загрузить пресет:", e, file=sys.stderr)
        return False

def apply_hue_offset(hue_deg: float) -> float:
    return (hue_deg + PALETTE_STATE.hue_offset) % 360.0

def maybe_invert_t(t: float) -> float:
    return 1.0 - t if PALETTE_STATE.invert else t



def palette_key(name: str) -> str:
    """Нормализует имя палитры к каноническому ключу."""
    n = (name or "").replace("→","->").strip()
    aliases = {
        "Blue->Green->Yellow->Red": "BGYR",
        "White->LightGray->Gray->DarkGray": "GRAYSCALE",
        "BrightRed->DarkRed->DarkGray->Black": "RED_DARKRED_GRAY_BLACK",
        # HUD alias / короткие названия
        "Red->DarkRed->Gray->Black": "RED_DARKRED_GRAY_BLACK",
        "BGYR": "BGYR",
        "GrayScale": "GRAYSCALE",
    }
    return aliases.get(n, "BGYR")

# -------------------- Цветовые функции --------------------
def norm_rms_for_color(rms: float, color_rms_min: float, color_rms_max: float) -> float:
    """Нормировка RMS для цвета в диапазон [0..1] на основе COLOR_RMS_MIN..MAX."""
    if color_rms_max <= color_rms_min:  # страховка
        color_rms_max = color_rms_min + 1e-6
    return clamp01((rms - color_rms_min) / (color_rms_max - color_rms_min))

def color_from_age_rms(age: int, rms: float, rms_strength: float,
                       fade_start: int, max_age: int,
                       sat_drop_pct: float, val_drop_pct: float,
                       color_rms_min: float, color_rms_max: float,
                       global_v_mul: float,
                       age_palette: str) -> tuple[int,int,int]:
    """
    Цвет по возрасту + модуляция RMS + выцветание + глобальный множитель яркости.
    age_palette: "Blue->Green->Yellow->Red" | "White->LightGray->Gray->DarkGray"
    """
    a = min(age, max_age if max_age>0 else age)
    t_age_raw = age_to_t(a, max_age if max_age>0 else max(12, a+1))
    t_age = maybe_invert_t(t_age_raw)

    t_rms = norm_rms_for_color(rms, color_rms_min, color_rms_max)
    strength = clamp01(rms_strength)

    pal_key = palette_key(age_palette)
    if pal_key == "GRAYSCALE":
        # Базовая яркость от возраста (кусково-линейно)
        if t_age < 1/3:
            v_age = lerp(1.0, 0.8, t_age*3.0)
        elif t_age < 2/3:
            v_age = lerp(0.8, 0.5, (t_age-1/3)*3.0)
        else:
            v_age = lerp(0.5, 0.25, (t_age-2/3)*3.0)
        # Модуляция RMS: подмешиваем 65..100% множитель яркости
        v = v_age * (0.65 + 0.35 * (t_rms * strength)) * clamp01(global_v_mul)
        s = 0.0  # серый
        # Выцветание по возрасту влияет только на яркость (насыщенность 0)
        _, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        v *= val_mul
        g = int(255 * clamp01(v))
        return (g, g, g)

    elif pal_key == "RED_DARKRED_GRAY_BLACK":
        if t_age < 1/3:
            s = 1.0
            v_age = lerp(1.0, 0.65, t_age*3.0)
            hue_deg = 0.0
        elif t_age < 2/3:
            k = (t_age-1/3)*3.0
            s = lerp(1.0, 0.0, k)
            v_age = lerp(0.65, 0.25, k)
            hue_deg = 0.0
        else:
            k = (t_age-2/3)*3.0
            s = 0.0
            v_age = lerp(0.25, 0.0, k)
            hue_deg = 0.0
        t_rms = norm_rms_for_color(rms, color_rms_min, color_rms_max)
        v = v_age * (0.65 + 0.35 * (t_rms * strength)) * clamp01(global_v_mul)
        hue_deg = apply_hue_offset(hue_deg)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        s *= sat_mul
        v *= val_mul
        r, g, b = colorsys.hsv_to_rgb((hue_deg%360)/360.0, clamp01(s), clamp01(v))
        return (int(r*255), int(g*255), int(b*255))
    else:
        # Цветной градиент
        hue_deg = hue_bgyr_from_t(t_age)
        hue_deg = apply_hue_offset(hue_deg)
        # Сдвиг hue к красному (0°) и увеличение яркости при громком сигнале
        hue_shift = (0.0 - hue_deg) * (0.25 * t_rms * strength)
        hue_deg = (hue_deg + hue_shift) % 360.0
        v = (0.65 + 0.35 * (t_rms * strength)) * clamp01(global_v_mul)
        s = 0.9
        # Выцветание по возрасту
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        s *= sat_mul
        v *= val_mul
        r, g, b = colorsys.hsv_to_rgb(hue_deg/360.0, clamp01(s), clamp01(v))
        return (int(r*255), int(g*255), int(b*255))


def color_from_pitch(freq_hz: float, rms: float, rms_strength: float,
                     global_v_mul: float) -> tuple[int,int,int]:
    """
    Цвет по высоте ноты:
      - Hue — из высоты (логарифмическая шкала, шаги ≈ полутон).
      - Saturation — фиксированная (0.9).
      - Value — из RMS (0.4..1.0) * global_v_mul.
    """
    try:
        f = float(freq_hz)
    except Exception:
        f = 0.0
    if not (f > 0.0):
        # Нет высоты — тускло-серый
        v = 0.25 * clamp01(global_v_mul)
        return (int(200*v), int(200*v), int(200*v))

    # Ограничим частоту диапазоном и переведём в «непрерывную MIDI-ноту»
    f = max(PITCH_COLOR_MIN_HZ, min(PITCH_COLOR_MAX_HZ, f))
    # 69 — A4=440Hz; midi = 69 + 12*log2(f/440)
    midi = 69.0 + 12.0 * math.log2(f / 440.0)

    # Hue из полутона (проекция на круг), плюс сдвиг hue_offset
    hue_deg = ((midi % 12.0) / 12.0) * 360.0
    hue_deg = apply_hue_offset(hue_deg)

    # Яркость из RMS с силой влияния rms_strength
    t_rms = norm_rms_for_color(rms, DEFAULT_COLOR_RMS_MIN, DEFAULT_COLOR_RMS_MAX)
    v = (0.40 + 0.60 * (t_rms * clamp01(rms_strength))) * clamp01(global_v_mul)
    s = 0.9

    r, g, b = colorsys.hsv_to_rgb((hue_deg % 360.0)/360.0, clamp01(s), clamp01(v))
    return (int(r*255), int(g*255), int(b*255))
def color_from_rms(rms: float, palette: str,
                   color_rms_min: float, color_rms_max: float,
                   global_v_mul: float) -> tuple[int,int,int]:
    # Normalize palette name to ASCII to be tolerant to old presets
    palette_norm = palette_key(palette)
    t = maybe_invert_t(norm_rms_for_color(rms, color_rms_min, color_rms_max))
    if palette_norm == "BGYR":
        hue_deg = hue_bgyr_from_t(t)
        hue_deg = apply_hue_offset(hue_deg)
        v = 1.0 * clamp01(global_v_mul)
        r, g, b = colorsys.hsv_to_rgb(hue_deg/360.0, 0.85, clamp01(v))
        return (int(r*255), int(g*255), int(b*255))
    elif palette_norm == "GRAYSCALE":
        if t < 1/3:
            v = lerp(1.0, 0.8, t*3.0)
        elif t < 2/3:
            v = lerp(0.8, 0.5, (t-1/3)*3.0)
        else:
            v = lerp(0.5, 0.25, (t-2/3)*3.0)
        v *= clamp01(global_v_mul)
        g = int(255*clamp01(v))
        return (g, g, g)

    elif palette_norm == "RED_DARKRED_GRAY_BLACK":
        # t: 0..1 → Bright Red → Dark Red → Dark Gray → Black
        if t < 1/3:
            s = 1.0
            v = lerp(1.0, 0.65, t*3.0)
        elif t < 2/3:
            k = (t-1/3)*3.0
            s = lerp(1.0, 0.0, k)
            v = lerp(0.65, 0.25, k)
        else:
            k = (t-2/3)*3.0
            s = 0.0
            v = lerp(0.25, 0.0, k)
        v *= clamp01(global_v_mul)
        hue_deg = apply_hue_offset(0.0)  # red
        r, g, b = colorsys.hsv_to_rgb((hue_deg%360)/360.0, clamp01(s), clamp01(v))
        return (int(r*255), int(g*255), int(b*255))

    else:
        hue_deg = hue_br_from_t(t)
        hue_deg = apply_hue_offset(hue_deg)
        v = 1.0 * clamp01(global_v_mul)
        r, g, b = colorsys.hsv_to_rgb(hue_deg/360.0, 0.85, clamp01(v))
        return (int(r*255), int(g*255), int(b*255))

# -------------------- GUI --------------------
def choose_settings():
    devices = sd.query_devices()
    input_devices = [d for d in devices if d['max_input_channels'] > 0]
    
    root = tk.Tk()
    root.title("Настройки")

    # — Входное устройство
    tk.Label(root, text="Входное устройство:").grid(row=0, column=0, padx=8, pady=6, sticky="w")
    device_var = tk.StringVar(value=input_devices[0]['name'] if input_devices else "")
    device_combo = ttk.Combobox(root, values=[d['name'] for d in input_devices], textvariable=device_var, state='readonly', width=45)
    device_combo.grid(row=0, column=1, padx=8, pady=6, sticky="w")

    # — Правило
    tk.Label(root, text="Правило автомата:").grid(row=1, column=0, padx=8, pady=6, sticky="w")
    rules = ["Conway", "HighLife", "Seeds"]
    rule_var = tk.StringVar(value=rules[0])
    rule_combo = ttk.Combobox(root, values=rules, textvariable=rule_var, state='readonly', width=20)
    rule_combo.grid(row=1, column=1, padx=8, pady=6, sticky="w")

    # — Цветовой режим
    tk.Label(root, text="Цветовой режим:").grid(row=2, column=0, padx=8, pady=6, sticky="w")
    color_modes = ["Возраст + RMS", "Только RMS", "Высота ноты (Pitch)"]
    color_mode_var = tk.StringVar(value=color_modes[0])
    color_mode_combo = ttk.Combobox(root, values=color_modes, textvariable=color_mode_var, state='readonly', width=20)
    color_mode_combo.grid(row=2, column=1, padx=8, pady=6, sticky="w")

    # — Палитра возраста
    tk.Label(root, text="Палитра возраста:").grid(row=3, column=0, padx=8, pady=6, sticky="w")
    age_palettes = ["Blue->Green->Yellow->Red", "White->LightGray->Gray->DarkGray", "BrightRed->DarkRed->DarkGray->Black", "BrightRed->DarkRed->DarkGray->Black"]
    age_palette_var = tk.StringVar(value=age_palettes[0])
    ttk.Combobox(root, values=age_palettes, textvariable=age_palette_var, state='readonly', width=28).grid(row=3, column=1, padx=8, pady=6, sticky="w")

    # — Палитра (для «Только RMS»)
    tk.Label(root, text="Палитра для RMS:").grid(row=4, column=0, padx=8, pady=6, sticky="w")
    palettes = ["Blue->Red", "Blue->Green->Yellow->Red", "White->LightGray->Gray->DarkGray", "BrightRed->DarkRed->DarkGray->Black"]
    palette_var = tk.StringVar(value=palettes[1])
    ttk.Combobox(root, values=palettes, textvariable=palette_var, state='readonly', width=28).grid(row=4, column=1, padx=8, pady=6, sticky="w")

    # — Модуляция RMS
    rms_mod_var = tk.BooleanVar(value=True)
    rms_mod_chk = ttk.Checkbutton(root, text="Модуляция цвета по RMS", variable=rms_mod_var)
    rms_mod_chk.grid(row=5, column=1, padx=8, pady=6, sticky="w")

    tk.Label(root, text="Сила модуляции RMS (%):").grid(row=6, column=0, padx=8, pady=6, sticky="w")
    rms_strength_var = tk.IntVar(value=100)
    rms_strength_scale = ttk.Scale(root, from_=0, to=100, orient="horizontal", variable=rms_strength_var)
    rms_strength_scale.grid(row=6, column=1, padx=8, pady=6, sticky="we")

    # — Время тика
    tk.Label(root, text="Время тика (мс):").grid(row=7, column=0, padx=8, pady=6, sticky="w")
    tick_ms_var = tk.IntVar(value=DEFAULT_TICK_MS)
    ttk.Entry(root, textvariable=tick_ms_var, width=10).grid(row=7, column=1, padx=8, pady=6, sticky="w")

    # — Pitch→Tick
    ttk.Separator(root, orient="horizontal").grid(row=8, column=0, columnspan=2, sticky="ew", pady=(6,6))
    pitch_tick_enable_var = tk.BooleanVar(value=False)
    ttk.Checkbutton(root, text="Привязать тик к высоте ноты (Pitch→Tick)", variable=pitch_tick_enable_var).grid(row=9, column=1, padx=8, pady=6, sticky="w")

    tk.Label(root, text="Мин. тик при низкой ноте (мс):").grid(row=10, column=0, padx=8, pady=6, sticky="w")
    pitch_tick_min_var = tk.IntVar(value=DEFAULT_PTICK_MIN_MS)
    ttk.Entry(root, textvariable=pitch_tick_min_var, width=10).grid(row=10, column=1, padx=8, pady=6, sticky="w")

    tk.Label(root, text="Макс. тик при высокой ноте (мс):").grid(row=11, column=0, padx=8, pady=6, sticky="w")
    pitch_tick_max_var = tk.IntVar(value=DEFAULT_PTICK_MAX_MS)
    ttk.Entry(root, textvariable=pitch_tick_max_var, width=10).grid(row=11, column=1, padx=8, pady=6, sticky="w")

    # — Ограничение возраста и выцветание
    tk.Label(root, text="Макс. возраст (тики):").grid(row=12, column=0, padx=8, pady=6, sticky="w")
    max_age_var = tk.IntVar(value=120)
    ttk.Entry(root, textvariable=max_age_var, width=10).grid(row=12, column=1, padx=8, pady=6, sticky="w")

    tk.Label(root, text="Порог выцветания (тики):").grid(row=13, column=0, padx=8, pady=6, sticky="w")
    fade_start_var = tk.IntVar(value=60)
    ttk.Entry(root, textvariable=fade_start_var, width=10).grid(row=13, column=1, padx=8, pady=6, sticky="w")

    tk.Label(root, text="Падение насыщенности к max_age (%):").grid(row=14, column=0, padx=8, pady=6, sticky="w")
    fade_sat_drop_var = tk.IntVar(value=70)
    ttk.Entry(root, textvariable=fade_sat_drop_var, width=10).grid(row=14, column=1, padx=8, pady=6, sticky="w")

    tk.Label(root, text="Падение яркости к max_age (%):").grid(row=15, column=0, padx=8, pady=6, sticky="w")
    fade_val_drop_var = tk.IntVar(value=60)
    ttk.Entry(root, textvariable=fade_val_drop_var, width=10).grid(row=15, column=1, padx=8, pady=6, sticky="w")

    # — Пороговая логика RMS
    ttk.Separator(root, orient="horizontal").grid(row=16, column=0, columnspan=2, sticky="ew", pady=(6,6))
    tk.Label(root, text="Порог автоочистки (RMS):").grid(row=17, column=0, padx=8, pady=6, sticky="w")
    clear_rms_var = tk.DoubleVar(value=DEFAULT_CLEAR_RMS)
    ttk.Entry(root, textvariable=clear_rms_var, width=10).grid(row=17, column=1, padx=8, pady=6, sticky="w")

    tk.Label(root, text="RMS min для цвета:").grid(row=18, column=0, padx=8, pady=6, sticky="w")
    color_rms_min_var = tk.DoubleVar(value=DEFAULT_COLOR_RMS_MIN)
    ttk.Entry(root, textvariable=color_rms_min_var, width=10).grid(row=18, column=1, padx=8, pady=6, sticky="w")

    tk.Label(root, text="RMS max для цвета:").grid(row=19, column=0, padx=8, pady=6, sticky="w")
    color_rms_max_var = tk.DoubleVar(value=DEFAULT_COLOR_RMS_MAX)
    ttk.Entry(root, textvariable=color_rms_max_var, width=10).grid(row=19, column=1, padx=8, pady=6, sticky="w")

    # — Софт-очистка
    ttk.Separator(root, orient="horizontal").grid(row=20, column=0, columnspan=2, sticky="ew", pady=(6,6))
    soft_clear_enable_var = tk.BooleanVar(value=True)
    ttk.Checkbutton(root, text="Софт-очистка при тишине", variable=soft_clear_enable_var).grid(row=21, column=1, padx=8, pady=6, sticky="w")

    tk.Label(root, text="Режим софт-очистки:").grid(row=22, column=0, padx=8, pady=6, sticky="w")
    soft_modes = ["Удалять клетки", "Затухание цвета"]
    soft_mode_var = tk.StringVar(value=soft_modes[0])
    ttk.Combobox(root, values=soft_modes, textvariable=soft_mode_var, state='readonly', width=20).grid(row=22, column=1, padx=8, pady=6, sticky="w")

    tk.Label(root, text="Скорость удаления (% живых/тик):").grid(row=23, column=0, padx=8, pady=6, sticky="w")
    soft_kill_rate_var = tk.IntVar(value=80)
    ttk.Entry(root, textvariable=soft_kill_rate_var, width=10).grid(row=23, column=1, padx=8, pady=6, sticky="w")

    tk.Label(root, text="Минимальная яркость V при затухании:").grid(row=24, column=0, padx=8, pady=6, sticky="w")
    soft_fade_floor_var = tk.DoubleVar(value=0.3)
    ttk.Entry(root, textvariable=soft_fade_floor_var, width=10).grid(row=24, column=1, padx=8, pady=6, sticky="w")

    tk.Label(root, text="Скорость затухания вниз (%/тик):").grid(row=25, column=0, padx=8, pady=6, sticky="w")
    soft_fade_down_var = tk.IntVar(value=1)
    ttk.Entry(root, textvariable=soft_fade_down_var, width=10).grid(row=25, column=1, padx=8, pady=6, sticky="w")

    tk.Label(root, text="Скорость восстановления вверх (%/тик):").grid(row=26, column=0, padx=8, pady=6, sticky="w")
    soft_fade_up_var = tk.IntVar(value=5)
    ttk.Entry(root, textvariable=soft_fade_up_var, width=10).grid(row=26, column=1, padx=8, pady=6, sticky="w")

    selection = {}
    def on_ok():
        selection['device']               = device_combo.get()
        selection['rule']                 = rule_combo.get()
        selection['color_mode']           = color_mode_var.get()
        selection['age_palette']          = age_palette_var.get()
        selection['palette']              = palette_var.get()
        selection['rms_mod']              = rms_mod_var.get()
        selection['rms_strength']         = max(0, min(100, int(rms_strength_var.get())))
        selection['tick_ms']              = max(5, int(tick_ms_var.get()))
        selection['pitch_tick_enable']    = bool(pitch_tick_enable_var.get())
        selection['pitch_tick_min_ms']    = max(5, int(pitch_tick_min_var.get()))
        selection['pitch_tick_max_ms']    = max(5, int(pitch_tick_max_var.get()))
        if selection['pitch_tick_max_ms'] < selection['pitch_tick_min_ms']:
            selection['pitch_tick_max_ms'] = selection['pitch_tick_min_ms']
        selection['max_age']              = max(1, int(max_age_var.get()))
        selection['fade_start']           = max(0, int(fade_start_var.get()))
        selection['fade_sat_drop']        = max(0, min(100, int(fade_sat_drop_var.get())))
        selection['fade_val_drop']        = max(0, min(100, int(fade_val_drop_var.get())))
        selection['clear_rms']            = max(0.0, float(clear_rms_var.get()))
        selection['color_rms_min']        = max(0.0, float(color_rms_min_var.get()))
        selection['color_rms_max']        = max(0.0, float(color_rms_max_var.get()))
        if selection['color_rms_max'] <= selection['color_rms_min']:
            selection['color_rms_max'] = selection['color_rms_min'] + 1e-6
        selection['soft_clear_enable']    = bool(soft_clear_enable_var.get())
        selection['soft_mode']            = soft_mode_var.get()
        selection['soft_kill_rate']       = max(0, min(100, int(soft_kill_rate_var.get())))
        selection['soft_fade_floor']      = clamp01(float(soft_fade_floor_var.get()))
        selection['soft_fade_down']       = max(0, min(100, int(soft_fade_down_var.get())))
        selection['soft_fade_up']         = max(0, min(100, int(soft_fade_up_var.get())))
        root.destroy()

    ttk.Button(root, text="OK", command=on_ok).grid(row=27, column=1, padx=8, pady=12, sticky="e")
    root.mainloop()
    return selection

# -------------------- Аудио --------------------
def audio_callback(indata, frames, time_info, status):
    if status:
        print("Audio status:", status, file=sys.stderr)
    mono = indata[:, 0].astype(np.float32)
    rms  = float(np.sqrt(np.mean(mono ** 2)))
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
    global stream
    device_id = None
    for i, d in enumerate(sd.query_devices()):
        if d['name'] == device_name:
            device_id = i; break
    if device_id is None:
        print("Устройство не найдено!")
        sys.exit(1)
    stream = sd.InputStream(
        samplerate=SAMPLE_RATE, blocksize=BLOCK_SIZE, dtype='float32',
        channels=CHANNELS, device=device_id, callback=audio_callback
    )
    stream.start()

# -------------------- Автомат --------------------
def step_life(grid, rule):
    H, W = grid.shape
    new = np.zeros_like(grid, dtype=bool)
    padded = np.pad(grid, ((1,1),(1,1)), mode='constant', constant_values=0)
    neighbors = sum([
        padded[0:H,0:W], padded[0:H,1:W+1], padded[0:H,2:W+2],
        padded[1:H+1,0:W],                   padded[1:H+1,2:W+2],
        padded[2:H+2,0:W], padded[2:H+2,1:W+1], padded[2:H+2,2:W+2],
    ])
    if rule == "Conway":
        new[(grid & ((neighbors==2)|(neighbors==3))) | (~grid & (neighbors==3))] = True
    elif rule == "HighLife":
        new[(grid & ((neighbors==2)|(neighbors==3))) | (~grid & ((neighbors==3)|(neighbors==6)))] = True
    elif rule == "Seeds":
        new[(~grid & (neighbors==2))] = True
    else:
        new = grid.copy()
    return new

def spawn_cells(grid, count):
    

    H, W = grid.shape
    if count <= 0:
        return
    
    # Количество «кластеров» и число точек на кластер:
    clusters = max(1, count // 80)
    per = max(1, count // clusters)
    
    for _ in range(clusters):
        cr = random.randrange(0, H)
        cc = random.randrange(0, W)
        radius = random.randint(2, 8)
        for _ in range(per):
            ang = random.random() * math.tau
            rr = cr + int(math.cos(ang) * random.randint(0, radius))
            cc2 = cc + int(math.sin(ang) * random.randint(0, radius))
            if 0 <= rr < H and 0 <= cc2 < W:
                grid[rr, cc2] = True

# -------------------- HUD --------------------
def draw_hud(screen, font,
             rule, color_mode, rms_strength, age_palette, palette,
             randomize_palette, fade_start, max_age,
             clear_rms, color_rms_min, color_rms_max,
             soft_clear_enable, soft_mode, soft_kill_rate, global_v_mul,
             pitch_tick_enable, pitch_tick_min_ms, pitch_tick_max_ms,
             current_tick_ms, detected_freq, detected_rms, spawn_count):
    # Заливка фона HUD
    hud_x = GRID_W * CELL_SIZE
    pygame.draw.rect(screen, (24, 24, 28), (hud_x, 0, HUD_WIDTH, GRID_H*CELL_SIZE))

    palette_aliases = {
        "Blue->Green->Yellow->Red": "BGYR",
        "White->LightGray->Gray->DarkGray": "GrayScale",
        "BrightRed->DarkRed->DarkGray->Black": "Red->DarkRed->Gray->Black",
    }
    pal_display = (PALETTE_STATE.rms_palette_choice if randomize_palette else palette)
    pal_display = palette_aliases.get((pal_display or "").replace("→","->"), pal_display)
    age_pal_display = (PALETTE_STATE.age_palette_choice if randomize_palette else age_palette)
    age_pal_display = palette_aliases.get((age_pal_display or "").replace("→","->"), age_pal_display)

    lines = [
        f"Rule: {rule}",
        f"Color mode: {color_mode}",
        f"RMS mod: {int(rms_strength*100)}%",
        f"Age palette: {age_pal_display}",
        f"RMS palette: {pal_display}",
        f"HueOffset: {int(PALETTE_STATE.hue_offset)}°",
        f"Invert: {'ON' if PALETTE_STATE.invert else 'OFF'}",
        f"FadeStart: {fade_start}",
        f"MaxAge: {max_age}",
        f"CLEAR RMS: {clear_rms:.3f}",
        f"Color RMS: [{color_rms_min:.3f} .. {color_rms_max:.3f}]",
        f"Soft clear: {'ON' if soft_clear_enable else 'OFF'}",
        f"Soft mode: {soft_mode}",
        f"Soft KillRate: {soft_kill_rate}%",
        f"Vmul: {global_v_mul:.2f}",
        f"PTick: {'ON' if pitch_tick_enable else 'OFF'} [{pitch_tick_min_ms}..{pitch_tick_max_ms}]",
        (f"PitchColorRange: {int(PITCH_COLOR_MIN_HZ)}–{int(PITCH_COLOR_MAX_HZ)} Hz" if color_mode == "Высота ноты (Pitch)" else ""),
        f"Tick: {current_tick_ms} ms",
        f"Freq: {detected_freq:.1f} Hz",
        f"RMS: {detected_rms:.4f}",
        f"Spawn/tick: {spawn_count}",
        "",
        "[C] Clear поле",
        "[R] Случайные зерна",
        "[P] Randomize палитра",
        "[I] Инверсия цвета",
        "[H/J] Hue ±30°",
        "[O] Hue = 0°",
        "[F7/F8] Tick ±10",
        "[F6] Tick = GUI",
        "[F5] Save | [F9] Load",
        "[F10] PalCycle",
        "[Esc] Exit",
    ]

    y = 12
    for line in lines:
        txt = font.render(line, True, (220,220,220))
        screen.blit(txt, (GRID_W*CELL_SIZE + 16, y))
        y += 22

# -------------------- Основной цикл приложения --------------------
def run_app(rule, color_mode, age_palette, palette, rms_mod, rms_strength_pct,
            tick_ms_init, pitch_tick_enable, pitch_tick_min_ms, pitch_tick_max_ms,
            fade_start, max_age, fade_sat_drop_pct, fade_val_drop_pct,
            randomize_palette,
            clear_rms, color_rms_min, color_rms_max,
            soft_clear_enable, soft_mode, soft_kill_rate,
            soft_fade_floor, soft_fade_down, soft_fade_up):
    pygame.init()
    screen = pygame.display.set_mode((GRID_W*CELL_SIZE + HUD_WIDTH, GRID_H*CELL_SIZE))
    pygame.display.set_caption("Guitar-driven Cellular Automaton")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 14)

    grid = np.zeros((GRID_H, GRID_W), dtype=bool)
    age  = np.zeros((GRID_H, GRID_W), dtype=np.int32)

    # начальные зерна
    for _ in range(200):
        r = random.randrange(0, GRID_H); c = random.randrange(0, GRID_W)
        grid[r,c]=True; age[r,c]=1

    last_tick = pygame.time.get_ticks()
    global running
    detected_freq = 0.0
    detected_rms  = 0.0
    spawn_count   = 0

    rms_strength = clamp01(rms_strength_pct / 100.0)
    tick_ms_default = max(5, int(tick_ms_init))
    tick_ms = tick_ms_default
    pitch_tick_min_ms = max(5, int(pitch_tick_min_ms))
    pitch_tick_max_ms = max(5, int(pitch_tick_max_ms))
    if pitch_tick_max_ms < pitch_tick_min_ms:
        pitch_tick_max_ms = pitch_tick_min_ms
    ptick_min_default = pitch_tick_min_ms
    ptick_max_default = pitch_tick_max_ms

    fade_start   = max(0, int(fade_start))
    max_age      = max(1, int(max_age))
    fade_sat_drop_pct = max(0.0, min(100.0, float(fade_sat_drop_pct)))
    fade_val_drop_pct = max(0.0, min(100.0, float(fade_val_drop_pct)))

    # глобальный множитель яркости для режима «затухание цвета»
    global_v_mul = 1.0

    # начальная рандомизация, если включена
    if randomize_palette:
        PALETTE_STATE.randomize()

    # --- FIX: Initialize current_tick_ms before use ---
    current_tick_ms = tick_ms

    while running:
        # Отрисовка поля
        screen.fill(BG_COLOR)
        for r in range(GRID_H):
            for c in range(GRID_W):
                if grid[r, c]:
                    if color_mode == "Возраст + RMS":
                        col = color_from_age_rms(
                            age[r, c], detected_rms, rms_strength,
                            fade_start, max_age,
                            fade_sat_drop_pct, fade_val_drop_pct,
                            color_rms_min, color_rms_max,
                            global_v_mul,
                            (PALETTE_STATE.age_palette_choice if randomize_palette else age_palette)
                        )
                    elif color_mode == "Высота ноты (Pitch)":
                        col = color_from_pitch(
                            detected_freq, detected_rms, rms_strength,
                            global_v_mul
                        )
                    else:
                        col = color_from_rms(
                            detected_rms,
                            (PALETTE_STATE.rms_palette_choice if randomize_palette else palette),
                            color_rms_min, color_rms_max,
                            global_v_mul
                        )
                    pygame.draw.rect(
                        screen, col,
                        (FIELD_OFFSET_X + c*CELL_SIZE, r*CELL_SIZE, CELL_SIZE, CELL_SIZE)
                    )

        draw_hud(
            screen, font,
            rule, color_mode, rms_strength,
            (PALETTE_STATE.age_palette_choice if randomize_palette else age_palette),
            (PALETTE_STATE.rms_palette_choice if randomize_palette else palette),
            randomize_palette, fade_start, max_age,
            clear_rms, color_rms_min, color_rms_max,
            soft_clear_enable, soft_mode, soft_kill_rate, global_v_mul,
            pitch_tick_enable, pitch_tick_min_ms, pitch_tick_max_ms,
            current_tick_ms, detected_freq, detected_rms, spawn_count
        )
        pygame.display.flip()

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running=False
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_c:
                    grid[:,:]=False; age[:,:]=0
                elif ev.key == pygame.K_r:
                    grid = np.random.rand(GRID_H, GRID_W) < 0.12
                    age  = grid.astype(np.int32)
                    if randomize_palette:
                        PALETTE_STATE.randomize()
                elif ev.key == pygame.K_ESCAPE:
                    running = False
                elif ev.key == pygame.K_p:
                    if randomize_palette: PALETTE_STATE.randomize()
                elif ev.key == pygame.K_i:
                    PALETTE_STATE.invert = not PALETTE_STATE.invert
                elif ev.key == pygame.K_h:
                    PALETTE_STATE.hue_offset = (PALETTE_STATE.hue_offset - 30.0) % 360.0
                elif ev.key == pygame.K_j:
                    PALETTE_STATE.hue_offset = (PALETTE_STATE.hue_offset + 30.0) % 360.0
                elif ev.key == pygame.K_o:
                    PALETTE_STATE.hue_offset = 0.0
                elif ev.key == pygame.K_F5:
                    save_preset(PRESET_PATH)
                elif ev.key == pygame.K_F9:
                    load_preset(PRESET_PATH)
                elif ev.key == pygame.K_F10:
                    # Переключение палитры: в режиме "Только RMS" — RMS палитра, иначе — палитра возраста
                    available = ["Blue->Green->Yellow->Red", "White->LightGray->Gray->DarkGray", "BrightRed->DarkRed->DarkGray->Black"]
                    if color_mode == "Только RMS":
                        cur = (PALETTE_STATE.rms_palette_choice if randomize_palette else palette)
                        cur_norm = (cur or "").replace("→","->")
                        try:
                            i = available.index(cur_norm)
                        except ValueError:
                            i = -1
                        new = available[(i+1) % len(available)]
                        if randomize_palette:
                            PALETTE_STATE.rms_palette_choice = new
                        else:
                            palette = new
                    else:
                        cur = (PALETTE_STATE.age_palette_choice if randomize_palette else age_palette)
                        cur_norm = (cur or "").replace("→","->")
                        try:
                            i = available.index(cur_norm)
                        except ValueError:
                            i = -1
                        new = available[(i+1) % len(available)]
                        if randomize_palette:
                            PALETTE_STATE.age_palette_choice = new
                        else:
                            age_palette = new
                elif ev.key == pygame.K_LEFTBRACKET:
                    rms_strength = max(0.0, rms_strength - 0.05)
                elif ev.key == pygame.K_RIGHTBRACKET:
                    rms_strength = min(1.0, rms_strength + 0.05)
                elif ev.key == pygame.K_MINUS:
                    fade_start = max(0, fade_start - 5)
                elif ev.key == pygame.K_EQUALS:
                    fade_start = min(max_age-1, fade_start + 5)
                elif ev.key == pygame.K_COMMA:
                    max_age = max(1, max_age - 5)
                    fade_start = min(fade_start, max_age-1)
                    age = np.minimum(age, max_age)
                elif ev.key == pygame.K_PERIOD:
                    max_age = max_age + 5
                elif ev.key == pygame.K_F7:
                    if pitch_tick_enable:
                        pitch_tick_min_ms = max(5, pitch_tick_min_ms - 10)
                        pitch_tick_max_ms = max(pitch_tick_max_ms, pitch_tick_min_ms)
                    else:
                        tick_ms = max(5, tick_ms - 10)
                elif ev.key == pygame.K_F8:
                    if pitch_tick_enable:
                        pitch_tick_max_ms = min(5000, pitch_tick_max_ms + 10)
                        pitch_tick_min_ms = min(pitch_tick_min_ms, pitch_tick_max_ms)
                    else:
                        tick_ms = min(2000, tick_ms + 10)
                elif ev.key == pygame.K_F6:
                    try:
                        # Reset to defaults from GUI (if defined)
                        if pitch_tick_enable:
                            pitch_tick_min_ms = ptick_min_default
                            pitch_tick_max_ms = ptick_max_default
                        else:
                            tick_ms = tick_ms_default
                    except NameError:
                        # Fallback: gentle reset values
                        if pitch_tick_enable:
                            pitch_tick_min_ms = max(5, min(100, pitch_tick_min_ms))
                            pitch_tick_max_ms = max(pitch_tick_min_ms, min(300, pitch_tick_max_ms))
                        else:
                            tick_ms = max(10, min(120, tick_ms))
                elif ev.key == pygame.K_ESCAPE:
                    running = False
                else:
                    tick_ms = tick_ms_default
        # забираем последние значения частоты/громкости
        try:
            while True: detected_freq = pitch_queue.get_nowait() or detected_freq
        except queue.Empty: pass
        try:
            while True: detected_rms = rms_queue.get_nowait() or detected_rms
        except queue.Empty: pass

        # Вычисляем текущий тик в зависимости от режима Pitch→Tick
        current_tick_ms = tick_ms
        if pitch_tick_enable and detected_freq > MIN_NOTE_FREQ:
            f_clamped = max(FREQ_MIN, min(FREQ_MAX, detected_freq))
            t = (f_clamped - FREQ_MIN) / (FREQ_MAX - FREQ_MIN)  # 0..1
            current_tick_ms = int(round(lerp(pitch_tick_min_ms, pitch_tick_max_ms, clamp01(t))))

        # Софт-очистка / поведение при тишине
        if detected_rms < clear_rms:
            if soft_clear_enable:
                if soft_mode == "Удалять клетки":
                    quiet_factor = 1.0 - (detected_rms / max(1e-9, clear_rms))
                    kill_frac = clamp01((soft_kill_rate / 100.0) * quiet_factor)
                    alive_indices = np.argwhere(grid)
                    if alive_indices.size > 0 and kill_frac > 0.0:
                        kill_count = int(len(alive_indices) * kill_frac)
                        if kill_count > 0:
                            idx = np.random.choice(len(alive_indices), size=kill_count, replace=False)
                            to_kill = alive_indices[idx]
                            grid[to_kill[:,0], to_kill[:,1]] = False
                            age[to_kill[:,0], to_kill[:,1]]  = 0
                else:
                    target = clamp01(max(soft_fade_floor, 0.0))
                    step = clamp01(soft_fade_down / 100.0)
                    global_v_mul = max(target, global_v_mul - step)
            else:
                grid[:,:] = False; age[:,:] = 0; spawn_count = 0
        else:
            step = clamp01(soft_fade_up / 100.0)
            global_v_mul = min(1.0, global_v_mul + step)

        # Спавн при достаточной частоте
        if detected_rms >= clear_rms:
            if detected_freq > MIN_NOTE_FREQ:
                f_clamped = max(FREQ_MIN, min(FREQ_MAX, detected_freq))
                t = (f_clamped-FREQ_MIN)/(FREQ_MAX-FREQ_MIN)
                base = 1.0 - t
                vol = min(detected_rms*VOLUME_SCALE,1.0)
                spawn_count = int(SPAWN_BASE + SPAWN_SCALE*base*vol)
            else:
                spawn_count = 0
        else:
            spawn_count = 0

        now = pygame.time.get_ticks()
        if now - last_tick >= current_tick_ms:
            if spawn_count>0: spawn_cells(grid, spawn_count)
            new_grid = step_life(grid, rule)

            survived = new_grid & grid
            age[survived] = np.minimum(age[survived] + 1, max_age)
            born = new_grid & (~grid)
            age[born] = 1
            died = (~new_grid) & grid
            age[died] = 0

            grid = new_grid
            last_tick = now

# -------------------- Точка входа --------------------
if __name__ == "__main__":
    print("Настройки...")
    sel = choose_settings()

    # --- Defaults shim (чтобы не было KeyError) ---
    defaults = {
        'randomize_palette': False,
        'clear_rms': DEFAULT_CLEAR_RMS,
        'color_rms_min': DEFAULT_COLOR_RMS_MIN,
        'color_rms_max': DEFAULT_COLOR_RMS_MAX,
        'soft_clear_enable': False,
        'soft_mode': "Удалять клетки",
        'soft_kill_rate': 80,
        'soft_fade_floor': 0.3,
        'soft_fade_down': 1,
        'soft_fade_up': 5,
        'tick_ms': DEFAULT_TICK_MS,
        'pitch_tick_enable': False,
        'pitch_tick_min_ms': DEFAULT_PTICK_MIN_MS,
        'pitch_tick_max_ms': DEFAULT_PTICK_MAX_MS,
        'age_palette': "Blue->Green->Yellow->Red",
    }
    for k, v in defaults.items():
        sel.setdefault(k, v)

    try:
        start_audio_stream(sel['device'])
    except Exception as e:
        print("Не удалось открыть аудио-стрим:", e, file=sys.stderr)
        sys.exit(1)

    try:
        run_app(
            sel['rule'],
            sel['color_mode'],
            sel['age_palette'],
            sel['palette'],
            sel['rms_mod'],
            sel['rms_strength'],
            sel['tick_ms'],
            sel['pitch_tick_enable'],
            sel['pitch_tick_min_ms'],
            sel['pitch_tick_max_ms'],
            sel['fade_start'],
            sel['max_age'],
            sel['fade_sat_drop'],
            sel['fade_val_drop'],
            sel.get('randomize_palette', False),
            sel['clear_rms'],
            sel['color_rms_min'],
            sel['color_rms_max'],
            sel['soft_clear_enable'],
            sel['soft_mode'],
            sel['soft_kill_rate'],
            sel['soft_fade_floor'],
            sel['soft_fade_down'],
            sel['soft_fade_up']
        )
    except KeyboardInterrupt:
        pass
    finally:
        running = False