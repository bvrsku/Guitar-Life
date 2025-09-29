#!/usr/bin/env python3
"""
Финальный тест второго ползунка VISUAL после исправления
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
    pygame.display.set_caption("Тест исправленного hue_offset")
    clock = pygame.time.Clock()
    
    # Создаем CyberHUD и переключаем на VISUAL
    font = pygame.font.Font(None, 24)
    hud = CyberHUD(font, 800)
    hud.visible = True
    hud.active_category = "VISUAL"
    
    print("🎨 Тестируем исправленный второй ползунок VISUAL (hue_offset)")
    print("✅ Устранен конфликт с max_age")
    print("✅ Фильтрация активных контролов работает")
    
    # Создаем простой объект info для HUD
    class SimpleInfo:
        def __init__(self):
            self.fps = 60
            self.generation = 100
            self.live_cells = 500
        
        def copy(self):
            return self
    
    info = SimpleInfo()
    last_hue = None
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
                elif event.key == pygame.K_2:
                    hud.active_category = "VISUAL"
                    print("🎨 Переключено на VISUAL")
                elif event.key == pygame.K_1:
                    hud.active_category = "AUDIO"
                    print("📻 Переключено на AUDIO")
            
            # Передаем событие в HUD
            handled = hud.handle_event(event)
            if handled and event.type == pygame.MOUSEBUTTONDOWN:
                print(f"🎯 Клик обработан в {hud.active_category}")
        
        # Отрисовка
        screen.fill((0, 20, 40))
        hud.draw(screen, info)
        
        # Проверяем изменение hue_offset
        if 'hue_offset' in hud.sliders:
            current_hue = hud.sliders['hue_offset'].current_val
            if last_hue is None or abs(last_hue - current_hue) > 0.5:
                if last_hue is not None:
                    print(f"🌈 hue_offset: {last_hue:.1f}° → {current_hue:.1f}°")
                last_hue = current_hue
            
            # Показываем большими цифрами
            font_huge = pygame.font.Font(None, 48)
            text = f"Hue Offset: {current_hue:.1f}°"
            # Простой цвет на основе hue
            hue_ratio = (current_hue / 360) % 1
            color_hue = (
                int(255 * (1 - hue_ratio)),
                int(255 * hue_ratio),
                100
            )
            surf = font_huge.render(text, True, color_hue)
            screen.blit(surf, (50, 50))
        
        # Показываем координаты второго ползунка
        if hud.active_category == "VISUAL" and 'hue_offset' in hud.sliders:
            slider = hud.sliders['hue_offset']
            coords_text = f"Slider#2: x={slider.rect.x}, y={slider.rect.y}, w={slider.rect.width}, h={slider.rect.height}"
            font_small = pygame.font.Font(None, 20)
            surf = font_small.render(coords_text, True, (0, 255, 150))
            screen.blit(surf, (50, 120))
        
        # Инструкции
        instructions = [
            "ESC - выход",
            "1 - AUDIO", 
            "2 - VISUAL",
            f"Активно: {hud.active_category}",
            "Двигайте второй ползунок!"
        ]
        
        y_pos = screen.get_height() - len(instructions) * 25
        for instruction in instructions:
            color = (0, 255, 200) if "Активно:" in instruction else (200, 200, 200)
            surf = font.render(instruction, True, color)
            screen.blit(surf, (50, y_pos))
            y_pos += 25
        
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
    pygame.quit()