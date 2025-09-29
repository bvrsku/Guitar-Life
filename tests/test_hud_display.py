#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест отображения всех параметров в HUD
"""

import sys
import os
import pygame
import numpy as np

# Добавляем путь к модулю
sys.path.insert(0, os.path.dirname(__file__))

# Импортируем необходимые классы
from guitar_lifeE import CyberHUD, DEFAULT_TICK_MS, DEFAULT_COLOR_RMS_MIN, DEFAULT_COLOR_RMS_MAX

class MockLayer:
    def __init__(self):
        self.grid = np.zeros((70, 120), dtype=bool)
        self.age = np.zeros((70, 120), dtype=np.int32)
        self.rule = 'Conway'
        self.age_palette = 'Fire'
        self.rms_palette = 'Ocean'
        self.alpha = 1.0
        self.blend_mode = 'normal'
        self.muted = False
        self.mute = False
        self.solo = False
        self.mirror_x = False
        self.mirror_y = False

class MockApp:
    def __init__(self):
        # Основные параметры
        self.tick_ms = DEFAULT_TICK_MS
        self.gain = 2.5
        self.rms_strength = 100
        self.aging_speed = 1.0
        self.max_age = 120
        self.fade_start = 60
        self.global_v_mul = 1.0
        self.fade_sat_drop = 70
        self.fade_val_drop = 60
        self.hue_offset = 0
        
        # Аудио параметры
        self.color_rms_min = DEFAULT_COLOR_RMS_MIN
        self.color_rms_max = DEFAULT_COLOR_RMS_MAX
        self.pitch_tick_enable = False
        self.pitch_tick_min = 60
        self.pitch_tick_max = 200
        
        # Параметры очистки
        self.clear_type = 'Полная очистка'
        self.soft_mode = 'Удалять клетки'
        self.clear_partial_percent = 50
        self.clear_age_threshold = 10
        self.clear_random_percent = 30
        
        # Зеркалирование
        self.mirror_x = False
        self.mirror_y = False
        
        # Эффекты
        self.fx = {
            'scanlines': False,
            'posterize': False,
            'dither': False,
            'pixelate': False,
            'blur': False
        }
        
        # Слои
        self.layers = [MockLayer() for _ in range(3)]
        self.selected_layer_index = 0

def test_hud_display():
    """Тестирует отображение HUD"""
    pygame.init()
    
    # Создаем экран
    screen = pygame.display.set_mode((1400, 800))
    pygame.display.set_caption("Test HUD Display")
    
    # Создаем шрифт
    font = pygame.font.SysFont("times new roman", 16)
    
    # Создаем HUD
    hud = CyberHUD(font, 800, 3)
    
    # Создаем мок приложения
    app = MockApp()
    
    # Устанавливаем колбэк
    def test_callback(param_name, value):
        print(f"🎛️ Parameter changed: {param_name} = {value}")
        # Обновляем мок приложение
        if hasattr(app, param_name):
            setattr(app, param_name, value)
    
    hud.on_parameter_change = test_callback
    
    # Обновляем HUD значениями из приложения
    hud.update_from_app(app)
    
    clock = pygame.time.Clock()
    running = True
    
    print("🚀 Тестирование отображения HUD")
    print("📋 Доступные категории:")
    for i, category in enumerate(hud.categories):
        print(f"   {i+1}. {category}")
    print("🎮 Управление:")
    print("   - Клик по вкладкам для переключения категорий")
    print("   - Колесо мыши для скролла")
    print("   - ESC для выхода")
    print()
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_1:
                    hud.active_category = 'AUDIO'
                elif event.key == pygame.K_2:
                    hud.active_category = 'VISUAL'
                elif event.key == pygame.K_3:
                    hud.active_category = 'LAYERS'
                elif event.key == pygame.K_4:
                    hud.active_category = 'EFFECTS'
                elif event.key == pygame.K_5:
                    hud.active_category = 'PERF'
                elif event.key == pygame.K_6:
                    hud.active_category = 'ACTIONS'
            else:
                hud.handle_event(event)
        
        # Обновляем HUD периодически
        hud.update_from_app(app)
        
        # Отрисовка
        screen.fill((10, 10, 15))
        
        # Создаем фиктивную информацию
        info = {
            'fps': 60,
            'cells': 1234,
            'layers': len(app.layers),
            'rms': 0.05
        }
        
        # Рисуем HUD
        hud.draw(screen, info)
        
        # Информация о текущей категории
        title_font = pygame.font.SysFont("arial", 24, bold=True)
        title_text = title_font.render(f"Active Category: {hud.active_category}", True, (255, 255, 255))
        screen.blit(title_text, (10, 10))
        
        # Инструкции
        help_font = pygame.font.SysFont("arial", 14)
        help_lines = [
            "Press 1-6 to switch categories",
            "Use mouse wheel to scroll",
            "Click tabs to navigate",
            "ESC to exit"
        ]
        
        for i, line in enumerate(help_lines):
            help_text = help_font.render(line, True, (200, 200, 200))
            screen.blit(help_text, (10, 50 + i * 20))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    print("✅ Тест завершен")

if __name__ == "__main__":
    test_hud_display()