#!/usr/bin/env python3
"""
Тест для проверки работы слайдеров в категории VISUAL
"""

import pygame
import sys
import os

# Добавляем текущую директорию в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from guitar_lifeE import CyberHUD

def main():
    pygame.init()
    screen = pygame.display.set_mode((1200, 800))
    pygame.display.set_caption("Тест VISUAL слайдеров")
    clock = pygame.time.Clock()
    
    # Создаем CyberHUD и переключаем на VISUAL
    font = pygame.font.Font(None, 24)
    hud = CyberHUD(font, 800)
    hud.visible = True
    hud.active_category = "VISUAL"
    
    print("🔍 Тестируем слайдеры в категории VISUAL")
    print(f"Найдено слайдеров: {len(hud.sliders)}")
    
    # Выводим все слайдеры VISUAL
    visual_sliders = ['global_v_mul', 'hue_offset', 'aging_speed', 'fade_start', 'fade_sat_drop', 'fade_val_drop', 'max_age']
    for name in visual_sliders:
        if name in hud.sliders:
            slider = hud.sliders[name]
            print(f"✅ {name}: x={slider.rect.x}, y={slider.rect.y}, w={slider.rect.width}, h={slider.rect.height}")
        else:
            print(f"❌ {name}: НЕ НАЙДЕН!")
    
    dragging = False
    last_mouse_pos = None
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
            
            # Проверяем события мыши
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                print(f"🖱️ Клик в ({mouse_x}, {mouse_y})")
                
                # Проверяем попадание в слайдеры
                for name, slider in hud.sliders.items():
                    if slider.rect.collidepoint(mouse_x, mouse_y):
                        print(f"✅ Попадание в слайдер {name}")
                        dragging = True
                        last_mouse_pos = (mouse_x, mouse_y)
                        break
                
            elif event.type == pygame.MOUSEBUTTONUP:
                if dragging:
                    print("⬆️ Отпустили мышь")
                    dragging = False
                    last_mouse_pos = None
            
            elif event.type == pygame.MOUSEMOTION:
                if dragging and last_mouse_pos:
                    mouse_x, mouse_y = event.pos
                    dx = mouse_x - last_mouse_pos[0]
                    print(f"🔄 Движение мыши: dx={dx}, новая позиция=({mouse_x}, {mouse_y})")
                    last_mouse_pos = (mouse_x, mouse_y)
            
            # Передаем событие в HUD
            handled = hud.handle_event(event)
            if handled:
                print(f"🎯 Событие обработано HUD: {event.type}")
        
        # Отрисовка
        screen.fill((0, 0, 0))
        
        # Создаем простой объект info для HUD
        class SimpleInfo:
            def __init__(self):
                self.fps = 60
                self.generation = 100
                self.live_cells = 500
            
            def copy(self):
                return self
        
        info = SimpleInfo()
        hud.draw(screen, info)
        
        # Показываем текущие значения слайдеров
        y_offset = 10
        font = pygame.font.Font(None, 24)
        for name in visual_sliders[:3]:  # Показываем первые 3
            if name in hud.sliders:
                slider = hud.sliders[name]
                text = f"{name}: {slider.current_val:.2f}"
                surf = font.render(text, True, (255, 255, 255))
                screen.blit(surf, (10, y_offset))
                y_offset += 25
        
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
    pygame.quit()