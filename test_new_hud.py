# This file has been deleted.
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест нового HUD с модулями слоев
"""

import pygame
import sys
import os

# Добавляем путь к основному модулю
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Импорт нужных классов
from guitar_life_patched import HUD, SimpleColors, Layer
import numpy as np

def test_hud():
    """Тестирует новый HUD с модулями слоев"""
    
    # Инициализация pygame
    pygame.init()
    
    # Создание окна
    GRID_W, GRID_H = 120, 70
    CELL_SIZE = 8
    HUD_WIDTH = 520
    
    width = GRID_W * CELL_SIZE + HUD_WIDTH
    height = GRID_H * CELL_SIZE
    
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Guitar Life HUD Test")
    
    # Создание шрифта
    font = pygame.font.SysFont("times new roman,georgia,serif", 16)
    
    # Создание HUD
    hud = HUD(font, height, 5)
    
    # Создание тестовых слоев
    test_layers = []
    for i in range(5):
        grid = np.zeros((GRID_H, GRID_W), dtype=bool)
        age = np.zeros((GRID_H, GRID_W), dtype=np.int32)
        
        layer = Layer(
            grid=grid,
            age=age,
            rule="Conway",
            age_palette="Fire",
            rms_palette="Ocean",
            color_mode="HSV-дизайны",
            rms_mode="brightness",
            blend_mode="normal",
            rms_enabled=True,
            alpha_live=220,
            alpha_old=140,
            mix="Normal",
            solo=False,
            mute=False
        )
        test_layers.append(layer)
    
    # Мок объект приложения для тестирования
    class MockApp:
        def __init__(self):
            self.layers = test_layers
    
    mock_app = MockApp()
    
    # Настройка колбэка для изменений параметров
    def on_parameter_change(param_name, value):
        print(f"Parameter changed: {param_name} = {value}")
    
    hud.on_parameter_change = on_parameter_change
    hud.update_from_app(mock_app)
    
    # Основной цикл
    clock = pygame.time.Clock()
    running = True
    
    print("🎮 HUD Test Started")
    print("📋 Controls:")
    print("   - Mouse: Interact with HUD elements")
    print("   - Mouse Wheel: Scroll HUD")
    print("   - H: Toggle HUD visibility")
    print("   - ESC: Exit")
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_h:
                    hud.visible = not hud.visible
                    print(f"🔄 HUD visibility: {'ON' if hud.visible else 'OFF'}")
            else:
                # Передаем события в HUD
                if hud.handle_event(event):
                    print(f"✅ HUD handled event: {event.type}")
        
        # Очистка экрана
        screen.fill((10, 10, 12))  # Темный фон
        
        # Отрисовка игрового поля (заглушка)
        game_area = pygame.Rect(0, 0, GRID_W * CELL_SIZE, GRID_H * CELL_SIZE)
        pygame.draw.rect(screen, (20, 20, 25), game_area)
        pygame.draw.rect(screen, (60, 60, 80), game_area, 2)
        
        # Информация для HUD
        info = {
            "Layers": str(len(test_layers)),
            "Alive": "150 cells",
            "RMS": "0.045",
            "Pitch": "440.0 Hz"
        }
        
        # Отрисовка HUD
        hud.draw(screen, info)
        
        # Обновление экрана
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    print("👋 HUD Test Finished")

if __name__ == "__main__":
    try:
        test_hud()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()