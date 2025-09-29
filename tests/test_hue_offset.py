#!/usr/bin/env python3
"""
Тест для проверки второго ползунка (hue_offset) в категории VISUAL
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
    pygame.display.set_caption("Тест второго ползунка VISUAL")
    clock = pygame.time.Clock()
    
    # Создаем CyberHUD и переключаем на VISUAL
    font = pygame.font.Font(None, 24)
    hud = CyberHUD(font, 800)
    hud.visible = True
    hud.active_category = "VISUAL"
    
    print("🔍 Тестируем второй ползунок в VISUAL (hue_offset)")
    
    # Проверяем что слайдер существует
    if 'hue_offset' in hud.sliders:
        slider = hud.sliders['hue_offset']
        print(f"✅ hue_offset найден: x={slider.rect.x}, y={slider.rect.y}, w={slider.rect.width}, h={slider.rect.height}")
        print(f"   Текущее значение: {slider.current_val}")
        print(f"   Диапазон: {slider.min_val} - {slider.max_val}")
    else:
        print("❌ hue_offset НЕ НАЙДЕН!")
        return
    
    # Проверяем активные контролы
    active_controls = hud._get_active_category_controls()
    print(f"\n📋 Активные контролы ({len(active_controls)}):")
    for i, (name, control) in enumerate(active_controls):
        status = "✅" if control else "❌"
        print(f"  {i+1}. {status} {name}")
        if name == 'hue_offset':
            print(f"     🎯 Второй ползунок найден в списке!")
    
    # Создаем простой объект info для HUD
    class SimpleInfo:
        def __init__(self):
            self.fps = 60
            self.generation = 100
            self.live_cells = 500
        
        def copy(self):
            return self
    
    info = SimpleInfo()
    last_value = None
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
            
            # Проверяем попадание в hue_offset при клике
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                slider = hud.sliders['hue_offset']
                
                if slider.rect.collidepoint(mouse_x, mouse_y):
                    print(f"🖱️ КЛИК по hue_offset в ({mouse_x}, {mouse_y})")
                    print(f"   Область слайдера: {slider.rect}")
                else:
                    print(f"🖱️ Клик мимо hue_offset в ({mouse_x}, {mouse_y})")
                    print(f"   Область слайдера: {slider.rect}")
                    
                    # Проверяем попадание в другие слайдеры
                    for name, other_slider in hud.sliders.items():
                        if other_slider.rect.collidepoint(mouse_x, mouse_y):
                            print(f"   ⚠️ Попадание в другой слайдер: {name}")
            
            # Передаем событие в HUD
            handled = hud.handle_event(event)
            if handled:
                print(f"🎯 Событие обработано HUD")
        
        # Отрисовка
        screen.fill((0, 0, 0))
        hud.draw(screen, info)
        
        # Проверяем изменение значения hue_offset
        current_value = hud.sliders['hue_offset'].current_val
        if last_value is None or abs(last_value - current_value) > 0.1:
            if last_value is not None:
                print(f"🔄 hue_offset изменился: {last_value:.1f} → {current_value:.1f}")
            last_value = current_value
        
        # Показываем значение на экране
        font_large = pygame.font.Font(None, 36)
        text = f"hue_offset: {current_value:.1f}°"
        color = (0, 255, 100) if current_value > 0 else (255, 255, 255)
        surf = font_large.render(text, True, color)
        screen.blit(surf, (10, 10))
        
        # Показываем координаты слайдера
        slider_info = f"Slider: x={slider.rect.x}, y={slider.rect.y}, w={slider.rect.width}, h={slider.rect.height}"
        surf_info = font.render(slider_info, True, (200, 200, 200))
        screen.blit(surf_info, (10, 50))
        
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
    pygame.quit()