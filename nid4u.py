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
                
                # Размещаем текст НАД слайдером с достаточным отступом
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
    
    @current_value.setter
    def current_value(self, value):
        """Устанавливает текущее значение по названию опции"""
        if value in self.options:
            self.current_index = self.options.index(value)
        else:
            # Если значение не найдено, попробуем найти похожее
            for i, option in enumerate(self.options):
                if option.lower() == value.lower():
                    self.current_index = i
                    return
            # Если ничего не найдено, оставляем как есть
            print(f"Warning: Option '{value}' not found in combobox")
    
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



# === HUD CLASS ===

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
        # Доступные палитры (используем новую группировку)
        palette_options = PALETTE_OPTIONS  # Используем глобальный список с новой сортировкой
        
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
            rms_mode_options = ["Brightness", "Palette", "Disabled"]
            self.comboboxes[f'layer_{layer_idx}_rms_mode'] = UIComboBox(
                x_pos, layer_y, 200, combo_height,
                f"RMS Mode {layer_idx+1}", rms_mode_options, 0  # Brightness по умолчанию
            )
            
            # Добавляем режим блендинга палитр
            x_pos += 210
            blend_mode_options = ["Normal", "Additive", "Screen", "Multiply", "Overlay"]
            self.comboboxes[f'layer_{layer_idx}_blend_mode'] = UIComboBox(
                x_pos, layer_y, 200, combo_height,
                f"Blend Mode {layer_idx+1}", blend_mode_options, 0  # Normal по умолчанию
            )
            
            # Кнопка для включения/выключения RMS палитры
            layer_y += combo_height + 8
            x_pos = panel_x
            
            self.buttons[f'layer_{layer_idx}_rms_enabled'] = UIButton(
                x_pos, layer_y, 200, combo_height,
                f"RMS Enabled {layer_idx+1}", True, True  # Включено по умолчанию, toggleable
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
        
        self.sliders['aging_speed'] = UISlider(panel_x, y_pos, slider_width, slider_height, 0.1, 5.0, 1.0, "Aging Speed", "{:.1f}")
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
        pass  # Простая заглушка для компиляции

    def update_callbacks(self):
        """Обновляет коллбэки для всех UI элементов"""
        pass  # Простая заглушка для компиляции

    def draw(self, surface, info=None):
        """Отрисовка HUD панели"""
        if not self.visible:
            return
        
        # Панель HUD
        panel_x = GRID_W * CELL_SIZE + 5
        panel_y = 5
        panel_width = HUD_WIDTH - 10
        panel_height = GRID_H * CELL_SIZE - 10
        
        # Фон панели
        pygame.draw.rect(surface, SimpleColors.GRAY_900, 
                        (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(surface, SimpleColors.PRIMARY, 
                        (panel_x, panel_y, panel_width, panel_height), 2)
        
        # Заголовок
        title_text = "GUITAR-LIFE v13"
        title_surface = self.font.render(title_text, True, SimpleColors.PRIMARY)
        surface.blit(title_surface, (panel_x + 10, panel_y + 10))
        
        # Смещение для скролла
        scroll_y = -self.scroll_offset
        
        # Отрисовка всех UI элементов с учетом скролла
        for separator in self.separators.values():
            temp_y = separator.y
            separator.y += scroll_y
            separator.draw(surface, self.font)
            separator.y = temp_y
        
        for label in self.labels.values():
            temp_y = label.y
            label.y += scroll_y
            label.draw(surface, self.small_font)
            label.y = temp_y
        
        for slider in self.sliders.values():
            temp_y = slider.y
            slider.y += scroll_y
            slider.draw(surface, self.font)
            slider.y = temp_y
        
        for button in self.buttons.values():
            temp_y = button.y
            button.y += scroll_y
            button.draw(surface, self.font)
            button.y = temp_y
        
        for combobox in self.comboboxes.values():
            temp_y = combobox.y
            combobox.y += scroll_y
            combobox.draw(surface, self.font)
            combobox.y = temp_y
        
        # Отрисовка полосы прокрутки
        self.draw_scrollbar(surface)
    def draw_scrollbar(self, surface):
        """Отрисовка полосы прокрутки"""
        if self.max_scroll <= 0:
            return
        
        panel_x = GRID_W * CELL_SIZE + 5
        panel_y = 5
        panel_width = HUD_WIDTH - 10
        panel_height = GRID_H * CELL_SIZE - 10
        
        # Полоса прокрутки справа
        scroll_bar_x = panel_x + panel_width - 15
        scroll_bar_y = panel_y + 40
        scroll_bar_width = 10
        scroll_bar_height = panel_height - 50
        
        # Фон полосы прокрутки
        pygame.draw.rect(surface, SimpleColors.GRAY_800, 
                        (scroll_bar_x, scroll_bar_y, scroll_bar_width, scroll_bar_height))
        
        # Вычисляем размер и позицию ползунка
        if self.max_scroll > 0:
            thumb_height = max(20, int(scroll_bar_height * (panel_height / (panel_height + self.max_scroll))))
            thumb_y = scroll_bar_y + int((self.scroll_offset / self.max_scroll) * (scroll_bar_height - thumb_height))
            
            # Ползунок
            thumb_rect = pygame.Rect(scroll_bar_x + 2, thumb_y, scroll_bar_width - 4, thumb_height)
            pygame.draw.rect(surface, SimpleColors.PRIMARY, thumb_rect, border_radius=4)
            
            # Сохраняем rect для обработки событий
            self.scroll_thumb_rect = thumb_rect.copy()

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
    "Viridis", "Inferno", "Magma", "Plasma", "Cividis", "Twilight"
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

HSV_COLOR_PALETTES = [
    # Основные HSV переходы
    "Blue->Red", "Blue->Green->Yellow->Red", "Rainbow", "RainbowSmooth", 
    # Природные дизайны
    "Sunset", "Aurora", "Ocean", "Fire", "Galaxy", "Tropical", "Volcano", "DeepSea",
    # Сезонные
    "Spring", "Summer", "Autumn", "Winter", "Ice", "Forest", "Desert",
    # Научные палитры
    "Viridis", "Inferno", "Magma", "Plasma", "Cividis", "Twilight"
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

def get_hsv_design_palettes():
    """Возвращает палитры для HSV-дизайнов (комбинированный режим)"""
    return HSV_DESIGN_PALETTES

def get_hsv_color_palettes():
    """Возвращает палитры для HSV палитр (только RMS режим)"""
    return HSV_COLOR_PALETTES

def get_palette_by_category(category: str):
    """Возвращает палитры по категории"""
    if category == "HSV-дизайны":
        return HSV_DESIGN_PALETTES
    elif category == "HSV Палитры":
        return HSV_COLOR_PALETTES
    else:
        return PALETTE_OPTIONS

# Audio processing settings
SPAWN_BASE, SPAWN_SCALE = 1, 360  # Уменьшено для меньшего количества клеток
FREQ_MIN, FREQ_MAX = 70.0, 1500.0
MIN_NOTE_FREQ = 60.0
VOLUME_SCALE = 8.0  # Уменьшено для более мягкой реакции на звук

# Default timing and threshold values
DEFAULT_CLEAR_RMS = 0.004
DEFAULT_COLOR_RMS_MIN = 0.004
DEFAULT_COLOR_RMS_MAX = 0.3
DEFAULT_TICK_MS = 10
DEFAULT_PTICK_MIN_MS = 60
DEFAULT_PTICK_MAX_MS = 200

# Clear types for different clearing methods
CLEAR_TYPES = [
    "Полная очистка",        # Complete clear - all cells
    "Частичная очистка",     # Partial clear - percentage
    "Очистка по возрасту",   # Age-based clear - old cells
    "Случайная очистка"      # Random clear - random cells
]

# ==================== CORE CLASSES ====================

@dataclass
class Layer:
    """Слой клеточного автомата с настройками"""
    grid: np.ndarray
    age:  np.ndarray
    rule: str
    age_palette: str
    rms_palette: str
    color_mode: str  # "HSV-дизайны" | "HSV Палитры" | "Высота ноты (Pitch)"
    rms_mode: str = "brightness"  # "brightness" | "palette" | "disabled"
    blend_mode: str = "normal"  # "normal" | "additive" | "screen" | "multiply" | "overlay"
    rms_enabled: bool = True  # Включена ли RMS палитра
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


# ==================== UTILITY FUNCTIONS ====================

def clamp01(x: float) -> float:
    """Ограничивает значение в диапазоне [0, 1]"""
    return max(0.0, min(1.0, x))


# ==================== EFFECTS FUNCTIONS ====================

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
    """Упорядоченный дизеринг (Bayer 4x4)"""
    bayer = (1/17.0) * np.array([[0,  8,  2, 10],
                                 [12, 4, 14,  6],
                                 [3, 11,  1,  9],
                                 [15, 7, 13,  5]], dtype=np.float32)
    arr = pygame.surfarray.pixels3d(surface).astype(np.float32)
    H, W = arr.shape[1], arr.shape[0]
    tile = np.tile(bayer, (W//4 + 1, H//4 + 1))[:W, :H].T[..., None]
    arr[:] = np.clip(arr + (tile * 8.0 - 4.0), 0, 255)


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


# ==================== RENDER MANAGER ====================

class RenderManager:
    """Менеджер рендеринга слоев"""
    def __init__(self, w_cells: int, h_cells: int, cell_size: int):
        self.wc = w_cells
        self.hc = h_cells  
        self.cs = cell_size
        self.canvas = pygame.Surface((w_cells * cell_size, h_cells * cell_size)).convert()

    def clear(self, color=BG_COLOR):
        """Очищает канвас указанным цветом"""
        self.canvas.fill(color)

    def blit_layer(self, color_img: np.ndarray, mix: str, alpha_live: int = 255, alpha_old: int = 255):
        """Отрисовывает слой на канвас
        color_img: (H,W,3) uint8 в координатах клеток
        """
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
                self.canvas.blit(rgb_surf, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
            else:
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
                
                # Создаем альфа-маску с учетом прозрачности слояф
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
                    self.canvas.blit(final_surf_alpha, (0, 0), special_flags=pygame.BLEND_ADD)
                
            except Exception as e2:
                print(f"ERROR in fallback blit_layer: {e2}")
                
                # Простейший fallback
                surf = pygame.surfarray.make_surface(np.transpose(color_img, (1, 0, 2)))
                surf = pygame.transform.scale(surf, self.canvas.get_size())
                surf.set_colorkey((0, 0, 0))
                surf.set_alpha(alpha_live)
                if mix == "Additive":
                    self.canvas.blit(surf, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
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
                
                # Размещаем текст НАД слайдером с достаточным отступом
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
    
    @current_value.setter
    def current_value(self, value):
        """Устанавливает текущее значение по названию опции"""
        if value in self.options:
            self.current_index = self.options.index(value)
        else:
            # Если значение не найдено, попробуем найти похожее
            for i, option in enumerate(self.options):
                if option.lower() == value.lower():
                    self.current_index = i
                    return
            # Если ничего не найдено, оставляем как есть
            print(f"Warning: Option '{value}' not found in combobox")
    
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
        # Синхронизируем координаты с rect
        self.x = self.rect.x
        self.y = self.rect.y
        
        try:
            label_font = pygame.font.SysFont("times new roman,georgia,serif", self.font_size)
        except:
            label_font = pygame.font.Font(None, self.font_size)
            
        # Отображаем текст
        text_surface = label_font.render(self.text, True, SimpleColors.TEXT_SECONDARY)
        surface.blit(text_surface, (self.x, self.y))

# === HUD CLASS ===

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
        # Доступные палитры (используем новую группировку)
        palette_options = PALETTE_OPTIONS  # Используем глобальный список с новой сортировкой
        
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
            rms_mode_options = ["Brightness", "Palette", "Disabled"]
            self.comboboxes[f'layer_{layer_idx}_rms_mode'] = UIComboBox(
                x_pos, layer_y, 200, combo_height,
                f"RMS Mode {layer_idx+1}", rms_mode_options, 0  # Brightness по умолчанию
            )
            
            # Добавляем режим блендинга палитр
            x_pos += 210
            blend_mode_options = ["Normal", "Additive", "Screen", "Multiply", "Overlay"]
            self.comboboxes[f'layer_{layer_idx}_blend_mode'] = UIComboBox(
                x_pos, layer_y, 200, combo_height,
                f"Blend Mode {layer_idx+1}", blend_mode_options, 0  # Normal по умолчанию
            )
            
            # Кнопка для включения/выключения RMS палитры
            layer_y += combo_height + 8
            x_pos = panel_x
            
            self.buttons[f'layer_{layer_idx}_rms_enabled'] = UIButton(
                x_pos, layer_y, 200, combo_height,
                f"RMS Enabled {layer_idx+1}", True, True  # Включено по умолчанию, toggleable
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
        
        self.sliders['aging_speed'] = UISlider(panel_x, y_pos, slider_width, slider_height, 0.1, 5.0, 1.0, "Aging Speed", "{:.1f}")
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
        pass  # Простая заглушка для компиляции

    def update_callbacks(self):
        """Обновляет коллбэки для всех UI элементов"""
        pass  # Простая заглушка для компиляции

    def draw(self, surface, info=None):
        """Отрисовка HUD панели"""
        if not self.visible:
            return
        
        # Панель HUD
        panel_x = GRID_W * CELL_SIZE + 5
        panel_y = 5
        panel_width = HUD_WIDTH - 10
        panel_height = GRID_H * CELL_SIZE - 10
        
        # Фон панели
        pygame.draw.rect(surface, SimpleColors.GRAY_900, 
                        (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(surface, SimpleColors.PRIMARY, 
                        (panel_x, panel_y, panel_width, panel_height), 2)
        
        # Заголовок
        title_text = "GUITAR-LIFE v13"
        title_surface = self.font.render(title_text, True, SimpleColors.PRIMARY)
        surface.blit(title_surface, (panel_x + 10, panel_y + 10))
        
        # Смещение для скролла
        scroll_y = -self.scroll_offset
        
        # Отрисовка всех UI элементов с учетом скролла
        for separator in self.separators.values():
            temp_y = separator.y
            separator.y += scroll_y
            separator.draw(surface, self.font)
            separator.y = temp_y
        
        for label in self.labels.values():
            temp_y = label.y
            label.y += scroll_y
            label.draw(surface, self.small_font)
            label.y = temp_y
        
        for slider in self.sliders.values():
            temp_y = slider.y
            slider.y += scroll_y
            slider.draw(surface, self.font)
            slider.y = temp_y
        
        for button in self.buttons.values():
            temp_y = button.y
            button.y += scroll_y
            button.draw(surface, self.font)
            button.y = temp_y
        
        for combobox in self.comboboxes.values():
            temp_y = combobox.y
            combobox.y += scroll_y
            combobox.draw(surface, self.font)
            combobox.y = temp_y
        
        # Отрисовка полосы прокрутки
        self.draw_scrollbar(surface)
    def draw_scrollbar(self, surface):
        """Отрисовка полосы прокрутки"""
        if self.max_scroll <= 0:
            return
        
        panel_x = GRID_W * CELL_SIZE + 5
        panel_y = 5
        panel_width = HUD_WIDTH - 10
        panel_height = GRID_H * CELL_SIZE - 10
        
        # Полоса прокрутки справа
        scroll_bar_x = panel_x + panel_width - 15
        scroll_bar_y = panel_y + 40
        scroll_bar_width = 10
        scroll_bar_height = panel_height - 50
        
        # Фон полосы прокрутки
        pygame.draw.rect(surface, SimpleColors.GRAY_800, 
                        (scroll_bar_x, scroll_bar_y, scroll_bar_width, scroll_bar_height))
        
        # Вычисляем размер и позицию ползунка
        if self.max_scroll > 0:
            thumb_height = max(20, int(scroll_bar_height * (panel_height / (panel_height + self.max_scroll))))
            thumb_y = scroll_bar_y + int((self.scroll_offset / self.max_scroll) * (scroll_bar_height - thumb_height))
            
            # Ползунок
            thumb_rect = pygame.Rect(scroll_bar_x + 2, thumb_y, scroll_bar_width - 4, thumb_height)
            pygame.draw.rect(surface, SimpleColors.PRIMARY, thumb_rect, border_radius=4)
            
            # Сохраняем rect для обработки событий
            self.scroll_thumb_rect = thumb_rect.copy()

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
    "Viridis", "Inferno", "Magma", "Plasma", "Cividis", "Twilight"
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

HSV_COLOR_PALETTES = [
    # Основные HSV переходы
    "Blue->Red", "Blue->Green->Yellow->Red", "Rainbow", "RainbowSmooth", 
    # Природные дизайны
    "Sunset", "Aurora", "Ocean", "Fire", "Galaxy", "Tropical", "Volcano", "DeepSea",
    # Сезонные
    "Spring", "Summer", "Autumn", "Winter", "Ice", "Forest", "Desert",
    # Научные палитры
    "Viridis", "Inferno", "Magma", "Plasma", "Cividis", "Twilight"
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

def get_hsv_design_palettes():
    """Возвращает палитры для HSV-дизайнов (комбинированный режим)"""
    return HSV_DESIGN_PALETTES

def get_hsv_color_palettes():
    """Возвращает палитры для HSV палитр (только RMS режим)"""
    return HSV_COLOR_PALETTES

def get_palette_by_category(category: str):
    """Возвращает палитры по категории"""
    if category == "HSV-дизайны":
        return HSV_DESIGN_PALETTES
    elif category == "HSV Палитры":
        return HSV_COLOR_PALETTES
    else:
        return PALETTE_OPTIONS

# Audio processing settings
SPAWN_BASE, SPAWN_SCALE = 1, 360  # Уменьшено для меньшего количества клеток
FREQ_MIN, FREQ_MAX = 70.0, 1500.0
MIN_NOTE_FREQ = 60.0
VOLUME_SCALE = 8.0  # Уменьшено для более мягкой реакции на звук

# Default timing and threshold values
DEFAULT_CLEAR_RMS = 0.004
DEFAULT_COLOR_RMS_MIN = 0.004
DEFAULT_COLOR_RMS_MAX = 0.3
DEFAULT_TICK_MS = 10
DEFAULT_PTICK_MIN_MS = 60
DEFAULT_PTICK_MAX_MS = 200

# Clear types for different clearing methods
CLEAR_TYPES = [
    "Полная очистка",        # Complete clear - all cells
    "Частичная очистка",     # Partial clear - percentage
    "Очистка по возрасту",   # Age-based clear - old cells
    "Случайная очистка"      # Random clear - random cells
]

# ==================== CORE CLASSES ====================

@dataclass
class Layer:
    """Слой клеточного автомата с настройками"""
    grid: np.ndarray
    age:  np.ndarray
    rule: str
    age_palette: str
    rms_palette: str
    color_mode: str  # "HSV-дизайны" | "HSV Палитры" | "Высота ноты (Pitch)"
    rms_mode: str = "brightness"  # "brightness" | "palette" | "disabled"
    blend_mode: str = "normal"  # "normal" | "additive" | "screen" | "multiply" | "overlay"
    rms_enabled: bool = True  # Включена ли RMS палитра
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

# ==================== UTILITY FUNCTIONS ====================

def clamp01(x: float) -> float:
    """Ограничивает значение в диапазоне [0, 1]"""
    return max(0.0, min(1.0, x))


# ==================== EFFECTS FUNCTIONS ====================

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
    """Упорядоченный дизеринг (Bayer 4x4)"""
    bayer = (1/17.0) * np.array([[0,  8,  2, 10],
                                 [12, 4, 14,  6],
                                 [3, 11,  1,  9],
                                 [15, 7, 13,  5]], dtype=np.float32)
    arr = pygame.surfarray.pixels3d(surface).astype(np.float32)
    H, W = arr.shape[1], arr.shape[0]
    tile = np.tile(bayer, (W//4 + 1, H//4 + 1))[:W, :H].T[..., None]
    arr[:] = np.clip(arr + (tile * 8.0 - 4.0), 0, 255)


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


# ==================== RENDER MANAGER ====================

class RenderManager:
    """Менеджер рендеринга слоев"""
    def __init__(self, w_cells: int, h_cells: int, cell_size: int):
        self.wc = w_cells
        self.hc = h_cells  
        self.cs = cell_size
        self.canvas = pygame.Surface((w_cells * cell_size, h_cells * cell_size)).convert()

    def clear(self, color=BG_COLOR):
        """Очищает канвас указанным цветом"""
        self.canvas.fill(color)

    def blit_layer(self, color_img: np.ndarray, mix: str, alpha_live: int = 255, alpha_old: int = 255):
        """Отрисовывает слой на канвас
        color_img: (H,W,3) uint8 в координатах клеток
        """
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
                self.canvas.blit(rgb_surf, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
            else:
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
                
                # Создаем альфа-маску с учетом прозрачности слояф
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
                    self.canvas.blit(final_surf_alpha, (0, 0), special_flags=pygame.BLEND_ADD)
                
            except Exception as e2:
                print(f"ERROR in fallback blit_layer: {e2}")
                
                # Простейший fallback
                surf = pygame.surfarray.make_surface(np.transpose(color_img, (1, 0, 2)))
                surf = pygame.transform.scale(surf, self.canvas.get_size())
                surf.set_colorkey((0, 0, 0))
                surf.set_alpha(alpha_live)
                if mix == "Additive":
                    self.canvas.blit(surf, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
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
                
                # Размещаем текст НАД слайдером с достаточным отступом
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
    
    @current_value.setter
    def current_value(self, value):
        """Устанавливает текущее значение по названию опции"""
        if value in self.options:
            self.current_index = self.options.index(value)
        else:
            # Если значение не найдено, попробуем найти похожее
            for i, option in enumerate(self.options):
                if option.lower() == value.lower():
                    self.current_index = i
                    return
            # Если ничего не найдено, оставляем как есть
            print(f"Warning: Option '{value}' not found in combobox")
    
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
        # Синхронизируем координаты с rect
        self.x = self.rect.x
        self.y = self.rect.y
        
        try:
            label_font = pygame.font.SysFont("times new roman,georgia,serif", self.font_size)
        except:
            label_font = pygame.font.Font(None, self.font_size)
            
        # Отображаем текст
        text_surface = label_font.render(self.text, True, SimpleColors.TEXT_SECONDARY)
        surface.blit(text_surface, (self.x, self.y))

# === HUD CLASS ===

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
        # Доступные палитры (используем новую группировку)
        palette_options = PALETTE_OPTIONS  # Используем глобальный список с новой сортировкой
        
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
            rms_mode_options = ["Brightness", "Palette", "Disabled"]
            self.comboboxes[f'layer_{layer_idx}_rms_mode'] = UIComboBox(
                x_pos, layer_y, 200, combo_height,
                f"RMS Mode {layer_idx+1}", rms_mode_options, 0  # Brightness по умолчанию
            )
            
            # Добавляем режим блендинга палитр
            x_pos += 210
            blend_mode_options = ["Normal", "Additive", "Screen", "Multiply", "Overlay"]
            self.comboboxes[f'layer_{layer_idx}_blend_mode'] = UIComboBox(
                x_pos, layer_y, 200, combo_height,
                f"Blend Mode {layer_idx+1}", blend_mode_options, 0  # Normal по умолчанию
            )
            
            # Кнопка для включения/выключения RMS палитры
            layer_y += combo_height + 8
            x_pos = panel_x
            
            self.buttons[f'layer_{layer_idx}_rms_enabled'] = UIButton(
                x_pos, layer_y, 200, combo_height,
                f"RMS Enabled {layer_idx+1}", True, True  # Включено по умолчанию, toggleable
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
        
        self.sliders['aging_speed'] = UISlider(panel_x, y_pos, slider_width, slider_height, 0.1, 5.0, 1.0, "Aging Speed", "{:.1f}")
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
        y_pos += 35           ###################################
        
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
            print(f" Error loading config values: ")
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
        pass  # Простая заглушка для компиляции

    def update_callbacks(self):
        """Обновляет коллбэки для всех UI элементов"""
        pass  # Простая заглушка для компиляции

    def draw(self, surface, info=None):
        """Отрисовка HUD панели"""
        if not self.visible:
            return
        
        # Панель HUD
        panel_x = GRID_W * CELL_SIZE + 5
        panel_y = 5
        panel_width = HUD_WIDTH - 10
        panel_height = GRID_H * CELL_SIZE - 10
        
        # Фон панели
        pygame.draw.rect(surface, SimpleColors.GRAY_900, 
                        (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(surface, SimpleColors.PRIMARY, 
                        (panel_x, panel_y, panel_width, panel_height), 2)
        
        # Заголовок
        title_text = "GUITAR-LIFE v13"
        title_surface = self.font.render(title_text, True, SimpleColors.PRIMARY)
        surface.blit(title_surface, (panel_x + 10, panel_y + 10))
        
        # Смещение для скролла
        scroll_y = -self.scroll_offset
        
        # Отрисовка всех UI элементов с учетом скролла
        for separator in self.separators.values():
            temp_y = separator.y
            separator.y += scroll_y
            separator.draw(surface, self.font)
            separator.y = temp_y
        
        for label in self.labels.values():
            temp_y = label.y
            label.y += scroll_y
            label.draw(surface, self.small_font)
            label.y = temp_y
        
        for slider in self.sliders.values():
            temp_y = slider.y
            slider.y += scroll_y
            slider.draw(surface, self.font)
            slider.y = temp_y
        
        for button in self.buttons.values():
            temp_y = button.y
            button.y += scroll_y
            button.draw(surface, self.font)
            button.y = temp_y
        
        for combobox in self.comboboxes.values():
            temp_y = combobox.y
            combobox.y += scroll_y
            combobox.draw(surface, self.font)
            combobox.y = temp_y
        
        # Отрисовка полосы прокрутки
        self.draw_scrollbar(surface)
    def draw_scrollbar(self, surface):
        """Отрисовка полосы прокрутки"""
        if self.max_scroll <= 0:
            return
        
        panel_x = GRID_W * CELL_SIZE + 5
        panel_y = 5
        panel_width = HUD_WIDTH - 10
        panel_height = GRID_H * CELL_SIZE - 10
        
        # Полоса прокрутки справа
        scroll_bar_x = panel_x + panel_width - 15
        scroll_bar_y = panel_y + 40
        scroll_bar_width = 10
        scroll_bar_height = panel_height - 50
        
        # Фон полосы прокрутки
        pygame.draw.rect(surface, SimpleColors.GRAY_800, 
                        (scroll_bar_x, scroll_bar_y, scroll_bar_width, scroll_bar_height))
        
        # Вычисляем размер и позицию ползунка
        if self.max_scroll > 0:
            thumb_height = max(20, int(scroll_bar_height * (panel_height / (panel_height + self.max_scroll))))
            thumb_y = scroll_bar_y + int((self.scroll_offset / self.max_scroll) * (scroll_bar_height - thumb_height))
            
            # Ползунок
            thumb_rect = pygame.Rect(scroll_bar_x + 2, thumb_y, scroll_bar_width - 4, thumb_height)
            pygame.draw.rect(surface, SimpleColors.PRIMARY, thumb_rect, border_radius=4)
            
            # Сохраняем rect для обработки событий
            self.scroll_thumb_rect = thumb_rect.copy()

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
    "Viridis", "Inferno", "Magma", "Plasma", "Cividis", "Twilight"
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

HSV_COLOR_PALETTES = [
    # Основные HSV переходы
    "Blue->Red", "Blue->Green->Yellow->Red", "Rainbow", "RainbowSmooth", 
    # Природные дизайны
    "Sunset", "Aurora", "Ocean", "Fire", "Galaxy", "Tropical", "Volcano", "DeepSea",
    # Сезонные
    "Spring", "Summer", "Autumn", "Winter", "Ice", "Forest", "Desert",
    # Научные палитры
    "Viridis", "Inferno", "Magma", "Plasma", "Cividis", "Twilight"
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

def get_hsv_design_palettes():
    """Возвращает палитры для HSV-дизайнов (комбинированный режим)"""
    return HSV_DESIGN_PALETTES

def get_hsv_color_palettes():
    """Возвращает палитры для HSV палитр (только RMS режим)"""
    return HSV_COLOR_PALETTES

def get_palette_by_category(category: str):
    """Возвращает палитры по категории"""
    if category == "HSV-дизайны":
        return HSV_DESIGN_PALETTES
    elif category == "HSV Палитры":
        return HSV_COLOR_PALETTES
    else:
        return PALETTE_OPTIONS

# Audio processing settings
SPAWN_BASE, SPAWN_SCALE = 1, 360  # Уменьшено для меньшего количества клеток
FREQ_MIN, FREQ_MAX = 70.0, 1500.0
MIN_NOTE_FREQ = 60.0
VOLUME_SCALE = 8.0  # Уменьшено для более мягкой реакции на звук

# Default timing and threshold values
DEFAULT_CLEAR_RMS = 0.004
DEFAULT_COLOR_RMS_MIN = 0.004
DEFAULT_COLOR_RMS_MAX = 0.3
DEFAULT_TICK_MS = 10
DEFAULT_PTICK_MIN_MS = 60
DEFAULT_PTICK_MAX_MS = 200

# Clear types for different clearing methods
CLEAR_TYPES = [
    "Полная очистка",        # Complete clear - all cells
    "Частичная очистка",     # Partial clear - percentage
    "Очистка по возрасту",   # Age-based clear - old cells
    "Случайная очистка"      # Random clear - random cells
]

# ==================== CORE CLASSES ====================

@dataclass
class Layer:
    """Слой клеточного автомата с настройками"""
    grid: np.ndarray
    age:  np.ndarray
    rule: str
    age_palette: str
    rms_palette: str
    color_mode: str  # "HSV-дизайны" | "HSV Палитры" | "Высота ноты (Pitch)"
    rms_mode: str = "brightness"  # "brightness" | "palette" | "disabled"
    blend_mode: str = "normal"  # "normal" | "additive" | "screen" | "multiply" | "overlay"
    rms_enabled: bool = True  # Включена ли RMS палитра
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


# ==================== UTILITY FUNCTIONS ====================

def clamp01(x: float) -> float:
    """Ограничивает значение в диапазоне [0, 1]"""
    return max(0.0, min(1.0, x))


# ==================== EFFECTS FUNCTIONS ====================

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
    """Упорядоченный дизеринг (Bayer 4x4)"""
    bayer = (1/17.0) * np.array([[0,  8,  2, 10],
                                 [12, 4, 14,  6],
                                 [3, 11,  1,  9],
                                 [15, 7, 13,  5]], dtype=np.float32)
    arr = pygame.surfarray.pixels3d(surface).astype(np.float32)
    H, W = arr.shape[1], arr.shape[0]
    tile = np.tile(bayer, (W//4 + 1, H//4 + 1))[:W, :H].T[..., None]
    arr[:] = np.clip(arr + (tile * 8.0 - 4.0), 0, 255)


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


# ==================== RENDER MANAGER ====================

class RenderManager:
    """Менеджер рендеринга слоев"""
    def __init__(self, w_cells: int, h_cells: int, cell_size: int):
        self.wc = w_cells
        self.hc = h_cells  
        self.cs = cell_size
        self.canvas = pygame.Surface((w_cells * cell_size, h_cells * cell_size)).convert()

    def clear(self, color=BG_COLOR):
        """Очищает канвас указанным цветом"""
        self.canvas.fill(color)

    def blit_layer(self, color_img: np.ndarray, mix: str, alpha_live: int = 255, alpha_old: int = 255):
        """Отрисовывает слой на канвас
        color_img: (H,W,3) uint8 в координатах клеток
        """
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
                self.canvas.blit(rgb_surf, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
            else:
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
                
                # Создаем альфа-маску с учетом прозрачности слояф
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
                self.canvas.blit(final_surf_alpha, (0, 0))
            except Exception as fallback_e:
                print(f"ERROR in fallback method: {fallback_e}")
                # Последний резерв - просто рисуем без альфы
                pass

    def step_layers(self):
        """Выполняет один шаг эволюции для всех слоев"""
        for i, L in enumerate(self.layers):
            if not L.alive: continue
            
            # SAFETY: Ensure grid shape is correct before processing
            if L.grid.shape != (GRID_H, GRID_W):
                print(f"🚨 CRITICAL: Layer {i} grid shape mismatch: {L.grid.shape} != {(GRID_H, GRID_W)}")
                print(f"   Recreating grid with correct shape...")
                print(f"🚨 CRITICAL: Layer {i} age shape mismatch: {L.age.shape} != {L.grid.shape}")
                L.age = np.zeros_like(L.grid, dtype=np.int32)
            
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
        
        # Обновляем кэш живых клеток после всех изменений
        self._cache_dirty = True

    def get_total_alive_cached(self) -> int:
        """Возвращает кэшированное количество живых клеток"""
        if self._cache_dirty:
            self._cached_total_alive = sum(np.sum(L.grid) for L in self.layers)
            self._cache_dirty = False
        return self._cached_total_alive

    def _schedule_save(self):
        """Планирует отложенное сохранение для оптимизации производительности"""
        self._save_pending = True
        self._last_save_time = pygame.time.get_ticks()

    def _process_pending_save(self):
        """Обрабатывает отложенное сохранение"""
        if self._save_pending:
            current_time = pygame.time.get_ticks()
            if current_time - self._last_save_time >= self._save_delay:
                self.save_layer_settings()
                self.hud.update_from_app(self)
                self._save_pending = False

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
        
        # Отрисовываем каждый слой
        for i, L in enumerate(layers):
            
            try:
                img = build_color_image(L.grid, L.age, L.color_mode, rms, pitch, cfg,
                                        L.age_palette, L.rms_palette, L.rms_mode, 
                                        L.blend_mode, L.rms_enabled)
                self.renderer.blit_layer(img, L.mix, L.alpha_live, L.alpha_old)
            except Exception:
                # Пропускаем слой при ошибке
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
        print(f"🎨 Генерация {len(layer_configs)} слоев из конфигураций...")
        
        # Очищаем текущие слои
        self.layers.clear()
        
        # Генерируем новые слои
        new_layers = self.layer_generator.generate_multiple_layers(layer_configs)
        self.layers.extend(new_layers)
        
        # Обновляем HUD
        self.hud.update_from_app(self)
        
        print(f"✅ Успешно создано {len(self.layers)} слоев")
    
    def generate_preset_layers(self, count: int, preset_type: str = "balanced") -> None:
        """Генерирует слои используя предустановленные конфигурации"""
        print(f"🎯 Генерация {count} слоев с пресетом '{preset_type}'...")
        
        configs = self.layer_generator.create_preset_configs(count, preset_type)
        self.generate_multiple_layers_from_configs(configs)
    
    def generate_random_layers(self, count: int) -> None:
        """Генерирует случайные слои"""
        print(f"🎲 Генерация {count} случайных слоев...")
        
        configs = [self.layer_generator.create_random_layer_config() for _ in range(count)]
        self.generate_multiple_layers_from_configs(configs)
    
    def add_layer_from_config(self, config: LayerConfig) -> None:
        """Добавляет один слой из конфигурации к существующим"""
        print(f"➕ Добавление нового слоя: {config.rule} | {config.age_palette}+{config.rms_palette}")
        
        new_layer = self.layer_generator.create_layer_from_config(config)
        self.layers.append(new_layer)
        
        # Обновляем HUD
        self.hud.update_from_app(self)
        
        print(f"✅ Слой добавлен. Всего слоев: {len(self.layers)}")
    
    def update_layer_transparency(self, layer_index: int, alpha_live: int, alpha_old: int) -> None:
        """Обновляет прозрачность конкретного слоя"""
        if 0 <= layer_index < len(self.layers):
            self.layer_generator.update_layer_transparency(self.layers[layer_index], alpha_live, alpha_old)
            
            # Обновляем HUD если этот слой выбран
            if layer_index == self.selected_layer_index:
                self.hud.update_from_app(self)
        else:
            print(f"❌ Неверный индекс слоя: {layer_index}")
    
    def update_all_layers_transparency(self, alpha_live: int, alpha_old: int) -> None:
        """Обновляет прозрачность всех слоев"""
        print(f"🔧 Обновление прозрачности всех слоев: α_live={alpha_live}, α_old={alpha_old}")
        
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
                initial_cells=20  # По умолчанию
            )
        
        return None
    
    def duplicate_layer(self, layer_index: int, modify_params: bool = True) -> None:
        """Дублирует слой с возможностью модификации параметров"""
        config = self.create_layer_config_from_current(layer_index)
        if config:
            if modify_params:
                # Немного изменяем параметры для разнообразия
                config.alpha_live = max(150, config.alpha_live - 30)
                config.alpha_old = max(100, config.alpha_old - 20)
                config.initial_cells += 10
                
                # Можно изменить палитру для визуального отличия
                if config.rms_palette in self.layer_generator.available_rms_palettes:
                    current_index = self.layer_generator.available_rms_palettes.index(config.rms_palette)
                    new_index = (current_index + 1) % len(self.layer_generator.available_rms_palettes)
                    config.rms_palette = self.layer_generator.available_rms_palettes[new_index]
            
            self.add_layer_from_config(config)
            print(f"📋 Слой {layer_index} дублирован")
        else:
            print(f"❌ Не удалось дублировать слой {layer_index}")

    def apply_different_layer_settings(self):
        """Применяет различные настройки из app_config.json к слоям"""
        try:
            with open('app_config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            layer_settings = config.get('layers', {}).get('layer_settings', [])
            
            print(f"🔧 Applying different layer settings to {len(self.layers)} layers...")
            print(f"🔧 Available settings for {len(layer_settings)} layers from config")
            
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
                    layer.mix = settings.get('mix', layer.mix)
                    layer.solo = bool(settings.get('solo', layer.solo))
                    layer.mute = bool(settings.get('mute', layer.mute))
                    layer.blend_mode = settings.get('blend_mode', getattr(layer, 'blend_mode', 'normal'))
                    
                    print(f"✅ Layer {i}: {layer.rule}, {layer.age_palette}, alpha={layer.alpha_live}")
                else:
                    print(f"⚠️ No settings found for layer {i}, using defaults")
                    
        except FileNotFoundError:
            print("⚠️ app_config.json not found, using default layer settings")
        except Exception as e:
            print(f"❌ Error applying layer settings: {e}")

    def add_new_layer(self):
        """Добавляет новый слой с базовыми настройками"""
        if len(self.layers) >= 5:
            print("❌ Максимальное количество слоев (5) уже достигнуто")
            return
            
        new_layer = self.create_layer()
        self.layers.append(new_layer)
        
        # Обновляем выбранный слой
        self.selected_layer_index = len(self.layers) - 1
        
        # Обновляем HUD
        self.hud.update_from_app(self)
        
        print(f"➕ Добавлен новый слой. Всего слоев: {len(self.layers)}")

    def cycle_layer_rule(self, layer_index: int):
        """Циклично переключает правило клеточного автомата для слоя"""
        if 0 <= layer_index < len(self.layers):
            layer = self.layers[layer_index]
            current_rule = layer.rule
            
            try:
                current_idx = CA_RULES.index(current_rule)
                next_idx = (current_idx + 1) % len(CA_RULES)
                layer.rule = CA_RULES[next_idx]
                
                print(f"🔄 Layer {layer_index} rule: {current_rule} → {layer.rule}")
                
                # Обновляем HUD если это текущий слой
                if layer_index == getattr(self, 'selected_layer_index', 0):
                    self.hud.update_from_app(self)
                    
            except ValueError:
                # Если текущее правило не в списке, устанавливаем первое
                layer.rule = CA_RULES[0]
                print(f"🔄 Layer {layer_index} rule reset to: {layer.rule}")
        else:
            print(f"❌ Invalid layer index: {layer_index}")

    def clear_with_type(self):
        """Очищает слои в соответствии с настройками clear_type"""
        clear_type = getattr(self, 'clear_type', 'all')
        
        if clear_type == 'all':
            self.clear_all_layers()
        elif clear_type == 'partial':
            # Частичная очистка - удаляем случайные клетки
            percent = getattr(self, 'clear_partial_percent', 50)
            for layer in self.layers:
                alive_cells = np.argwhere(layer.grid)
                if len(alive_cells) > 0:
                    num_to_clear = int(len(alive_cells) * percent / 100)
                    indices = np.random.choice(len(alive_cells), num_to_clear, replace=False)
                    for idx in indices:
                        r, c = alive_cells[idx]
                        layer.grid[r, c] = False
                        layer.age[r, c] = 0
        elif clear_type == 'old':
            # Очистка старых клеток
            age_threshold = getattr(self, 'clear_age_threshold', 50)
            for layer in self.layers:
                old_mask = layer.age > age_threshold
                layer.grid[old_mask] = False
                layer.age[old_mask] = 0
        
        print(f"🧹 Cleared layers using type: {clear_type}")

    def reset_to_defaults(self):
        """Сбрасывает все параметры к значениям по умолчанию"""
        # Параметры времени
        self.tick_ms = DEFAULT_TICK_MS
        self.pitch_tick_enable = False
        self.pitch_tick_min = DEFAULT_PTICK_MIN_MS
        self.pitch_tick_max = DEFAULT_PTICK_MAX_MS
        
        # Цветовые параметры
        self.max_age = 120
        self.aging_speed = 1.0
        self.fade_start = 60
        self.fade_sat_drop = 70
        self.fade_val_drop = 60
        self.color_rms_min = DEFAULT_COLOR_RMS_MIN
        self.color_rms_max = DEFAULT_COLOR_RMS_MAX
        self.rms_strength = 100
        self.gain = 2.5
        self.global_v_mul = 1.0
        
        # Параметры soft clear
        self.soft_clear_enable = True
        self.soft_mode = 'Удалять клетки'
        self.soft_kill_rate = 80
        self.soft_fade_floor = 0.3
        self.soft_fade_down = 1
        self.soft_fade_up = 5
        
        # Сброс FX
        self.fx = {}
        
        # Сброс зеркалирования
        self.mirror_x = False
        self.mirror_y = False
        
        # Обновляем HUD
        self.hud.update_from_app(self)
        
        print("🔄 All parameters reset to defaults")

    def save_current_preset(self):
        """Сохраняет текущие настройки в файл пресета"""
        preset_data = {
            'timestamp': time.time(),
            'version': 'v13',
            'settings': {
                'tick_ms': self.tick_ms,
                'pitch_tick_enable': self.pitch_tick_enable,
                'pitch_tick_min': self.pitch_tick_min,
                'pitch_tick_max': self.pitch_tick_max,
                'max_age': self.max_age,
                'aging_speed': self.aging_speed,
                'fade_start': self.fade_start,
                'fade_sat_drop': self.fade_sat_drop,
                'fade_val_drop': self.fade_val_drop,
                'color_rms_min': self.color_rms_min,
                'color_rms_max': self.color_rms_max,
                'rms_strength': self.rms_strength,
                'gain': self.gain,
                'global_v_mul': self.global_v_mul,
                'soft_clear_enable': self.soft_clear_enable,
                'soft_mode': self.soft_mode,
                'soft_kill_rate': self.soft_kill_rate,
                'soft_fade_floor': self.soft_fade_floor,
                'soft_fade_down': self.soft_fade_down,
                'soft_fade_up': self.soft_fade_up,
                'mirror_x': self.mirror_x,
                'mirror_y': self.mirror_y
            },
            'fx': dict(self.fx),
            'layers': []
        }
        
        # Сохраняем настройки слоев
        for i, layer in enumerate(self.layers):
            layer_data = {
                'rule': layer.rule,
                'age_palette': layer.age_palette,
                'rms_palette': layer.rms_palette,
                'color_mode': layer.color_mode,
                'rms_mode': layer.rms_mode,
                'alpha_live': layer.alpha_live,
                'alpha_old': layer.alpha_old,
                'mix': layer.mix,
                'solo': layer.solo,
                'mute': layer.mute,
                'blend_mode': getattr(layer, 'blend_mode', 'normal')
            }
            preset_data['layers'].append(layer_data)
        
    def save_layer_settings(self):
        """Сохраняет настройки слоев в конфиг"""

  
    def load_preset(self, filename: str):
        """Загружает пресет из файла"""
       
    def create_glider_pattern(self):
        """Создает паттерн планеров Conway's Game of Life"""
        # Очищаем все слои
        self.clear_all_layers()
        
        # Планер - классический паттерн Conway's Game of Life
        glider_pattern = [
            [0, 1, 0],
            [0, 0, 1],
            [1, 1, 1]
        ]
        
        for layer in self.layers:
            # Устанавливаем правило Conway для всех слоев
            layer.rule = "Conway"
            
            # Размещаем несколько планеров в разных местах
            positions = [
                (10, 10), (30, 20), (50, 40), (20, 50), (40, 15)
            ]
            
            for start_r, start_c in positions:
                # Проверяем границы
                if start_r + 3 < GRID_H and start_c + 3 < GRID_W:
                    for dr, row in enumerate(glider_pattern):
                        for dc, cell in enumerate(row):
                            if cell:
                                r, c = start_r + dr, start_c + dc
                                layer.grid[r, c] = True
                                layer.age[r, c] = 1
        
    
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
        
        print("🧪 Test pattern created")

    def clear_all_layers(self):
        """Очищает все клетки во всех слоях"""
        for layer in self.layers:
            layer.grid.fill(False)
            layer.age.fill(0)
        print("🧹 All layers cleared")

    def generate_random_patterns(self):
        """Генерирует случайные паттерны во всех слоях"""
        self.clear_all_layers()
        
        for layer in self.layers:
            # Создаем случайные паттерны
            num_patterns = random.randint(3, 8)
            
            for _ in range(num_patterns):
                # Выбираем случайную позицию
                r = random.randint(5, GRID_H - 10)
                c = random.randint(5, GRID_W - 10)
                
                # Выбираем случайный тип паттерна
                pattern_type = random.choice(['block', 'line', 'cross', 'random_cluster'])
                
                if pattern_type == 'block':
                    # Блок 2x2 или 3x3
                    size = random.choice([2, 3])
                    for dr in range(size):
                        for dc in range(size):
                            if r + dr < GRID_H and c + dc < GRID_W:
                                layer.grid[r + dr, c + dc] = True
                                layer.age[r + dr, c + dc] = 1
                
                elif pattern_type == 'line':
                    # Горизонтальная или вертикальная линия
                    length = random.randint(3, 7)
                    if random.choice([True, False]):  # Горизонтальная
                        for dc in range(length):
                            if c + dc < GRID_W:
                                layer.grid[r, c + dc] = True
                                layer.age[r, c + dc] = 1
                    else:  # Вертикальная
                        for dr in range(length):
                            if r + dr < GRID_H:
                                layer.grid[r + dr, c] = True
                                layer.age[r + dr, c] = 1
                
                elif pattern_type == 'cross':
                    # Крестообразный паттерн
                    layer.grid[r, c] = True
                    layer.age[r, c] = 1
                    for delta in [-1, 1]:
                        if 0 <= r + delta < GRID_H:
                            layer.grid[r + delta, c] = True
                            layer.age[r + delta, c] = 1
                        if 0 <= c + delta < GRID_W:
                            layer.grid[r, c + delta] = True
                            layer.age[r, c + delta] = 1
                
                else:  # random_cluster
                    # Случайный кластер
                    cluster_size = random.randint(4, 12)
                    for _ in range(cluster_size):
                        dr = random.randint(-2, 2)
                        dc = random.randint(-2, 2)
                        if 0 <= r + dr < GRID_H and 0 <= c + dc < GRID_W:
                            layer.grid[r + dr, c + dc] = True
                            layer.age[r + dr, c + dc] = 1
        
        print("🎲 Random patterns generated")

    def run(self):          
        global audio_gain
        rms = 0.0; pitch = 0.0
        running = True
        frame_count = 0  # Счетчик кадров для оптимизации HUD
        
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
                    # Генерация случайных слоев
                    elif ev.key == pygame.K_1:
                        self.generate_random_layers(1)
                    elif ev.key == pygame.K_2:
                        self.generate_random_layers(2)
                    elif ev.key == pygame.K_3:
                        self.generate_random_layers(3)
                    elif ev.key == pygame.K_4:
                        self.generate_random_layers(4)
                    elif ev.key == pygame.K_5:
                        self.generate_random_layers(5)
                    # Генерация пресетных слоев
                    elif ev.key == pygame.K_F4:
                        self.generate_preset_layers(3, "balanced")
                    elif ev.key == pygame.K_F5:
                        self.generate_preset_layers(3, "chaotic")
                    elif ev.key == pygame.K_F6:
                        self.generate_preset_layers(3, "stable")
                    # Дублирование слоя
                    elif ev.key == pygame.K_d and (pygame.key.get_pressed()[pygame.K_LCTRL] or pygame.key.get_pressed()[pygame.K_RCTRL]):
                        self.duplicate_layer(self.selected_layer_index)
                    # Добавление нового слоя
                    elif ev.key == pygame.K_PLUS or ev.key == pygame.K_EQUALS:
                        self.add_new_layer()
                elif ev.type == pygame.KEYUP:
                    if ev.key == pygame.K_TAB:
                        self.hud.mini_held = False

            # снять свежие значения аудио (ограничиваем для производительности)
            audio_updates = 0
            try:
                while audio_updates < 10:  # Ограничиваем количество обновлений
                    new_pitch = pitch_queue.get_nowait()
                    new_rms = rms_queue.get_nowait()
                    pitch = new_pitch
                    rms = new_rms
                    audio_updates += 1
            except queue.Empty:
                pass

            # Обрабатываем отложенное сохранение
            self._process_pending_save()

            # тик автомата
            now = pygame.time.get_ticks()
            dyn_ms = self.maybe_tick_interval(pitch)
            if now - self.last_tick >= dyn_ms:
                self.last_tick = now
                births = int(SPAWN_BASE + SPAWN_SCALE *
                             clamp01(math.log10(1.0 + VOLUME_SCALE * max(0.0, rms))))
                
                if rms < self.sel.get('clear_rms', DEFAULT_CLEAR_RMS):
                    self.soft_clear()
                else:
                    self.soft_recover()
                self.update_layers(births)

            # рендер
            self.render(rms, pitch)

            # HUD - обновляем не каждый кадр для производительности
            frame_count += 1
            if frame_count % 5 == 0:  # Обновляем каждый 5-й кадр
                total_alive = self.get_total_alive_cached()
                
                # Создаем информацию о альфа-значениях слоев
                alpha_info = []
                for i, layer in enumerate(self.layers):
                    alpha_info.append(f"L{i}: {layer.alpha_live}/{layer.alpha_old}")
                
                info = {
                    "RMS": f"{rms:.4f}",
                    "Pitch": f"{pitch:.1f} Hz" if pitch > 0 else "—",
                    "Tick": f"{dyn_ms} ms",
                    "Alive": f"{total_alive} cells",
                    "Layers": f"{len(self.layers)}",
                    "Max Age": f"{self.max_age}",
                    "Aging Speed": f"{self.aging_speed:.1f}x",
                    "Alpha Values": " | ".join(alpha_info) if alpha_info else "none",
                    "FX": ", ".join([k for k in ['trails','blur','bloom','posterize','dither','scanlines','pixelate','outline']
                                     if self.fx.get(k, False)]) or "none",
                }
            else:
                # Используем простую информацию без тяжелых вычислений
                info = {
                    "RMS": f"{rms:.4f}",
                    "Pitch": f"{pitch:.1f} Hz" if pitch > 0 else "—",
                    "Tick": f"{dyn_ms} ms",
                }
            
            self.hud.draw(self.screen, info)

            pygame.display.flip()
            self.clock.tick(FPS)
        pygame.quit()


# === MAIN APPLICATION CLASS ===

class App:
    """Основной класс приложения Guitar Life"""
    
    def __init__(self, settings):
        # Инициализация pygame
        pygame.init()
        
        # Настройки из параметров
        self.settings = settings
        self.gain = settings.get('gain', 2.5)
        
        # Экран и часы
        self.screen = pygame.display.set_mode((GRID_W * CELL_SIZE + HUD_WIDTH, GRID_H * CELL_SIZE))
        pygame.display.set_caption("Guitar Life")
        self.clock = pygame.time.Clock()
        
        # Создаем основные компоненты
        self.layers = []
        self.renderer = RenderManager(GRID_W, GRID_H, CELL_SIZE)
        
        # Инициализируем шрифт для HUD
        pygame.font.init()
        font = pygame.font.SysFont("arial", 14)
        self.hud = HUD(font, GRID_H * CELL_SIZE)
        
        # Параметры времени
        self.tick_ms = settings.get('tick_ms', 60)
        self.last_tick = 0
        
        # Основные параметры
        self.max_age = 120
        self.aging_speed = 1.0
        self.fade_start = 60
        self.fade_sat_drop = 70
        self.fade_val_drop = 60
        self.rms_strength = 100
        self.global_v_mul = 1.0
        self.fx = {}
        self.mirror_x = False
        self.mirror_y = False
        
        # Создаем начальные слои
        self.create_initial_layers()
        
    def create_initial_layers(self):
        """Создает начальные слои"""
        for i in range(3):  # Создаем 3 слоя по умолчанию
            layer = Layer(
                grid=np.zeros((GRID_H, GRID_W), dtype=bool),
                age=np.zeros((GRID_H, GRID_W), dtype=np.int32),
                rule="Conway",
                age_palette=PALETTE_OPTIONS[i % len(PALETTE_OPTIONS)],
                rms_palette=PALETTE_OPTIONS[(i + 1) % len(PALETTE_OPTIONS)],
                color_mode="HSV-дизайны"
            )
            self.layers.append(layer)
    
    def run(self):
        """Основной цикл приложения"""
        global audio_gain
        rms = 0.0
        pitch = 0.0
        running = True
        frame_count = 0
        
        # Initialize global audio gain for audio callback
        audio_gain = self.gain
        
        print("🚀 Guitar Life запущен!")
        
        while running:
            # Обработка событий
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        # Пауза/возобновление
                        pass
                    elif event.key == pygame.K_r:
                        # Сброс
                        for layer in self.layers:
                            layer.grid.fill(False)
                            layer.age.fill(0)
            
            # Получаем аудио данные
            current_time = pygame.time.get_ticks()
            if current_time - self.last_tick >= self.tick_ms:
                rms = audio_rms
                pitch = audio_pitch
                
                # Обновляем слои
                for layer in self.layers:
                    if hasattr(layer, 'step_life'):
                        try:
                            layer.step_life()
                        except:
                            pass
                    # Исправляем проблему с типами
                    layer.age = (layer.age + self.aging_speed).astype(np.int32)
                
                self.last_tick = current_time
            
            # Рендеринг
            self.renderer.clear(BG_COLOR)
            
            # Отрисовка слоев (упрощенная версия)
            for layer in self.layers:
                if hasattr(layer, 'grid') and np.any(layer.grid):
                    # Создаем простое цветное изображение
                    color_img = np.zeros((GRID_H, GRID_W, 3), dtype=np.uint8)
                    live_mask = layer.grid
                    color_img[live_mask] = [255, 255, 255]  # Белый цвет для живых клеток
                    
                    # Отрисовка слоя
                    if hasattr(self.renderer, 'blit_layer'):
                        try:
                            self.renderer.blit_layer(color_img, "Normal", 255, 255)
                        except:
                            pass
            
            # Копируем на экран
            self.screen.blit(self.renderer.canvas, (0, 0))
            
            # Простая информация
            if frame_count % 30 == 0:  # Обновляем каждые 30 кадров
                info = {
                    "RMS": f"{rms:.4f}",
                    "Pitch": f"{pitch:.1f} Hz" if pitch > 0 else "—",
                    "Layers": f"{len(self.layers)}",
                }
                
                if hasattr(self.hud, 'draw'):
                    try:
                        self.hud.draw(self.screen, info)
                    except:
                        pass
            
            pygame.display.flip()
            self.clock.tick(60)  # 60 FPS
            frame_count += 1

        pygame.quit()


# === AUDIO FUNCTIONS ===

def audio_callback(indata, frames, time, status):
    """Callback для обработки аудио потока"""
    global audio_rms, audio_pitch
    
    try:
        audio_data = indata[:, 0] * audio_gain
        
        # Вычисляем RMS
        audio_rms = np.sqrt(np.mean(audio_data ** 2))
        
        # Простое определение частоты через FFT
        fft = np.fft.rfft(audio_data)
        magnitude = np.abs(fft)
        
        # Находим доминирующую частоту
        freqs = np.fft.rfftfreq(len(audio_data), 1/44100)  # Используем константу напрямую
        peak_idx = np.argmax(magnitude[1:]) + 1  # Исключаем DC компоненту
        audio_pitch = freqs[peak_idx] if peak_idx < len(freqs) else 0.0
        
    except Exception:
        audio_rms = 0.0
        audio_pitch = 0.0

def start_audio_stream(device_name):
    """Запускает аудио стрим"""
    if sd is None:
        print("⚠️ sounddevice недоступен — нет аудио-входа.")
        return None
    
    device_id = None
    for i, d in enumerate(sd.query_devices()):
        if d['name'] == device_name:
            device_id = i
            break
    
    if device_id is None:
        print(f"⚠️ Устройство '{device_name}' не найдено")
        return None
    
    try:
        stream = sd.InputStream(
            samplerate=44100,  # Используем константу напрямую
            blocksize=2048,   # Используем константу напрямую
            dtype='float32',
            channels=1,       # Используем константу напрямую
            device=device_id, 
            callback=audio_callback
        )
        stream.start()
        return stream
    except Exception as e:
        print(f"❌ Ошибка запуска аудио: {e}")
        return None

def choose_settings():
    """Возвращает настройки по умолчанию"""
    return {
        'device': 'default',
        'tick_ms': 60,
        'gain': 2.5
    }


# -------------------- Запуск ---------------

def main(sel=None):
    if sel is None:
        sel = choose_settings()
        if not sel:
            return
    
    stream = start_audio_stream(sel['device'])
    try:
        app = App(sel)
        app.run()
    finally:
        try:
            stream.stop(); stream.close()
        except Exception:
            pass


def load_config():
    """Загружает конфигурацию из файла или создает конфигурацию по умолчанию"""
    try:
        with open('guitar_config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        print("📁 Configuration loaded from guitar_config.json")
        return config
    except FileNotFoundError:
        print("⚠️ guitar_config.json not found, using defaults")
        # Создаем конфигурацию по умолчанию
        default_config = {
            'device': 'Default',
            'layer_count': 3,
            'tick_ms': DEFAULT_TICK_MS,
            'pitch_tick_enable': False,
            'max_age': 120,
            'aging_speed': 1.0,
            'fade_start': 60,
            'fade_sat_drop': 70,
            'fade_val_drop': 60,
            'rms_strength': 100,
            'gain': 2.5,
            'soft_clear_enable': True,
            'soft_mode': 'Удалять клетки',
            'soft_kill_rate': 80,
            'layers_different': True,
            'fx': {},
            'mirror_x': False,
            'mirror_y': False
        }
        return default_config
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        return {'device': 'Default', 'layer_count': 3}


if __name__ == "__main__":
    # Загружаем конфигурацию и запускаем приложение
    import signal
    import sys
    
    def signal_handler(sig, frame):
        print('\n🛑 Программа прервана пользователем')
        pygame.quit()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        sel = load_config()
        main(sel)
    except KeyboardInterrupt:
        print('\n🛑 Программа прервана пользователем')
    except Exception as e:
        print(f'❌ Ошибка запуска: {e}')
        import traceback
        traceback.print_exc()
    finally:
        pygame.quit()
