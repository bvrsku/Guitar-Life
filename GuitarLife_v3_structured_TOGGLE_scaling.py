#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════════════════════════
                              GUITAR LIFE v21
                         Структурированная версия
═══════════════════════════════════════════════════════════════════════════════

Интерактивная визуализация клеточных автоматов с аудио-анализом
Автор: Guitar Life Team
Версия: 21 (Structured)

Основные возможности:
• Многослойные клеточные автоматы (Conway, HighLife, Day&Night и др.)
• Аудио-анализ в реальном времени с микрофона
• Интерактивные цветовые палитры (60+ вариантов)
• Визуальные эффекты (bloom, trails, blur, dither и др.)
• Полноценный GUI с настройками слоев
• Сохранение/загрузка пресетов

Оптимизации производительности:
• Кэширование HSV/RGB вычислений
• Векторизация NumPy операций
• Оптимизированное управление памятью
• Профилирование производительности
"""

from __future__ import annotations

# ═══════════════════════════════════════════════════════════════════════════════
#                                   IMPORTS
# ═══════════════════════════════════════════════════════════════════════════════

# Подавление предупреждений
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="pygame.pkgdata")

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
from functools import lru_cache
from typing import Any, Dict, List, Optional, Tuple, Union

# Основные зависимости
try:
    import numpy as np
except ImportError as e:
    raise SystemExit("NumPy is required. Install with: pip install numpy") from e

try:
    import pygame
except ImportError as e:
    raise SystemExit("pygame is required. Install with: pip install pygame") from e

# Аудио зависимости (опционально)
try:
    import sounddevice as sd
    SD_AVAILABLE = True
except ImportError:
    sd = None
    SD_AVAILABLE = False

try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    librosa = None
    LIBROSA_AVAILABLE = False

# Дополнительные модули (опционально)
try:
    from settings_window import SettingsWindow
    SETTINGS_WINDOW_AVAILABLE = True
except ImportError:
    SETTINGS_WINDOW_AVAILABLE = False

try:
    from resource_utils import (resource_manager, load_app_config, save_app_config, 
                               load_guitar_config, save_guitar_config)
except ImportError:
    resource_manager = None
    def load_app_config(): return {}
    def save_app_config(config): return False
    def load_guitar_config(): return {}
    def save_guitar_config(config): return False

# ═══════════════════════════════════════════════════════════════════════════════
#                              КОНСТАНТЫ И НАСТРОЙКИ
# ═══════════════════════════════════════════════════════════════════════════════

# === АУДИО НАСТРОЙКИ ===
SAMPLE_RATE = 44100
BLOCK_SIZE = 2048
CHANNELS = 1
FPS = 60

# === НАСТРОЙКИ СЕТКИ И ДИСПЛЕЯ ===
GRID_W, GRID_H = 120, 70
CELL_SIZE = 8
BG_COLOR = (10, 10, 12)
HUD_WIDTH = 520
FIELD_OFFSET_X = 0

# === ПРАВИЛА КЛЕТОЧНЫХ АВТОМАТОВ ===
CA_RULES = [
    "Conway", "HighLife", "Day&Night", "Replicator", 
    "Seeds", "Maze", "Coral", "LifeWithoutDeath", "Gnarl"
]

# === ЦВЕТОВЫЕ ПАЛИТРЫ ===
HSV_DESIGN_PALETTES = [
    # Основные HSV переходы
    "Blue->Red", "Blue->Green->Yellow->Red", "Rainbow", "RainbowSmooth", 
    # Природные дизайны
    "Sunset", "Aurora", "Ocean", "Fire", "Galaxy", "Tropical", "Volcano", "DeepSea",
    # Сезонные
    "Spring", "Summer", "Autumn", "Winter", "Ice", "Forest", "Desert",
    # Научные палитры
    "Viridis", "Inferno", "Magma", "Plasma", "Cividis", "Twilight",
    # Монохромные и контрастные
    "White->LightGray->Gray->DarkGray", "BrightRed->DarkRed->DarkGray->Black", 
    "Monochrome", "Sepia", "HighContrast", "LowContrast",
    # Материалы и текстуры
    "Gold", "Silver", "Copper", "Emerald", "Sapphire", "Ruby", "Amethyst",
    "Steel", "Bronze", "Pearl", "Coral", "Jade", "Topaz",
    # Специальные и тематические
    "Ukraine", "Neon", "Cyberpunk", "Retro", "Vintage", "Pastel", "Candy",
    # Природные цвета
    "Lime", "Mint", "Peach", "Lavender", "Rose", "Sky", "Sand", "Charcoal", "Clouds", "Flame"
]

HSV_COLOR_PALETTES = HSV_DESIGN_PALETTES  # Для совместимости

# Объединенный список палитр
ALL_PALETTES = list(set(HSV_DESIGN_PALETTES + HSV_COLOR_PALETTES))
PALETTE_OPTIONS = ALL_PALETTES

# === НАСТРОЙКИ АУДИО ОБРАБОТКИ ===
SPAWN_BASE, SPAWN_SCALE = 10, 349
FREQ_MIN, FREQ_MAX = 72.0, 1500.0
MIN_NOTE_FREQ = 70.0
VOLUME_SCALE = 8.0

# === ПОРОГОВЫЕ ЗНАЧЕНИЯ ===
DEFAULT_CLEAR_RMS = 0.004
DEFAULT_COLOR_RMS_MIN = 0.005
DEFAULT_COLOR_RMS_MAX = 0.2
DEFAULT_TICK_MS = 20
DEFAULT_PTICK_MIN_MS = 60
DEFAULT_PTICK_MAX_MS = 120

# === ТИПЫ ОЧИСТКИ ===
CLEAR_TYPES = [
    "Полная очистка",        # Complete clear - all cells
    "Частичная очистка",     # Partial clear - percentage
    "Очистка по возрасту",   # Age-based clear - old cells
    "Случайная очистка"      # Random clear - random cells
]

# === ГЛОБАЛЬНЫЕ АУДИО ПЕРЕМЕННЫЕ ===
audio_rms = 0.0
audio_pitch = 0.0
audio_gain = 0.0

# Очереди для аудио данных
pitch_queue = queue.Queue(maxsize=8)
rms_queue = queue.Queue(maxsize=8)
running = True

# ═══════════════════════════════════════════════════════════════════════════════
#                               УТИЛИТАРНЫЕ ФУНКЦИИ
# ═══════════════════════════════════════════════════════════════════════════════

def clamp01(x: float) -> float:
    """Ограничивает значение в диапазоне [0, 1]"""
    return max(0.0, min(1.0, x))

def lerp(a: float, b: float, t: float) -> float:
    """Линейная интерполяция между a и b"""
    return a + (b - a) * t

def get_palette_by_category(category: str = "all") -> List[str]:
    """Возвращает список палитр по категории"""
    if category == "HSV-дизайны":
        return HSV_DESIGN_PALETTES
    elif category == "Только RMS":
        return HSV_COLOR_PALETTES
    else:
        return PALETTE_OPTIONS

def _create_optimized_grid(height: int, width: int) -> np.ndarray:
    """Создает оптимизированную сетку для клеток"""
    return np.zeros((height, width), dtype=bool)

def _create_optimized_age_array(height: int, width: int) -> np.ndarray:
    """Создает оптимизированный массив возраста клеток (np.uint32 для предотвращения переполнения)"""
    return np.zeros((height, width), dtype=np.uint32)

# ═══════════════════════════════════════════════════════════════════════════════
#                               ЦВЕТОВЫЕ ФУНКЦИИ
# ═══════════════════════════════════════════════════════════════════════════════

@lru_cache(maxsize=2048)
def _cached_hsv_to_rgb(h: float, s: float, v: float) -> Tuple[int, int, int]:
    """Кэшированная конверсия HSV в RGB для оптимизации"""
    h_norm = (h % 360.0) / 360.0
    s_norm = max(0.0, min(1.0, s))
    v_norm = max(0.0, min(1.0, v))
    r, g, b = colorsys.hsv_to_rgb(h_norm, s_norm, v_norm)
    return (int(r * 255), int(g * 255), int(b * 255))

def hue_bgyr_from_t(t: float) -> float:
    """Базовая BGYR палитра: синий -> зеленый -> желтый -> красный"""
    t = clamp01(t)
    if t < 1/3:   
        return lerp(220.0, 120.0, t * 3.0)
    elif t < 2/3: 
        return lerp(120.0, 60.0, (t - 1/3) * 3.0)
    else:
        return lerp(60.0, 0.0, (t - 2/3) * 3.0)

def hue_fire_from_t(t: float) -> Tuple[float, float, float]:
    """Огненная палитра"""
    t = clamp01(t)
    if t < 0.25:
        h, s, v = 0.0, 1.0, lerp(0.05, 0.25, t / 0.25)
    elif t < 0.5:
        k = (t - 0.25) / 0.25
        h, s, v = 0.0, 1.0, lerp(0.25, 0.6, k)
    elif t < 0.75:
        k = (t - 0.5) / 0.25
        h, s, v = lerp(20.0, 50.0, k), 1.0, lerp(0.6, 0.9, k)
    else:
        k = (t - 0.75) / 0.25
        h, s, v = 55.0, lerp(1.0, 0.0, k), 1.0
    return h, s, v

def hue_ocean_from_t(t: float) -> Tuple[float, float, float]:
    """Океаническая палитра"""
    t = clamp01(t)
    if t < 0.5:
        k = t / 0.5
        h = lerp(220.0, 200.0, k)
        s = 1.0
        v = lerp(0.35, 0.85, k)
    else:
        k = (t - 0.5) / 0.5
        h = lerp(200.0, 180.0, k)
        s = lerp(1.0, 0.2, k)
        v = lerp(0.85, 1.0, k)
    return h, s, v

def hue_neon_from_t(t: float) -> Tuple[float, float, float]:
    """Неоновая палитра"""
    t = clamp01(t)
    if t < 1/3:      
        h = lerp(285.0, 240.0, t * 3.0)
    elif t < 2/3:    
        h = lerp(240.0, 120.0, (t - 1/3) * 3.0)
    else:
        h = lerp(120.0, 315.0, (t - 2/3) * 3.0)
    s = 1.0
    v = 1.0
    return h, s, v

def hue_ukraine_from_t(t: float) -> Tuple[float, float, float]:
    """Украинская палитра"""
    t = clamp01(t)
    if t < 0.5:
        k = t / 0.5
        h = 50.0
        s = lerp(1.0, 0.6, k)
        v = lerp(0.95, 1.0, k)
    else:
        k = (t - 0.5) / 0.5
        h = lerp(50.0, 220.0, k)
        s = lerp(0.6, 1.0, k)
        v = lerp(1.0, 0.9, k)
    return h, s, v

# ═══════════════════════════════════════════════════════════════════════════════
#                               ВИЗУАЛЬНЫЕ ЭФФЕКТЫ
# ═══════════════════════════════════════════════════════════════════════════════

def apply_trails(surface: pygame.Surface, trail_strength: float):
    """Эффект следов - затухание предыдущего кадра"""
    if trail_strength <= 0: 
        return
    fade = clamp01(1.0 - trail_strength)
    try:
        arr = pygame.surfarray.pixels3d(surface)
        arr[:] = (arr * fade).astype(arr.dtype)
    except Exception:
        pass

def apply_scale_blur(surface: pygame.Surface, scale: int):
    """Блюр через масштабирование"""
    if scale <= 1: 
        return
    try:
        w, h = surface.get_size()
        dw, dh = max(1, w // scale), max(1, h // scale)
        small = pygame.transform.smoothscale(surface, (dw, dh))
        surface.blit(pygame.transform.smoothscale(small, (w, h)), (0, 0))
    except Exception:
        pass

def apply_bloom(surface: pygame.Surface, strength: float):
    """Эффект свечения для ярких областей"""
    if strength <= 0: 
        return
    try:
        w, h = surface.get_size()
        arr = pygame.surfarray.pixels3d(surface)
        # Простая яркостная маска
        lum = (0.2126 * arr[:, :, 0] + 0.7152 * arr[:, :, 1] + 0.0722 * arr[:, :, 2])
        mask = (lum > 180).astype(np.float32) * strength
        mask3 = np.dstack([mask, mask, mask])
        # Downscale / upscale для мягкого свечения
        k = 4
        dw, dh = max(1, w // k), max(1, h // k)
        small = pygame.transform.smoothscale(surface, (dw, dh))
        blurred = pygame.transform.smoothscale(small, (w, h))
        arr_b = pygame.surfarray.pixels3d(blurred)
        arr[:] = np.clip(arr + arr_b * mask3, 0, 255).astype(np.uint8)
    except Exception:
        pass

def apply_posterize(surface: pygame.Surface, strength: int):
    """Постеризация - уменьшение количества цветов"""
    if strength <= 1:
        return
    try:
        arr = pygame.surfarray.pixels3d(surface)
        factor = 255.0 / (strength - 1)
        arr[:] = (np.round(arr / factor) * factor).astype(np.uint8)
    except Exception:
        pass

def apply_dither(surface: pygame.Surface):
    """Дизеринг для создания ретро-эффекта"""
    try:
        w, h = surface.get_size()
        arr = pygame.surfarray.pixels3d(surface)
        
        # Создаем шум для дизеринга
        noise = np.random.randint(-16, 17, size=(w, h, 1))
        
        # Применяем шум
        dithered = arr.astype(np.int16) + noise
        arr[:] = np.clip(dithered, 0, 255).astype(np.uint8)
    except Exception:
        pass

def apply_scanlines(surface: pygame.Surface, strength: float):
    """Эффект сканирующих линий"""
    if strength <= 0: 
        return
    try:
        arr = pygame.surfarray.pixels3d(surface)
        h = arr.shape[1]
        for y in range(0, h, 2):
            if y < h:
                arr[:, y] = (arr[:, y] * (1.0 - strength)).astype(np.uint8)
    except Exception:
        pass

def apply_pixelate(surface: pygame.Surface, block: int):
    """Пикселизация изображения"""
    if block <= 1: 
        return
    try:
        w, h = surface.get_size()
        dw, dh = max(1, w // block), max(1, h // block)
        small = pygame.transform.scale(surface, (dw, dh))
        surface.blit(pygame.transform.scale(small, (w, h)), (0, 0))
    except Exception:
        pass

def apply_outline(surface: pygame.Surface, thickness: int = 1):
    """Создание контуров"""
    if thickness <= 0: 
        return
    try:
        # Простая реализация контуров через edge detection
        arr = pygame.surfarray.pixels3d(surface)
        gray = np.mean(arr, axis=2)
        
        # Sobel edge detection
        gx = np.gradient(gray, axis=0)
        gy = np.gradient(gray, axis=1)
        edges = np.sqrt(gx**2 + gy**2)
        
        # Threshold и применение
        edge_mask = (edges > 30).astype(np.uint8) * 255
        for i in range(3):
            arr[:, :, i] = np.maximum(arr[:, :, i], edge_mask)
    except Exception:
        pass

# ═══════════════════════════════════════════════════════════════════════════════
#                            КЛЕТОЧНЫЕ АВТОМАТЫ
# ═══════════════════════════════════════════════════════════════════════════════

def step_life(grid: np.ndarray, rule: str) -> np.ndarray:
    """Выполняет один шаг клеточного автомата"""
    H, W = grid.shape
    
    # Оптимизированный подсчет соседей
    padded = np.pad(grid.astype(int), ((1, 1), (1, 1)), mode='constant', constant_values=0)
    neighbors = (
        padded[0:H, 0:W] + padded[0:H, 1:W+1] + padded[0:H, 2:W+2] +
        padded[1:H+1, 0:W] +                     padded[1:H+1, 2:W+2] +
        padded[2:H+2, 0:W] + padded[2:H+2, 1:W+1] + padded[2:H+2, 2:W+2]
    )
    
    new = np.zeros_like(grid, dtype=bool)

    if rule == "Conway":
        survive_mask = grid & ((neighbors == 2) | (neighbors == 3))
        birth_mask = (~grid) & (neighbors == 3)
        new[survive_mask | birth_mask] = True
            
    elif rule == "HighLife":
        survive_mask = grid & ((neighbors == 2) | (neighbors == 3))
        birth_mask = (~grid) & ((neighbors == 3) | (neighbors == 6))
        new[survive_mask | birth_mask] = True
            
    elif rule == "Day&Night":
        survive_mask = grid & (((neighbors >= 3) & (neighbors <= 6)) | (neighbors == 7) | (neighbors == 8))
        birth_mask = (~grid) & ((neighbors == 3) | (neighbors == 6) | (neighbors == 7) | (neighbors == 8))
        new[survive_mask | birth_mask] = True
            
    elif rule == "Replicator":
        new[(neighbors % 2) == 1] = True
        
    elif rule == "Seeds":
        new[(~grid & (neighbors == 2))] = True
        
    elif rule == "Maze":  # B3/S12345
        born = (~grid) & (neighbors == 3)
        survive = grid & ((neighbors >= 1) & (neighbors <= 5))
        new[born | survive] = True
        
    elif rule == "Coral":  # B3/S45678
        born = (~grid) & (neighbors == 3)
        survive = grid & ((neighbors >= 4) & (neighbors <= 8))
        new[born | survive] = True
        
    elif rule == "LifeWithoutDeath":  # B3/S012345678
        born = (~grid) & (neighbors == 3)
        survive = grid
        new[born | survive] = True
                    
    elif rule == "Gnarl":  # B1/S1
        born = (~grid) & (neighbors == 1)
        survive = grid & (neighbors == 1)
        new[born | survive] = True
    
    elif rule == "Feq": # Custom rule example
        survive_mask = grid & ((neighbors == 2) | (neighbors == 4))
        birth_mask = (~grid) & (neighbors == 3)
        new[survive_mask | birth_mask] = True
    
    elif rule == "Custom": # Custom rule example
        new[(neighbors % 10 - 5) == 2] = True

    else:  # Default to Conway
        survive_mask = grid & ((neighbors == 2) | (neighbors == 3))
        birth_mask = (~grid) & (neighbors == 3)
        new[survive_mask | birth_mask] = True

    return new

def spawn_cells(grid: np.ndarray, count: int, method: str = "blocks") -> None:
    """Спавн клеток различными методами"""
    if count <= 0:
        return
    
    H, W = grid.shape
    
    if method == "random":
        # Случайный спавн
        for _ in range(count):
            r = random.randrange(H)
            c = random.randrange(W)
            grid[r, c] = True
            
    elif method == "blocks":
        # Спавн блоков 2x2
        blocks = count // 4
        for _ in range(blocks):
            r = random.randrange(H - 1)
            c = random.randrange(W - 1)
            grid[r:r+2, c:c+2] = True
            
    elif method == "gliders":
        # Спавн глайдеров
        glider = np.array([
            [0, 1, 0],
            [0, 0, 1],
            [1, 1, 1]
        ], dtype=bool)
        gliders = count // 5
        for _ in range(gliders):
            r = random.randrange(H - 3)
            c = random.randrange(W - 3)
            grid[r:r+3, c:c+3] |= glider
    elif method == "lines":
        # Спавн линий
        lines = count // 5
        for _ in range(lines):
            r = random.randrange(H)
            c = random.randrange(W - 5)
            grid[r, c:c+5] = True
    elif method == "crosses":    
        # Спавн крестов
        crosses = count // 5
        for _ in range(crosses):
            r = random.randrange(2, H - 2)
            c = random.randrange(2, W - 2)
            grid[r-2:r+3, c] = True
            grid[r, c-2:c+3] = True
    elif method == "clusters":
        # Спавн кластеров 3x3
        clusters = count // 9
        for _ in range(clusters):
            r = random.randrange(H - 2)
            c = random.randrange(W - 2)
            grid[r:r+3, c:c+3] = True
    elif method == "spirals":
        # Спавн спиралей
        spirals = count // 7
        for _ in range(spirals):
            r = random.randrange(3, H - 3)
            c = random.randrange(3, W - 3)
            grid[r-3:r+4, c] = True
            grid[r, c-3:c+4] = True
            grid[r-2:r+3, c-2:c+3] = True
            grid[r-1:r+2, c-1:c+2] = True         
    elif method == "checkerboard":
        # Шахматный спавн
        for r in range(H):
            for c in range(W):
                if (r + c) % 2 == 0 and count > 0:
                    grid[r, c] = True
                    count -= 1
                    if count <= 0:
                        break
            if count <= 0:
                break
    elif method == "spiral":
        # Спавн спиралью от центра
        r, c = H // 2, W // 2
        dr, dc = 0, 1
        steps = 1
        while count > 0:
            for _ in range(2):
                for _ in range(steps):
                    if 0 <= r < H and 0 <= c < W and count > 0:
                        grid[r, c] = True
                        count -= 1
                    r += dr
                    c += dc
                dr, dc = dc, -dr
            steps += 1
    elif method == "edges":
        # Спавн по краям
        per_side = count // (2 * (H + W))
        for i in range(per_side):
            if count <= 0: break
            grid[i, :] = True  # Верх
            count -= W
            if count <= 0: break
            grid[H - 1 - i, :] = True  # Низ
            count -= W
            if count <= 0: break
            grid[:, i] = True  # Лево
            count -= H
            if count <= 0: break
            grid[:, W - 1 - i] = True  # Право
            count -= H
    elif method == "age_based":
        # Спавн в зависимости от возраста (старые клетки)
        age_indices = np.argwhere(grid)
        if len(age_indices) > 0:
            selected = age_indices[np.random.choice(len(age_indices), min(count, len(age_indices)), replace=False)]
            for r, c in selected:
                grid[r, c] = True
    else: # default to random
        for _ in range(count):
            r = random.randrange(H)
            c = random.randrange(W)
            grid[r, c] = True
            
def clear_grid(grid: np.ndarray, clear_type: str = "full", partial_ratio: float = 0.5) -> None:
    """
    Очистка сетки различными способами.

    Args:
        grid (np.ndarray): Сетка клеточного автомата.
        clear_type (str): Тип очистки ("full", "partial", "edges").
        partial_ratio (float): Доля очищаемых клеток для "partial" (от 0.0 до 1.0, по умолчанию 0.5).
    """
    if clear_type == "full":
        grid.fill(False)
    elif clear_type == "partial":
        # Очищаем заданный процент клеток (по умолчанию 50%)
        mask = np.random.random(grid.shape) < partial_ratio
        grid[mask] = False
    elif clear_type == "edges":
        # Очищаем края
        grid[0, :] = False
        grid[-1, :] = False
        grid[:, 0] = False
        grid[:, -1] = False

# ═══════════════════════════════════════════════════════════════════════════════
#                              АУДИО ОБРАБОТКА
# ═══════════════════════════════════════════════════════════════════════════════

def audio_callback(indata, frames, time_info, status):
    """Callback функция для обработки аудио данных"""
    global audio_rms, audio_pitch
    
    if status:
        print("Audio status:", status, file=sys.stderr)
    
    # Вычисляем RMS
    rms = float(np.sqrt(np.mean(indata**2)))
    audio_rms = rms
    
    # Анализ высоты тона (если доступен librosa)
    if LIBROSA_AVAILABLE:
        try:
            pitch = float(librosa.yin(indata.flatten(), fmin=70, fmax=1500, sr=SAMPLE_RATE))
            audio_pitch = pitch
        except Exception:
            audio_pitch = 440.0
    else:
        audio_pitch = 440.0
    
    # Добавляем в очереди
    try:
        if not pitch_queue.full():
            pitch_queue.put_nowait(audio_pitch)
        if not rms_queue.full():
            rms_queue.put_nowait(audio_rms)
    except Exception:
        pass

def start_audio_stream(device_name: str = None):
    """Запуск аудио потока"""
    if not SD_AVAILABLE:
        print("⚠️  sounddevice недоступен")
        return None
    
    try:
        if device_name:
            devices = sd.query_devices()
            device_id = None
            for i, device in enumerate(devices):
                if device['name'] == device_name:
                    device_id = i
                    break
        else:
            device_id = None
        
        stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            blocksize=BLOCK_SIZE,
            dtype='float32',
            channels=CHANNELS,
            device=device_id,
            callback=audio_callback
        )
        stream.start()
        return stream
    except Exception as e:
        print(f"❌ Ошибка запуска аудио: {e}")
        return None

def choose_settings() -> Optional[Dict[str, Any]]:
    """Выбор настроек аудио устройства"""
    if not SD_AVAILABLE:
        print("⚠️ sounddevice недоступен, используем демо режим")
        return {"device": None, "layer_count": 3}
    
    try:
        devices = sd.query_devices()
        input_devices = [d for d in devices if d['max_input_channels'] > 0]
        
        if not input_devices:
            print("⚠️ Нет доступных аудио устройств")
            return {"device": None, "layer_count": 3}
        
        print("🎤 Доступные аудио устройства:")
        for i, device in enumerate(input_devices):
            print(f"  {i}: {device['name']}")
        
        # Используем первое доступное устройство
        selected_device = input_devices[0]['name']
        print(f"✅ Выбрано устройство: {selected_device}")
        
        return {
            "device": selected_device,
            "layer_count": 3,
            "mirror_x": False,
            "mirror_y": False
        }
    except Exception as e:
        print(f"❌ Ошибка выбора устройства: {e}")
        return {"device": None, "layer_count": 3}

# ═══════════════════════════════════════════════════════════════════════════════
#                                  ОСНОВНЫЕ КЛАССЫ
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Layer:
    """Слой клеточного автомата с настройками"""
    grid: np.ndarray
    age: np.ndarray
    rule: str = "Conway"
    age_palette: str = "Fire"
    rms_palette: str = "Ocean"
    color_mode: str = "HSV-дизайны"
    rms_mode: str = "brightness"
    blend_mode: str = "normal"
    rms_enabled: bool = True
    alpha_live: int = 220
    alpha_old: int = 140
    mix: str = "Normal"
    solo: bool = False
    mute: bool = False
    max_age: int = 120
    palette_mix: float = 0.5
    
    @property
    def alpha(self) -> int:
        """Средняя прозрачность слоя"""
        return (self.alpha_live + self.alpha_old) // 2
    
    @alpha.setter
    def alpha(self, value: int):
        """Установка прозрачности для живых и старых клеток"""
        self.alpha_live = value
        self.alpha_old = value

class SimpleColors:
    """Цветовая схема для UI элементов"""
    PRIMARY = (0, 150, 255)
    PRIMARY_LIGHT = (100, 180, 255)
    SECONDARY = (108, 117, 125)
    SUCCESS = (40, 167, 69)
    DANGER = (220, 53, 69)
    WARNING = (255, 193, 7)
    INFO = (23, 162, 184)
    LIGHT = (248, 249, 250)
    DARK = (52, 58, 64)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    
    # Дополнительные цвета
    GRAY_100 = (248, 249, 250)
    GRAY_200 = (233, 236, 239)
    GRAY_300 = (206, 212, 218)
    GRAY_400 = (173, 181, 189)
    GRAY_500 = (108, 117, 125)
    GRAY_600 = (73, 80, 87)
    GRAY_700 = (52, 58, 64)
    GRAY_800 = (33, 37, 41)
    GRAY_900 = (13, 27, 42)

class PaletteState:
    """Состояние системы палитр"""
    def __init__(self):
        self.current_age_palette = "Fire"
        self.current_rms_palette = "Ocean"
        self.palette_mix = 0.5
        self.auto_cycle = False
        self.cycle_speed = 1.0
        self.last_cycle_time = 0.0
    
    def update(self, dt: float):
        """Обновление состояния палитр"""
        if self.auto_cycle:
            self.last_cycle_time += dt
            if self.last_cycle_time >= self.cycle_speed:
                self.cycle_palette()
                self.last_cycle_time = 0.0
    
    def cycle_palette(self):
        """Переключение на следующую палитру"""
        current_index = ALL_PALETTES.index(self.current_age_palette)
        next_index = (current_index + 1) % len(ALL_PALETTES)
        self.current_age_palette = ALL_PALETTES[next_index]

# ═══════════════════════════════════════════════════════════════════════════════
#                                  UI КОМПОНЕНТЫ
# ═══════════════════════════════════════════════════════════════════════════════

class UISlider:
    """Интерактивный слайдер"""
    def __init__(self, x: int, y: int, width: int, height: int, 
                 min_val: float, max_val: float, current_val: float, 
                 label: str = "", value_format: str = "{:.1f}"):
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
    
    def handle_event(self, event: pygame.event.Event) -> bool:
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
    
    def _update_value_from_mouse(self, mouse_pos: Tuple[int, int]):
        """Обновление значения по позиции мыши"""
        rel_x = mouse_pos[0] - self.rect.x
        ratio = max(0.0, min(1.0, rel_x / self.width))
        self.current_val = self.min_val + ratio * (self.max_val - self.min_val)
    
    def draw(self, surface: pygame.Surface, font: pygame.font.Font):
        """Отрисовка слайдера"""
        # Фон слайдера
        bg_color = SimpleColors.GRAY_300 if self.dragging else SimpleColors.GRAY_200
        pygame.draw.rect(surface, bg_color, self.rect, border_radius=4)
        
        # Заполнение
        ratio = (self.current_val - self.min_val) / (self.max_val - self.min_val)
        fill_width = int(self.width * ratio)
        if fill_width > 0:
            fill_rect = pygame.Rect(self.x, self.y, fill_width, self.height)
            fill_color = SimpleColors.PRIMARY if self.dragging else SimpleColors.PRIMARY_LIGHT
            pygame.draw.rect(surface, fill_color, fill_rect, border_radius=4)
        
        # Бордер
        border_color = SimpleColors.PRIMARY if self.dragging else SimpleColors.GRAY_400
        pygame.draw.rect(surface, border_color, self.rect, 2, border_radius=4)
        
        # Ползунок
        if fill_width > 0:
            handle_x = self.x + fill_width
            handle_y = self.y + self.height // 2
            handle_color = SimpleColors.WHITE
            pygame.draw.circle(surface, handle_color, (handle_x, handle_y), 6)
            pygame.draw.circle(surface, border_color, (handle_x, handle_y), 6, 2)
        
        # Текст
        if self.label:
            try:
                label_text = f"{self.label}: {self.value_format.format(self.current_val)}"
                text_color = SimpleColors.DARK
                text_surface = font.render(label_text, True, text_color)
                text_y = self.y - 20
                surface.blit(text_surface, (self.x, text_y))
            except Exception:
                pass

class UIButton:
    """Интерактивная кнопка"""
    def __init__(self, x: int, y: int, width: int, height: int, 
                 label: str, is_toggle: bool = False, active: bool = False):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.label = label
        self.is_toggle = is_toggle
        self.active = active
        self.rect = pygame.Rect(x, y, width, height)
        self.pressed = False
    
    def handle_event(self, event: pygame.event.Event) -> bool:
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
    
    def draw(self, surface: pygame.Surface, font: pygame.font.Font):
        """Отрисовка кнопки"""
        # Цвета в зависимости от состояния
        if self.is_toggle and self.active:
            bg_color = SimpleColors.SUCCESS
            text_color = SimpleColors.WHITE
        elif self.pressed:
            bg_color = SimpleColors.PRIMARY
            text_color = SimpleColors.WHITE
        else:
            bg_color = SimpleColors.LIGHT
            text_color = SimpleColors.DARK
        
        # Фон кнопки
        pygame.draw.rect(surface, bg_color, self.rect, border_radius=4)
        
        # Бордер
        border_color = SimpleColors.GRAY_400
        pygame.draw.rect(surface, border_color, self.rect, 2, border_radius=4)
        
        # Текст
        try:
            text_surface = font.render(self.label, True, text_color)
            text_rect = text_surface.get_rect(center=self.rect.center)
            surface.blit(text_surface, text_rect)
        except Exception:
            pass

class UIComboBox:
    """Выпадающий список"""
    def __init__(self, x: int, y: int, width: int, height: int, 
                 label: str, options: List[str], selected_index: int = 0):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.label = label
        self.options = options
        self.selected_index = selected_index
        self.expanded = False
        self.rect = pygame.Rect(x, y, width, height)
        self.dropdown_height = min(200, len(options) * 25)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Обработка событий мыши"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.expanded = not self.expanded
                return True
            elif self.expanded:
                # Проверяем клик по элементам списка
                dropdown_rect = pygame.Rect(self.x, self.y + self.height, 
                                          self.width, self.dropdown_height)
                if dropdown_rect.collidepoint(event.pos):
                    relative_y = event.pos[1] - (self.y + self.height)
                    item_index = relative_y // 25
                    if 0 <= item_index < len(self.options):
                        self.selected_index = item_index
                        self.expanded = False
                        return True
                else:
                    self.expanded = False
        return False
    
    def draw(self, surface: pygame.Surface, font: pygame.font.Font):
        """Отрисовка комбобокса"""
        # Основное поле
        bg_color = SimpleColors.WHITE
        pygame.draw.rect(surface, bg_color, self.rect, border_radius=4)
        pygame.draw.rect(surface, SimpleColors.GRAY_400, self.rect, 2, border_radius=4)
        
        # Текст выбранного элемента
        if 0 <= self.selected_index < len(self.options):
            selected_text = self.options[self.selected_index]
            try:
                text_surface = font.render(selected_text, True, SimpleColors.DARK)
                text_rect = text_surface.get_rect(midleft=(self.x + 10, self.rect.centery))
                surface.blit(text_surface, text_rect)
            except Exception:
                pass
        
        # Стрелка
        arrow_x = self.x + self.width - 20
        arrow_y = self.rect.centery
        points = [(arrow_x, arrow_y - 5), (arrow_x + 10, arrow_y - 5), (arrow_x + 5, arrow_y + 5)]
        pygame.draw.polygon(surface, SimpleColors.GRAY_600, points)
        
        # Выпадающий список
        if self.expanded:
            dropdown_rect = pygame.Rect(self.x, self.y + self.height, 
                                      self.width, self.dropdown_height)
            pygame.draw.rect(surface, SimpleColors.WHITE, dropdown_rect)
            pygame.draw.rect(surface, SimpleColors.GRAY_400, dropdown_rect, 2)
            
            for i, option in enumerate(self.options[:self.dropdown_height // 25]):
                item_rect = pygame.Rect(self.x, self.y + self.height + i * 25, 
                                      self.width, 25)
                
                # Подсветка при наведении
                mouse_pos = pygame.mouse.get_pos()
                if item_rect.collidepoint(mouse_pos):
                    pygame.draw.rect(surface, SimpleColors.GRAY_200, item_rect)
                
                # Текст опции
                try:
                    text_surface = font.render(option, True, SimpleColors.DARK)
                    text_rect = text_surface.get_rect(midleft=(self.x + 10, item_rect.centery))
                    surface.blit(text_surface, text_rect)
                except Exception:
                    pass

# ═══════════════════════════════════════════════════════════════════════════════
#                                МЕНЕДЖЕРЫ И HUD
# ═══════════════════════════════════════════════════════════════════════════════

class LayerConfig:
    """Конфигурация слоя"""
    def __init__(self):
        self.rule = "Conway"
        self.age_palette = "Fire"
        self.rms_palette = "Ocean"
        self.rms_mode = "brightness"
        self.max_age = 120
        self.palette_mix = 0.5
        self.alpha_live = 220
        self.alpha_old = 140
        self.solo = False
        self.mute = False
        self.rms_enabled = True

class LayerGenerator:
    """Генератор слоев с различными настройками"""
    
    @staticmethod
    def create_random_layer(grid_shape: Tuple[int, int]) -> Layer:
        """Создание случайного слоя"""
        grid = _create_optimized_grid(*grid_shape)
        age = _create_optimized_age_array(*grid_shape)
        
        # Случайные настройки
        rule = random.choice(CA_RULES)
        age_palette = random.choice(ALL_PALETTES)
        rms_palette = random.choice(ALL_PALETTES)
        
        return Layer(
            grid=grid,
            age=age,
            rule=rule,
            age_palette=age_palette,
            rms_palette=rms_palette,
            max_age=random.randint(60, 180),
            palette_mix=random.uniform(0.2, 0.8)
        )
    
    @staticmethod
    def create_preset_layer(preset_name: str, grid_shape: Tuple[int, int]) -> Layer:
        """Создание слоя по пресету"""
        grid = _create_optimized_grid(*grid_shape)
        age = _create_optimized_age_array(*grid_shape)
        
        presets = {
            "Fire": Layer(grid=grid, age=age, rule="Conway", age_palette="Fire", rms_palette="Sunset", max_age=120, palette_mix=0.5),
            "Ocean": Layer(grid=grid, age=age, rule="HighLife", age_palette="Ocean", rms_palette="DeepSea", max_age=120, palette_mix=0.5),
            "Neon": Layer(grid=grid, age=age, rule="Day&Night", age_palette="Neon", rms_palette="Cyberpunk", max_age=120, palette_mix=0.5),
            "Nature": Layer(grid=grid, age=age, rule="Coral", age_palette="Forest", rms_palette="Spring", max_age=120, palette_mix=0.5)
        }
        
        # Use case-insensitive lookup and safe fallback
        return presets.get(preset_name.lower(), presets.get("Fire"))

class RenderManager:
    """Менеджер рендеринга слоев"""
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.effects_enabled = True
        self.performance_mode = False
    
    def render_layer(self, layer: Layer, surface: pygame.Surface, 
                    rms: float, pitch: float, config: Dict[str, Any]):
        """Рендеринг одного слоя"""
        if layer.mute:
            return
        
        # Создаем цветное изображение слоя
        img = self.build_color_image(layer, rms, config)

        # Конвертируем в pygame surface
        try:
            layer_surface = pygame.surfarray.make_surface(img.swapaxes(0, 1))
            scaler = pygame.transform.smoothscale if config.get('smooth_scale') else pygame.transform.scale
            # ⬆️ Создаем поверхность (размер сетки), затем масштабируем до пиксельного размера экрана
            try:
                gh, gw = layer.grid.shape
                target_w = gw * CELL_SIZE
                target_h = gh * CELL_SIZE
                if (target_w, target_h) != (self.width, self.height):
                    # На случай рассинхронизации размеров берем целевое из grid*CELL_SIZE
                    layer_surface = scaler(layer_surface, (target_w, target_h))
                else:
                    layer_surface = scaler(layer_surface, (self.width, self.height))
            except Exception:
                # Fallback на безопасный масштаб
                layer_surface = scaler(layer_surface, (self.width, self.height))
            # Применяем прозрачность
            if layer.alpha < 255:
                layer_surface.set_alpha(layer.alpha)
            # Блендинг
            if layer.blend_mode == "add":
                surface.blit(layer_surface, (0, 0), special_flags=pygame.BLEND_ADD)
            elif layer.blend_mode == "multiply":
                surface.blit(layer_surface, (0, 0), special_flags=pygame.BLEND_MULT)
            elif layer.blend_mode == "normal":
                surface.blit(layer_surface, (0, 0))
            elif layer.blend_mode == "divide":
                surface.blit(layer_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
            elif layer.blend_mode == "difference":
                surface.blit(layer_surface, (0, 0), special_flags=pygame.BLEND_RGB_SUB)
            elif layer.blend_mode == "modulate":
                surface.blit(layer_surface, (0, 0), special_flags=pygame.BLEND_MULT)
            elif layer.blend_mode == "subtract":
                surface.blit(layer_surface, (0, 0), special_flags=pygame.BLEND_SUB)
            elif layer.blend_mode == "screen":
                surface.blit(layer_surface, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
            elif layer.blend_mode == "overlay":
                surface.blit(layer_surface, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
            elif layer.blend_mode == "invert":
                # Direct pixel inversion for performance
                arr = pygame.surfarray.pixels3d(layer_surface)
                inverted_arr = 255 - arr
                inverted_surface = pygame.surfarray.make_surface(inverted_arr)
                surface.blit(inverted_surface, (0, 0))
            elif layer.blend_mode == "darken":
                surface.blit(layer_surface, (0, 0), special_flags=pygame.BLEND_RGB_MIN)
            elif layer.blend_mode == "lighten":
                surface.blit(layer_surface, (0, 0), special_flags=pygame.BLEND_MAX)
            else:
                surface.blit(layer_surface, (0, 0))
        except Exception as e:
            print(f"❌ Ошибка рендеринга слоя: {e}")
    
    def _get_palette_hsvs(self, palette_name: str, t: np.ndarray) -> np.ndarray:
        """Возвращает HSV значения для заданной палитры и массива t."""
        if palette_name == "Fire":
            return np.array([hue_fire_from_t(tt) for tt in t])
        elif palette_name == "Ocean":
            return np.array([hue_ocean_from_t(tt) for tt in t])
        elif palette_name == "Neon":
            return np.array([hue_neon_from_t(tt) for tt in t])
        elif palette_name == "Ukraine":
            return np.array([hue_ukraine_from_t(tt) for tt in t])
        else:
            hsvs = np.zeros((len(t), 3))
            hsvs[:, 0] = np.array([hue_bgyr_from_t(tt) for tt in t])
            hsvs[:, 1] = 0.85
            hsvs[:, 2] = 1.0
            return hsvs

    def build_color_image(self, layer: Layer, rms: float, config: Dict[str, Any]) -> np.ndarray:
        """
        Создание цветного изображения слоя.

        Args:
            layer (Layer): Слой клеточного автомата.
            rms (float): Значение RMS аудио.
            config (Dict[str, Any]): Конфигурация рендера.

        Returns:
            np.ndarray: Массив формы (H, W, 3) и типа np.uint8, где H и W — размеры сетки.
        """
        H, W = layer.grid.shape
        img = np.zeros((H, W, 3), dtype=np.uint8)

        # Параметры из конфига
        rms_strength = config.get('rms_strength', 100) / 100.0
        fade_start = config.get('fade_start', 60)
        sat_drop = config.get('fade_sat_drop', 70)
        val_drop = config.get('fade_val_drop', 60)
        v_mul = config.get('global_v_mul', 1.0)
        cmin = config.get('color_rms_min', 0.004)
        cmax = config.get('color_rms_max', DEFAULT_COLOR_RMS_MAX)

        # Находим живые клетки
        mask = layer.grid
        ages = layer.age[mask]
        ages = np.where(ages <= 0, 1, ages)
        t = np.clip(ages / max(1, layer.max_age), 0, 1)

        # Выбираем палитру
        hsvs = self._get_palette_hsvs(layer.age_palette, t)
        h, s, v = hsvs[:, 0], hsvs[:, 1], hsvs[:, 2]

        # Модификация по RMS
        if layer.rms_enabled and layer.rms_mode != "disabled":
            rms_factor = clamp01((rms - cmin) / max(0.001, cmax - cmin))
            if layer.rms_mode == "brightness":
                v *= (0.3 + 0.7 * rms_factor)
            elif layer.rms_mode == "palette":
                rms_hsvs = self._get_palette_hsvs(layer.rms_palette, np.full_like(t, rms_factor))
                mix = layer.palette_mix
                h = h * (1 - mix) + rms_hsvs[:, 0] * mix
                s = s * (1 - mix) + rms_hsvs[:, 1] * mix
                v = v * (1 - mix) + rms_hsvs[:, 2] * mix

        # Затухание старых клеток
        fade_mask = ages > fade_start
        if np.any(fade_mask):
            fade_factor = np.clip((ages[fade_mask] - fade_start) / max(1, layer.max_age - fade_start), 0, 1)
            s[fade_mask] *= (1.0 - fade_factor * sat_drop / 100.0)
            v[fade_mask] *= (1.0 - fade_factor * val_drop / 100.0)

        # Глобальный множитель яркости
        v *= v_mul

        # Конвертируем в RGB
        rgb = np.array([_cached_hsv_to_rgb(hh, ss, vv) for hh, ss, vv in zip(h, s, v)], dtype=np.uint8)
        ys, xs = np.nonzero(mask)
        img[ys, xs] = rgb

        return img

class HUD:
    """Head-Up Display для отображения информации и управления"""
    def __init__(self, font: pygame.font.Font, screen_height: int, layer_count: int = 3):
        self.font = font
        self.visible = True
        self.screen_height = screen_height
        self.layer_count = layer_count
        self.panel_x = GRID_W * CELL_SIZE + 10
        self.panel_y = 10
        self.panel_width = HUD_WIDTH - 20
        
        # UI элементы
        self.controls = {}
        self.layer_modules = []
        
        # Инициализация элементов управления
        self._create_global_controls()
        self._create_layer_modules()
    
    def _create_global_controls(self):
        """Создание глобальных элементов управления"""
        y_offset = self.panel_y
        
        # Глобальные настройки
        self.controls['global_speed'] = UISlider(
            self.panel_x, y_offset, 200, 20,
            1, 60, 30, "Скорость", "{:.0f} FPS"
        )
        y_offset += 40
        
        self.controls['global_volume'] = UISlider(
            self.panel_x, y_offset, 200, 20,
            0.0, 2.0, 1.0, "Громкость", "{:.1f}"
        )
        y_offset += 40
        
        # Тумблер сглаженного масштабирования
        self.controls['smooth_scale'] = UIButton(
            self.panel_x, y_offset, 160, 25,
            'Smooth Scale', is_toggle=True, active=False
        )
        y_offset += 35

        # Кнопки управления
        button_width = 80
        button_height = 25
        
        self.controls['play_pause'] = UIButton(
            self.panel_x, y_offset, button_width, button_height,
            "PAUSE", is_toggle=True
        )
        
        self.controls['clear_all'] = UIButton(
            self.panel_x + button_width + 10, y_offset, button_width, button_height,
            "CLEAR"
        )
        
        self.controls['randomize'] = UIButton(
            self.panel_x + 2 * (button_width + 10), y_offset, button_width, button_height,
            "RANDOM"
        )
    
    def _create_layer_modules(self):
        """Создание модулей управления слоями"""
        start_y = self.panel_y + 120
        module_height = 150
        
        for i in range(self.layer_count):
            module = self._create_layer_module(i, start_y + i * (module_height + 10))
            self.layer_modules.append(module)
    
    def _create_layer_module(self, layer_index: int, y_pos: int) -> Dict[str, Any]:
        """Создание модуля управления одним слоем"""
        module = {'controls': {}, 'y': y_pos, 'height': 140}
        
        x_left = self.panel_x 
        x_right = self.panel_x + 250
        control_height = 20
        button_width = 60
        
        current_y = y_pos + 25
        
        # Правило автомата
        module['controls']['rule'] = UIComboBox(
            x_left, current_y, 120, control_height,
            "Rule", CA_RULES, 0
        )
        
        # Возрастная палитра
        module['controls']['age_palette'] = UIComboBox(
            x_right, current_y, 120, control_height,
            "Age Palette", ALL_PALETTES[:60], 0  # Ограничиваем для UI
        )
        current_y += 30
        
        # RMS палитра
        module['controls']['rms_palette'] = UIComboBox(
            x_left, current_y, 120, control_height,
            "RMS Palette", ALL_PALETTES[:10], 1
        )
        
        # Максимальный возраст
        module['controls']['max_age'] = UISlider(
            x_right, current_y, 120, control_height,
            30, 300, 120, "Max Age", "{:.0f}"
        )
        current_y += 30
        
        # Микс палитр
        module['controls']['palette_mix'] = UISlider(
            x_left, current_y, 200, control_height,
            0.0, 1.0, 0.5, "Palette Mix", "{:.2f}"
        )
        current_y += 30
        
        # Прозрачность
        module['controls']['alpha'] = UISlider(
            x_left, current_y, 200, control_height,
            0, 255, 220, "Alpha", "{:.0f}"
        )
        current_y += 30
        
        # Кнопки Solo, Mute
        module['controls']['solo'] = UIButton(
            x_left, current_y, button_width, control_height,
            "SOLO", is_toggle=True, active=False
        )
        
        module['controls']['mute'] = UIButton(
            x_left + button_width + 10, current_y, button_width, control_height,
            "MUTE", is_toggle=True, active=False
        )
        
        module['controls']['spawn'] = UIButton(
            x_left + 2 * (button_width + 10), current_y, button_width, control_height,
            "SPAWN"
        )
        
        return module
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Обработка событий UI"""
        if not self.visible:
            return False
        
        # Глобальные контролы
        for control in self.controls.values():
            if control.handle_event(event):
                return True
        
        # Контролы слоев
        for module in self.layer_modules:
            for control in module['controls'].values():
                if control.handle_event(event):
                    return True
        
        return False
    
    def draw(self, surface: pygame.Surface, info: Dict[str, Any]):
        """Отрисовка HUD"""
        if not self.visible:
            return
        
        try:
            # Фон панели
            panel_rect = pygame.Rect(self.panel_x - 5, self.panel_y - 5, 
                                   self.panel_width + 10, self.screen_height - 20)
            pygame.draw.rect(surface, (20, 25, 30, 180), panel_rect, border_radius=8)
            pygame.draw.rect(surface, SimpleColors.GRAY_600, panel_rect, 2, border_radius=8)
            
            # Заголовок
            title_font = pygame.font.Font(None, 28)
            title = title_font.render("Guitar Life v21", True, SimpleColors.WHITE)
            surface.blit(title, (self.panel_x, self.panel_y))
            
            # Информация о производительности
            info_y = self.panel_y + 35
            for key, value in info.items():
                if isinstance(value, (int, float)):
                    text = f"{key}: {value:.1f}" if isinstance(value, float) else f"{key}: {value}"
                else:
                    text = f"{key}: {value}"
                
                info_surface = self.font.render(text, True, SimpleColors.GRAY_300)
                surface.blit(info_surface, (self.panel_x, info_y))
                info_y += 18
            
            # Глобальные контролы
            for control in self.controls.values():
                control.draw(surface, self.font)
            
            # Модули слоев
            for i, module in enumerate(self.layer_modules):
                # Заголовок слоя
                layer_title = f"Layer {i + 1}"
                layer_font = pygame.font.Font(None, 20)
                layer_surface = layer_font.render(layer_title, True, SimpleColors.WHITE)
                surface.blit(layer_surface, (self.panel_x, module['y']))
                
                # Контролы слоя
                for control in module['controls'].values():
                    control.draw(surface, self.font)
                
                # Разделитель
                separator_y = module['y'] + module['height']
                pygame.draw.line(surface, SimpleColors.GRAY_600, 
                               (self.panel_x, separator_y), 
                               (self.panel_x + self.panel_width, separator_y), 1)
            
        except Exception as e:
            print(f"❌ Ошибка отрисовки HUD: {e}")

# ═══════════════════════════════════════════════════════════════════════════════
#                              ОСНОВНОЕ ПРИЛОЖЕНИЕ
# ═══════════════════════════════════════════════════════════════════════════════

class App:
    """Главное приложение Guitar Life"""
    
    def __init__(self, config: Dict[str, Any]):
        """Инициализация приложения"""
        print("🚀 Инициализация Guitar Life v21...")
        
        # Инициализация pygame
        pygame.init()
        
        # Настройки экрана
        self.W = GRID_W * CELL_SIZE
        self.H = GRID_H * CELL_SIZE
        self.screen = pygame.display.set_mode((self.W + HUD_WIDTH, self.H))
        pygame.display.set_caption("Guitar Life v21 - Structured")
        
        self.smooth_scale = False  # UI тумблер сглаженного масштабирования
        # Основные компоненты
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 16)
        self.running = True
        self.paused = False
        
        # Конфигурация
        self.config = config
        self.layer_count = config.get('layer_count', 3)
        
        # Создание слоев
        self.layers = []
        for i in range(self.layer_count):
            layer = LayerGenerator.create_random_layer((GRID_H, GRID_W))
            self.layers.append(layer)
        
        # Менеджеры
        self.render_manager = RenderManager(self.W, self.H)
        self.palette_state = PaletteState()
        
        # HUD
        self.hud = HUD(self.font, self.H, self.layer_count)
        
        # Счетчики и статистика
        self.generation = 0
        self.frame_count = 0
        self.fps_counter = 0
        self.last_fps_time = time.time()
        
        # Создание начальных паттернов
        self._create_initial_patterns()
        
        print(f"✅ Приложение инициализировано с {len(self.layers)} слоями")
    
    def _create_initial_patterns(self):
        """Создание начальных паттернов на слоях"""
        for i, layer in enumerate(self.layers):
            if i == 0:
                # Глайдеры на первом слое
                spawn_cells(layer.grid, 20, "gliders")
            elif i == 1:
                # Случайные блоки на втором слое
                spawn_cells(layer.grid, 30, "blocks")
            else:
                # Случайные клетки на остальных слоях
                spawn_cells(layer.grid, 25, "random")
        
        # Устанавливаем начальный возраст для всех клеток
        for layer in self.layers:
            layer.age[layer.grid] = 1
        
        # Проверяем что клетки созданы
        total_cells = sum(np.sum(layer.grid) for layer in self.layers)
        print(f"🎲 Создано {total_cells} начальных клеток")
    
    def handle_events(self):
        """Обработка событий"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                self._handle_keydown(event)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._handle_mouse_click(event)
            
            # Передаем события в HUD
            if self.hud.handle_event(event):
                self._sync_hud_to_layers()
    
    def _handle_keydown(self, event: pygame.event.Event):
        """Обработка нажатий клавиш"""
        key = event.key
        
        if key == pygame.K_ESCAPE:
            self.running = False
        elif key == pygame.K_SPACE:
            self.paused = not self.paused
        elif key == pygame.K_TAB:
            self.hud.visible = not self.hud.visible
        elif key == pygame.K_c:
            self._clear_all_layers()
        elif key == pygame.K_r:
            self._randomize_layers()
        elif key == pygame.K_F1:
            self._show_help()
        elif key == pygame.K_F12 and SETTINGS_WINDOW_AVAILABLE:
            self._open_settings()
        
        # Быстрые команды для слоев
        elif pygame.K_1 <= key <= pygame.K_9:
            layer_index = key - pygame.K_1
            if layer_index < len(self.layers):
                self._toggle_layer_solo(layer_index)
    
    def _handle_mouse_click(self, event: pygame.event.Event):
        """Обработка кликов мыши"""
        mouse_x, mouse_y = event.pos
        
        # Рисование в области сетки
        if mouse_x < self.W:
            grid_x = mouse_x // CELL_SIZE
            grid_y = mouse_y // CELL_SIZE
            
            if 0 <= grid_x < GRID_W and 0 <= grid_y < GRID_H:
                # Рисуем на активном слое (первом не заглушенном)
                for layer in self.layers:
                    if not layer.mute:
                        layer.grid[grid_y, grid_x] = not layer.grid[grid_y, grid_x]
                        if layer.grid[grid_y, grid_x]:
                            layer.age[grid_y, grid_x] = 0
                        break
    
    def _sync_hud_to_layers(self):
        """Синхронизация настроек HUD с слоями"""
        # Глобальные настройки из HUD
        if 'smooth_scale' in self.hud.controls:
            self.smooth_scale = self.hud.controls['smooth_scale'].active
        for i, (layer, module) in enumerate(zip(self.layers, self.hud.layer_modules)):
            controls = module['controls']
            
            # Обновляем настройки слоя из UI
            if 'rule' in controls:
                rule_combo = controls['rule']
                if 0 <= rule_combo.selected_index < len(CA_RULES):
                    layer.rule = CA_RULES[rule_combo.selected_index]
            
            if 'max_age' in controls:
                layer.max_age = int(controls['max_age'].current_val)
            
            if 'palette_mix' in controls:
                layer.palette_mix = controls['palette_mix'].current_val
            
            if 'alpha' in controls:
                layer.alpha = int(controls['alpha'].current_val)
            
            if 'solo' in controls:
                layer.solo = controls['solo'].active
            
            if 'mute' in controls:
                layer.mute = controls['mute'].active
    
    def update_simulation(self):
        """Обновление симуляции клеточных автоматов"""
        if self.paused:
            return
        
        # Обновляем только каждые несколько кадров для контроля скорости
        if self.frame_count % 2 == 0:  # Каждый второй кадр
            for layer in self.layers:
                if not layer.mute:
                    # Обновляем возраст живых клеток
                    layer.age[layer.grid] += 1
                    
                    # Применяем правило клеточного автомата
                    new_grid = step_life(layer.grid, layer.rule)
                    
                    # Сбрасываем возраст новых клеток
                    new_cells = new_grid & ~layer.grid
                    layer.age[new_cells] = 0
                    
                    # Обнуляем возраст мертвых клеток
                    dead_cells = ~new_grid & layer.grid
                    layer.age[dead_cells] = 0
                    
                    # Обновляем сетку
                    layer.grid[:] = new_grid
            
            self.generation += 1
        
        # Обновляем состояние палитр
        dt = 1.0 / FPS
        self.palette_state.update(dt)
    
    def render(self):
        """Рендеринг кадра"""
        # Очищаем экран
        self.screen.fill(BG_COLOR)

        # Синхронизируем HUD/UI с слоями перед рендерингом
        self._sync_hud_to_layers()

        # Создаем поверхность для поля (field), размером GRID_W * CELL_SIZE x GRID_H * CELL_SIZE
        field_width = GRID_W * CELL_SIZE
        field_height = GRID_H * CELL_SIZE
        layer_surface = pygame.Surface((field_width, field_height))
        layer_surface.fill(BG_COLOR)

        # Рендерим каждый слой
        render_config = {
            'rms_strength': 100,
            'fade_start': 60,
            'fade_sat_drop': 70,
            'fade_val_drop': 60,
            'global_v_mul': 1.0,
            'color_rms_min': 0.004,
            'color_rms_max': DEFAULT_COLOR_RMS_MAX,
            'smooth_scale': getattr(self, 'smooth_scale', False)
        }

        for layer in self.layers:
            if not layer.mute:
                cells_count = np.sum(layer.grid)
                if cells_count > 0:
                    self.render_manager.render_layer(
                        layer, layer_surface, audio_rms, audio_pitch, render_config
                    )

        # Применяем глобальные эффекты (если включены)
            if self.render_manager.effects_enabled:
                # Примеры эффектов - можно настроить через UI
                if hasattr(self, 'trail_strength') and self.trail_strength > 0:
                    apply_trails(layer_surface, self.trail_strength)

            # Копируем поле на основной экран (слева)
            self.screen.blit(layer_surface, (0, 0))
            # Рисуем HUD справа от поля
            self.hud.draw(self.screen, self._gather_info())

    
    def _gather_info(self) -> Dict[str, Any]:
        """Сбор информации для отображения"""
        total_cells = sum(np.sum(layer.grid) for layer in self.layers if not layer.mute)
        active_layers = sum(1 for layer in self.layers if not layer.mute)
        
        return {
            'Generation': self.generation,
            'FPS': self.fps_counter,
            'Total Cells': total_cells,
            'Active Layers': active_layers,
            'Audio RMS': f"{audio_rms:.4f}",
            'Audio Pitch': f"{audio_pitch:.1f} Hz",
            'Status': 'PAUSED' if self.paused else 'RUNNING'
        }
    
    def _clear_all_layers(self):
        """Очистка всех слоев"""
        for layer in self.layers:
            clear_grid(layer.grid, "Полная очистка")
            layer.age.fill(0)
        print("🧹 Все слои очищены")
    
    def _randomize_layers(self):
        """Случайная генерация паттернов на слоях"""
        for layer in self.layers:
            clear_grid(layer.grid, "Полная очистка")
            spawn_cells(layer.grid, random.randint(20, 50), 
                        random.choice(["random", "blocks", "gliders"]))
            layer.age.fill(0)
        print("🎲 Слои рандомизированы")
    
    def _toggle_layer_solo(self, layer_index: int):
        """Переключение solo режима слоя"""
        if 0 <= layer_index < len(self.layers):
            layer = self.layers[layer_index]
            layer.solo = not layer.solo
            
            # Если включили solo, выключаем у остальных
            if layer.solo:
                for i, other_layer in enumerate(self.layers):
                    if i != layer_index:
                        other_layer.solo = False
            
            print(f"🎵 Layer {layer_index + 1} solo: {layer.solo}")
    
    def _show_help(self):
        """Показать справку по горячим клавишам"""
        help_text = """
        GUITAR LIFE v21 - Горячие клавиши:
        
        ESC - Выход
        SPACE - Пауза/Продолжение
        TAB - Показать/скрыть HUD
        C - Очистить все слои
        R - Рандомизировать слои
        F1 - Эта справка
        F12 - Окно настроек
        1-9 - Solo слоя
        
        Мышь - Рисование в области сетки
        """
        print(help_text)
    
    def _open_settings(self):
        """Открытие окна настроек"""
        try:
            settings_window = SettingsWindow()
            settings_window.show()
        except Exception as e:
            print(f"❌ Ошибка открытия настроек: {e}")
    
    def run(self):
        """Главный цикл приложения"""
        print("🎯 Запуск главного цикла...")
        
        while self.running:
            frame_start = time.time()
            
            # Обработка событий
            self.handle_events()
            
            # Обновление симуляции
            self.update_simulation()
            
            # Рендеринг
            self.render()
            
            # Обновление экрана
            pygame.display.flip()
            
            # Ограничение FPS
            self.clock.tick(FPS)
            
            # Подсчет FPS
            self.frame_count += 1
            current_time = time.time()
            if current_time - self.last_fps_time >= 1.0:
                self.fps_counter = int(self.frame_count / (current_time - self.last_fps_time))
                self.frame_count = 0
                self.last_fps_time = current_time
            
            # Профилирование (каждые 60 кадров)
            if self.frame_count % 60 == 0:
                frame_time = time.time() - frame_start
                if frame_time > 0.02:  # Если кадр дольше 20мс
                    print(f"⚠️  Медленный кадр: {frame_time*1000:.1f}ms")
        
        print("👋 Завершение приложения...")
        pygame.quit()

# ═══════════════════════════════════════════════════════════════════════════════
#                                 ТОЧКА ВХОДА
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """Главная функция запуска приложения"""
    print("🎸 GUITAR LIFE v21 - Structured Edition")
    
    try:
        # Выбор настроек аудио
        print("🔧 Настройка аудио...")
        config = choose_settings()
        if not config:
            print("❌ Не удалось настроить аудио")
            return
        
        # Запуск аудио потока
        print("🎵 Запуск аудио потока...")
        audio_stream = start_audio_stream(config.get('device'))
        
        try:
            # Создание и запуск приложения
            print("🚀 Создание приложения...")
            app = App(config)
            
            print("▶️  Запуск Guitar Life v21!")
            print("   Нажмите F1 для справки по управлению")
            print("   Нажмите ESC для выхода")
            print("-" * 50)
            
            app.run()
            
        finally:
            # Остановка аудио потока
            if audio_stream:
                try:
                    audio_stream.stop()
                    audio_stream.close()
                    print("🔇 Аудио поток остановлен")
                except Exception:
                    pass
    
    except KeyboardInterrupt:
        print("\n⏹️  Прерывание пользователем (Ctrl+C)")
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
    
    print("✅ Guitar Life v21 завершен")

if __name__ == "__main__":
    main()
