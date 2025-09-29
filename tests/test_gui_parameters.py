#!/usr/bin/env python3
"""
Тест применения параметров GUI в реальном приложении
"""

import pygame
import sys
import os

# Добавляем текущую директорию в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from guitar_lifeE import CyberHUD

def main():
    pygame.init()
    
    # Создаем приложение как в основном коде
    font = pygame.font.SysFont("times new roman,georgia,serif", 16)
    hud = CyberHUD(font, 800)
    
    # Имитируем установку коллбэка как в основном приложении
    parameter_changes = []
    
    def test_callback(param_name, value):
        parameter_changes.append((param_name, value))
        print(f"🎛️ Параметр изменен: {param_name} = {value}")
    
    hud.on_parameter_change = test_callback
    hud.update_callbacks()
    
    print("🔍 Тестируем применение параметров из GUI")
    print("✅ Коллбэк установлен и обновлен")
    
    # Переключаемся на VISUAL категорию
    hud.active_category = "VISUAL"
    
    # Проверяем что коллбэки установлены правильно
    visual_sliders = ['global_v_mul', 'hue_offset', 'aging_speed', 'fade_start']
    
    for name in visual_sliders:
        if name in hud.sliders:
            slider = hud.sliders[name]
            print(f"  {name}: callback={slider.callback is not None}, param_name={slider.param_name}")
            
            if slider.callback and slider.param_name:
                # Симулируем перетаскивание слайдера
                old_value = slider.current_val
                
                # Симулируем событие клика
                click_event = type('Event', (), {
                    'type': pygame.MOUSEBUTTONDOWN,
                    'pos': (slider.rect.x + 100, slider.rect.y + 12)
                })()
                
                slider.handle_event(click_event)
                
                # Симулируем событие движения мыши
                move_event = type('Event', (), {
                    'type': pygame.MOUSEMOTION,
                    'pos': (slider.rect.x + 150, slider.rect.y + 12)
                })()
                
                slider.handle_event(move_event)
                
                new_value = slider.current_val
                print(f"    🔄 {name}: {old_value:.2f} → {new_value:.2f}")
        else:
            print(f"  ❌ {name}: НЕ НАЙДЕН")
    
    print(f"\n📊 Всего зафиксировано изменений параметров: {len(parameter_changes)}")
    for param_name, value in parameter_changes:
        print(f"  • {param_name}: {value}")
    
    if parameter_changes:
        print("✅ Параметры применяются правильно!")
    else:
        print("❌ Параметры НЕ применяются!")

if __name__ == "__main__":
    main()
    pygame.quit()