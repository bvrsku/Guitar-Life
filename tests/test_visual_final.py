#!/usr/bin/env python3
"""
Финальный тест слайдеров VISUAL в основном приложении
"""

import pygame
import sys
import os

# Добавляем текущую директорию в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from guitar_lifeE import CyberHUD

def main():
    pygame.init()
    screen = pygame.display.set_mode((1400, 800))
    pygame.display.set_caption("Финальный тест VISUAL слайдеров")
    clock = pygame.time.Clock()
    
    # Создаем CyberHUD и переключаем на VISUAL
    font = pygame.font.Font(None, 24)
    hud = CyberHUD(font, 800)
    hud.visible = True
    hud.active_category = "VISUAL"
    
    print("🎨 Тестируем только VISUAL слайдеры")
    print("✅ Исправлена обработка событий - теперь работают только активные контролы")
    
    # Создаем простой объект info для HUD
    class SimpleInfo:
        def __init__(self):
            self.fps = 60
            self.generation = 100
            self.live_cells = 500
        
        def copy(self):
            return self
    
    info = SimpleInfo()
    last_values = {}
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
                elif event.key == pygame.K_1:
                    hud.active_category = "AUDIO"
                    print("📻 Переключено на AUDIO")
                elif event.key == pygame.K_2:
                    hud.active_category = "VISUAL"
                    print("🎨 Переключено на VISUAL")
                elif event.key == pygame.K_3:
                    hud.active_category = "LAYERS"
                    print("🎭 Переключено на LAYERS")
            
            # Передаем событие в HUD
            handled = hud.handle_event(event)
            if handled and event.type == pygame.MOUSEBUTTONDOWN:
                print(f"🎯 Клик обработан в категории {hud.active_category}")
        
        # Отрисовка
        screen.fill((0, 20, 40))  # Темно-синий фон
        hud.draw(screen, info)
        
        # Показываем текущие значения VISUAL слайдеров
        if hud.active_category == "VISUAL":
            visual_sliders = ['global_v_mul', 'hue_offset', 'aging_speed', 'fade_start']
            y_offset = 10
            font_small = pygame.font.Font(None, 20)
            
            for name in visual_sliders:
                if name in hud.sliders:
                    slider = hud.sliders[name]
                    current_val = slider.current_val
                    
                    # Проверяем изменение значения
                    if name not in last_values or abs(last_values[name] - current_val) > 0.01:
                        last_values[name] = current_val
                        print(f"🔄 {name}: {current_val:.2f}")
                    
                    # Отображаем на экране
                    text = f"{name}: {current_val:.2f}"
                    color = (0, 255, 100) if name in last_values else (255, 255, 255)
                    surf = font_small.render(text, True, color)
                    screen.blit(surf, (10, y_offset))
                    y_offset += 25
        
        # Инструкции
        instructions = [
            "ESC - выход",
            "1 - AUDIO категория", 
            "2 - VISUAL категория",
            "3 - LAYERS категория",
            f"Активная: {hud.active_category}"
        ]
        
        y_offset = screen.get_height() - len(instructions) * 25
        font_info = pygame.font.Font(None, 24)
        
        for instruction in instructions:
            color = (0, 255, 200) if instruction.startswith("Активная:") else (200, 200, 200)
            surf = font_info.render(instruction, True, color)
            screen.blit(surf, (10, y_offset))
            y_offset += 25
        
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
    pygame.quit()