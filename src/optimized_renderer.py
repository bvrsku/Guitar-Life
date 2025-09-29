#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Оптимизированный рендерер для Guitar Life
Улучшенная производительность рендеринга слоев
"""

import pygame
import numpy as np
import time
from typing import List, Dict, Tuple, Optional, Any

class OptimizedRenderManager:
    """Оптимизированный менеджер рендеринга с кэшированием поверхностей"""
    
    def __init__(self, w_cells: int, h_cells: int, cell_size: int):
        self.wc = w_cells
        self.hc = h_cells
        self.cs = cell_size
        
        # Основная поверхность для рендеринга
        self.canvas = pygame.Surface((w_cells * cell_size, h_cells * cell_size)).convert()
        
        # Кэш поверхностей для каждого слоя
        self.layer_surfaces: Dict[int, pygame.Surface] = {}
        self.layer_hashes: Dict[int, int] = {}
        
        # Статистика производительности
        self.cache_hits = 0
        self.cache_misses = 0
        self.last_render_time = 0
        
    def clear(self, color=(0, 0, 0)):
        """Очищает основную поверхность"""
        self.canvas.fill(color)
        
    def get_layer_hash(self, layer) -> int:
        """Вычисляет хэш состояния слоя для определения изменений"""
        try:
            # Комбинируем хэши ключевых параметров слоя
            grid_hash = hash(layer.grid.tobytes())
            age_hash = hash(layer.age.tobytes()) if hasattr(layer, 'age') else 0
            params_hash = hash((
                layer.color_mode if hasattr(layer, 'color_mode') else '',
                layer.age_palette if hasattr(layer, 'age_palette') else '',
                layer.rms_palette if hasattr(layer, 'rms_palette') else '',
                layer.alpha_live if hasattr(layer, 'alpha_live') else 255,
                layer.alpha_old if hasattr(layer, 'alpha_old') else 255,
                layer.mix if hasattr(layer, 'mix') else 'Normal'
            ))
            return hash((grid_hash, age_hash, params_hash))
        except Exception as e:
            print(f"⚠️ Error computing layer hash: {e}")
            return hash(time.time())  # Fallback
    
    def create_layer_surface(self, color_img: np.ndarray) -> pygame.Surface:
        """Создает поверхность pygame из цветового изображения"""
        try:
            h, w = color_img.shape[:2]
            
            # Создаем поверхность из numpy массива
            rgb_surf = pygame.surfarray.make_surface(np.transpose(color_img, (1, 0, 2)))
            
            # Масштабируем до размера пикселей
            scaled_size = (w * self.cs, h * self.cs)
            rgb_surf = pygame.transform.scale(rgb_surf, scaled_size)
            
            # Конвертируем для лучшей производительности
            rgb_surf = rgb_surf.convert()
            
            return rgb_surf
        except Exception as e:
            print(f"❌ Error creating layer surface: {e}")
            # Создаем пустую поверхность как fallback
            return pygame.Surface((self.wc * self.cs, self.hc * self.cs)).convert()
    
    def blit_layer_optimized(self, layer_id: int, layer, color_img: np.ndarray):
        """Оптимизированный блит слоя с кэшированием"""
        current_hash = self.get_layer_hash(layer)
        
        # Проверяем нужно ли обновлять кэшированную поверхность
        if (layer_id not in self.layer_surfaces or 
            self.layer_hashes.get(layer_id) != current_hash):
            
            # Кэш промах - создаем новую поверхность
            self.layer_surfaces[layer_id] = self.create_layer_surface(color_img)
            self.layer_hashes[layer_id] = current_hash
            self.cache_misses += 1
        else:
            # Кэш попадание
            self.cache_hits += 1
        
        # Получаем кэшированную поверхность
        surface = self.layer_surfaces[layer_id]
        
        # Применяем настройки прозрачности и смешивания
        self.apply_layer_blending(surface, layer)
        
        # Рендерим на основную поверхность
        self.canvas.blit(surface, (0, 0))
    
    def apply_layer_blending(self, surface: pygame.Surface, layer):
        """Применяет настройки смешивания и прозрачности к поверхности"""
        try:
            # Устанавливаем прозрачность
            alpha = getattr(layer, 'alpha_live', 255)
            surface.set_alpha(alpha)
            
            # Устанавливаем режим смешивания
            mix_mode = getattr(layer, 'mix', 'Normal')
            if mix_mode == "Additive":
                surface.set_blend_mode(pygame.BLEND_RGB_ADD)
            else:
                surface.set_blend_mode(pygame.BLEND_ALPHA_SDL2)
                
            # Устанавливаем цветовой ключ для прозрачности
            surface.set_colorkey((0, 0, 0))
            
        except Exception as e:
            print(f"⚠️ Error applying layer blending: {e}")
    
    def render_layers_batch(self, layers: List, color_images: List[np.ndarray]):
        """Батчевый рендеринг нескольких слоев"""
        start_time = time.perf_counter()
        
        # Очищаем основную поверхность
        self.clear()
        
        # Группируем слои по режимам смешивания для оптимизации
        normal_layers = []
        additive_layers = []
        
        for i, layer in enumerate(layers):
            mix_mode = getattr(layer, 'mix', 'Normal')
            layer_data = (i, layer, color_images[i] if i < len(color_images) else None)
            
            if mix_mode == "Additive":
                additive_layers.append(layer_data)
            else:
                normal_layers.append(layer_data)
        
        # Сначала рендерим Normal слои (более быстрые)
        for layer_id, layer, color_img in normal_layers:
            if color_img is not None:
                self.blit_layer_optimized(layer_id, layer, color_img)
        
        # Затем рендерим Additive слои (более медленные)
        for layer_id, layer, color_img in additive_layers:
            if color_img is not None:
                self.blit_layer_optimized(layer_id, layer, color_img)
        
        self.last_render_time = time.perf_counter() - start_time
    
    def cleanup_cache(self, active_layer_ids: List[int]):
        """Очищает кэш от неиспользуемых слоев"""
        cached_ids = list(self.layer_surfaces.keys())
        for layer_id in cached_ids:
            if layer_id not in active_layer_ids:
                del self.layer_surfaces[layer_id]
                if layer_id in self.layer_hashes:
                    del self.layer_hashes[layer_id]
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Возвращает статистику производительности"""
        total_requests = self.cache_hits + self.cache_misses
        hit_rate = (self.cache_hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'cache_hit_rate': hit_rate,
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'cached_surfaces': len(self.layer_surfaces),
            'last_render_time_ms': self.last_render_time * 1000
        }
    
    def print_performance_stats(self):
        """Выводит статистику производительности"""
        stats = self.get_performance_stats()
        print(f"🎯 Render Performance:")
        print(f"   Cache hit rate: {stats['cache_hit_rate']:.1f}%")
        print(f"   Render time: {stats['last_render_time_ms']:.1f}ms")
        print(f"   Cached surfaces: {stats['cached_surfaces']}")


class PerformanceMonitor:
    """Мониторинг производительности рендеринга"""
    
    def __init__(self, window_size: int = 60):
        self.window_size = window_size
        self.frame_times = []
        self.render_times = []
        self.frame_start = 0
        
    def start_frame(self):
        """Начинает измерение времени кадра"""
        self.frame_start = time.perf_counter()
    
    def end_frame(self):
        """Заканчивает измерение времени кадра"""
        frame_time = time.perf_counter() - self.frame_start
        self.frame_times.append(frame_time)
        
        # Поддерживаем скользящее окно
        if len(self.frame_times) > self.window_size:
            self.frame_times.pop(0)
    
    def record_render_time(self, render_time: float):
        """Записывает время рендеринга"""
        self.render_times.append(render_time)
        
        if len(self.render_times) > self.window_size:
            self.render_times.pop(0)
    
    def get_fps(self) -> float:
        """Возвращает текущий FPS"""
        if not self.frame_times:
            return 0
        avg_frame_time = sum(self.frame_times) / len(self.frame_times)
        return 1.0 / avg_frame_time if avg_frame_time > 0 else 0
    
    def get_avg_render_time(self) -> float:
        """Возвращает среднее время рендеринга в миллисекундах"""
        if not self.render_times:
            return 0
        return (sum(self.render_times) / len(self.render_times)) * 1000
    
    def print_stats(self):
        """Выводит статистику производительности"""
        fps = self.get_fps()
        avg_render = self.get_avg_render_time()
        current_frame = self.frame_times[-1] * 1000 if self.frame_times else 0
        
        print(f"📊 Performance Stats:")
        print(f"   FPS: {fps:.1f}")
        print(f"   Frame time: {current_frame:.1f}ms")
        print(f"   Avg render time: {avg_render:.1f}ms")


# Пример интеграции с существующим кодом
class OptimizedApp:
    """Пример интеграции оптимизированного рендеринга"""
    
    def __init__(self):
        # Заменяем стандартный RenderManager на оптимизированный
        self.renderer = OptimizedRenderManager(GRID_W, GRID_H, CELL_SIZE)
        self.performance = PerformanceMonitor()
        
    def render_optimized(self, layers, rms: float, pitch: float):
        """Оптимизированный метод рендеринга"""
        self.performance.start_frame()
        
        # Генерируем цветовые изображения для всех слоев
        color_images = []
        for layer in layers:
            try:
                # Здесь должен быть вызов build_color_image
                img = build_color_image(
                    layer.grid, layer.age, layer.color_mode, 
                    rms, pitch, self.cfg, 
                    layer.age_palette, layer.rms_palette, 
                    layer.rms_mode, layer.blend_mode, layer.rms_enabled
                )
                color_images.append(img)
            except Exception as e:
                print(f"❌ Error building color image for layer: {e}")
                # Создаем пустое изображение как fallback
                empty_img = np.zeros((GRID_H, GRID_W, 3), dtype=np.uint8)
                color_images.append(empty_img)
        
        # Батчевый рендеринг всех слоев
        self.renderer.render_layers_batch(layers, color_images)
        
        # Записываем статистику
        self.performance.record_render_time(self.renderer.last_render_time)
        self.performance.end_frame()
        
        # Очищаем кэш от неиспользуемых слоев
        active_ids = list(range(len(layers)))
        self.renderer.cleanup_cache(active_ids)
        
        return self.renderer.canvas


# Утилита для бенчмаркинга
def benchmark_rendering(app, layers, iterations: int = 100):
    """Бенчмарк производительности рендеринга"""
    print(f"🏃 Benchmarking rendering performance ({iterations} iterations)...")
    
    times = []
    for i in range(iterations):
        start = time.perf_counter()
        app.render_optimized(layers, 0.5, 440.0)  # Тестовые значения
        end = time.perf_counter()
        times.append(end - start)
        
        if i % 20 == 0:
            print(f"   Progress: {i}/{iterations}")
    
    avg_time = sum(times) * 1000 / len(times)  # В миллисекундах
    fps = 1.0 / (sum(times) / len(times))
    
    print(f"📈 Benchmark Results:")
    print(f"   Average render time: {avg_time:.2f}ms")
    print(f"   Estimated FPS: {fps:.1f}")
    print(f"   Min time: {min(times)*1000:.2f}ms")
    print(f"   Max time: {max(times)*1000:.2f}ms")


if __name__ == "__main__":
    print("🚀 Optimized Layer Renderer loaded successfully!")
    print("   Use OptimizedRenderManager instead of RenderManager")
    print("   Use PerformanceMonitor to track rendering performance")
    print("   Call benchmark_rendering() to test performance")