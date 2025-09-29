#!/usr/bin/env python3
"""
Простая диагностика второго ползунка
"""

import pygame
import sys
import os

# Добавляем текущую директорию в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from guitar_lifeE import CyberHUD

def main():
    pygame.init()
    font = pygame.font.Font(None, 24)
    hud = CyberHUD(font, 800)
    hud.active_category = "VISUAL"
    
    print("🔍 Диагностика hue_offset слайдера")
    
    # Проверяем слайдер
    if 'hue_offset' in hud.sliders:
        slider = hud.sliders['hue_offset']
        print(f"✅ hue_offset: {slider.rect}, value={slider.current_val}")
        
        # Симулируем клик
        test_event = type('Event', (), {
            'type': pygame.MOUSEBUTTONDOWN,
            'pos': (slider.rect.x + 50, slider.rect.y + 12)  # Клик в центр слайдера
        })()
        
        print(f"🖱️ Симулируем клик в {test_event.pos}")
        result = slider.handle_event(test_event)
        print(f"   Результат: {result}")
        print(f"   Новое значение: {slider.current_val}")
        
        # Симулируем движение
        test_move = type('Event', (), {
            'type': pygame.MOUSEMOTION,
            'pos': (slider.rect.x + 100, slider.rect.y + 12)
        })()
        
        # Устанавливаем флаг перетаскивания
        slider.dragging = True
        result2 = slider.handle_event(test_move)
        print(f"🔄 Симулируем движение в {test_move.pos}")
        print(f"   Результат: {result2}")
        print(f"   Новое значение: {slider.current_val}")
        
    # Проверяем активные контролы
    active_controls = hud._get_active_category_controls()
    print(f"\n📋 Активные контролы для VISUAL:")
    for name, control in active_controls:
        if name == 'hue_offset':
            print(f"   ✅ {name}: {control}")
            
            # Тестируем обработку через HUD
            test_hud_event = type('Event', (), {
                'type': pygame.MOUSEBUTTONDOWN,
                'pos': (control.rect.x + 50, control.rect.y + 12)
            })()
            
            print(f"🎯 Тестируем обработку через HUD...")
            hud_result = hud.handle_event(test_hud_event)
            print(f"   HUD результат: {hud_result}")

if __name__ == "__main__":
    main()
    pygame.quit()