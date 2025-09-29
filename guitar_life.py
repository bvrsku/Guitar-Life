#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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
from functools import lru_cache

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

# Константы сетки
GRID_W = 98
GRID_H = 55
CELL_SIZE = 10

# === UI COLORS ===
class SimpleColors:
    """Расширенная палитра цветов для современного UI"""
    PRIMARY = (0, 150, 255)
    PRIMARY_LIGHT = (100, 180, 255)
    GRAY_50 = (248, 250, 252)
    GRAY_100 = (241, 245, 249)
    GRAY_400 = (156, 163, 175)
    GRAY_700 = (55, 65, 81)
    GRAY_800 = (31, 41, 55)
    GRAY_900 = (17, 24, 39)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    
    # Дополнительные цвета для UI
    SURFACE = (248, 250, 252)
    ACTIVE = (219, 234, 254)
    BORDER = (203, 213, 225)
    BORDER_FOCUS = (59, 130, 246)
    TEXT_PRIMARY = (30, 41, 59)
    TEXT_SECONDARY = (100, 116, 139)

# Константы экрана и интерфейса
HUD_WIDTH = 520
MAX_EFFECTS = 20

# Палитры
PALETTE_OPTIONS = [
    "Blue->Green->Yellow->Red",
    "Red->Yellow->White",
    "Fire",
    "Green->Cyan",
    "Purple->Pink->White",
    "Sunset",
    "Ocean",
    "Rainbow",
    "Coral",
    "Ice",
    "Jade",
    "Dark->Orange",
    "Monochrome->Red",
    "Deep Blue",
    "Volcanic"
]

# === GLOBAL AUDIO VARIABLES ===
audio_rms = 0.0
audio_pitch = 0.0
audio_gain = 1.0

# Audio queues
pitch_queue = queue.Queue(maxsize=8)
rms_queue = queue.Queue(maxsize=8)
running = True

# === UI COMPONENTS ===

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
        rel_x = mouse_pos[0] - self.rect.x
        ratio = max(0.0, min(1.0, rel_x / self.width))
        self.current_val = self.min_val + ratio * (self.max_val - self.min_val)
    
    def draw(self, surface, font):
        """Отрисовка простого современного слайдера"""
        self.x = self.rect.x
        self.y = self.rect.y
        
        bg_color = SimpleColors.GRAY_100 if self.dragging else SimpleColors.GRAY_50
        pygame.draw.rect(surface, bg_color, self.rect, border_radius=8)
        
        ratio = (self.current_val - self.min_val) / (self.max_val - self.min_val)
        fill_width = int(self.width * ratio)
        if fill_width > 4:
            fill_rect = pygame.Rect(self.x, self.y, fill_width, self.height)
            fill_color = SimpleColors.PRIMARY if self.dragging else SimpleColors.PRIMARY_LIGHT
            pygame.draw.rect(surface, fill_color, fill_rect, border_radius=8)
        
        border_color = SimpleColors.BORDER_FOCUS if self.dragging else SimpleColors.BORDER
        pygame.draw.rect(surface, border_color, self.rect, 2, border_radius=8)
        
        if fill_width > 0:
            handle_x = self.x + fill_width
            handle_y = self.y + self.height // 2
            
            handle_color = SimpleColors.PRIMARY if self.dragging else SimpleColors.GRAY_400
            pygame.draw.circle(surface, SimpleColors.SURFACE, (handle_x, handle_y), 8)
            pygame.draw.circle(surface, handle_color, (handle_x, handle_y), 6)
            pygame.draw.circle(surface, SimpleColors.BORDER, (handle_x, handle_y), 8, 2)
        
        if self.label:
            try:
                label_font = pygame.font.SysFont("times new roman,georgia,serif", 14)
                value_font = pygame.font.SysFont("times new roman,georgia,serif", 13)
            except:
                label_font = pygame.font.Font(None, 14)
                value_font = pygame.font.Font(None, 13)
            
            try:
                label_text = str(self.label).encode('ascii', 'ignore').decode('ascii')
                value_text = str(self.value_format.format(self.current_val)).encode('ascii', 'ignore').decode('ascii')
                
                label_color = SimpleColors.TEXT_PRIMARY
                value_color = SimpleColors.PRIMARY if self.dragging else SimpleColors.TEXT_SECONDARY
                
                label_surface = label_font.render(label_text, True, label_color)
                value_surface = value_font.render(value_text, True, value_color)
                
                text_y = self.y - 25
                surface.blit(label_surface, (self.x, text_y))
                value_x = self.x + self.width - value_surface.get_width()
                surface.blit(value_surface, (value_x, text_y))
                    
            except Exception as e:
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
        self.x = self.rect.x
        self.y = self.rect.y
        
        if self.is_toggle and self.active:
            bg_color = SimpleColors.PRIMARY
            border_color = SimpleColors.PRIMARY
        elif self.pressed:
            bg_color = SimpleColors.ACTIVE
            border_color = SimpleColors.BORDER_FOCUS
        else:
            bg_color = SimpleColors.SURFACE
            border_color = SimpleColors.BORDER
            
        pygame.draw.rect(surface, bg_color, self.rect, border_radius=8)
        pygame.draw.rect(surface, border_color, self.rect, 2, border_radius=8)
        
        if self.is_toggle and self.active:
            pygame.draw.circle(surface, SimpleColors.SURFACE, (self.x + 8, self.y + 8), 3)
        
        try:
            button_font = pygame.font.SysFont("times new roman,georgia,serif", 12)
        except:
            button_font = pygame.font.Font(None, 12)
            
        try:
            button_text = str(self.label).encode('ascii', 'ignore').decode('ascii')
            
            if self.is_toggle and self.active:
                text_color = SimpleColors.SURFACE
            else:
                text_color = SimpleColors.TEXT_PRIMARY
                
            text = button_font.render(button_text, True, text_color)
            text_rect = text.get_rect(center=self.rect.center)
            surface.blit(text, text_rect)
            
        except Exception as e:
            text = button_font.render("BTN", True, SimpleColors.TEXT_SECONDARY)
            text_rect = text.get_rect(center=self.rect.center)
            surface.blit(text, text_rect)

# === MAIN APPLICATION FUNCTIONS ===

def main(config):
    """Основная функция приложения"""
    print("🎸 Starting Guitar Life...")

    # Инициализация pygame
    pygame.init()

    # Создание экрана
    screen_width = GRID_W * CELL_SIZE + HUD_WIDTH
    screen_height = GRID_H * CELL_SIZE
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Guitar Life")

    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 24)

    # Создание HUD
    hud = HUD(font, screen_height, config.get('layer_count', 3))
    
    # Создание слоев
    layers = []
    for i in range(config.get('layer_count', 3)):
        grid = np.zeros((GRID_H, GRID_W), dtype=bool)
        age = np.zeros((GRID_H, GRID_W), dtype=np.uint16)
        
        layer = Layer(
            grid=grid,
            age=age,
            rule="Conway",
            age_palette="Fire",
            rms_palette="Ocean",
            color_mode="HSV-дизайны"
        )
        layers.append(layer)
    
    # Основной цикл
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_TAB:
                    hud.visible = not hud.visible
            
            hud.handle_event(event)
        
        # Обновление слоев
        for layer in layers:
            if not layer.mute:
                layer.grid = step_life(layer.grid, layer.rule)
                layer.age += 1
                layer.age[layer.grid] = 1
        
        # Отрисовка
        screen.fill((10, 10, 12))
        
        for layer in layers:
            if not layer.mute:
                cfg = {
                    'rms_strength': 100,
                    'fade_start': 60,
                    'fade_sat_drop': 70,
                    'fade_val_drop': 60,
                    'global_v_mul': 1.0,
                    'color_rms_min': 0.004,
                    'color_rms_max': 0.30
                }
                
                img = build_color_image(
                    layer.grid, layer.age, "HSV-дизайны",
                    audio_rms, audio_pitch, cfg,
                    layer.age_palette, layer.rms_palette,
                    layer.rms_mode, layer.blend_mode,
                    layer.rms_enabled, layer.max_age, layer.palette_mix
                )
                
                surface = pygame.surfarray.make_surface(img.swapaxes(0, 1))
                screen.blit(surface, (0, 0))
        
        if hud.visible:
            hud.draw(screen)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

# Helper functions for color generation
def lerp(a: float, b: float, t: float) -> float:
    """Линейная интерполяция между a и b"""
    return a + (b - a) * t

def hue_bgyr_from_t(t: float) -> float:
    """Базовая BGYR палитра: синий -> зеленый -> желтый -> красный"""
    t = max(0.0, min(1.0, t))
    if t < 1/3:   
        return lerp(220.0, 120.0, t*3.0)
    elif t < 2/3: 
        return lerp(120.0, 60.0, (t-1/3)*3.0)
    else:
        return lerp(60.0, 0.0, (t-2/3)*3.0)

def hue_fire_from_t(t: float) -> tuple[float, float, float]:
    """Огненная палитра"""
    t = max(0.0, min(1.0, t))
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

def hue_ocean_from_t(t: float) -> tuple[float, float, float]:
    """Океаническая палитра"""
    t = max(0.0, min(1.0, t))
    if t < 0.5:
        k = t/0.5
        h = lerp(220.0, 200.0, k)
        s = 1.0
        v = lerp(0.35, 0.85, k)
    else:
        k = (t-0.5)/0.5
        h = lerp(200.0, 180.0, k)
        s = lerp(1.0, 0.2, k)
        v = lerp(0.85, 1.0, k)
    return h, s, v

def hue_neon_from_t(t: float) -> tuple[float, float, float]:
    """Неоновая палитра"""
    t = max(0.0, min(1.0, t))
    if t < 1/3:      
        h = lerp(285.0, 240.0, t*3.0)
    elif t < 2/3:    
        h = lerp(240.0, 120.0, (t-1/3)*3.0)
    else:
        h = lerp(120.0, 315.0, (t-2/3)*3.0)
    s = 1.0
    v = 1.0
    return h, s, v

def hue_ukraine_from_t(t: float) -> tuple[float, float, float]:
    """Украинская палитра"""
    t = max(0.0, min(1.0, t))
    if t < 0.5:
        k = t/0.5
        h = 50.0
        s = lerp(1.0, 0.6, k)
        v = lerp(0.95, 1.0, k)
    else:
        k = (t-0.5)/0.5
        h = lerp(50.0, 220.0, k)
        s = lerp(0.6, 1.0, k)
        v = lerp(1.0, 0.9, k)
    return h, s, v

@lru_cache(maxsize=1024)
def _cached_hsv_to_rgb(h: float, s: float, v: float) -> tuple[int, int, int]:
    """Кэшированная конверсия HSV в RGB"""
    r, g, b = colorsys.hsv_to_rgb((h % 360) / 360.0, max(0.0, min(1.0, s)), max(0.0, min(1.0, v)))
    return (int(r * 255), int(g * 255), int(b * 255))

def build_color_image(layer_grid: np.ndarray, layer_age: np.ndarray, mode: str,
                      rms: float, pitch: float, cfg: dict,
                      age_palette: str, rms_palette: str, 
                      rms_mode: str = "brightness",
                      blend_mode: str = "normal",
                      rms_enabled: bool = True,
                      max_age: int = 120,
                      palette_mix: float = 0.5) -> np.ndarray:
    """Создает цветное изображение слоя на основе сетки, возраста и настроек"""
    H, W = layer_grid.shape
    img = np.zeros((H, W, 3), dtype=np.uint8)

    rms_strength = cfg.get('rms_strength', 100) / 100.0
    fade_start = cfg.get('fade_start', 60)
    sat_drop = cfg.get('fade_sat_drop', 70)
    val_drop = cfg.get('fade_val_drop', 60)
    v_mul = cfg.get('global_v_mul', 1.0)
    cmin = cfg.get('color_rms_min', 0.004)
    cmax = cfg.get('color_rms_max', 0.30)

    ys, xs = np.nonzero(layer_grid)
    
    for idx, (i, j) in enumerate(zip(ys, xs)):
        i, j = int(i), int(j)
        
        if i < 0 or i >= H or j < 0 or j >= W:
            continue
            
        age = int(layer_age[i, j])
        
        if age > 0:
            t = min(1.0, age / max(1, max_age))
            
            if age_palette == "Fire":
                h, s, v = hue_fire_from_t(t)
            elif age_palette == "Ocean":
                h, s, v = hue_ocean_from_t(t)
            elif age_palette == "Neon":
                h, s, v = hue_neon_from_t(t)
            elif age_palette == "Ukraine":
                h, s, v = hue_ukraine_from_t(t)
        else:
                h = hue_bgyr_from_t(t)
                s, v = 0.85, 1.0
            
        if rms_enabled and rms_mode != "disabled":
            rms_factor = max(0.0, min(1.0, (rms - cmin) / max(0.001, cmax - cmin)))
            
            if rms_mode == "brightness":
                v *= (0.3 + 0.7 * rms_factor)
            elif rms_mode == "palette":
                if rms_palette == "Fire":
                    rms_h, rms_s, rms_v = hue_fire_from_t(rms_factor)
                elif rms_palette == "Ocean":
                    rms_h, rms_s, rms_v = hue_ocean_from_t(rms_factor)
                elif rms_palette == "Neon":
                    rms_h, rms_s, rms_v = hue_neon_from_t(rms_factor)
                elif rms_palette == "Ukraine":
                    rms_h, rms_s, rms_v = hue_ukraine_from_t(rms_factor)
            else:
                rms_h = hue_bgyr_from_t(rms_factor)
                rms_s, rms_v = 0.85, 1.0
            
                h = h * (1 - palette_mix) + rms_h * palette_mix
                s = s * (1 - palette_mix) + rms_s * palette_mix
                v = v * (1 - palette_mix) + rms_v * palette_mix
            
            if age > fade_start:
                fade_factor = min(1.0, (age - fade_start) / max(1, max_age - fade_start))
                s *= (1.0 - fade_factor * sat_drop / 100.0)
                v *= (1.0 - fade_factor * val_drop / 100.0)
            
            v *= v_mul
            
            r, g, b = _cached_hsv_to_rgb(h, s, v)
            img[i, j] = [r, g, b]
    
    return img

def start_audio_stream(device_name):
    """Запускает аудио поток для захвата звука"""
    if sd is None:
        raise SystemExit("sounddevice недоступен — нет аудио-входа.")
    device_id = None
    for i, d in enumerate(sd.query_devices()):
        if d['name'] == device_name:
            device_id = i
            break
    if device_id is None:
        raise SystemExit("Устройство не найдено")
    stream = sd.InputStream(
        samplerate=44100, blocksize=2048, dtype='float32',
        channels=1, device=device_id, callback=audio_callback
    )
    stream.start()
    return stream

def choose_settings():
    """Выбор настроек аудио устройства"""
    if sd is None:
        print("⚠️ sounddevice недоступен, используем демо режим")
        return "Default"
    
    devices = sd.query_devices()
    input_devices = [d for d in devices if d['max_input_channels'] > 0]
    
    if not input_devices:
        print("⚠️ Нет доступных аудио устройств, используем демо режим")
        return "Default"
    
    print("🎤 Доступные аудио устройства:")
    for i, device in enumerate(input_devices):
        print(f"  {i}: {device['name']}")
    
    return input_devices[0]['name']

def audio_callback(indata, frames, time, status):
    """Callback функция для обработки аудио"""
    global audio_rms, audio_pitch
    
    if status:
        print(f"Audio status: {status}")
    
    rms = float(np.sqrt(np.mean(indata**2)))
    audio_rms = rms
    
    if librosa is not None:
        try:
            pitch = float(librosa.yin(indata.flatten(), fmin=70, fmax=1500))
            audio_pitch = pitch
        except:
            audio_pitch = 440.0
        else:
            audio_pitch = 440.0
    
        try:
            if not pitch_queue.full():
                pitch_queue.put_nowait(audio_pitch)
            if not rms_queue.full():
                rms_queue.put_nowait(audio_rms)
        except:
            pass

def step_life(grid: np.ndarray, rule: str) -> np.ndarray:
    """Обновляет состояние клеточного автомата согласно правилу"""
    H, W = grid.shape
    
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
        
    else:
        survive_mask = grid & ((neighbors==2)|(neighbors==3))
        birth_mask = (~grid) & (neighbors==3)
        new[survive_mask | birth_mask] = True

    return new

def load_config():
    """Загружает конфигурацию из файла или создает конфигурацию по умолчанию"""
    try:
        with open('guitar_config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
        print("📁 Configuration loaded from guitar_config.json")
        return config
    except FileNotFoundError:
        print("⚠️ guitar_config.json not found, using defaults")
        default_config = {
            'device': 'Default',
            'layer_count': 3,
            'mirror_x': False,
            'mirror_y': False
        }
    return default_config

# Placeholder classes for compatibility
class HUD:
    def __init__(self, font, screen_height, layer_count=3):
        self.font = font
        self.visible = True
        self.screen_height = screen_height
        self.layer_count = layer_count

    def handle_event(self, event):
            return False
        
    def draw(self, surface):
        pass

@dataclass
class Layer:
    """Слой клеточного автомата с настройками"""
    grid: np.ndarray
    age: np.ndarray
    rule: str
    age_palette: str
    rms_palette: str
    color_mode: str
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
    def alpha(self):
        return (self.alpha_live + self.alpha_old) // 2
    
    @alpha.setter
    def alpha(self, value):
        self.alpha_live = value
        self.alpha_old = value

if __name__ == "__main__":
    import signal
    import sys
    
    def signal_handler(sig, frame):
        print('\n🛑 Программа прервана пользователем')
        pygame.quit()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        config = load_config()
        main(config)
    except KeyboardInterrupt:
        print('\n🛑 Программа прервана пользователем')
    except Exception as e:
        print(f'❌ Ошибка запуска: {e}')
        import traceback
        traceback.print_exc()
    finally:
        pygame.quit()
