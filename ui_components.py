#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Guitar Life - UI компоненты
===========================
UI элементы для интерфейса.
"""

import pygame
from typing import List, Optional, Any

# Простая цветовая схема
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

class UISlider:
    """Интерактивный слайдер для HUD"""
    
    def __init__(self, x: int, y: int, width: int, height: int, 
                 min_val: float, max_val: float, current_val: float, 
                 label: str = "", value_format: str = "{:.0f}"):
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
    
    def _update_value_from_mouse(self, mouse_pos: tuple):
        """Обновляет значение на основе позиции мыши"""
        try:
            rel_x = mouse_pos[0] - self.rect.x
            ratio = max(0.0, min(1.0, rel_x / self.width))
            self.current_val = self.min_val + ratio * (self.max_val - self.min_val)
        except (TypeError, ValueError, ZeroDivisionError) as e:
            print(f"Slider value update error: {e}")
    
    def draw(self, surface: pygame.Surface, font: Optional[pygame.font.Font] = None):
        """Отрисовка простого современного слайдера"""
        # Синхронизируем координаты с rect
        self.x = self.rect.x
        self.y = self.rect.y
        
        # Простой фон слайдера
        bg_color = SimpleColors.GRAY_100 if self.dragging else SimpleColors.GRAY_50
        pygame.draw.rect(surface, bg_color, self.rect, border_radius=8)
        
        # Заполненная часть (прогресс)
        if self.max_val != self.min_val:
            ratio = (self.current_val - self.min_val) / (self.max_val - self.min_val)
            fill_width = int(self.width * ratio)
            if fill_width > 4:
                fill_rect = pygame.Rect(self.x, self.y, fill_width, self.height)
                fill_color = SimpleColors.PRIMARY if self.dragging else SimpleColors.PRIMARY_LIGHT
                pygame.draw.rect(surface, fill_color, fill_rect, border_radius=8)
        
        # Рамка слайдера
        border_color = SimpleColors.BORDER_FOCUS if self.dragging else SimpleColors.BORDER
        pygame.draw.rect(surface, border_color, self.rect, 2, border_radius=8)
        
        # Ручка слайдера
        if self.max_val != self.min_val:
            ratio = (self.current_val - self.min_val) / (self.max_val - self.min_val)
            handle_x = self.x + int(self.width * ratio)
            handle_y = self.y + self.height // 2
            
            # Основа ручки
            handle_color = SimpleColors.PRIMARY if self.dragging else SimpleColors.GRAY_400
            pygame.draw.circle(surface, SimpleColors.SURFACE, (handle_x, handle_y), 8)
            pygame.draw.circle(surface, handle_color, (handle_x, handle_y), 6)
            pygame.draw.circle(surface, SimpleColors.BORDER, (handle_x, handle_y), 8, 2)
        
        # Текст
        if self.label:
            try:
                label_font = pygame.font.SysFont("arial", 14) if font is None else font
                value_font = pygame.font.SysFont("arial", 13) if font is None else font
                
                # Безопасное отображение
                label_text = str(self.label).encode('ascii', 'ignore').decode('ascii')
                
                # Специальная обработка для логарифмического слайдера
                if self.value_format == "max_age_log":
                    from .palettes import max_age_slider_to_value
                    actual_max_age = max_age_slider_to_value(self.current_val)
                    value_text = f"{actual_max_age}"
                else:
                    value_text = str(self.value_format.format(self.current_val)).encode('ascii', 'ignore').decode('ascii')
                
                # Цвета текста
                label_color = SimpleColors.TEXT_PRIMARY
                value_color = SimpleColors.PRIMARY if self.dragging else SimpleColors.TEXT_SECONDARY
                
                label_surface = label_font.render(label_text, True, label_color)
                value_surface = value_font.render(value_text, True, value_color)
                
                # Размещение текста над слайдером
                text_y = self.y - 25
                surface.blit(label_surface, (self.x, text_y))
                value_x = self.x + self.width - value_surface.get_width()
                surface.blit(value_surface, (value_x, text_y))
                    
            except Exception as e:
                # Fallback
                fallback_text = str(int(self.current_val))
                fallback_font = pygame.font.Font(None, 16)
                fallback_surface = fallback_font.render(fallback_text, True, SimpleColors.TEXT_SECONDARY)
                surface.blit(fallback_surface, (self.x, self.y - 25))

class UIButton:
    """Интерактивная кнопка для HUD"""
    
    def __init__(self, x: int, y: int, width: int, height: int, label: str, 
                 is_toggle: bool = False, active: bool = False):
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
    
    def draw(self, surface: pygame.Surface, font: Optional[pygame.font.Font] = None):
        """Отрисовка простой современной кнопки"""
        # Синхронизируем координаты с rect
        self.x = self.rect.x
        self.y = self.rect.y
        
        # Цвета кнопки
        if self.is_toggle and self.active:
            bg_color = SimpleColors.PRIMARY
            border_color = SimpleColors.PRIMARY
        elif self.pressed:
            bg_color = SimpleColors.ACTIVE
            border_color = SimpleColors.BORDER_FOCUS
        else:
            bg_color = SimpleColors.SURFACE
            border_color = SimpleColors.BORDER
            
        # Рисуем кнопку
        pygame.draw.rect(surface, bg_color, self.rect, border_radius=8)
        pygame.draw.rect(surface, border_color, self.rect, 2, border_radius=8)
        
        # Индикатор для активных переключателей
        if self.is_toggle and self.active:
            pygame.draw.circle(surface, SimpleColors.SURFACE, (self.x + 8, self.y + 8), 3)
        
        # Текст
        try:
            button_font = pygame.font.SysFont("arial", 12) if font is None else font
            button_text = str(self.label).encode('ascii', 'ignore').decode('ascii')
            
            if self.is_toggle and self.active:
                text_color = SimpleColors.SURFACE
            else:
                text_color = SimpleColors.TEXT_PRIMARY
                
            text = button_font.render(button_text, True, text_color)
            text_rect = text.get_rect(center=self.rect.center)
            surface.blit(text, text_rect)
            
        except Exception:
            # Fallback
            fallback_font = pygame.font.Font(None, 12)
            text = fallback_font.render("BTN", True, SimpleColors.TEXT_SECONDARY)
            text_rect = text.get_rect(center=self.rect.center)
            surface.blit(text, text_rect)

class UIComboBox:
    """Выпадающий список для HUD"""
    
    def __init__(self, x: int, y: int, width: int, height: int, label: str, 
                 options: List[str], current_index: int = 0):
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
        self.selected_index = current_index
        
    @property
    def expanded(self) -> bool:
        """Alias для is_open для совместимости"""
        return self.is_open
        
    @expanded.setter
    def expanded(self, value: bool):
        """Setter для expanded"""
        self.is_open = value
        
    @property
    def current_value(self) -> str:
        """Текущее выбранное значение"""
        if 0 <= self.current_index < len(self.options):
            return self.options[self.current_index]
        return ""
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Обработка событий комбобокса"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                # Клик по основному элементу
                self.is_open = not self.is_open
                if self.is_open:
                    self.selected_index = self.current_index
                return True
            elif self.is_open:
                # Клик по выпадающему списку
                dropdown_rect = self._get_dropdown_rect()
                if dropdown_rect.collidepoint(event.pos):
                    # Определяем элемент
                    relative_y = event.pos[1] - dropdown_rect.y
                    item_index = int(relative_y // self.height) + self.scroll_offset
                    
                    if 0 <= item_index < len(self.options):
                        self.current_index = item_index
                        self.selected_index = item_index
                        self.is_open = False
                        return True
                else:
                    # Клик вне списка - закрываем
                    self.is_open = False
                    return False
        
        elif event.type == pygame.MOUSEWHEEL and self.is_open:
            # Прокрутка в списке
            dropdown_rect = self._get_dropdown_rect()
            if dropdown_rect.collidepoint(pygame.mouse.get_pos()):
                self.scroll_offset = max(0, min(self.scroll_offset - event.y, 
                                              len(self.options) - self.max_visible_items))
                return True
        
        elif event.type == pygame.KEYDOWN and self.is_open:
            # Навигация клавиатурой
            if event.key == pygame.K_UP:
                if self.selected_index > 0:
                    self.selected_index -= 1
                    if self.selected_index < self.scroll_offset:
                        self.scroll_offset = self.selected_index
                return True
            
            elif event.key == pygame.K_DOWN:
                if self.selected_index < len(self.options) - 1:
                    self.selected_index += 1
                    if self.selected_index >= self.scroll_offset + self.max_visible_items:
                        self.scroll_offset = self.selected_index - self.max_visible_items + 1
                return True
            
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                if 0 <= self.selected_index < len(self.options):
                    self.current_index = self.selected_index
                    self.is_open = False
                return True
            
            elif event.key == pygame.K_ESCAPE:
                self.selected_index = self.current_index
                self.is_open = False
                return True
        
        return False
    
    def _get_dropdown_rect(self) -> pygame.Rect:
        """Получить прямоугольник выпадающего списка"""
        visible_items = min(self.max_visible_items, len(self.options))
        dropdown_height = visible_items * self.height
        return pygame.Rect(self.x, self.y + self.height, self.width, dropdown_height)
    
    def draw(self, surface: pygame.Surface, font: Optional[pygame.font.Font] = None):
        """Отрисовка комбобокса"""
        # Синхронизируем координаты
        self.x = self.rect.x
        self.y = self.rect.y
        
        # Основной элемент
        bg_color = SimpleColors.ACTIVE if self.is_open else SimpleColors.SURFACE
        border_color = SimpleColors.BORDER_FOCUS if self.is_open else SimpleColors.BORDER
        
        pygame.draw.rect(surface, bg_color, self.rect, border_radius=8)
        pygame.draw.rect(surface, border_color, self.rect, 2, border_radius=8)
        
        # Стрелка
        arrow_x = self.x + self.width - 20
        arrow_y = self.y + self.height // 2
        arrow_points = [
            (arrow_x, arrow_y - 3),
            (arrow_x + 6, arrow_y + 3),
            (arrow_x - 6, arrow_y + 3)
        ]
        pygame.draw.polygon(surface, SimpleColors.TEXT_SECONDARY, arrow_points)
        
        # Текст текущего значения
        try:
            combo_font = pygame.font.SysFont("arial", 12) if font is None else font
            current_text = str(self.current_value).encode('ascii', 'ignore').decode('ascii')
            
            # Обрезаем текст если он слишком длинный
            max_width = self.width - 30
            if combo_font.size(current_text)[0] > max_width:
                # Обрезаем текст
                while combo_font.size(current_text + "...")[0] > max_width and len(current_text) > 3:
                    current_text = current_text[:-1]
                current_text += "..."
            
            text_color = SimpleColors.TEXT_PRIMARY
            text = combo_font.render(current_text, True, text_color)
            text_y = self.y + (self.height - text.get_height()) // 2
            surface.blit(text, (self.x + 8, text_y))
            
        except Exception:
            # Fallback
            fallback_font = pygame.font.Font(None, 12)
            text = fallback_font.render("...", True, SimpleColors.TEXT_SECONDARY)
            text_y = self.y + (self.height - text.get_height()) // 2
            surface.blit(text, (self.x + 8, text_y))
        
        # Выпадающий список
        if self.is_open:
            self._draw_dropdown(surface, font)
    
    def _draw_dropdown(self, surface: pygame.Surface, font: Optional[pygame.font.Font] = None):
        """Отрисовка выпадающего списка"""
        dropdown_rect = self._get_dropdown_rect()
        
        # Фон списка
        pygame.draw.rect(surface, SimpleColors.SURFACE, dropdown_rect, border_radius=8)
        pygame.draw.rect(surface, SimpleColors.BORDER, dropdown_rect, 2, border_radius=8)
        
        # Элементы списка
        try:
            dropdown_font = pygame.font.SysFont("arial", 12) if font is None else font
            
            visible_items = min(self.max_visible_items, len(self.options))
            for i in range(visible_items):
                item_index = i + self.scroll_offset
                if item_index >= len(self.options):
                    break
                
                item_rect = pygame.Rect(
                    dropdown_rect.x,
                    dropdown_rect.y + i * self.height,
                    dropdown_rect.width,
                    self.height
                )
                
                # Фон элемента
                if item_index == self.selected_index:
                    pygame.draw.rect(surface, SimpleColors.PRIMARY_LIGHT, item_rect)
                elif item_index == self.current_index:
                    pygame.draw.rect(surface, SimpleColors.GRAY_100, item_rect)
                
                # Текст элемента
                option_text = str(self.options[item_index]).encode('ascii', 'ignore').decode('ascii')
                
                # Обрезаем текст если нужно
                max_width = dropdown_rect.width - 16
                if dropdown_font.size(option_text)[0] > max_width:
                    while dropdown_font.size(option_text + "...")[0] > max_width and len(option_text) > 3:
                        option_text = option_text[:-1]
                    option_text += "..."
                
                text_color = SimpleColors.TEXT_PRIMARY
                text = dropdown_font.render(option_text, True, text_color)
                text_y = item_rect.y + (self.height - text.get_height()) // 2
                surface.blit(text, (item_rect.x + 8, text_y))
                
        except Exception:
            # Fallback для проблемных случаев
            pass
        
        # Скроллбар если нужен
        if len(self.options) > self.max_visible_items:
            self._draw_scrollbar(surface, dropdown_rect)
    
    def _draw_scrollbar(self, surface: pygame.Surface, dropdown_rect: pygame.Rect):
        """Отрисовка скроллбара"""
        scrollbar_width = 8
        scrollbar_x = dropdown_rect.x + dropdown_rect.width - scrollbar_width - 2
        scrollbar_rect = pygame.Rect(scrollbar_x, dropdown_rect.y + 2, 
                                   scrollbar_width, dropdown_rect.height - 4)
        
        # Фон скроллбара
        pygame.draw.rect(surface, SimpleColors.GRAY_200, scrollbar_rect, border_radius=4)
        
        # Ползунок
        total_items = len(self.options)
        visible_items = self.max_visible_items
        thumb_height = max(20, int((visible_items / total_items) * scrollbar_rect.height))
        thumb_y = scrollbar_rect.y + int((self.scroll_offset / (total_items - visible_items)) * 
                                       (scrollbar_rect.height - thumb_height))
        
        thumb_rect = pygame.Rect(scrollbar_x, thumb_y, scrollbar_width, thumb_height)
        pygame.draw.rect(surface, SimpleColors.GRAY_400, thumb_rect, border_radius=4)

# Вспомогательные функции для UI
def create_slider(x: int, y: int, width: int, height: int, min_val: float, max_val: float, 
                 current_val: float, label: str = "", value_format: str = "{:.0f}") -> UISlider:
    """Создать слайдер с заданными параметрами"""
    return UISlider(x, y, width, height, min_val, max_val, current_val, label, value_format)

def create_button(x: int, y: int, width: int, height: int, label: str, 
                 is_toggle: bool = False, active: bool = False) -> UIButton:
    """Создать кнопку с заданными параметрами"""
    return UIButton(x, y, width, height, label, is_toggle, active)

def create_combobox(x: int, y: int, width: int, height: int, label: str, 
                   options: List[str], current_index: int = 0) -> UIComboBox:
    """Создать комбобокс с заданными параметрами"""
    return UIComboBox(x, y, width, height, label, options, current_index)

def handle_ui_events(ui_elements: List[Any], event: pygame.event.Event) -> Optional[Any]:
    """Обработать события для списка UI элементов"""
    for element in ui_elements:
        if hasattr(element, 'handle_event') and element.handle_event(event):
            return element
    return None

def draw_ui_elements(surface: pygame.Surface, ui_elements: List[Any], font: Optional[pygame.font.Font] = None):
    """Отрисовать список UI элементов"""
    for element in ui_elements:
        if hasattr(element, 'draw'):
            element.draw(surface, font)
