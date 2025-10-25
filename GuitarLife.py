from __future__ import annotations
#!/usr/bin/env python3
# -*-coding: utf-8 -*-

import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="pygame.pkgdata")

# Стандартные библиотеки
import colorsys
import json
import math
import numpy as np
import os
import pygame
import queue
import random
import sys
import time
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional, Tuple


# Импорт окна настроек
try:
    from settings_window import SettingsWindow
    SETTINGS_WINDOW_AVAILABLE = True
except ImportError:
    SETTINGS_WINDOW_AVAILABLE = False
try:
    from core.ui_components import SimpleColors
except ImportError:
    class SimpleColors:
        """Простая цветовая схема для UI"""
        # Основные цвета
        PRIMARY = (59, 130, 246)          # Синий
        PRIMARY_LIGHT = (147, 197, 253)   # Светло-синий
        SECONDARY = (107, 114, 128)       # Серый
        
        # Поверхности
        SURFACE = (255, 255, 255)         # Белый
        BACKGROUND = (249, 250, 251)      # Очень светло-серый
        
        # Состояния
        ACTIVE = (239, 246, 255)          # Светло-синий фон
        HOVER = (243, 244, 246)           # Светло-серый при наведении
        
        # Границы
        BORDER = (209, 213, 219)          # Светло-серая граница
        BORDER_FOCUS = (59, 130, 246)     # Синяя граница при фокусе
        
        # Текст
        TEXT_PRIMARY = (17, 24, 39)       # Темно-серый
        TEXT_SECONDARY = (107, 114, 128)  # Серый
        TEXT_MUTED = (156, 163, 175)      # Светло-серый
        
        # Серые оттенки
        GRAY_50 = (249, 250, 251)
        GRAY_100 = (243, 244, 246)
        GRAY_200 = (229, 231, 235)
        GRAY_300 = (209, 213, 219)
        GRAY_400 = (156, 163, 175)
        GRAY_500 = (107, 114, 128)
        GRAY_600 = (75, 85, 99)
        GRAY_700 = (55, 65, 81)
        GRAY_800 = (31, 41, 55)
        GRAY_900 = (17, 24, 39)
        
        # Дополнительные цвета
        WHITE = (255, 255, 255)

# resource utilities
try:
    from resource_utils import resource_manager, load_app_config, save_app_config, load_guitar_config, save_guitar_config
except ImportError:
    # Fallback if resource_utils is not available
    resource_manager = None
    def load_app_config(): return {}
    def save_app_config(config): return False
    def load_guitar_config(): return {}
    def save_guitar_config(config): return False

# Основные внешние зависимости
try:
    import numpy as np
except ImportError as e:
    raise SystemExit("NumPy is required. Install with: pip install numpy") from e

# ==================== КОНСТАНТЫ И НАСТРОЙКИ ====================

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

# Available color palettes grouped by category
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
# Материалы и текстуры
    "Gold", "Silver", "Copper", "Emerald", "Sapphire", "Ruby", "Amethyst",
    "Steel", "Bronze", "Pearl", "Coral", "Jade", "Topaz",
    # Специальные и тематические
    "Ukraine", "Neon", "Cyberpunk", "Retro", "Vintage", "Pastel", "Candy",
    # Природные цвета
    "Lime", "Mint", "Peach", "Lavender", "Rose", "Sky", "Sand", "Charcoal", "Clouds", "Flame"

    "Gold", "Silver", "Copper", "Emerald", "Sapphire", "Ruby", "Amethyst",
    "Steel", "Bronze", "Pearl", "Coral", "Jade", "Topaz",
    # Специальные и тематические
    "Ukraine", "Neon", "Cyberpunk", "Retro", "Vintage", "Pastel", "Candy",
    # Природные цвета
    "Lime", "Mint", "Peach", "Lavender", "Rose", "Sky", "Sand", "Charcoal", "Clouds", "Flame"
]

HSV_COLOR_PALETTES = [
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

# Combined list for backward compatibility
PALETTE_OPTIONS = HSV_DESIGN_PALETTES + HSV_COLOR_PALETTES

# Audio processing settings
SPAWN_BASE, SPAWN_SCALE = 10, 70
FREQ_MIN, FREQ_MAX = 72.0, 1500.0
MIN_NOTE_FREQ = 70.0
VOLUME_SCALE = 8.0

# Default timing and threshold values
DEFAULT_CLEAR_RMS = 0.004
DEFAULT_COLOR_RMS_MIN = 0.004
DEFAULT_COLOR_RMS_MAX = 0.30
DEFAULT_TICK_MS = 30
DEFAULT_PTICK_MIN_MS = 60
DEFAULT_PTICK_MAX_MS = 200

# Clear types for different clearing methods
CLEAR_TYPES = [
    "Полная очистка",        # Complete clear - all cells
    "Частичная очистка",     # Partial clear - percentage
    "Очистка по возрасту",   # Age-based clear - old cells
    "Случайная очистка"      # Random clear - random cells
]

# Audio globals
audio_rms = 0.0
audio_pitch = 0.0
audio_gain = 0.0

# ==================== Utilities ====================

def clamp01(x: float) -> float:
    """Ограничивает значение в диапазоне [0, 1]"""
    return max(0.0, min(1.0, x))

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


# ==================== CORE CLASSES ====================

@dataclass
class Layer:
    """Слой клеточного автомата с настройками"""
    def __init__(self, grid, age, rule, age_palette, rms_palette, color_mode,
                 rms_mode="brightness", blend_mode="normal", rms_enabled=True,
                 alpha_live=220, alpha_old=140, max_age=60, mix="Normal",
                 solo=False, mute=False, palette_mix=0.5, spawn_method="Стабильные блоки", spawn_percent=100, aging_speed=1.0,
                 invert_age_palette=False, invert_rms_palette=False):
        self.grid = grid
        self.age = age
        self.rule = rule
        self.age_palette = age_palette
        self.rms_palette = rms_palette
        self.color_mode = color_mode
        self.rms_mode = rms_mode
        self.blend_mode = blend_mode
        self.rms_enabled = rms_enabled
        self.alpha_live = alpha_live
        self.alpha_old = alpha_old
        self.max_age = max_age
        self.mix = mix
        self.solo = solo
        self.mute = mute
        self.palette_mix = palette_mix
        self.spawn_method = spawn_method
        self.tick_ms = DEFAULT_TICK_MS
        self.spawn_percent = spawn_percent  # Процент спавна клеток (0-300%)
        self.aging_speed = aging_speed  # Скорость старения
        self.invert_age_palette = invert_age_palette 
        self.invert_rms_palette = invert_rms_palette 
# ==================== HUD ===================

class HUD:
    """Полнофункциональный HUD с модулями настройки слоев"""
    def __init__(self, font: pygame.font.Font, screen_height: int, layer_count: int = 5, enabled: bool = True, smooth_scale: bool = False):
        self.tick_ms = DEFAULT_TICK_MS  # HUD now owns tick interval
        self.font = font
        self.visible = enabled
        self.mini_held = False
        self.expanded = False
        self.layer_count = min(layer_count, 5)  # Максимум 5 слоев
        self.enabled = enabled
        self.smooth_scale = smooth_scale  # параметр включения сглаженного масштабирования
        # Колбэк для изменения параметров
        self.on_parameter_change = None
        # Позиционирование панели
        self.panel_x = GRID_W * CELL_SIZE + 5
        self.panel_y = 5
        self.panel_width = HUD_WIDTH - 10
        # Прокрутка
        self.scroll_y = 0
        self.scroll_dragging = False
        self.scroll_drag_start_y = 0
        self.scroll_thumb_rect = None
        # Модули слоев
        self.layer_modules = []
        self._create_layer_modules()
        # Общие элементы управления
        self.global_controls = []
        self._create_global_controls()
    
    def _create_layer_modules(self):
        """Создает модули настройки для каждого слоя"""
        self.layer_modules = []
        
        # Доступные опции для выпадающих списков
        palette_options = PALETTE_OPTIONS
        
        rule_options = [
            "Conway", "HighLife", "Day&Night", "Replicator", 
            "Seeds", "Maze", "Coral", "LifeWithoutDeath", "Gnarl"
        ]
        
        blend_options = ["normal", "additive", "screen", "multiply", "overlay"]
        rms_mode_options = ["brightness", "palette", "disabled"]
        spawn_options = [
            "Стабильные блоки",
            "Случайные точки",
            "Глайдеры",
            "Осцилляторы",
            "Смешанный",
            "Линии",
            "Кресты",
            "Кольца"
        ]
        
        module_height = 280  # Высота каждого модуля
        module_spacing = 20   # Отступ между модулями
        
        for i in range(self.layer_count):
            y_offset = 80 + i * (module_height + module_spacing)  # 80px для заголовка
            module = self._create_single_layer_module(i, y_offset, palette_options, 
                                                    rule_options, blend_options, 
                                                    rms_mode_options, spawn_options)
            self.layer_modules.append(module)
    
    def _create_single_layer_module(self, layer_index, y_offset, palette_options, 
                                   rule_options, blend_options, rms_mode_options, spawn_options):
        """Создает модуль настройки для одного слоя"""
        
        module = {
            'layer_index': layer_index,
            'y_offset': y_offset,
            'controls': {}
        }
        
        # Размеры элементов
        control_width = 180
        control_height = 25
        slider_width = 150
        button_width = 60
        combo_width = 120

        x_left = self.panel_x + 10
        x_right = self.panel_x + 200

        current_y = y_offset + 30  # Отступ под заголовок
        right_column_y = y_offset + 30  # Отдельный Y для правой колонки


        # --- CLEAR PARAMETERS ---"""
        # Тип очистки (комбобокс)
        module['controls']['clear_type'] = UIComboBox(
            x_left, current_y, combo_width, control_height,
            f"Тип очистки", CLEAR_TYPES, 0
        )
        current_y += 40

        # Процент очистки (для частичной/случайной)
        module['controls']['clear_percent'] = UISlider(
            x_left, current_y, slider_width, control_height,
            0, 100, 50, f"% Очистки", "{:.0f}%"
        )
        current_y += 40

        # Порог возраста (для возрастной очистки)
        module['controls']['clear_age_threshold'] = UISlider(
            x_left, current_y, slider_width, control_height,
            0, 200, 60, f"Порог возраста", "{:.0f}"
        )
        current_y += 40

        # RMS-порог (для RMS-очистки)
        module['controls']['clear_rms_threshold'] = UISlider(
            x_left, current_y, slider_width, control_height,
            0.0, 0.1, DEFAULT_CLEAR_RMS, f"RMS порог", "{:.3f}"
        )
        current_y += 40

        # Кнопка очистки слоя
        module['controls']['clear_now'] = UIButton(
            x_left, current_y, button_width, control_height,
            "Очистить слой", is_toggle=False, active=False
        )
        current_y += 40

        # Age Palette комбобокс (левая)
        module['controls']['age_palette'] = UIComboBox(
            x_left, current_y, combo_width, control_height,
            f"Age Palette", palette_options, 0
        )
        # Чекбокс Invert Palette (левая)
        module['controls']['invert_age_palette'] = UIButton(
            x_left + combo_width + 10, current_y, 28, control_height,
            "⮂", is_toggle=True, active=False
        )
        current_y += 30

        # RMS Palette комбобокс (правая)
        module['controls']['rms_palette'] = UIComboBox(
            x_right, right_column_y, combo_width, control_height,
            f"RMS Palette", palette_options, 1
        )
        # Чекбокс Invert Palette (правая)
        module['controls']['invert_rms_palette'] = UIButton(
            x_right + combo_width + 10, right_column_y, 28, control_height,
            "⮂", is_toggle=True, active=False
        )
        right_column_y += 30

        # Fade Start слайдер (левая)
        module['controls']['fade_start'] = UISlider(
            x_left, current_y, slider_width, control_height,
            0, 200, 60, f"Fade Start", "{:.0f}"
        )
        current_y += 30

        # Aging Speed слайдер (левая)
        module['controls']['aging_speed'] = UISlider(
            x_left, current_y, slider_width, control_height,
            1.0, 5.0, 1000.0, f"Aging Speed", "{:.2f}"
        )
        current_y += 30

        # Alpha Live слайдер (левая)
        # Soft Kill (%)
        module['controls']['soft_kill'] = UISlider(
            x_left, current_y, slider_width, control_height,
            0, 100, 80, f"Soft Kill (%)", "{:.0f}"
        )
        current_y += 30

        # Fade Floor
        module['controls']['fade_floor'] = UISlider(
            x_left, current_y, slider_width, control_height,
            0.0, 1.0, 0.6, f"Fade Floor", "{:.2f}"
        )
        current_y += 30

        # Age Bias (%)
        module['controls']['age_bias'] = UISlider(
            x_left, current_y, slider_width, control_height,
            0, 100, 15, f"Age Bias (%)", "{:.0f}"
        )
        current_y += 30
        module['controls']['alpha_live'] = UISlider(
            x_left, current_y, slider_width, control_height,
            0, 255, 220, f"Alpha Live (Layer)", "{:.0f}"
        )
        current_y += 30

        module['controls']['spawn_percent'] = UISlider(
            x_right, right_column_y, 100, control_height,
            0, 300, 100, f"SPAWN SCALE", "{:.0f}%"
        )
        right_column_y += 30

        module['controls']['alpha_old'] = UISlider(
            x_left, current_y, slider_width, control_height,
            0, 255, 140, f"Alpha Old (Layer)", "{:.0f}"
        )
        current_y += 30

        # RMS Mode комбобокс (правая)
        module['controls']['rms_mode'] = UIComboBox(
            x_right, right_column_y, combo_width, control_height,
            f"RMS Mode", rms_mode_options, 0
        )
        right_column_y += 30

        # Максимальный возраст клеток (логарифмический слайдер, левая)
        module['controls']['max_age'] = UISlider(
            x_left, current_y, slider_width, control_height,
            0, 100, 41.7, f"Max Age", "max_age_log"
        )
        current_y += 30

        # Palette Mix слайдер (правая)
        palette_mix_slider = UISlider(
            x_right, right_column_y, slider_width, control_height,
            0.0, 1.0, 0.5, f"Palette Mix", "{:.2f}"
        )
        module['controls']['palette_mix'] = palette_mix_slider
        right_column_y += 30

        # Rule комбобокс (левая)
        module['controls']['rule'] = UIComboBox(
            x_left, current_y, combo_width, control_height,
            f"Rule", rule_options, 0
        )
        current_y += 30

        # Blend Mode комбобокс (левая)
        module['controls']['blend_mode'] = UIComboBox(
            x_left, current_y, combo_width, control_height,
            f"Blend", blend_options, 0
        )
        current_y += 30

        # Spawn Method комбобокс (левая)
        module['controls']['spawn_method'] = UIComboBox(
            x_left, current_y, combo_width, control_height,
            f"Spawn", spawn_options, 0
        )
        current_y += 30

        # Синхронизируем current_y с максимальной позицией
        current_y = max(current_y, right_column_y)

        # Solo, Mute и RMS кнопки
        module['controls']['solo'] = UIButton(
            x_left, current_y, button_width, control_height,
            "SOLO", is_toggle=True, active=False
        )

        module['controls']['mute'] = UIButton(
            x_left + button_width + 10, current_y, button_width, control_height,
            "MUTE", is_toggle=True, active=False
        )

        return module
    
    def _create_global_controls(self):
        """Создает общие элементы управления"""
        # Глобальный слайдер для tick_ms
        slider_x = self.panel_x + 250
        slider_y = self.panel_y + 10
        slider_width = 180
        slider_height = 25
        self.global_tick_slider = UISlider(
            slider_x, slider_y, slider_width, slider_height,
            5, 100, self.tick_ms, "Tick (ms)", "{:.0f} ms"
        )
        self.btn_all = UIButton(self.panel_x + self.panel_width - 70, self.panel_y + 10, 60, 25, "ALL", is_toggle=True, active=True)
        self.global_controls = [self.btn_all, self.global_tick_slider]
    
    def handle_event(self, event):
        """Обработка событий для всех элементов HUD"""
        if not self.visible:
            return False
        # --- Scrollbar interactions ---
        # Mouse wheel scroll over the HUD panel
        if event.type == pygame.MOUSEWHEEL:
            pos = getattr(event, 'pos', pygame.mouse.get_pos())
            if self._is_mouse_over_panel(pos):
                self.scroll_y -= event.y * 30
                self._clamp_scroll()
                return True
        # Drag the scrollbar thumb
        if event.type == pygame.MOUSEBUTTONDOWN and getattr(event, 'button', 1) == 1:
            pos = getattr(event, 'pos', pygame.mouse.get_pos())
            if self.scroll_thumb_rect and self.scroll_thumb_rect.collidepoint(pos):
                self.scroll_dragging = True
                self.scroll_drag_start_y = pos[1] - self.scroll_thumb_rect.y
                return True
        if event.type == pygame.MOUSEMOTION and self.scroll_dragging:
            pos = getattr(event, 'pos', pygame.mouse.get_pos())
            scrollbar_y = self.panel_y + 60
            scrollbar_h = 600 - 60
            total_h = len(self.layer_modules) * 300
            if total_h > scrollbar_h and self.scroll_thumb_rect is not None:
                thumb_h = self.scroll_thumb_rect.height
                new_thumb_y = max(scrollbar_y, min(scrollbar_y + scrollbar_h - thumb_h, pos[1] - self.scroll_drag_start_y))
                self.scroll_thumb_rect.y = new_thumb_y
                # Map thumb position back to scroll_y
                denom = (scrollbar_h - thumb_h) if (scrollbar_h - thumb_h) > 0 else 1
                self.scroll_y = -int((new_thumb_y - scrollbar_y) * (total_h - scrollbar_h) / denom)
                self._clamp_scroll()
            return True
        if event.type == pygame.MOUSEBUTTONUP and self.scroll_dragging:
            self.scroll_dragging = False
            return True

        # Обработка глобального слайдера
        if hasattr(self, 'global_tick_slider'):
            if self.global_tick_slider.handle_event(event):
                self.tick_ms = int(self.global_tick_slider.current_val)
                # Передаем изменение в App, если есть
                if hasattr(self, 'app') and hasattr(self.app, 'on_global_tick_ms_change'):
                    self.app.on_global_tick_ms_change(self.tick_ms)
                return True
        # Кнопка ALL
        if hasattr(self, 'btn_all') and self.btn_all.handle_event(event):
            if hasattr(self, 'app') and hasattr(self.app, 'layers'):
                state = self.btn_all.active
                for layer in self.app.layers:
                    layer.mute = not state
                # обновить HUD
                if hasattr(self, 'update_from_app'):
                    self.update_from_app(self.app)
            return True

        # Обработка прокрутки
        if event.type == pygame.MOUSEWHEEL:
            if hasattr(event, 'pos') and self._is_mouse_over_panel(event.pos):
                self.scroll_y -= event.y * 30
                self._clamp_scroll()
                return True
            elif not hasattr(event, 'pos'):
                mouse_pos = pygame.mouse.get_pos()
                if self._is_mouse_over_panel(mouse_pos):
                    self.scroll_y -= event.y * 30
                    self._clamp_scroll()
                    return True
        # Обработка событий модулей слоев
        for module in self.layer_modules:
            layer_idx = module['layer_index']
            for control_name, control in module['controls'].items():
                if hasattr(control, 'handle_event'):
                    original_y = control.y
                    control.y += self.scroll_y
                    control.rect.y += self.scroll_y
                    if control.handle_event(event):
                        control.y = original_y
                        control.rect.y = original_y
                        param_name = f"layer_{layer_idx}_{control_name}"
                        if isinstance(control, UISlider):
                            value = control.current_val
                        elif isinstance(control, UIComboBox):
                            value = control.current_value
                        elif isinstance(control, UIButton):
                            value = control.active if control.is_toggle else True
                        else:
                            value = None
                        if self.on_parameter_change and value is not None:
                            self.on_parameter_change(param_name, value)
                        return True
                    control.y = original_y
                    control.rect.y = original_y
        return False
    
    def _is_mouse_over_panel(self, mouse_pos):
        """Проверяет, находится ли мышь над панелью HUD"""
        return (self.panel_x <= mouse_pos[0] <= self.panel_x + self.panel_width and
                self.panel_y <= mouse_pos[1] <= self.panel_y + 600)  # Примерная высота панели
    
    def _clamp_scroll(self):
        """Ограничивает прокрутку допустимыми значениями"""
        max_scroll = max(0, len(self.layer_modules) * 300 - 500)  # Примерный расчет
        self.scroll_y = max(-max_scroll, min(0, self.scroll_y))
    
    def update_from_app(self, app):

        """Обновляет значения UI элементов из состояния приложения"""
        if not hasattr(app, 'layers') or len(app.layers) == 0:
            return # Нет слоев для обновления
        
        # Обновляем каждый модуль слоя
        for i, module in enumerate(self.layer_modules):
            if i > 0:
                module['visible'] = False
            else:
                module['visible'] = True
            if i >= len(app.layers):
                break
            layer = app.layers[i]
            controls = module['controls']
            # Обновляем чекбоксы инверсии палитр
            if 'invert_age_palette' in controls:
                controls['invert_age_palette'].active = getattr(layer, 'invert_age_palette', False)
            if 'invert_rms_palette' in controls:
                controls['invert_rms_palette'].active = getattr(layer, 'invert_rms_palette', False)
            
        # Обновляем каждый модуль слоя
        for i, module in enumerate(self.layer_modules):
            if i > 0:
                module['visible'] = False
            else:
                module['visible'] = True
            if i >= len(app.layers):
                break
            layer = app.layers[i]
            controls = module['controls']
            
            # Обновляем палитры
            if 'age_palette' in controls:
                try:
                    idx = controls['age_palette'].options.index(layer.age_palette)
                    controls['age_palette'].current_index = idx
                except (ValueError, AttributeError):
                    pass
                    
            if 'rms_palette' in controls:
                try:
                    idx = controls['rms_palette'].options.index(layer.rms_palette)
                    controls['rms_palette'].current_index = idx
                except (ValueError, AttributeError):
                    pass
            
            # Обновляем слайдеры
            if 'alpha_live' in controls:
                controls['alpha_live'].current_val = getattr(layer, 'alpha_live', 220)
            if 'alpha_old' in controls:
                controls['alpha_old'].current_val = getattr(layer, 'alpha_old', 140)
            if 'max_age' in controls:
                layer.max_age = getattr(layer, 'max_age', 60)
                controls['max_age'].current_val = max_age_value_to_slider(layer.max_age)
            if 'palette_mix' in controls:
                controls['palette_mix'].current_val = getattr(layer, 'palette_mix', 0.5)
            if 'aging_speed' in controls:
                controls['aging_speed'].current_val = getattr(layer, 'aging_speed', 10.0)
            
            # Обновляем комбобоксы
            if 'rule' in controls:
                try:
                    idx = controls['rule'].options.index(layer.rule)
                    controls['rule'].current_index = idx
                except (ValueError, AttributeError):
                    pass
                    
            if 'blend_mode' in controls:
                try:
                    idx = controls['blend_mode'].options.index(getattr(layer, 'blend_mode', 'normal'))
                    controls['blend_mode'].current_index = idx
                except (ValueError, AttributeError):
                    pass
                    
            if 'rms_mode' in controls:
                try:
                    idx = controls['rms_mode'].options.index(getattr(layer, 'rms_mode', 'brightness'))
                    controls['rms_mode'].current_index = idx
                except (ValueError, AttributeError):
                    pass
                    
            if 'spawn_method' in controls:
                try:
                    idx = controls['spawn_method'].options.index(getattr(layer, 'spawn_method', 'Стабильные блоки'))
                    controls['spawn_method'].current_index = idx
                except (ValueError, AttributeError):
                    pass
            
            # Обновляем кнопки
            if 'solo' in controls:
                controls['solo'].active = getattr(layer, 'solo', False)
            if 'mute' in controls:
                controls['mute'].active = getattr(layer, 'mute', False)
    
    def update_callbacks(self):
        """Обновляет колбэки для всех UI элементов"""
        pass
    
    def draw(self, surface, info=None):
        """Отрисовка HUD с модулями слоев"""
        if not self.visible:
            return
        panel_height = 600  # Фиксированная высота панели
        pygame.draw.rect(surface, SimpleColors.GRAY_900, 
                        (self.panel_x, self.panel_y, self.panel_width, panel_height))
        pygame.draw.rect(surface, SimpleColors.PRIMARY, 
                        (self.panel_x, self.panel_y, self.panel_width, panel_height), 2)
        # Заголовок
        title_text = "GUITAR-LIFE v13 - Layer Controls"
        title_surface = self.font.render(title_text, True, SimpleColors.PRIMARY)
        surface.blit(title_surface, (self.panel_x + 10, self.panel_y + 10))
        # Глобальный слайдер Tick (ms)
        if hasattr(self, 'global_tick_slider'):
            self.global_tick_slider.draw(surface, self.font)
        # Кнопка ALL (включить/выключить все слои)
        if hasattr(self, 'btn_all'):
            self.btn_all.draw(surface, self.font)

        # Краткая информация
        if info:
            info_text = f"Layers: {info.get('Layers', 0)} | Cells: {info.get('Alive', '0 cells')}"
            info_surface = self.font.render(info_text, True, SimpleColors.WHITE)
            surface.blit(info_surface, (self.panel_x + 10, self.panel_y + 35))
        # Создаем область отсечения для прокрутки
        clip_rect = pygame.Rect(self.panel_x, self.panel_y + 60, self.panel_width, panel_height - 60)
        surface.set_clip(clip_rect)
        open_dropdowns = []
        # Отрисовываем только первый модуль слоя
        if self.layer_modules:
            open_dropdowns.extend(self._draw_layer_module(surface, self.layer_modules[0], collect_dropdowns=True))
        surface.set_clip(None)
        for dropdown_info in open_dropdowns:
            control, original_y = dropdown_info
            control.y += self.scroll_y
            control.rect.y += self.scroll_y
            self._draw_dropdown_only(surface, control)
            control.y = original_y
            control.rect.y = original_y
        self._draw_scrollbar(surface, panel_height)
    
    def _draw_layer_module(self, surface, module, collect_dropdowns=False):
        """Отрисовка одного модуля слоя"""
        layer_idx = module['layer_index']
        y_offset = module['y_offset'] + self.scroll_y
        open_dropdowns = []
        
        # Пропускаем модули, которые не видны
        if y_offset + 280 < self.panel_y or y_offset > self.panel_y + 600:
            return open_dropdowns if collect_dropdowns else None
        
        # Фон модуля
        module_rect = pygame.Rect(self.panel_x + 5, y_offset, self.panel_width - 10, 270)
        pygame.draw.rect(surface, SimpleColors.GRAY_800, module_rect, border_radius=8)
        pygame.draw.rect(surface, SimpleColors.BORDER, module_rect, 1, border_radius=8)
        
        # Заголовок модуля
        title_text = f"Layer {layer_idx + 1}"
        title_surface = self.font.render(title_text, True, SimpleColors.PRIMARY)
        surface.blit(title_surface, (self.panel_x + 15, y_offset + 10))
        
        # Отрисовка всех элементов управления
        controls = module['controls']
        
        # Корректируем позиции элементов для прокрутки и отрисовываем
        for control_name, control in controls.items():
            if hasattr(control, 'draw'):
                # Временно корректируем позицию для отрисовки
                original_y = control.y
                control.y += self.scroll_y
                control.rect.y += self.scroll_y
                
                # Отрисовываем только если элемент видим
                if (control.y + control.height >= self.panel_y + 60 and 
                    control.y <= self.panel_y + 600):
                    
                    # Отрисовка слайдера и лейбла для UISlider
                    if isinstance(control, UISlider) and hasattr(control, 'label'):
                        control.draw(surface, self.font)  # рисуем сам слайдер
                        label_text = f"{control.label}: {control.value_format.format(control.current_val)}"
                        label_surface = self.font.render(label_text, True, SimpleColors.WHITE)
                        surface.blit(label_surface, (control.x, control.y - 20))
                    
                    # Отрисовка лейбла для комбобоксов
                    elif isinstance(control, UIComboBox):
                        label_surface = self.font.render(control.label, True, SimpleColors.WHITE)
                        surface.blit(label_surface, (control.x, control.y - 20))
                        
                        # Если комбобокс открыт, сохраняем его для отрисовки поверх всего
                        if collect_dropdowns and control.is_open:
                            open_dropdowns.append((control, original_y))
                        
                        # Отрисовываем только кнопку комбобокса (без выпадающего списка)
                        self._draw_combobox_button_only(surface, control)
                    else:
                        # Обычная отрисовка для слайдеров и других элементов
                        control.draw(surface, self.font)
                
                # Восстанавливаем позицию
                control.y = original_y
                control.rect.y = original_y
        
        return open_dropdowns if collect_dropdowns else None
    
    def _draw_combobox_button_only(self, surface, control):
        """Отрисовка только кнопки комбобокса (без выпадающего списка)"""
        # Синхронизируем координаты с rect
        control.x = control.rect.x
        control.y = control.rect.y
        
        # Основная кнопка
        bg_color = SimpleColors.ACTIVE if control.is_open else SimpleColors.SURFACE
        border_color = SimpleColors.BORDER_FOCUS if control.is_open else SimpleColors.BORDER
        
        pygame.draw.rect(surface, bg_color, control.rect, border_radius=8)
        pygame.draw.rect(surface, border_color, control.rect, 2, border_radius=8)
        
        # Текст текущего значения
        current_text = control.current_value if control.current_value else "Select..."
        text_surface = self.font.render(current_text, True, SimpleColors.TEXT_PRIMARY)
        text_x = control.x + 8
        text_y = control.y + (control.height - text_surface.get_height()) // 2
        surface.blit(text_surface, (text_x, text_y))
        
        # Стрелка
        arrow_text = "▲" if control.is_open else "▼"
        arrow_surface = self.font.render(arrow_text, True, SimpleColors.TEXT_SECONDARY)
        arrow_x = control.x + control.width - arrow_surface.get_width() - 8
        arrow_y = control.y + (control.height - arrow_surface.get_height()) // 2
        surface.blit(arrow_surface, (arrow_x, arrow_y))
    
    def _draw_dropdown_only(self, surface, control):
        """Отрисовка только выпадающего списка комбобокса"""
        if not control.is_open or not control.options:
            return
        
        # Синхронизируем координаты с rect
        control.x = control.rect.x
        control.y = control.rect.y
        
        dropdown_rect = control._get_dropdown_rect()
        
        # Фон выпадающего списка
        pygame.draw.rect(surface, SimpleColors.SURFACE, dropdown_rect, border_radius=8)
        pygame.draw.rect(surface, SimpleColors.BORDER, dropdown_rect, 2, border_radius=8)
        
        # Элементы списка
        visible_items = min(len(control.options), control.max_visible_items)
        for i in range(visible_items):
            option_index = i + control.scroll_offset
            if option_index >= len(control.options):
                break
                
            option_rect = pygame.Rect(
                dropdown_rect.x + 2, 
                dropdown_rect.y + i * control.height + 2,
                dropdown_rect.width - 4, 
                control.height - 2
            )
            
            # Подсветка при наведении, выборе или выделении клавиатурой
            mouse_pos = pygame.mouse.get_pos()
            is_hovered = option_rect.collidepoint(mouse_pos)
            is_selected = option_index == control.current_index
            is_keyboard_highlighted = option_index == control.selected_index
            
            if is_selected:
                # Выбранный элемент - синий фон
                pygame.draw.rect(surface, SimpleColors.PRIMARY, option_rect, border_radius=6)
                text_color = SimpleColors.WHITE
            elif is_keyboard_highlighted:
                # Выделенный клавиатурой элемент - светло-серый фон с рамкой
                pygame.draw.rect(surface, SimpleColors.GRAY_100, option_rect, border_radius=6)
                pygame.draw.rect(surface, SimpleColors.PRIMARY, option_rect, 2, border_radius=6)
                text_color = SimpleColors.TEXT_PRIMARY
            elif is_hovered:
                # Наведение мышью - слабая подсветка
                pygame.draw.rect(surface, SimpleColors.GRAY_50, option_rect, border_radius=6)
                text_color = SimpleColors.TEXT_PRIMARY
            else:
                text_color = SimpleColors.TEXT_PRIMARY
            
            # Текст опции
            option_text = str(control.options[option_index])
            option_surface = self.font.render(option_text, True, text_color)
            option_text_x = option_rect.x + 6
            option_text_y = option_rect.y + (option_rect.height - option_surface.get_height()) // 2
            surface.blit(option_surface, (option_text_x, option_text_y))
        
        # Отображение текста поиска внизу списка
        if hasattr(control, 'search_text') and control.search_text:
            search_bg_rect = pygame.Rect(dropdown_rect.x, dropdown_rect.bottom + 2, dropdown_rect.width, 25)
            pygame.draw.rect(surface, SimpleColors.GRAY_800, search_bg_rect, border_radius=6)
            pygame.draw.rect(surface, SimpleColors.BORDER_FOCUS, search_bg_rect, 2, border_radius=6)
            
            search_display = f"Поиск: {control.search_text}_"
            search_surface = self.font.render(search_display, True, SimpleColors.WHITE)
            search_x = search_bg_rect.x + 6
            search_y = search_bg_rect.y + (search_bg_rect.height - search_surface.get_height()) // 2
            surface.blit(search_surface, (search_x, search_y))
    
    def _draw_scrollbar(self, surface, panel_height):
        """Отрисовка полосы прокрутки"""
        # Простая полоса прокрутки справа
        scrollbar_x = self.panel_x + self.panel_width - 15
        scrollbar_y = self.panel_y + 60
        scrollbar_height = panel_height - 60
        
        # Фон полосы прокрутки
        pygame.draw.rect(surface, SimpleColors.GRAY_700, 
                        (scrollbar_x, scrollbar_y, 10, scrollbar_height))
        
        # Ползунок прокрутки
        total_content_height = len(self.layer_modules) * 300
        if total_content_height > scrollbar_height:
            thumb_height = max(20, int(scrollbar_height * scrollbar_height / total_content_height))
            thumb_y = scrollbar_y + int(-self.scroll_y * (scrollbar_height - thumb_height) / 
                                      (total_content_height - scrollbar_height))
            
            self.scroll_thumb_rect = pygame.Rect(scrollbar_x, thumb_y, 10, thumb_height)
            pygame.draw.rect(surface, SimpleColors.PRIMARY, self.scroll_thumb_rect, border_radius=5)


# ==================== ЭФФЕКТЫ ====================

def apply_trails(surface: pygame.Surface, trail_strength: float):
    """Эффект следов - затухание предыдущего кадра"""
    if trail_strength <= 0: 
        return
    fade = max(0.0, min(1.0, 1.0 - trail_strength))
    arr = pygame.surfarray.pixels3d(surface)
    arr[:] = (arr * fade).astype(arr.dtype)


def apply_scale_blur(surface: pygame.Surface, scale: int):
    """Блюр через масштабирование"""
    if scale <= 1: 
        return
    w, h = surface.get_size()
    dw, dh = max(1, w//scale), max(1, h//scale)
    small = pygame.transform.smoothscale(surface, (dw, dh))
    surface.blit(pygame.transform.smoothscale(small, (w, h)), (0,0))


def apply_bloom(surface: pygame.Surface, strength: float):
    """Эффект свечения для ярких областей"""
    if strength <= 0: 
        return
    w,h = surface.get_size()
    arr = pygame.surfarray.pixels3d(surface)
    # Простая яркостная маска
    lum = (0.2126*arr[:,:,0] + 0.7152*arr[:,:,1] + 0.0722*arr[:,:,2])
    mask = (lum > 180).astype(np.float32) * strength
    mask3 = np.dstack([mask, mask, mask])
    # Downscale / upscale для мягкого свечения
    k = 4
    dw, dh = max(1, w // k), max(1, h // k)
    small = pygame.transform.smoothscale(surface, (dw, dh))
    blurred = pygame.transform.smoothscale(small, (w, h))
    arr_b = pygame.surfarray.pixels3d(blurred)
    arr = pygame.surfarray.pixels3d(surface)
    # Усиливаем только яркие места
    np.multiply(arr_b, mask3, out=arr_b, casting='unsafe')
    arr[:] = np.clip(arr.astype(np.float32) + arr_b.astype(np.float32) * strength, 0, 255).astype(np.uint8)


def apply_posterize(surface: pygame.Surface, levels: int):
    """Постеризация цветов до заданного числа уровней"""
    levels = max(2, int(levels))
    arr = pygame.surfarray.pixels3d(surface)
    step = 255 // (levels - 1)
    q = (arr.astype(np.int32) + step // 2) // step
    arr[:] = np.clip(q * step, 0, 255).astype(np.uint8)


def apply_dither(surface: pygame.Surface):
    """Исправленная функция dither для решения проблемы broadcasting"""
    # Конвертируем Surface в numpy array
    arr = pygame.surfarray.array3d(surface)
    
    # Транспонируем для правильного порядка осей (pygame использует (width, height, channels))
    arr = np.transpose(arr, (1, 0, 2))  # Теперь (height, width, channels)
    
    if len(arr.shape) != 3:
        return surface
    
    height, width, channels = arr.shape
    
    # Создаем простой dither pattern
    pattern = np.array([[0, 0.5], [0.75, 0.25]])
    
    # Создаем тайл нужного размера (height, width) 
    tile_height = (height // pattern.shape[0] + 1) * pattern.shape[0]
    tile_width = (width // pattern.shape[1] + 1) * pattern.shape[1]
    
    # Тайлим pattern
    tile = np.tile(pattern, (tile_height // pattern.shape[0], tile_width // pattern.shape[1]))
    
    # Обрезаем до нужного размера
    tile = tile[:height, :width]
    
    # Добавляем размерность для channels и применяем ко всем каналам
    tile = tile[:, :, np.newaxis]  # (height, width, 1)
    
    # Применяем dither
    arr = arr + (tile * 16 - 8)  # Небольшое случайное смещение
    
    # Обрезаем значения
    arr = np.clip(arr, 0, 255).astype(np.uint8)
    
    # Транспонируем обратно для pygame
    arr = np.transpose(arr, (1, 0, 2))
    
    # Конвертируем обратно в Surface
    pygame.surfarray.blit_array(surface, arr)
    
    return surface


def apply_scanlines(surface: pygame.Surface, strength: float):
    """Сканлайны: затемнение каждой второй строки"""
    strength = clamp01(strength)
    if strength <= 0: 
        return
    arr = pygame.surfarray.pixels3d(surface)
    arr[1::2, :, :] = (arr[1::2, :, :].astype(np.float32) * (1.0 - 0.5 * strength)).astype(np.uint8)


def apply_pixelate(surface: pygame.Surface, block: int):
    """Пикселизация: downscale → upscale с целочисленным блоком"""
    block = max(1, int(block))
    if block == 1: 
        return
    w, h = surface.get_size()
    small = pygame.transform.scale(surface, (max(1, w // block), max(1, h // block)))
    surface.blit(pygame.transform.scale(small, (w, h)), (0, 0))


def apply_outline(surface: pygame.Surface, thickness: int = 1):
    """Контур по градиенту яркости (простая Sobel-like оценка)"""
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
CHANNELS = 1

# Grid and display settings
GRID_W, GRID_H = 120, 70
BG_COLOR = (10, 10, 12)
FIELD_OFFSET_X = 0

# Cellular automaton rules
CA_RULES = [
    "Conway", "HighLife", "Day&Night", "Replicator", 
    "Seeds", "Maze", "Coral", "LifeWithoutDeath", "Gnarl"
]

# Available color palettes grouped by category
# Унифицированная система палитр - устранено дублирование
PALETTE_NAMES = [
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

# Категоризация палитр для оптимизации
PALETTE_CATEGORIES = {
    "basic": ["Blue->Red", "Blue->Green->Yellow->Red", "Rainbow", "RainbowSmooth"],
    "nature": ["Sunset", "Aurora", "Ocean", "Fire", "Galaxy", "Tropical", "Volcano", "DeepSea"],
    "seasonal": ["Spring", "Summer", "Autumn", "Winter", "Ice", "Forest", "Desert"],
    "scientific": ["Viridis", "Inferno", "Magma", "Plasma", "Cividis", "Twilight"],
    "monochrome": ["White->LightGray->Gray->DarkGray", "BrightRed->DarkRed->DarkGray->Black", 
                  "Monochrome", "Sepia", "HighContrast", "LowContrast"],
    "materials": ["Gold", "Silver", "Copper", "Emerald", "Sapphire", "Ruby", "Amethyst",
                 "Steel", "Bronze", "Pearl", "Coral", "Jade", "Topaz"],
    "special": ["Ukraine", "Neon", "Cyberpunk", "Retro", "Vintage", "Pastel", "Candy"],
    "natural_colors": ["Lime", "Mint", "Peach", "Lavender", "Rose", "Sky", "Sand", "Charcoal", "Clouds", "Flame"]
}

# Обратная совместимость
HSV_DESIGN_PALETTES = PALETTE_NAMES  
HSV_COLOR_PALETTES = PALETTE_NAMES
PALETTE_OPTIONS = PALETTE_NAMES

def get_hsv_design_palettes():
    """Возвращает палитры для HSV-дизайнов (комбинированный режим)"""
    return PALETTE_NAMES

def get_hsv_color_palettes():
    """Возвращает палитры для HSV палитр (только RMS режим)"""
    return PALETTE_NAMES

def get_palette_by_category(category: str = "all"):
    """Возвращает палитры по категории с кэшированием"""
    if category == "Возраст + RMS" or category == "Только RMS":
        return PALETTE_NAMES
    elif category in PALETTE_CATEGORIES:
        return PALETTE_CATEGORIES[category]
    else:
        return PALETTE_NAMES

# Audio processing settings
SPAWN_BASE, SPAWN_SCALE = 20, 40  # Уменьшено для меньшего количества клеток
FREQ_MIN, FREQ_MAX = 70.0, 1500.0
MIN_NOTE_FREQ = 60.0
VOLUME_SCALE = 9.0  # Уменьшено для более мягкой реакции на звук

# Default timing and threshold values
DEFAULT_CLEAR_RMS = 0.004
DEFAULT_COLOR_RMS_MIN = 0.004
DEFAULT_COLOR_RMS_MAX = 0.30
DEFAULT_TICK_MS = 60
DEFAULT_PTICK_MIN_MS = 60
DEFAULT_PTICK_MAX_MS = 200

# Pitch-based coloring
PITCH_COLOR_MIN_HZ = 72.0
PITCH_COLOR_MAX_HZ = 1500.0

# File paths - using modern resource management
if resource_manager:
    PRESET_PATH = resource_manager.get_resource_path("runtime_state.json") or "runtime_state.json"
    PALETTE_PATH = resource_manager.get_resource_path("palette_preset.json") or "palette_preset.json"
else:
    # Fallback to old method
    PRESET_PATH = os.path.join(os.path.dirname(__file__) if "__file__" in globals() else ".", "runtime_state.json")
    PALETTE_PATH = os.path.join(os.path.dirname(__file__) if "__file__" in globals() else ".", "palette_preset.json")

# SimpleColors уже определен выше в секции HUD - дублирование удалено

pitch_queue = queue.Queue(maxsize=8)
rms_queue   = queue.Queue(maxsize=8)
running     = True
audio_gain  = 2.5  # Global variable for audio gain

# -------------------- Утилиты --------------------
def clamp01(x: float) -> float:
    return 0.0 if x < 0 else (1.0 if x > 1 else x)

def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t

# Кэш для дорогих вычислений
from functools import lru_cache
# import weakref

# Оптимизация памяти для NumPy массивов
def _create_optimized_grid(height: int, width: int) -> np.ndarray:
    """Создает оптимизированную сетку с минимальным использованием памяти"""
    return np.zeros((height, width), dtype=bool, order='C')

def _create_optimized_age_array(height: int, width: int) -> np.ndarray:
    """Создает оптимизированный массив возраста с минимальным использованием памяти"""
    return np.zeros((height, width), dtype=np.uint16, order='C')  # uint16 вместо int32 для экономии памяти

def _optimize_array_memory(arr: np.ndarray) -> np.ndarray:
    """Оптимизирует использование памяти массива"""
    if arr.dtype == np.int32 and np.max(arr) < 65535:
        # Преобразуем int32 в uint16 если значения помещаются
        return arr.astype(np.uint16, copy=False)
    elif not arr.flags['C_CONTIGUOUS']:
        # Обеспечиваем C-contiguous layout для лучшей производительности
        return np.ascontiguousarray(arr)
    return arr

@lru_cache(maxsize=1024)
def _cached_hsv_to_rgb(h: float, s: float, v: float) -> tuple[int, int, int]:
    """Кэшированная конверсия HSV в RGB"""
    r, g, b = colorsys.hsv_to_rgb((h % 360) / 360.0, clamp01(s), clamp01(v))
    return (int(r * 255), int(g * 255), int(b * 255))

@lru_cache(maxsize=512)
def _cached_age_to_t(age: int, max_age: int) -> float:
    """Кэшированная функция возраста"""
    if max_age <= 1:
        return 1.0
    k = max(6.0, max_age / 6.0)
    return clamp01(1.0 - math.exp(-age / k))

@lru_cache(maxsize=256)
def _cached_palette_hsv(palette_name: str, t: float) -> tuple[float, float, float]:
    """Кэшированная генерация HSV для палитр"""
    t = clamp01(t)
    PALETTE_FUNCTIONS = {
        "FIRE": hue_fire_from_t,
        "OCEAN": hue_ocean_from_t,
        "NEON": hue_neon_from_t,
        "UKRAINE": hue_ukraine_from_t,
        "RAINBOWSMOOTH": hue_rainbow_smooth_from_t,
        "SUNSET": hue_sunset_from_t,
        "AURORA": hue_aurora_from_t,
        "GALAXY": hue_galaxy_from_t,
        "TROPICAL": hue_tropical_from_t,
        "VOLCANO": hue_volcano_from_t,
        "DEEPSEA": hue_deepsea_from_t,
        "CYBERPUNK": hue_cyberpunk_from_t,
        "BGYR": lambda t: (hue_bgyr_from_t(t), 0.85, 1.0),
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
        "GOLD": hue_gold_from_t,
        "SILVER": hue_silver_from_t,
        "COPPER": hue_copper_from_t,
        "EMERALD": hue_emerald_from_t,
        "SAPPHIRE": hue_sapphire_from_t,
        "RUBY": hue_ruby_from_t,
        "AMETHYST": hue_amethyst_from_t,
        "SEPIA": hue_sepia_from_t
    # Добавьте остальные палитры по аналогии
    }
    func = PALETTE_FUNCTIONS.get(palette_name.upper())
    if func:
        return func(t)
    # Default fallback
    hue = hue_bgyr_from_t(t)
    return (hue, 0.85, 1.0)

def blend_colors(color1: Tuple[int, int, int], color2: Tuple[int, int, int], 
                factor: float, blend_mode: str = "normal") -> Tuple[int, int, int]:
    """
    Смешивает два RGB цвета с различными режимами блендинга.
    
    Args:
        color1: Базовый цвет (R, G, B)
        color2: Цвет для смешивания (R, G, B)
        factor: Фактор смешивания (0.0 - 1.0)
        blend_mode: Режим блендинга ("normal", "additive", "screen", "multiply", "overlay")
    
    Returns:
        Смешанный цвет (R, G, B)
    """
    r1, g1, b1 = color1
    r2, g2, b2 = color2
    factor = clamp01(factor)
    
    if blend_mode == "normal":
        # Альфа-блендинг (линейная интерполяция)
        r = int(lerp(r1, r2, factor))
        g = int(lerp(g1, g2, factor))
        b = int(lerp(b1, b2, factor))
    
    elif blend_mode == "additive":
        # Аддитивное смешивание
        r = min(255, int(r1 + r2 * factor))
        g = min(255, int(g1 + g2 * factor))
        b = min(255, int(b1 + b2 * factor))
    
    elif blend_mode == "screen":
        # Screen blend mode: 1 - (1-a)*(1-b)
        r = int(255 - (255 - r1) * (255 - r2 * factor) / 255)
        g = int(255 - (255 - g1) * (255 - g2 * factor) / 255)
        b = int(255 - (255 - b1) * (255 - b2 * factor) / 255)
    
    elif blend_mode == "multiply":
        # Multiply blend mode
        r = int(r1 * (r2 * factor / 255 * factor + (1 - factor)))
        g = int(g1 * (g2 * factor / 255 * factor + (1 - factor)))
        b = int(b1 * (b2 * factor / 255 * factor + (1 - factor)))
    
    elif blend_mode == "overlay":
        # Overlay blend mode
        def overlay_channel(base, overlay, factor):
            scaled_overlay = overlay * factor
            if base < 128:
                return int(2 * base * scaled_overlay / 255)
            else:
                return int(255 - 2 * (255 - base) * (255 - scaled_overlay) / 255)
        
        r = int(lerp(r1, overlay_channel(r1, r2, factor), factor))
        g = int(lerp(g1, overlay_channel(g1, g2, factor), factor))
        b = int(lerp(b1, overlay_channel(b1, b2, factor), factor))
    
    else:
        # Fallback к normal режиму
        r = int(lerp(r1, r2, factor))
        g = int(lerp(g1, g2, factor))
        b = int(lerp(b1, b2, factor))
    
    return (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))

# -------------------- Палитры и возраст/выцветание --------------------
def hue_bgyr_from_t(t: float) -> float:
    t = clamp01(t)
    if t < 1/3:   return lerp(220.0, 120.0, t*3.0)
    elif t < 2/3: return lerp(120.0, 60.0, (t-1/3)*3.0)
    else:         return lerp(60.0, 0.0, (t-2/3)*3.0)

def hue_br_from_t(t: float) -> float:
    return lerp(220.0, 0.0, clamp01(t))

# расширенные палитры (Возраст + RMS)
# === Материальные палитры ===
def hue_bronze_from_t(t: float) -> tuple[float, float, float]:
    # Бронза: коричнево-оранжевый переход
    t = clamp01(t)
    hue = 30.0 + 15.0 * t  # 30 (коричневый) -> 45 (оранжевый)
    sat = 0.7 + 0.1 * t
    val = 0.7 + 0.2 * t
    return (hue, sat, val)

def hue_pearl_from_t(t: float) -> tuple[float, float, float]:
    # Жемчуг: бело-розовый переход
    t = clamp01(t)
    hue = 0.0 + 10.0 * t  # 0 (белый) -> 10 (розоватый)
    sat = 0.05 + 0.15 * t
    val = 1.0 - 0.1 * t
    return (hue, sat, val)

def hue_coral_from_t(t: float) -> tuple[float, float, float]:
    # Коралл: розово-оранжевый переход
    t = clamp01(t)
    hue = 10.0 + 20.0 * t  # 10 (розовый) -> 30 (оранжевый)
    sat = 0.8 - 0.1 * t
    val = 0.9 - 0.1 * t
    return (hue, sat, val)

def hue_jade_from_t(t: float) -> tuple[float, float, float]:
    # Нефрит: зеленый переход
    t = clamp01(t)
    hue = 140.0 + 20.0 * t  # 140 (зеленый) -> 160 (сине-зеленый)
    sat = 0.7 + 0.1 * t
    val = 0.8 + 0.1 * t
    return (hue, sat, val)

def hue_topaz_from_t(t: float) -> tuple[float, float, float]:
    # Топаз: желто-голубой переход
    t = clamp01(t)
    hue = 50.0 + 70.0 * t  # 50 (желтый) -> 120 (голубой)
    sat = 0.7 + 0.2 * t
    val = 0.9 - 0.1 * t
    return (hue, sat, val)
def hue_gold_from_t(t: float) -> tuple[float, float, float]:
    # Золотой: желто-оранжевый переход (hue в градусах: 47 -> 72)
    t = clamp01(t)
    hue = 47.0 + 25.0 * t  # 47 (желтый) -> 72 (оранжевый)
    sat = 0.85 - 0.15 * t
    val = 1.0 - 0.1 * t
    return (hue, sat, val)

def hue_silver_from_t(t: float) -> tuple[float, float, float]:
    # Серебро: бело-серый переход
    # hue is fixed at 0.0 for grayscale; saturation increases slightly with t to add a subtle tint,
    # and value decreases to create a transition from bright silver to darker gray.
    t = clamp01(t)
    hue = 0.0
    sat = 0.0 + 0.05 * t
    val = 1.0 - 0.3 * t
    return (hue, sat, val)

def hue_copper_from_t(t: float) -> tuple[float, float, float]:
    # Медь: красно-оранжевый переход (hue в градусах: 18 -> 36)
    t = clamp01(t)
    hue = 18.0 + 18.0 * t  # 18 (оранжевый) -> 36 (красно-оранжевый)
    sat = 0.8 - 0.1 * t
    val = 0.9 - 0.2 * t
    return (hue, sat, val)

def hue_emerald_from_t(t: float) -> tuple[float, float, float]:
    # Изумруд: зеленый переход
    t = clamp01(t)
    hue = (0.33 + 0.07 * t) * 360.0  # 0.33 (зеленый) -> 0.40 (сине-зеленый) in degrees
    sat = 0.85 - 0.1 * t
    val = 1.0 - 0.1 * t
    return (hue, sat, val)

def hue_sapphire_from_t(t: float) -> tuple[float, float, float]:
    # Сапфир: синий переход
    t = clamp01(t)
    hue = (0.58 + 0.07 * t) * 360.0  # 0.58 (синий) -> 0.65 (фиолетово-синий), converted to degrees
    sat = 0.85 - 0.1 * t
    val = 1.0 - 0.1 * t
    return (hue, sat, val)

def hue_ruby_from_t(t: float) -> tuple[float, float, float]:
    # Рубин: красно-розовый переход
    t = clamp01(t)
    hue = (0.97 - 0.07 * t) * 360.0  # 0.97 (красный) -> 0.90 (розовый), now in degrees
    sat = 0.85 - 0.1 * t
    val = 1.0 - 0.1 * t
    return (hue, sat, val)

def hue_amethyst_from_t(t: float) -> tuple[float, float, float]:
    # Аметист: фиолетовый переход (hue в градусах: 273.6 -> 298.8)
    t = clamp01(t)
    hue = (0.76 + 0.07 * t) * 360.0  # 0.76 (фиолетовый) -> 0.83 (сине-фиолетовый) in degrees
    sat = 0.85 - 0.1 * t
    val = 1.0 - 0.1 * t
    return (hue, sat, val)

def hue_sepia_from_t(t: float) -> tuple[float, float, float]:
    """
    Sepia palette: brownish-yellow gradient.
    Hue is fixed at 30 (brown-yellow), saturation and value decrease with t.
    """
    t = clamp01(t)
    h = 30.0
    s = lerp(0.5, 0.2, t)
    v = lerp(0.9, 0.6, t)
    return h, s, v

def hue_grayscale_from_t(t: float) -> tuple:
    t = clamp01(t)
    # Градиент от белого к черному
    h = 0.0
    s = 0.0
    v = 1.0 - t
    return h, s, v

def hue_red_darkred_gray_black_from_t(t: float) -> tuple:
    t = clamp01(t)
    # Красный -> темно-красный -> серый -> черный
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

# Расширенные палитры (Возраст + RMS, Только RMS)
def hue_spring_from_t(t: float) -> tuple:
    t = clamp01(t)
    # Зеленый -> желтый -> розовый
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
    t = clamp01(t)
    # Желтый -> оранжевый -> красный
    h = 50 + t * 40  # 50-90
    s = 1.0
    v = 1.0
    return h, s, v

def hue_autumn_from_t(t: float) -> tuple:
    t = clamp01(t)
    # Оранжевый -> коричневый -> красный
    h = 30 + t * 30  # 30-60
    s = 0.7 + 0.3 * t
    v = 0.7 + 0.3 * (1-t)
    return h, s, v

def hue_winter_from_t(t: float) -> tuple:
    t = clamp01(t)
    # Голубой -> синий -> белый
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
    t = clamp01(t)
    # Голубой -> белый
    h = 190 + t * 20
    s = 0.3 + 0.7 * (1-t)
    v = 0.9 + 0.1 * t
    return h, s, v

def hue_forest_from_t(t: float) -> tuple:
    t = clamp01(t)
    # Зеленый -> темно-зеленый
    h = 120 + t * 30
    s = 0.7 + 0.3 * (1-t)
    v = 0.6 + 0.4 * t
    return h, s, v

def hue_desert_from_t(t: float) -> tuple:
    t = clamp01(t)
    # Песочный -> желтый -> светло-коричневый
    h = 40 + t * 20
    s = 0.6 + 0.4 * (1-t)
    v = 0.9
    return h, s, v

def hue_viridis_from_t(t: float) -> tuple:
    t = clamp01(t)
    # Зеленый -> синий -> желтый
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
    t = clamp01(t)
    # Темно-красный -> оранжевый -> желтый
    h = 10 + t * 50
    s = 1.0
    v = 0.7 + 0.3 * t
    return h, s, v

def hue_magma_from_t(t: float) -> tuple:
    t = clamp01(t)
    # Фиолетовый -> красный -> желтый
    h = 300 - t * 120
    s = 1.0
    v = 0.7 + 0.3 * t
    return h, s, v

def hue_plasma_from_t(t: float) -> tuple:
    t = clamp01(t)
    # Синий -> фиолетовый -> желтый
    h = 240 + t * 60
    s = 1.0
    v = 0.8 + 0.2 * t
    return h, s, v

def hue_cividis_from_t(t: float) -> tuple:
    t = clamp01(t)
    # Зеленый -> желтый -> коричневый
    h = 90 + t * 60
    s = 0.8 + 0.2 * t
    v = 0.7 + 0.3 * (1-t)
    return h, s, v

def hue_twilight_from_t(t: float) -> tuple:
    t = clamp01(t)
    # Синий -> фиолетовый -> розовый
    h = 240 + t * 60
    s = 0.7 + 0.3 * t
    v = 0.8 + 0.2 * (1-t)
    return h, s, v

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

def hue_sepia_from_t(t: float) -> tuple[float, float, float]:
    """
    Sepia palette: brownish-yellow gradient.
    Hue is fixed at 30 (brown-yellow), saturation and value decrease with t.
    """
    t = clamp01(t)
    h = 30.0
    s = lerp(0.5, 0.2, t)
    v = lerp(0.9, 0.6, t)
    return h, s, v

class PaletteState:
    def __init__(self):
        self.hue_offset = 0.0
        self.invert = False
        self.rms_palette_choice = "Blue->Green->Yellow->Red"
        self.age_palette_choice = "Blue->Green->Yellow->Red"

    def randomize(self):
        self.hue_offset = random.uniform(0 , 360)
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
    "Spring": "SPRING",        # Теперь уникальная палитра
    "Summer": "SUMMER",
    "Autumn": "AUTUMN",
    "Winter": "WINTER",
    "Ice": "ICE",
    "Forest": "FOREST",
    "Desert": "DESERT",
    "Viridis": "VIRIDIS",      # Теперь уникальная палитра
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
    "Retro": "RETRO",
    "Vintage": "VINTAGE",
    "Pastel": "PASTEL",
    "Candy": "CANDY",
    "Lime": "LIME",
    "Mint": "MINT",
    "Peach": "PEACH",
    "Lavender": "LAVENDER",
    "Rose": "ROSE",
    "Sky": "SKY",
    "Sand": "SAND",
    "Charcoal": "CHARCOAL",
    "Clouds": "CLOUDS",
    "Flame": "FLAME",
    
    # Базовые названия
    "Neon": "NEON",
    "Ukraine": "UKRAINE",
    "Cyberpunk": "CYBERPUNK",
    
    # HSV цветовые палитры
    "Monochrome": "GRAYSCALE",
    "Sepia": "SEPIA",
    "HighContrast": "RED_DARKRED_GRAY_BLACK",
    "LowContrast": "GRAYSCALE",
}

def palette_key(name: str) -> str:
    n = (name or "").replace("→","->").strip()
    return _PALETTE_ALIASES.get(n, "BGYR")

def apply_hue_offset(hue_deg: float) -> float:
    return (hue_deg + PALETTE_STATE.hue_offset) % 360.0

def maybe_invert_t(t: float) -> float:
    return 1.0 - t if PALETTE_STATE.invert else t

# возраст/выцветание

def max_age_slider_to_value(slider_percent: float) -> int:
    """
    Преобразует позицию слайдера (0-100%) в логарифмическое значение max_age.
    Первая половина слайдера (0-50%) покрывает диапазон 10-70.
    Вторая половина слайдера (50-100%) покрывает диапазон 70-500.
    """
    import math
    
    slider_percent = max(0.0, min(100.0, slider_percent))
    
    if slider_percent <= 50.0:
        # Первая половина: 10-70 (диапазон 60)
        t = slider_percent / 50.0  # 0.0 - 1.0
        return int(10 + t * 60)
    else:
        # Вторая половина: 70-500 (диапазон 430)
        t = (slider_percent - 50.0) / 50.0  # 0.0 - 1.0
        # Логарифмическое масштабирование для больших значений
        log_t = math.pow(t, 1.5)  # Ускоряем рост
        return int(70 + log_t * 430)

def max_age_value_to_slider(max_age: int) -> float:
    """
    Преобразует значение max_age обратно в позицию слайдера (0-100%).
    """
    import math
    
    max_age = max(10, min(500, max_age))
    
    if max_age <= 70:
        # Первая половина: 10-70
        t = (max_age - 10) / 60.0
        return t * 50.0
    else:
        # Вторая половина: 70-500
        value_range = max_age - 70
        max_range = 430
        log_t = value_range / max_range
        t = math.pow(log_t, 1.0/1.5)  # Обратное преобразование
        return 50.0 + t * 50.0

def age_to_t(age: int, max_age: int) -> float:
    """Оптимизированная функция возраста с кэшированием"""
    return _cached_age_to_t(age, max_age)

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
    """Оптимизированная функция конверсии HSV в RGB с кэшированием"""
    return _cached_hsv_to_rgb(h, s, v)


def color_from_age_rms(age: int, rms: float, rms_strength: float,
                       fade_start: int, max_age: int,
                       sat_drop_pct: float, val_drop_pct: float,
                       color_rms_min: float, color_rms_max: float,
                       global_v_mul: float,
                       age_palette: str, rms_palette: str, 
                       rms_mode: str = "brightness", 
                       blend_mode: str = "normal",
                       rms_enabled: bool = True,
                       palette_mix: float = 0.5) -> Tuple[int,int,int]:
    """
    Генерирует цвет клетки на основе возраста и RMS.
    
    Args:
        age: Возраст клетки
        rms: RMS значение аудио
        rms_strength: Сила влияния RMS (0-1)
        fade_start: Начало затухания
        max_age: Максимальный возраст
        sat_drop_pct: Процент падения насыщенности
        val_drop_pct: Процент падения яркости
        color_rms_min: Минимальное RMS для цвета
        color_rms_max: Максимальное RMS для цвета
        global_v_mul: Глобальный множитель яркости
        age_palette: Палитра для возраста
        rms_palette: Палитра для RMS
        rms_mode: Режим RMS ("brightness" | "palette" | "disabled")
        blend_mode: Режим блендинга палитр
        rms_enabled: Включена ли RMS палита
        palette_mix: Баланс между палитрами (0.0=только возраст, 1.0=только RMS)
    
    Returns:
        RGB цвет (r, g, b)
    """
    a = min(age, max_age if max_age > 0 else age)
    t_age_raw = age_to_t(a, max_age if max_age > 0 else max(12, a+1))
    t_age = maybe_invert_t(t_age_raw)
    # Инверсия age_palette
    if hasattr(locals().get('layer', None), 'invert_age_palette'):
        if getattr(locals()['layer'], 'invert_age_palette', False):
            t_age = 1.0 - t_age

    t_rms = norm_rms_for_color(rms, color_rms_min, color_rms_max)
    # Инверсия rms_palette
    if hasattr(locals().get('layer', None), 'invert_rms_palette'):
        if getattr(locals()['layer'], 'invert_rms_palette', False):
            t_rms = 1.0 - t_rms
    strength = clamp01(rms_strength)

    # Если RMS отключена, используем только возрастную палитру
    if not rms_enabled or rms_mode == "disabled":
        return color_from_age_only(age, fade_start, max_age, sat_drop_pct, val_drop_pct, 
                                 global_v_mul, age_palette)

    # В режиме "palette" смешиваем цвета из age_palette и rms_palette
    if rms_mode == "palette":
        # Получаем цвет от возраста (фиксированное значение для стабильности)
        age_color = color_from_age_only(age, fade_start, max_age, sat_drop_pct, val_drop_pct,
                                      global_v_mul, age_palette)
        
        # Получаем цвет от RMS
        rms_color = color_from_rms(rms, rms_palette, color_rms_min, color_rms_max, global_v_mul)
        
        # Комбинируем palette_mix (статичный баланс) с RMS интенсивностью (динамический)
        # palette_mix контролирует базовый баланс между палитрами
        # RMS добавляет динамическую модуляцию поверх этого баланса
        base_mix = clamp01(palette_mix)  # Статичный баланс 0.0-1.0
        rms_modulation = clamp01(t_rms * strength)  # Динамическая модуляция от RMS
        
        # Финальный mix factor: базовый баланс + RMS модуляция
        final_mix = clamp01(base_mix + rms_modulation * (1.0 - base_mix))
        
        # Смешиваем цвета с выбранным режимом блендинга
        final_color = blend_colors(age_color, rms_color, final_mix, blend_mode)
        
        return final_color

    # Режим "brightness" - RMS влияет на яркость и насыщенность
    return color_from_age_brightness_rms(age, rms, rms_strength, fade_start, max_age,
                                       sat_drop_pct, val_drop_pct, color_rms_min, color_rms_max,
                                       global_v_mul, age_palette)


def color_from_age_only(age: int, fade_start: int, max_age: int,
                       sat_drop_pct: float, val_drop_pct: float,
                       global_v_mul: float, age_palette: str) -> Tuple[int,int,int]:
    # ...existing code...
    a = min(age, max_age if max_age > 0 else age)
    t_age_raw = age_to_t(a, max_age if max_age > 0 else max(12, a+1))
    t_age = maybe_invert_t(t_age_raw)
    # Инверсия age_palette
    if hasattr(locals().get('layer', None), 'invert_age_palette'):
        if getattr(locals()['layer'], 'invert_age_palette', False):
            t_age = 1.0 - t_age

    pal = palette_key(age_palette)

    # --- МАТЕРИАЛЫ ---
    if pal == "GOLD":
        h,s,v = hue_gold_from_t(t_age); h = apply_hue_offset(h)
        v *= clamp01(global_v_mul)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        return _rgb_from_hsv(h, s*sat_mul, v*val_mul)
    elif pal == "SILVER":
        h,s,v = hue_silver_from_t(t_age); h = apply_hue_offset(h)
        v *= clamp01(global_v_mul)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        return _rgb_from_hsv(h, s*sat_mul, v*val_mul)
    elif pal == "COPPER":
        h,s,v = hue_copper_from_t(t_age); h = apply_hue_offset(h)
        v *= clamp01(global_v_mul)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        return _rgb_from_hsv(h, s*sat_mul, v*val_mul)
    elif pal == "EMERALD":
        h,s,v = hue_emerald_from_t(t_age); h = apply_hue_offset(h)
        v *= clamp01(global_v_mul)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        return _rgb_from_hsv(h, s*sat_mul, v*val_mul)
    elif pal == "SAPPHIRE":
        h,s,v = hue_sapphire_from_t(t_age); h = apply_hue_offset(h)
        v *= clamp01(global_v_mul)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        return _rgb_from_hsv(h, s*sat_mul, v*val_mul)
    elif pal == "RUBY":
        h,s,v = hue_ruby_from_t(t_age); h = apply_hue_offset(h)
        v *= clamp01(global_v_mul)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        return _rgb_from_hsv(h, s*sat_mul, v*val_mul)
    elif pal == "AMETHYST":
        h,s,v = hue_amethyst_from_t(t_age); h = apply_hue_offset(h)
        v *= clamp01(global_v_mul)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        return _rgb_from_hsv(h, s*sat_mul, v*val_mul)
    elif pal == "STEEL":
        # Можно использовать оттенок серого с небольшим синим
        h,s,v = 210.0, 0.08, 0.85
        h = apply_hue_offset(h)
        v *= clamp01(global_v_mul)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        return _rgb_from_hsv(h, s*sat_mul, v*val_mul)
    elif pal == "BRONZE":
        h,s,v = hue_bronze_from_t(t_age); h = apply_hue_offset(h)
        v *= clamp01(global_v_mul)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        return _rgb_from_hsv(h, s*sat_mul, v*val_mul)
    elif pal == "PEARL":
        h,s,v = hue_pearl_from_t(t_age); h = apply_hue_offset(h)
        v *= clamp01(global_v_mul)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        return _rgb_from_hsv(h, s*sat_mul, v*val_mul)
    elif pal == "CORAL":
        h,s,v = hue_coral_from_t(t_age); h = apply_hue_offset(h)
        v *= clamp01(global_v_mul)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        return _rgb_from_hsv(h, s*sat_mul, v*val_mul)
    elif pal == "JADE":
        h,s,v = hue_jade_from_t(t_age); h = apply_hue_offset(h)
        v *= clamp01(global_v_mul)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        return _rgb_from_hsv(h, s*sat_mul, v*val_mul)
    elif pal == "TOPAZ":
        h,s,v = hue_topaz_from_t(t_age); h = apply_hue_offset(h)
        v *= clamp01(global_v_mul)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        return _rgb_from_hsv(h, s*sat_mul, v*val_mul)

    # --- СПЕЦИАЛЬНЫЕ И ТЕМАТИЧЕСКИЕ ---
    elif pal == "UKRAINE":
        h,s,v = hue_ukraine_from_t(t_age); h = apply_hue_offset(h)
        v *= clamp01(global_v_mul)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        return _rgb_from_hsv(h, s*sat_mul, v*val_mul)
    elif pal == "NEON":
        h,s,v = hue_neon_from_t(t_age); h = apply_hue_offset(h)
        v *= clamp01(global_v_mul)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        return _rgb_from_hsv(h, s*sat_mul, v*val_mul)
    elif pal == "CYBERPUNK":
        h,s,v = hue_cyberpunk_from_t(t_age); h = apply_hue_offset(h)
        v *= clamp01(global_v_mul)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        return _rgb_from_hsv(h, s*sat_mul, v*val_mul)
    elif pal == "RETRO":
        # Пример: желто-оранжево-коричневая гамма
        h = lerp(40.0, 20.0, t_age)
        s = lerp(0.9, 0.7, t_age)
        v = lerp(1.0, 0.6, t_age) * clamp01(global_v_mul)
        h = apply_hue_offset(h)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        return _rgb_from_hsv(h, s*sat_mul, v*val_mul)
    elif pal == "VINTAGE":
        # Пример: сепия
        h = 30.0
        s = lerp(0.5, 0.2, t_age)
        v = lerp(0.9, 0.6, t_age) * clamp01(global_v_mul)
        h = apply_hue_offset(h)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        return _rgb_from_hsv(h, s*sat_mul, v*val_mul)
    elif pal == "PASTEL":
        # Пример: пастельные тона
        h = lerp(320.0, 60.0, t_age)
        s = lerp(0.4, 0.2, t_age)
        v = lerp(1.0, 0.85, t_age) * clamp01(global_v_mul)
        h = apply_hue_offset(h)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        return _rgb_from_hsv(h, s*sat_mul, v*val_mul)
    elif pal == "CANDY":
        # Пример: ярко-розовые и голубые
        h = lerp(330.0, 200.0, t_age)
        s = lerp(0.9, 0.7, t_age)
        v = lerp(1.0, 0.9, t_age) * clamp01(global_v_mul)
        h = apply_hue_offset(h)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        return _rgb_from_hsv(h, s*sat_mul, v*val_mul)

    # --- ПРИРОДНЫЕ ЦВЕТА ---
    elif pal == "LIME":
        h = 75.0
        s = lerp(0.9, 0.7, t_age)
        v = lerp(1.0, 0.8, t_age) * clamp01(global_v_mul)
        h = apply_hue_offset(h)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        return _rgb_from_hsv(h, s*sat_mul, v*val_mul)
    elif pal == "MINT":
        h = 160.0
        s = lerp(0.7, 0.5, t_age)
        v = lerp(1.0, 0.85, t_age) * clamp01(global_v_mul)
        h = apply_hue_offset(h)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        return _rgb_from_hsv(h, s*sat_mul, v*val_mul)
    elif pal == "PEACH":
        h = 20.0
        s = lerp(0.8, 0.5, t_age)
        v = lerp(1.0, 0.85, t_age) * clamp01(global_v_mul)
        h = apply_hue_offset(h)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        return _rgb_from_hsv(h, s*sat_mul, v*val_mul)
    elif pal == "LAVENDER":
        h = 270.0
        s = lerp(0.5, 0.3, t_age)
        v = lerp(1.0, 0.85, t_age) * clamp01(global_v_mul)
        h = apply_hue_offset(h)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        return _rgb_from_hsv(h, s*sat_mul, v*val_mul)
    elif pal == "ROSE":
        h = 340.0
        s = lerp(0.8, 0.5, t_age)
        v = lerp(1.0, 0.85, t_age) * clamp01(global_v_mul)
        h = apply_hue_offset(h)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        return _rgb_from_hsv(h, s*sat_mul, v*val_mul)
    elif pal == "SKY":
        h = 200.0
        s = lerp(0.7, 0.4, t_age)
        v = lerp(1.0, 0.85, t_age) * clamp01(global_v_mul)
        h = apply_hue_offset(h)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        return _rgb_from_hsv(h, s*sat_mul, v*val_mul)
    elif pal == "SAND":
        h = 40.0
        s = lerp(0.6, 0.3, t_age)
        v = lerp(1.0, 0.85, t_age) * clamp01(global_v_mul)
        h = apply_hue_offset(h)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        return _rgb_from_hsv(h, s*sat_mul, v*val_mul)
    elif pal == "CHARCOAL":
        h = 0.0
        s = 0.0
        v = lerp(0.3, 0.1, t_age) * clamp01(global_v_mul)
        h = apply_hue_offset(h)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        return _rgb_from_hsv(h, s*sat_mul, v*val_mul)
    elif pal == "CLOUDS":
        h = 210.0
        s = lerp(0.1, 0.0, t_age)
        v = lerp(1.0, 0.9, t_age) * clamp01(global_v_mul)
        h = apply_hue_offset(h)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        return _rgb_from_hsv(h, s*sat_mul, v*val_mul)
    elif pal == "FLAME":
        h = lerp(0.0, 45.0, t_age)
        s = lerp(1.0, 0.7, t_age)
        v = lerp(1.0, 0.8, t_age) * clamp01(global_v_mul)
        h = apply_hue_offset(h)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        return _rgb_from_hsv(h, s*sat_mul, v*val_mul)

    # --- СЕЗОННЫЕ, НАУЧНЫЕ, МОНОХРОМНЫЕ и др. ---
    elif pal == "SPRING":
        h,s,v = hue_spring_from_t(t_age); h = apply_hue_offset(h)
        v *= clamp01(global_v_mul)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        return _rgb_from_hsv(h, s*sat_mul, v*val_mul)
    elif pal == "SUMMER":
        h,s,v = hue_summer_from_t(t_age); h = apply_hue_offset(h)
        v *= clamp01(global_v_mul)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        return _rgb_from_hsv(h, s*sat_mul, v*val_mul)
    elif pal == "AUTUMN":
        h,s,v = hue_autumn_from_t(t_age); h = apply_hue_offset(h)
        v *= clamp01(global_v_mul)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        return _rgb_from_hsv(h, s*sat_mul, v*val_mul)
    elif pal == "WINTER":
        h,s,v = hue_winter_from_t(t_age); h = apply_hue_offset(h)
        v *= clamp01(global_v_mul)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        return _rgb_from_hsv(h, s*sat_mul, v*val_mul)
    elif pal == "ICE":
        h,s,v = hue_ice_from_t(t_age); h = apply_hue_offset(h)
        v *= clamp01(global_v_mul)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        return _rgb_from_hsv(h, s*sat_mul, v*val_mul)
    elif pal == "FOREST":
        h,s,v = hue_forest_from_t(t_age); h = apply_hue_offset(h)
        v *= clamp01(global_v_mul)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        return _rgb_from_hsv(h, s*sat_mul, v*val_mul)
    elif pal == "DESERT":
        h,s,v = hue_desert_from_t(t_age); h = apply_hue_offset(h)
        v *= clamp01(global_v_mul)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        return _rgb_from_hsv(h, s*sat_mul, v*val_mul)
    elif pal == "VIRIDIS":
        h,s,v = hue_viridis_from_t(t_age); h = apply_hue_offset(h)
        v *= clamp01(global_v_mul)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        return _rgb_from_hsv(h, s*sat_mul, v*val_mul)
    elif pal == "INFERNO":
        h,s,v = hue_inferno_from_t(t_age); h = apply_hue_offset(h)
        v *= clamp01(global_v_mul)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        return _rgb_from_hsv(h, s*sat_mul, v*val_mul)
    elif pal == "MAGMA":
        h,s,v = hue_magma_from_t(t_age); h = apply_hue_offset(h)
        v *= clamp01(global_v_mul)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        return _rgb_from_hsv(h, s*sat_mul, v*val_mul)
    elif pal == "PLASMA":
        h,s,v = hue_plasma_from_t(t_age); h = apply_hue_offset(h)
        v *= clamp01(global_v_mul)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        return _rgb_from_hsv(h, s*sat_mul, v*val_mul)
    elif pal == "CIVIDIS":
        h,s,v = hue_cividis_from_t(t_age); h = apply_hue_offset(h)
        v *= clamp01(global_v_mul)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        return _rgb_from_hsv(h, s*sat_mul, v*val_mul)
    elif pal == "TWILIGHT":
        h,s,v = hue_twilight_from_t(t_age); h = apply_hue_offset(h)
        v *= clamp01(global_v_mul)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        return _rgb_from_hsv(h, s*sat_mul, v*val_mul)

    # --- ОСТАЛЬНЫЕ ---
    elif pal == "RAINBOWSMOOTH":
        h,s,v = hue_rainbow_smooth_from_t(t_age); h = apply_hue_offset(h)
        v *= clamp01(global_v_mul)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        return _rgb_from_hsv(h, s*sat_mul, v*val_mul)
    elif pal == "SUNSET":
        h,s,v = hue_sunset_from_t(t_age); h = apply_hue_offset(h)
        v *= clamp01(global_v_mul)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        return _rgb_from_hsv(h, s*sat_mul, v*val_mul)
    elif pal == "AURORA":
        h,s,v = hue_aurora_from_t(t_age); h = apply_hue_offset(h)
        v *= clamp01(global_v_mul)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        return _rgb_from_hsv(h, s*sat_mul, v*val_mul)
    elif pal == "GALAXY":
        h,s,v = hue_galaxy_from_t(t_age); h = apply_hue_offset(h)
        v *= clamp01(global_v_mul)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        return _rgb_from_hsv(h, s*sat_mul, v*val_mul)
    elif pal == "TROPICAL":
        h,s,v = hue_tropical_from_t(t_age); h = apply_hue_offset(h)
        v *= clamp01(global_v_mul)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        return _rgb_from_hsv(h, s*sat_mul, v*val_mul)
    elif pal == "VOLCANO":
        h,s,v = hue_volcano_from_t(t_age); h = apply_hue_offset(h)
        v *= clamp01(global_v_mul)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        return _rgb_from_hsv(h, s*sat_mul, v*val_mul)
    elif pal == "DEEPSEA":
        h,s,v = hue_deepsea_from_t(t_age); h = apply_hue_offset(h)
        v *= clamp01(global_v_mul)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        return _rgb_from_hsv(h, s*sat_mul, v*val_mul)
    elif pal == "BGYR":
        hue_deg = hue_bgyr_from_t(t_age)
        hue_deg = apply_hue_offset(hue_deg)
        v = clamp01(global_v_mul)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        return _rgb_from_hsv(hue_deg, 0.85*sat_mul, v*val_mul)
    
    elif pal == "SEPIA":
        hue_deg = hue_sepia_from_t(t_age); 
        hue_deg = apply_hue_offset(hue_deg)
        v *= clamp01(global_v_mul)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        return _rgb_from_hsv(hue_deg, s*sat_mul, v*val_mul)

    # --- МОНОХРОМНЫЕ и КОНТРАСТНЫЕ ---
    elif pal == "GRAYSCALE":
        if t_age < 1/3:      v_age = lerp(1.0, 0.8, t_age*3.0)
        elif t_age < 2/3:    v_age = lerp(0.8, 0.5, (t_age-1/3)*3.0)
        else:                v_age = lerp(0.5, 0.25, (t_age-2/3)*3.0)
        v = v_age * clamp01(global_v_mul)
        _, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        v *= val_mul
        g = int(255*clamp01(v))
        return (g, g, g)
    elif pal == "RED_DARKRED_GRAY_BLACK":
        if t_age < 1/3:
            s = 1.0; v_age = lerp(1.0, 0.65, t_age*3.0); hue_deg = 0.0
        elif t_age < 2/3:
            k = (t_age-1/3)*3.0; s = lerp(1.0, 0.0, k); v_age = lerp(0.65, 0.25, k); hue_deg = 0.0
        else:
            k = (t_age-2/3)*3.0; s = 0.0; v_age = lerp(0.25, 0.0, k); hue_deg = 0.0
        v = v_age * clamp01(global_v_mul)
        hue_deg = apply_hue_offset(hue_deg)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        return _rgb_from_hsv(hue_deg, s*sat_mul, v*val_mul)

    # --- Fallback ---
    else:
        # Fallback
        return (128, 128, 128)


def color_from_age_brightness_rms(age: int, rms: float, rms_strength: float,
                                fade_start: int, max_age: int,
                                sat_drop_pct: float, val_drop_pct: float,
                                color_rms_min: float, color_rms_max: float,
                                global_v_mul: float, age_palette: str) -> Tuple[int,int,int]:
    """Генерирует цвет с RMS влиянием на яркость/насыщенность (старая логика)."""
    a = min(age, max_age if max_age>0 else age)
    t_age_raw = age_to_t(a, max_age if max_age>0 else max(12, a+1))
    t_age = maybe_invert_t(t_age_raw)

    t_rms = norm_rms_for_color(rms, color_rms_min, color_rms_max)
    strength = clamp01(rms_strength)

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
        return (g, g, g)
    elif pal == "SEPIA":
        h,s,v = hue_sepia_from_t(t_age); h = apply_hue_offset(h)
        v *= (0.65 + 0.35 * (t_rms * strength)) * clamp01(global_v_mul)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        return _rgb_from_hsv(h, s*sat_mul, v*val_mul)

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
        return _rgb_from_hsv(hue_deg, s*sat_mul, v*val_mul)

    elif pal == "FIRE":
        h,s,v = hue_fire_from_t(t_age); h = apply_hue_offset(h)
        v *= (0.65 + 0.35 * (t_rms * strength)) * clamp01(global_v_mul)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        return _rgb_from_hsv(h, s*sat_mul, v*val_mul)
    elif pal == "GOLD":
        h,s,v = hue_gold_from_t(t_age); h = apply_hue_offset(h)
        v *= (0.65 + 0.35 * (t_rms * strength)) * clamp01(global_v_mul)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        return _rgb_from_hsv(h, s*sat_mul, v*val_mul)
    elif pal == "SILVER":
        h,s,v = hue_silver_from_t(t_age); h = apply_hue_offset(h)
        v *= (0.65 + 0.35 * (t_rms * strength)) * clamp01(global_v_mul)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        return _rgb_from_hsv(h, s*sat_mul, v*val_mul)
    elif pal == "COPPER":
        h,s,v = hue_copper_from_t(t_age); h = apply_hue_offset(h)
        v *= (0.65 + 0.35 * (t_rms * strength)) * clamp01(global_v_mul)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        return _rgb_from_hsv(h, s*sat_mul, v*val_mul)
    elif pal == "EMERALD":
        h,s,v = hue_emerald_from_t(t_age); h = apply_hue_offset(h)
        v *= (0.65 + 0.35 * (t_rms * strength)) * clamp01(global_v_mul)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        return _rgb_from_hsv(h, s*sat_mul, v*val_mul)
    elif pal == "SAPPHIRE":
        h,s,v = hue_sapphire_from_t(t_age); h = apply_hue_offset(h)
        v *= (0.65 + 0.35 * (t_rms * strength)) * clamp01(global_v_mul)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        return _rgb_from_hsv(h, s*sat_mul, v*val_mul)
    elif pal == "RUBY":
        h,s,v = hue_ruby_from_t(t_age); h = apply_hue_offset(h)
        v *= (0.65 + 0.35 * (t_rms * strength)) * clamp01(global_v_mul)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        return _rgb_from_hsv(h, s*sat_mul, v*val_mul)
    elif pal == "AMETHYST":
        h,s,v = hue_amethyst_from_t(t_age); h = apply_hue_offset(h)
        v *= (0.65 + 0.35 * (t_rms * strength)) * clamp01(global_v_mul)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        return _rgb_from_hsv(h, s*sat_mul, v*val_mul)
    elif pal == "BRONZE":
        h,s,v = hue_bronze_from_t(t_age); h = apply_hue_offset(h)
        v *= (0.65 + 0.35 * (t_rms * strength)) * clamp01(global_v_mul)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        return _rgb_from_hsv(h, s*sat_mul, v*val_mul)
    elif pal == "PEARL":
        h,s,v = hue_pearl_from_t(t_age); h = apply_hue_offset(h)
        v *= (0.65 + 0.35 * (t_rms * strength)) * clamp01(global_v_mul)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        return _rgb_from_hsv(h, s*sat_mul, v*val_mul)
    elif pal == "CORAL":
        h,s,v = hue_coral_from_t(t_age); h = apply_hue_offset(h)
        v *= (0.65 + 0.35 * (t_rms * strength)) * clamp01(global_v_mul)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        return _rgb_from_hsv(h, s*sat_mul, v*val_mul)
    elif pal == "JADE":
        h,s,v = hue_jade_from_t(t_age); h = apply_hue_offset(h)
        v *= (0.65 + 0.35 * (t_rms * strength)) * clamp01(global_v_mul)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        return _rgb_from_hsv(h, s*sat_mul, v*val_mul)
    elif pal == "TOPAZ":
        h,s,v = hue_topaz_from_t(t_age); h = apply_hue_offset(h)
        v *= (0.65 + 0.35 * (t_rms * strength)) * clamp01(global_v_mul)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        return _rgb_from_hsv(h, s*sat_mul, v*val_mul)

    elif pal == "OCEAN":
        h,s,v = hue_ocean_from_t(t_age); h = apply_hue_offset(h)
        v *= (0.65 + 0.35 * (t_rms * strength)) * clamp01(global_v_mul)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        return _rgb_from_hsv(h, s*sat_mul, v*val_mul)

    elif pal == "NEON":
        h,s,v = hue_neon_from_t(t_age); h = apply_hue_offset(h)
        v *= (0.65 + 0.35 * (t_rms * strength)) * clamp01(global_v_mul)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        return _rgb_from_hsv(h, s*sat_mul, v*val_mul)

    elif pal == "UKRAINE":
        h,s,v = hue_ukraine_from_t(t_age); h = apply_hue_offset(h)
        v *= (0.65 + 0.35 * (t_rms * strength)) * clamp01(global_v_mul)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        return _rgb_from_hsv(h, s*sat_mul, v*val_mul)

    elif pal == "RAINBOWSMOOTH":
        h,s,v = hue_rainbow_smooth_from_t(t_age); h = apply_hue_offset(h)
        v *= (0.65 + 0.35 * (t_rms * strength)) * clamp01(global_v_mul)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        return _rgb_from_hsv(h, s*sat_mul, v*val_mul)

    elif pal == "SUNSET":
        h,s,v = hue_sunset_from_t(t_age); h = apply_hue_offset(h)
        v *= (0.65 + 0.35 * (t_rms * strength)) * clamp01(global_v_mul)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        return _rgb_from_hsv(h, s*sat_mul, v*val_mul)

    elif pal == "AURORA":
        h,s,v = hue_aurora_from_t(t_age); h = apply_hue_offset(h)
        v *= (0.65 + 0.35 * (t_rms * strength)) * clamp01(global_v_mul)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        return _rgb_from_hsv(h, s*sat_mul, v*val_mul)

    elif pal == "GALAXY":
        h,s,v = hue_galaxy_from_t(t_age); h = apply_hue_offset(h)
        v *= (0.65 + 0.35 * (t_rms * strength)) * clamp01(global_v_mul)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        return _rgb_from_hsv(h, s*sat_mul, v*val_mul)

    elif pal == "TROPICAL":
        h,s,v = hue_tropical_from_t(t_age); h = apply_hue_offset(h)
        v *= (0.65 + 0.35 * (t_rms * strength)) * clamp01(global_v_mul)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        return _rgb_from_hsv(h, s*sat_mul, v*val_mul)

    elif pal == "VOLCANO":
        h,s,v = hue_volcano_from_t(t_age); h = apply_hue_offset(h)
        v *= (0.65 + 0.35 * (t_rms * strength)) * clamp01(global_v_mul)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        return _rgb_from_hsv(h, s*sat_mul, v*val_mul)

    elif pal == "DEEPSEA":
        h,s,v = hue_deepsea_from_t(t_age); h = apply_hue_offset(h)
        v *= (0.65 + 0.35 * (t_rms * strength)) * clamp01(global_v_mul)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        return _rgb_from_hsv(h, s*sat_mul, v*val_mul)

    elif pal == "CYBERPUNK":
        h,s,v = hue_cyberpunk_from_t(t_age); h = apply_hue_offset(h)
        v *= (0.65 + 0.35 * (t_rms * strength)) * clamp01(global_v_mul)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        return _rgb_from_hsv(h, s*sat_mul, v*val_mul)

    elif pal == "BGYR":
        hue_deg = hue_bgyr_from_t(t_age)
        hue_deg = apply_hue_offset(hue_deg)
        v = (0.65 + 0.35 * (t_rms * strength)) * clamp01(global_v_mul)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        return _rgb_from_hsv(hue_deg, 0.85*sat_mul, v*val_mul)
    
    elif pal == "BRONZE":
        h,s,v = hue_bronze_from_t(t_age); h = apply_hue_offset(h)
        v *= (0.65 + 0.35 * (t_rms * strength)) * clamp01(global_v_mul)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        return _rgb_from_hsv(h, s*sat_mul, v*val_mul)
    elif pal == "PEARL":
        h,s,v = hue_pearl_from_t(t_age); h = apply_hue_offset(h)
        v *= (0.65 + 0.35 * (t_rms * strength)) * clamp01(global_v_mul)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        return _rgb_from_hsv(h, s*sat_mul, v*val_mul)
    elif pal == "CORAL":
        h,s,v = hue_coral_from_t(t_age); h = apply_hue_offset(h)
        v *= (0.65 + 0.35 * (t_rms * strength)) * clamp01(global_v_mul)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        return _rgb_from_hsv(h, s*sat_mul, v*val_mul)
    elif pal == "JADE":
        h,s,v = hue_jade_from_t(t_age); h = apply_hue_offset(h)
        v *= (0.65 + 0.35 * (t_rms * strength)) * clamp01(global_v_mul)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        return _rgb_from_hsv(h, s*sat_mul, v*val_mul)
    elif pal == "TOPAZ":
        h,s,v = hue_topaz_from_t(t_age); h = apply_hue_offset(h)
        v *= (0.65 + 0.35 * (t_rms * strength)) * clamp01(global_v_mul)
        sat_mul, val_mul = fade_factors(a, fade_start, max_age if max_age>0 else a+1, sat_drop_pct, val_drop_pct)
        return _rgb_from_hsv(h, s*sat_mul, v*val_mul)
    
    else:
        # Fallback
        return (128, 128, 128)


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
    """
    Generates an RGB color from RMS value and palette.
    For the BGYR palette, the value parameter for _rgb_from_hsv is determined by global_v_mul,
    and the saturation is fixed at 0.85.
    """
    palette_norm = palette_key(palette)
    t = maybe_invert_t(norm_rms_for_color(rms, color_rms_min, color_rms_max))
    # Инверсия rms_palette
    if hasattr(locals().get('layer', None), 'invert_rms_palette'):
        if getattr(locals()['layer'], 'invert_rms_palette', False):
            t = 1.0 - t

    if palette_norm == "BGYR":
        h,s,v = hue_bgyr_from_t(t)
        h = apply_hue_offset(h)
        sat = 0.85
        return _rgb_from_hsv(h, s*sat, v*clamp01(global_v_mul))

    elif palette_norm == "SEPIA":
        h,s,v = hue_sepia_from_t(t)
        h = apply_hue_offset(h)
        return _rgb_from_hsv(h, s, v * clamp01(global_v_mul))

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

    elif palette_norm == "RAINBOWSMOOTH":
        h,s,v = hue_rainbow_smooth_from_t(t); h = apply_hue_offset(h)
        return _rgb_from_hsv(h, s, v*clamp01(global_v_mul))

    elif palette_norm == "SUNSET":
        h,s,v = hue_sunset_from_t(t); h = apply_hue_offset(h)
        return _rgb_from_hsv(h, s, v*clamp01(global_v_mul))
    elif palette_norm == "BRONZE":
        h,s,v = hue_bronze_from_t(t); h = apply_hue_offset(h)
        return _rgb_from_hsv(h, s, v*clamp01(global_v_mul))
    elif palette_norm == "PEARL":
        h,s,v = hue_pearl_from_t(t); h = apply_hue_offset(h)
        return _rgb_from_hsv(h, s, v*clamp01(global_v_mul))
    elif palette_norm == "CORAL":
        h,s,v = hue_coral_from_t(t); h = apply_hue_offset(h)
        return _rgb_from_hsv(h, s, v*clamp01(global_v_mul))
    elif palette_norm == "JADE":
        h,s,v = hue_jade_from_t(t); h = apply_hue_offset(h)
        return _rgb_from_hsv(h, s, v*clamp01(global_v_mul))
    elif palette_norm == "TOPAZ":
        h,s,v = hue_topaz_from_t(t); h = apply_hue_offset(h)
        return _rgb_from_hsv(h, s, v*clamp01(global_v_mul))

    elif palette_norm == "AURORA":
        h,s,v = hue_aurora_from_t(t); h = apply_hue_offset(h)
        return _rgb_from_hsv(h, s, v*clamp01(global_v_mul))

    elif palette_norm == "GALAXY":
        h,s,v = hue_galaxy_from_t(t); h = apply_hue_offset(h)
        return _rgb_from_hsv(h, s, v*clamp01(global_v_mul))

    elif palette_norm == "TROPICAL":
        h,s,v = hue_tropical_from_t(t); h = apply_hue_offset(h)
        return _rgb_from_hsv(h, s, v*clamp01(global_v_mul))

    elif palette_norm == "VOLCANO":
        h,s,v = hue_volcano_from_t(t); h = apply_hue_offset(h)
        return _rgb_from_hsv(h, s, v*clamp01(global_v_mul))

    elif palette_norm == "DEEPSEA":
        h,s,v = hue_deepsea_from_t(t); h = apply_hue_offset(h)
        return _rgb_from_hsv(h, s, v*clamp01(global_v_mul))

    elif palette_norm == "CYBERPUNK":
        h,s,v = hue_cyberpunk_from_t(t); h = apply_hue_offset(h)
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
        from modern_gui import show_modern_gui
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

                rules_all    = ['Conway', 'HighLife', 'Seeds', 'Day & Night', 'Replicator', '34Life', 'Maze', 'Coral', 'Anneal', 'DryLife']
                # Используем новую группировку палитр
                age_palettes = HSV_DESIGN_PALETTES  # Для возраста используем 'Возраст + RMS'
                rms_palettes = HSV_COLOR_PALETTES   # Для RMS используем 'Только RMS'
                
                if diff_per_layer:
                    for i in range(layer_count):
                        layers_cfg.append({
                            'rule': rules_all[i % len(rules_all)],
                            'color_mode': result.get('color_mode', 'Возраст + RMS'),
                            'age_palette': age_palettes[i % len(age_palettes)],
                            'rms_palette': rms_palettes[(i+1) % len(rms_palettes)],
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
                'aging_speed': result.get('aging_speed', 10.0),
                'fade_start_age': result.get('fade_start', 60),
                'fade_saturation_drop': result.get('fade_sat_drop', 70),
                'fade_value_drop': result.get('fade_val_drop', 60),
                'clear_rms_threshold': result.get('clear_rms', DEFAULT_CLEAR_RMS),
                'color_rms_min': result.get('color_rms_min', DEFAULT_COLOR_RMS_MIN),
                'color_rms_max': result.get('color_rms_max', DEFAULT_COLOR_RMS_MAX),
                'soft_clear_enable': result.get('soft_clear_enable', True),
                'soft_clear_mode': result.get('soft_mode', 'Удалять клетки'),
                'clear_type': result.get('clear_type', 'Полная очистка'),
                'clear_partial_percent': result.get('clear_partial_percent', 50),
                'clear_age_threshold': result.get('clear_age_threshold', 10),
                'clear_random_percent': result.get('clear_random_percent', 30),
                'soft_kill_percentage': result.get('soft_kill_rate', 80),
                'soft_fade_floor': result.get('soft_fade_floor', 0.3),
                'soft_fade_down_percentage': result.get('soft_fade_down', 1),
                'soft_fade_up_percentage': result.get('soft_fade_up', 1),
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

# Spawn methods configuration
SPAWN_METHODS = [
    "Случайные точки",           # Классический случайный спавн
    "Стабильные блоки",          # Текущий метод (блоки 2x2)
    "Глайдеры",                  # Движущиеся паттерны
    "Осцилляторы",               # Мигающие паттерны
    "Смешанный",                 # Комбинация разных типов
    "Линии",                     # Горизонтальные/вертикальные линии
    "Кресты",                    # Крестообразные паттерны
    "Кольца",                    # Круглые структуры
]

def spawn_cells_random_points(grid: np.ndarray, count: int) -> None:
    """Классический случайный спавн отдельных клеток"""
    H, W = grid.shape
    if count <= 0:
        return
    
    # Создаем случайные координаты с отступом от краев
    margin = 2
    attempts = 0
    spawned = 0
    
    while spawned < count and attempts < count * 3:  # Ограничиваем попытки
        r = random.randrange(margin, H - margin)
        c = random.randrange(margin, W - margin)
        
        # Проверяем, свободна ли клетка
        if not grid[r, c]:
            grid[r, c] = True
            spawned += 1
        
        attempts += 1

def spawn_cells_stable_blocks(grid: np.ndarray, count: int) -> None:
    """Спавн стабильных блоков 2x2 (текущий метод)"""
    H, W = grid.shape
    if count <= 0 or H < 4 or W < 4:
        return
    
    blocks_to_create = max(1, count // 4)  # Один блок = 4 клетки
    
    created_blocks = 0
    for _ in range(blocks_to_create):
        attempts = 0
        while attempts < 10:  # Максимум 10 попыток
            r = random.randrange(2, H - 4)  # Увеличиваем отступ
            c = random.randrange(2, W - 4)
            
            # Проверим, свободно ли место 2x2
            if not grid[r:r+2, c:c+2].any():
                grid[r:r+2, c:c+2] = True
                created_blocks += 1
                break
            attempts += 1

def spawn_cells_gliders(grid: np.ndarray, count: int) -> None:
    """Спавн глайдеров (движущихся паттернов)"""
    H, W = grid.shape
    if count <= 0 or H < 6 or W < 6:
        return
    
    # Паттерн глайдера
    glider_pattern = np.array([
        [False, True,  False],
        [False, False, True ],
        [True,  True,  True ]
    ])
    
    gliders_to_create = max(1, count // 5)  # Один глайдер = 5 клеток
    
    for _ in range(gliders_to_create):
        attempts = 0
        while attempts < 10:
            r = random.randrange(2, H - 5)
            c = random.randrange(2, W - 5)
            
            # Проверяем область 3x3 для глайдера
            if not grid[r:r+3, c:c+3].any():
                grid[r:r+3, c:c+3] = glider_pattern
                break
            attempts += 1

def spawn_cells_oscillators(grid: np.ndarray, count: int) -> None:
    """Спавн осцилляторов (мигающих паттернов)"""
    H, W = grid.shape
    if count <= 0 or H < 5 or W < 5:
        return
    
    # Различные осцилляторы
    blinker = np.array([[True, True, True]])  # Период 2
    toad = np.array([
        [False, True,  True,  True ],
        [True,  True,  True,  False]
    ])  # Период 2
    beacon = np.array([
        [True,  True,  False, False],
        [True,  True,  False, False],
        [False, False, True,  True ],
        [False, False, True,  True ]
    ])  # Период 2
    
    patterns = [blinker, toad, beacon]
    oscillators_to_create = max(1, count // 6)
    
    for _ in range(oscillators_to_create):
        pattern = random.choice(patterns)
        ph, pw = pattern.shape
        
        attempts = 0
        while attempts < 10:
            r = random.randrange(2, H - ph - 2)
            c = random.randrange(2, W - pw - 2)
            
            if not grid[r:r+ph, c:c+pw].any():
                grid[r:r+ph, c:c+pw] = pattern
                break
            attempts += 1

def spawn_cells_mixed(grid: np.ndarray, count: int) -> None:
    """Смешанный спавн различных типов паттернов"""
    if count <= 0:
        return
    
    # Распределяем count между разными типами
    points_count = count // 4
    blocks_count = count // 4
    gliders_count = count // 4
    remaining = count - (points_count + blocks_count + gliders_count)
    
    spawn_cells_random_points(grid, points_count)
    spawn_cells_stable_blocks(grid, blocks_count)
    spawn_cells_gliders(grid, gliders_count)
    spawn_cells_random_points(grid, remaining)  # Остаток как случайные точки

def spawn_cells_lines(grid: np.ndarray, count: int) -> None:
    """Спавн линий (горизонтальных и вертикальных)"""
    H, W = grid.shape
    if count <= 0:
        return
    
    lines_to_create = max(1, count // 5)  # Одна линия ≈ 5 клеток
    
    for _ in range(lines_to_create):
        if random.random() < 0.5:
            # Горизонтальная линия
            length = min(random.randrange(3, 8), W - 4)
            r = random.randrange(2, H - 2)
            c = random.randrange(2, W - length - 2)
            
            if not grid[r, c:c+length].any():
                grid[r, c:c+length] = True
        else:
            # Вертикальная линия
            length = min(random.randrange(3, 8), H - 4)
            r = random.randrange(2, H - length - 2)
            c = random.randrange(2, W - 2)
            
            if not grid[r:r+length, c].any():
                grid[r:r+length, c] = True

def spawn_cells_crosses(grid: np.ndarray, count: int) -> None:
    """Спавн крестообразных паттернов"""
    H, W = grid.shape
    if count <= 0 or H < 6 or W < 6:
        return
    
    # Паттерн креста
    cross_pattern = np.array([
        [False, True,  False],
        [True,  True,  True ],
        [False, True,  False]
    ])
    
    crosses_to_create = max(1, count // 5)  # Один крест = 5 клеток
    
    for _ in range(crosses_to_create):
        attempts = 0
        while attempts < 10:
            r = random.randrange(2, H - 5)
            c = random.randrange(2, W - 5)
            
            if not grid[r:r+3, c:c+3].any():
                grid[r:r+3, c:c+3] = cross_pattern
                break
            attempts += 1

def spawn_cells_rings(grid: np.ndarray, count: int) -> None:
    """Спавн кольцевых структур"""
    H, W = grid.shape
    if count <= 0 or H < 8 or W < 8:
        return
    
    # Простое кольцо 5x5
    ring_pattern = np.array([
        [False, True,  True,  True,  False],
        [True,  False, False, False, True ],
        [True,  False, False, False, True ],
        [True,  False, False, False, True ],
        [False, True,  True,  True,  False]
    ])
    
    rings_to_create = max(1, count // 12)  # Одно кольцо ≈ 12 клеток
    
    for _ in range(rings_to_create):
        attempts = 0
        while attempts < 10:
            r = random.randrange(2, H - 7)
            c = random.randrange(2, W - 7)
            
            if not grid[r:r+5, c:c+5].any():
                grid[r:r+5, c:c+5] = ring_pattern
                break
            attempts += 1

def spawn_cells(grid: np.ndarray, count: int, method: str = "Стабильные блоки") -> None:
    """Главная функция спавна с выбором метода"""
    if method == "Случайные точки":
        spawn_cells_random_points(grid, count)
    elif method == "Стабильные блоки":
        spawn_cells_stable_blocks(grid, count)
    elif method == "Глайдеры":
        spawn_cells_gliders(grid, count)
    elif method == "Осцилляторы":
        spawn_cells_oscillators(grid, count)
    elif method == "Смешанный":
        spawn_cells_mixed(grid, count)
    elif method == "Линии":
        spawn_cells_lines(grid, count)
    elif method == "Кресты":
        spawn_cells_crosses(grid, count)
    elif method == "Кольца":
        spawn_cells_rings(grid, count)
    else:
        # Fallback к стабильным блокам
        spawn_cells_stable_blocks(grid, count)

# -------------------- Layer Generator --------------------

@dataclass 
class LayerConfig:
    """Конфигурация для создания слоя"""
    rule: str = "Conway"
    age_palette: str = "Fire"
    rms_palette: str = "Ocean" 
    color_mode: str = "HSV-дизайны"
    rms_mode: str = "brightness"  # "brightness" | "palette" | "disabled"
    blend_mode: str = "normal"  # "normal" | "additive" | "screen" | "multiply" | "overlay"
    rms_enabled: bool = True
    alpha_live: int = 220  # 0..255
    alpha_old: int = 140   # 0..255
    max_age: int = 60      # Максимальный возраст клеток
    mix: str = "Normal"    # "Normal" | "Additive"
    solo: bool = False
    mute: bool = False
    palette_mix: float = 0.5  # Баланс между палитрами: 0.0=только возраст, 1.0=только RMS
    spawn_method: str = "Стабильные блоки"  # Метод спавна клеток
    spawn_percent: int = 30  # Процент от максимального спавна (0-300%)


class LayerGenerator:
    """Класс для генерации слоев с индивидуальными параметрами"""
    
    def __init__(self):
        self.available_rules = CA_RULES
        self.available_spawn_methods = SPAWN_METHODS
        self.available_age_palettes = HSV_DESIGN_PALETTES
        self.available_rms_palettes = HSV_COLOR_PALETTES
        self.available_color_modes = ["HSV-дизайны", "HSV Палитры", "Высота ноты (Pitch)"]
        self.available_rms_modes = ["brightness", "palette", "disabled"]
        self.available_blend_modes = ["normal", "additive", "screen", "multiply", "overlay"]
        self.available_mix_modes = ["Normal", "Additive"]
        
    def create_layer_from_config(self, config: LayerConfig) -> Layer:
        """Создает оптимизированный слой из конфигурации"""
        # Создаем оптимизированные сетки для экономии памяти
        grid = _create_optimized_grid(GRID_H, GRID_W)
        age = _create_optimized_age_array(GRID_H, GRID_W)
        
        # Добавляем начальные клетки согласно выбранному методу
        # Преобразуем процент в количество клеток (базовое количество для инициализации)
        base_spawn_amount = SPAWN_SCALE  # Используем SPAWN_SCALE как базу
        actual_cells = int(base_spawn_amount * (config.spawn_percent / 100.0))
        spawn_cells(grid, max(1, actual_cells), config.spawn_method)
        
        # Устанавливаем начальный возраст для живых клеток
        age[grid] = 1
        
        # Создаем и возвращаем слой
        return Layer(
            grid=grid,
            age=age, 
            rule=config.rule,
            age_palette=config.age_palette,
            rms_palette=config.rms_palette,
            color_mode=config.color_mode,
            rms_mode=config.rms_mode,
            blend_mode=config.blend_mode,
            rms_enabled=config.rms_enabled,
            alpha_live=config.alpha_live,
            alpha_old=config.alpha_old,
            max_age=config.max_age,
            mix=config.mix,
            solo=config.solo,
            mute=config.mute,
            palette_mix=config.palette_mix,
            spawn_method=config.spawn_method
        )
    
    def generate_multiple_layers(self, layer_configs: List[LayerConfig]) -> List[Layer]:
        """Генерирует несколько слоев из списка конфигураций"""
        layers = []
        for config in layer_configs:
            layer = self.create_layer_from_config(config)
            layers.append(layer)
            print(f"🎨 Создан слой: {config.rule} | {config.age_palette}+{config.rms_palette} | α={config.alpha_live}/{config.alpha_old}")
        
        print(f"✅ Всего создано слоев: {len(layers)}")
        return layers
    
    def create_random_layer_config(self) -> LayerConfig:
        """Создает случайную конфигурацию слоя"""
        return LayerConfig(
            rule=random.choice(self.available_rules),
            age_palette=random.choice(self.available_age_palettes),
            rms_palette=random.choice(self.available_rms_palettes),
            color_mode=random.choice(self.available_color_modes),
            rms_mode=random.choice(self.available_rms_modes),
            blend_mode=random.choice(self.available_blend_modes),
            rms_enabled=random.choice([True, False]),
            alpha_live=random.randint(150, 255),
            alpha_old=random.randint(100, 200),
            mix=random.choice(self.available_mix_modes),
            solo=False,  # По умолчанию не соло
            mute=False,  # По умолчанию не заглушен
            spawn_method=random.choice(self.available_spawn_methods),
            spawn_percent=random.randint(20, 80)  # Процент 20-80%
        )
    
    def create_preset_configs(self, count: int, preset_type: str = "balanced") -> List[LayerConfig]:
        """Создает пресетные конфигурации слоев"""
        configs = []
        
        if preset_type == "balanced":
            # Сбалансированный пресет с разнообразием
            base_configs = [
                LayerConfig(rule="Conway", age_palette="Fire", rms_palette="Ocean", spawn_method="Стабильные блоки"),
                LayerConfig(rule="HighLife", age_palette="Aurora", rms_palette="Neon", spawn_method="Глайдеры"),
                LayerConfig(rule="Day&Night", age_palette="Galaxy", rms_palette="Cyberpunk", spawn_method="Осцилляторы"),
                LayerConfig(rule="Maze", age_palette="Tropical", rms_palette="Sunset", spawn_method="Случайные точки"),
                LayerConfig(rule="Seeds", age_palette="Volcano", rms_palette="Ukraine", spawn_method="Линии"),
            ]
            
        elif preset_type == "artistic":
            # Художественный пресет с красивыми палитрами
            base_configs = [
                LayerConfig(rule="Conway", age_palette="Sunset", rms_palette="Aurora", blend_mode="screen"),
                LayerConfig(rule="HighLife", age_palette="Galaxy", rms_palette="Tropical", blend_mode="additive"),
                LayerConfig(rule="Coral", age_palette="Ocean", rms_palette="Fire", blend_mode="overlay"),
                LayerConfig(rule="Maze", age_palette="Cyberpunk", rms_palette="Neon", blend_mode="multiply"),
            ]
            
        elif preset_type == "experimental":
            # Экспериментальный пресет с необычными правилами
            base_configs = [
                LayerConfig(rule="Replicator", age_palette="DeepSea", rms_palette="Volcano", spawn_method="Кольца"),
                LayerConfig(rule="Gnarl", age_palette="Cyberpunk", rms_palette="Ukraine", spawn_method="Кресты"),
                LayerConfig(rule="LifeWithoutDeath", age_palette="Fire", rms_palette="Ice", spawn_method="Смешанный"),
                LayerConfig(rule="Seeds", age_palette="Rainbow", rms_palette="Monochrome", spawn_method="Глайдеры"),
            ]
            
        else:  # random
            base_configs = [self.create_random_layer_config() for _ in range(5)]
        
        # Расширяем конфигурации до нужного количества
        for i in range(count):
            base_config = base_configs[i % len(base_configs)]
            
            # Модифицируем альфа-значения для разнообразия
            config = LayerConfig(
                rule=base_config.rule,
                age_palette=base_config.age_palette,
                rms_palette=base_config.rms_palette,
                color_mode=base_config.color_mode,
                rms_mode=base_config.rms_mode,
                blend_mode=base_config.blend_mode,
                rms_enabled=base_config.rms_enabled,
                alpha_live=max(150, base_config.alpha_live - i * 10),
                alpha_old=max(100, base_config.alpha_old - i * 5),
                mix=base_config.mix,
                solo=False,
                mute=False,
                spawn_method=base_config.spawn_method,
                spawn_percent=min(100, base_config.spawn_percent + i * 10)  # Увеличиваем процент на 10% для каждого следующего слоя
            )
            configs.append(config)
        
        return configs
    
    def update_layer_transparency(self, layer: Layer, alpha_live: int, alpha_old: int):
        """Обновляет прозрачность слоя"""
        layer.alpha_live = max(0, min(255, alpha_live))
        layer.alpha_old = max(0, min(255, alpha_old))

# -------------------- Цветовые функции --------------------

class RenderManager:
    def __init__(self, w_cells: int, h_cells: int, cell_size: int):
        self.wc = w_cells; self.hc = h_cells; self.cs = cell_size
        self.canvas = pygame.Surface((w_cells * cell_size, h_cells * cell_size)).convert()

    def clear(self, color=BG_COLOR):
        self.canvas.fill(color)

    def _has_layer_masks(self):
        """Helper to check if both last_age_mask and last_grid_mask exist."""
        return hasattr(self, 'last_age_mask') and hasattr(self, 'last_grid_mask')

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

            # --- Корректная генерация альфа-канала для каждого слоя ---
            if self._has_layer_masks():
                age_mask = self.last_age_mask
                grid_mask = self.last_grid_mask
                max_age = getattr(self, 'last_max_age', 60)
                old_mask = (age_mask >= max_age) & grid_mask
                live_mask = (age_mask < max_age) & grid_mask

                surf_w, surf_h = rgb_surf.get_size()
                mask_shape = age_mask.shape
                alpha_arr = np.zeros(mask_shape, dtype=np.uint8)
                alpha_arr[live_mask] = np.uint8(alpha_live)
                alpha_arr[old_mask] = np.uint8(alpha_old)

                # Масштабируем альфа-маску до размера поверхности
                if alpha_arr.shape != (surf_h, surf_w):
                    alpha_arr_t = np.transpose(alpha_arr, (1, 0))
                    try:
                        from scipy.ndimage import zoom
                        zoom_y = surf_h / alpha_arr_t.shape[1]
                        zoom_x = surf_w / alpha_arr_t.shape[0]
                        scaled_alpha_arr = zoom(alpha_arr_t, (zoom_x, zoom_y), order=0)
                        scaled_alpha_arr = scaled_alpha_arr.astype(np.uint8)
                    except ImportError:
                        alpha_mask_surf = pygame.surfarray.make_surface(np.stack([alpha_arr_t]*3, axis=-1))
                        alpha_mask_surf = pygame.transform.scale(alpha_mask_surf, (surf_w, surf_h))
                        scaled_alpha_arr = pygame.surfarray.array3d(alpha_mask_surf)[:,:,0].astype(np.uint8)
                else:
                    scaled_alpha_arr = np.transpose(alpha_arr, (1, 0)).astype(np.uint8)

                # Диагностика: вывод уникальных значений альфа-маски
                print(f"Alpha mask unique values after scaling: {np.unique(scaled_alpha_arr)}")

                rgb_surf = rgb_surf.convert_alpha()
                alpha_pixels = pygame.surfarray.pixels_alpha(rgb_surf)
                alpha_pixels[:, :] = scaled_alpha_arr
                del alpha_pixels
            else:
                # Fallback: если нет маски, применяем глобальный alpha ко всему слою
                rgb_surf.set_alpha(np.uint8(alpha_live))
            mode = (mix or "normal")
            try:
                mode_l = mode.lower()
            except Exception:
                mode_l = "normal"
            if mode_l in ("add", "additive", "blend_add"):
                self.canvas.blit(rgb_surf, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
            elif mode_l in ("multiply", "mult", "blend_mult"):
                self.canvas.blit(rgb_surf, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
            elif mode_l in ("screen",):
                arr_canvas = pygame.surfarray.pixels3d(self.canvas)
                arr_new = pygame.surfarray.pixels3d(rgb_surf)
                out = arr_canvas.astype(np.uint16) + arr_new.astype(np.uint16) - (arr_canvas.astype(np.uint16) * arr_new.astype(np.uint16)) // 255
                np.clip(out, 0, 255, out=out)
                arr_canvas[:] = out.astype(np.uint8)
                del arr_canvas, arr_new
            else:
                self.canvas.blit(rgb_surf, (0, 0))
        except Exception as e:
            print(f"ERROR in blit_layer: {e}")
            print(f"Image shape: {color_img.shape}, mix: {mix}")
            import traceback
            traceback.print_exc()
            # Fallback: always define surf
            surf = pygame.surfarray.make_surface(np.transpose(color_img, (1, 0, 2)))
            surf = pygame.transform.scale(surf, self.canvas.get_size())
            surf.set_colorkey((0, 0, 0))
            surf.set_alpha(alpha_live)
            surf.set_alpha(alpha_old)
            if mix == "Additive":
                self.canvas.blit(surf, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
            else:
                self.canvas.blit(surf, (0, 0))


# -------------------- Приложение --------------------

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
        try:
            rel_x = mouse_pos[0] - self.rect.x  # Используем rect.x вместо self.x
            ratio = max(0.0, min(1.0, rel_x / self.width))
            self.current_val = self.min_val + ratio * (self.max_val - self.min_val)
        except (TypeError, ValueError, ZeroDivisionError) as e:
            # Защита от некорректных значений
            print(f"Slider value update error: {e}")
            pass
    
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
                
                # Специальная обработка для логарифмического слайдера max_age
                if self.value_format == "max_age_log":
                    actual_max_age = max_age_slider_to_value(self.current_val)
                    value_text = f"{actual_max_age}"
                else:
                    value_text = str(self.value_format.format(self.current_val)).encode('ascii', 'ignore').decode('ascii')
                
                # Простые цвета текста
                label_color = SimpleColors.TEXT_PRIMARY
                value_color = SimpleColors.PRIMARY if self.dragging else SimpleColors.TEXT_SECONDARY
                
                label_surface = label_font.render(label_text, True, label_color)
                value_surface = value_font.render(value_text, True, value_color)
                
                # Размещаем текст ВНАДцм слайдером с достаточным отступом
                text_y = self.y - 40  # Увеличиваем отступ чтобы избежать наложения
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
        self.current_index = max(0, min(current_index, len(options) - 1)) if options else 0
        self.rect = pygame.Rect(x, y, width, height)
        self.is_open = False
        self.hover_index = -1
        self.scroll_offset = 0
        self.max_visible_items = 6
        self.selected_index = current_index  # Индекс выделенного элемента для навигации с клавиатуры
        self.search_text = ""  # Текст для быстрого поиска
        self.search_timer = 0  # Таймер для очистки поиска
        
    @property
    def expanded(self):
        """Alias для is_open для совместимости с кодом отрисовки"""
        return self.is_open
        
    @expanded.setter
    def expanded(self, value):
        """Setter для expanded"""
        self.is_open = value
        
    @property
    def current_value(self):
        if 0 <= self.current_index < len(self.options):
            return self.options[self.current_index]
        return ""
    
    def handle_event(self, event):
        """Обработка событий комбобокса"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                # Клик по основному элементу - переключаем состояние
                self.is_open = not self.is_open
                if self.is_open:
                    self.selected_index = self.current_index  # Синхронизируем выделение с текущим значением
                return True
            elif self.is_open:
                # Клик по выпадающему списку
                dropdown_rect = self._get_dropdown_rect()
                if dropdown_rect.collidepoint(event.pos):
                    # Определяем, по какому элементу кликнули
                    relative_y = event.pos[1] - dropdown_rect.y
                    item_index = int(relative_y // self.height) + self.scroll_offset
                    
                    if 0 <= item_index < len(self.options):
                        self.current_index = item_index
                        self.selected_index = item_index
                        self.is_open = False
                        return True
                else:
                    # Клик вне выпадающего списка - закрываем
                    self.is_open = False
                    return False
        
        elif event.type == pygame.MOUSEWHEEL and self.is_open:
            # Прокрутка в выпадающем списке
            dropdown_rect = self._get_dropdown_rect()
            if dropdown_rect.collidepoint(pygame.mouse.get_pos()):
                self.scroll_offset = max(0, min(self.scroll_offset - event.y, 
                                              len(self.options) - self.max_visible_items))
                return True
        
        elif event.type == pygame.KEYDOWN and self.is_open:
            # Навигация с клавиатуры по выпадающему списку
            if event.key == pygame.K_UP:
                # Стрелка вверх - перемещение к предыдущему элементу
                if self.selected_index > 0:
                    self.selected_index -= 1
                    # Автоскролл если нужно
                    if self.selected_index < self.scroll_offset:
                        self.scroll_offset = self.selected_index
                return True
            
            elif event.key == pygame.K_DOWN:
                # Стрелка вниз - перемещение к следующему элементу
                if self.selected_index < len(self.options) - 1:
                    self.selected_index += 1
                    # Автоскролл если нужно
                    if self.selected_index >= self.scroll_offset + self.max_visible_items:
                        self.scroll_offset = self.selected_index - self.max_visible_items + 1
                return True
            
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                # Enter или Space - выбор текущего выделенного элемента
                if 0 <= self.selected_index < len(self.options):
                    self.current_index = self.selected_index
                    self.is_open = False
                return True
            
            elif event.key == pygame.K_ESCAPE:
                # Escape - закрытие без изменений
                self.selected_index = self.current_index  # Возвращаем выделение
                self.is_open = False
                return True
            
            elif event.key == pygame.K_HOME:
                # Home - к первому элементу
                self.selected_index = 0
                self.scroll_offset = 0
                return True
            
            elif event.key == pygame.K_END:
                # End - к последнему элементу
                self.selected_index = len(self.options) - 1
                self.scroll_offset = max(0, len(self.options) - self.max_visible_items)
                return True
            
            elif event.key == pygame.K_PAGEUP:
                # Page Up - на страницу вверх
                self.selected_index = max(0, self.selected_index - self.max_visible_items)
                if self.selected_index < self.scroll_offset:
                    self.scroll_offset = self.selected_index
                return True
            
            elif event.key == pygame.K_PAGEDOWN:
                # Page Down - на страницу вниз
                self.selected_index = min(len(self.options) - 1, 
                                        self.selected_index + self.max_visible_items)
                if self.selected_index >= self.scroll_offset + self.max_visible_items:
                    self.scroll_offset = self.selected_index - self.max_visible_items + 1
                return True
            
            elif event.key == pygame.K_BACKSPACE:
                # Backspace - удаление последнего символа поиска
                if self.search_text:
                    self.search_text = self.search_text[:-1]
                    self.search_timer = pygame.time.get_ticks()
                return True
            
            else:
                # Обработка ввода символов для быстрого поиска
                if event.unicode and event.unicode.isprintable():
                    self.search_text += event.unicode.lower()
                    self.search_timer = pygame.time.get_ticks()
                    
                    # Ищем первое совпадение
                    for i, option in enumerate(self.options):
                        if option.lower().startswith(self.search_text):
                            self.selected_index = i
                            # Автоскролл к найденному элементу
                            if self.selected_index < self.scroll_offset:
                                self.scroll_offset = self.selected_index
                            elif self.selected_index >= self.scroll_offset + self.max_visible_items:
                                self.scroll_offset = self.selected_index - self.max_visible_items + 1
                            break
                    return True
        
        # Очистка поиска через 2 секунды бездействия
        if self.search_text and pygame.time.get_ticks() - self.search_timer > 2000:
            self.search_text = ""
        
        return False
    
    def _get_dropdown_rect(self):
        """Возвращает прямоугольник выпадающего списка"""
        visible_items = min(len(self.options), self.max_visible_items)
        dropdown_height = visible_items * self.height
        return pygame.Rect(self.x, self.y + self.height, self.width, dropdown_height)
    
    def draw(self, surface, font):
        """Отрисовка комбобокса"""
        # Синхронизируем координаты с rect
        self.x = self.rect.x
        self.y = self.rect.y
        
        # Основная кнопка
        bg_color = SimpleColors.ACTIVE if self.is_open else SimpleColors.SURFACE
        border_color = SimpleColors.BORDER_FOCUS if self.is_open else SimpleColors.BORDER
        
        pygame.draw.rect(surface, bg_color, self.rect, border_radius=8)
        pygame.draw.rect(surface, border_color, self.rect, 2, border_radius=8)
        
        # Текст текущего значения
        current_text = self.current_value if self.current_value else "Select..."
        text_surface = font.render(current_text, True, SimpleColors.TEXT_PRIMARY)
        text_x = self.x + 8
        text_y = self.y + (self.height - text_surface.get_height()) // 2
        surface.blit(text_surface, (text_x, text_y))
        
        # Стрелка
        arrow_text = "▲" if self.is_open else "▼"
        arrow_surface = font.render(arrow_text, True, SimpleColors.TEXT_SECONDARY)
        arrow_x = self.x + self.width - arrow_surface.get_width() - 8
        arrow_y = self.y + (self.height - arrow_surface.get_height()) // 2
        surface.blit(arrow_surface, (arrow_x, arrow_y))
        
        # Выпадающий список
        if self.is_open and self.options:
            dropdown_rect = self._get_dropdown_rect()
            
            # Фон выпадающего списка
            pygame.draw.rect(surface, SimpleColors.SURFACE, dropdown_rect, border_radius=8)
            pygame.draw.rect(surface, SimpleColors.BORDER, dropdown_rect, 2, border_radius=8)
            
            # Элементы списка
            visible_items = min(len(self.options), self.max_visible_items)
            for i in range(visible_items):
                option_index = i + self.scroll_offset
                if option_index >= len(self.options):
                    break
                    
                option_rect = pygame.Rect(
                    dropdown_rect.x + 2, 
                    dropdown_rect.y + i * self.height + 2,
                    dropdown_rect.width - 4, 
                    self.height - 2
                )
                
                # Подсветка при наведении, выборе или выделении клавиатурой
                mouse_pos = pygame.mouse.get_pos()
                is_hovered = option_rect.collidepoint(mouse_pos)
                is_selected = option_index == self.current_index
                is_keyboard_highlighted = option_index == self.selected_index
                
                if is_selected:
                    # Выбранный элемент - синий фон
                    pygame.draw.rect(surface, SimpleColors.PRIMARY, option_rect, border_radius=6)
                    text_color = SimpleColors.WHITE
                elif is_keyboard_highlighted:
                    # Выделенный клавиатурой элемент - светло-серый фон с рамкой
                    pygame.draw.rect(surface, SimpleColors.GRAY_100, option_rect, border_radius=6)
                    pygame.draw.rect(surface, SimpleColors.PRIMARY, option_rect, 2, border_radius=6)
                    text_color = SimpleColors.TEXT_PRIMARY
                elif is_hovered:
                    # Наведение мышью - слабая подсветка
                    pygame.draw.rect(surface, SimpleColors.GRAY_50, option_rect, border_radius=6)
                    text_color = SimpleColors.TEXT_PRIMARY
                else:
                    text_color = SimpleColors.TEXT_PRIMARY
                
                # Текст опции
                option_text = str(self.options[option_index])
                option_surface = font.render(option_text, True, text_color)
                option_text_x = option_rect.x + 6
                option_text_y = option_rect.y + (option_rect.height - option_surface.get_height()) // 2
                surface.blit(option_surface, (option_text_x, option_text_y))
            
            # Отображение текста поиска внизу списка
            if self.search_text:
                search_bg_rect = pygame.Rect(dropdown_rect.x, dropdown_rect.bottom + 2, dropdown_rect.width, 25)
                pygame.draw.rect(surface, SimpleColors.GRAY_800, search_bg_rect, border_radius=6)
                pygame.draw.rect(surface, SimpleColors.BORDER_FOCUS, search_bg_rect, 2, border_radius=6)
                
                search_display = f"Поиск: {self.search_text}_"
                search_surface = font.render(search_display, True, SimpleColors.WHITE)
                search_x = search_bg_rect.x + 6
                search_y = search_bg_rect.y + (search_bg_rect.height - search_surface.get_height()) // 2
                surface.blit(search_surface, (search_x, search_y))



# -------------------- Помощник формирования цвета клетки --------------------

def build_color_image(layer_grid: np.ndarray, layer_age: np.ndarray, mode: str,
                      rms: float, pitch: float, cfg: Dict[str, Any],
                      age_palette: str, rms_palette: str, 
                      rms_mode: str = "brightness",
                      blend_mode: str = "normal",
                      rms_enabled: bool = True,
                      max_age: int = 120,
                      palette_mix: float = 0.5) -> np.ndarray:
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
    
    for idx, (i, j) in enumerate(zip(ys, xs)):
        # Преобразуем индексы в int
        i, j = int(i), int(j)
        
        if i < 0 or i >= H or j < 0 or j >= W:
            continue
            
        if i >= layer_age.shape[0] or j >= layer_age.shape[1]:
            continue
            
        try:
            if mode == "Только RMS":
                color = color_from_rms(rms, rms_palette, cmin, cmax, v_mul)
            elif mode == "Высота ноты (Pitch)":
                color = color_from_pitch(pitch, rms, rms_strength, v_mul)
            else:
                color = color_from_age_rms(int(layer_age[i, j]), rms, rms_strength,
                                           fade_start, max_age, sat_drop, val_drop,
                                           cmin, cmax, v_mul, age_palette, rms_palette,
                                           rms_mode, blend_mode, rms_enabled, palette_mix)
            img[i, j] = color
        except Exception as e:
            print(f"Color calculation error at ({i},{j}): {e}")
            img[i, j] = (255, 255, 255)
    return img
# -------------------- Приложение --------------------

class App:
    def on_global_tick_ms_change(self, new_tick_ms):
        """Глобальное изменение интервала тика через HUD"""
        self.tick_ms = new_tick_ms
        for layer in self.layers:
            layer.tick_ms = new_tick_ms
        self.hud.update_from_app(self)
    def __init__(self, sel: Dict[str, Any]):
        self.sel = sel
        self.W = GRID_W * CELL_SIZE + FIELD_OFFSET_X
        self.H = GRID_H * CELL_SIZE

        pygame.init()
        self.screen = pygame.display.set_mode((self.W + HUD_WIDTH, self.H))  # Добавляем HUD_WIDTH
        pygame.display.set_caption("Guitar Life 4 — Ultimate")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("times new roman,georgia,serif", 16)
        self.show_hud = True  # параметр включения HUD
        self.smooth_scale = False  # параметр включения сглаженного масштабирования для HUD
        self.hud = HUD(self.font, self.H, 5, enabled=self.show_hud, smooth_scale=self.smooth_scale)  # Поддерживаем до 5 слоёв в GUI
        self.hud.on_parameter_change = self.on_hud_parameter_change
        self.hud.update_callbacks()  # Обновляем коллбэки после установки
        self.hud.app = self
        
        # Инициализация окна настроек
        self.settings_window = None
        if SETTINGS_WINDOW_AVAILABLE:
            self.settings_window = SettingsWindow(self)
        
        # HUD кэширование для оптимизации производительности
        self.hud_surface_cache = None
        self.hud_last_update = 0
        self.hud_cache_valid = False
        self.renderer = RenderManager(GRID_W, GRID_H, CELL_SIZE)
        self.layers: List[Layer] = []
        
        # Проверяем, используем ли мы конфигурацию слоёв из sel или из app_config.json
        use_config_file = sel.get('layers_different', True) and ('layers_cfg' not in sel or not sel['layers_cfg'])

        for i in range(sel['layer_count']):
            grid = np.zeros((GRID_H, GRID_W), dtype=bool)
            age = np.zeros((GRID_H, GRID_W), dtype=np.int32)

            # Проверяем размеры сетки
            if grid.shape != (GRID_H, GRID_W):
                grid = np.zeros((GRID_H, GRID_W), dtype=bool)
            if use_config_file:
                # Используем базовые настройки, они будут перезаписаны apply_different_layer_settings()
                layer_params = {
                    'rule': 'rule',
                    'age_palette': 'Blue->Green->Yellow->Red',
                    'rms_palette': 'Fire',
                    'color_mode': 'Возраст + RMS',
                    'rms_mode': 'brightness',
                    'alpha_live': 255,
                    'alpha_old': 255,
                    'mix': 'Normal',
                    'solo': False,
                    'mute': False }
            else:
                # Используем конфигурацию из sel['layers_cfg'] с проверкой границ
                layers_cfg = sel.get('layers_cfg', [])
                if i < len(layers_cfg):
                    row = layers_cfg[i]
                    # Нормализуем значения из GUI/конфига
                    mix_val = row.get('mix', 'Normal')
                    if isinstance(mix_val, str):
                        mix_val = mix_val.capitalize()
                    blend_val = row.get('blend_mode', row.get('blend', 'normal'))
                    if isinstance(blend_val, str):
                        blend_val = blend_val.lower()
                    layer_params = {
                        'rule': row.get('rule', 'Conway'),
                        'age_palette': row.get('age_palette', 'Blue->Green->Yellow->Red'),
                        'rms_palette': row.get('rms_palette', 'Blue->Green->Yellow->Red'),
                        'color_mode': row.get('color_mode', 'Возраст + RMS'),
                        'rms_mode': row.get('rms_mode', 'brightness'),
                        'alpha_live': int(row.get('alpha_live', row.get('alpha', 220))),
                        'alpha_old': int(row.get('alpha_old', row.get('alpha', 140))),
                        'mix': mix_val,
                        'solo': bool(row.get('solo', False)),
                        'mute': bool(row.get('mute', False)),
                        'blend_mode': blend_val,}
                else:
                    # Fallback к базовым настройкам если индекс выходит за границы
                    # Debug print removed
                    layer_params = {
                        'rule': 'Conway',
                        'age_palette': 'Fire',
                        'rms_palette': 'Ocean',
                        'color_mode': 'Возраст + RMS',
                        'rms_mode': 'brightness',
                        'alpha_live': 220,
                        'alpha_old': 140,
                        'mix': 'Normal',
                        'solo': False,
                        'mute': False
                    }

            layer = Layer(
                grid=grid,
                age=age,
                **layer_params
            )
            self.layers.append(layer)
        # Применяем разные настройки слоёв если нужно
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
        self.aging_speed = sel.get('aging_speed', 10.0)  # Ускорение старения (умножитель)
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
        self.soft_fade_up    = sel.get('soft_fade_up', 1)
        
        # Новые параметры контроля популяции
        self.max_cells_percent = sel.get('max_cells_percent', 90)  # Максимальный процент заполнения сетки
        self.soft_clear_threshold = sel.get('soft_clear_threshold', 80)  # При каком проценте начинать очистку
        self.age_bias = sel.get('age_bias', 20)  # Вероятность удаления старых клеток vs случайных
        self.old_cells_priority = sel.get('old_cells_priority', False)  # Приоритет старых клеток при удалении
        # self.clear_type = sel.get('clear_type', 'Полная очистка')  # Тип очистки для кнопки Clear
        # self.clear_partial_percent = sel.get('clear_partial_percent', 80)  # Процент для частичной очистки
        # self.clear_age_threshold = sel.get('clear_age_threshold', 1)  # Возрастной порог для очистки по возрасту
        
        # Spawn method
        self.spawn_method = sel.get('spawn_method', 'Стабильные блоки')  # Метод спавна новых клеток
        # self.clear_random_percent = sel.get('clear_random_percent', 30)  # Процент для случайной очистки

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
        
        # Инициализируем выбранный слой для редактирования
        self.selected_layer_index = 0  # По умолчанию выбран первый слой
        
        # Инициализируем LayerGenerator для создания новых слоев
        self.layer_generator = LayerGenerator()
        
        # Обновляем HUD после инициализации
        self.hud.update_from_app(self)
        
        # Обновляем контролы слоя для отображения выбранного слоя
        if self.layers:
            getattr(self.hud, 'update_layer_controls', lambda *a, **k: None)(self)

    # ---------- хоткей-пресет ----------
    def apply_joy_division(self):
        self.fx['scanlines'] = True
        self.fx['scan_strength'] = 0.35
        self.fx['posterize'] = True
        self.fx['poster_levels'] = 5
        PALETTE_STATE.invert = False
        PALETTE_STATE.hue_offset = 0.0
        for layer in self.layers:
            layer.age_palette = "White->LightGray->Gray->DarkGray"
            layer.rms_palette = "White->LightGray->DarkGray"

    def on_hud_parameter_change(self, param_name: str, value):
        # Обработка изменения aging_speed для слоя
        if param_name.startswith('layer_') and param_name.endswith('_aging_speed'):
            layer_idx = int(param_name.split('_')[1])
            if layer_idx < len(self.layers):
                aging_speed = max(1.0, min(10.0, float(value)))
                self.layers[layer_idx].aging_speed = aging_speed
                print(f" Layer {layer_idx+1} Aging Speed: {aging_speed}")
                self.save_layer_settings()
        """Обработчик изменений параметров из HUD"""
        # Инвалидируем кэш HUD при любом изменении параметров
        self.hud_cache_valid = False
        
        # Защита от некорректных значений
        try:
            # Обновляем параметры приложения
            if param_name == 'tick_ms':
                self.tick_ms = int(max(1, min(300, float(value))))
            elif param_name == 'rms_strength':
                self.rms_strength = int(max(0, min(500, float(value))))
            elif param_name == 'gain':
                global audio_gain
                self.gain = float(max(0.1, min(10.0, float(value))))
                audio_gain = self.gain  # Update global variable for audio callback
            elif param_name == 'max_age':
                self.max_age = int(max(1, min(1000, float(value))))
            elif param_name == 'aging_speed':
                self.aging_speed = float(max(0.1, min(10.0, float(value))))
            elif param_name == 'global_v_mul':
                self.global_v_mul = float(max(0.1, min(3.0, float(value))))
            elif param_name == 'hue_offset':
                self.hue_offset = float(max(0, min(360, float(value))))
            elif param_name == 'fade_sat_drop':
                self.fade_sat_drop = float(max(0, min(100, float(value))))
            elif param_name == 'fade_val_drop':
                self.fade_val_drop = float(max(0, min(100, float(value))))
            elif param_name == 'fade_start':
                self.fade_start = int(max(1, min(500, float(value))))
            elif param_name == 'clear_rms':
                self.sel['clear_rms'] = float(max(0.001, min(1.0, float(value))))
            elif param_name == 'color_rms_min':
                self.color_rms_min = float(max(0.001, min(1.0, float(value))))
            elif param_name == 'color_rms_max':
                self.color_rms_max = float(max(0.001, min(1.0, float(value))))
            elif param_name == 'soft_kill_rate':
                self.soft_kill_rate = int(max(0, min(100, float(value))))
                self.sel['soft_kill_rate'] = self.soft_kill_rate
            elif param_name == 'soft_fade_floor':
                self.soft_fade_floor = float(max(0.0, min(1.0, float(value))))
                self.sel['soft_fade_floor'] = self.soft_fade_floor
            elif param_name == 'soft_fade_down':
                self.soft_fade_down = int(max(1, min(100, float(value))))
                self.sel['soft_fade_down'] = self.soft_fade_down
            elif param_name == 'soft_fade_up':
                self.soft_fade_up = int(max(1, min(100, float(value))))
                self.sel['soft_fade_up'] = self.soft_fade_up
            elif param_name == 'max_cells_percent':
                self.max_cells_percent = int(max(10, min(100, float(value))))
                self.sel['max_cells_percent'] = self.max_cells_percent
            elif param_name == 'soft_clear_threshold':
                self.soft_clear_threshold = int(max(10, min(100, float(value))))
                self.sel['soft_clear_threshold'] = self.soft_clear_threshold
            elif param_name == 'age_bias':
                self.age_bias = int(max(0, min(100, float(value))))
                self.sel['age_bias'] = self.age_bias
            elif param_name == 'pitch_tick_min':
                self.pitch_tick_min = int(max(1, min(1000, float(value))))
            elif param_name == 'pitch_tick_max':
                self.pitch_tick_max = int(max(1, min(5000, float(value))))
            elif param_name == 'clear_partial_percent':
                self.clear_partial_percent = int(max(10, min(90, float(value))))
                self.sel['clear_partial_percent'] = self.clear_partial_percent
            elif param_name == 'clear_age_threshold':
                self.clear_age_threshold = int(max(1, min(100, float(value))))
                self.sel['clear_age_threshold'] = self.clear_age_threshold
            elif param_name == 'clear_random_percent':
                self.clear_random_percent = int(max(10, min(90, float(value))))
                self.sel['clear_random_percent'] = self.clear_random_percent
        except (ValueError, TypeError):
            print(f" Invalid value for {param_name}: {value}")
            return
            
        # Булевые параметры
        if param_name == 'pitch_tick_enable':
            self.pitch_tick_enable = bool(value)
        elif param_name == 'rms_modulation':
            # Добавляем поддержку RMS модуляции если ее нет
            self.rms_modulation = bool(value)
        elif param_name == 'soft_clear_enable':
            self.soft_clear_enable = bool(value)
            self.sel['soft_clear_enable'] = self.soft_clear_enable
        elif param_name == 'soft_mode':
            # Преобразуем значение комбобокса в внутреннее представление
            if value == "Kill":
                self.soft_mode = 'Удалять клетки'
            elif value == "Fade":
                self.soft_mode = 'Затухание клеток'
            elif value == "Fade+Kill":
                self.soft_mode = 'Затухание + удаление'
            self.sel['soft_mode'] = self.soft_mode
        elif param_name == 'soft_mode_toggle':
            # Оставляем для обратной совместимости
            self.soft_mode = 'Затухание клеток' if value else 'Удалять клетки'
        elif param_name == 'old_cells_priority':
            self.old_cells_priority = bool(value)
        elif param_name == 'clear_type':
            self.clear_type = str(value)
        elif param_name == 'mirror_x':
            self.mirror_x = bool(value)
        elif param_name == 'mirror_y':
            self.mirror_y = bool(value)
        # FX параметры
        elif param_name.startswith('fx_'):
            fx_name = param_name[3:]  # Убираем префикс 'fx_'
            self.fx[fx_name] = bool(value)
        # elif param_name == 'fx_scan_strength':
        #     self.fx['scan_strength'] = float(max(0.0, min(1.0, float(value))))
        # Действия кнопок
        elif param_name == 'random_pattern':
            self.clear_all_layers()
            self.generate_random_patterns()
        elif param_name == 'clear':
            self.clear_with_type()
        elif param_name == 'test':
            self.create_test_pattern()
        elif param_name == 'reset_defaults':
            self.reset_to_defaults()
        elif param_name == 'save_preset':
            self.save_current_preset()
        elif param_name == 'load_preset':
            self.load_preset_dialog()
        elif param_name == 'joy_division':
            self.apply_joy_division()
        elif param_name == 'conway_gliders':
            self.create_glider_pattern()
        # elif param_name == 'spawn_method':
        #     self.spawn_method = str(value)
            
        # Слой-специфичные параметры
        elif param_name == 'layer_count':
            new_count = int(max(1, min(5, float(value))))
            self.adjust_layer_count(new_count)
        elif param_name == 'layer_alpha':
            if hasattr(self, 'selected_layer_index'):
                self.layers[self.selected_layer_index].alpha = float(max(0.0, min(1.0, float(value))))
        elif param_name == 'layer_blend_mode':
            if hasattr(self, 'selected_layer_index'):
                self.layers[self.selected_layer_index].blend_mode = str(value)
        elif param_name == 'layer_rule':
            if hasattr(self, 'selected_layer_index'):
                self.layers[self.selected_layer_index].rule = str(value)
        elif param_name == 'layer_age_palette':
            if hasattr(self, 'selected_layer_index'):
                self.layers[self.selected_layer_index].age_palette = str(value)
        elif param_name == 'layer_rms_palette':
            if hasattr(self, 'selected_layer_index'):
                self.layers[self.selected_layer_index].rms_palette = str(value)
        elif param_name == 'layer_mute':
            if hasattr(self, 'selected_layer_index'):
                self.layers[self.selected_layer_index].muted = bool(value)
        elif param_name == 'layer_solo':
            if hasattr(self, 'selected_layer_index'):
                self.layers[self.selected_layer_index].solo = bool(value)
        elif param_name == 'layer_mirror_x':
            if hasattr(self, 'selected_layer_index'):
                self.layers[self.selected_layer_index].mirror_x = bool(value)
        elif param_name == 'layer_mirror_y':
            if hasattr(self, 'selected_layer_index'):
                self.layers[self.selected_layer_index].mirror_y = bool(value)
        elif param_name.startswith('layer_select_'):
            # Обработка выбора слоя
            layer_index = int(param_name.split('_')[2])
            if 0 <= layer_index < len(self.layers):
                self.selected_layer_index = layer_index
                print(f" Выбран слой {layer_index + 1} для редактирования")
                # Обновляем HUD для отображения параметров выбранного слоя
                if hasattr(self, 'hud'):
                    getattr(self.hud, 'update_layer_controls', lambda *a, **k: None)(self)
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
                print(f" Layer {layer_idx+1} Age Palette changed to: {value}")
                self.save_layer_settings()  # Сохраняем настройки
                self.hud.update_from_app(self)  # Обновляем GUI
        elif param_name.startswith('layer_') and '_rms_palette' in param_name:
            # Извлекаем номер слоя из имени параметра
            layer_idx = int(param_name.split('_')[1])
            if layer_idx < len(self.layers):
                self.layers[layer_idx].rms_palette = str(value)
                print(f" Layer {layer_idx+1} RMS Palette changed to: {value}")
                self.save_layer_settings()  # Сохраняем настройки
                self.hud.update_from_app(self)  # Обновляем GUI
        elif param_name.startswith('layer_') and '_alpha_live' in param_name:
            # Обработка alpha_live слайдера
            layer_idx = int(param_name.split('_')[1])
            if layer_idx < len(self.layers):
                self.layers[layer_idx].alpha_live = int(max(0, min(255, float(value))))
                print(f" Layer {layer_idx+1} Alpha Live: {self.layers[layer_idx].alpha_live}")
                self.save_layer_settings()
        elif param_name.startswith('layer_') and '_alpha_old' in param_name:
            # Обработка alpha_old слайдера
            layer_idx = int(param_name.split('_')[1])
            if layer_idx < len(self.layers):
                self.layers[layer_idx].alpha_old = int(max(0, min(255, float(value))))
                print(f" Layer {layer_idx+1} Alpha Old: {self.layers[layer_idx].alpha_old}")
                self.save_layer_settings()
        elif param_name.startswith('layer_') and '_max_age' in param_name:
            # Обработка максимального возраста клеток (логарифмический слайдер)
            layer_idx = int(param_name.split('_')[1])
            if layer_idx < len(self.layers):
                slider_percent = max(0, min(100, float(value)))
                max_age_value = max_age_slider_to_value(slider_percent)
                self.layers[layer_idx].max_age = max_age_value
                print(f"🔧 Layer {layer_idx+1} Max Age: {max_age_value} (slider: {slider_percent:.1f}%)")
                self.save_layer_settings()
        elif param_name.startswith('layer_') and '_rule' in param_name:
            # Обработка изменения правила (не циклирование, а прямое назначение)
            layer_idx = int(param_name.split('_')[1])
            if layer_idx < len(self.layers):
                self.layers[layer_idx].rule = str(value)
                print(f" Layer {layer_idx+1} Rule set to: {value}")
                self.save_layer_settings()
        elif param_name.startswith('layer_') and '_spawn_percent' in param_name:
            # Обработка процента спавна клеток (0-300%)
            layer_idx = int(param_name.split('_')[1])
            if layer_idx < len(self.layers):
                spawn_percent = max(0, min(300, float(value)))
                layer = self.layers[layer_idx]
                layer.spawn_percent = spawn_percent
                print(f" Layer {layer_idx+1} Spawn Rate: {spawn_percent:.0f}% (max {SPAWN_SCALE} cells)")
                # Пересчёт клеток: очищаем слой и спавним новое количество
                layer.grid[:] = False
                layer.age[:] = 0
                new_cells = int(SPAWN_SCALE * (spawn_percent / 100.0))
                spawn_cells(layer.grid, new_cells, layer.spawn_method)
                layer.age[layer.grid] = 1
                self.save_layer_settings()
                self.hud.update_from_app(self)  # Обновить HUD
        elif param_name.startswith('layer_') and '_blend_mode' in param_name:
            # Извлекаем номер слоя из имени параметра
            layer_idx = int(param_name.split('_')[1])
            if layer_idx < len(self.layers):
                # Преобразуем UI значение в внутреннее
                blend_mode = value.lower()
                self.layers[layer_idx].blend_mode = blend_mode
                print(f" Layer {layer_idx+1} Blend Mode changed to: {blend_mode}")
                self.save_layer_settings()  # Сохраняем настройки
                self.hud.update_from_app(self)  # Обновляем GUI
        elif param_name.startswith('layer_') and '_rms_mode' in param_name:
            # Извлекаем номер слоя из имени параметра
            layer_idx = int(param_name.split('_')[1])
            if layer_idx < len(self.layers):
                # Преобразуем UI значение в внутреннее
                rms_mode = value.lower()
                self.layers[layer_idx].rms_mode = rms_mode
                print(f" Layer {layer_idx+1} RMS Mode changed to: {rms_mode}")
                self.save_layer_settings()  # Сохраняем настройки
                self.hud.update_from_app(self)  # Обновляем GUI
        elif param_name.startswith('layer_') and '_spawn_method' in param_name:
            # Обработка метода спавна
            layer_idx = int(param_name.split('_')[1])
            if layer_idx < len(self.layers):
                spawn_method = str(value)
                self.layers[layer_idx].spawn_method = spawn_method
                print(f"🌱 Layer {layer_idx+1} Spawn Method: {spawn_method}")
                self.save_layer_settings()  # Сохраняем настройки
        elif param_name.startswith('layer_') and '_solo' in param_name:
            # Обработка кнопки Solo
            layer_idx = int(param_name.split('_')[1])
            if layer_idx < len(self.layers):
                # Переключаем solo режим
                self.layers[layer_idx].solo = not self.layers[layer_idx].solo
                # Если включили solo, выключаем у всех остальных 
                if self.layers[layer_idx].solo:
                    for i, layer in enumerate(self.layers):
                        if i != layer_idx:
                            layer.solo = False
                print(f" Layer {layer_idx + 1} Solo: {'ON' if self.layers[layer_idx].solo else 'OFF'}")
                self.save_layer_settings()  # Сохраняем настройки
                self.hud.update_from_app(self)
        elif param_name.startswith('layer_') and '_mute' in param_name:
            # Обработка кнопки Mute
            layer_idx = int(param_name.split('_')[1])
            if layer_idx < len(self.layers):
                self.layers[layer_idx].mute = not self.layers[layer_idx].mute
                print(f" Layer {layer_idx + 1} Mute: {'ON' if self.layers[layer_idx].mute else 'OFF'}")
                self.save_layer_settings()  # Сохраняем настройки
                self.hud.update_from_app(self)
        elif param_name.startswith('layer_') and '_palette_mix' in param_name:
            # Обработка слайдера баланса палитр
            layer_idx = int(param_name.split('_')[1])
            if layer_idx < len(self.layers):
                palette_mix = max(0.0, min(1.0, float(value)))
                self.layers[layer_idx].palette_mix = palette_mix
                print(f" Layer {layer_idx + 1} Palette Mix: {palette_mix:.2f} (Age←→RMS)")
                self.save_layer_settings()  # Сохраняем настройки
        
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

    def cycle_layer_rule(self, layer_idx: int):
        """Переключает правило клеточного автомата для указанного слоя"""
        if layer_idx < 0 or layer_idx >= len(self.layers):
            print(f" Invalid layer index: {layer_idx}")
            return
            
        # Список доступных правил
        available_rules = [
            "Conway", "HighLife", "Day&Night", "Replicator", 
            "Seeds", "Maze", "Coral", "LifeWithoutDeath", "Gnarl"
        ]
        
        current_rule = self.layers[layer_idx].rule
        try:
            current_index = available_rules.index(current_rule)
            next_index = (current_index + 1) % len(available_rules)
        except ValueError:
            # Если текущее правило не найдено, начинаем с Conway
            next_index = 0
            
        new_rule = available_rules[next_index]
        self.layers[layer_idx].rule = new_rule
        
        print(f" Layer {layer_idx + 1} rule changed: {current_rule} → {new_rule}")
        
        # Сохраняем настройки и обновляем HUD
        self.save_layer_settings()
        if hasattr(self, 'hud'):
            self.hud.update_from_app(self)
            self.hud_cache_valid = False  # Инвалидируем кэш

    def invalidate_hud_cache(self):
        """Принудительно инвалидирует кэш HUD"""
        self.hud_cache_valid = False

    def change_layer_count(self, new_count: int):
        """Изменяет количество слоев"""
        new_count = max(1, min(5, new_count))  # Ограничиваем от 1 до 5 слоев
        current_count = len(self.layers)
        
        if new_count > current_count:
            # Загружаем настройки из конфигурации using modern resource management
            try:
                if resource_manager:
                    config = load_app_config()
                    layer_settings = config.get('layers', {}).get('layer_settings', [])
                else:
                    # Fallback to old method
                    with open('app_config.json', 'r', encoding='utf-8') as f:
                        config = json.load(f)
                    layer_settings = config.get('layers', {}).get('layer_settings', [])
            except:
                layer_settings = []
                
            # Добавляем новые слои
            for i in range(current_count, new_count):
                new_layer = self.create_layer()
                new_layer.rule = 'Conway'
                new_layer.age_palette = 'Blue->Green->Yellow->Red'
                new_layer.rms_palette = 'Fire'
                self.layers.append(new_layer)
                print(f" Добавлен слой {i+1}")
        elif new_count < current_count:
            # Удаляем лишние слои
            removed_count = current_count - new_count
            self.layers = self.layers[:new_count]
            print(f"➖ Удалено {removed_count} слоев")
        
        print(f" Общее количество слоев: {len(self.layers)}")
        
        # Инициализируем выбранный слой если нужно
        if not hasattr(self, 'selected_layer_index') or self.selected_layer_index >= len(self.layers):
            self.selected_layer_index = 0

    def create_layer(self) -> Layer:
        """Создает новый оптимизированный слой с базовыми настройками"""
        grid = _create_optimized_grid(GRID_H, GRID_W)
        age = _create_optimized_age_array(GRID_H, GRID_W)
        
        # Палитры для разнообразия - возьмем случайные из доступных
        age_palettes = ["Fire", "Ocean", "Sunset", "Aurora", "Galaxy", "Cyberpunk"]
        rms_palettes = ["Ocean", "Neon", "Tropical", "DeepSea", "Rainbow", "Ukraine"]
        
        age_palette = age_palettes[len(self.layers) % len(age_palettes)]
        rms_palette = rms_palettes[len(self.layers) % len(rms_palettes)]
        
        return Layer(
            grid=grid, 
            age=age,
            rule='Conway',
            age_palette=age_palette,
            rms_palette=rms_palette,
            color_mode="HSV-дизайны",
            rms_mode="brightness",
            blend_mode="normal",
            rms_enabled=True,
            alpha_live=220,
            alpha_old=140,
            max_age=60,
            mix="Normal",
            solo=False,
            mute=False,
            palette_mix=0.5,
            spawn_method="Стабильные блоки"
        )

    # ---------- внутренняя логика ----------
    def maybe_tick_interval(self, pitch_hz: float) -> int:
        if not self.pitch_tick_enable or pitch_hz <= 0:
            # Always use the latest tick_ms from App
            return self.tick_ms
        # логарифмическая проекция частоты в интервал тика
        p = np.clip((math.log2(pitch_hz) - math.log2(80.0)) /
                    (math.log2(1500.0) - math.log2(80.0)), 0.0, 1.0)
        return int(self.pitch_tick_max + (self.pitch_tick_min - self.pitch_tick_max) * p)

    def soft_clear(self):
        if not self.soft_clear_enable:
            return
        # Получаем параметры из HUD для каждого слоя
        for i, layer in enumerate(self.layers):
            if hasattr(self, 'hud') and self.hud and i < len(self.hud.layer_modules):
                controls = self.hud.layer_modules[i]['controls']
                soft_kill = controls.get('soft_kill').current_val if 'soft_kill' in controls else 80
                fade_floor = controls.get('fade_floor').current_val if 'fade_floor' in controls else 0.6
                age_bias = controls.get('age_bias').current_val if 'age_bias' in controls else 15
            else:
                soft_kill, fade_floor, age_bias = 80, 0.6, 15

            if self.soft_mode == "Удалять клетки":
                g = layer.grid
                if not g.any(): continue
                alive = np.argwhere(g)
                k = int(len(alive) * soft_kill / 100.0)
                if k > 0:
                    if self.old_cells_priority:
                        alive_positions = np.where(g)
                        ages = layer.age[alive_positions]
                        sorted_indices = np.argsort(ages)[::-1]
                        remove_indices = sorted_indices[:k]
                        remove_r = alive_positions[0][remove_indices]
                        remove_c = alive_positions[1][remove_indices]
                        g[remove_r, remove_c] = False
                    else:
                        pick = alive[np.random.choice(len(alive), size=k, replace=False)]
                        g[pick[:, 0], pick[:, 1]] = False
            elif self.soft_mode == "Затухание клеток":
                self.global_v_mul = max(fade_floor,
                                        self.global_v_mul * (1.0 - self.soft_fade_down / 100.0))
            elif self.soft_mode == "Затухание + удаление":
                self.global_v_mul = max(fade_floor,
                                        self.global_v_mul * (1.0 - self.soft_fade_down / 100.0))
                fade_kill_rate = soft_kill * 0.5
                g = layer.grid
                if not g.any(): continue
                alive = np.argwhere(g)
                k = int(len(alive) * fade_kill_rate / 100.0)
                if k > 0:
                    if self.old_cells_priority:
                        alive_positions = np.where(g)
                        ages = layer.age[alive_positions]
                        sorted_indices = np.argsort(ages)[::-1]
                        remove_indices = sorted_indices[:k]
                        remove_r = alive_positions[0][remove_indices]
                        remove_c = alive_positions[1][remove_indices]
                        g[remove_r, remove_c] = False
                    else:
                        pick = alive[np.random.choice(len(alive), size=k, replace=False)]
                        g[pick[:, 0], pick[:, 1]] = False
                        
    def soft_population_control(self):
        """Оптимизированная универсальная мягкая система контроля популяции для всех правил"""
        if not self.soft_clear_enable:
            return
        total_grid_size = GRID_H * GRID_W
        debug_info = []
        for i, layer in enumerate(self.layers):
            if hasattr(self, 'hud') and self.hud and i < len(self.hud.layer_modules):
                controls = self.hud.layer_modules[i]['controls']
                soft_kill = controls.get('soft_kill').current_val if 'soft_kill' in controls else 80
                fade_floor = controls.get('fade_floor').current_val if 'fade_floor' in controls else 0.6
                age_bias = controls.get('age_bias').current_val if 'age_bias' in controls else 15
                max_cells_percent = controls.get('max_cells').current_val if 'max_cells' in controls else 27
                clear_threshold = controls.get('clear_at').current_val if 'clear_at' in controls else 58
            else:
                soft_kill, fade_floor, age_bias, max_cells_percent, clear_threshold = 80, 0.6, 15, 27, 58

            total_cells = np.sum(layer.grid)
            max_allowed_cells = int(total_grid_size * max_cells_percent / 100.0)
            clear_threshold_cells = int(total_grid_size * clear_threshold / 100.0)

            if total_cells <= clear_threshold_cells:
                continue

            if total_cells > max_allowed_cells:
                excess_ratio = (total_cells - max_allowed_cells) / max_allowed_cells
                base_removal = int(total_cells * soft_kill / 100.0)
                removal_rate = max(10, int(base_removal * (1.0 + excess_ratio)))
                debug_info.append(f"Layer {i}: {total_cells} cells > {max_allowed_cells} max → aggressive removal {removal_rate}")
            else:
                threshold_ratio = (total_cells - clear_threshold_cells) / (max_allowed_cells - clear_threshold_cells)
                base_removal = int(total_cells * soft_kill / 100.0)
                removal_rate = max(5, int(base_removal * threshold_ratio * 0.3))
                debug_info.append(f"Layer {i}: {total_cells} cells > {clear_threshold_cells} threshold → soft removal {removal_rate}")

            removal_rate = min(removal_rate, total_cells)

            alive_mask = layer.grid
            if not np.any(alive_mask):
                continue

            alive_r, alive_c = np.where(alive_mask)
            ages = layer.age[alive_r, alive_c]

            if self.old_cells_priority and age_bias > np.random.randint(0, 100):
                sorted_indices = np.argsort(-ages)
            else:
                sorted_indices = np.random.permutation(len(ages))

            num_to_remove = min(removal_rate, len(alive_r))
            if num_to_remove <= 0:
                continue

            remove_indices = sorted_indices[:num_to_remove]
            remove_r = alive_r[remove_indices]
            remove_c = alive_c[remove_indices]

            if self.soft_mode == "Удалять клетки":
                layer.grid[remove_r, remove_c] = False
                layer.age[remove_r, remove_c] = 0
                debug_info[-1] += f" → removed {num_to_remove} cells instantly"
            elif self.soft_mode == "Затухание клеток":
                layer.age[remove_r, remove_c] = np.maximum(0, layer.age[remove_r, remove_c] - 10)
                zero_age_mask = layer.age == 0
                layer.grid[zero_age_mask] = False
                debug_info[-1] += f" → aged {num_to_remove} cells"
            elif self.soft_mode == "Затухание + удаление":
                half_point = num_to_remove // 2

                if half_point > 0:
                    layer.grid[remove_r[:half_point], remove_c[:half_point]] = False
                    layer.age[remove_r[:half_point], remove_c[:half_point]] = 0

                if num_to_remove > half_point:
                    fade_r = remove_r[half_point:]
                    fade_c = remove_c[half_point:]
                    layer.age[fade_r, fade_c] = np.maximum(0, layer.age[fade_r, fade_c] - 10)
                    zero_age_mask = layer.age == 0
                    layer.grid[zero_age_mask] = False

        if debug_info:
            self.debug_counter = getattr(self, 'debug_counter', 0) + 1
            if self.debug_counter % 60 == 0:
                for info in debug_info:
                    print(f" Population control: {info}")
            elif not hasattr(self, 'debug_counter'):
                self.debug_counter = 1
                for info in debug_info:
                    print(f" Population control: {info}")

    def soft_recover(self):
        self.global_v_mul = min(1.0, self.global_v_mul * (1.0 + self.soft_fade_up / 100.0))

    def update_layers(self, births: int):
        """Оптимизированное обновление слоев с векторизованными операциями"""
        # Векторизованное распределение рождений по слоям с учетом процентных настроек
        if births > 0 and self.layers:
            # Максимальное количество клеток от RMS = SPAWN_BASE + (SPAWN_SCALE * 3)
            max_births = SPAWN_BASE + (SPAWN_SCALE * 3)
            births = min(births, max_births)
            # Для каждого слоя применяем его индивидуальный процент
            if hasattr(self, 'hud') and self.hud and hasattr(self.hud, 'layer_modules'):
                for i, layer in enumerate(self.layers):
                    if i < len(self.hud.layer_modules):
                        module = self.hud.layer_modules[i]
                        if 'controls' in module and 'spawn_percent' in module['controls']:
                            layer_percent = module['controls']['spawn_percent'].current_val
                        else:
                            layer_percent = 100
                    else:
                        layer_percent = 100  # Default to 100% if not found
                    # Рассчитываем количество клеток для этого слоя на основе процента
                    layer_births = int(births * (layer_percent / 100.0))
                    if layer_births > 0:
                        print(f"🌱 DEBUG: Spawning {layer_births} cells using method '{layer.spawn_method}' for layer {i}")
                        spawn_cells(layer.grid, layer_births, layer.spawn_method)

        # Векторизованное обновление всех слоев
        age_increment = int(self.aging_speed)
        fractional_part = self.aging_speed - age_increment
        
        # Предвычисляем случайное число для дробного старения
        if fractional_part > 0:
            random_increment = np.random.random() < fractional_part
        else:
            random_increment = False
        
        for i, layer in enumerate(self.layers):
            try:
                # Векторизованное увеличение возраста
                if fractional_part > 0:
                    effective_increment = age_increment + (1 if random_increment else 0)
                else:
                    effective_increment = age_increment
                
                # Векторизованное обновление возраста только для живых клеток
                alive_mask = layer.grid
                layer.age[alive_mask] += effective_increment
                layer.age[~alive_mask] = 0
                
                # Обновление правил CA
                layer.grid = step_life(layer.grid, layer.rule)
                
                # SAFETY: Векторизованная проверка и восстановление формы сетки
                if layer.grid.shape != (GRID_H, GRID_W):
                    # print(f" CRITICAL: Layer {i} grid shape corrupted: {layer.grid.shape} != ({GRID_H}, {GRID_W})")
                    # print(f"   Recreating grid with correct shape...")
                    new_grid = np.zeros((GRID_H, GRID_W), dtype=bool)
                    if layer.grid.size > 0:
                        copy_h = min(layer.grid.shape[0], GRID_H)
                        copy_w = min(layer.grid.shape[1], GRID_W)
                        new_grid[:copy_h, :copy_w] = layer.grid[:copy_h, :copy_w]
                    layer.grid = new_grid
                
                # SAFETY: Векторизованная проверка формы массива возраста
                if layer.age.shape != layer.grid.shape:
                    # print(f" CRITICAL: Layer {i} age shape mismatch: {layer.age.shape} != {layer.grid.shape}")
                    layer.age = np.zeros_like(layer.grid, dtype=np.int32)
                
                # Векторизованная очистка краев для предотвращения визуального "выползания"
                layer.grid[[0, -1], :] = False  # Верхний и нижний края одновременно
                layer.grid[:, [0, -1]] = False  # Левый и правый края одновременно
                
                # Убираем debug проверки координат для улучшения производительности
                # if np.any(layer.grid):
                #     live_coords = np.where(layer.grid)
                #     max_r, max_c = np.max(live_coords[0]), np.max(live_coords[1])
                #     min_r, min_c = np.min(live_coords[0]), np.min(live_coords[1])
                #     
                #     if max_r >= GRID_H or max_c >= GRID_W or min_r < 0 or min_c < 0:
                #         print(f"WARNING: Layer {i} has cells at invalid coords: r=[{min_r}, {max_r}], c=[{min_c}, {max_c}]")
                #     
                #     if max_r >= GRID_H-1 or max_c >= GRID_W-1 or min_r <= 0 or min_c <= 0:
                #         print(f"EDGE CHECK: Layer {i} has cells near edges: r=[{min_r}, {max_r}], c=[{min_c}, {max_c}]")
                
                # Векторизованное зеркалирование
                if self.mirror_x:
                    layer.grid = np.fliplr(layer.grid)
                if self.mirror_y:
                    layer.grid = np.flipud(layer.grid)
                
                # Удаляем клетки, которые достигли максимального возраста для этого слоя
                old_cells_mask = layer.age >= layer.max_age
                layer.grid[old_cells_mask] = False
                layer.age[old_cells_mask] = 0
                    
            except Exception as e:
                print(f"   ERROR updating layer {i}: {e}")
                print(f"   Layer rule: {getattr(layer, 'rule', 'Unknown')}")
                print(f"   Grid shape: {getattr(layer.grid, 'shape', 'Unknown') if hasattr(layer, 'grid') else 'No grid'}")
                
                # Emergency fallback - recreate layer
                try:
                    layer.grid = np.zeros((GRID_H, GRID_W), dtype=bool)
                    layer.age = np.zeros((GRID_H, GRID_W), dtype=np.int32)
                    print(f"   Emergency recovery: Layer {i} reset")
                except Exception as recovery_error:
                    print(f"    Recovery failed: {recovery_error}")
        
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
        solos = [layer for layer in self.layers if layer.solo and not layer.mute]
        layers = solos if solos else [layer for layer in self.layers if not layer.mute]

        # Убираем излишний debug вывод для улучшения производительности
        # print(f"RENDER DEBUG: Total layers={len(self.layers)}")
        # for idx, layer in enumerate(self.layers):
        #     print(f"  Layer {idx}: solo={layer.solo}, mute={layer.mute}, rule={layer.rule}, cells={np.sum(layer.grid)}")
        # print(f"RENDER DEBUG: Solos found={len(solos)}, Will render={len(layers)} layers")
        
        # Отрисовываем каждый слой
        for i, layer in enumerate(layers):
            live_cells = np.sum(layer.grid)
            print(f"RENDER DEBUG: Layer {i} ({layer.rule}): {live_cells} live cells, solo={layer.solo}, mute={layer.mute}")
            try:
                img = build_color_image(layer.grid, layer.age, "Возраст + RMS", rms, pitch, cfg,
                                        layer.age_palette, layer.rms_palette, layer.rms_mode, 
                                        layer.blend_mode, layer.rms_enabled, layer.max_age, layer.palette_mix)
                # --- Передаем маски возраста и живых клеток для alpha_old ---
                self.renderer.last_age_mask = layer.age.copy()
                self.renderer.last_grid_mask = layer.grid.copy()
                self.renderer.last_max_age = layer.max_age
                self.renderer.blit_layer(img, getattr(layer, "blend_mode", getattr(layer, "mix", "normal")), layer.alpha_live, layer.alpha_old)
            except Exception as e:
                print(f"RENDER ERROR in layer {i}: {e}")
                print(f"  Layer info: rule={layer.rule}, color_mode={layer.color_mode}")
                print(f"  Palettes: age={layer.age_palette}, rms={layer.rms_palette}")
                print(f"  RMS mode: {layer.rms_mode}, blend: {layer.blend_mode}, rms_enabled: {layer.rms_enabled}")
                print(f"  Grid shape: {layer.grid.shape}, Age shape: {layer.age.shape}")
                print(f"  RMS: {rms}, Pitch: {pitch}")
                import traceback
                traceback.print_exc()
                continue
                
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

    # -------------------- Методы LayerGenerator --------------------
    
    def generate_multiple_layers_from_configs(self, layer_configs: List[LayerConfig]) -> None:
        """Генерирует несколько слоев из списка конфигураций и заменяет текущие слои"""
        
        # Очищаем текущие слои
        self.layers.clear()
        
        # Генерируем новые слои
        new_layers = self.layer_generator.generate_multiple_layers(layer_configs)
        self.layers.extend(new_layers)
        
        # Обновляем HUD
        self.hud.update_from_app(self)
        
    
    def generate_preset_layers(self, count: int, preset_type: str = "balanced") -> None:
        """Генерирует слои используя предустановленные конфигурации"""
        
        configs = self.layer_generator.create_preset_configs(count, preset_type)
        self.generate_multiple_layers_from_configs(configs)
    
    def generate_random_layers(self, count: int) -> None:
        """Генерирует случайные слои"""
        
        configs = [self.layer_generator.create_random_layer_config() for _ in range(count)]
        self.generate_multiple_layers_from_configs(configs)
    
    def add_layer_from_config(self, config: LayerConfig) -> None:
        """Добавляет один слой из конфигурации к существующим"""
        
        new_layer = self.layer_generator.create_layer_from_config(config)
        self.layers.append(new_layer)
        
        # Обновляем HUD
        self.hud.update_from_app(self)
        
    def update_layer_transparency(self, layer_index: int, alpha_live: int, alpha_old: int) -> None:
        """Обновляет прозрачность конкретного слоя"""
        if 0 <= layer_index < len(self.layers):
            self.layer_generator.update_layer_transparency(self.layers[layer_index], alpha_live, alpha_old)
            
            # Обновляем HUD если этот слой выбран
            if layer_index == self.selected_layer_index:
                self.hud.update_from_app(self)
        
    
    def update_all_layers_transparency(self, alpha_live: int, alpha_old: int) -> None:
        """Обновляет прозрачность всех слоев"""
        
        for i, layer in enumerate(self.layers):
            self.layer_generator.update_layer_transparency(layer, alpha_live, alpha_old)
        
        # Обновляем HUD
        self.hud.update_from_app(self)
    
    def create_layer_config_from_current(self, layer_index: int) -> Optional[LayerConfig]:
        """Создает LayerConfig из текущего слоя для копирования настроек"""
        if 0 <= layer_index < len(self.layers):
            layer = self.layers[layer_index]
            
            return LayerConfig(
                rule=layer.rule,
                age_palette=layer.age_palette,
                rms_palette=layer.rms_palette,
                color_mode=layer.color_mode,
                rms_mode=layer.rms_mode,
                blend_mode=layer.blend_mode,
                rms_enabled=layer.rms_enabled,
                alpha_live=layer.alpha_live,
                alpha_old=layer.alpha_old,
                mix=layer.mix,
                solo=layer.solo,
                mute=layer.mute,
                spawn_method="Стабильные блоки",  # По умолчанию
                spawn_percent=30  # По умолчанию 30%
            )
        
        return None
    
    def duplicate_layer(self, layer_index: int, modify_params: bool = True) -> None:
        """Дублирует слой с возможностью модификации параметров"""
        config = self.create_layer_config_from_current(layer_index)
        if config:
            if modify_params:
                # Немного изменяем параметры для разнообразия
                config.alpha_live = max(150, config.alpha_live - 30)
                config.alpha_old = max(90, config.alpha_old - 10)
                config.spawn_percent += 10

                # Можно изменить палитру для визуального отличия
                if config.rms_palette in self.layer_generator.available_rms_palettes:
                    current_index = self.layer_generator.available_rms_palettes.index(config.rms_palette)
                    new_index = (current_index + 1) % len(self.layer_generator.available_rms_palettes)
                    config.rms_palette = self.layer_generator.available_rms_palettes[new_index]
            
    def create_test_pattern(self):
        """Создает тестовый паттерн для проверки работы системы"""
        # Очищаем все слои
        self.clear_all_layers()
        
        # Создаем разные паттерны для каждого слоя
        patterns = [
            # Блоки 2x2 (стабильный паттерн)
            [(10, 10), (10, 11), (11, 10), (11, 11)],
            # Горизонтальная линия (осциллятор)
            [(20, 20), (20, 21), (20, 22)],
            # Диагональная линия
            [(30, 30), (31, 31), (32, 32), (33, 33)],
            # Плюс
            [(40, 40), (39, 40), (41, 40), (40, 39), (40, 41)],
            # Случайные точки
            [(15, 25), (25, 35), (35, 15), (45, 25), (25, 45)]
        ]
        
        for i, layer in enumerate(self.layers):
            if i < len(patterns):
                pattern = patterns[i]
                for r, c in pattern:
                    if 0 <= r < GRID_H and 0 <= c < GRID_W:
                        layer.grid[r, c] = True
                        layer.age[r, c] = 1
    def clear_all_layers(self):
        """Очищает все слои"""
        for layer in self.layers:
            layer.grid.fill(False)
            layer.age.fill(0)

    def show_help(self):
        """Показывает справку по горячим клавишам"""
        help_text = """
         ОСНОВНОЕ УПРАВЛЕНИЕ:
          ESC          - Выход из приложения
          SPACE        - Пауза/Продолжение симуляции
          TAB          - Показать/скрыть HUD (панель управления)
          H            - Эта справка

         УПРАВЛЕНИЕ СЛОЯМИ:
          C            - Очистить все слои
          R            - Рандомизировать слои (создать новые паттерны)
          T            - Создать тестовый паттерн
          1-5          - Генерация 1-5 случайных слоев
          F4-F6        - Генерация пресетных конфигураций
          Ctrl+D       - Дублирование текущего слоя
          +/-          - Добавление нового слоя

         АУДИО И ЭФФЕКТЫ:
          F1           - Переключить эффект следов (trails)
          F2           - Переключить эффект размытия (blur)
          F3           - Применить Joy Division эффект
          F12          - Открыть окно настроек

         МЫШЬ:
          Клик в области сетки - Рисование/стирание клеток
          Перетаскивание       - Рисование множественных клеток

        """
        print(help_text)

    def apply_different_layer_settings(self):
        """Применяет различные настройки из app_config.json к слоям"""
        try:
            # Используем современную систему загрузки ресурсов
            if resource_manager:
                config = load_app_config()
            else:
                # Fallback к старому методу
                with open('app_config.json', 'r', encoding='utf-8') as f:
                    config = json.load(f)
            
            layer_settings = config.get('layers', {}).get('layer_settings', [])
            
            for i, layer in enumerate(self.layers):
                if i < len(layer_settings):
                    settings = layer_settings[i]
                    
                    # Применяем настройки к слою
                    layer.rule = settings.get('rule', layer.rule)
                    layer.age_palette = settings.get('age_palette', layer.age_palette)
                    layer.rms_palette = settings.get('rms_palette', layer.rms_palette)
                    layer.color_mode = settings.get('color_mode', layer.color_mode)
                    layer.rms_mode = settings.get('rms_mode', layer.rms_mode)
                    layer.alpha_live = int(settings.get('alpha_live', layer.alpha_live))
                    layer.alpha_old = int(settings.get('alpha_old', layer.alpha_old))
                    layer.max_age = int(settings.get('max_age', getattr(layer, 'max_age', 60)))
                    layer.mix = settings.get('mix', layer.mix)
                    layer.solo = bool(settings.get('solo', layer.solo))
                    layer.mute = bool(settings.get('mute', layer.mute))
                    layer.palette_mix = float(settings.get('palette_mix', getattr(layer, 'palette_mix', 0.5)))
                    layer.blend_mode = settings.get('blend_mode', getattr(layer, 'blend_mode', 'normal'))
                    layer.spawn_method = settings.get('spawn_method', getattr(layer, 'spawn_method', 'Стабильные блоки'))
                    
        except FileNotFoundError:
            print("app_config.json not found, using default layer settings")


    def save_layer_settings(self):
        """Сохраняет настройки слоев в конфиг"""
        try:
            layer_settings = []
            for layer in self.layers:
                settings = {
                    'rule': layer.rule,
                    'age_palette': layer.age_palette,
                    'rms_palette': layer.rms_palette,
                    'color_mode': layer.color_mode,
                    'rms_mode': layer.rms_mode,
                    'alpha_live': layer.alpha_live,
                    'alpha_old': layer.alpha_old,
                    'max_age': getattr(layer, 'max_age', 60),
                    'mix': layer.mix,
                    'solo': layer.solo,
                    'mute': layer.mute,
                    'palette_mix': getattr(layer, 'palette_mix', 0.5),
                    'blend_mode': getattr(layer, 'blend_mode', 'normal'),
                    'spawn_method': getattr(layer, 'spawn_method', 'Стабильные блоки')
                }
                layer_settings.append(settings)
            
            config = {'layers': {'layer_settings': layer_settings}}
            
            if resource_manager:
                success = save_app_config(config)
                if success:
                    print("Layer settings saved successfully")
                else:
                    print("Failed to save layer settings")
            else:
                with open('app_config.json', 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                    
        except Exception as e:
            print(f"Error saving layer settings: {e}")

        for i, layer in enumerate(self.layers):
            if getattr(layer, 'mute', False):
                continue  # Полностью пропускаем слой, если он замьючен

    def run(self):          
        global audio_gain
        rms = 0.0; pitch = 0.0
        running = True
        
        # Initialize global audio gain for audio callback
        audio_gain = self.gain
        
        # Инициализация HUD с текущими значениями
        print("DEBUG: Initializing HUD from app state...")
        
        # Применяем настройки из app_config.json если включен режим разных слоев
        if getattr(self, 'layers_different', True):
            self.apply_different_layer_settings()
        
        self.hud.update_from_app(self)
    
        # Проверяем, что параметры слоев установлены правильно
        for i, layer in enumerate(self.layers):
            pass
        
        while running:
            frame_start = time.time()
            
            # Время обработки событий
            event_start = time.time()
            for ev in pygame.event.get():
                # Оптимизация: обрабатываем события HUD только если он видим
                if self.hud.visible and self.hud.handle_event(ev):
                    continue  # Если HUD обработал событие, пропускаем дальнейшую обработку
                if ev.type == pygame.QUIT:
                    running = False
                elif ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_ESCAPE:
                        running = False
                    elif ev.key == pygame.K_h:
                        self.hud.visible = not self.hud.visible
                        # Инвалидируем кэш HUD при изменении видимости
                        self.hud_cache_valid = False
                    elif ev.key == pygame.K_s and (ev.mod & pygame.KMOD_CTRL):
                        if self.settings_window and SETTINGS_WINDOW_AVAILABLE:
                            self.settings_window.start()
                    elif ev.key == pygame.K_TAB:
                        self.hud.visible = not self.hud.visible
                        print(f"HUD {'скрыт' if not self.hud.visible else 'показан'}")
                    elif ev.key == pygame.K_r:
                        self.generate_random_layers(3)
                    elif ev.key == pygame.K_c:
                        self.clear_all_layers()
                    elif ev.key == pygame.K_t:
                        self.create_test_pattern()
                    elif ev.key == pygame.K_F3:
                        self.apply_joy_division()
                        self.hud.update_from_app(self)  # Обновляем HUD после изменений
                        self.hud_cache_valid = False  # Инвалидируем кэш
                    elif ev.key == pygame.K_F1:
                        self.fx['trails'] = not self.fx.get('trails', True)
                        self.hud.update_from_app(self)  # Обновляем HUD после изменений
                        self.hud_cache_valid = False  # Инвалидируем кэш
                    elif ev.key == pygame.K_F2:
                        self.fx['blur'] = not self.fx.get('blur', False)
                        self.hud.update_from_app(self)  # Обновляем HUD после изменений
                        self.hud_cache_valid = False  # Инвалидируем кэш
                    elif ev.key == pygame.K_h:
                        self.show_help()
                    # Добавить pass для пустых if/elif
                    else:
                        pass
                elif ev.type == pygame.KEYUP:
                    pass
            
            event_time = time.time() - event_start

            audio_start = time.time()
            try:
                while True:
                    pitch = pitch_queue.get_nowait()
                    rms   = rms_queue.get_nowait()
            except queue.Empty:
                pass
            except Exception:
                pass
            audio_time = time.time() - audio_start

            # Обработка изменений из окна настроек
            if self.settings_window and SETTINGS_WINDOW_AVAILABLE:
                changes = self.settings_window.get_pending_changes()
                for param_name, value in changes:
                    try:
                        # Применяем изменение через существующий обработчик
                        self.on_hud_parameter_change(param_name, value)
                    except Exception:
                        pass
            # тик автомата
            simulation_start = time.time()
            now = pygame.time.get_ticks()
            dyn_ms = self.maybe_tick_interval(pitch)
            if now - self.last_tick >= dyn_ms:
                self.last_tick = now
                births = int(SPAWN_BASE + SPAWN_SCALE *
                             clamp01(math.log10(1.0 + VOLUME_SCALE * max(0.0, rms))))
                
                # Убираем debug вывод для улучшения производительности
                # if births > 0 and rms > 0.001:
                #     print(f"DEBUG: RMS={rms:.4f}, births={births}")

                if rms <= self.sel.get('clear_rms', DEFAULT_CLEAR_RMS):
                    self.soft_clear()
                else:
                    self.soft_recover()
                self.update_layers(births)
                
                # Убираем подсчет живых клеток на каждом тике для производительности
                # total_alive = sum(np.sum(layer.grid) for layer in self.layers)
                # if total_alive > 0:
                #     print(f"DEBUG: {total_alive} cells alive after tick")
            simulation_time = time.time() - simulation_start

            # рендер
            render_start = time.time()
            self.render(rms, pitch)
            render_time = time.time() - render_start

            # HUD: оптимизированная подготовка информации
            current_time = time.time()
            
            # Инициализируем таймеры для оптимизации info
            if not hasattr(self, '_info_last_update'):
                self._info_last_update = 0
                self._info_update_interval = 1.0 / 10.0  # Обновляем некоторые данные только 10 раз в секунду
                self._cached_info = {}
            
            # Данные, которые обновляются каждый кадр (быстрые)
            fast_info = {
                "RMS": f"{rms:.4f}",
                "Pitch": f"{pitch:.1f} Hz" if pitch > 0 else "—",
                "Tick": f"{dyn_ms} ms",
            }
            
            # Данные, которые обновляются реже (медленные расчеты)
            if current_time - self._info_last_update >= self._info_update_interval:
                total_alive = sum(np.sum(layer.grid) for layer in self.layers)
                
                # Создаем информацию о альфа-значениях слоев
                alpha_info = []
                for i, layer in enumerate(self.layers):
                    alpha_info.append(f"layer{i}: {layer.alpha_live}/{layer.alpha_old}")
                
                self._cached_info.update({
                    "Alive": f"{total_alive} cells",
                    "Layers": f"{len(self.layers)}",
                    "Max Age": f"{self.max_age}",
                    "Aging Speed": f"{self.aging_speed:.1f}x",
                    "Alpha Values": " | ".join(alpha_info) if alpha_info else "none",
                    "FX": ", ".join([k for k in ['trails','blur','bloom','posterize','dither','scanlines','pixelate','outline']
                                     if self.fx.get(k, False)]) or "none",
                })
                self._info_last_update = current_time
            
            # Объединяем быстрые и кэшированные данные
            info = {**fast_info, **self._cached_info}
            
            # ЭКСПЕРИМЕНТАЛЬНОЕ отключение HUD для тестирования производительности
            # Раскомментируйте следующую строку чтобы полностью отключить HUD
            # self.hud.visible = False
            
            # Простой текстовый HUD вместо сложного GUI
            # Можно переключать: True = простой быстрый HUD, False = полнофункциональный медленный HUD
            use_simple_hud = getattr(self.hud, "mini_held", False)
            
            # HUD отрисовка с профилированием
            hud_start = time.time()
            if self.hud.visible and not use_simple_hud:
                current_time = time.time()
                if not hasattr(self, '_hud_last_update'):
                    self._hud_last_update = 0
                    self._hud_update_interval = 1.0 / 10.0  # Очень низкая частота для HUD
                
                # Обновляем HUD только если прошло достаточно времени
                if current_time - self._hud_last_update >= self._hud_update_interval:
                    self.hud.draw(self.screen, info)
                    self._hud_last_update = current_time
            elif use_simple_hud:
                # Простой текстовый HUD - намного быстрее
                y_offset = 10
                for key, value in info.items():
                    text = self.font.render(f"{key}: {value}", True, (255, 255, 255))
                    self.screen.blit(text, (self.W + 10, y_offset))
                    y_offset += 25
            hud_time = time.time() - hud_start

            # Отображение с профилированием  
            display_start = time.time()
            pygame.display.flip()
            display_time = time.time() - display_start
            
            # Ограничение FPS
            clock_start = time.time()
            self.clock.tick(FPS)
            clock_time = time.time() - clock_start
            
            # Общее время кадра
            frame_time = time.time() - frame_start
            
            # Выводим профилирование каждые 60 кадров (примерно раз в секунду)
            if not hasattr(self, '_profile_counter'):
                self._profile_counter = 0
                self._profile_counter += 1
            
            if self._profile_counter % 60 == 0:
                print(f" PROFILE: Frame={frame_time*1000:.1f}ms, Events={event_time*1000:.1f}ms, "
                      f"Audio={audio_time*1000:.1f}ms, Sim={simulation_time*1000:.1f}ms, "
                      f"Render={render_time*1000:.1f}ms, HUD={hud_time*1000:.1f}ms, "
                      f"Display={display_time*1000:.1f}ms, Clock={clock_time*1000:.1f}ms")
                      
        pygame.quit()


# -------------------- Запуск ---------------

def main():
    sel = choose_settings()
    if not sel:
        return  
    stream = start_audio_stream(sel['device'])
    try:
        app = App(sel)
        
        # for i, layer in enumerate(app.layers):
        #     cells = np.sum(layer.grid)
        # app.create_test_pattern()
            # continue
        for i, layer in enumerate(app.layers):
            cells = np.sum(layer.grid)
        app.run()
    finally:
        try:
            stream.stop(); stream.close()
        except Exception:
            pass

if __name__ == "__main__":
    main()
