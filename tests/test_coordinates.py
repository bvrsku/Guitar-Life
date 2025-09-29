#!/usr/bin/env python3
"""
Проверка координат всех VISUAL слайдеров
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
    
    print("🔍 Координаты всех слайдеров в приложении:")
    
    # Все слайдеры (не только VISUAL)
    all_sliders = [
        'gain', 'rms_strength', 'color_rms_min', 'color_rms_max',  # AUDIO
        'global_v_mul', 'hue_offset', 'aging_speed', 'fade_start', 'fade_sat_drop', 'fade_val_drop', 'max_age',  # VISUAL
        'layer_count'  # LAYERS
    ]
    
    print("\n📊 Полный список координат:")
    overlaps = []
    
    for name in all_sliders:
        if name in hud.sliders:
            slider = hud.sliders[name]
            category = "AUDIO" if name in ['gain', 'rms_strength', 'color_rms_min', 'color_rms_max'] else \
                      "VISUAL" if name in ['global_v_mul', 'hue_offset', 'aging_speed', 'fade_start', 'fade_sat_drop', 'fade_val_drop', 'max_age'] else \
                      "OTHER"
            
            print(f"  {category:6} {name:15} y={slider.rect.y:3d} x={slider.rect.x:4d} w={slider.rect.width:3d} h={slider.rect.height:2d}")
            
            # Проверяем перекрытия с hue_offset
            if name != 'hue_offset' and name in hud.sliders:
                hue_slider = hud.sliders['hue_offset']
                if (slider.rect.x < hue_slider.rect.x + hue_slider.rect.width and
                    slider.rect.x + slider.rect.width > hue_slider.rect.x and
                    slider.rect.y < hue_slider.rect.y + hue_slider.rect.height and
                    slider.rect.y + slider.rect.height > hue_slider.rect.y):
                    overlaps.append(name)
    
    print(f"\n⚠️ Перекрытия с hue_offset:")
    if overlaps:
        for overlap in overlaps:
            slider = hud.sliders[overlap]
            print(f"   ❌ {overlap}: y={slider.rect.y} (конфликт!)")
    else:
        print("   ✅ Перекрытий не найдено")
    
    # Проверяем порядок обработки в активных контролах
    print(f"\n🔄 Порядок обработки в VISUAL категории:")
    active_controls = hud._get_active_category_controls()
    for i, (name, control) in enumerate(active_controls):
        if control:
            print(f"  {i+1}. {name} y={control.rect.y}")

if __name__ == "__main__":
    main()
    pygame.quit()