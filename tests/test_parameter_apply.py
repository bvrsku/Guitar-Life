#!/usr/bin/env python3
"""
Тест применения параметров из GUI к приложению
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
    
    # Имитируем создание как в основном приложении
    hud = CyberHUD(font, 800)
    
    # Создаем имитацию коллбэка
    def test_callback(param_name, value):
        print(f"🎛️ {param_name}: {value}")
    
    # Устанавливаем коллбэк
    hud.on_parameter_change = test_callback
    hud.active_category = "VISUAL"
    
    print("🔍 Тестируем применение параметров")
    print("✅ Коллбэк установлен")
    
    # Проверяем что слайдеры имеют коллбэки
    visual_sliders = ['global_v_mul', 'hue_offset', 'aging_speed', 'fade_start']
    
    for name in visual_sliders:
        if name in hud.sliders:
            slider = hud.sliders[name]
            has_callback = slider.callback is not None
            has_param = slider.param_name is not None
            print(f"  {name}: callback={has_callback}, param_name={has_param}")
            
            if has_callback and has_param:
                # Симулируем изменение значения
                print(f"    🔄 Тестируем изменение {name}...")
                old_value = slider.current_val
                slider.current_val = old_value + 10  # Изменяем значение
                slider._update_value(slider.rect.x + 100)  # Симулируем движение мыши
        else:
            print(f"  ❌ {name}: НЕ НАЙДЕН")

if __name__ == "__main__":
    main()
    pygame.quit()