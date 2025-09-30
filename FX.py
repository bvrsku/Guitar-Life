"""
"""

import pygame
import numpy as np


def clamp01(x):
    """Ограничивает значение между 0 и 1"""
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
    
    #Тайл нужного размера (height, width) 
    tile_height = (height // pattern.shape[0] + 1) * pattern.shape[0]
    tile_width = (width // pattern.shape[1] + 1) * pattern.shape[1]
    
    # Тайл pattern
    tile = np.tile(pattern, (tile_height // pattern.shape[0], tile_width // pattern.shape[1]))
    
    # Обрезаем до нужного размера
    tile = tile[:height, :width]
    
    # Добавляем размерность для channels и применяем ко всем каналам
    tile = tile[:, :, np.newaxis]  # (height, width, 1)
    
    # Применяем dither
    arr = arr + (tile * 16 - 8)
    
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