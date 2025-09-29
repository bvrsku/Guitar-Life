#!/usr/bin/env python3
"""
Простой тест для проверки фильтрации контролов по категориям
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
    
    print("🔍 Проверка фильтрации контролов по категориям")
    
    # Проверяем AUDIO категорию
    print("\n📻 AUDIO категория:")
    hud.active_category = "AUDIO"
    audio_controls = hud._get_active_category_controls()
    for name, control in audio_controls:
        found = "✅" if control else "❌"
        print(f"  {found} {name}")
    
    # Проверяем VISUAL категорию
    print("\n🎨 VISUAL категория:")
    hud.active_category = "VISUAL"
    visual_controls = hud._get_active_category_controls()
    for name, control in visual_controls:
        found = "✅" if control else "❌"
        print(f"  {found} {name}")
    
    print(f"\n🔢 Общее количество слайдеров: {len(hud.sliders)}")
    print(f"🔢 Общее количество кнопок: {len(hud.buttons)}")
    print(f"🔢 Общее количество комбо-боксов: {len(hud.comboboxes)}")
    
    print("\n✅ Все слайдеры:")
    for name in hud.sliders.keys():
        print(f"  - {name}")

if __name__ == "__main__":
    main()
    pygame.quit()