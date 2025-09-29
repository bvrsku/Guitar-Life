#!/usr/bin/env python3
"""
Тест позиций слайдеров по категориям
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
    
    print("🔍 Сравнение позиций слайдеров")
    
    # AUDIO слайдеры
    print("\n📻 AUDIO слайдеры:")
    audio_sliders = ['gain', 'rms_strength', 'color_rms_min', 'color_rms_max']
    for name in audio_sliders:
        if name in hud.sliders:
            slider = hud.sliders[name]
            print(f"  {name}: y={slider.rect.y}")
    
    # VISUAL слайдеры
    print("\n🎨 VISUAL слайдеры:")
    visual_sliders = ['global_v_mul', 'hue_offset', 'aging_speed', 'fade_start', 'fade_sat_drop', 'fade_val_drop']
    for name in visual_sliders:
        if name in hud.sliders:
            slider = hud.sliders[name]
            print(f"  {name}: y={slider.rect.y}")

if __name__ == "__main__":
    main()
    pygame.quit()