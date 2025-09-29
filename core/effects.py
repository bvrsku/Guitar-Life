#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Guitar Life - Визуальные эффекты
===============================

Модуль содержит все визуальные эффекты для обработки изображений.
"""

import numpy as np
import pygame
from typing import Tuple

def clamp01(x: float) -> float:
    """Ограничивает значение в диапазоне [0, 1]"""
    return max(0.0, min(1.0, x))

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
    h = arr.shape[1]
    for y in range(1, h, 2):
        arr[:, y] = (arr[:, y] * (1.0 - strength)).astype(arr.dtype)

def apply_pixelate(surface: pygame.Surface, block: int):
    """Пикселизация через уменьшение и увеличение"""
    block = max(1, int(block))
    if block <= 1: 
        return
    w, h = surface.get_size()
    dw, dh = max(1, w//block), max(1, h//block)
    small = pygame.transform.scale(surface, (dw, dh))
    surface.blit(pygame.transform.scale(small, (w, h)), (0,0))

def apply_outline(surface: pygame.Surface, thickness: int = 1):
    """Эффект контура: выделение границ"""
    if thickness <= 0:
        return
    
    arr = pygame.surfarray.array3d(surface)
    arr = np.transpose(arr, (1, 0, 2))  # (height, width, channels)
    
    if len(arr.shape) != 3:
        return
    
    height, width, channels = arr.shape
    
    # Создаем копию для результата
    result = arr.copy()
    
    # Простой edge detection через разности
    for y in range(thickness, height - thickness):
        for x in range(thickness, width - thickness):
            # Сравниваем с соседними пикселями
            center = arr[y, x].astype(np.int32)
            
            # Проверяем соседей
            edge_strength = 0
            neighbors = [
                arr[y-thickness, x],    # верх
                arr[y+thickness, x],    # низ
                arr[y, x-thickness],    # лево
                arr[y, x+thickness]     # право
            ]
            
            for neighbor in neighbors:
                diff = np.sum(np.abs(center - neighbor.astype(np.int32)))
                edge_strength = max(edge_strength, diff)
            
            # Если найдена граница, делаем пиксель ярче
            if edge_strength > 30:  # порог для обнаружения границы
                result[y, x] = np.clip(arr[y, x].astype(np.int32) + 50, 0, 255).astype(np.uint8)
    
    # Транспонируем обратно и применяем
    result = np.transpose(result, (1, 0, 2))
    pygame.surfarray.blit_array(surface, result)

def blend_colors(color1: Tuple[int, int, int], color2: Tuple[int, int, int], 
                blend_mode: str = "normal", alpha: float = 0.5) -> Tuple[int, int, int]:
    """Смешивание двух цветов с различными режимами"""
    alpha = clamp01(alpha)
    r1, g1, b1 = color1
    r2, g2, b2 = color2
    
    if blend_mode == "normal":
        r = int(r1 * (1 - alpha) + r2 * alpha)
        g = int(g1 * (1 - alpha) + g2 * alpha)
        b = int(b1 * (1 - alpha) + b2 * alpha)
    elif blend_mode == "multiply":
        r = int((r1 * r2 / 255) * alpha + r1 * (1 - alpha))
        g = int((g1 * g2 / 255) * alpha + g1 * (1 - alpha))
        b = int((b1 * b2 / 255) * alpha + b1 * (1 - alpha))
    elif blend_mode == "screen":
        r = int((255 - ((255 - r1) * (255 - r2) / 255)) * alpha + r1 * (1 - alpha))
        g = int((255 - ((255 - g1) * (255 - g2) / 255)) * alpha + g1 * (1 - alpha))
        b = int((255 - ((255 - b1) * (255 - b2) / 255)) * alpha + b1 * (1 - alpha))
    elif blend_mode == "overlay":
        def overlay_channel(base, overlay):
            if base < 128:
                return 2 * base * overlay / 255
            else:
                return 255 - 2 * (255 - base) * (255 - overlay) / 255
        
        r = int(overlay_channel(r1, r2) * alpha + r1 * (1 - alpha))
        g = int(overlay_channel(g1, g2) * alpha + g1 * (1 - alpha))
        b = int(overlay_channel(b1, b2) * alpha + b1 * (1 - alpha))
    elif blend_mode == "add":
        r = int(min(255, r1 + r2 * alpha))
        g = int(min(255, g1 + g2 * alpha))
        b = int(min(255, b1 + b2 * alpha))
    elif blend_mode == "subtract":
        r = int(max(0, r1 - r2 * alpha))
        g = int(max(0, g1 - g2 * alpha))
        b = int(max(0, b1 - b2 * alpha))
    else:
        # Default to normal
        r = int(r1 * (1 - alpha) + r2 * alpha)
        g = int(g1 * (1 - alpha) + g2 * alpha)
        b = int(b1 * (1 - alpha) + b2 * alpha)
    
    return (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))

def apply_color_filter(surface: pygame.Surface, filter_color: Tuple[int, int, int], 
                      strength: float = 0.5, blend_mode: str = "multiply"):
    """Применение цветового фильтра к поверхности"""
    if strength <= 0:
        return
    
    strength = clamp01(strength)
    arr = pygame.surfarray.pixels3d(surface)
    h, w = arr.shape[1], arr.shape[0]
    
    for x in range(w):
        for y in range(h):
            original = (int(arr[x, y, 0]), int(arr[x, y, 1]), int(arr[x, y, 2]))
            filtered = blend_colors(original, filter_color, blend_mode, strength)
            arr[x, y] = filtered

def apply_vignette(surface: pygame.Surface, strength: float = 0.5, color: Tuple[int, int, int] = (0, 0, 0)):
    """Применение виньетки (затемнение по краям)"""
    if strength <= 0:
        return
    
    strength = clamp01(strength)
    w, h = surface.get_size()
    center_x, center_y = w // 2, h // 2
    max_distance = ((center_x ** 2 + center_y ** 2) ** 0.5)
    
    arr = pygame.surfarray.pixels3d(surface)
    
    for x in range(w):
        for y in range(h):
            # Расчет расстояния от центра
            distance = ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5
            # Нормализация расстояния
            normalized_distance = min(1.0, distance / max_distance)
            # Расчет силы виньетки
            vignette_strength = normalized_distance * strength
            
            # Применение виньетки
            original = (int(arr[x, y, 0]), int(arr[x, y, 1]), int(arr[x, y, 2]))
            vignetted = blend_colors(original, color, "multiply", vignette_strength)
            arr[x, y] = vignetted

# Список всех доступных эффектов
AVAILABLE_EFFECTS = [
    "trails",
    "blur", 
    "bloom",
    "posterize",
    "dither",
    "scanlines", 
    "pixelate",
    "outline",
    "color_filter",
    "vignette"
]

def apply_effect(surface: pygame.Surface, effect_name: str, **kwargs):
    """Универсальная функция для применения эффектов"""
    if effect_name == "trails":
        apply_trails(surface, kwargs.get("strength", 0.1))
    elif effect_name == "blur":
        apply_scale_blur(surface, kwargs.get("scale", 2))
    elif effect_name == "bloom":
        apply_bloom(surface, kwargs.get("strength", 0.3))
    elif effect_name == "posterize":
        apply_posterize(surface, kwargs.get("levels", 8))
    elif effect_name == "dither":
        apply_dither(surface)
    elif effect_name == "scanlines":
        apply_scanlines(surface, kwargs.get("strength", 0.3))
    elif effect_name == "pixelate":
        apply_pixelate(surface, kwargs.get("block_size", 4))
    elif effect_name == "outline":
        apply_outline(surface, kwargs.get("thickness", 1))
    elif effect_name == "color_filter":
        apply_color_filter(surface, kwargs.get("color", (255, 0, 0)), 
                          kwargs.get("strength", 0.5), kwargs.get("blend_mode", "multiply"))
    elif effect_name == "vignette":
        apply_vignette(surface, kwargs.get("strength", 0.5), kwargs.get("color", (0, 0, 0)))
    else:
        print(f"Unknown effect: {effect_name}")
