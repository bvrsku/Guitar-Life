#!/usr/bin/env python3
"""
Простая демонстрация HUD элементов
"""

import pygame
import sys

# Импортируем наши классы
from guitar_life import HUD, UISlider, UIButton

def demo_hud():
    """Демонстрация HUD интерфейса"""
    pygame.init()
    
    # Создаем окно
    width, height = 1400, 700
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Demo HUD Interface")
    
    # Создаем шрифт и HUD
    font = pygame.font.SysFont("consolas", 16)
    hud = HUD(font)
    
    # Фиктивное приложение для тестирования
    class MockApp:
        def __init__(self):
            self.tick_ms = 120
            self.rms_strength = 100
            self.max_age = 120
            self.fade_start = 60
            self.sel = {'clear_rms': 0.004}
            self.color_rms_min = 0.004
            self.color_rms_max = 0.3
            self.soft_kill_rate = 80
            self.soft_fade_floor = 0.3
            self.pitch_tick_min = 60
            self.pitch_tick_max = 300
            self.pitch_tick_enable = False
            self.rms_modulation = True
            self.soft_clear_enable = True
            self.soft_mode = 'Удалять клетки'
            self.mirror_x = False
            self.mirror_y = False
            self.fx = {
                'trails': True,
                'blur': False,
                'bloom': False,
                'posterize': False,
                'dither': False,
                'scanlines': False,
                'pixelate': False,
                'outline': False
            }
    
    mock_app = MockApp()
    
    # Настройка колбэка
    def on_param_change(param_name, value):
        print(f"Parameter changed: {param_name} = {value}")
        # Обновляем мок-приложение
        if hasattr(mock_app, param_name.replace('fx_', '')):
            if param_name.startswith('fx_'):
                mock_app.fx[param_name[3:]] = value
            else:
                setattr(mock_app, param_name, value)
    
    hud.on_parameter_change = on_param_change
    hud.update_from_app(mock_app)
    
    clock = pygame.time.Clock()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_h:
                    hud.visible = not hud.visible
            
            # Обрабатываем события HUD
            hud.handle_event(event)
        
        # Очищаем экран
        screen.fill((30, 30, 40))
        
        # Рисуем игровое поле (заглушка)
        game_rect = pygame.Rect(10, 10, 960, 560)
        pygame.draw.rect(screen, (50, 50, 60), game_rect)
        pygame.draw.rect(screen, (100, 100, 120), game_rect, 2)
        
        # Добавляем текст
        text = font.render("Demo Game Field - Press H to toggle HUD", True, (200, 200, 200))
        screen.blit(text, (20, 30))
        
        # Рисуем HUD
        info = {
            "Status": "Demo Mode",
            "FPS": f"{clock.get_fps():.1f}",
            "Mouse": f"{pygame.mouse.get_pos()}"
        }
        hud.draw(screen, info)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    demo_hud()